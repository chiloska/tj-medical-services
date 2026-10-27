# aim-kit rules (installed by /aim-kit:install, do not edit here: change the kit and reinstall)

These rules hold in every project of the AI Company portfolio, in local sessions, background sessions and cloud
threads. The full working agreement is `docs/agile.md`.

- **No secrets in the repo**, ever: not in code, docs, examples, issue comments or commit messages. Point to the
  server file or the Bitwarden entry name. Never read `.env` files or plain-text secret notes.
- **Never push to `main`, `master` or `production`**, never force-push, never merge a PR (`gh pr merge`). Every change
  goes through a story branch `<type>/<ID>-<slug>` and a PR with `Closes #<n>`; **the PO's merge is the acceptance**.
- Never bypass the guard: no `--no-verify`, no hook overrides, no editing `.githooks/` or `.claude/settings.json` to
  loosen a rule. If a rule blocks the work, stop and say so on the issue.
- **Ask the PO first** for: deploys, spending credits (paid API calls, headless runs on an API key), stopping or
  removing containers, anything needing `sudo`, touching a live service, publishing anything.
- Changes to another project's files: only a clearly marked note or warning, never a commit there unless the PO asks.
- Every unattended run ends where the PO looks: a draft PR plus a comment on the issue. There is no inbox.
- Record-keeping (progress, decisions, story files) reaches `main` in the story's PR, never on its own.
