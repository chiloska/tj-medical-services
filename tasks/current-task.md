# Current task

_Status: blocked_
_Updated: 2026-10-20 (new-session)_
_Branch: main_

## Goal
Roll out WhatsApp notifications. Patients get a WhatsApp confirmation, reschedule or cancellation notice when they book on Cal.com, and Sofía (Retell) can send clinic addresses by WhatsApp during a call. All business rules live in this repo; sending goes through Twilio Content templates. The full spec is reflected in `docs/whatsapp-notifications.md`.

## Done so far
- 8 templates created and submitted by the user with `--apply` (2026-10-20); WhatsApp approval pending. SIDs: CONFIRM_EN HXbd3963cfc26af78dc70a3b82148b233b, CONFIRM_ES HX5ace98593f6b711c721aab6c31af7569, RESCHEDULE_EN HXeed1f5ec9138139b368aa939e28a5a15, RESCHEDULE_ES HX2002f02f811809e43b59cc546161c359, CANCEL_EN HXd04e255c22946071738f7387297a05c3, CANCEL_ES HX971d4efaf13d54e611e5b8288f6364cd, ADDRESS_EN HX922b0a111ffee9d1b29995616a8e99d8, ADDRESS_ES HXe60ee0ed8e2fbfc80aeefa983fa0b5a9 (verified with `--status`)
- Production deploy of `74879fb` serves both functions: unsigned POST to `/api/webhooks/calcom` and `/api/retell/whatsapp` → 401 (verified 2026-10-20)
- `scripts/create-whatsapp-templates.mjs` (`npm run wa:templates [-- --apply|--status]`) creates and submits the 8 templates through the Content API (uncommitted; verified: preview runs, 66 tests pass, typecheck clean; not yet run against Twilio)
- Routes `api/webhooks/calcom.ts` and `api/retell/whatsapp.ts`, shared `lib/notifications/*` — `74879fb` (verified: `npm test` 57 pass, `npm run typecheck` clean)
- `/reference` rules + `retell/agent-prompt.md` WhatsApp section — `74879fb` (verified: site rebuilt)
- `.env.example`, `docs/whatsapp-notifications.md` — `74879fb`

## Remaining
- [x] Create the 8 Twilio Content templates (confirm / reschedule / cancel / address × EN/ES), category Utility, using the exact text in `lib/notifications/templates.ts`; submit each for WhatsApp approval; record the HX SIDs
- [x] Vercel deploy of `api/` verified (401 on unsigned POST)
- [ ] Wait for WhatsApp approval (`npm run wa:templates -- --status`)
- [ ] User commits and pushes the uncommitted work (template script, new phone +1 (619) 349-9659, rebuilt `public/`); production still shows the old 555 number until then
- [ ] Set env vars in Vercel (Preview and Production) per `.env.example`, starting with `NOTIFICATIONS_DRY_RUN=true`
- [ ] Create the Cal.com webhook (URL, 3 triggers, secret) and run its Ping test
- [ ] Add the `send_whatsapp_info` custom function in Retell (settings in docs §4); copy the prompt section into `sofia-prompt.md`
- [ ] Run the manual test plan in `docs/whatsapp-notifications.md` §6, including the reschedule double-message check

## Blockers / errors
- The Claude Twilio connector (`twilio__search` / `twilio__retrieve`) is the read-only Twilio docs MCP. It can't call APIs; Twilio lists tools that execute API calls as planned. Templates must be created by the script (or in the Console).

## Next action
User sets Vercel env vars (Preview and Production): Twilio credentials, `TWILIO_WHATSAPP_FROM=whatsapp:+16193499659`, the 8 `WA_TPL_*` SIDs above, `RETELL_API_KEY`, `CALCOM_WEBHOOK_SECRET`, `NOTIFICATIONS_DRY_RUN=true`. Then create the Cal.com webhook (docs §3) and run its Ping test.

## Key files
- `lib/notifications/templates.ts` — approved template text and the `WA_TPL_*` env lookup (must match Twilio exactly)
- `lib/notifications/whatsapp.ts` — Twilio sender, dry run, Sandbox body fallback
- `api/webhooks/calcom.ts`, `api/retell/whatsapp.ts` — the two routes
- `docs/whatsapp-notifications.md` — external setup steps and test plan
- `.env.example` — every env var

## Notes for next session
- The repo is NOT Next.js: a static Python-generated site plus plain Vercel Functions in `api/`. Keep relative imports extensionless and the package CommonJS (no `"type": "module"`). TypeScript is pinned to `~5.9.3` because TS 7 has no JS API, which @vercel/node may need.
- Template variables: confirm/reschedule use {{1}} name, {{2}} appointment, {{3}} date/time, {{4}} location. Cancel uses {{1}}–{{3}}. Address uses {{1}} name, {{2}} address. Meta needs sample values on submission.
- Creating templates, pushing, and configuring Cal.com/Retell/Vercel are outward-facing: confirm with the user first.
- The user commits themselves; don't commit or push unless asked.
- The memory files (`progress.md`, `tasks/`, `docs/decisions.md`) are untracked. The user decides whether to commit them.
