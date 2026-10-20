// Business rules: Cal.com event type -> appointment copy and location, language, date and name formatting.
import { CLINIC } from './clinic.generated';

export type Lang = 'en' | 'es';
export type ApptKey = 'dental' | 'weight_loss' | 'cosmetic' | 'orthopedic' | 'checkup' | 'specialist';
export type LocationKind = 'tijuana' | 'sandiego' | 'video';

export interface ApptType {
  key: ApptKey;
  nameEn: string;
  nameEs: string;
  location: LocationKind;
}

export const EVENT_TYPES: Record<number, ApptType> = {
  7564958: { key: 'dental', nameEn: 'dental evaluation', nameEs: 'evaluación dental', location: 'tijuana' },
  7564959: { key: 'weight_loss', nameEn: 'weight-loss surgery consultation', nameEs: 'consulta de cirugía para bajar de peso', location: 'video' },
  7564960: { key: 'cosmetic', nameEn: 'cosmetic surgery consultation', nameEs: 'consulta de cirugía estética', location: 'video' },
  7564961: { key: 'orthopedic', nameEn: 'orthopedic consultation', nameEs: 'consulta de ortopedia', location: 'video' },
  7564962: { key: 'checkup', nameEn: 'check-up and imaging appointment', nameEs: 'cita de chequeo e imagenología', location: 'tijuana' },
  7564963: { key: 'specialist', nameEn: 'specialist consultation', nameEs: 'consulta con especialista', location: 'sandiego' },
};

export const ADDRESSES: Record<'tijuana' | 'sandiego', string> = {
  tijuana: CLINIC.tj_address,
  sandiego: CLINIC.sd_address,
};

export const TIME_ZONE = 'America/Tijuana';

export function eventType(id: unknown): ApptType | undefined {
  const n = typeof id === 'string' ? Number(id) : id;
  return typeof n === 'number' && Number.isInteger(n) ? EVENT_TYPES[n] : undefined;
}

export function apptName(appt: ApptType, lang: Lang): string {
  return lang === 'es' ? appt.nameEs : appt.nameEn;
}

/** 'es' if any candidate is a Spanish locale ("es", "es-MX", "es_419"...), else 'en'. */
export function detectLanguage(...candidates: unknown[]): Lang {
  return candidates.some((c) => typeof c === 'string' && /^es(?:$|[-_])/i.test(c.trim())) ? 'es' : 'en';
}

export function locationText(kind: LocationKind, lang: Lang, videoUrl?: unknown): string {
  if (kind !== 'video') return ADDRESSES[kind];
  const url = typeof videoUrl === 'string' && /^https:\/\/\S+$/.test(videoUrl.trim()) ? videoUrl.trim() : undefined;
  if (lang === 'es') return url ? `Videollamada gratuita: ${url}` : 'Videollamada gratuita (el enlace se envía por separado)';
  return url ? `Free video call: ${url}` : 'Free video call (link sent separately)';
}

/** "Fri, Oct 23, 10:00 AM" / "viernes 23 de octubre, 10:00 a.m." in Tijuana time; undefined for a bad date. */
export function formatAppointmentTime(iso: unknown, lang: Lang): string | undefined {
  if (typeof iso !== 'string') return undefined;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return undefined;
  const opts: Intl.DateTimeFormatOptions = { timeZone: TIME_ZONE, day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true };
  if (lang === 'en') {
    const text = new Intl.DateTimeFormat('en-US', { ...opts, weekday: 'short', month: 'short' }).format(date);
    return text.replace(/[  ]/g, ' ');
  }
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat('es-MX', { ...opts, weekday: 'long', month: 'long' }).formatToParts(date).map((p) => [p.type, p.value]),
  );
  const period = (parts.dayPeriod ?? '').replace(/[\s  ]/g, '').toLowerCase();
  return `${parts.weekday} ${parts.day} de ${parts.month}, ${parts.hour}:${parts.minute} ${period}`;
}

/**
 * Name for the greeting. Keeps letters, spaces, apostrophes, hyphens and periods only, so neither an
 * LLM-filled argument nor a booking form can inject links or line breaks into the template.
 */
export function displayName(raw: unknown, lang: Lang): string {
  let name = '';
  if (typeof raw === 'string') name = raw;
  else if (raw && typeof raw === 'object') {
    const { firstName, lastName } = raw as { firstName?: unknown; lastName?: unknown };
    name = [firstName, lastName].filter((v) => typeof v === 'string').join(' ');
  }
  name = name.replace(/[^\p{L}\p{M}' .-]/gu, ' ').replace(/\s+/g, ' ').trim().slice(0, 60).trim();
  return /\p{L}/u.test(name) ? name : lang === 'es' ? 'estimado paciente' : 'there';
}
