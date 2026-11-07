#!/usr/bin/env python3
"""
rebanada.py - Rebanada de contexto que se actualiza al cerrar sesion.
Uso:
  python rebanada.py chat <user_id>
  python rebanada.py ver <user_id>
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from groq import Groq

# --- CONFIG ---
REBANADA_DIR = Path("./rebanadas")
MODEL = "openai/gpt-oss-120b"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- REBANADA ---

def load_rebanada(user_id: str) -> str:
    path = REBANADA_DIR / f"{user_id}.txt"
    if path.exists():
        return path.read_text()
    return ""

def save_rebanada(user_id: str, texto: str):
    REBANADA_DIR.mkdir(exist_ok=True)
    path = REBANADA_DIR / f"{user_id}.txt"
    path.write_text(texto)
    print(f"Rebanada guardada: {path} ({len(texto.split())} palabras)")

def rebanada_to_context(rebanada: str) -> str:
    if not rebanada:
        return "Primera conversacion con este usuario. Observa y adapatate."
    return f"Contexto de la conversacion previa (rebanada):\n{rebanada}\n\nContinua de donde quedo. No saludes de nuevo, no resumas, solo sigue el hilo."

# --- ACTUALIZAR REBANADA ---

def update_rebanada(user_id: str, transcript: list):
    existing = load_rebanada(user_id)
    transcript_str = "\n".join(
        f"{m['role']}: {m['content']}" for m in transcript[-30:]
    )

    prompt = f"""Eres un editor de contexto. Tu trabajo: generar la "rebanada" - un texto corto (max 200 palabras) que capture lo esencial de esta conversacion para que la siguiente continue sin cortes.

NO es un perfil. NO es un resumen formal. Es como si le dijeras a un amigo: "o sea, estaba platicando con fulano sobre esto, quedo asi, y lo siguiente es..."

Si ya hay una rebanada previa, integrala: lo que siga relevante, lo que ya no, sueltalo.

Rebanada previa:
{existing if existing else "(no hay, es la primera vez)"}

Conversacion de esta sesion:
{transcript_str}

Escribe solo la nueva rebanada, sin etiquetas, sin formato, texto plano."""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    nueva_rebanada = resp.choices[0].message.content.strip()
    save_rebanada(user_id, nueva_rebanada)
    print(f"\n--- Nueva rebanada ---\n{nueva_rebanada}\n---")

# --- CHAT ---

def chat(user_id: str):
    rebanada = load_rebanada(user_id)
    context = rebanada_to_context(rebanada)

    print(f"--- Sesion: {user_id} ---")
    if rebanada:
        print(f"Rebanada activa ({len(rebanada.split())} palabras).")
    else:
        print("Primera vez. Sin rebanada.")
    print("Escribe 'salir' para terminar.\n")

    messages = [{"role": "system", "content": context}]

    while True:
        try:
            user_msg = input("Tu: ")
        except (EOFError, KeyboardInterrupt):
            break

        if user_msg.lower() in ("salir", "exit", "q"):
            break

        messages.append({"role": "user", "content": user_msg})

        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        reply = resp.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print(f"Bot: {reply}\n")

    if len(messages) > 2:
        update_rebanada(user_id, messages)

# --- CLI ---

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    user_id = sys.argv[2]

    if cmd == "chat":
        chat(user_id)
    elif cmd == "ver":
        r = load_rebanada(user_id)
        print(r if r else "(sin rebanada)")
    else:
        print(f"Comando desconocido: {cmd}")