# clips_lib/cleanup.py
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import shutil
from datetime import datetime, timedelta

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "clips_output")
MAX_AGE_DAYS = 7  # borra clips de más de 7 días

def cleanup():
    if not os.path.exists(OUTPUT_DIR):
        print("[OK] clips_output no existe, nada que limpiar.")
        return
    
    cutoff = datetime.now() - timedelta(days=MAX_AGE_DAYS)
    borrados = 0
    
    for f in os.listdir(OUTPUT_DIR):
        filepath = os.path.join(OUTPUT_DIR, f)
        if os.path.isfile(filepath):
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff:
                os.remove(filepath)
                borrados += 1
                print(f"[DEL] {f}")
    
    print(f"[OK] {borrados} clips viejos eliminados (> {MAX_AGE_DAYS} días)")

if __name__ == "__main__":
    cleanup()   
