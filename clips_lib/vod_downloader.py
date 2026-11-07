import subprocess
import os
import json
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "clips_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CANAL = "elbusk_pa_chin"

def get_latest_vod():
    """Obtiene el VOD más reciente del canal."""
    url = f"https://www.twitch.tv/elbusk_pa_chin/videos"
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-end", "1",
        "--print", "%(id)s|%(title)s|%(upload_date)s",
        url
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[ERROR] yt-dlp: {r.stderr}")
        return None

    lines = r.stdout.strip().split("\n")
    if not lines or not lines[0]:
        return None

    parts = lines[0].split("|", 2)
    if len(parts) < 3:
        return None

    vid_id, title, date = parts
    return {
        "id": vid_id,
        "title": title,
        "date": date,
        "url": f"https://www.twitch.tv/videos/{vid_id}"
    }
def download_vod(vid_id):
    """Descarga el VOD en mp4."""
    out_path = os.path.join(OUTPUT_DIR, f"vod_{vid_id}.mp4")
    if os.path.exists(out_path):
        print(f"[SKIP] Ya descargado: {out_path}")
        return out_path

    cmd = [
        "yt-dlp",
        "--merge-output-format", "mp4",
        "-o", out_path,
        f"https://www.twitch.tv/elbusk_pa_chin/v/2906953637"
    ]
    print(f"[DL] Descargando VOD {vid_id}...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[ERROR] {r.stderr}")
        return None
    print(f"[OK] {out_path}")
    return out_path

def run():
    print(f"\n{'='*50}")
    print(f"[CLIPS] {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")

    vod = get_latest_vod()
    if not vod:
        print("[SKIP] No hay VOD disponible.")
        return []

    # Solo VODs de las últimas 48h
    try:
        vod_date = datetime.strptime(vod["date"], "%Y%m%d")
        if datetime.now() - vod_date > timedelta(hours=48):
            print(f"[SKIP] VOD de {vod_date}, no es reciente.")
            return []
    except ValueError:
        pass

    path = download_vod(vod["id"])
    if not path:
        return []

    print(f"[INFO] VOD: {vod['title']}")
    return [path]   
