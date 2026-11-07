import os
import json
from datetime import datetime
from langchain_ollama import ChatOllama

class AgenteEngagement:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:7b",
            temperature=0.7,
            num_ctx=4096,
            num_predict=800,
        )
        self.carpeta = "engagement"
        self.historial_path = "historial_engagement.json"
        os.makedirs(self.carpeta, exist_ok=True)

    def sugerir_respuestas(self, comentario: str, contexto: str = "") -> dict:
        print("Generando sugerencias de respuesta...\n")

        prompt = f"""Eres un experto en engagement para TikTok e Instagram.
Tu estilo es cercano, natural y orientado a generar conversación o leads.

Comentario del usuario:
"{comentario}"

Contexto adicional (opcional):
{contexto if contexto else "Ninguno"}

Genera 3 posibles respuestas:
1. Una respuesta amigable que invite a seguir conversando
2. Una respuesta que haga una pregunta
3. Una respuesta con un llamado a la acción suave (lead o siguiente paso)

Sé breve, natural y evita sonar robótico.
"""

        respuesta = self.llm.invoke(prompt)
        sugerencias = respuesta.content

        resultado = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "comentario": comentario,
            "contexto": contexto,
            "sugerencias": sugerencias
        }

        # Guardar
        nombre = "".join(c if c.isalnum() or c in " _-" else "_" for c in comentario[:30])
        ruta = os.path.join(self.carpeta, f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f"Comentario: {comentario}\n\n{sugerencias}")

        # Historial
        historial = []
        if os.path.exists(self.historial_path):
            try:
                with open(self.historial_path, "r", encoding="utf-8") as f:
                    historial = json.load(f)
            except:
                pass
        historial.append(resultado)
        with open(self.historial_path, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)

        print(f"Guardado en: {ruta}\n")
        print("=" * 60)
        print(sugerencias)
        print("=" * 60)

        return resultado

    def generar_ideas_engagement(self, tema: str) -> str:
        """Genera ideas generales de engagement para un tema."""
        prompt = f"""Genera 5 ideas de engagement para contenido sobre: {tema}

Incluye:
- Preguntas para comentarios
- Ideas de encuestas
- CTAs suaves
- Formas de incentivar respuestas
"""
        respuesta = self.llm.invoke(prompt)
        return respuesta.content

if __name__ == "__main__":
    agente = AgenteEngagement()
    
    # Ejemplo de uso
    agente.sugerir_respuestas(
        comentario="¿Cómo empezaste con esto?",
        contexto="Contenido sobre crecimiento en redes y stream"
    )
