import json, sys, shutil, requests
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
BUS_FILE = BASE / "bus.json"
ORDERS_FILE = BASE / "orders.json"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "cerebro.log"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def load_key():
    key_file = BASE / "groq_key.txt"
    if key_file.exists():
        return key_file.read_text().strip()
    return ""

GROQ_KEY = load_key()

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def clean_json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]
    return raw.strip()

def backup_orders():
    """Copia orders.json a logs/orders_backup.json antes de sobrescribirlo."""
    if ORDERS_FILE.exists():
        shutil.copy2(ORDERS_FILE, LOG_DIR / "orders_backup.json")

PROMPT = """Eres el cerebro de un sistema de agentes.
Analiza el estado actual y responde en JSON con:
1. "diagnostico": qué está pasando (1 frase)
2. "orden": qué debe hacer cada agente (lista de {{agente, accion}})
3. "alerta": si hay algo urgente que el usuario deba saber (o null)
4. "voz": una frase corta que se le va a decir al usuario por voz (máx 20 palabras)

Responde SOLO en JSON."""

def think(contexto=None):
    if contexto is None:
        if not BUS_FILE.exists():
            log("Sin bus.json, sin datos")
            return {"diagnostico": "Sin datos", "orden": [], "alerta": None, "voz": "No hay datos aún."}
        messages = json.loads(BUS_FILE.read_text())["messages"]
        if not messages:
            log("Bus vacío")
            return {"diagnostico": "Bus vacío", "orden": [], "alerta": None, "voz": "Todo en calma."}
        contexto = "\n".join([
            f'[{m["timestamp"]}] {m["agent"]}: {m["estado"]}'
            + (f' Problema: {m["problema"]}' if m.get("problema") else "")
            + (f' Propuesta: {m["propuesta"]}' if m.get("propuesta") else "")
            + (f' Resultado: {m["resultado"]}' if m.get("resultado") else "")
            for m in messages[-20:]
        ])

    full_prompt = PROMPT + f"\n\nEstado actual:\n{contexto}"
    log(f"Ciclo iniciado. Contexto: {len(contexto)} chars")

    try:
        r = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={"model": "openai/gpt-oss-120b",
                  "messages": [{"role": "user", "content": full_prompt}]},
            timeout=30)
        raw = r.json()["choices"][0]["message"]["content"]
        result = json.loads(clean_json(raw))

        backup_orders()
        ORDERS_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        log(f"Ciclo OK. Diagnóstico: {result.get('diagnostico', '?')}")
        return result
    except Exception as e:
        log(f"ERROR: {e}")
        return {"diagnostico": f"Error: {e}", "orden": [], "alerta": None, "voz": "Hubo un error en el cerebro."}

if __name__ == "__main__":
    r = think()
    sys.stdout.write(json.dumps(r, indent=2, ensure_ascii=False))   
