# TJ Medical Services — demo clinic website

Bilingual (EN/ES) static website for a **fictional** cross-border medical clinic in Tijuana with a San Diego office. Built to serve as the knowledge base for a Retell AI voice receptionist.

## Structure

```
src/data.py      ← all clinic facts: phones, addresses, hours, services, prices, team, FAQ
src/build.py     ← generates the HTML pages from data.py
public/          ← the deployable site (Vercel serves this folder)
retell/          ← ready-to-paste Retell agent prompt
vercel.json      ← static deploy, clean URLs (/prices instead of /prices.html)
```

Pages (English at `/`, Spanish at `/es/`): Home, Services, Prices, Getting here, Our team, FAQ, Contact, Patient guide, Payments & policies, and **Clinic fact sheet** (`/reference`) — every fact on one page, written for the AI receptionist.

## Edit content

1. Change `src/data.py` (or page copy in `src/build.py`).
2. Run `python3 src/build.py`.
3. Commit and push — Vercel redeploys automatically.

Before going live, replace the placeholder phone numbers, email and `CLINIC["url"]` (used in canonical links and the sitemap) with real values.

## Deploy on Vercel

1. vercel.com → **Add New… → Project** → import `chiloska/tj-medical-services`.
2. Framework preset: **Other**. Leave build command empty; output directory is set by `vercel.json` (`public`).
3. Deploy. Then set `CLINIC["url"]` in `src/data.py` to the final domain and rebuild.

## Connect Retell

1. In Retell → **Knowledge Base** → create one → **Add URL**.
2. Add `https://<your-domain>/reference` and `https://<your-domain>/es/reference` (one page each holds everything). Optionally add the sitemap `https://<your-domain>/sitemap.xml` to pull every page.
3. Enable auto-refresh if offered, so price or hour changes reach the agent.
4. Attach the knowledge base to your agent and paste `retell/agent-prompt.md` as its prompt.
5. Test with questions like "How much is a gastric sleeve?", "¿Aceptan seguro?", "What do I need to cross back?".
