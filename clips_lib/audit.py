import os
import subprocess
from pathlib import Path

import sys
sys.stdout.reconfigure(encoding='utf-8')   

ROOT = Path(r"C:\Users\Steve\Desktop\agente")
CLIPS_LIB = ROOT / "clips_lib"
BRAND = CLIPS_LIB / "brand"
AGENTS = ROOT / "agents"
OUTPUT = CLIPS_LIB / "clips_output"

def audit():
    report = []
    report.append("=" * 50)
    report.append("  AUDITORÍA DEL PROYECTO")
    report.append("=" * 50)

    # 1. Estructura
    report.append("\n[1] ESTRUCTURA")
    checks = {
        "main.py": ROOT / "mi" / "agente" / "main.py",
        "clips_editor.py": CLIPS_LIB / "clips_editor.py",
        "build.py (branding)": BRAND / "build.py",
        "AGENTS.md (coordinador)": ROOT / "AGENTS.md",
        "agents/ (carpeta)": AGENTS,
        "brand/ (carpeta)": BRAND,
        "clips_output/ (carpeta)": OUTPUT,
    }
    for name, path in checks.items():
        status = "[OK]" if path.exists() else "❌"
        report.append(f"  {status} {name}")

    # 2. Branding
    report.append("\n[2] BRANDING (PNGs)")
    brand_files = ["logo_800.png", "overlay_1920.png", "template_clips_1080.png", "banner_1280.png", "offline_1920.png"]
    for f in brand_files:
        p = BRAND / f
        if p.exists() and p.stat().st_size > 1000:
            report.append(f"  [OK] {f} ({p.stat().st_size//1024} KB)")
        elif p.exists():
            report.append(f"  ⚠️ {f} (vacío: {p.stat().st_size} bytes)")
        else:
            report.append(f"  ❌ {f} (no existe)")

    # 3. VODs
    report.append("\n[3] VODs")
    vods = list(OUTPUT.glob("vod_*.mp4")) if OUTPUT.exists() else []
    for v in vods:
        size_gb = v.stat().st_size / (1024**3)
        report.append(f"  📹 {v.name} ({size_gb:.1f} GB)")
    if not vods:
        report.append("  ❌ Sin VODs en clips_output/")

    # 4. Clips generados
    report.append("\n[4] CLIPS GENERADOS")
    clips = list(OUTPUT.glob("clip_*.mp4")) if OUTPUT.exists() else []
    valid = [c for c in clips if c.stat().st_size > 1000]
    invalid = [c for c in clips if c.stat().st_size <= 1000]
    report.append(f"  [OK] Válidos: {len(valid)}")
    report.append(f"  ❌ Vacíos: {len(invalid)}")
    if invalid:
        report.append("     → Borrar: " + ", ".join(c.name for c in invalid[:5]))

    # 5. Agentes
    report.append("\n[5] AGENTES (.md)")
    if AGENTS.exists():
        mds = list(AGENTS.glob("*.md"))
        for m in sorted(mds):
            size = m.stat().st_size
            status = "✅" if size > 100 else "⚠️ (muy corto)"
            report.append(f"  {status} {m.name} ({size} bytes)")
    else:
        report.append("  ❌ Carpeta agents/ no existe")

    # 6. FFmpeg
    report.append("\n[6] DEPENDENCIAS")
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        ver = r.stdout.split("\n")[0] if r.stdout else "desconocida"
        report.append(f"  ✅ FFmpeg: {ver}")
    except:
        report.append("  ❌ FFmpeg: NO INSTALADO")

    try:
        r = subprocess.run(["ffprobe", "-version"], capture_output=True, text=True, timeout=5)
        report.append(f"  ✅ FFprobe: instalado")
    except:
        report.append("  ❌ FFprobe: NO INSTALADO")

    try:
        import PIL
        report.append(f"  ✅ Pillow: {PIL.__version__}")
    except:
        report.append("  ❌ Pillow: NO INSTALADO")

    try:
        import openai
        report.append(f"  ✅ OpenAI SDK: {openai.__version__}")
    except:
        report.append("  ❌ OpenAI SDK: NO INSTALADO")

    try:
        import dotenv
        report.append(f"  ✅ python-dotenv: instalado")
    except:
        report.append("  ❌ python-dotenv: NO INSTALADO")

    # 7. .env
    report.append("\n[7] CONFIGURACIÓN")
    env_file = ROOT / "mi" / "agente" / ".env"
    if env_file.exists():
        content = env_file.read_text()
        has_key = "GROQ_API_KEY" in content
        report.append(f"  {'✅' if has_key else '❌'} .env con GROQ_API_KEY")
    else:
        report.append("  ❌ .env no encontrado")

    # 8. Cookies TikTok
    report.append("\n[8] TIKTOK")
    cookies = CLIPS_LIB / "poster" / "cookies.txt"
    if not cookies.exists():
        cookies = CLIPS_LIB / "cookies.txt"
    if cookies.exists() and cookies.stat().st_size > 100:
        report.append(f"  ✅ cookies.txt ({cookies.stat().st_size} bytes)")
    else:
        report.append("  ❌ cookies.txt: FALTA (necesario para subir a TikTok)")

    # 9. Clips vacíos a borrar
    report.append("\n[9] ACCIONES PENDIENTES")
    actions = []
    if invalid:
        actions.append(f"Borrar {len(invalid)} clips vacíos")
    if not vods:
        actions.append("Descargar VODs (yt-dlp)")
    if not (cookies.exists() and cookies.stat().st_size > 100):
        actions.append("Exportar cookies.txt para TikTok")
    if not actions:
        actions.append("Nada. Todo en orden.")
    for a in actions:
        report.append(f"  → {a}")

    report.append("\n" + "=" * 50)
    return "\n".join(report)


if __name__ == "__main__":
    print(audit())   
