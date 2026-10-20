import { describe, expect, it } from 'vitest';
import { CLINIC } from '../lib/notifications/clinic.generated';
import { apptName, detectLanguage, displayName, eventType, formatAppointmentTime, locationText } from '../lib/notifications/rules';
import { renderBody } from '../lib/notifications/templates';

describe('eventType', () => {
  it('maps every Cal.com event type to its location', () => {
    expect(eventType(7564958)?.location).toBe('tijuana');
    expect(eventType(7564959)?.location).toBe('video');
    expect(eventType(7564960)?.location).toBe('video');
    expect(eventType(7564961)?.location).toBe('video');
    expect(eventType(7564962)?.location).toBe('tijuana');
    expect(eventType(7564963)?.location).toBe('sandiego');
    expect(eventType('7564963')?.key).toBe('specialist');
  });
  it('returns undefined for unknown ids', () => {
    expect(eventType(1)).toBeUndefined();
    expect(eventType(undefined)).toBeUndefined();
    expect(eventType('abc')).toBeUndefined();
  });
  it('names the appointment in each language', () => {
    expect(apptName(eventType(7564958)!, 'en')).toBe('dental evaluation');
    expect(apptName(eventType(7564958)!, 'es')).toBe('evaluación dental');
  });
});

describe('detectLanguage', () => {
  it('detects Spanish locales', () => {
    for (const l of ['es', 'es-MX', 'ES', 'es_419']) expect(detectLanguage(l)).toBe('es');
  });
  it('defaults to English', () => {
    for (const l of ['en', 'en-US', 'estonian', undefined, '']) expect(detectLanguage(l)).toBe('en');
  });
});

describe('formatAppointmentTime (America/Tijuana)', () => {
  const iso = '2026-10-23T17:00:00Z'; // 10:00 a.m. PDT
  it('formats English', () => {
    expect(formatAppointmentTime(iso, 'en')).toBe('Fri, Oct 23, 10:00 AM');
  });
  it('formats Spanish', () => {
    expect(formatAppointmentTime(iso, 'es')).toBe('viernes 23 de octubre, 10:00 a.m.');
  });
  it('follows the DST change (PST in December)', () => {
    expect(formatAppointmentTime('2026-12-01T22:30:00Z', 'en')).toBe('Tue, Dec 1, 2:30 PM');
    expect(formatAppointmentTime('2026-12-01T22:30:00Z', 'es')).toBe('martes 1 de diciembre, 2:30 p.m.');
  });
  it('rejects bad input', () => {
    expect(formatAppointmentTime('tomorrow', 'en')).toBeUndefined();
    expect(formatAppointmentTime(undefined, 'en')).toBeUndefined();
  });
});

describe('locationText', () => {
  it('uses the generated clinic addresses for in-person visits', () => {
    expect(locationText('tijuana', 'en')).toBe(CLINIC.tj_address);
    expect(locationText('sandiego', 'es')).toBe(CLINIC.sd_address);
  });
  it('includes the video link when present', () => {
    expect(locationText('video', 'en', 'https://app.cal.com/video/abc')).toBe('Free video call: https://app.cal.com/video/abc');
    expect(locationText('video', 'es', 'https://app.cal.com/video/abc')).toBe('Videollamada gratuita: https://app.cal.com/video/abc');
  });
  it('falls back when there is no usable link', () => {
    expect(locationText('video', 'en')).toBe('Free video call (link sent separately)');
    expect(locationText('video', 'en', 'javascript:alert(1)')).toBe('Free video call (link sent separately)');
  });
});

describe('displayName', () => {
  it('keeps real names, including accents and compound names', () => {
    expect(displayName('María José', 'es')).toBe('María José');
    expect(displayName("  O'Brien-Smith ", 'en')).toBe("O'Brien-Smith");
    expect(displayName({ firstName: 'Ana', lastName: 'López' }, 'es')).toBe('Ana López');
  });
  it('strips links and line breaks', () => {
    expect(displayName('Bob\nvisit http://evil.example', 'en')).toBe('Bob visit http evil.example');
  });
  it('falls back to a generic greeting', () => {
    expect(displayName('', 'en')).toBe('there');
    expect(displayName(undefined, 'es')).toBe('estimado paciente');
    expect(displayName('12345', 'en')).toBe('there');
  });
});

describe('renderBody', () => {
  it('fills the template variables', () => {
    expect(renderBody('cancel', 'en', { '1': 'Ana', '2': 'dental evaluation', '3': 'Fri, Oct 23, 10:00 AM' })).toBe(
      'Hi Ana, your dental evaluation with TJ Medical Services on Fri, Oct 23, 10:00 AM has been cancelled. To book a new time, reply here or call +1 (619) 555-0148.',
    );
  });
});
