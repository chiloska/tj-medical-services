---
name: retro
description: Close out a sprint - compute delivered vs committed points, run a short retrospective, carry unfinished issues forward, record notes in docs/retros/, and close the milestone. Use when the user says "retro", "end the sprint", "close the sprint", or "sprint review".
argument-hint: "[Sprint N - defaults to the earliest-due open sprint]"
---

# Sprint review and retrospective

## 1. Review: facts first

```bash
gh api "repos/{owner}/{repo}/milestones?state=open&sort=due_on&direction=asc" --jq '.[0] | [.number,.title,.due_on,.description] | @tsv'
gh issue list --milestone "<sprint>" --state all --json number,title,state,labels,closedAt
gh pr list --state merged --search "milestone:\"<sprint>\"" --json number,title,mergedAt
git log --since="<sprint start>" --pretty="%h %s" main
```

Work out committed and delivered points (from `size:1|2|3|5`; legacy S=1, M=2, L=3), which issues are unfinished, and whether the sprint goal in the milestone description was met. Look back at earlier `docs/retros/*.md` files to see how velocity has trended.

## 2. Retrospective

Ask the user for their take, or draft it from the evidence and let them edit:
- **Went well**
- **Didn't go well**: missed stories, stories that grew mid-sprint, hook or build friction
- **Action items**: at most 3 concrete changes. Each one becomes a `type:chore` issue through `/story`, or an edit to CLAUDE.md or a skill.

## 3. Record and close (confirm with the user first)

Write `docs/retros/sprint-N.md` with the dates, the goal, committed and delivered points, the issue list, and the three retro sections. Commit it on a branch or directly to main, whichever the user prefers.

For unfinished issues, ask: carry over to the next sprint, or return to the backlog?

```bash
gh issue edit <n> --milestone "Sprint N+1"     # carry over (create the milestone with /sprint-plan if needed)
gh issue edit <n> --remove-milestone           # back to the backlog
gh api -X PATCH repos/{owner}/{repo}/milestones/<number> -f state=closed
```

Finish by suggesting `/sprint-plan` for the next sprint, using this sprint's delivered points as the capacity.
