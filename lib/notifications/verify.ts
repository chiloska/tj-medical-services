// Webhook signature checks. Both compare HMAC-SHA256 hex digests in constant time.
import { createHmac, timingSafeEqual } from 'node:crypto';

export const RETELL_MAX_AGE_MS = 5 * 60 * 1000;

function hmacHex(secret: string, message: string): string {
  return createHmac('sha256', secret).update(message, 'utf8').digest('hex');
}

function hexEqual(expected: string, received: string): boolean {
  if (!/^[0-9a-f]{64}$/i.test(received)) return false;
  return timingSafeEqual(Buffer.from(expected, 'hex'), Buffer.from(received, 'hex'));
}

/** Cal.com: X-Cal-Signature-256 = hex HMAC-SHA256(secret, raw body). */
export function verifyCalcomSignature(rawBody: string, header: string | null, secret: string | undefined): boolean {
  if (!secret || !header) return false;
  return hexEqual(hmacHex(secret, rawBody), header.trim().replace(/^sha256=/i, ''));
}

/** Retell: X-Retell-Signature = "v={unix ms},d={hex HMAC-SHA256(api key, raw body + timestamp)}", at most 5 minutes old. */
export function verifyRetellSignature(
  rawBody: string,
  header: string | null,
  apiKey: string | undefined,
  now: number = Date.now(),
): boolean {
  if (!apiKey || !header) return false;
  const match = /^v=(\d+),d=([0-9a-f]+)$/i.exec(header.trim());
  if (!match) return false;
  const [, timestamp, digest] = match;
  if (Math.abs(now - Number(timestamp)) > RETELL_MAX_AGE_MS) return false;
  return hexEqual(hmacHex(apiKey, rawBody + timestamp), digest);
}
