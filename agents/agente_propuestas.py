"""
agente_propuestas.py
====================
Redacta propuestas freelance para Workana/Fiverr usando
los insights de encuestas + leads scrapeados.

Llamado por coordinador.py (cada 12h junto con leads,
o manualmente: python agents/agente_propuestas.py)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))
from bus import init as bus_init, write as bus_write
from social_agents.config import GroqConfig

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
LEADS_FILE = DATA_DIR / "leads.json"
INSIGHT_FILE = DATA_DIR / "insight_actual.json"
PROPUESTAS_DIR = DATA_DIR / "propuestas"

GROQ = GroqConfig()

# --- Tu perfil (edítalo cuando quieras) ---
PERFIL = {
    "nombre": "Steve",
    "skills": ["Automatización con IA", "Agentes autónomos", "Contenido para redes", "Scraping", "Pipelines de datos"],
    "precio_mensual": "$801 - $1,200 MXN",
    "precio_por_proyecto": "$500 - $3,000 MXN",
    "idiomas": ["Español", "Inglés básico"],
    "disponibilidad": "Inmediata",
}


def _llm_call(prompt: str, system: str = "") -> str:
    import requests
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ.api_key}", "Content-Type": "application/json"},
        json={"model": GROQ.model, "messages": msgs, "temperature": 0.7, "max_tokens": 2048},
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            pass
    return default


def _save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


PROMPT_INSIGHT = """
Eres un analista de mercado. Con base en estos datos de encuestas internas,
responde en JSON:
- "nicho": string (sector a atacar)
- "pricing": string (rango de precio recomendado)
- "valor_propuesto": string (1 frase de lo que el cliente gana)
- "urgencia": string (por qué contratar YA)

Datos:
{datos}

SOLO JSON.
"""

PROMPT_PROPIESTA = """
Redacta una propuesta freelance para Workana.

DATOS DEL CLIENTE:
{lead}

MI PERFIL:
{perfil}

INSIGHT DE MERCADO:
{insight}

REGLAS:
- Max 200 palabras
- Tono: profesional pero cercano (no robótico)
- Estructura: saludo corto -> entiendo tu necesidad -> lo que haré (3 bullets) -> precio -> CTA
- NO usar: "espero que estés bien", "me gustaría", "quedo atento"
- SÍ usar: verbos de acción, números concretos, resultados medibles

Devuelve SOLO el texto de la propuesta, sin markdown.
"""


def run() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROPUESTAS_DIR.mkdir(parents=True, exist_ok=True)
    bus_init()

    # 1. Cargar leads
    leads = _load_json(LEADS_FILE, [])
    if not isinstance(leads, list):
        leads = []

    # Filtrar leads sin propuesta aún
    pendientes = [l for l in leads if not l.get("propuesta_id")]

    if not pendientes:
        bus_write(agent="propuestas", estado="sin_leads",
                  resultado=json.dumps({"pendientes": 0}))
        print("[propuestas] Sin leads pendientes.")
        return {"status": "ok", "generadas": 0}

    # 2. Cargar insight (o generar uno si no hay)
    insight = _load_json(INSIGHT_FILE, None)
    if not insight:
        encuestas = _load_json(DATA_DIR / "encuestas_internas.json", [])
        completadas = [e for e in encuestas if e.get("status") == "completed"]
        if completadas:
            try:
                raw = _llm_call(
                    PROMPT_INSIGHT.format(datos=json.dumps(completadas, ensure_ascii=False)),
                    system="Responde SOLO en JSON valido."
                )
                insight = json.loads(_clean_json(raw))
                _save_json(INSIGHT_FILE, insight)
            except Exception as e:
                print(f"[propuestas] Error insight: {e}", file=sys.stderr)
                insight = {"nicho": "marketing digital", "pricing": "$801-$1200 MXN",
                           "valor_propuesto": "Ahorra 10h/semana en contenido", "urgencia": "Cada día sin automatizar es dinero perdido"}
        else:
            insight = {"nicho": "marketing digital", "pricing": "$801-$1200 MXN",
                       "valor_propuesto": "Ahorra 10h/semana en contenido", "urgencia": "Cada día sin automatizar es dinero perdido"}

    # 3. Generar propuestas (máx 3 por ciclo para no gastar mucho)
    generadas = 0
    for lead in pendientes[:3]:
        try:
            texto = _llm_call(
                PROMPT_PROPIESTA.format(
                    lead=json.dumps(lead, ensure_ascii=False),
                    perfil=json.dumps(PERFIL, ensure_ascii=False),
                    insight=json.dumps(insight, ensure_ascii=False),
                ),
                system="Eres un freelancer experto en IA y automatización. Redacta propuestas que cierren."
            )

            # Guardar
            fecha = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            out_file = PROPUESTAS_DIR / f"propuesta_{fecha}.txt"
            out_file.write_text(texto, encoding="utf-8")

            # Marcar lead
            lead["propuesta_id"] = out_file.name
            lead["propuesta_fecha"] = fecha

            generadas += 1
            print(f"[propuestas] ✅ {out_file.name}")

        except Exception as e:
            print(f"[propuestas] Error: {e}", file=sys.stderr)

    # Guardar leads actualizados
    _save_json(LEADS_FILE, leads)

    # 4. Publicar en bus
    bus_write(
        agent="propuestas",
        estado=f"generadas_{generadas}",
        resultado=json.dumps({"generadas": generadas, "pendientes": len(pendientes) - generadas})
    )

    return {"status": "ok", "generadas": generadas}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))