# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A bilingual (EN/ES) static website for a **fictional** cross-border medical clinic (Tijuana clinic + San Ysidro/San Diego office). Its main purpose is to serve as the knowledge base for a Retell AI voice receptionist ("Sofía"). All names, phones, prices and doctors are illustrative; the footer carries a disclaimer saying so — keep it.

## Commands

```bash
python3 src/build.py      # regenerate everything in public/ (stdlib only, no dependencies)
python3 src/serve.py      # preview at http://localhost:8000 with Vercel-style clean URLs (/prices -> prices.html)
npm test                  # vitest: WhatsApp functions (signatures, phones, rules, both routes in dry-run)
npx vitest run tests/phone.test.ts -t "rejects"   # single file / test name
npm run typecheck         # tsc --noEmit
```

Deploy is Vercel serving `public/` as-is (`vercel.json`: empty build command, `cleanUrls`, no trailing slash), so **built output is committed** — always rebuild and commit `public/` together with source changes. npm is only for the functions in `api/`; the site build stays stdlib Python.

## Claude Code tooling (`.claude/`, `.mcp.json`)

- **Hooks** (`.claude/settings.json`, scripts in `.claude/hooks/`): editing a `src/*.py` file auto-runs the build; Edit/Write to generated files (`public/**/*.html`, `sitemap.xml`, `robots.txt`, `llms.txt`) is blocked — `styles.css`, `site.js`, `favicon.svg` stay editable; session start prints the current sprint's open stories.
- **MCP servers**: `playwright` (browser checks against `src/serve.py`), `vercel` (deploy/preview status; OAuth on first use). GitHub is accessed with the `gh` CLI, not an MCP.

## Architecture

- `src/data.py` — structured clinic facts: `CLINIC` (contact info + `url`), `HOURS`, `SERVICES`, `PRICES`, `TEAM`, `FAQ`. Bilingual content is stored side-by-side, either as `{"en": {...}, "es": {...}}` dicts (SERVICES, HOURS) or as positional tuples with EN/ES pairs (PRICES rows `(name_en, name_es, usd, note_en, note_es)`, TEAM `(name, role_en, role_es, bio_en, bio_es)`, FAQ `(q_en, q_es, a_en, a_es)`). A price of `0` renders as "Free"/"Gratis".
- `src/build.py` — one `p_<page>(lang)` function per page returning `(title, description, body_html, jsonld_or_None)`, wrapped by `layout()`. `PAGES` defines slug order, nav labels and which pages appear in the main nav; `BUILDERS` maps slugs to functions. Inside page functions, `t(en, es)` picks the string for the current language. `main()` writes `public/<slug>.html` (EN) and `public/es/<slug>.html` (ES), plus `404.html`, `sitemap.xml`, `robots.txt` and `llms.txt`.
- `public/styles.css`, `public/site.js`, `public/favicon.svg` are hand-written (not generated). `site.js` only turns the contact form into a pre-filled `mailto:` (no backend).
- `retell/agent-prompt.md` — the Retell agent prompt, maintained by hand.

### WhatsApp functions (`api/`, `lib/notifications/`)

Vercel Functions (Node runtime, Web `Request`/`Response` handlers exporting `POST`) send Twilio WhatsApp templates: `api/webhooks/calcom.ts` (Cal.com booking created/rescheduled/cancelled) and `api/retell/whatsapp.ts` (Retell custom function `send_whatsapp_info`). Both read the raw body and verify an HMAC signature before anything else. Shared logic is in `lib/notifications/`: `rules.ts` maps Cal.com event type IDs to appointment names and locations, `templates.ts` holds the approved template text (must match Twilio exactly) and the `WA_TPL_*` env lookup, `whatsapp.ts` sends (honors `NOTIFICATIONS_DRY_RUN`), `dedupe.ts` (Upstash Redis if configured, else in-memory).

- Addresses come from `lib/notifications/clinic.generated.ts`, which `src/build.py` writes from `src/data.py` — rebuild after changing contact data; don't edit it.
- Keep relative imports extensionless and the package CommonJS (no `"type": "module"`) so Vercel's TS compile resolves them.
- External setup (Twilio templates, env vars, Cal.com webhook, Retell function) and the manual test plan: `docs/whatsapp-notifications.md`.

### Facts are not only in data.py

Despite the "single source of truth" comment, a lot of factual copy is hardcoded in `build.py` page functions: deposits, cancellation rules, guarantees, payment methods, shuttle times, package inclusions, travel documents, and the JSON-LD street addresses in `p_index`. The `/reference` page (`p_reference`) restates most of these in dense prose for the AI receptionist. When changing any fact, grep for it across `src/build.py`, `src/data.py` and `retell/agent-prompt.md` and update every occurrence, in **both** languages.

### The reference page and receptionist rules

`/reference` and `/es/reference` are the pages Retell ingests, so they must contain every fact the agent may need. The "Rules for the virtual receptionist" section in `p_reference` and the safety rules in `retell/agent-prompt.md` describe the same policies (911 for emergencies, no diagnosis/candidacy/medication advice, prices are always "starting at", never sell medical-lane passes, never promise wait times) — keep them consistent.

## Agile workflow

GitHub Issues on `chiloska/tj-medical-services` (public — no real patient data in issues) is the backlog; one-week sprints are milestones named `Sprint N`.

- Labels: type `story` / `bug` / `chore`; `size:S|M|L` = 1/2/3 points; `priority:high|medium|low`; `in-progress` while being worked.
- Branches `story/<n>-<slug>` off `main`; PRs say `Closes #<n>`; Vercel builds a preview per PR.
- Skills, in cycle order: `/story` (write a story) → `/sprint-plan` → `/start-story` → `/done` (Definition of Done check + PR) → `/standup` (read-only status) → `/retro` (close sprint, notes in `docs/retros/`).

## Before going live

Replace the placeholder phone numbers, email and `CLINIC["url"]` (used in canonical/hreflang links, sitemap, robots.txt and llms.txt) in `src/data.py`, then rebuild.
