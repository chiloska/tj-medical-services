---
name: sprint-plan
description: Plan the next one-week sprint - create a "Sprint N" GitHub milestone and pull the highest-priority backlog stories into it up to capacity. Use when the user says "plan the sprint", "start a sprint", "what should we do this week", or "sprint planning".
argument-hint: "[capacity in points, default 8] [sprint goal]"
---

# Sprint planning

Sprints are GitHub milestones named `Sprint N`, one week long. Points: `size:S`=1, `size:M`=2, `size:L`=3. Default capacity is **8 points** unless the user gives one.

## 1. Check state

```bash
gh api "repos/{owner}/{repo}/milestones?state=all&per_page=100" --jq '.[] | [.number,.title,.state,.due_on,.open_issues,.closed_issues] | @tsv'
gh issue list --state open --limit 200 --json number,title,labels,milestone
```

- If an open `Sprint N` milestone still has open issues, ask whether to finish it first (`/retro` closes it and carries work over) or plan alongside it.
- The backlog is the open issues with **no milestone**.

## 2. Propose the sprint

Sort the backlog by priority (high, medium, low), then bugs before stories, then smaller first. Fill up to capacity. Flag:
- unsized issues: estimate a size and say so
- `size:L` issues: suggest splitting with `/story` before committing to them
- dependencies between issues (e.g. a price change that must land before the Retell prompt update)

Present: sprint name (next N), dates (today to today+7), a one-sentence sprint goal, the chosen issues with points and total, and what stays in the backlog. Wait for the user to confirm or adjust.

## 3. Apply

```bash
gh api repos/{owner}/{repo}/milestones -f title="Sprint N" -f due_on="YYYY-MM-DDT23:59:59Z" -f description="Goal: ..."
gh issue edit <n> --milestone "Sprint N"            # for each chosen issue
gh issue edit <n> --add-label size:M                # if you estimated a missing size
```

Report the milestone URL and the committed points. The SessionStart hook shows this sprint's progress in each new session.
