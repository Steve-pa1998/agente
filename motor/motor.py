# motor.py — Motor de tareas genérico
# Pega en: C:\Users\Steve\Desktop\agente\motor\motor.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, os, time
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.join(BASE, "pipeline.json")
RESULTADOS = os.path.join(BASE, "resultados.json")

def _load(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _rank(pts, dur_min, sens=""):
    if dur_min <= 0: return "C"
    pmp = pts / dur_min
    buena = sens in ["facil", "normal", "buena", ""]
    if pmp > 15 and buena: return "S"
    if pmp > 8 and buena: return "A"
    if pmp > 4: return "B"
    return "C"

def agregar_tarea(tipo, nombre, dur_est, dificultad, pts_esperados, url=""):
    """Agrega una tarea al pipeline."""
    p = _load(PIPELINE, {"tareas": []})
    p["tareas"].append({
        "id": len(p["tareas"]) + 1,
        "tipo": tipo,
        "nombre": nombre,
        "dur_est_min": int(dur_est),
        "dificultad": int(dificultad),
        "pts_esperados": int(pts_esperados),
        "url": url,
        "estado": "disponible",
        "fecha_agregada": datetime.now().isoformat()
    })
    _save(PIPELINE, p)
    r = _rank(pts_esperados, dur_est)
    print(f"  ⚔️  [{r}] {nombre} | {tipo} | ~{dur_est}min | dif:{dificultad}")

def tomar():
    """Muestra la siguiente tarea recomendada (mejor pts/min disponible)."""
    p = _load(PIPELINE, {"tareas": []})
    disponibles = [t for t in p["tareas"] if t["estado"] == "disponible"]
    if not disponibles:
        print("  📋 Sin tareas disponibles. Agrega con: py motor.py agregar ...")
        return
    # Ordenar por pts/min esperado (desc)
    disponibles.sort(key=lambda t: t["pts_esperados"] / max(1, t["dur_est_min"]), reverse=True)
    t = disponibles[0]
    r = _rank(t["pts_esperados"], t["dur_est_min"])
    icon = {"S":"🟢","A":"🔵","B":"🟡","C":"🔴"}[r]
    print(f"\n  {icon} SIGUIENTE TAREA:")
    print(f"     {t['nombre']} ({t['tipo']})")
    print(f"     ~{t['dur_est_min']}min | dif:{t['dificultad']} | ~{t['pts_esperados']}pts")
    print(f"     URL: {t.get('url','N/A')}")
    print(f"\n     Al terminar: py motor.py completar {t['id']} <pts_reales> <sensacion>")
    print()

def completar(tarea_id, pts_reales, sens=""):
    """Marca tarea como completada y registra métricas."""
    p = _load(PIPELINE, {"tareas": []})
    r = _load(RESULTADOS, {"completadas": [], "total_pts": 0, "xp": 0})
    
    for t in p["tareas"]:
        if t["id"] == int(tarea_id):
            t["estado"] = "completada"
            break
    
    # Buscar el inicio (si existe)
    inicio = None
    for c in reversed(r["completadas"]):
        if c.get("tarea_id") == int(tarea_id) and c.get("estado") == "en_progreso":
            inicio = c
            break
    
    if inicio:
        dur = (time.time() - inicio["ts"]) / 60
        inicio["estado"] = "completada"
        inicio["dur_real"] = round(dur, 1)
        inicio["pts"] = int(pts_reales)
        inicio["sens"] = sens
        inicio["pmp"] = round(int(pts_reales) / dur, 2) if dur > 0 else 0
        inicio["rank"] = _rank(int(pts_reales), dur, sens)
    else:
        r["completadas"].append({
            "tarea_id": int(tarea_id),
            "fecha": datetime.now().isoformat(),
            "pts": int(pts_reales),
            "sens": sens,
            "pmp": 0,
            "rank": _rank(int(pts_reales), 5, sens)
        })
    
    r["total_pts"] += int(pts_reales)
    r["xp"] += 10
    _save(PIPELINE, p)
    _save(RESULTADOS, r)
    
    e = r["completadas"][-1]
    icon = {"S":"🟢","A":"🔵","B":"🟡","C":"🔴"}.get(e.get("rank","C"), "⚪")
    print(f"  {icon} +{pts_reales}pts | Rank: {e.get('rank','?')} | Total: {r['total_pts']}pts")

def iniciar(tarea_id):
    """Inicia timer para una tarea."""
    r = _load(RESULTADOS, {"completadas": [], "total_pts": 0, "xp": 0})
    r["completadas"].append({
        "tarea_id": int(tarea_id),
        "ts": time.time(),
        "estado": "en_progreso"
    })
    _save(RESULTADOS, r)
    print(f"  ⏱️  Tarea {tarea_id} iniciada. Al terminar: py motor.py completar {tarea_id} <pts> <sens>")

def board():
    """Muestra el board completo."""
    p = _load(PIPELINE, {"tareas": []})
    r = _load(RESULTADOS, {"completadas": [], "total_pts": 0, "xp": 0})
    comp = [c for c in r["completadas"] if c.get("estado") == "completada"]
    disp = [t for t in p["tareas"] if t["estado"] == "disponible"]
    
    print(f"\n{'='*52}")
    print(f"  📋 MOTOR — BOARD")
    print(f"{'='*52}")
    print(f"  💰 Total: {r['total_pts']} pts | 📈 XP: {r['xp']}")
    print(f"  📌 Disponibles: {len(disp)} | Completadas: {len(comp)}")
    print(f"{'='*52}")
    
    if comp:
        # Por tipo
        por_tipo = {}
        for c in comp:
            t_id = c.get("tarea_id", 0)
            tipo = "desconocido"
            for t in p["tareas"]:
                if t["id"] == t_id:
                    tipo = t["tipo"]
                    break
            if tipo not in por_tipo:
                por_tipo[tipo] = {"n": 0, "pts": 0, "min": 0}
            por_tipo[tipo]["n"] += 1
            por_tipo[tipo]["pts"] += c.get("pts", 0)
            por_tipo[tipo]["min"] += c.get("dur_real", 0)
        
        print(f"\n  {'Tipo':<15}{'N':<4}{'Pts':<7}{'Pts/Min':<9}")
        print(f"  {'-'*38}")
        for tipo, v in sorted(por_tipo.items(), key=lambda x: x[1]["pts"]/max(1,x[1]["min"]), reverse=True):
            pmp = round(v["pts"]/v["min"], 1) if v["min"] > 0 else 0
            print(f"  {tipo:<15}{v['n']:<4}{v['pts']:<7}{pmp:<9}")
    
    if disp:
        print(f"\n  PRÓXIMAS (por pts/min):")
        disp.sort(key=lambda t: t["pts_esperados"]/max(1,t["dur_est_min"]), reverse=True)
        for t in disp[:5]:
            r = _rank(t["pts_esperados"], t["dur_est_min"])
            icon = {"S":"🟢","A":"🔵","B":"🟡","C":"🔴"}[r]
            print(f"  {icon} {t['nombre']} (~{t['dur_est_min']}min, ~{t['pts_esperados']}pts)")
    
    print(f"{'='*52}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "agregar" and len(sys.argv) >= 7:
            url = sys.argv[7] if len(sys.argv) > 7 else ""
            agregar_tarea(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], url)
        elif cmd == "tomar":
            tomar()
        elif cmd == "iniciar" and len(sys.argv) >= 3:
            iniciar(sys.argv[2])
        elif cmd == "completar" and len(sys.argv) >= 4:
            sens = sys.argv[4] if len(sys.argv) > 4 else ""
            completar(sys.argv[2], sys.argv[3], sens)
        elif cmd == "board":
            board()
        else:
            print("  Uso:")
            print("    py motor.py agregar <tipo> <nombre> <min> <dif> <pts> [url]")
            print("    py motor.py tomar")
            print("    py motor.py iniciar <id>")
            print("    py motor.py completar <id> <pts> [sens]")
            print("    py motor.py board")
    else:
        board()   
