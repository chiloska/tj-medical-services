import { describe, expect, it } from 'vitest';
import { maskPhone, toE164 } from '../lib/notifications/phone';

describe('toE164', () => {
  it.each([
    ['+16195550148', '+16195550148'],
    ['+1 (619) 555-0148', '+16195550148'],
    ['1-619-555-0148', '+16195550148'],
    ['whatsapp:+16195550148', '+16195550148'],
    ['+52 664 555 0148', '+526645550148'],
    ['+5216645550148', '+526645550148'], // legacy mobile prefix
    ['00526645550148', '+526645550148'],
    ['526645550148', '+526645550148'],
  ])('%s -> %s', (input, expected) => {
    expect(toE164(input)).toBe(expected);
  });

  it.each([
    ['6195550148'], // bare 10 digits: U.S. or Mexico?
    ['+44 20 7946 0958'], // outside +1 / +52
    ['+1 019 555 0148'], // invalid NANP area code
    ['+52 0664 555 014'],
    ['call me'],
    [''],
  ])('rejects %s', (input) => {
    expect(toE164(input)).toBeUndefined();
  });

  it('rejects non-strings', () => {
    expect(toE164(undefined)).toBeUndefined();
    expect(toE164(6195550148)).toBeUndefined();
  });
});

describe('maskPhone', () => {
  it('keeps only the country code and last 4 digits', () => {
    expect(maskPhone('+16195550148')).toBe('+1…0148');
    expect(maskPhone('+526645550148')).toBe('+52…0148');
  });
});
