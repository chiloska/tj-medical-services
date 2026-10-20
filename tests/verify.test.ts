import { createHmac } from 'node:crypto';
import { describe, expect, it } from 'vitest';
import { RETELL_MAX_AGE_MS, verifyCalcomSignature, verifyRetellSignature } from '../lib/notifications/verify';

const hmac = (key: string, msg: string) => createHmac('sha256', key).update(msg).digest('hex');

describe('verifyCalcomSignature', () => {
  const secret = 'cal-secret';
  const body = '{"triggerEvent":"BOOKING_CREATED","payload":{"name":"José"}}';

  it('accepts a valid signature', () => {
    expect(verifyCalcomSignature(body, hmac(secret, body), secret)).toBe(true);
  });
  it('rejects a tampered body', () => {
    expect(verifyCalcomSignature(body.replace('José', 'Jose'), hmac(secret, body), secret)).toBe(false);
  });
  it('rejects the wrong secret, a missing header and a missing secret', () => {
    expect(verifyCalcomSignature(body, hmac('other', body), secret)).toBe(false);
    expect(verifyCalcomSignature(body, null, secret)).toBe(false);
    expect(verifyCalcomSignature(body, hmac(secret, body), undefined)).toBe(false);
  });
  it('rejects malformed digests without throwing', () => {
    expect(verifyCalcomSignature(body, 'not-hex', secret)).toBe(false);
    expect(verifyCalcomSignature(body, 'abcd', secret)).toBe(false);
  });
});

describe('verifyRetellSignature', () => {
  const key = 'key_retell';
  const body = '{"name":"send_whatsapp_info","args":{}}';
  const now = 1_790_000_000_000;
  const sign = (ts: number, b = body) => `v=${ts},d=${hmac(key, b + ts)}`;

  it('accepts a fresh, valid signature', () => {
    expect(verifyRetellSignature(body, sign(now - 1000), key, now)).toBe(true);
  });
  it('rejects a tampered body', () => {
    expect(verifyRetellSignature(body + ' ', sign(now), key, now)).toBe(false);
  });
  it('rejects a stale or far-future timestamp', () => {
    expect(verifyRetellSignature(body, sign(now - RETELL_MAX_AGE_MS - 1), key, now)).toBe(false);
    expect(verifyRetellSignature(body, sign(now + RETELL_MAX_AGE_MS + 1), key, now)).toBe(false);
  });
  it('rejects a changed timestamp, wrong key and malformed headers', () => {
    expect(verifyRetellSignature(body, sign(now).replace(`v=${now}`, `v=${now - 1}`), key, now)).toBe(false);
    expect(verifyRetellSignature(body, sign(now), 'key_other', now)).toBe(false);
    expect(verifyRetellSignature(body, `d=${hmac(key, body + now)}`, key, now)).toBe(false);
    expect(verifyRetellSignature(body, null, key, now)).toBe(false);
  });
});
