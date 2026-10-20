#!/usr/bin/env node
// Creates the 8 WhatsApp Content templates (confirm / reschedule / cancel / address x EN/ES) in Twilio from
// the text in lib/notifications/templates.ts and submits each for WhatsApp approval (category UTILITY).
//
//   npm run wa:templates               preview: show what would be created, call nothing
//   npm run wa:templates -- --apply    create missing templates and submit them for approval
//   npm run wa:templates -- --status   show the approval status of existing templates
//
// Reads TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN from the environment or .env.local. Safe to re-run: a template
// whose name already exists is reused, never duplicated, and only submitted if it hasn't been yet.
// Needs Node 24+ (imports TypeScript files directly).
import { pathToFileURL } from 'node:url';
import { TEXT } from '../lib/notifications/templates.ts';
import { CLINIC } from '../lib/notifications/clinic.generated.ts';

const API = 'https://content.twilio.com/v1';
const CATEGORY = 'UTILITY';
// Template names as listed in docs/whatsapp-notifications.md; the language is appended (tjms_clinic_address_es).
const NAMES = {
  confirm: 'tjms_appointment_confirmation',
  reschedule: 'tjms_appointment_rescheduled',
  cancel: 'tjms_appointment_cancelled',
  address: 'tjms_clinic_address',
};

// Sample values Meta reviews with the template. Same shapes the code sends (see rules.ts).
const SAMPLES = {
  confirm: {
    en: { 1: 'Maria', 2: 'dental evaluation', 3: 'Fri, Oct 23, 10:00 AM', 4: CLINIC.tj_address },
    es: { 1: 'María', 2: 'evaluación dental', 3: 'viernes 23 de octubre, 10:00 a.m.', 4: CLINIC.tj_address },
  },
  reschedule: {
    en: { 1: 'Maria', 2: 'specialist consultation', 3: 'Mon, Oct 26, 2:30 PM', 4: CLINIC.sd_address },
    es: { 1: 'María', 2: 'consulta con especialista', 3: 'lunes 26 de octubre, 2:30 p.m.', 4: CLINIC.sd_address },
  },
  cancel: {
    en: { 1: 'Maria', 2: 'dental evaluation', 3: 'Fri, Oct 23, 10:00 AM' },
    es: { 1: 'María', 2: 'evaluación dental', 3: 'viernes 23 de octubre, 10:00 a.m.' },
  },
  address: {
    en: { 1: 'Maria', 2: CLINIC.tj_address },
    es: { 1: 'María', 2: CLINIC.tj_address },
  },
};

/** One entry per template: Twilio/Meta name, env var, language, body and sample variables. */
export function templateSpecs() {
  return Object.entries(TEXT).flatMap(([kind, byLang]) =>
    Object.entries(byLang).map(([lang, body]) => ({
      name: `${NAMES[kind]}_${lang}`,
      envVar: `WA_TPL_${kind.toUpperCase()}_${lang.toUpperCase()}`,
      lang,
      body,
      variables: Object.fromEntries(Object.entries(SAMPLES[kind][lang]).map(([n, v]) => [n, String(v)])),
    })),
  );
}

function loadCredentials() {
  try {
    process.loadEnvFile('.env.local');
  } catch {
    // no .env.local: rely on the environment
  }
  const sid = process.env.TWILIO_ACCOUNT_SID?.trim();
  const token = process.env.TWILIO_AUTH_TOKEN?.trim();
  if (!sid || !token) {
    console.error('Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env.local (or the environment).');
    process.exit(1);
  }
  return 'Basic ' + Buffer.from(`${sid}:${token}`).toString('base64');
}

async function twilio(auth, method, url, body) {
  const res = await fetch(url.startsWith('http') ? url : API + url, {
    method,
    headers: { Authorization: auth, ...(body && { 'Content-Type': 'application/json' }) },
    body: body && JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${method} ${url} -> ${res.status}: ${data.message ?? JSON.stringify(data)}`);
  return data;
}

/** friendly_name -> content SID for every template in the account. */
async function existingTemplates(auth) {
  const byName = new Map();
  let url = '/Content?PageSize=100';
  while (url) {
    const page = await twilio(auth, 'GET', url);
    for (const c of page.contents ?? []) byName.set(c.friendly_name, c.sid);
    url = page.meta?.next_page_url;
  }
  return byName;
}

/** WhatsApp approval status: 'unsubmitted', 'received', 'pending', 'approved', 'rejected'... */
async function approval(auth, sid) {
  const data = await twilio(auth, 'GET', `/Content/${sid}/ApprovalRequests`);
  const wa = data.whatsapp ?? {};
  return { status: (wa.status || 'unsubmitted').toLowerCase(), reason: wa.rejection_reason || '' };
}

async function main() {
  const args = new Set(process.argv.slice(2));
  const specs = templateSpecs();

  if (!args.has('--apply') && !args.has('--status')) {
    for (const s of specs) {
      console.log(`\n${s.name} (${s.lang}, ${CATEGORY}) -> ${s.envVar}\n  ${s.body}`);
      for (const [n, v] of Object.entries(s.variables)) console.log(`  {{${n}}} sample: ${v}`);
    }
    console.log('\nPreview only. Run with --apply to create and submit these templates.');
    return;
  }

  const auth = loadCredentials();
  const existing = await existingTemplates(auth);
  const envLines = [];
  let failed = false;

  for (const s of specs) {
    try {
      let sid = existing.get(s.name);
      if (!sid && args.has('--apply')) {
        const created = await twilio(auth, 'POST', '/Content', {
          friendly_name: s.name,
          language: s.lang,
          variables: s.variables,
          types: { 'twilio/text': { body: s.body } },
        });
        sid = created.sid;
        console.log(`${s.name}: created ${sid}`);
      }
      if (!sid) {
        console.log(`${s.name}: not created yet`);
        continue;
      }

      let { status, reason } = await approval(auth, sid);
      if (status === 'unsubmitted' && args.has('--apply')) {
        const req = await twilio(auth, 'POST', `/Content/${sid}/ApprovalRequests/whatsapp`, { name: s.name, category: CATEGORY });
        status = (req.status || 'received').toLowerCase();
        reason = req.rejection_reason || '';
      }
      console.log(`${s.name}: ${sid} WhatsApp approval ${status}${reason ? ` (${reason})` : ''}`);
      if (status === 'rejected') failed = true;
      envLines.push(`${s.envVar}=${sid}`);
    } catch (err) {
      failed = true;
      console.error(`${s.name}: ${err.message}`);
    }
  }

  if (envLines.length) {
    console.log('\nAdd to Vercel env vars (and .env.local). Messages only deliver once a template is approved:\n');
    console.log(envLines.join('\n'));
  }
  if (failed) process.exitCode = 1;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  main().catch((err) => {
    console.error(err.message);
    process.exit(1);
  });
}
