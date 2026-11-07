import chromadb
from chromadb.utils import embedding_functions
from langchain_ollama import ChatOllama
import subprocess
import re

# --- Configuración ---
ef = embedding_functions.OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434"
)

db = chromadb.PersistentClient(path="./mi_db")
coleccion = db.get_or_create_collection("docs", embedding_function=ef)

llm = ChatOllama(model="llama3")

# --- Funciones ---

def buscar_contexto(pregunta: str) -> str:
    resultado = coleccion.query(query_texts=[pregunta], n_results=3)
    return "\n".join(resultado["documents"][0])

def ejecutar_codigo(codigo: str) -> str:
    resultado = subprocess.run(
        ["py", "-c", codigo],
        capture_output=True, text=True, timeout=30
    )
    if resultado.returncode == 0:
        return resultado.stdout
    return f"ERROR: {resultado.stderr}"

def extraer_codigo(texto: str) -> str:
    patron = r"```python\n(.*?)```"
    match = re.search(patron, texto, re.DOTALL)
    if match:
        return match.group(1)
    return texto

def agente(pregunta: str) -> str:
    # 1. Buscar contexto en RAG
    contexto = buscar_contexto(pregunta)

    # 2. Pedir código al LLM con contexto
    prompt = f"""Eres un programador Python experto.
    REGLAS:
    - Escribe UNA función (def), no un script completo.
    - No uses subprocess, os.system, ni archivos externos.
    - No inventes APIs, URLs ni librerías que no sean del estánder de Python.
    - Si la tarea no es posible, responde solo: "no puedo hacer eso"
    - Escribe el código DENTRO de ```python ... ```

Contexto de referencia:
{contexto}

Tarea: {pregunta}

Responde SOLO el código, sin explicaciones.
"""
    respuesta = llm.invoke(prompt)
    codigo = extraer_codigo(respuesta.content)

    # 3. Ejecutar y corregir (máx 3 intentos)
    for intento in range(3):
        resultado = ejecutar_codigo(codigo)
        if "ERROR" not in resultado:
            return f"Código:\n{codigo}\n\nSalida:\n{resultado}"
        prompt_fix = f"""..."""
        respuesta = llm.invoke(prompt_fix)
        codigo = extraer_codigo(respuesta.content)
        # 4. Pedir corrección
        # ← SOLO el prompt_fix NUEVO 
    prompt_fix = f"""El código dio este error:
{resultado}

Código anterior:
{codigo}

Arregla SOLO el error. Mantiene la misma estructura (una función, sin subprocess).
Responde SOLO el código corregido en ```python ... ```
"""   
    respuesta = llm.invoke(prompt_fix)
    codigo = extraer_codigo(respuesta.content)

    return f"No pude resolverlo en 3 intentos.\nÚltimo código:\n{codigo}\nÚltimo error:\n{resultado}"

