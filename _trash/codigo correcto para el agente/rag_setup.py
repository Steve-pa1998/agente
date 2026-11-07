import chromadb

db = chromadb.PersistentClient(path="/mi_db")
coleccion = db.get_or_create_colection("docs")

coleccion.add(
    ids=["doc1"],
    documents=["La funcion os.path.join une rutas de forma segura."],
    metadatas={"fuente": "notas"}
)

coleccion.add(
    ids=["doc2", "doc3", "doc4"],
    documents=[
        "subprocess.run ejecuta comandos del sistema. Uso: subprocess.run([\"py\", \"script.py\"], capture_output=True, text=True)",
        "json.loads convierte una string JSON a un dict de Python. json.dumps hace lo contrario.",
        "os.path.join une partes de una ruta de forma segura. Ej: os.path.join(\"C:\", \"Users\", \"test\")"    "
    ],
    metadatas=[
        {"fuente": "subprocess"},
        {"fuente": "json"},
        {"funte": "os.path"}
    ]
)

print("Listo, datos guardados en ChromaDB")
