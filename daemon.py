import time
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\Steve\Desktop\agente")
LOG_FILE = ROOT / "daemon_log.txt"
ROADMAP = ROOT / "roadmap.json"

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_roadmap():
    if ROADMAP.exists():
        return json.loads(ROADMAP.read_text(encoding="utf-8"))
    return {"tareas": []}

def save_roadmap(data):
    ROADMAP.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def next_task(data):
    """Devuelve la siguiente tarea pendiente (por prioridad)."""
    pendientes = [t for t in data["tareas"] if t["estado"] == "pendiente"]
    if not pendientes:
        return None
    pendientes.sort(key=lambda x: x["prioridad"])
    return pendientes[0]

def execute_task(task):
    """Ejecuta el comando de la tarea."""
    log(f"[TAREA {task['id']}] {task['tarea']}")
    try:
        r = subprocess.run(
            task["comando"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=3600,
            cwd=str(ROOT)
        )
        output = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            log(f"[TAREA {task['id']}] OK: {output[:200]}")
            return True, output
        else:
            log(f"[TAREA {task['id']}] FAIL: {output[:200]}")
            return False, output
    except subprocess.TimeoutExpired:
        log(f"[TAREA {task['id']}] TIMEOUT")
        return False, "timeout"
    except Exception as e:
        log(f"[TAREA {task['id']}] ERROR: {e}")
        return False, str(e)

def main():
    log("=== DAEMON v2 INICIADO (modo roadmap) ===")
    log(f"PID: {os.getpid()}")

    while True:
        data = load_roadmap()
        task = next_task(data)

        if task is None:
            log("Roadmap completado. Dormindo 1h...")
            time.sleep(3600)
            continue

        ok, output = execute_task(task)

        # Marcar estado
        for t in data["tareas"]:
            if t["id"] == task["id"]:
                t["estado"] = "completado" if ok else "error"
                t["fecha"] = datetime.now().isoformat()
                t["output"] = output[:500]
                break
        save_roadmap(data)

        pendientes = sum(1 for t in data["tareas"] if t["estado"] == "pendiente")
        log(f"Quedan {pendientes} tareas. Pausa 5 min...")
        time.sleep(300)

if __name__ == "__main__":
    main()
