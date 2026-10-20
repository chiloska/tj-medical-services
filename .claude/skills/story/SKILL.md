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
- type: `story` (new value), `bug` (something wrong), or `chore` (tooling/maintenance)
- size: `size:S` (≤ half a day, 1 pt), `size:M` (about a day, 2 pts), `size:L` (3 pts — suggest splitting into smaller stories)
- priority: `priority:high`, `priority:medium` or `priority:low`

## 3. Create it

Show the user the draft (title, labels, body). Create it once they confirm, or straight away if they already asked you to create it.

If labels are missing (`gh label list`), create them first:

```bash
gh label create story --color 1d76db --description "User story" --force
gh label create chore --color c5def5 --description "Tooling / maintenance" --force
gh label create in-progress --color fbca04 --description "Being worked on" --force
for s in S M L; do gh label create "size:$s" --color bfdadc --force; done
for p in high medium low; do gh label create "priority:$p" --color e99695 --force; done
```

```bash
gh issue create --title "<title>" --label story,size:M,priority:medium --body-file <tmpfile>
```

Write the body to a temp file in your scratchpad rather than inlining it, so quoting doesn't break. Do not assign a milestone here; `/sprint-plan` does that. Report the issue URL.
