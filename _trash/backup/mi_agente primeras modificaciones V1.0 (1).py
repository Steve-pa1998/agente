from langchain_ollama import ChatOllama
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
import os

llm = ChatOllama(model="qwen2.5:7b", temperature=0)

@tool
def read_file(path: str) -> str:
    """Lee el contenido de un archivo."""
    with open(path, 'r') as f:
        return f.read()

@tool
def write_file(path: str, content: str) -> str:
    """Escribe contenido en un archivo."""
    with open(path, 'w') as f:
        f.write(content)
    return f"Escribi en {path}"

@tool
def list_files(directory: str = ".") -> str:
    """Lista los archivos en un directorio."""
    return "\n".join(os.listdir(directory))

agent = create_react_agent(
    llm,
    [read_file, write_file, list_files],
    prompt="Eres un pair programmer conciso. Planifica en pasos, luego escribe codigo archivo por archivo."
ARCHIVOS EXISTENTES EN LA CARPETA:
{existing}
Si quieres crear un archivo, asegurate de que no exista. Si quieres modificar un archivo, asegurate de que exista.""""""    
)

result = agent.invoke({
    "messages": [("user", "Crea un script que calcule el factorial de un numero con recursion y guardalo en factorial.py")]
})factorial.py
print(result["messages"][-1].content)   
