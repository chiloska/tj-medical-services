// Normalize patient phone numbers to E.164. Only U.S./Canada (+1) and Mexico (+52) are accepted.

/**
 * Returns "+1XXXXXXXXXX" or "+52XXXXXXXXXX", or undefined when the number is missing, invalid,
 * or ambiguous. A bare 10-digit number is rejected: it could be U.S. or Mexican, and guessing
 * wrong would send appointment details to a stranger.
 */
export function toE164(raw: unknown): string | undefined {
  if (typeof raw !== 'string') return undefined;
  const s = raw.trim().replace(/^whatsapp:/i, '');
  let digits = s.replace(/\D/g, '');
  if (!s.startsWith('+') && digits.startsWith('00')) digits = digits.slice(2);

  if (/^1[2-9]\d{2}[2-9]\d{6}$/.test(digits)) return `+${digits}`;
  if (digits.startsWith('52')) {
    let national = digits.slice(2);
    if (national.length === 11 && national.startsWith('1')) national = national.slice(1); // legacy +52 1 mobile prefix
    if (/^[1-9]\d{9}$/.test(national)) return `+52${national}`;
  }
  return undefined;
}

/** For logs: keep only the country code and last 4 digits. */
export function maskPhone(e164: string): string {
  const cc = e164.startsWith('+52') ? '+52' : '+1';
  return `${cc}…${e164.slice(-4)}`;
}
