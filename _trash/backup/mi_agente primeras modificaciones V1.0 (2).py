from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

llm = Ollama(model="llama3")
embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# Carga TODO lo que haya en tu carpeta
docs = SimpleDirectoryReader(
    "C:/Users/Steve/Desktop/folder de ollama run llama3"
).load_data()

index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
query_engine = index.as_query_engine(llm=llm)

print# ✅ Solo se ejecuta si lo corres directo (python rag.py)
if __name__ == "__main__":
    query_engine.query("¿Qué es un agente de IA?")   
