import os
import json
from datetime import datetime
from langchain_ollama import ChatOllama

class Investigador:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:7b",
            temperature=0.3,
            num_ctx=4096,
            num_predict=1024,
        )
        self.historial_path = "historial_investigaciones.json"
        self.carpeta_investigaciones = "investigaciones"
        os.makedirs(self.carpeta_investigaciones, exist_ok=True)

    def investigar(self, pregunta: str, usar_rag: bool = False) -> dict:
        print(f"Investigando sobre: {pregunta}\n")

        contexto_rag = ""
        if usar_rag:
            try:
                from rag import query_engine
                contexto_rag = str(query_engine.query(pregunta))
                print("Contexto RAG obtenido.\n")
            except Exception as e:
                contexto_rag = f"(No se pudo usar RAG: {e})"

        prompt = f"""Eres un agente de investigación preciso y claro.
Analiza la pregunta y responde de forma estructurada.

Pregunta: {pregunta}

{"Contexto adicional (RAG):\n" + contexto_rag if contexto_rag else ""}

Responde en este formato:
- Resumen corto
- Puntos clave
- Conclusión o recomendación
"""

        respuesta = self.llm.invoke(prompt)
        contenido = respuesta.content

        # Resultado estructurado
        resultado = {
            "pregunta": pregunta,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "respuesta": contenido,
            "uso_rag": usar_rag
        }

        # 1. Guardar en archivo individual
        nombre_archivo = "".join(c if c.isalnum() or c in " _-" else "_" for c in pregunta[:50])
        ruta_individual = os.path.join(self.carpeta_investigaciones, f"{nombre_archivo}.txt")
        with open(ruta_individual, "w", encoding="utf-8") as f:
            f.write(f"Pregunta: {pregunta}\n")
            f.write(f"Fecha: {resultado['fecha']}\n\n")
            f.write(contenido)

        # 2. Agregar al historial JSON
        historial = []
        if os.path.exists(self.historial_path):
            with open(self.historial_path, "r", encoding="utf-8") as f:
                try:
                    historial = json.load(f)
                except:
                    historial = []
        historial.append(resultado)
        with open(self.historial_path, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)

        print(f"Guardado en: {ruta_individual}")
        print(f"Agregado al historial: {self.historial_path}\n")

        return resultado

# Prueba
if __name__ == "__main__":
    agente = Investigador()
    resultado = agente.investigar(
        "¿Cómo funcionan los algoritmos de recomendación en TikTok?",
        usar_rag=False   # cambia a True si quieres probar RAG
    )
    print("="*60)
    print(resultado["respuesta"])
    print("="*60)
