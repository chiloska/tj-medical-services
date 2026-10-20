// WhatsApp Content templates: ContentSid lookup (env vars) and the approved text, used for dry-run
// logs and the Twilio Sandbox fallback. Keep the text identical to what is approved in Twilio.
import type { Lang } from './rules';

export type TemplateKind = 'confirm' | 'reschedule' | 'cancel' | 'address';

const ENV_PREFIX: Record<TemplateKind, string> = {
  confirm: 'WA_TPL_CONFIRM',
  reschedule: 'WA_TPL_RESCHEDULE',
  cancel: 'WA_TPL_CANCEL',
  address: 'WA_TPL_ADDRESS',
};

// Also read by scripts/create-whatsapp-templates.mjs, which submits this text to Twilio.
export const TEXT: Record<TemplateKind, Record<Lang, string>> = {
  confirm: {
    en: 'Hi {{1}}, your {{2}} with TJ Medical Services is confirmed for {{3}} (Pacific Time). Location: {{4}}. To reschedule, reply to this message or call +1 (619) 349-9659.',
    es: 'Hola {{1}}, su {{2}} con TJ Medical Services está confirmada para el {{3}} (hora del Pacífico). Lugar: {{4}}. Para reprogramar, responda a este mensaje o llame al +1 (619) 349-9659.',
  },
  reschedule: {
    en: 'Hi {{1}}, your {{2}} with TJ Medical Services has been moved to {{3}} (Pacific Time). Location: {{4}}. Questions? Reply here or call +1 (619) 349-9659.',
    es: 'Hola {{1}}, su {{2}} con TJ Medical Services se cambió al {{3}} (hora del Pacífico). Lugar: {{4}}. ¿Dudas? Responda aquí o llame al +1 (619) 349-9659.',
  },
  cancel: {
    en: 'Hi {{1}}, your {{2}} with TJ Medical Services on {{3}} has been cancelled. To book a new time, reply here or call +1 (619) 349-9659.',
    es: 'Hola {{1}}, su {{2}} con TJ Medical Services del {{3}} fue cancelada. Para agendar otra fecha, responda aquí o llame al +1 (619) 349-9659.',
  },
  address: {
    en: 'Hi {{1}}, here is the address you asked for: {{2}}. Our free shuttle runs from the San Diego office to the Tijuana clinic every hour, 7 a.m.–3 p.m., Mon–Sat. Reply here with any questions.',
    es: 'Hola {{1}}, aquí está la dirección que solicitó: {{2}}. Nuestro transporte gratuito sale de la oficina de San Diego a la clínica de Tijuana cada hora, de 7 a.m. a 3 p.m., lunes a sábado. Responda aquí si tiene dudas.',
  },
};

export type TemplateVars = Record<string, string>;

export function contentSid(kind: TemplateKind, lang: Lang): string | undefined {
  return process.env[`${ENV_PREFIX[kind]}_${lang.toUpperCase()}`]?.trim() || undefined;
}

export function renderBody(kind: TemplateKind, lang: Lang, vars: TemplateVars): string {
  return TEXT[kind][lang].replace(/\{\{(\d+)\}\}/g, (_, n: string) => vars[n] ?? '');
}
