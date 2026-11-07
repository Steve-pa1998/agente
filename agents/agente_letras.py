import json, os, requests
from pathlib import Path
from datetime import datetime

def load_env():
    env = {}
    for line in (Path(__file__).parent.parent / ".env").read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

env = load_env()
GROQ_KEY = env.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OUT_DIR = Path(__file__).parent.parent / "musica" / "letras"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def generate(vibra, estilo="rap", bpm=100, num_versos=2, rima="AA BB CC"):
    """Genera letra con métrica y rima."""
    prompt = f"""Eres un letrista de {estilo} mexicano.
Escribe una canción con estas especificaciones:

Vibra/tema: {vibra}
Estilo: {estilo}
BPM: {bpm}
Número de versos: {num_versos}
Esquema de rima: {rima}
Idioma: español (con jerga CDMX si aplica)
Estructura: [Intro] → [Verso 1] → [Coro] → [Verso 2] → [Coro] → [Outro]

Reglas:
- Cada línea debe tener entre 8 y 14 sílabas (métrica consistente)
- Las rimas deben ser CONSONANTES (no asonantes)
- El coro debe ser pegajoso (frase corta que se repite)
- Incluye al menos 1 metáfora original (no cliché)
- No uses: "corazón", "estrella", "luna" (clichés)
- SÍ usa: imágenes concretas, sensoriales, de CDMX

Responde SOLO con la letra, sin explicaciones."""

    r = requests.post(GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_KEY}"},
        json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}]},
        timeout=60)
    letra = r.json()["choices"][0]["message"]["content"].strip()

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    safe = vibra.replace(" ", "_")[:30]
    out_file = OUT_DIR / f"{ts}_{safe}.txt"
    out_file.write_text(f"Vibra: {vibra}\nEstilo: {estilo}\nBPM: {bpm}\nRima: {rima}\n\n{letra}", encoding="utf-8")
    print(f"✅ Letra guardada: {out_file}")
    print(letra)
    return letra

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        generate(" ".join(sys.argv[1:]))
    else:
        print("Uso: python agente_letras.py 'noche, CDMX, soledad, 120bpm'")
        generate("noche, CDMX, soledad, 120bpm")
