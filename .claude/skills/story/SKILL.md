---
name: story
description: Turn a feature request, content change or bug into a GitHub issue user story with acceptance criteria, size and priority, and add it to the backlog. Use when the user says "add a story", "new ticket", "backlog this", "write a user story", or describes work to be done later.
argument-hint: "<what needs to change>"
---

# Write a user story

The backlog is GitHub Issues on this repo (see "Agile workflow" in CLAUDE.md). The repo is **public**: never put real patient data, credentials or private contact details in an issue.

## 1. Understand the change

Read enough of `src/data.py`, `src/build.py` and `retell/agent-prompt.md` to know which files, pages and languages the change touches. If the request is ambiguous in a way that changes the acceptance criteria, ask one question; otherwise make a sensible assumption and note it in the issue.

## 2. Draft the issue

Title: short, imperative ("Add Saturday hours for the San Diego office").

Body:

```markdown
**As a** <prospective patient | caller to the AI receptionist | clinic coordinator | site maintainer>
**I want** <capability>
**So that** <outcome>

### Acceptance criteria
- [ ] <observable, testable behavior>
- [ ] Copy exists in both English and Spanish
- [ ] /reference and /es/reference reflect the change            <- only if it is a clinic fact
- [ ] retell/agent-prompt.md updated                              <- only if agent behavior/rules change

### Notes
Files likely touched: ...
Assumptions: ...
```

Drop the conditional criteria lines that don't apply (and the `<-` hints).

Pick labels:
- type: `type:story` (new value), `type:bug` (something wrong), `type:chore` (tooling/maintenance) or `type:spike` (time-boxed investigation)
- size: `size:1` (≤ half a day), `size:2` (about a day), `size:3` (two days), `size:5` (too big — suggest splitting into smaller stories)
- priority: `priority:high`, `priority:medium` or `priority:low`

## 3. Create it

Show the user the draft (title, labels, body). Create it once they confirm, or straight away if they already asked you to create it.

The `type:*`, `size:*` and `priority:*` labels come from aim-kit (`/aim-kit:install` creates them; don't recreate or `--force` them). Only `in-progress` is this repo's own; create it if `gh label list` doesn't show it:

```bash
gh label create in-progress --color fbca04 --description "Being worked on"
```

```bash
gh issue create --title "<title>" --label type:story,size:2,priority:medium --body-file <tmpfile>
```

Write the body to a temp file in your scratchpad rather than inlining it, so quoting doesn't break. Do not assign a milestone here; `/sprint-plan` does that. Report the issue URL, then run `/aim-kit:board-sync` so the issue lands on Project 1 (`Project` = tj-medical-services, Stage, Points).
