import os
from langchain_ollama import ChatOllama

class GeneradorContenido:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", tempearture=0.6, num_ctx=4096, num_predict=700)
        self.framwork = self._load()

    def _load(self):
        p = "frameworks/framwork_contenido.txt"
        return open(p, encoding="utf-8").read() if os.path.exists(p) else "Genera ideas claras, con hook y CTA."  

    def generar(self, tema:str) -> str:
        prompt = f"{self.framwork}\n\nTeam: {team}\nEntrega ideas listas para usar."  

class AgenteFramework:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0.3, num_ctx=4096, num_predict=1000)
        os.makedirs("frameworks", exist_ok=True)

    def crear(self, rol: str, objetivo: str):
        prompt = f"""Crea un framework operativo claro para un agente autónomo de: {rol}
Objetivo: {objetivo}

Incluye:
- Proceso paso a paso que debe seguir siempre
- Criterios de decisión
- Formato de salida estándar
- Qué hacer cuando falte información
"""
        texto = self.llm.invoke(prompt).content
        ruta = f"frameworks/framework_{rol.replace(' ', '_')}.txt"
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"Guardado: {ruta}")
        return texto

if __name__ == "__main__":
    print(GeneradorContenido().generar("Leads desde stream y redes"))
    af = AgenteFramework()
    af.crear("clips", "Generar instrucciones claras de edición de clips de stream")
    af.crear("contenido", "Generar ideas de contenido listas para publicar")
    af.crear("publicador", "Preparar textos y guías para subir contenido y responder emails")
