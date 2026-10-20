# WhatsApp notifications: setup and testing

Code: `api/webhooks/calcom.ts`, `api/retell/whatsapp.ts`, shared logic in `lib/notifications/`. These are plain Vercel Functions (Node.js runtime) living next to the static site. There is no framework.

## 1. Twilio templates

In Twilio → Content Template Builder, create these 4 templates, each in English and Spanish, with category **Utility**, and submit them for WhatsApp approval. The text must match `lib/notifications/templates.ts` exactly: the code uses that copy for dry-run logs and the Sandbox fallback.

| Template | Variables |
|---|---|
| `tjms_appointment_confirmation` | 1 name, 2 appointment, 3 date/time, 4 location |
| `tjms_appointment_rescheduled` | 1 name, 2 appointment, 3 new date/time, 4 location |
| `tjms_appointment_cancelled` | 1 name, 2 appointment, 3 date/time |
| `tjms_clinic_address` | 1 name, 2 address |

Paste each HX SID into the matching `WA_TPL_*` variable.

## 2. Environment variables

Set every key in `.env.example` in Vercel → Project → Settings → Environment Variables, for both Preview and Production. Start with `NOTIFICATIONS_DRY_RUN=true`.

While you're on the Twilio Sandbox (`TWILIO_WHATSAPP_FROM=whatsapp:+14155238886`), you can leave the template variables empty: the code then sends the same text as a free-form body. This only reaches testers who have joined the Sandbox.

For duplicate protection that works across serverless instances, add Upstash Redis from the Vercel Marketplace. Its `KV_REST_API_URL` / `KV_REST_API_TOKEN` (or `UPSTASH_REDIS_REST_*`) variables are detected automatically.

## 3. Cal.com webhook

Settings → Developer → Webhooks → New:
- Subscriber URL: `https://tj-medical-services.vercel.app/api/webhooks/calcom`
- Triggers: Booking Created, Booking Rescheduled, Booking Cancelled
- Secret: the value of `CALCOM_WEBHOOK_SECRET`
- Payload template: default

Run the Ping test; it should get a 200. For the first real booking, set `NOTIFICATIONS_LOG_PAYLOADS=true` to log the raw payload and confirm the fields (`responses.attendeePhoneNumber`, `attendees[0].language.locale`, `videoCallData.url`). Turn it off afterwards, because the payload contains patient details.

## 4. Retell custom function

Agent → Functions → + Add → Custom Function:
- Name `send_whatsapp_info`; method POST; URL `https://tj-medical-services.vercel.app/api/retell/whatsapp`
- Timeout 10000 ms, max retry 0, **Payload: args only → OFF** (the route needs `call.from_number`)
- Talk While Waiting: "One moment, I'm sending that now."
- Parameters:

```json
{
  "type": "object",
  "required": ["info_type", "language"],
  "properties": {
    "info_type": { "type": "string", "enum": ["tijuana_clinic_address", "san_diego_office_address"], "description": "Which information the caller asked to receive" },
    "patient_name": { "type": "string", "description": "Caller's first name if known, otherwise empty" },
    "language": { "type": "string", "enum": ["en", "es"], "description": "Language the caller is speaking" }
  }
}
```

Requests are verified with `RETELL_API_KEY`, which must be the key with the "webhook" badge. Add the "Sending information by WhatsApp" section from `retell/agent-prompt.md` to the live agent prompt.

## 5. Behavior worth knowing

- The WhatsApp message always goes to the booking's phone number or the caller's number. Any number in the LLM's arguments is ignored.
- Only +1 and +52 numbers are accepted. A bare 10-digit number is rejected because it could be either country, so the message is skipped (Cal.com's phone field always includes the country code).
- Cal.com responses: 401 for a bad signature; 200 for every business-rule skip (unknown event type, bad phone, duplicate, missing template); 500 only for a transient Twilio error, so Cal.com retries.
- The Retell route always returns 200 with `{ result, message }`. When sending fails, the message includes the address so Sofía can read it out.

## 6. Test plan

1. Dry run: book on the Cal.com page, then search the Vercel logs for `whatsapp.dry_run` and check the template, variables and phone.
2. Repeat with a Spanish booking, then reschedule and cancel. Check whether a reschedule also triggers a `BOOKING_CANCELLED` for the old slot; if it does, the patient gets two messages and the route needs a filter.
3. Turn dry run off and check that a real WhatsApp message arrives on a test phone.
4. Call the Retell number and book: a confirmation should arrive within about a minute. Ask "send me the Tijuana address" and check that it arrives and Sofía reads the result.
5. A bad signature on either route returns 401 (also covered by `npm test`).
