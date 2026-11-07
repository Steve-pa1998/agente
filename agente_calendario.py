import os
from datetime import datetime
from langchain_ollama import ChatOllama

class AgenteCalendario:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0.5, num_ctx=8192)
        self.carpeta = "calendario"
        os.makedirs(self.carpeta, exist_ok=True)

    def crear_calendario(self, tema: str, dias: int = 7) -> str:
        prompt = f"""Crea un calendario de contenido de {dias} días para: {tema}

Para cada día incluye:
- Tipo de contenido (Reel, Post, Story, Live)
- Tema / idea
- Objetivo (alcance, engagement, leads)
- Horario sugerido
"""
        respuesta = self.llm.invoke(prompt)
        contenido = respuesta.content

        ruta = os.path.join(self.carpeta, f"calendario_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Guardado en: {ruta}")
        return contenido

if __name__ == "__main__":
    print(AgenteCalendario().crear_calendario("Crecimiento en TikTok e Instagram + leads"))
