from llama_index.core import StorageContext, load_index_from_storage

# Cargar el índice que ya construiste
storage_context = StorageContext.from_defaults(
    persist_dir="C:/Users/Steve/Desktop/folder de ollama run llama3/index_storage"
)
rag_index = load_index_from_storage(storage_context)
rag_engine = rag_index.as_query_engine(llm=Ollama(model="llama3"))  
