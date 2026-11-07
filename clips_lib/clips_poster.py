import os
import json
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Aquí llamas a TUS agentes existentes
# Ajusta el nombre del script o la función según cómo los tengas

def post_clips(clips: list[str]):
    """Dispara a tus agentes para que posteen los clips."""
    print(f"\n[POST] {len(clips)} clips listos para postear.")

    for i, clip_path in enumerate(clips):
        filename = os.path.basename(clip_path)
        print(f"[POST] Clip {i+1}: {filename}")

        # --- OPCIÓN A: Llamar a tu agente por CLI ---
        # Ajusta "python" y la ruta a tu agente de posting
        # cmd = [sys.executable, os.path.join(BASE_DIR, "src", "agente_post.py"), clip_path]
        # subprocess.run(cmd)

        # --- OPCIÓN B: Llamar a tu agente por API (si tienes uno) ---
        # import requests
        # requests.post("http://localhost:5000/post", json={"clip": clip_path})

        # --- OPCIÓN C: Solo registrar (para que otro proceso los tome) ---
        queue_file = os.path.join(BASE_DIR, "clips_output", "pending_posts.json")
        queue = []
        if os.path.exists(queue_file):
            with open(queue_file) as f:
                queue = json.load(f)
        queue.append({
            "file": clip_path,
            "name": filename,
            "queued_at": datetime.now().isoformat(),
            "posted": False
        })
        with open(queue_file, "w") as f:
            json.dump(queue, f, indent=2)

        print(f"[POST] En cola: {filename}")

    print(f"[POST] Total en cola: {len(queue)} clips.")   
