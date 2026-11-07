import chromadb
from langchain_ollama import ChatOllama

db = chromadb.PersistentClient(path="./mi_db")
coleccion = db.get_or_create_collection("docs")

# Lo que el usuario pregunta
pregunta = "como uso os.path.join"

# Buscar en ChromaDB
resultado = coleccion.query(query_texts=[pregunta], n_results=3)

# Construir contexto
contexto = "\n".join(resultado["documents"][0])

# Pasar al LLM con contexto
llm = ChatOllama(model="llama3")
respuesta = llm.invoke(f"""
Usa SOLO este contexto para responder. No inventes APIs.
Contexto:
{contexto}

Pregunta: {pregunta}
""")

print(respuesta.content)   
