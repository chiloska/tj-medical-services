#!/usr/bin/env python3
"""SessionStart: print the current sprint (earliest-due open milestone) and its open stories."""
import json
import subprocess
import sys


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8", timeout=15)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return json.loads(r.stdout or "null")


try:
    milestones = gh("api", "repos/{owner}/{repo}/milestones?state=open&sort=due_on&direction=asc")
    if not milestones:
        print("Agile: no open sprint (milestone). Run /sprint-plan to start one.")
        sys.exit(0)
    m = milestones[0]
    issues = gh("issue", "list", "--milestone", m["title"], "--state", "all", "--limit", "100",
                "--json", "number,title,state,labels")
except Exception:
    sys.exit(0)  # offline or gh not authenticated: stay silent

due = (m.get("due_on") or "")[:10] or "no due date"
closed = [i for i in issues if i["state"] == "CLOSED"]
print(f"Agile: {m['title']} (due {due}) - {len(closed)}/{len(issues)} stories done.")
for i in issues:
    if i["state"] == "CLOSED":
        continue
    labels = ",".join(l["name"] for l in i["labels"] if l["name"] != "story")
    print(f"  #{i['number']} {i['title']}" + (f" [{labels}]" if labels else ""))
