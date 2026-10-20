// End-to-end route tests in dry-run mode: nothing is sent to Twilio.
import { createHmac } from 'node:crypto';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { POST as calcom } from '../api/webhooks/calcom';
import { POST as retell } from '../api/retell/whatsapp';
import { CLINIC } from '../lib/notifications/clinic.generated';

const CAL_SECRET = 'cal-secret';
const RETELL_KEY = 'key_retell';
const hmac = (key: string, msg: string) => createHmac('sha256', key).update(msg).digest('hex');

let logs: Array<Record<string, any>>;

beforeEach(() => {
  vi.stubEnv('NOTIFICATIONS_DRY_RUN', 'true');
  vi.stubEnv('CALCOM_WEBHOOK_SECRET', CAL_SECRET);
  vi.stubEnv('RETELL_API_KEY', RETELL_KEY);
  vi.stubEnv('UPSTASH_REDIS_REST_URL', '');
  vi.stubEnv('KV_REST_API_URL', '');
  logs = [];
  vi.spyOn(console, 'log').mockImplementation((line: string) => logs.push(JSON.parse(line)));
});
afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

const dryRuns = () => logs.filter((l) => l.event === 'whatsapp.dry_run');
let uid = 0;

function calRequest(body: unknown, signature?: string) {
  const raw = JSON.stringify(body);
  return new Request('https://x/api/webhooks/calcom', {
    method: 'POST',
    headers: { 'x-cal-signature-256': signature ?? hmac(CAL_SECRET, raw) },
    body: raw,
  });
}

function booking(trigger: string, overrides: Record<string, unknown> = {}) {
  return {
    triggerEvent: trigger,
    payload: {
      uid: `booking-${++uid}`,
      eventTypeId: 7564958,
      startTime: '2026-10-23T17:00:00Z',
      attendees: [{ name: 'Ana López', email: 'ana@example.com', timeZone: 'America/Los_Angeles', language: { locale: 'en' } }],
      responses: { attendeePhoneNumber: { value: '+1 619 555 0100' }, name: { value: 'Ana López' } },
      ...overrides,
    },
  };
}

describe('POST /api/webhooks/calcom', () => {
  it('sends the confirmation template for a new booking', async () => {
    const res = await calcom(calRequest(booking('BOOKING_CREATED')));
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ ok: true, action: 'confirm', sid: 'dry-run' });
    expect(dryRuns()).toHaveLength(1);
    expect(dryRuns()[0]).toMatchObject({
      to: '+16195550100',
      kind: 'confirm',
      lang: 'en',
      vars: { '1': 'Ana López', '2': 'dental evaluation', '3': 'Fri, Oct 23, 10:00 AM', '4': CLINIC.tj_address },
    });
  });

  it('uses Spanish and the video link for a Spanish video booking', async () => {
    const body = booking('BOOKING_CREATED', {
      eventTypeId: 7564959,
      attendees: [{ name: 'Luis', language: { locale: 'es-MX' }, phoneNumber: '+52 664 555 0100' }],
      responses: { name: { value: 'Luis' } },
      videoCallData: { url: 'https://app.cal.com/video/xyz' },
    });
    await calcom(calRequest(body));
    expect(dryRuns()[0]).toMatchObject({
      to: '+526645550100', // fell back to attendees[0].phoneNumber
      lang: 'es',
      vars: { '2': 'consulta de cirugía para bajar de peso', '3': 'viernes 23 de octubre, 10:00 a.m.', '4': 'Videollamada gratuita: https://app.cal.com/video/xyz' },
    });
  });

  it('maps reschedule and cancel, and leaves the location out of cancellations', async () => {
    await calcom(calRequest(booking('BOOKING_RESCHEDULED', { startTime: '2026-10-24T18:00:00Z' })));
    await calcom(calRequest(booking('BOOKING_CANCELLED')));
    const [moved, cancelled] = dryRuns();
    expect(moved).toMatchObject({ kind: 'reschedule', vars: { '3': 'Sat, Oct 24, 11:00 AM' } });
    expect(cancelled.kind).toBe('cancel');
    expect(cancelled.vars['4']).toBeUndefined();
  });

  it('sends only once when Cal.com redelivers the same webhook', async () => {
    const body = booking('BOOKING_CREATED');
    await calcom(calRequest(body));
    const res = await calcom(calRequest(body));
    expect(await res.json()).toEqual({ ok: true, action: 'skipped', reason: 'duplicate' });
    expect(dryRuns()).toHaveLength(1);
  });

  it.each([
    ['unknown_event_type', { eventTypeId: 999 }],
    ['invalid_phone', { responses: { attendeePhoneNumber: { value: '6195550100' } } }],
    ['invalid_start_time', { startTime: 'soon' }],
  ])('skips with 200 on %s', async (reason, overrides) => {
    const res = await calcom(calRequest(booking('BOOKING_CREATED', overrides)));
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ ok: true, action: 'skipped', reason });
    expect(dryRuns()).toHaveLength(0);
  });

  it('answers the ping test with 200', async () => {
    const res = await calcom(calRequest({ triggerEvent: 'PING', payload: {} }));
    expect(res.status).toBe(200);
    expect((await res.json()).action).toBe('ignored');
  });

  it('rejects a bad signature or a tampered body with 401', async () => {
    expect((await calcom(calRequest(booking('BOOKING_CREATED'), 'f'.repeat(64)))).status).toBe(401);
    const signed = calRequest(booking('BOOKING_CREATED'));
    const tampered = new Request(signed.url, {
      method: 'POST',
      headers: signed.headers,
      body: (await signed.text()).replace('Ana', 'Eve'),
    });
    expect((await calcom(tampered)).status).toBe(401);
    expect(dryRuns()).toHaveLength(0);
  });

  it('rejects everything with 401 when the secret is not configured', async () => {
    vi.stubEnv('CALCOM_WEBHOOK_SECRET', '');
    expect((await calcom(calRequest(booking('BOOKING_CREATED')))).status).toBe(401);
  });
});

let callId = 0;

function retellRequest(args: Record<string, unknown>, call: Record<string, unknown> = {}, ts = Date.now(), key = RETELL_KEY) {
  const raw = JSON.stringify({ name: 'send_whatsapp_info', call: { call_id: `call-${++callId}`, from_number: '+16195550100', ...call }, args });
  return new Request('https://x/api/retell/whatsapp', {
    method: 'POST',
    headers: { 'x-retell-signature': `v=${ts},d=${hmac(key, raw + ts)}` },
    body: raw,
  });
}

describe('POST /api/retell/whatsapp', () => {
  it('sends the address to the calling number', async () => {
    const res = await retell(retellRequest({ info_type: 'tijuana_clinic_address', patient_name: 'Ana', language: 'en' }));
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ result: 'sent', message: "Sent to the WhatsApp number you're calling from." });
    expect(dryRuns()[0]).toMatchObject({ to: '+16195550100', kind: 'address', lang: 'en', vars: { '1': 'Ana', '2': CLINIC.tj_address } });
  });

  it('speaks Spanish and uses the Spanish fallback name', async () => {
    const res = await retell(retellRequest({ info_type: 'san_diego_office_address', patient_name: '', language: 'es' }));
    expect((await res.json()).message).toBe('Se lo envié al WhatsApp del número desde el que llama.');
    expect(dryRuns()[0]).toMatchObject({ lang: 'es', vars: { '1': 'estimado paciente', '2': CLINIC.sd_address } });
  });

  it('ignores any destination number in the args', async () => {
    await retell(retellRequest({ info_type: 'tijuana_clinic_address', language: 'en', to: '+16195559999', phone: '+16195559999' }));
    expect(dryRuns()[0].to).toBe('+16195550100');
  });

  it('reads the address back when the call has no phone number (web call)', async () => {
    const res = await retell(retellRequest({ info_type: 'tijuana_clinic_address', language: 'en' }, { from_number: undefined }));
    expect(await res.json()).toEqual({
      result: 'failed',
      message: `I couldn't send a WhatsApp message from this call. Please write down the address instead. The address is ${CLINIC.tj_address}.`,
    });
    expect(dryRuns()).toHaveLength(0);
  });

  it('refuses unsupported info types', async () => {
    const res = await retell(retellRequest({ info_type: 'prices', language: 'en' }));
    expect((await res.json()).result).toBe('failed');
    expect(dryRuns()).toHaveLength(0);
  });

  it('sends once per call and info type', async () => {
    const raw = retellRequest({ info_type: 'tijuana_clinic_address', language: 'en' });
    const body = await raw.text();
    const headers = raw.headers;
    await retell(new Request(raw.url, { method: 'POST', headers, body }));
    const again = await retell(new Request(raw.url, { method: 'POST', headers, body }));
    expect((await again.json()).result).toBe('sent');
    expect(dryRuns()).toHaveLength(1);
  });

  it('rejects stale, wrong-key and missing signatures with 401', async () => {
    const args = { info_type: 'tijuana_clinic_address', language: 'en' };
    expect((await retell(retellRequest(args, {}, Date.now() - 6 * 60 * 1000))).status).toBe(401);
    expect((await retell(retellRequest(args, {}, Date.now(), 'key_other'))).status).toBe(401);
    expect((await retell(new Request('https://x', { method: 'POST', body: '{}' }))).status).toBe(401);
    expect(dryRuns()).toHaveLength(0);
  });
});
