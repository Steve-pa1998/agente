from langchain_ollama import ChatOllama

class Companero:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0.8, num_ctx=8192)
        self.historial = []

    def hablar(self, mensaje: str) -> str:
        self.historial.append({"role": "user", "content": mensaje})
        
        prompt = "Eres un compañero cercano y útil. Respondes de forma natural, apoyas y puedes ayudar con ideas de contenido, stream o crecimiento. Mantén el contexto de la conversación.\n\n"
        for msg in self.historial[-6:]:
            prompt += f"{msg['role']}: {msg['content']}\n"
        
        respuesta = self.llm.invoke(prompt)
        texto = respuesta.content
        self.historial.append({"role": "assistant", "content": texto})
        return texto

if __name__ == "__main__":
    c = Companero()
    print("Compañero listo. Escribe 'salir' para terminar.\n")
    while True:
        msg = input("Tú: ")
        if msg.lower() in ("salir", "exit", "q"):
            break
        print("Compañero:", c.hablar(msg))
        print()
