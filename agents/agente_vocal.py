import json, os, random
from pathlib import Path
from datetime import datetime, timedelta

OUT_DIR = Path(__file__).parent.parent / "musica" / "vocal"
OUT_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = OUT_DIR / "progreso.json"

# Ejercicios por nivel
EJERCICIOS = {
    "calentamiento": [
        "Lip trills (brrrr) de Do4 a Sol4 y de vuelta — 3 repeticiones",
        "Escala mayor de Do: Do-Re-Mi-Fa-Sol-La-Si-Do — 2 octavas, 5 repeticiones",
        "Vibrato: nota sostenida (La4) 4 seg con vibrato, 10 repeticiones",
        "Descenso: Do5 → Do4 (nota larga bajando), 5 repeticiones",
        "Humming: Mmm en Do4, Re4, Mi4, Fa4, Sol4 — 3 repeticiones",
    ],
    "rango": [
        "Salto de 5ta: Do4 → Sol4, Re4 → La4, Mi4 → Si4 — 10 repeticiones",
        "Glissando: Do4 → Do5 (subiendo) → Do4 (bajando) — 5 repeticiones",
        "Nota aguda sostenida: Si4 por 3 seg — 10 repeticiones (no forzar)",
        "Nota grave sostenida: Do3 por 3 seg — 10 repeticiones",
        "Escala cromática: Do4 → Do#4 → Re4 → ... → Do5 — 3 repeticiones",
    ],
    "pitch": [
        "Cantar una nota y mantenerla 5 seg sin moverse (La4) — 10 repeticiones",
        "Imitar: toca un tono en el piano/phone y cántalo — 20 repeticiones",
        "Intervalo de 3ra: Do4-Mi4, Re4-Fa4, Mi4-Sol4 — 10 repeticiones cada uno",
        "Descanso-pitch: canta Do4, para 2 seg, canta Do4 otra vez (mismo tono) — 10 repeticiones",
        "Semitono: Do4 → Do#4 → Do4 (muy lento) — 15 repeticiones",
    ],
    "respiracion": [
        "Respiración diafragmática: inhala 4 seg, sostén 4 seg, exhala 8 seg — 10 repeticiones",
        "Sostén una nota (La4) mientras exhalas: objetivo 10 seg — 5 repeticiones",
        "Frase larga: canta 'ma-ma-ma-ma-ma-ma-ma-ma' en una sola respiración — 10 repeticiones",
        "Exhalación con fricción: 'sss' por 15 seg sin tomar aire — 5 repeticiones",
    ],
}

def get_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"dias": 0, "ultimo": None, "nivel": "calentamiento", "historial": []}

def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))

def daily_exercise():
    state = get_state()
    hoy = datetime.now().strftime("%Y-%m-%d")

    if state.get("ultimo") == hoy:
        print("Ya hiciste tu ejercicio hoy.")
        return

    state["dias"] += 1
    state["ultimo"] = hoy

    # Subir de nivel cada 7 días
    if state["dias"] % 7 == 0 and state["nivel"] != "respiracion":
        niveles = ["calentamiento", "rango", "pitch", "respiracion"]
        idx = niveles.index(state["nivel"])
        if idx + 1 < len(niveles):
            state["nivel"] = niveles[idx + 1]
            print(f"📈 Subiste a nivel: {state['nivel']}")

    ejercicios = EJERCICIOS[state["nivel"]]
    seleccion = random.sample(ejercicios, min(3, len(ejercicios)))

    print(f"\n{'='*50}")
    print(f"🎤 EJERCICIO DEL DÍA — Día {state['dias']} — Nivel: {state['nivel']}")
    print(f"{'='*50}\n")
    for i, e in enumerate(seleccion, 1):
        print(f"  {i}. {e}")
    print(f"\n⏱️  Tiempo estimado: 10-15 min")
    print(f"📝 Regla: hazlo ANTES de grabar. No saltes el calentamiento.")

    state["historial"].append({"fecha": hoy, "nivel": state["nivel"], "ejercicios": seleccion})
    state["historial"] = state["historial"][-30:]
    save_state(state)

if __name__ == "__main__":
    daily_exercise()
