import os
from datetime import datetime
from langchain_ollama import ChatOllama

class AgentePublicador:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0.5, num_ctx=4096, num_predict=1024)
        self.carpeta = "publicaciones"
        os.makedirs(self.carpeta, exist_ok=True)

    def responder_email(self, email: str) -> str:
        prompt = f"""Redacta una respuesta profesional y cercana a este email:

{email}

Mantén un tono natural y útil.
"""
        return self.llm.invoke(prompt).content

    def guia_subida(self, plataforma: str, descripcion_clip: str) -> str:
        prompt = f"""Dame una guía rápida para subir un clip a {plataforma}.

Descripción del clip:
{descripcion_clip}

Incluye:
- Título sugerido
- Descripción
- Hashtags
- Mejores prácticas de subida para esa plataforma
"""
        respuesta = self.llm.invoke(prompt)
        contenido = respuesta.content

        ruta = os.path.join(self.carpeta, f"{plataforma}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Guardado en: {ruta}")
        return contenido

if __name__ == "__main__":
    pub = AgentePublicador()
    print(pub.guia_subida("TikTok", "Clip de reacción graciosa en stream"))
