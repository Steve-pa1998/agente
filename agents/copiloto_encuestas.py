"""
copiloto_encuestas.py
Copia la pregunta de la encuesta, pégala aquí, te sugiere respuesta.
Uso: python agents/copiloto_encuestas.py
"""
import os
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(BASE / ".env")

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

PERFIL = """
PERFIL DE RESPONDENTE (sé consistente SIEMPRE con esto):
- Nombre: Steve
- Edad: 28
- Género: Hombre
- Ubicación: Ciudad de México, México
- Ocupación: Freelancer / Desarrollador
- Ingresos: $15,000-$25,000 MXN/mes
- Educación: Técnico en programación (no universitario)
- Dispositivos: Laptop Windows + iPhone 13
- Redes sociales: Instagram, YouTube, LinkedIn
- Intereses: Tecnología, IA, automatización, marketing digital
- Compra: En línea (Amazon, Mercado Libre), comida delivery (Rappi, Uber Eats)
- Streaming: YouTube, Spotify
- Carro: No
- Casa: Renta, departamento 2 recámaras
- Mascotas: No
- Viajes: 1 vez al año, nacional
- Idiomas: Español (nativo), Inglés (básico)
- Hábitos: Despierta 8am, duerme 1am, trabaja de forma remota
- Compras recientes: Suscripción a un servicio de IA, laptop
- No fuma, no bebe regularmente
- Política: No opina / evita el tema
"""

SYSTEM = f"""Eres un asistente que ayuda a responder encuestas.
El usuario te pega una pregunta (o varias) de una encuesta.
Tú respondes CORTO (1-3 palabras o una frase) como lo haría una persona real.

REGLAS:
- Sé consistente con el perfil.
- Responde como lo haría una persona normal, no como un bot.
- Si es de opción múltiple, dice UNA opción.
- Si es escala 1-5 o 1-10, da UN número.
- Si es texto libre, máximo 20 palabras.
- Si la pregunta es "¿cuál de las siguientes?", elige una.
- Responde SOLO con la respuesta, sin explicación.
- Si la pregunta está en inglés, responde en inglés.
- Si está en español, responde en español.
"""


def main():
    print("=" * 50)
    print("🎯 Copiloto de Encuestas")
    print("   Pega la pregunta → Enter → te doy la respuesta")
    print("   Escribe 'salir' para terminar")
    print("=" * 50)

    while True:
        print()
        try:
            pregunta = input("❓ Pregunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not pregunta:
            continue
        if pregunta.lower() in ("salir", "quit", "exit", "q"):
            print("👋 Adios.")
            break

        try:
            resp = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": pregunta},
                ],
                temperature=0.8,
                max_tokens=50,
            )
            respuesta = resp.choices[0].message.content.strip()
            print(f"\n✅ Respuesta: {respuesta}\n")
        except Exception as e:
            print(f"⚠️  Error: {e}")


if __name__ == "__main__":
    main()   
