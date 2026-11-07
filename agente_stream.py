import os
from datetime import datetime
from langchain_ollama import ChatOllama

class AgenteStream:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0.7, num_ctx=8192)
        self.carpeta = "stream"
        os.makedirs(self.carpeta, exist_ok=True)

    def generar_ideas(self, tema: str = "stream y crecimiento") -> str:
        prompt = f"""Genera ideas para un stream sobre: {tema}

Incluye:
- 5 títulos llamativos
- Ganchos de apertura
- Ideas de segmentos o dinámicas
- Formas de generar clips durante el directo
- CTAs para leads o comunidad
"""
        respuesta = self.llm.invoke(prompt)
        contenido = respuesta.content

        ruta = os.path.join(self.carpeta, f"stream_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Guardado en: {ruta}")
        return contenido

if __name__ == "__main__":
    print(AgenteStream().generar_ideas())
