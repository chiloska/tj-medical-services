#!/usr/bin/env python3
"""Generates the static TJ Medical Services site (EN + ES) into ../public.

Run:  python3 src/build.py
All facts live in src/data.py so the website and the AI receptionist stay in sync.
"""
import json
import os
from html import escape

from data import CLINIC, HOURS, SERVICES, PRICES, TEAM, FAQ

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public")
C = CLINIC

PAGES = [
    # slug, nav label en, nav label es, in main nav
    ("index", "Home", "Inicio", False),
    ("services", "Services", "Servicios", True),
    ("prices", "Prices", "Precios", True),
    ("travel", "Getting here", "Cómo llegar", True),
    ("team", "Our team", "Equipo", True),
    ("faq", "FAQ", "Preguntas", True),
    ("contact", "Contact", "Contacto", True),
    ("patient-guide", "Patient guide", "Guía del paciente", False),
    ("payments", "Payments & policies", "Pagos y políticas", False),
    ("reference", "Clinic fact sheet", "Ficha de la clínica", False),
]
LABEL = {p[0]: {"en": p[1], "es": p[2]} for p in PAGES}
SERVICE_BY_ID = {s["id"]: s for s in SERVICES}


def href(slug, lang, frm_lang=None):
    """Absolute site path for slug in lang (works with Vercel cleanUrls)."""
    base = "/es/" if lang == "es" else "/"
    return base + ("" if slug == "index" else slug)


def money(n, lang):
    if n == 0:
        return "Free" if lang == "en" else "Gratis"
    return f"${n:,} USD"


LOGO = (
    '<svg class="mark" viewBox="0 0 44 16" aria-hidden="true">'
    '<circle cx="5" cy="8" r="4"/><line x1="12" y1="8" x2="32" y2="8"/>'
    '<circle cx="39" cy="8" r="4"/></svg>'
)


def layout(slug, lang, title, desc, body, jsonld=None):
    t = lambda en, es: en if lang == "en" else es
    other = "es" if lang == "en" else "en"
    pre = "/"
    nav = "".join(
        f'<li><a href="{href(s, lang)}"{" aria-current=\"page\"" if s == slug else ""}>{LABEL[s][lang]}</a></li>'
        for s, _, _, main in PAGES if main
    )
    alt_url_en = C["url"] + "/" + ("" if slug == "index" else slug)
    alt_url_es = C["url"] + "/es/" + ("" if slug == "index" else slug)
    canonical = alt_url_en if lang == "en" else alt_url_es
    ld = ""
    for block in (jsonld or []):
        ld += f'<script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>\n'
    page_title = f"{title} | {C['name']}" if slug != "index" else f"{C['name']} — {title}"
    footer_links = "".join(
        f'<li><a href="{href(s, lang)}">{LABEL[s][lang]}</a></li>' for s, *_ in PAGES if s != "index"
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(page_title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{alt_url_en}">
<link rel="alternate" hreflang="es" href="{alt_url_es}">
<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Public+Sans:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}styles.css">
{ld}</head>
<body>
<a class="skip" href="#main">{t("Skip to content", "Ir al contenido")}</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{href('index', lang)}">{LOGO}<span>TJ Medical Services</span></a>
    <details class="menu">
      <summary>{t("Menu", "Menú")}</summary>
      <nav aria-label="{t('Main', 'Principal')}"><ul>{nav}</ul></nav>
    </details>
    <nav class="nav-wide" aria-label="{t('Main', 'Principal')}"><ul>{nav}</ul></nav>
    <div class="header-actions">
      <a class="lang" href="{href(slug, other, lang)}" hreflang="{other}" lang="{other}">{t("Español", "English")}</a>
      <a class="btn btn-small" href="tel:{C['phone_us_tel']}">{t("Call", "Llamar")} {C['phone_us']}</a>
    </div>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="brand brand-footer">{LOGO}<span>TJ Medical Services</span></p>
      <p>{t("Specialist care in Tijuana, coordinated from San Diego.", "Atención especializada en Tijuana, coordinada desde San Diego.")}</p>
      <p>{t("Emergency? Call 911 — it works in both the U.S. and Mexico.", "¿Emergencia? Llame al 911, funciona en Estados Unidos y en México.")}</p>
    </div>
    <div>
      <h2 class="footer-h">{t("Tijuana clinic", "Clínica Tijuana")}</h2>
      <p>{C['tj_address']}<br><a href="tel:{C['phone_mx_tel']}">{C['phone_mx']}</a></p>
      <h2 class="footer-h">{t("San Diego office", "Oficina San Diego")}</h2>
      <p>{C['sd_address']}<br><a href="tel:{C['phone_us_tel']}">{C['phone_us']}</a></p>
    </div>
    <div>
      <h2 class="footer-h">{t("Pages", "Páginas")}</h2>
      <ul class="footer-links">{footer_links}</ul>
    </div>
  </div>
  <div class="wrap demo-note">
    <p>{t("TJ Medical Services is a fictional clinic created to demonstrate an AI receptionist. Names, addresses, phone numbers, doctors and prices are illustrative and are not an offer of medical services.",
          "TJ Medical Services es una clínica ficticia creada para demostrar una recepcionista con IA. Los nombres, direcciones, teléfonos, médicos y precios son ilustrativos y no constituyen una oferta de servicios médicos.")}</p>
  </div>
</footer>
<script src="{pre}site.js" defer></script>
</body>
</html>
"""


def page_head(title, lede):
    return f'<section class="page-head"><div class="wrap"><h1>{title}</h1><p class="lede">{lede}</p></div></section>'


def cta(lang):
    t = lambda en, es: en if lang == "en" else es
    return f"""<section class="cta-band"><div class="wrap cta-row">
<div><h2>{t("Get a written quote in 2 business days", "Reciba una cotización por escrito en 2 días hábiles")}</h2>
<p>{t("Tell us what you need. A doctor reviews your case before we quote, and surgery candidates get a free video consult.", "Díganos qué necesita. Un médico revisa su caso antes de cotizar, y los candidatos a cirugía reciben una videoconsulta gratuita.")}</p></div>
<div class="cta-actions"><a class="btn" href="{href('contact', lang)}">{t("Request a quote", "Solicitar cotización")}</a>
<a class="btn btn-ghost" href="{C['whatsapp_link']}">WhatsApp {C['whatsapp']}</a></div>
</div></section>"""


# ------------------------------------------------------------------ pages
def p_index(lang):
    t = lambda en, es: en if lang == "en" else es
    svc = "".join(
        f'<li><a href="{href("services", lang)}#{s["id"]}"><h3>{s[lang]["name"]}</h3><p>{s[lang]["short"]}</p></a></li>'
        for s in SERVICES
    )
    steps = [
        (t("Tell us what you need", "Cuéntenos qué necesita"), t("Call, message us on WhatsApp or send the form. We reply within one business day.", "Llame, escríbanos por WhatsApp o envíe el formulario. Respondemos en un día hábil.")),
        (t("Doctor review and written quote", "Revisión médica y cotización"), t("A doctor reviews your questionnaire, X-rays or photos. You get an itemized quote within 2 business days.", "Un médico revisa su cuestionario, radiografías o fotos. Recibe una cotización detallada en 2 días hábiles.")),
        (t("Reserve your date", "Reserve su fecha"), t("A refundable deposit holds your date. Your coordinator books transport and your recovery hotel.", "Un depósito reembolsable aparta su fecha. Su coordinador reserva transporte y hotel de recuperación.")),
        (t("Treatment in Tijuana", "Tratamiento en Tijuana"), t("We pick you up in San Diego and drive you to the clinic. A coordinator is with you at every appointment.", "Pasamos por usted a San Diego y lo llevamos a la clínica. Un coordinador lo acompaña en cada cita.")),
        (t("Home, with follow-up", "De regreso, con seguimiento"), t("You cross back using the medical lane pass, then check in with us in San Diego or by video.", "Regresa con el pase del carril médico y da seguimiento en San Diego o por video.")),
    ]
    steps_html = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in steps)
    body = f"""
<section class="hero"><div class="wrap">
  <h1>{t("Treatment in Tijuana, with one team on both sides of the border.", "Tratamiento en Tijuana, con un solo equipo en ambos lados de la frontera.")}</h1>
  <p class="lede">{t("Dental, weight-loss, cosmetic and orthopedic care at prices typically 40–70% below U.S. rates. We handle the quote, the drive, the border crossing and your follow-up — in English or Spanish.",
                    "Odontología, cirugía para bajar de peso, cirugía plástica y ortopedia a precios normalmente 40–70% menores que en Estados Unidos. Nosotros nos encargamos de la cotización, el traslado, el cruce fronterizo y su seguimiento, en español o inglés.")}</p>
  <div class="hero-actions">
    <a class="btn" href="{href('contact', lang)}">{t("Book a free virtual consult", "Agendar videoconsulta gratuita")}</a>
    <a class="btn btn-ghost" href="{href('prices', lang)}">{t("See starting prices", "Ver precios")}</a>
  </div>
  <ol class="route" aria-label="{t('How patients get from San Diego to our clinic', 'Cómo llegan los pacientes de San Diego a la clínica')}">
    <li class="stop"><span class="dot"></span><strong>{t("San Diego office", "Oficina San Diego")}</strong><span>San Ysidro, CA · {t("consults, pre-op, shuttle", "consultas, preoperatorio, traslado")}</span></li>
    <li class="leg"><span>5 min</span></li>
    <li class="stop border"><span class="bar"></span><strong>{t("Border crossing", "Cruce fronterizo")}</strong><span>San Ysidro / Otay Mesa · {t("medical lane pass on return", "pase de carril médico al regresar")}</span></li>
    <li class="leg"><span>15 min</span></li>
    <li class="stop"><span class="dot"></span><strong>{t("Tijuana clinic", "Clínica Tijuana")}</strong><span>Zona Río · {t("procedures and surgery", "procedimientos y cirugía")}</span></li>
  </ol>
</div></section>

<section class="section"><div class="wrap">
  <h2>{t("What we treat", "Qué atendemos")}</h2>
  <ul class="service-list">{svc}</ul>
</div></section>

<section class="section section-mist"><div class="wrap">
  <h2>{t("How a visit works", "Cómo funciona su visita")}</h2>
  <ol class="steps">{steps_html}</ol>
</div></section>

<section class="section"><div class="wrap two-col">
  <div>
    <h2>{t("Two locations, one coordinator", "Dos sedes, un coordinador")}</h2>
    <p>{t("Your coordinator plans everything from our San Diego office and stays your single point of contact from the first call to your last follow-up.", "Su coordinador planea todo desde nuestra oficina de San Diego y es su único contacto desde la primera llamada hasta el último seguimiento.")}</p>
    <p><a href="{href('travel', lang)}">{t("Read the full travel and border guide", "Lea la guía completa de viaje y frontera")}</a></p>
  </div>
  <dl class="facts">
    <dt>{t("Languages", "Idiomas")}</dt><dd>{t("English and Spanish, every doctor and document", "Español e inglés, todos los médicos y documentos")}</dd>
    <dt>{t("Quotes", "Cotizaciones")}</dt><dd>{t("Written, itemized, in U.S. dollars, within 2 business days", "Por escrito, detalladas, en dólares, en 2 días hábiles")}</dd>
    <dt>{t("Transport", "Transporte")}</dt><dd>{t("San Diego airport pickup with surgery packages; free shuttle from San Ysidro", "Recogida en el aeropuerto de San Diego con paquetes de cirugía; traslado gratuito desde San Ysidro")}</dd>
    <dt>{t("Licensing", "Licencias")}</dt><dd>{t("COFEPRIS-licensed clinic; board-certified specialists", "Clínica con licencia COFEPRIS; especialistas certificados")}</dd>
    <dt>{t("Follow-up", "Seguimiento")}</dt><dd>{t("In San Diego or by video; 24/7 on-call line during recovery", "En San Diego o por video; guardia 24/7 durante la recuperación")}</dd>
  </dl>
</div></section>
{cta(lang)}"""
    ld = [{
        "@context": "https://schema.org",
        "@type": "MedicalClinic",
        "name": C["name"],
        "url": C["url"],
        "telephone": C["phone_us"],
        "email": C["email"],
        "availableLanguage": ["English", "Spanish"],
        "medicalSpecialty": ["Dentistry", "PlasticSurgery", "Musculoskeletal", "Gastroenterologic", "Cardiovascular"],
        "address": {"@type": "PostalAddress", "streetAddress": "Paseo de los Héroes 9000, Torre TJMS, Floor 4, Zona Río",
                    "addressLocality": "Tijuana", "addressRegion": "B.C.", "postalCode": "22010", "addressCountry": "MX"},
        "department": [{"@type": "MedicalClinic", "name": C["name"] + " — San Diego office", "telephone": C["phone_us"],
                        "address": {"@type": "PostalAddress", "streetAddress": "480 Frontera Way, Suite 210",
                                    "addressLocality": "San Ysidro", "addressRegion": "CA", "postalCode": "92173", "addressCountry": "US"}}],
    }]
    return (t("Medical care in Tijuana for U.S. and Canadian patients", "Atención médica en Tijuana para pacientes de EE. UU. y Canadá"),
            t("Dental, weight-loss, cosmetic and orthopedic care in Tijuana, coordinated from our San Diego office. Bilingual team, written quotes, border-crossing help.",
              "Odontología, cirugía bariátrica, plástica y ortopedia en Tijuana, coordinadas desde San Diego. Equipo bilingüe, cotizaciones por escrito y apoyo en el cruce."),
            body, ld)


def p_services(lang):
    t = lambda en, es: en if lang == "en" else es
    toc = "".join(f'<li><a href="#{s["id"]}">{s[lang]["name"]}</a></li>' for s in SERVICES)
    secs = ""
    for s in SERVICES:
        d = s[lang]
        paras = "".join(f"<p>{p}</p>" for p in d["body"])
        items = "".join(f"<li>{i}</li>" for i in d["list"])
        secs += f"""<section class="svc" id="{s['id']}"><h2>{d['name']}</h2>{paras}
<h3>{t("Treatments", "Tratamientos")}</h3><ul class="ticks">{items}</ul>
<h3>{t("Time in Tijuana", "Tiempo en Tijuana")}</h3><p>{d['visits']}</p>
<p><a href="{href('prices', lang)}#{s['id']}">{t("Starting prices for", "Precios desde para")} {d['name'].lower()}</a></p></section>"""
    body = page_head(t("Services", "Servicios"),
                     t("Six departments under one roof in Zona Río, Tijuana. Every treatment is planned with your doctor before you travel.",
                       "Seis departamentos en un mismo edificio en Zona Río, Tijuana. Cada tratamiento se planea con su médico antes de viajar.")) + \
        f'<div class="wrap with-toc"><nav class="toc" aria-label="{t("On this page", "En esta página")}"><ul>{toc}</ul></nav><div class="prose">{secs}</div></div>' + cta(lang)
    return (t("Services", "Servicios"),
            t("Dental implants, All-on-4, gastric sleeve, plastic surgery, joint replacement, check-ups and specialist consultations in Tijuana.",
              "Implantes dentales, All-on-4, manga gástrica, cirugía plástica, reemplazo articular, chequeos y especialidades en Tijuana."),
            body, None)


def p_prices(lang):
    t = lambda en, es: en if lang == "en" else es
    tables = ""
    for sid, rows in PRICES:
        name = SERVICE_BY_ID[sid][lang]["name"]
        trs = "".join(
            f'<tr><th scope="row">{en if lang == "en" else es}</th><td class="num">{t("from", "desde") + " " if n else ""}{money(n, lang)}</td><td>{ue if lang == "en" else us}</td></tr>'
            for en, es, n, ue, us in rows
        )
        tables += f"""<section class="price-block" id="{sid}"><h2>{name}</h2>
<div class="table-scroll"><table><thead><tr><th scope="col">{t("Treatment", "Tratamiento")}</th><th scope="col">{t("Starting price", "Precio desde")}</th><th scope="col">{t("Notes", "Notas")}</th></tr></thead><tbody>{trs}</tbody></table></div></section>"""
    body = page_head(t("Starting prices", "Precios desde"),
                     t("Prices are in U.S. dollars and show where each treatment starts. Your exact price comes in a written quote after a doctor reviews your case, and it does not change once you accept it.",
                       "Los precios están en dólares estadounidenses e indican desde dónde inicia cada tratamiento. Su precio exacto llega en una cotización por escrito después de que un médico revise su caso, y no cambia una vez aceptada.")) + \
        f"""<div class="wrap prose-wide">
<section class="note"><h2>{t("What surgery packages include", "Qué incluyen los paquetes de cirugía")}</h2>
<ul class="ticks">
<li>{t("Surgeon, anesthesiologist and operating-room fees", "Honorarios del cirujano, anestesiólogo y quirófano")}</li>
<li>{t("Pre-surgery lab tests, ECG and chest X-ray", "Laboratorios preoperatorios, electrocardiograma y radiografía de tórax")}</li>
<li>{t("Hospital stay and medications while admitted", "Estancia hospitalaria y medicamentos durante la estancia")}</li>
<li>{t("Recovery-hotel nights with nurse visits (room shared with one companion)", "Noches de hotel de recuperación con visitas de enfermería (habitación compartida con un acompañante)")}</li>
<li>{t("Pickup at San Diego (SAN) or Tijuana (TIJ) airport and all local transport", "Recogida en el aeropuerto de San Diego (SAN) o Tijuana (TIJ) y todo el transporte local")}</li>
<li>{t("Medical-lane crossing pass for your return, when eligible", "Pase de carril médico para su regreso, cuando aplique")}</li>
<li>{t("Follow-up calls and visits at our San Diego office", "Llamadas de seguimiento y visitas en nuestra oficina de San Diego")}</li>
</ul>
<p>{t("Not included: flights, meals outside the hospital, travel insurance and extra hotel nights you request.", "No incluye: vuelos, comidas fuera del hospital, seguro de viaje ni noches de hotel adicionales que usted solicite.")}</p>
</section>
{tables}
<p class="small">{t("Prices current as of October 2026. Dental prices exclude hotel and transport unless you add a dental travel package (from $150 per night, including transport).", "Precios vigentes a octubre de 2026. Los precios dentales no incluyen hotel ni transporte, salvo que agregue un paquete de viaje dental (desde $150 dólares por noche, con transporte).")}</p>
<p><a href="{href('payments', lang)}">{t("Payment methods, deposits and insurance", "Formas de pago, depósitos y seguros")}</a></p>
</div>""" + cta(lang)
    return (t("Prices", "Precios"),
            t("Starting prices in USD for dental implants, All-on-4, gastric sleeve, breast augmentation, tummy tuck, knee and hip replacement, MRI and check-ups in Tijuana.",
              "Precios desde en dólares para implantes, All-on-4, manga gástrica, aumento de busto, abdominoplastía, reemplazo de rodilla y cadera, resonancia y chequeos en Tijuana."),
            body, None)


def p_travel(lang):
    t = lambda en, es: en if lang == "en" else es
    body = page_head(t("Getting here", "Cómo llegar"),
                     t("Most patients fly into San Diego and are at our clinic within an hour. Here is exactly how the trip works.",
                       "La mayoría de los pacientes vuela a San Diego y llega a la clínica en menos de una hora. Así funciona el viaje.")) + f"""
<div class="wrap prose">
<h2>{t("Our two locations", "Nuestras dos sedes")}</h2>
<dl class="facts">
<dt>{t("San Diego office", "Oficina San Diego")}</dt><dd>{C['sd_address']}. {t("About 5 minutes from the San Ysidro port of entry. Consultations, pre-op appointments, post-op checks and the shuttle to Tijuana. Free parking for patients.", "A unos 5 minutos de la garita de San Ysidro. Consultas, citas preoperatorias, revisiones postoperatorias y traslado a Tijuana. Estacionamiento gratuito para pacientes.")}</dd>
<dt>{t("Tijuana clinic", "Clínica Tijuana")}</dt><dd>{C['tj_address']}. {t("About 15 minutes by car from the San Ysidro crossing. All procedures, surgery and imaging take place here.", "A unos 15 minutos en auto de la garita de San Ysidro. Aquí se realizan todos los procedimientos, cirugías y estudios.")}</dd>
</dl>

<h2>{t("Arriving by plane", "Si llega en avión")}</h2>
<p>{t("Fly into San Diego International Airport (SAN). Surgery patients are met at arrivals by our driver, who takes you to the San Diego office or straight to the clinic. The drive from SAN to the border is about 25 minutes without traffic.", "Vuele al Aeropuerto Internacional de San Diego (SAN). A los pacientes de cirugía los espera nuestro chofer en llegadas y los lleva a la oficina de San Diego o directo a la clínica. El trayecto de SAN a la frontera es de unos 25 minutos sin tráfico.")}</p>
<p>{t("You can also fly into Tijuana International Airport (TIJ), which has domestic flights within Mexico, or use the Cross Border Xpress (CBX) bridge from its San Diego terminal directly into the Tijuana airport. We pick you up at TIJ either way.", "También puede volar al Aeropuerto Internacional de Tijuana (TIJ), con vuelos nacionales, o usar el puente Cross Border Xpress (CBX) desde su terminal en San Diego directo al aeropuerto de Tijuana. En ambos casos pasamos por usted a TIJ.")}</p>

<h2>{t("Arriving by car or on foot", "Si llega en auto o caminando")}</h2>
<p>{t("You can park at our San Diego office and take the free shuttle, which leaves every hour on the hour from 7:00 a.m. to 3:00 p.m., Monday to Saturday. Reserve a seat when you book. Dental and check-up patients often walk across at San Ysidro; tell us and a driver will meet you on the Mexican side.", "Puede estacionarse en nuestra oficina de San Diego y tomar el traslado gratuito, que sale cada hora en punto de 7:00 a.m. a 3:00 p.m., de lunes a sábado. Reserve su lugar al agendar. Muchos pacientes de odontología y chequeos cruzan caminando por San Ysidro; avísenos y un chofer lo espera del lado mexicano.")}</p>
<p>{t("We do not recommend driving your own car into Mexico after surgery. If you do drive in, you need Mexican auto insurance; U.S. policies generally do not cover you in Mexico.", "No recomendamos manejar su propio auto a México después de una cirugía. Si entra manejando, necesita seguro de auto mexicano; las pólizas de Estados Unidos generalmente no tienen cobertura en México.")}</p>

<h2>{t("Crossing back into the United States", "Regreso a Estados Unidos")}</h2>
<p>{t("Waits at the San Ysidro and Otay Mesa ports of entry can be several hours at busy times. Eligible patients receive a free medical quick-crossing pass, issued by the City of Tijuana, for the medical lane. Passes are only given to patients treated at our clinic and are never sold. Lane hours are set by the city and can change, so your coordinator confirms them and plans your return time.", "La espera en las garitas de San Ysidro y Otay puede ser de varias horas en horarios concurridos. Los pacientes elegibles reciben un pase médico de cruce ágil gratuito, emitido por el Ayuntamiento de Tijuana, para el carril médico. Los pases solo se entregan a pacientes atendidos en nuestra clínica y nunca se venden. El horario del carril lo define el ayuntamiento y puede cambiar, por eso su coordinador lo confirma y planea su hora de regreso.")}</p>

<h2>{t("Documents to bring", "Documentos que debe traer")}</h2>
<ul class="ticks">
<li>{t("U.S. citizens: valid passport, passport card, or SENTRI/Global Entry card", "Ciudadanos estadounidenses: pasaporte vigente, passport card o tarjeta SENTRI/Global Entry")}</li>
<li>{t("Canadian citizens: valid passport", "Ciudadanos canadienses: pasaporte vigente")}</li>
<li>{t("Other nationalities: passport plus any U.S. visa your nationality requires", "Otras nacionalidades: pasaporte y la visa estadounidense que requiera su nacionalidad")}</li>
<li>{t("Lawful permanent residents: green card and passport", "Residentes permanentes: green card y pasaporte")}</li>
</ul>
<p class="small">{t("Requirements are set by U.S. Customs and Border Protection and Mexican immigration authorities and can change. Check them before you travel.", "Los requisitos los establecen la Oficina de Aduanas y Protección Fronteriza de EE. UU. y las autoridades migratorias de México, y pueden cambiar. Verifíquelos antes de viajar.")}</p>

<h2>{t("Where you stay", "Dónde se hospeda")}</h2>
<p>{t("Surgery patients recover at partner hotels in Zona Río, a short walk or drive from the clinic, with daily nurse visits. Dental patients can add a hotel package or stay on the San Diego side and use the shuttle each day.", "Los pacientes de cirugía se recuperan en hoteles asociados en Zona Río, cerca de la clínica, con visitas diarias de enfermería. Los pacientes de odontología pueden agregar un paquete de hotel o quedarse del lado de San Diego y usar el traslado cada día.")}</p>

<h2>{t("Money and phones", "Dinero y teléfono")}</h2>
<p>{t("U.S. dollars are widely accepted in Tijuana, and all clinic prices are in dollars. Most U.S. and Canadian mobile plans work in Mexico; check roaming with your carrier. Tijuana uses Pacific Time, the same as San Diego.", "El dólar se acepta ampliamente en Tijuana y todos los precios de la clínica están en dólares. La mayoría de los planes celulares de EE. UU. y Canadá funcionan en México; consulte el roaming con su compañía. Tijuana usa la hora del Pacífico, igual que San Diego.")}</p>
</div>""" + cta(lang)
    return (t("Getting here", "Cómo llegar"),
            t("How to get to our Tijuana clinic from San Diego: airport pickup, free shuttle, border crossing, medical lane pass and documents to bring.",
              "Cómo llegar a nuestra clínica en Tijuana desde San Diego: recogida en aeropuerto, traslado gratuito, cruce fronterizo, pase médico y documentos."),
            body, None)


def p_team(lang):
    t = lambda en, es: en if lang == "en" else es
    cards = "".join(
        f'<li><h2>{n}</h2><p class="role">{re if lang == "en" else rs}</p><p>{be if lang == "en" else bs}</p></li>'
        for n, re, rs, be, bs in TEAM
    )
    body = page_head(t("Our team", "Nuestro equipo"),
                     t("Every doctor is certified by their Mexican specialty board and speaks English. Every patient has one coordinator from first call to last follow-up.",
                       "Cada médico está certificado por su consejo de especialidad y habla inglés. Cada paciente tiene un coordinador desde la primera llamada hasta el último seguimiento.")) + \
        f'<div class="wrap"><ul class="team">{cards}</ul></div>' + cta(lang)
    return (t("Our team", "Nuestro equipo"),
            t("Meet the bilingual dentists, surgeons and coordinators at TJ Medical Services in Tijuana and San Diego.",
              "Conozca a los dentistas, cirujanos y coordinadores bilingües de TJ Medical Services en Tijuana y San Diego."),
            body, None)


def faq_html(lang, heading_tag="h2"):
    out = ""
    for qe, qs, ae, as_ in FAQ:
        q, a = (qe, ae) if lang == "en" else (qs, as_)
        out += f'<details class="qa"><summary><{heading_tag}>{q}</{heading_tag}></summary><p>{a}</p></details>'
    return out


def p_faq(lang):
    t = lambda en, es: en if lang == "en" else es
    body = page_head(t("Frequently asked questions", "Preguntas frecuentes"),
                     t("Answers about prices, insurance, the border crossing, safety and recovery. Can't find yours? Call us any time.",
                       "Respuestas sobre precios, seguros, cruce fronterizo, seguridad y recuperación. ¿No encuentra la suya? Llámenos a cualquier hora.")) + \
        f'<div class="wrap prose">{faq_html(lang)}</div>' + cta(lang)
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": (qe if lang == "en" else qs),
         "acceptedAnswer": {"@type": "Answer", "text": (ae if lang == "en" else as_)}} for qe, qs, ae, as_ in FAQ]}]
    return (t("FAQ", "Preguntas frecuentes"),
            t("Questions about medical treatment in Tijuana: prices, insurance, border crossing, safety, deposits and recovery.",
              "Preguntas sobre tratamiento médico en Tijuana: precios, seguros, cruce fronterizo, seguridad, depósitos y recuperación."),
            body, ld)


def p_contact(lang):
    t = lambda en, es: en if lang == "en" else es
    hours = "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in HOURS[lang])
    opts = "".join(f'<option value="{s[lang]["name"]}">{s[lang]["name"]}</option>' for s in SERVICES)
    body = page_head(t("Contact and booking", "Contacto y citas"),
                     t("Call, message or send the form. Our phone line is answered 24/7, and a coordinator replies within one business day.",
                       "Llame, escriba o envíe el formulario. Nuestra línea se atiende 24/7 y un coordinador responde en un día hábil.")) + f"""
<div class="wrap two-col contact">
<div>
<h2>{t("Reach us", "Contáctenos")}</h2>
<dl class="facts">
<dt>{t("Phone (U.S.)", "Teléfono (EE. UU.)")}</dt><dd><a href="tel:{C['phone_us_tel']}">{C['phone_us']}</a></dd>
<dt>{t("Phone (Mexico)", "Teléfono (México)")}</dt><dd><a href="tel:{C['phone_mx_tel']}">{C['phone_mx']}</a></dd>
<dt>WhatsApp</dt><dd><a href="{C['whatsapp_link']}">{C['whatsapp']}</a></dd>
<dt>{t("Email", "Correo")}</dt><dd><a href="mailto:{C['email']}">{C['email']}</a></dd>
<dt>{t("Tijuana clinic", "Clínica Tijuana")}</dt><dd>{C['tj_address']}</dd>
<dt>{t("San Diego office", "Oficina San Diego")}</dt><dd>{C['sd_address']}</dd>
</dl>
<h2>{t("Hours", "Horario")}</h2>
<dl class="facts">{hours}</dl>
<p class="alert">{t("For a medical emergency, call 911. It works in both the United States and Mexico.", "En una emergencia médica, llame al 911. Funciona en Estados Unidos y en México.")}</p>
</div>
<div>
<h2>{t("Request a quote or consultation", "Solicite cotización o consulta")}</h2>
<form class="form" id="quote-form" data-email="{C['email']}" data-lang="{lang}">
<label>{t("Full name", "Nombre completo")}<input name="name" required autocomplete="name"></label>
<label>{t("Email", "Correo")}<input name="email" type="email" required autocomplete="email"></label>
<label>{t("Phone", "Teléfono")}<input name="phone" type="tel" autocomplete="tel"></label>
<label>{t("Treatment of interest", "Tratamiento de interés")}<select name="treatment">{opts}<option>{t("Not sure yet", "Aún no sé")}</option></select></label>
<label>{t("Preferred travel dates", "Fechas de viaje preferidas")}<input name="dates" placeholder="{t('e.g. mid-December', 'ej. mediados de diciembre')}"></label>
<label>{t("Anything we should know", "Algo que debamos saber")}<textarea name="notes" rows="4"></textarea></label>
<button class="btn" type="submit">{t("Send request", "Enviar solicitud")}</button>
<p class="small">{t("The form opens your email app with your request filled in. Please don't include detailed medical history here; your coordinator sends a secure questionnaire.", "El formulario abre su aplicación de correo con la solicitud ya escrita. No incluya historial médico detallado aquí; su coordinador le enviará un cuestionario seguro.")}</p>
</form>
</div>
</div>"""
    return (t("Contact", "Contacto"),
            t("Phone, WhatsApp, email, addresses and hours for TJ Medical Services in Tijuana and San Diego. Request a free quote.",
              "Teléfono, WhatsApp, correo, direcciones y horario de TJ Medical Services en Tijuana y San Diego. Solicite una cotización gratuita."),
            body, None)


def p_guide(lang):
    t = lambda en, es: en if lang == "en" else es
    body = page_head(t("Patient guide", "Guía del paciente"),
                     t("What to do before you travel, during your stay and after you go home.",
                       "Qué hacer antes de viajar, durante su estancia y después de regresar a casa.")) + f"""
<div class="wrap prose">
<h2>{t("Before you travel", "Antes de viajar")}</h2>
<ul class="ticks">
<li>{t("Complete the medical questionnaire your coordinator sends, and share recent X-rays, lab results or photos.", "Llene el cuestionario médico que le envía su coordinador y comparta radiografías, laboratorios o fotos recientes.")}</li>
<li>{t("Surgery patients: get any tests your surgeon requests (usually blood work and an ECG if you are over 40) and send the results at least 7 days before travel.", "Pacientes de cirugía: hágase los estudios que pida su cirujano (normalmente laboratorios y un electrocardiograma si tiene más de 40 años) y envíe los resultados al menos 7 días antes de viajar.")}</li>
<li>{t("Tell us about every medication and supplement you take. Your doctor will tell you which ones to stop and when — do not stop prescribed medication on your own.", "Infórmenos de todos los medicamentos y suplementos que toma. Su médico le dirá cuáles suspender y cuándo; no suspenda medicamentos recetados por su cuenta.")}</li>
<li>{t("Stop smoking and vaping at least 4 weeks before any surgery; it raises the risk of complications.", "Deje de fumar y vapear al menos 4 semanas antes de cualquier cirugía; aumenta el riesgo de complicaciones.")}</li>
<li>{t("Weight-loss surgery patients follow a 2-week pre-op liquid diet provided by our nutritionist.", "Los pacientes de cirugía bariátrica siguen una dieta líquida preoperatoria de 2 semanas indicada por nuestra nutrióloga.")}</li>
<li>{t("Buy travel insurance that covers medical travel, if you want coverage for cancelled flights or extended stays.", "Contrate un seguro de viaje que cubra viajes médicos si desea cobertura por vuelos cancelados o estancias más largas.")}</li>
</ul>
<h2>{t("What to pack", "Qué empacar")}</h2>
<ul class="ticks">
<li>{t("Passport or other border-crossing document", "Pasaporte u otro documento para cruzar la frontera")}</li>
<li>{t("Your medications in their original containers, and a written list", "Sus medicamentos en su envase original y una lista por escrito")}</li>
<li>{t("Loose, front-opening clothes and slip-on shoes", "Ropa holgada que abra por delante y zapatos sin agujetas")}</li>
<li>{t("Phone charger and any CPAP machine you use", "Cargador de teléfono y su equipo CPAP si lo usa")}</li>
<li>{t("Credit card or funds for the balance of your treatment", "Tarjeta o fondos para el saldo de su tratamiento")}</li>
</ul>
<h2>{t("During your stay", "Durante su estancia")}</h2>
<p>{t("Your coordinator meets you on arrival and is at every appointment. Before any procedure you sign an informed-consent form in English or Spanish, after your doctor explains the risks and answers your questions. Surgery patients stay 1 to 2 nights in hospital, then move to the recovery hotel with daily nurse visits.", "Su coordinador lo recibe a su llegada y lo acompaña en cada cita. Antes de cualquier procedimiento firma un consentimiento informado en español o inglés, después de que su médico le explique los riesgos y responda sus preguntas. Los pacientes de cirugía pasan 1 a 2 noches en el hospital y luego se trasladan al hotel de recuperación con visitas diarias de enfermería.")}</p>
<h2>{t("After you go home", "Después de regresar a casa")}</h2>
<ul class="ticks">
<li>{t("You leave with your records, imaging, operative report and medication instructions in English.", "Se va con su expediente, estudios, reporte quirúrgico e indicaciones de medicamentos en inglés.")}</li>
<li>{t("Follow-up calls at 1 day, 1 week, 1 month and 3 months, plus visits at our San Diego office if needed.", "Llamadas de seguimiento al día 1, semana 1, mes 1 y mes 3, y visitas en nuestra oficina de San Diego si se necesitan.")}</li>
<li>{t("Wait at least 7 days after body surgery and 3 days after weight-loss surgery before flying long distances, unless your surgeon says otherwise.", "Espere al menos 7 días después de cirugía corporal y 3 días después de cirugía bariátrica antes de volar distancias largas, salvo que su cirujano indique otra cosa.")}</li>
<li>{t("Call the 24/7 on-call number on your discharge card with any question about your recovery.", "Llame al número de guardia 24/7 de su tarjeta de alta con cualquier duda sobre su recuperación.")}</li>
<li class="strong">{t("Go to an emergency room or call 911 right away for chest pain, trouble breathing, heavy bleeding, fever above 101°F (38.3°C), or severe pain or swelling in one leg.", "Acuda a urgencias o llame al 911 de inmediato si tiene dolor en el pecho, dificultad para respirar, sangrado abundante, fiebre mayor a 38.3 °C (101 °F), o dolor o hinchazón intensa en una pierna.")}</li>
</ul>
</div>""" + cta(lang)
    return (t("Patient guide", "Guía del paciente"),
            t("How to prepare for treatment in Tijuana, what to pack, what happens during your stay and how follow-up works.",
              "Cómo prepararse para su tratamiento en Tijuana, qué empacar, qué pasa durante su estancia y cómo es el seguimiento."),
            body, None)


def p_payments(lang):
    t = lambda en, es: en if lang == "en" else es
    body = page_head(t("Payments and policies", "Pagos y políticas"),
                     t("How to pay, how deposits and cancellations work, what our guarantees cover, and how we handle your information.",
                       "Cómo pagar, cómo funcionan los depósitos y cancelaciones, qué cubren nuestras garantías y cómo cuidamos su información.")) + f"""
<div class="wrap prose">
<h2>{t("Payment methods", "Formas de pago")}</h2>
<p>{t("Visa, Mastercard, American Express, debit cards, bank wire transfer, and cash in U.S. dollars or Mexican pesos. Card payments have no surcharge. Patient financing is available through third-party lenders, subject to their approval; your coordinator can send the application link.", "Visa, Mastercard, American Express, tarjetas de débito, transferencia bancaria y efectivo en dólares o pesos mexicanos. Los pagos con tarjeta no tienen recargo. Hay financiamiento con terceros, sujeto a su aprobación; su coordinador puede enviarle el enlace de solicitud.")}</p>
<h2>{t("Deposits", "Depósitos")}</h2>
<ul class="ticks">
<li>{t("Surgery: $500 deposit to reserve your date; balance due at your pre-op appointment.", "Cirugía: depósito de $500 dólares para reservar la fecha; saldo en su cita preoperatoria.")}</li>
<li>{t("Dental treatment over $2,000: $200 deposit; each phase is paid when it is completed.", "Tratamiento dental mayor a $2,000 dólares: depósito de $200 dólares; cada fase se paga al terminarla.")}</li>
<li>{t("Consultations, check-ups and imaging: no deposit; pay on the day.", "Consultas, chequeos y estudios: sin depósito; se paga el mismo día.")}</li>
</ul>
<h2>{t("Cancellations and changes", "Cancelaciones y cambios")}</h2>
<ul class="ticks">
<li>{t("14 or more days before your date: full deposit refund.", "Con 14 días o más de anticipación: reembolso total del depósito.")}</li>
<li>{t("Fewer than 14 days: the deposit can be moved once to a new date within 12 months, but is not refunded.", "Con menos de 14 días: el depósito puede cambiarse una vez a otra fecha dentro de 12 meses, pero no se reembolsa.")}</li>
<li>{t("If your doctor decides the procedure is not safe for you, your deposit is refunded in full.", "Si su médico determina que el procedimiento no es seguro para usted, el depósito se reembolsa por completo.")}</li>
<li>{t("Refunds go back to the original payment method within 10 business days.", "Los reembolsos se hacen al método de pago original en 10 días hábiles.")}</li>
</ul>
<h2>{t("Insurance", "Seguros")}</h2>
<p>{t("We do not bill insurance companies directly. You receive an itemized invoice in English with procedure codes to submit an out-of-network claim. Check with your insurer before traveling; most U.S. and Canadian plans do not cover elective treatment abroad.", "No facturamos directamente a aseguradoras. Recibe una factura detallada en inglés con códigos de procedimiento para presentar un reembolso fuera de red. Consulte con su aseguradora antes de viajar; la mayoría de los planes de EE. UU. y Canadá no cubren tratamientos electivos en el extranjero.")}</p>
<h2>{t("Guarantees", "Garantías")}</h2>
<ul class="ticks">
<li>{t("Surgery: corrective procedures related to the original surgery are covered for 12 months (surgeon and facility fees); travel is not covered.", "Cirugía: los procedimientos correctivos relacionados con la cirugía original están cubiertos por 12 meses (honorarios y hospital); el viaje no está cubierto.")}</li>
<li>{t("Dental implants: 5 years on the implant fixture; crowns and veneers: 2 years against breakage under normal use.", "Implantes dentales: 5 años en el implante; coronas y carillas: 2 años contra fractura en uso normal.")}</li>
<li>{t("Guarantees require attending the follow-up appointments in your care plan.", "Las garantías requieren asistir a las citas de seguimiento de su plan de atención.")}</li>
</ul>
<h2>{t("Privacy", "Privacidad")}</h2>
<p>{t("We handle your personal and medical information under Mexico's federal personal-data protection law and only share it with the doctors treating you, or with others you authorize in writing. Calls to our phone line may be answered by an AI virtual receptionist and recorded to improve service; you can ask for a person at any time.", "Tratamos sus datos personales y médicos conforme a la ley federal mexicana de protección de datos personales y solo los compartimos con los médicos que lo atienden o con quien usted autorice por escrito. Las llamadas a nuestra línea pueden ser atendidas por una recepcionista virtual con IA y grabadas para mejorar el servicio; puede pedir hablar con una persona en cualquier momento.")}</p>
</div>""" + cta(lang)
    return (t("Payments and policies", "Pagos y políticas"),
            t("Payment methods, deposits, cancellation policy, insurance, guarantees and privacy at TJ Medical Services.",
              "Formas de pago, depósitos, política de cancelación, seguros, garantías y privacidad en TJ Medical Services."),
            body, None)


def p_reference(lang):
    """Dense, plain-language fact sheet for the AI receptionist (and anyone who wants everything on one page)."""
    t = lambda en, es: en if lang == "en" else es
    svc = ""
    for s in SERVICES:
        d = s[lang]
        svc += f"<h3>{d['name']}</h3><p>{' '.join(d['body'])}</p><p>{t('Treatments', 'Tratamientos')}: {'; '.join(d['list'])}.</p><p>{d['visits']}</p>"
    prices = ""
    for sid, rows in PRICES:
        items = "; ".join(
            f"{(en if lang == 'en' else es)}: {(t('from', 'desde') + ' ') if n else ''}{money(n, lang)}{(' ' + (ue if lang == 'en' else us)) if (ue or us) else ''}"
            for en, es, n, ue, us in rows
        )
        prices += f"<p><strong>{SERVICE_BY_ID[sid][lang]['name']}</strong> — {items}.</p>"
    hours = "".join(f"<li>{a}: {b}</li>" for a, b in HOURS[lang])
    team = "".join(f"<li>{n} — {re if lang == 'en' else rs}. {be if lang == 'en' else bs}</li>" for n, re, rs, be, bs in TEAM)
    faq = "".join(f"<h3>{qe if lang == 'en' else qs}</h3><p>{ae if lang == 'en' else as_}</p>" for qe, qs, ae, as_ in FAQ)
    body = page_head(t("Clinic fact sheet", "Ficha de la clínica"),
                     t("Everything about TJ Medical Services on one page: services, prices, hours, locations, travel, policies and answers to common questions. This page is also the knowledge source for our virtual receptionist.",
                       "Todo sobre TJ Medical Services en una página: servicios, precios, horario, sedes, viaje, políticas y respuestas a preguntas comunes. Esta página también es la fuente de información de nuestra recepcionista virtual.")) + f"""
<div class="wrap prose reference">
<h2>{t("About the clinic", "Sobre la clínica")}</h2>
<p>{t("TJ Medical Services is a bilingual (English and Spanish) medical clinic for patients from the United States and Canada. Procedures happen at our clinic in Zona Río, Tijuana, Baja California, Mexico. Our office in San Ysidro, San Diego, California handles consultations, pre-op and post-op visits and transport to the clinic. Prices are typically 40% to 70% below U.S. prices.", "TJ Medical Services es una clínica bilingüe (español e inglés) para pacientes de Estados Unidos y Canadá. Los procedimientos se realizan en nuestra clínica en Zona Río, Tijuana, Baja California, México. Nuestra oficina en San Ysidro, San Diego, California atiende consultas, citas pre y postoperatorias y el traslado a la clínica. Los precios suelen ser 40% a 70% menores que en Estados Unidos.")}</p>

<h2>{t("Contact details", "Datos de contacto")}</h2>
<ul>
<li>{t("U.S. phone", "Teléfono EE. UU.")}: {C['phone_us']}</li>
<li>{t("Mexico phone", "Teléfono México")}: {C['phone_mx']}</li>
<li>WhatsApp: {C['whatsapp']}</li>
<li>{t("Email", "Correo")}: {C['email']}</li>
<li>{t("Tijuana clinic address", "Dirección clínica Tijuana")}: {C['tj_address']}</li>
<li>{t("San Diego office address", "Dirección oficina San Diego")}: {C['sd_address']}</li>
<li>{t("Website", "Sitio web")}: {C['url']}</li>
</ul>

<h2>{t("Hours", "Horario")}</h2>
<ul>{hours}</ul>

<h2>{t("Services", "Servicios")}</h2>
{svc}

<h2>{t("Starting prices (U.S. dollars)", "Precios desde (dólares estadounidenses)")}</h2>
<p>{t("All prices are starting prices. The final price is confirmed in a written quote after a doctor reviews the patient's case, usually within 2 business days. Surgery packages include surgeon, anesthesia and operating-room fees, pre-op tests, hospital stay, recovery-hotel nights with nurse visits, airport pickup at SAN or TIJ, local transport, the medical-lane crossing pass when eligible, and follow-up. Flights, meals outside the hospital and travel insurance are not included. Dental travel packages with hotel and transport start at $150 per night.", "Todos los precios son precios desde. El precio final se confirma en una cotización por escrito después de que un médico revise el caso, normalmente en 2 días hábiles. Los paquetes de cirugía incluyen honorarios del cirujano, anestesia y quirófano, estudios preoperatorios, estancia hospitalaria, noches de hotel de recuperación con visitas de enfermería, recogida en aeropuerto SAN o TIJ, transporte local, pase de carril médico cuando aplique y seguimiento. No incluyen vuelos, comidas fuera del hospital ni seguro de viaje. Los paquetes de viaje dental con hotel y transporte inician en $150 dólares por noche.")}</p>
{prices}

<h2>{t("Booking process", "Proceso para agendar")}</h2>
<p>{t("1) The patient calls, messages on WhatsApp, emails or sends the website form. 2) A coordinator sends a medical questionnaire and collects X-rays, photos or lab results. 3) A doctor reviews the case and the patient receives a written, itemized quote within 2 business days; surgery candidates also get a free video consultation with the surgeon. 4) A refundable deposit reserves the date. 5) The coordinator books transport and hotel and sends a day-by-day itinerary.", "1) El paciente llama, escribe por WhatsApp, envía correo o el formulario del sitio. 2) Un coordinador envía un cuestionario médico y recaba radiografías, fotos o laboratorios. 3) Un médico revisa el caso y el paciente recibe una cotización detallada por escrito en 2 días hábiles; los candidatos a cirugía también reciben una videoconsulta gratuita con el cirujano. 4) Un depósito reembolsable reserva la fecha. 5) El coordinador reserva transporte y hotel y envía un itinerario día por día.")}</p>

<h2>{t("Travel and border crossing", "Viaje y cruce fronterizo")}</h2>
<p>{t("Most patients fly into San Diego International Airport (SAN). Surgery patients are picked up at SAN arrivals. Patients can also fly into Tijuana International Airport (TIJ) or use the Cross Border Xpress (CBX) bridge. A free shuttle runs from the San Diego office to the Tijuana clinic every hour on the hour, 7:00 a.m. to 3:00 p.m., Monday to Saturday; seats must be reserved. The San Diego office is about 5 minutes from the San Ysidro port of entry, and the clinic is about 15 minutes by car from the border. Eligible patients get a free medical quick-crossing pass from the City of Tijuana for the medical lane at San Ysidro and Otay Mesa when returning to the U.S.; the clinic never sells passes, and lane hours are set by the city. U.S. citizens need a passport, passport card, or SENTRI/Global Entry card to return to the U.S.; Canadians need a passport. Tijuana is on Pacific Time.", "La mayoría de los pacientes vuela al Aeropuerto Internacional de San Diego (SAN). A los pacientes de cirugía se les recoge en llegadas de SAN. También pueden volar al Aeropuerto de Tijuana (TIJ) o usar el puente Cross Border Xpress (CBX). Un traslado gratuito sale de la oficina de San Diego a la clínica cada hora en punto, de 7:00 a.m. a 3:00 p.m., de lunes a sábado; se debe reservar lugar. La oficina de San Diego está a unos 5 minutos de la garita de San Ysidro y la clínica a unos 15 minutos en auto de la frontera. Los pacientes elegibles reciben un pase médico de cruce ágil gratuito del Ayuntamiento de Tijuana para el carril médico en San Ysidro y Otay al regresar a EE. UU.; la clínica nunca vende pases y el horario del carril lo define el ayuntamiento. Los ciudadanos estadounidenses necesitan pasaporte, passport card o tarjeta SENTRI/Global Entry para regresar; los canadienses necesitan pasaporte. Tijuana usa la hora del Pacífico.")}</p>

<h2>{t("Payments, deposits and insurance", "Pagos, depósitos y seguros")}</h2>
<p>{t("Accepted: Visa, Mastercard, American Express, debit cards, wire transfer, cash in USD or MXN; no card surcharge; third-party financing subject to approval. Deposits: $500 for surgery, $200 for dental treatment over $2,000, none for consultations, check-ups or imaging. Deposits are fully refunded with 14 or more days' notice or if the doctor finds the procedure unsafe; with less notice, the deposit can be moved once to a date within 12 months. Refunds take up to 10 business days. The clinic does not bill insurance directly but provides itemized invoices with procedure codes for out-of-network claims. Guarantees: 12 months on corrective procedures related to surgery; 5 years on dental implant fixtures; 2 years on crowns and veneers.", "Se aceptan: Visa, Mastercard, American Express, débito, transferencia, efectivo en USD o MXN; sin recargo por tarjeta; financiamiento con terceros sujeto a aprobación. Depósitos: $500 dólares para cirugía, $200 dólares para tratamiento dental mayor a $2,000, ninguno para consultas, chequeos o estudios. El depósito se reembolsa completo con 14 días o más de aviso o si el médico determina que el procedimiento no es seguro; con menos aviso, puede cambiarse una vez a otra fecha dentro de 12 meses. Los reembolsos tardan hasta 10 días hábiles. La clínica no factura a aseguradoras, pero entrega facturas detalladas con códigos para reembolsos fuera de red. Garantías: 12 meses en procedimientos correctivos de cirugía; 5 años en implantes dentales; 2 años en coronas y carillas.")}</p>

<h2>{t("Medical team", "Equipo médico")}</h2>
<ul>{team}</ul>

<h2>{t("Rules for the virtual receptionist", "Reglas para la recepcionista virtual")}</h2>
<ul>
<li>{t("If a caller describes chest pain, trouble breathing, heavy bleeding, fainting, signs of stroke, or any emergency: tell them to hang up and call 911 now (911 works in the U.S. and Mexico).", "Si quien llama describe dolor en el pecho, dificultad para respirar, sangrado abundante, desmayo, signos de derrame cerebral o cualquier emergencia: indíquele que cuelgue y llame al 911 de inmediato (funciona en EE. UU. y México).")}</li>
<li>{t("Post-operative patients with urgent but non-emergency concerns (fever, wound changes, nausea): transfer to the on-call nurse.", "Pacientes postoperatorios con dudas urgentes pero no de emergencia (fiebre, cambios en la herida, náusea): transferir a la enfermera de guardia.")}</li>
<li>{t("Never diagnose, recommend a specific treatment, say whether someone is a candidate, or give medication advice. Offer a free consultation or a nurse callback instead.", "Nunca diagnosticar, recomendar un tratamiento específico, decir si alguien es candidato ni dar indicaciones de medicamentos. Ofrecer una consulta gratuita o una llamada de enfermería.")}</li>
<li>{t("Always describe prices as starting prices and explain that the final price comes in a written quote.", "Siempre presentar los precios como precios desde y explicar que el precio final llega en una cotización por escrito.")}</li>
<li>{t("Never promise a specific medical-lane wait time, crossing time or result of a procedure.", "Nunca prometer un tiempo de espera en el carril médico, tiempo de cruce ni resultado de un procedimiento.")}</li>
<li>{t("To book: book the consultation or evaluation directly in the calendar (name and phone number required, email optional) and tell the caller a WhatsApp confirmation will arrive shortly. Reschedules and cancellations are also confirmed by WhatsApp.", "Para agendar: reservar la consulta o evaluación directamente en el calendario (nombre y teléfono obligatorios, correo opcional) e informar que en breve llegará una confirmación por WhatsApp. Los cambios y cancelaciones también se confirman por WhatsApp.")}</li>
<li>{t("If the caller asks for the clinic or office address, offer to send it by WhatsApp to the number they are calling from, and only send it if they agree.", "Si quien llama pide la dirección de la clínica o de la oficina, ofrecer enviarla por WhatsApp al número desde el que llama, y solo enviarla si acepta.")}</li>
<li>{t("Answer in the caller's language (English or Spanish). If a caller asks for a person, transfer them or take a callback request.", "Responder en el idioma de quien llama (español o inglés). Si pide hablar con una persona, transferir o tomar una solicitud de devolución de llamada.")}</li>
</ul>

<h2>{t("Frequently asked questions", "Preguntas frecuentes")}</h2>
{faq}
</div>"""
    return (t("Clinic fact sheet", "Ficha de la clínica"),
            t("Complete fact sheet for TJ Medical Services: services, starting prices, hours, addresses, travel, payment policies and FAQ.",
              "Ficha completa de TJ Medical Services: servicios, precios desde, horario, direcciones, viaje, políticas de pago y preguntas frecuentes."),
            body, None)


BUILDERS = {
    "index": p_index, "services": p_services, "prices": p_prices, "travel": p_travel, "team": p_team,
    "faq": p_faq, "contact": p_contact, "patient-guide": p_guide, "payments": p_payments, "reference": p_reference,
}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    urls = []
    for lang in ("en", "es"):
        for slug, *_ in PAGES:
            title, desc, body, ld = BUILDERS[slug](lang)
            html = layout(slug, lang, title, desc, body, ld)
            sub = "" if lang == "en" else "es"
            write(os.path.join(OUT, sub, f"{slug}.html"), html)
            urls.append(C["url"] + ("/es" if lang == "es" else "") + ("/" if slug == "index" else "/" + slug))

    # 404
    title, desc = "Page not found", "Page not found"
    body = page_head("Page not found / Página no encontrada",
                     'This page doesn\'t exist. <a href="/">Go to the home page</a> · <a href="/es/">Ir a la página de inicio</a>')
    write(os.path.join(OUT, "404.html"), layout("index", "en", title, desc, body))

    write(os.path.join(OUT, "sitemap.xml"),
          '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write(os.path.join(OUT, "robots.txt"), f"User-agent: *\nAllow: /\nSitemap: {C['url']}/sitemap.xml\n")
    write(os.path.join(OUT, "llms.txt"),
          f"# {C['name']}\n\n> Fictional bilingual medical clinic in Tijuana, Mexico, with an office in San Ysidro, San Diego. Demo knowledge base for an AI receptionist.\n\n"
          f"- [Clinic fact sheet (everything on one page)]({C['url']}/reference)\n"
          f"- [Ficha de la clínica (español)]({C['url']}/es/reference)\n"
          + "".join(f"- [{LABEL[s]['en']}]({C['url']}/{'' if s == 'index' else s})\n" for s, *_ in PAGES if s != "reference"))
    # Contact facts for the WhatsApp functions in api/ (TypeScript reads this instead of duplicating data.py)
    clinic_ts = {k: C[k] for k in ("name", "phone_us", "whatsapp", "tj_address", "sd_address", "url")}
    write(os.path.join(ROOT, "lib", "notifications", "clinic.generated.ts"),
          "// Generated by src/build.py from src/data.py. Do not edit.\n"
          f"export const CLINIC = {json.dumps(clinic_ts, ensure_ascii=False, indent=2)} as const;\n")
    print(f"Built {len(urls)} pages into {OUT}")


if __name__ == "__main__":
    main()
