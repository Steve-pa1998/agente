import os, json, shutil
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
CONTEXT = BASE / "context"
NOTAS = CONTEXT / "Notas"

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def get_mes_folder():
    """Devuelve la carpeta del mes actual (la crea si no existe)."""
    hoy = datetime.now()
    mes_nombre = MESES[hoy.month]
    folder = NOTAS / mes_nombre
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def get_chat_del_dia():
    """Busca el chat más reciente de HOY en context/."""
    hoy = datetime.now().strftime("%Y%m%d")
    chats = sorted(CONTEXT.glob(f"chat_{hoy}_*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
    # Filtrar los vacíos
    chats = [c for c in chats if c.stat().st_size > 0]
    if chats:
        return chats[0]
    return None

def get_resume():
    """Devuelve el contenido del RESUME.md."""
    resume = CONTEXT / "RESUME.md"
    if resume.exists() and resume.stat().st_size > 0:
        return resume.read_text(encoding="utf-8")
    return ""

def get_estado_sistema():
    """Checa qué está corriendo."""
    estado = {}

    # Procesos Python
    import subprocess
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe"], capture_output=True, text=True)
        estado["python_procesos"] = "Sí" if "python.exe" in r.stdout else "No"
    except:
        estado["python_procesos"] = "?"

    # Task Scheduler
    try:
        r = subprocess.run(["powershell", "-Command",
            "Get-ScheduledTask -TaskName 'AgenteCoordinador','AgenteEmail' -ErrorAction SilentlyContinue | Select-Object TaskName,State | Format-Table -AutoSize | Out-String"],
            capture_output=True, text=True, timeout=10)
        estado["scheduler"] = r.stdout.strip() if r.stdout.strip() else "No encontrados"
    except:
        estado["scheduler"] = "?"

    # Último log del coordinador
    coord_log = BASE / "coordinador_log.txt"
    if coord_log.exists():
        lines = coord_log.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
        estado["ultimo_coordinador"] = lines[-1] if lines else "vacío"
    else:
        estado["ultimo_coordinador"] = "no existe"

    return estado

def guardar_resumen_dia():
    """Guarda el resumen del día en context/Notas/[Mes]/."""
    hoy = datetime.now()
    mes_folder = get_mes_folder()
    fecha_str = hoy.strftime("%d_%m_%Y")
    out_file = mes_folder / f"resumen_{fecha_str}.md"

    # Juntar todo
    contenido = f"# Resumen del día — {hoy.strftime('%d/%m/%Y %H:%M')}\n\n"

    # Estado del sistema
    estado = get_estado_sistema()
    contenido += "## Estado del sistema\n"
    contenido += f"- Python corriendo: {estado.get('python_procesos', '?')}\n"
    contenido += f"- Último coordinador: {estado.get('ultimo_coordinador', '?')}\n\n"

    # RESUME (primeras 20 líneas como contexto)
    resume = get_resume()
    if resume:
        contenido += "## RESUME (actual)\n"
        contenido += "```\n"
        contenido += "\n".join(resume.splitlines()[:30])
        contenido += "\n```\n\n"

    # Chat del día (si existe)
    chat = get_chat_del_dia()
    if chat:
        contenido += f"## Chat del día ({chat.name})\n"
        chat_text = chat.read_text(encoding="utf-8", errors="ignore")
        # Si es muy largo, solo primeras 100 líneas
        lines = chat_text.splitlines()
        if len(lines) > 100:
            contenido += "\n".join(lines[:100])
            contenido += f"\n\n... ({len(lines) - 100} líneas más en {chat.name})"
        else:
            contenido += chat_text
        contenido += "\n"

    # Guardar
    out_file.write_text(contenido, encoding="utf-8")
    print(f"✅ Resumen guardado: {out_file}")
    print(f"   Mes: {MESES[hoy.month]}")
    print(f"   Tamaño: {out_file.stat().st_size // 1024} KB")

if __name__ == "__main__":
    guardar_resumen_dia()
