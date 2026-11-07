import os
import subprocess
import sys
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

# =================================================
# CONFIG
# =================================================

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0.2,
    num_ctx=8192,
    num_predict=4096,
    keep_alive="30m"
)

# =================================================
# TOOLS
# =================================================

def read_file(path: str) -> str:
    """Lee el contenido de un archivo. Recibe la ruta del archivo."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: '{path}' no existe."
    except PermissionError:
        return f"Error: Sin permiso para leer '{path}'."

def write_file(path: str, content: str) -> str:
    """Escribe contenido en un archivo (sobrescribe si existe). Recibe ruta y contenido."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Escrito: {path} ({len(content)} chars)"
    except Exception as e:
        return f"❌ Error escribiendo '{path}': {e}"

def list_files(directory: str = ".") -> str:
    """Lista los archivos y carpetas en un directorio. Recibe la ruta (default: '.')."""
    try:
        entries = os.listdir(directory)
        resultado = []
        for e in sorted(entries):
            full = os.path.join(directory, e)
            tipo = "📁" if os.path.isdir(full) else "📄"
            resultado.append(f"{tipo} {e}")
        return "\n".join(resultado) if resultado else "(vacío)"
    except Exception as e:
        return f"❌ Error: {e}"

def run_code(path: str) -> str:
    """
    Ejecuta un archivo Python y devuelve el output (stdout + stderr).
    Recibe la ruta del archivo .py a ejecutar.
    Úsalo para PROBAR el código que acabas de escribir.
    """
    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        if result.returncode == 0:
            return f"✅ Exit code 0\n{output}"
        else:
            return f"❌ Exit code {result.returncode}\n{output}"
    except subprocess.TimeoutExpired:
        return "❌ Timeout: el código tardó más de 30 segundos."
    except Exception as e:
        return f"❌ Error ejecutando: {e}"

def rag_query(question: str) -> str:
    """
    Busca información en tus documentos indexados (RAG/ChromaDB).
    Úsalo cuando necesites contexto de tus apuntes o documentos.
    Recibe la pregunta en texto natural.
    """
    try:
        from rag import query_engine
        return str(query_engine.query(question))
    except ImportError:
        return "❌ No se pudo importar rag.py. Asegúrate de que esté en la misma carpeta."
    except Exception as e:
        return f"❌ Error en RAG: {e}"

# =================================================
# PROMPT
# =================================================

def get_existing_files() -> str:
    """Obtiene la lista de archivos actuales para inyectar en el prompt."""
    try:
        entries = sorted(os.listdir("."))
        return "\n".join(f" - {e}" for e in entries)
    except:
        return " (no se pudo listar)"

SYSTEM_PROMPT = """Eres un agente especializado en crear otros agentes de Python.
Recibes una ESPECIFICACIÓN APROBADA por el usuario y la conviertes en código funcional.

REGLAS:
1. Solo escribes código cuando recibes una especificación clara y aprobada.
2. Antes de modificar un archivo existente, LÉELO primero con read_file.
3. Después de escribir un archivo .py, EJECÚTALO con run_code para verificar que no tenga errores.
4. Si run_code devuelve error, corrígelo y vuelve a ejecutar.
5. Usa rag_query solo si la especificación lo requiere o necesitas contexto técnico.
6. Sé conciso. Entrega el código y un resumen corto de lo que creaste.
7. Crea agentes que sean modulares y fáciles de integrar después.

ESPECIFICACIÓN APROBADA:
{spec}

ARCHIVOS ACTUALES EN LA CARPETA:
{files}"""

# =================================================
# AGENTE
# =================================================

def crear_agente(spec: str = "Ninguna especificación proporcionada aún."):
    """Crea el agente con la especificación aprobada y la lista de archivos actualizada."""
    prompt = SYSTEM_PROMPT.format(
        spec=spec,
        files=get_existing_files()
    )
    return create_react_agent(
        llm,
        [read_file, write_file, list_files, run_code, rag_query],
        prompt=prompt
    )

# =================================================
# LOOP INTERACTIVO
# =================================================

if __name__ == "__main__":
    print("🤖 Agente Creador de Agentes (qwen2.5-7b + Ollama)")
    print("   Herramientas: read_file, write_file, list_files, run_code, rag_query")
    print("   Escribe 'salir' para terminar.\n")

    while True:
        tarea = input("📝 Tarea: ").strip()
        if tarea.lower() in ("salir", "quit", "q"):
            print("👋 Adiós.")
            break
        if not tarea:
            continue

        print("\nPega la especificación aprobada (o escribe 'usar anterior' si ya la tienes):")
        spec = input("Especificación: ").strip()
        if not spec or spec.lower() == "usar anterior":
            spec = "Continuar con la tarea anterior o crear según lo pedido."

        # Se re-crea el agente en cada tarea con la especificación y archivos actualizados
        agent = crear_agente(spec=spec)

        try:
            resultado = agent.invoke(
                {"messages": [("user", tarea)]}
            )
            # Imprimir el último mensaje del agente
            last_msg = resultado["messages"][-1]
            print(f"\n{'=' * 50}")
            print(f"AGENTE: {last_msg.content}")
            print("=" * 50)
        except Exception as e:
            print(f"\n❌ Error: {e}")

        print()  # línea en blanco entre tareas
