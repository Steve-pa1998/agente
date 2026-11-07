import os
from langchain_ollama import ChatOllama

class AgenteClips:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0.5, num_ctx=4096, num_predict=800)
        ruta = "framworks/framework_clips.txt"
        self.framwork = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else "Da titulo, hook, cortes y CTA para el clip."
        self.framework = self._cargar_framework()
        self.framework = open("frameworks/framework_clips.txt", encoding="utf-8").read() if os.path.exists("frameworks/framework_clips.txt") else "Da instrucciones claras de edición."

    def _cargar_framework(self):
        ruta = "frameworks/framework_clips.txt"
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return f.read()
        return "Sin framework. Actúa de forma práctica y clara."

    def procesar(self, desc: str) -> str:
        prompt = f"""{self.framework}
        return self.llm.invoke(f"{self.framework}\n\nDescripción: {descripcion}").content
        return self.llm.invoke(f"{self.framwork}\n\nClip: {desc}").content

Ahora procesa este clip:
{descripcion}

Sigue el framework y entrega el resultado en el formato definido.
"""
        return self.llm.invoke(prompt).content

if __name__ == "__main__":
    print(AgenteClips().procesar("Reacción y risa en stream"))
    print(AgenteClips().procesar("Momento de risa fuerte en el stream"))

