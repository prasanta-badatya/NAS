#!/usr/bin/env python3
"""
Designer Agent — Senior UI/UX redesign agent (5 years experience).

Usage:
    python agents/designer_agent.py
    python agents/designer_agent.py "Redesign only the login page"

Requirements:
    pip install anthropic
    ANTHROPIC_API_KEY must be set in environment.
"""

import io
import os
import sys
import json
import glob as glob_module
from pathlib import Path

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import anthropic

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
UI_SRC = PROJECT_ROOT / "nas-ui" / "src"

# ── Designer system prompt ────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior UI/UX designer with 5 years of experience \
specialising in premium, dark-mode web applications. You have shipped \
production design systems for SaaS products used by millions of users.

Your expertise:
- Premium dark UI: deep backgrounds, layered surfaces, subtle depth
- Typography hierarchy: proper weights, sizes, letter-spacing, line-heights
- Color theory: sophisticated palettes with restrained accent usage
- Micro-interactions: smooth cubic-bezier transitions, hover/focus states
- Icon systems: always use clean inline SVG — NEVER use emoji as icons
- Glass morphism: backdrop-filter, semi-transparent surfaces with borders
- Mobile-first responsive layouts

Your design philosophy:
- Premium = calm, intentional, and refined — never flashy or loud
- Whitespace breathes life into layouts; don't fear empty space
- Consistent border-radius, spacing, and shadow hierarchy everywhere
- Every interactive element needs a clear hover and focus state
- Transitions should feel natural: 180–220ms, cubic-bezier(0.4, 0, 0.2, 1)

━━━ Design tokens to apply ━━━

Backgrounds:
  --bg:        #07070e   (page background)
  --s1:        #0e0e1c   (raised surface)
  --s2:        #14142a   (card / input background)
  --s3:        #1e1e38   (hover / selected state)

Borders:
  --b0:        rgba(255,255,255,0.05)   (very subtle)
  --b1:        rgba(255,255,255,0.09)   (default)
  --b2:        rgba(255,255,255,0.15)   (emphasis)

Accent (indigo):
  --a:         #6366f1
  --a-hover:   #818cf8
  --a-dim:     rgba(99,102,241,0.15)
  --a-glow:    rgba(99,102,241,0.25)

Status:
  --ok:        #22c55e   (success green)
  --ok-dim:    rgba(34,197,94,0.15)
  --warn:      #f59e0b
  --err:       #ef4444   (danger red)
  --err-dim:   rgba(239,68,68,0.15)

Text:
  --t1:        #f1f5f9   (primary)
  --t2:        #94a3b8   (secondary)
  --t3:        #475569   (muted)

Radius:
  --r-sm:  8px
  --r-md:  12px
  --r-lg:  16px
  --r-xl:  20px

Shadows:
  --sh1: 0 1px 3px rgba(0,0,0,0.4)
  --sh2: 0 4px 16px rgba(0,0,0,0.5)
  --sh3: 0 8px 32px rgba(0,0,0,0.6)

━━━ Icon style ━━━
Use 20×20 inline SVGs with stroke="currentColor", fill="none",
stroke-width="1.75", stroke-linecap="round", stroke-linejoin="round".
Wrap in <span class="icon"> for consistent sizing.

━━━ Rules ━━━
1. Read the current file first with read_file.
2. Keep ALL Angular bindings (*ngIf, *ngFor, (click), [(ngModel)], [class.*],
   @Input, @Output, routerLink) EXACTLY as-is.
3. Only change visual presentation (HTML structure, CSS classes, SCSS styles).
4. Write the redesigned file with write_file.
5. After all files are done, print a short summary of what changed."""

# ── Tool definitions ──────────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the full contents of a file. Path is relative to project root (NAS/).",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "e.g. nas-ui/src/styles.scss"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Overwrite a file with new content. Path is relative to project root (NAS/).",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_files",
        "description": "List files matching a glob pattern, relative to NAS/nas-ui/src/.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "e.g. app/**/*.scss"}
            },
            "required": ["pattern"]
        }
    }
]

# ── Tool executor ─────────────────────────────────────────────────────────────
def run_tool(name: str, args: dict) -> str:
    if name == "read_file":
        path = PROJECT_ROOT / args["path"]
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return f"ERROR: File not found — {args['path']}"

    elif name == "write_file":
        path = PROJECT_ROOT / args["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(args["content"], encoding="utf-8")
        return f"OK: wrote {args['path']} ({len(args['content'])} chars)"

    elif name == "list_files":
        pattern = str(UI_SRC / args["pattern"])
        matches = glob_module.glob(pattern, recursive=True)
        rel = [
            str(Path(m).relative_to(PROJECT_ROOT)).replace("\\", "/")
            for m in sorted(matches)
        ]
        return json.dumps(rel)

    return f"ERROR: unknown tool '{name}'"


# ── Default redesign task ─────────────────────────────────────────────────────
DEFAULT_TASK = """Redesign the entire Angular UI of this NAS photo app to look \
premium and polished.

Files to redesign (read each one first, then write the improved version):

  1. nas-ui/src/styles.scss
  2. nas-ui/src/app/auth/login/login.component.html
  3. nas-ui/src/app/auth/login/login.component.scss
  4. nas-ui/src/app/gallery/gallery-home/gallery-home.component.html
  5. nas-ui/src/app/gallery/gallery-home/gallery-home.component.scss
  6. nas-ui/src/app/gallery/photo-grid/photo-grid.component.html
  7. nas-ui/src/app/gallery/photo-grid/photo-grid.component.scss
  8. nas-ui/src/app/gallery/upload/upload.component.html
  9. nas-ui/src/app/gallery/upload/upload.component.scss
 10. nas-ui/src/app/gallery/viewer/viewer.component.html
 11. nas-ui/src/app/gallery/viewer/viewer.component.scss
 12. nas-ui/src/app/gallery/trash/trash.component.html
 13. nas-ui/src/app/gallery/trash/trash.component.scss
 14. nas-ui/src/app/shared/confirm-dialog/confirm-dialog.component.html
 15. nas-ui/src/app/shared/confirm-dialog/confirm-dialog.component.scss

Design requirements:
- Replace every emoji used as an icon (📷 🗑 ⬇ ℹ ✕ ↩ ↑) with clean 20px inline SVG
- Apply the design tokens from your system prompt consistently
- Make the topbar/header feel premium with a subtle gradient border-bottom
- Buttons: gradient accent, subtle box-shadow, smooth hover/active transitions
- Inputs: dark fill, focused glow ring using --a-glow
- Cards: glassy surface with --b1 border, --sh2 shadow
- Photo grid tiles: rounded corners, smooth scale + brightness on hover
- Viewer: full glass-dark treatment, blurred topbar overlay
- Upload drop zone: dashed gradient border, animated on drag-over
- Confirm dialog: glass modal with frosted backdrop
- Keep every Angular directive, binding, and event handler untouched"""


# ── Agent loop ────────────────────────────────────────────────────────────────
def run(task: str):
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": task}]
    divider = "-" * 60

    print(f"\n🎨  Designer Agent\n{divider}")
    print(f"Task: {task[:120]}{'...' if len(task) > 120 else ''}\n{divider}\n")

    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(f"\n✅  Done\n{divider}\n{block.text}\n")
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []

            for block in response.content:
                if block.type == "tool_use":
                    first_val = str(list(block.input.values())[0])[:70]
                    print(f"  ⚙  {block.name}  {first_val}")
                    output = run_tool(block.name, block.input)
                    if block.name == "write_file":
                        print(f"     → {output}")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                    })

            messages.append({"role": "user", "content": results})
        else:
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break

    print(f"{divider}\n🎨  Designer Agent finished.\n")


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT_TASK
    run(task)
