"""
agentes_leads.py — Scraper de Workana (Playwright) → data/leads.json + bus
Ejecución: python agents/agentes_leads.py
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import bus

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LEADS_FILE = DATA_DIR / "leads.json"

SEARCHES = [
    ("marketing digital", "sales-marketing"),
    ("redes sociales", "sales-marketing"),
    ("contenido", "sales-marketing"),
    ("automatización", "it-programming"),
    ("inteligencia artificial", "it-programming"),
    ("chatbot", "it-programming"),
]

MAX_PAGES = 3
DELAY_S = 4.0

RELEVANCE_KEYWORDS = [
    "marketing", "redes", "social media", "contenido", "publicidad",
    "branding", "automatiz", "ia", "inteligencia artificial", "chatbot",
    "pipeline", "scraping", "crm", "email marketing", "copywriting",
    "freelance", "agencia", "community", "video", "landing",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("agentes_leads")


@dataclass
class Lead:
    titulo: str
    slug: str
    url: str
    descripcion: str
    presupuesto: str
    skills: list
    total_bids: int
    publicado: str
    scrapeado_en: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        return asdict(self)


def _is_relevant(texto: str) -> bool:
    t = texto.lower()
    return any(kw in t for kw in RELEVANCE_KEYWORDS)


def _build_url(query: str, category: str, page: int = 1) -> str:
    params = []
    if query:
        params.append(f"query={query.replace(' ', '+')}")
    if category:
        params.append(f"category={category}")
    if page > 1:
        params.append(f"page={page}")
    return f"https://www.workana.com/es/jobs?{'&'.join(params)}"


def scrape_with_playwright() -> list:
    from playwright.sync_api import sync_playwright
    all_leads = []
    seen_slugs = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            locale="es-MX",
        )
        page = context.new_page()

        for query, category in SEARCHES:
            log.info("Buscando: '%s' [%s]", query, category)

            for pg in range(1, MAX_PAGES + 1):
                url = _build_url(query, category, pg)
                log.info("  -> %s", url)

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(8)
                except Exception as e:
                    log.warning("  Error: %s", e)
                    break

                links = page.query_selector_all("a[href*='/job/']")
                log.info("  Jobs encontrados: %d", len(links))

                if not links:
                    break

                for link in links:
                    try:
                        href = link.get_attribute("href") or ""
                        if href.startswith("/"):
                            href = "https://www.workana.com" + href

                        slug = href.rstrip("/").split("/")[-1]
                        if not slug or slug in seen_slugs:
                            continue

                        titulo = (link.inner_text() or "").strip()
                        if not titulo:
                            continue

                        # Contexto de la tarjeta
                        card = link.evaluate_handle(
                            "el => el.closest('article, li, [class*=job], [class*=card], [class*=project]') || el.parentElement"
                        ).as_element()

                        descripcion = ""
                        presupuesto = ""
                        skills = []
                        total_bids = 0
                        publicado = ""

                        if card:
                            card_text = card.inner_text() or ""

                            bm = re.search(
                                r"(\$|USD|MXN|EUR|GBP)\s*[\d,]+(?:\s*[-\u2013\u2014]\s*[\d,]+)?(?:\s*/\s*(?:hora|hour|hr))?",
                                card_text, re.I
                            )
                            if bm:
                                presupuesto = bm.group(0).strip()

                            bm2 = re.search(
                                r"(\d+)\s*(?:proposals?|interested|interesados?|propuestas?)",
                                card_text, re.I
                            )
                            if bm2:
                                total_bids = int(bm2.group(1))

                            lines = [l.strip() for l in card_text.split("\n") if l.strip()]
                            desc_lines = [
                                l for l in lines
                                if len(l) > 30 and l != titulo and presupuesto not in l
                            ]
                            if desc_lines:
                                descripcion = " ".join(desc_lines[:3])[:600]

                            for se in card.query_selector_all("[class*=skill], [class*=tag], [class*=chip]"):
                                st = (se.inner_text() or "").strip()
                                if st and len(st) < 30 and st not in skills:
                                    skills.append(st)

                        if not _is_relevant(titulo + " " + descripcion):
                            continue

                        seen_slugs.add(slug)
                        all_leads.append(Lead(
                            titulo=titulo,
                            slug=slug,
                            url=href,
                            descripcion=descripcion,
                            presupuesto=presupuesto,
                            skills=skills[:10],
                            total_bids=total_bids,
                            publicado=publicado,
                        ))
                        log.info("    + %s", titulo[:60])

                    except Exception:
                        continue

                time.sleep(DELAY_S)

        browser.close()

    log.info("Total leads relevantes: %d", len(all_leads))
    return all_leads


def save_leads(leads: list) -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existentes = []
    if LEADS_FILE.exists():
        try:
            existentes = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
        except Exception:
            existentes = []

    slugs_existentes = {l.get("slug", "") for l in existentes}
    nuevos = [l.to_dict() for l in leads if l.slug not in slugs_existentes]
    LEADS_FILE.write_text(
        json.dumps(existentes + nuevos, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return len(nuevos)


def main():
    log.info("=== agentes_leads.py - inicio ===")
    t0 = time.time()

    leads = scrape_with_playwright()
    nuevos = save_leads(leads)
    elapsed = time.time() - t0

    log.info("=== Completo en %.1fs | %d scrapeados, %d nuevos ===", elapsed, len(leads), nuevos)

    resultado = json.dumps({
        "total_scrapeados": len(leads),
        "nuevos": nuevos,
        "archivo": "data/leads.json",
        "tiempo_segundos": round(elapsed, 1),
    }, ensure_ascii=False)

    bus.write(
        agent="agentes_leads",
        estado="completado" if leads else "sin_resultados",
        problema=None if leads else "No se encontraron leads relevantes",
        propuesta=None,
        resultado=resultado,
    )
    log.info("Publicado en bus.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
