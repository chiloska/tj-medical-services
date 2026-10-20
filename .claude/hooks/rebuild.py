#!/usr/bin/env python3
"""PostToolUse (Edit|Write): regenerate public/ whenever a file in src/ changes."""
import json
import os
import subprocess
import sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path") or ""
root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
try:
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root)).replace("\\", "/")
except ValueError:
    sys.exit(0)
if not (rel.startswith("src/") and rel.endswith(".py")):
    sys.exit(0)

r = subprocess.run([sys.executable, os.path.join(root, "src", "build.py")],
                   capture_output=True, text=True, encoding="utf-8")
if r.returncode != 0:
    print(f"src/build.py failed after editing {rel}:\n{r.stderr or r.stdout}", file=sys.stderr)
    sys.exit(2)
print(json.dumps({"suppressOutput": True, "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": f"Auto-rebuilt site: {r.stdout.strip()}"}}))
