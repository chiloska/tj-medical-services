---
name: done
description: Check the current story branch against the Definition of Done (build, bilingual parity, fact consistency, browser check) and open a pull request that closes the issue. Use when the user says "done", "ready for review", "open a PR", "ship it", or after finishing a story.
argument-hint: "[issue number - inferred from the branch name if omitted]"
---

# Definition of Done

Get the issue number from the branch (`story/<n>-...`) or the argument, and read its acceptance criteria with `gh issue view <n>`. Check every item below and report each as pass, fail or not applicable. Fix the failures before opening the PR. If one can't be fixed, stop and tell the user.

## Checklist

1. **Acceptance criteria**: each criterion in the issue is met. Quote the evidence (file and line, or what the page shows).
2. **Build is clean and committed**: `python src/build.py` succeeds and then `git status --short public/` is empty, meaning the committed `public/` matches the source.
3. **Bilingual parity**: every string added or changed in `src/` has both its EN and ES versions, and the ES text is a real translation, not a copy of the English.
4. **Fact consistency**: for each fact that changed (a price, hours, phone number, policy), grep for the old value across `src/`, `retell/` and `README.md`. No stale copies may remain. Check that `public/reference.html` and `public/es/reference.html` show the new value.
5. **Receptionist rules**: if policies or safety rules changed, the "Rules for the virtual receptionist" section in `p_reference` and `retell/agent-prompt.md` still agree.
6. **Browser check**: start `python src/serve.py 8000` in the background. With the Playwright MCP, open each changed page in EN and ES at 1280px and 375px width. Confirm the change renders, nothing overflows horizontally, and the console shows no errors. Stop the server afterwards. If the Playwright MCP isn't connected, say this step was skipped. Don't report it as passed.
7. **Disclaimer intact**: the fictional-clinic note is still in the footer.

## Ship

```bash
git push -u origin HEAD
gh pr create --title "<issue title> (#<n>)" --body-file <tmpfile>
```

The PR body should contain a short summary, the checklist results, and `Closes #<n>`, and end with the attribution line required by the session. Then remove the `in-progress` label: `gh issue edit <n> --remove-label in-progress`.

Vercel builds a preview for the PR. If the Vercel MCP is connected, fetch the preview URL and include it in your report.
