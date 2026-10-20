import { describe, expect, it } from 'vitest';
// @ts-expect-error plain .mjs script without type declarations
import { templateSpecs } from '../scripts/create-whatsapp-templates.mjs';

interface Spec {
  name: string;
  envVar: string;
  lang: string;
  body: string;
  variables: Record<string, string>;
}

const specs: Spec[] = templateSpecs();

describe('create-whatsapp-templates script', () => {
  it('covers the 8 templates the code looks up', () => {
    expect(specs.map((s) => s.envVar).sort()).toEqual(
      ['ADDRESS', 'CANCEL', 'CONFIRM', 'RESCHEDULE'].flatMap((k) => [`WA_TPL_${k}_EN`, `WA_TPL_${k}_ES`]).sort(),
    );
  });

  it.each(specs.map((s) => [s.name, s] as const))('%s meets WhatsApp template rules', (_, s) => {
    expect(s.name).toMatch(/^[a-z0-9_]+$/);
    const used = [...s.body.matchAll(/\{\{(\d+)\}\}/g)].map((m) => m[1]);
    expect(used).toEqual(used.map((_, i) => String(i + 1))); // sequential, each once
    expect(Object.keys(s.variables).sort()).toEqual([...used].sort()); // a sample for every variable
    expect(Object.values(s.variables).every((v) => v.trim().length > 0)).toBe(true);
    expect(s.body).not.toMatch(/^\s*\{\{|\}\}\s*\.?\s*$/); // no variable at the start or end
  });
});
