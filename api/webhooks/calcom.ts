// POST /api/webhooks/calcom: WhatsApp confirmation / reschedule / cancellation for Cal.com bookings.
// Once the signature is valid, always answer 200 so Cal.com doesn't retry business-rule skips;
// 500 only for transient Twilio failures, where a retry is wanted.
import { claim, release } from '../../lib/notifications/dedupe';
import { json, log } from '../../lib/notifications/log';
import { maskPhone, toE164 } from '../../lib/notifications/phone';
import { apptName, detectLanguage, displayName, eventType, formatAppointmentTime, locationText } from '../../lib/notifications/rules';
import type { TemplateKind, TemplateVars } from '../../lib/notifications/templates';
import { verifyCalcomSignature } from '../../lib/notifications/verify';
import { sendWhatsApp } from '../../lib/notifications/whatsapp';

const TRIGGERS: Record<string, TemplateKind> = {
  BOOKING_CREATED: 'confirm',
  BOOKING_RESCHEDULED: 'reschedule',
  BOOKING_CANCELLED: 'cancel',
};

interface CalAttendee {
  name?: unknown;
  phoneNumber?: unknown;
  language?: { locale?: unknown };
}

interface CalPayload {
  uid?: unknown;
  eventTypeId?: unknown;
  startTime?: unknown;
  attendees?: CalAttendee[];
  responses?: { attendeePhoneNumber?: { value?: unknown }; name?: { value?: unknown } };
  videoCallData?: { url?: unknown };
  metadata?: { videoCallUrl?: unknown };
}

export async function POST(request: Request): Promise<Response> {
  const raw = await request.text();
  const secret = process.env.CALCOM_WEBHOOK_SECRET;
  if (!secret) log('calcom.config_error', { missing: 'CALCOM_WEBHOOK_SECRET' });
  if (!verifyCalcomSignature(raw, request.headers.get('x-cal-signature-256'), secret)) {
    log('calcom.unauthorized');
    return json({ ok: false, error: 'unauthorized' }, 401);
  }

  let body: { triggerEvent?: unknown; payload?: CalPayload };
  try {
    body = JSON.parse(raw);
  } catch {
    log('calcom.skipped', { reason: 'invalid_json' });
    return json({ ok: true, action: 'skipped', reason: 'invalid_json' });
  }
  if (process.env.NOTIFICATIONS_LOG_PAYLOADS === 'true') log('calcom.payload', { raw: body }); // contains patient PII

  const trigger = String(body.triggerEvent ?? '');
  const kind = TRIGGERS[trigger];
  if (!kind) {
    // Includes the "Ping test" from the Cal.com webhook settings.
    log('calcom.ignored', { trigger });
    return json({ ok: true, action: 'ignored', trigger });
  }

  const p = body.payload ?? {};
  const skip = (reason: string) => {
    log('calcom.skipped', { reason, trigger, uid: p.uid, eventTypeId: p.eventTypeId });
    return json({ ok: true, action: 'skipped', reason });
  };

  const appt = eventType(p.eventTypeId);
  if (!appt) return skip('unknown_event_type');

  const attendee = p.attendees?.[0] ?? {};
  const phone = toE164(p.responses?.attendeePhoneNumber?.value) ?? toE164(attendee.phoneNumber);
  if (!phone) return skip('invalid_phone');

  const lang = detectLanguage(attendee.language?.locale);
  const when = formatAppointmentTime(p.startTime, lang);
  if (!when) return skip('invalid_start_time');

  const vars: TemplateVars = {
    '1': displayName(p.responses?.name?.value ?? attendee.name, lang),
    '2': apptName(appt, lang),
    '3': when,
  };
  if (kind !== 'cancel') vars['4'] = locationText(appt.location, lang, p.videoCallData?.url ?? p.metadata?.videoCallUrl);

  const key = `cal:${trigger}:${String(p.uid)}:${String(p.startTime)}`;
  if (!(await claim(key))) return skip('duplicate');

  const result = await sendWhatsApp(phone, kind, lang, vars);
  log('calcom.result', { trigger, uid: p.uid, appt: appt.key, lang, to: maskPhone(phone), ...result });

  switch (result.status) {
    case 'sent':
    case 'dry_run':
      return json({ ok: true, action: kind, sid: result.sid });
    case 'skipped':
      await release(key); // config problem: let a redelivery try again once it's fixed
      return json({ ok: true, action: 'skipped', reason: result.reason });
    case 'failed':
      await release(key);
      return result.transient
        ? json({ ok: false, action: 'failed', error: result.error }, 500)
        : json({ ok: true, action: 'failed', error: result.error });
  }
}
