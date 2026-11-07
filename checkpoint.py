import os
from datetime import datetime

CONTEXT_DIR = os.path.join(os.path.dirname(__file__), "context")
os.makedirs(CONTEXT_DIR, exist_ok=True)

def save_checkpoint(full_text: str, summary: str = ""):
    """Guarda el chat completo + genera RESUME.md para pegar en chat nuevo."""
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 1. Chat completo (backup)
    full_path = os.path.join(CONTEXT_DIR, f"chat_{ts}.md")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    # 2. RESUME.md (lo que pegas en el chat nuevo)
    resume_path = os.path.join(CONTEXT_DIR, "RESUME.md")
    with open(resume_path, "w", encoding="utf-8") as f:
        f.write(f"# Contexto para continuar\n")
        f.write(f"Guardado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        if summary:
            f.write(f"## Resumen\n{summary}\n\n")
        f.write(f"## Chat completo\n\n{full_text}\n")
    
    print(f"✅ Chat guardado: {full_path}")
    print(f"✅ Resume listo: {resume_path}")
    print(f"\nPega el contenido de RESUME.md en el chat nuevo.")

# --- USO ---
if __name__ == "__main__":
    # Opción A: pegar texto desde archivo
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            save_checkpoint(f.read())
    else:
        print("Pega el chat completo y presiona Ctrl+Z (Windows) + Enter:")
        text = sys.stdin.read()
        save_checkpoint(text)   
