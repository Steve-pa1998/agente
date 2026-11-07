import os
from datetime import datetime
from langchain_ollama import ChatOllama

class GeneradorContenido:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:7b",
            temperature=0.7,
            num_ctx=8192,
        )
        self.carpeta = "contenido"
        os.makedirs(self.carpeta, exist_ok=True)

    def generar(self, tema: str, cantidad: int = 5) -> str:
        print(f"Generando ideas de contenido sobre: {tema}\n")

        prompt = f"""Eres un experto en contenido para TikTok e Instagram.
Genera {cantidad} ideas de posts, reels o stories sobre el siguiente tema.

Tema: {tema}

Para cada idea incluye:
- Tipo (Reel, Post, Story, Carrusel)
- Hook o primera frase
- Descripción breve
- Idea de engagement (pregunta, encuesta o llamado a la acción)
- Hashtags sugeridos

Sé creativo y enfocado en generar engagement y leads.
"""

        respuesta = self.llm.invoke(prompt)
        contenido = respuesta.content

        # Guardar
        nombre = "".join(c if c.isalnum() or c in " _-" else "_" for c in tema[:40])
        ruta = os.path.join(self.carpeta, f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)

        print(f"Ideas guardadas en: {ruta}\n")
        return contenido

if __name__ == "__main__":
    gen = GeneradorContenido()
    resultado = gen.generar("Crecimiento en TikTok e Instagram para generar leads")
    print("=" * 60)
    print(resultado)
    print("=" * 60)




