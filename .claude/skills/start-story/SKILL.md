---
name: start-story
description: Pick up a GitHub issue from the current sprint - create its branch, mark it in progress, and implement it against its acceptance criteria. Use when the user says "work on #12", "start the next story", "pick up a ticket", or "what's next".
argument-hint: "[issue number - omit to take the top open story in the sprint]"
---

# Start a story

## 1. Choose the issue

If no number is given, take the highest-priority open issue in the current sprint (earliest-due open milestone) that isn't labeled `in-progress`:

```bash
gh api "repos/{owner}/{repo}/milestones?state=open&sort=due_on&direction=asc" --jq '.[0].title'
gh issue list --milestone "<title>" --state open --json number,title,labels
```

Read it in full: `gh issue view <n> --comments`. If its acceptance criteria are missing or vague, propose criteria and confirm them before writing code.

## 2. Set up

Make sure the working tree is clean (`git status`); if it isn't, ask what to do with the existing changes. Then:

```bash
git switch main && git pull --ff-only
git switch -c story/<n>-<short-slug>
gh issue edit <n> --add-label in-progress
```

## 3. Implement

Follow CLAUDE.md. In particular:
- Change facts in `src/data.py` or the page functions in `src/build.py`, never in `public/`. The project hooks block hand edits to generated files and rebuild `public/` after every `src/` edit.
- A fact change means grepping `src/build.py`, `src/data.py` and `retell/agent-prompt.md` for every copy, in both languages.
- Keep the fictional-clinic disclaimer.

Work through the acceptance criteria one at a time. Commit in small steps with messages that reference the issue (`Update shuttle hours (#<n>)`), committing `src/` and the regenerated `public/` together.

When every criterion is met, run `/done` to check the Definition of Done and open the PR.
