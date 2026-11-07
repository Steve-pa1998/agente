import os, time, json, sys
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from clips_lib.downloader import run as download
from clips_lib.editor import process_vod
from clips_lib.postear import post_clips

# Hora a la que corre (ajusta a tu zona)
RUN_HOUR = 11 
RUN_MINUTE = 0

def next_run():
    """Próxima ejecución."""
    now = datetime.now()
    target = now.replace(hour=RUN_HOUR, minute=RUN_MINUTE, second=0, microsecond=0)
    if now >= target:
        from datetime import timedelta
        target += timedelta(days=1)
    return target

def run_cycle():
    """Un ciclo completo: descargar → editar → postear."""
    print(f"\n{'='*50}")
    print(f"[SCHED] Ciclo iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    # 1. Descargar
    vods = download()
    if not vods:
        print("[SCHED] Nada que procesar.")
        return

    # 2. Editar
    all_clips = []
    for vod in vods:
        clips = process_vod(vod)
        all_clips.extend(clips)

    if not all_clips:
        print("[SCHED] No se generaron clips.")
        return

    # 3. Postear
    post_clips(all_clips)

def main():
    print(f"[SCHED] Agente de clips activo.")
    print(f"[SCHED] Corre diariamente a las {RUN_HOUR:02d}:{RUN_MINUTE:02d}")
    print(f"[SCHED] 'exit' para salir.\n")

    while True:
        target = next_run()
        wait = (target - datetime.now()).total_seconds()
        print(f"[SCHED] Próxima ejecución: {target.strftime('%Y-%m-%d %H:%M')} ({int(wait//3600)}h {int(wait%3600//60)}m)")

        # Espera hasta la hora
        while datetime.now() < target:
            time.sleep(60)

        # Ejecuta
        try:
            run_cycle()
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()   
