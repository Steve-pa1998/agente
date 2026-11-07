import os
from langchain_ollama import ChatOllama

class GeneradorContenido:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0.6, num_ctx=4096, num_predict=800)
        ruta = "framework/framework_contenido.txt"
        self.framework = open(ruta, encoding="utf-8").read() if os.path.exists(rura) else "Genera ideas de contenido con hook, descripción y CTA." 
        self.framework = self._cargar()

    def _cargar(self):
        ruta = "frameworks/framework_contenido.txt"
        return open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else "Genera ideas claras y accionables."

    def generar(self, tema: str) -> str:
        prompt = f"{self.framework}\n\nTema: {tema}\nGenera el contenido siguiendo el framework."
        prompt = f"{self.framework}\n\nTema: {tema}\nGenerar ideas listas para publicar."
        return self.llm.invoke(prompt).content

if __name__ == "__main__":
    print(GeneradorContenido().generar("Crecimiento y leads en redes"))



