# How we work (aim-kit working agreement v1)

<!-- aim-kit:agreement v1. Everything above "## Project-specific" belongs to the kit and is refreshed by
     /aim-kit:install --upgrade; change it in chiloska/ai-manager kit/aim-kit/templates/agile.md. -->

The shared working agreement of every AI Company project (D-007 in chiloska/ai-manager). Base: Video Generator's
agreement (time boxes, lanes, delegation, Scrum of Scrums), with the autonomy model and budget split from
[ai-manager docs/05-autonomy-and-operations.md](https://github.com/chiloska/ai-manager/blob/main/docs/05-autonomy-and-operations.md)
applied. A project overrides only what it lists under "Project-specific" below.

## Roles

| Role | Who | Decides |
|---|---|---|
| Product Owner (PO) | The user | Backlog order, sprint scope, story acceptance, every **merge**, deploy, credit spend, publication |
| Scrum Master / orchestrator | Main Claude session (interactive) or the scheduled sprint runner | Runs ceremonies, dispatches agents, keeps the board, enforces time boxes |
| PO advisor | `assistant-po` agent | Routine calls inside the delegation below; parks everything else on `Needs PO` |
| Builders and reviewers | `business-analyst`, `architect`, `developer`, `qa-engineer`, `security-reviewer`, `compliance-reviewer`, `release-engineer` agents; ChatGPT through Codex (`/review-gpt`) as second reviewer | Their step only |

## The board

- **System of record:** GitHub Issues in the project's repo, all on the private Project
  [AI Company Portfolio](https://github.com/users/chiloska/projects/1). One issue per story.
- **Fields on the Project:** `Project`, `Stage` (Refine · Ready · Sprint · Doing · Review · Done · Blocked), `Points`,
  `Sprint`, `Needs PO` (Yes/No), `Team`, `Due`.
- **Labels in every repo:** `type:story` `type:chore` `type:spike` `type:bug` `po-task` · `size:1` `size:2` `size:3`
  `size:5` · `priority:high|medium|low` · `needs-po` · `agent:go` (an agent may start it unattended) · `autonomy:L1`
  `autonomy:L2` `autonomy:L3`.
- **IDs:** the issue title starts with the story ID (`AM-101 aim CLI ...`); epics own a hundred (E1 → `AM-1xx`).
  Cross-project references are written `<repo>#<n>`.
- **Sprints** are GitHub milestones `Sprint NN`; scope-boxed (a sprint ends when its committed scope is Done or the
  PO closes it).
- **Story files** `tasks/stories/<ID>.md` keep the hand-off log (design → build → QA → reviews → DoD) so a fresh or
  unattended session can resume. The issue links to the file; the PR body repeats the summary.

## Autonomy levels (who may start what)

| Level | Starts | Ends in | Allowed for |
|---|---|---|---|
| L1 delegated | PO, in a session (`/story <ID>`) | hand-off in the story file, then a PR | Anything; default for work that needs this PC (GPU, local stacks) |
| L2 unattended | PO adds `agent:go`, or the sprint runner picks it | a **draft PR** + a comment on the issue | Stories labelled `autonomy:L2` that are Ready, ≤3 points, no credit spend, no prompt/legal/compliance content |
| L3 event-driven | schedule or GitHub event | a comment, an issue, or a PR | The automations in the automation register ([ai-manager `docs/automations.md`](https://github.com/chiloska/ai-manager/blob/main/docs/automations.md)) |

**Every unattended run must end by writing where the PO looks** (PR, issue comment, digest). There is no inbox.

## Definition of Ready
- Story format with testable acceptance criteria, including the failure case.
- Size 1, 2, 3 or 5; anything bigger is split.
- Dependencies and open PO questions resolved or listed; credit cost stated (none / estimate approved).
- Live impact stated: does it touch a running service, a deploy, or another project's files?
- Autonomy level chosen (`autonomy:L1|L2|L3`).

## Definition of Done
- All acceptance criteria pass, with evidence in the story file (commands and their result lines).
- Tests or checks for the new behaviour exist and pass.
- `security-reviewer` has no open Critical/High; for code changes, `/review-gpt` has no open High.
- Docs, registry and runbooks updated where the change touches them.
- PR open with `Closes #<n>`; the PO merges. **The PO's merge is the acceptance.** Merge to `main` is also the staging
  deploy decision where staging auto-deploys (D-004 update, Q17).
- Leftovers removed: scratch files, test stacks, worktrees.

## Branches, commits, merges
- One branch per story: `<type>/<ID>-<slug>` (`feat/AM-101-aim-status`). Agents commit and push to their branch and
  open a PR; **they never push to `main`**.
- GitHub Free cannot protect `main` on private repos (verified 2026-10-25), so the guard is local and in the agents'
  permissions: a `pre-push` hook rejects pushes to `main` unless `ALLOW_MAIN_PUSH=1` is set by the PO, and the kit's
  settings deny `git push * main`. Cloud sessions push only to `claude/*` branches.
- No exceptions: record-keeping (progress, registry, decisions, runbook records) also reaches `main` through a PR,
  batched into the story PR it belongs to. Agents may push story branches freely; the deny rules block `main`,
  `production`, force pushes and `gh pr merge`, so merging stays with the PO (verified 2026-10-25: the rule refused a
  push to `main` before git ran). Rules exist for both the Bash and PowerShell tools. Side effect: a branch name ending
  in `main` is refused too, so don't name branches that way.
- Commit messages: conventional (`feat:`, `fix:`, `chore:`, `docs:`, `infra:`), story ID included, attribution line
  from the session's instructions.

## Cadence
| Ceremony | How | When |
|---|---|---|
| Daily digest | automation A1 (email) | 07:00 |
| Stand-up | `/standup` | start of every interactive session |
| Refinement | `/refine` | any time; top of the backlog must stay Ready |
| Sprint planning | `/sprint-plan` (PO approves scope) | start of a sprint |
| Story delivery | `/story <ID>` (L1) or `agent:go` (L2) | per story |
| Sprint review + retro | `/sprint-review` | when the committed scope is Done |
| Portfolio review | `assistant-po` with the PO | weekly |

## Time boxes and hang checks (from Video Generator, 2026-10-23)
Review agents 45 min; BA or architect 1 h; build 1 h per point; QA 2 h. Every brief states its box. At the box the
Scrum Master checks the lane's git status and newest files and decides: continue (new check time), ask for a
hand-off, or stop. Hard stop at twice the box. Agents hand back as soon as the report is written and never poll.

## Token policy (D-004 update)
- Max 5x subscription for interactive and story work; the weekly window is the cap. The sprint runner skips a day
  when the window is above 80 %.
- Automations run on the monthly Console API credit (USD 100) with an API key, Haiku by default, Sonnet for reviews.
- Models by role: Opus only for `architect` and `security-reviewer`; Sonnet for builders, BA, QA, compliance; Haiku
  for summaries and board sync. Stories of 2 points or less use the lean path (orchestrator builds inline, only the
  security review runs as an agent).
- Unattended runs always set a turn cap; headless runs add `--max-budget-usd`.

## Delegation to `assistant-po`
May decide: order of refinement candidates, accepting or declining review findings below High, stopping a hung agent,
small scope cuts that keep a deadline, starting the next sprint from Ready items when the PO has pre-approved it.
Must escalate (≤3 questions at once, each with a recommendation): merges, deploys, any spend, legal/medical/
compliance wording, anything touching a live service, a deadline that slips.

## Project-specific
- Board: repo `chiloska/tj-medical-services` (**public**: no patient data, no secret values, only Bitwarden entry
  names); every issue on [Project 1](https://github.com/users/chiloska/projects/1) with `Project` =
  `tj-medical-services`. IDs: issue numbers (`#<n>`); no epics yet. Installed by AM-206 (chiloska/ai-manager#13).
- **Override: this repo keeps its own skill cycle.** `/story` (write an issue) → `/sprint-plan` → `/start-story` →
  `/done` → `/standup` → `/retro`, with branches `story/<n>-<slug>`. Reason: the `/done` Definition of Done checks
  this site's specifics (rebuild, EN/ES parity, fact consistency across `src/` and `retell/`, browser check). The
  kit's skills are available as `/aim-kit:<name>`; which one to use when both exist is in `CLAUDE.md`
  ("Agile workflow").
- **Override: sprints are one week**, milestones `Sprint N` (no zero padding), default capacity 8 points. Reason:
  the existing `/sprint-plan` and SessionStart hook use that.
- Labels: the kit's `type:*` and `size:1|2|3|5` are the standard. Legacy `story`/`bug`/`chore` and `size:S|M|L`
  (= 1/2/3 points) were never created on GitHub (no issues existed at install time, 2026-10-27); the skills still
  read them if they ever appear. `in-progress` stays this repo's own "Doing" marker.
