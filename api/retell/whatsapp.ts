// POST /api/retell/whatsapp: the `send_whatsapp_info` custom function for the Retell agent.
// Always answers 200 with { result, message } for the agent to speak; 401 only for a bad signature.
// The recipient is the number the call comes from, never a number from the LLM-filled args.
import { claim, release } from '../../lib/notifications/dedupe';
import { json, log } from '../../lib/notifications/log';
import { maskPhone, toE164 } from '../../lib/notifications/phone';
import { ADDRESSES, detectLanguage, displayName, type Lang } from '../../lib/notifications/rules';
import { verifyRetellSignature } from '../../lib/notifications/verify';
import { sendWhatsApp } from '../../lib/notifications/whatsapp';

const INFO_TYPES = {
  tijuana_clinic_address: 'tijuana',
  san_diego_office_address: 'sandiego',
} as const;

const MESSAGES = {
  sent: {
    en: "Sent to the WhatsApp number you're calling from.",
    es: 'Se lo envié al WhatsApp del número desde el que llama.',
  },
  noPhone: {
    en: "I couldn't send a WhatsApp message from this call. Please write down the address instead.",
    es: 'No pude enviar un WhatsApp desde esta llamada. Por favor anote la dirección.',
  },
  failed: {
    en: "I couldn't send it right now.",
    es: 'No pude enviarlo en este momento.',
  },
  unsupported: {
    en: 'I can only send our clinic and office addresses by WhatsApp.',
    es: 'Por WhatsApp solo puedo enviar la dirección de la clínica o de la oficina.',
  },
};

function reply(result: 'sent' | 'failed', message: string): Response {
  return json({ result, message });
}

function withAddress(text: string, address: string, lang: Lang): string {
  return `${text} ${lang === 'es' ? 'La dirección es' : 'The address is'} ${address}.`;
}

export async function POST(request: Request): Promise<Response> {
  const raw = await request.text();
  const apiKey = process.env.RETELL_API_KEY;
  if (!apiKey) log('retell.config_error', { missing: 'RETELL_API_KEY' });
  if (!verifyRetellSignature(raw, request.headers.get('x-retell-signature'), apiKey)) {
    log('retell.unauthorized');
    return json({ error: 'unauthorized' }, 401);
  }

  let body: { name?: unknown; call?: { call_id?: unknown; from_number?: unknown }; args?: Record<string, unknown> };
  try {
    body = JSON.parse(raw);
  } catch {
    log('retell.skipped', { reason: 'invalid_json' });
    return reply('failed', MESSAGES.failed.en);
  }

  const args = body.args ?? {};
  const callId = typeof body.call?.call_id === 'string' ? body.call.call_id : undefined;
  const lang = detectLanguage(args.language);
  const infoType = String(args.info_type ?? '');
  const place = INFO_TYPES[infoType as keyof typeof INFO_TYPES];
  if (!place) {
    log('retell.skipped', { reason: 'unsupported_info_type', infoType, callId });
    return reply('failed', MESSAGES.unsupported[lang]);
  }
  const address = ADDRESSES[place];

  const phone = toE164(body.call?.from_number);
  if (!phone) {
    log('retell.skipped', { reason: 'no_caller_number', callId });
    return reply('failed', withAddress(MESSAGES.noPhone[lang], address, lang));
  }

  // Without a call_id there is nothing stable to dedupe on, so just send.
  const key = callId ? `retell:${callId}:${infoType}` : undefined;
  if (key && !(await claim(key))) {
    log('retell.skipped', { reason: 'duplicate', callId, infoType });
    return reply('sent', MESSAGES.sent[lang]);
  }

  const result = await sendWhatsApp(phone, 'address', lang, { '1': displayName(args.patient_name, lang), '2': address });
  log('retell.result', { callId, infoType, lang, to: maskPhone(phone), ...result });

  if (result.status === 'sent' || result.status === 'dry_run') return reply('sent', MESSAGES.sent[lang]);
  if (key) await release(key);
  return reply('failed', withAddress(MESSAGES.failed[lang], address, lang));
}
