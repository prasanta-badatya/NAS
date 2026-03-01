from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DevTaskEvent:
    """
    Fired when a developer submits a task.
    This is the entry point for the entire Brain → Agent pipeline.
    """
    task: str
    repo_path: str
    task_id: str = field(
        default_factory=lambda: f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    files_hint: list[str] = field(default_factory=list)


@dataclass
class AgentResult:
    """
    Returned by every agent after execution.
    The Brain reads these to build the next decision.
    """
    agent: str
    success: bool
    output: str
    files_changed: list[str] = field(default_factory=list)
    error: Optional[str] = None