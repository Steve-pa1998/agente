import subprocess, os, json, sys
from pathlib import Path

CLIPS_DIR = os.path.join(os.path.dirname(__file__), "clips_output")
os.makedirs(CLIPS_DIR, exist_ok=True)
MAX_CLIPS = 10
CLIP_MIN = 30

def get_duration(vod_path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", vod_path],
        capture_output=True, text=True
    )
    return float(json.loads(r.stdout)["format"]["duration"])

def detect_silences(vod_path, min_dur=2.0):
    r = subprocess.run(
        ["ffmpeg", "-i", vod_path, "-af", f"silencedetect=noise=-30dB:d={min_dur}", "-f", "null", "-"],
        capture_output=True, text=True
    )
    silences = []
    start = None
    for line in r.stderr.splitlines():
        if "silence_start:" in line:
            start = float(line.split("silence_start:")[1].split()[0])
        elif "silence_end:" in line and start is not None:
            end = float(line.split("silence_end:")[1].split()[0])
            silences.append((start, end))
            start = None
    return silences

def find_peaks(vod_path, threshold=-20):
    r = subprocess.run(
        ["ffmpeg", "-i", vod_path, "-af", f"astats=metadata=1,ametadata=print:key=lavfi.astats.Overall.RMS_level", "-f", "null", "-"],
        capture_output=True, text=True
    )
    peaks = []
    current_time = 0
    for line in r.stderr.splitlines():
        if "pts_time:" in line:
            try:
                current_time = float(line.split("pts_time:")[1].split()[0])
            except:
                pass
        if "RMS_level" in line:
            try:
                val = float(line.split("RMS_level:")[1].split()[0])
                if val > threshold and val < 0:
                    peaks.append(current_time)
            except:
                pass
    return peaks

def find_windows_from_silences(silences, duration):
    windows = []
    for i in range(len(silences) - 1):
        start = silences[i][1]
        end = silences[i + 1][0]
        if end - start >= CLIP_MIN:
            windows.append((start, end))
    return windows[:MAX_CLIPS]

def find_windows_from_peaks(peaks, duration):
    windows = []
    if not peaks:
        return windows
    peak_dur = max(duration / MAX_CLIPS, CLIP_MIN)
    i = 0
    while i < len(peaks) and len(windows) < MAX_CLIPS:
        start = max(0, peaks[i] - 5)
        end = min(duration, start + peak_dur)
        if end - start >= CLIP_MIN:
            windows.append((start, end))
        i += int(peak_dur)
    return windows

def uniform_windows(duration):
    clip_dur = max(duration / MAX_CLIPS, CLIP_MIN)
    windows = []
    start = 0
    while start < duration - 10:
        end = min(start + clip_dur, duration)
        if end - start < 15:
            break
        windows.append((start, end))
        start = end
    return windows[:MAX_CLIPS]

def process_vod(vod_path):
    print(f"[VOD] {os.path.basename(vod_path)}")
    duration = get_duration(vod_path)
    print(f"[VOD] Duracion: {duration:.0f}s ({duration/60:.1f} min)")

    # Intento 1: silencios
    silences = detect_silences(vod_path)
    windows = find_windows_from_silences(silences, duration)
    if windows:
        print(f"[EDIT] {len(windows)} clips por silencios.")

    # Intento 2: picos de volumen
    if not windows:
        peaks = find_peaks(vod_path)
        windows = find_windows_from_peaks(peaks, duration)
        if windows:
            print(f"[EDIT] {len(windows)} clips por picos de volumen.")

    # Intento 3: division uniforme (SIEMPRE funciona)
    if not windows:
        windows = uniform_windows(duration)
        print(f"[EDIT] {len(windows)} clips por division uniforme.")

    if not windows:
        print("[ERROR] VOD demasiado corto.")
        return []

    clips = []
    for i, (start, end) in enumerate(windows):
        dur = end - start
        out_path = os.path.join(CLIPS_DIR, f"clip_{i+1:02d}.mp4")
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(start), "-t", str(dur), "-i", vod_path,
             "-c:v", "libx264", "-crf", "23", "-c:a", "aac",
             "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
             out_path],
            capture_output=True, timeout=600
        )
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            clips.append(out_path)
            print(f"[OK] clip_{i+1:02d}.mp4 ({os.path.getsize(out_path)//1024} KB)")
        else:
            print(f"[FAIL] clip_{i+1:02d}.mp4")

    print(f"\n[EDIT] Total: {len(clips)}/{MAX_CLIPS} clips.")
    return clips

if __name__ == "__main__":
    VOD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(CLIPS_DIR, "vod_v2904565493.mp4")
    if os.path.exists(VOD):
        process_vod(VOD)
    else:
        print(f"[ERROR] No existe: {VOD}")
        print("[HINT] Pega la ruta del VOD: python clips_editor.py ruta\\a\\tu\\vod.mp4")
