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
index.storage_context.persist("C:/Users/Steve/Desktop/folder de ollama run llama3/index_storage")   

chat = index.as_chat_engine(llm=llm, chat_mode="condense_question")

while True:
    q = input("\nPregunta: ")
    if q.lower() in ("salir", "quit", "q"):
        break
    print(chat.chat(q))   
