// Twilio WhatsApp sender shared by the Cal.com and Retell routes.
import twilio from 'twilio';
import { log } from './log';
import { maskPhone } from './phone';
import type { Lang } from './rules';
import { contentSid, renderBody, type TemplateKind, type TemplateVars } from './templates';

export const SANDBOX_FROM = 'whatsapp:+14155238886';

export type SendResult =
  | { status: 'sent' | 'dry_run'; sid: string }
  | { status: 'skipped'; reason: 'missing_twilio_config' | 'missing_template' }
  | { status: 'failed'; transient: boolean; error: string };

let client: ReturnType<typeof twilio> | undefined;

function getClient() {
  client ??= twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);
  return client;
}

export async function sendWhatsApp(toE164: string, kind: TemplateKind, lang: Lang, vars: TemplateVars): Promise<SendResult> {
  const from = process.env.TWILIO_WHATSAPP_FROM?.trim();
  const sid = contentSid(kind, lang);
  // Free-form body only works inside the Sandbox (after the tester joins it); everywhere else a template is required.
  const useBody = !sid && from === SANDBOX_FROM;

  if (process.env.NOTIFICATIONS_DRY_RUN === 'true') {
    log('whatsapp.dry_run', { to: toE164, kind, lang, contentSid: sid ?? null, vars, body: renderBody(kind, lang, vars) });
    return { status: 'dry_run', sid: 'dry-run' };
  }
  if (!from || !process.env.TWILIO_ACCOUNT_SID || !process.env.TWILIO_AUTH_TOKEN) {
    log('whatsapp.config_error', { missing: 'TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_WHATSAPP_FROM' });
    return { status: 'skipped', reason: 'missing_twilio_config' };
  }
  if (!sid && !useBody) {
    log('whatsapp.config_error', { missing: `template ContentSid for ${kind}/${lang}` });
    return { status: 'skipped', reason: 'missing_template' };
  }

  try {
    const message = await getClient().messages.create({
      from,
      to: `whatsapp:${toE164}`,
      ...(useBody ? { body: renderBody(kind, lang, vars) } : { contentSid: sid, contentVariables: JSON.stringify(vars) }),
    });
    log('whatsapp.sent', { to: maskPhone(toE164), kind, lang, sid: message.sid, mode: useBody ? 'body' : 'template' });
    return { status: 'sent', sid: message.sid };
  } catch (err) {
    const { status, code, message } = err as { status?: number; code?: number; message?: string };
    // No HTTP status (network error), throttling or a Twilio 5xx are worth retrying; 4xx (bad number, unapproved template...) are not.
    const transient = status === undefined || status === 429 || status >= 500;
    log('whatsapp.failed', { to: maskPhone(toE164), kind, lang, status, code, error: message, transient });
    return { status: 'failed', transient, error: code ? `twilio_${code}` : 'twilio_error' };
  }
}
