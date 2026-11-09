from social_agents.config import GroqConfig   

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
import os
GROQ = type("GroqConfig", (), {"api_key": os.getenv("GROQ_API_KEY", ""), "model": "openai/gpt-oss-120b"})()   

sys.path.insert(0, str(Path(__file__).parent.parent))
from bus import init as bus_init, write as bus_write
from social_agents.config import GroqConfig

DATA_DIR = Path(__file__).parent / "data"
ENCUESTAS_FILE = DATA_DIR / "encuestas_internas.json"
RESULTADOS_FILE = DATA_DIR / "resultados_encuestas.json"

GROQ = GroqConfig()


def _llm_call(prompt: str) -> str:
    import requests
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ.api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ.model,
            "messages": [
                {"role": "system", "content": "Eres un analista de mercado freelance. Responde SOLO en JSON valido, sin markdown fences."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        },
        timeout=60,
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
        except json.JSONDecodeError:
            pass
    return default


def _save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


PROMPT_GENERAR = """
Genera 3 encuestas internas para un freelancer en Mexico que vende servicios de IA y automatizacion de contenido.

Cada encuesta debe tener:
- "id": string
- "tema": string (max 60 chars)
- "pregunta": string
- "opciones": array de 3-4 strings
- "objetivo": string (pricing, nicho, contenido, validacion)
- "fecha": string ISO

Devuelve SOLO el JSON array, sin texto adicional.
"""

PROMPT_ANALIZAR = """
Aqui tienes los resultados acumulados de encuestas internas:

{resultados}

Responde en JSON:
- "insight": string
- "recomendacion_pricing": string
- "recomendacion_nicho": string
- "idea_contenido": string
- "prioridad": "alta" | "media" | "baja"

SOLO JSON, sin markdown.
"""


def run() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    bus_init()
    encuestas = _load_json(ENCUESTAS_FILE, [])
    resultados = _load_json(ENCUESTAS_FILE, [])

    pendientes = [e for e in encuestas if e.get("status") == "pending"]

    if len(pendientes) < 10:
        try:
            raw = _llm_call(PROMPT_GENERAR)
            nuevas = json.loads(_clean_json(raw))
            if isinstance(nuevas, list):
                existing_ids = {e["id"] for e in encuestas}
                for enc in nuevas:
                    if enc.get("id") not in existing_ids:
                        enc["status"] = "pending"
                        encuestas.append(enc)
                _save_json(ENCUESTAS_FILE, encuestas)
                bus_write(
                    agent="encuestas",
                    estado=f"generadas_{len(nuevas)}",
                    propuesta="Nuevas encuestas listas para responder"
                )
                print(f"[encuestas] Generadas {len(nuevas)} nuevas.")
        except Exception as e:
            bus_write(agent="encuestas", estado="error", problema=str(e))
            print(f"[encuestas] Error generando: {e}", file=sys.stderr)

    completadas = [e for e in encuestas if e.get("status") == "completed"]

    if len(completadas) >= 3:
        try:
            resumen = json.dumps(completadas[-20:], ensure_ascii=False)
            raw = _llm_call(PROMPT_ANALIZAR.format(resultados=resumen))
            insight = json.loads(_clean_json(raw))
            bus_write(
                agent="encuestas",
                estado="insight",
                resultado=json.dumps(insight, ensure_ascii=False)
            )
            print(f"[encuestas] Insight: {insight.get('insight', 'N/A')}")
        except Exception as e:
            bus_write(agent="encuestas", estado="error_analisis", problema=str(e))
            print(f"[encuestas] Error analizando: {e}", file=sys.stderr)

    bus_write(
        agent="encuestas",
        estado="ciclo_completado",
        resultado=json.dumps({"total": len(encuestas), "pendientes": len(pendientes), "resultados": len(completadas)})
    )

    return {
        "status": "ok",
        "encuestas_totales": len(encuestas),
        "pendientes": len(pendientes),
        "resultados": len(completadas),
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
