---
name: standup
description: Read-only daily standup summary - what got done since the last working day, what is in progress, what is blocked, and whether the sprint is on track. Use when the user says "standup", "status", "where are we", or "what did we do yesterday".
---

# Standup

This skill only reads; it changes nothing on GitHub or in git.

Gather:

```bash
git log --since="yesterday" --all --pretty="%h %ad %s" --date=short    # on Monday, use --since="last friday"
gh api "repos/{owner}/{repo}/milestones?state=open&sort=due_on&direction=asc" --jq '.[0] | [.title,.due_on] | @tsv'
gh issue list --milestone "<sprint>" --state all --json number,title,state,labels,closedAt
gh pr list --state open --json number,title,headRefName,reviewDecision,statusCheckRollup
git status --short
```

Report in this shape, keeping each section to a few bullets:

- **Done**: issues closed and PRs merged since the last working day, plus notable commits
- **In progress**: open issues labeled `in-progress` or with an open PR, and their PR or check status
- **Blocked / at risk**: failing checks, PRs waiting on review, stale `in-progress` issues with no commits in 2+ days, uncommitted work in the tree
- **Sprint**: points done out of committed points (S=1, M=2, L=3), days left until the due date, and on track or at risk (compare the share of points done with the share of time elapsed)
- **Suggested next**: the top open story, to start with `/start-story`
