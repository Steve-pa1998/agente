import os
from datetime import datetime
from langchain_ollama import ChatOllama

class AgenteMarca:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0.7, num_ctx=4096, num_predict=1200)
        self.carpeta = "marca"
        os.makedirs(self.carpeta, exist_ok=True)

    def desarrollar_marca(self, descripcion: str) -> str:
        prompt = f"""Ayúdame a construir una marca personal / imagen.

Descripción de lo que hago o quiero transmitir:
{descripcion}

Incluye:
- Posicionamiento (cómo quiero ser percibido)
- Tono de voz
- Valores o personalidad de marca
- Ideas de contenido que refuercen la marca
- Posibles colores / estilo visual
- Frases o eslóganes
- Cómo diferenciarme
"""
        respuesta = self.llm.invoke(prompt)
        contenido = respuesta.content

        ruta = os.path.join(self.carpeta, f"marca_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Guardado en: {ruta}")
        return contenido

if __name__ == "__main__":
    print(AgenteMarca().desarrollar_marca("Streamer que crea contenido de crecimiento, leads y comunidad"))
