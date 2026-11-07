# agente_encuestas.py
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import time
import subprocess
from datetime import datetime

BASE = r"C:\Users\Steve\Desktop\agente"
LOG_FILE = os.path.join(BASE, "docs", "encuestas_log.json")

def log_encuesta(plataforma, nombre, puntos):
    """Registra una encuesta completada."""
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log = json.load(f)
    
    log.append({
        "fecha": datetime.now().isoformat(),
        "plataforma": plataforma,
        "encuesta": nombre,
        "puntos": puntos
    })
    
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    
    total = sum(e["puntos"] for e in log)
    print(f"[OK] {plataforma}: {nombre} (+{puntos} pts) | Total: {total} pts")

def abrir_encuestas():
    """Abre los dashboards de encuestas."""
    subprocess.Popen("start https://www.ysense.com/es/mx/encuestas")
    subprocess.Popen("start https://www.toluna.com/es-mx/surveys")
    print("[OK] Dashboards abiertos")

def resumen():
    """Muestra resumen de encuestas hechas."""
    if not os.path.exists(LOG_FILE):
        print("Sin encuestas registradas aún.")
        return
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)
    
    por_plataforma = {}
    for e in log:
        p = e["plataforma"]
        por_plataforma[p] = por_plataforma.get(p, 0) + e["puntos"]
    
    print(f"\n{'='*40}")
    print(f"  RESUMEN ENCUESTAS")
    print(f"{'='*40}")
    for plat, pts in por_plataforma.items():
        print(f"  {plat}: {pts} pts")
    print(f"  TOTAL: {sum(por_plataforma.values())} pts")
    print(f"{'='*40}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "abrir":
            abrir_encuestas()
        elif cmd == "log":
            # python agente_encuestas.py log YSense "Encuesta X" 50
            log_encuesta(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        elif cmd == "resumen":
            resumen()
        else:
            print("Uso: agente_encuestas.py [abrir|log|resumen]")
    else:
        print("Uso:")
        print("  python agente_encuestas.py abrir          → abre dashboards")
        print("  python agente_encuestas.py log YS 'X' 50  → registra encuesta")
        print("  python agente_encuestas.py resumen        → muestra total")   
