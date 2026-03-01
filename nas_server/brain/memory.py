from dataclasses import dataclass, field
from typing import Optional

from .events import DevTaskEvent, AgentResult


@dataclass
class TaskMemory:
    """
    Stores everything known about a single task session.
    The Brain reads and writes this between agent calls.
    Agents never touch memory directly — only the Brain does.
    """
    task_id: str
    event: DevTaskEvent
    task_type: Optional[str] = None
    agent_plan: Optional[str] = None
    code_context: Optional[str] = None
    agent_results: list[AgentResult] = field(default_factory=list)

    def add_result(self, result: AgentResult) -> None:
        self.agent_results.append(result)

    def get_summary(self) -> str:
        lines = [f"Original task: {self.event.task}"]
        if self.task_type:
            lines.append(f"Task type: {self.task_type}")
            lines.append(f"Plan: {self.agent_plan}")
        if self.code_context:
            lines.append(f"\n--- Code Analysis ---\n{self.code_context}")
        for r in self.agent_results:
            status = "✓" if r.success else "✗"
            lines.append(f"\n--- [{status} {r.agent}] ---\n{r.output}")
            if r.files_changed:
                lines.append(f"Files changed: {', '.join(r.files_changed)}")
            if r.error:
                lines.append(f"Error: {r.error}")
        return "\n".join(lines)


class Memory:
    """
    In-process store for TaskMemory objects.
    One entry per active task, keyed by task_id.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, TaskMemory] = {}

    def create(self, event: DevTaskEvent) -> TaskMemory:
        mem = TaskMemory(task_id=event.task_id, event=event)
        self._tasks[event.task_id] = mem
        return mem

    def get(self, task_id: str) -> Optional[TaskMemory]:
        return self._tasks.get(task_id)

    def clear(self, task_id: str) -> None:
        self._tasks.pop(task_id, None)