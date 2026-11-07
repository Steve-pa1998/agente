import subprocess, os, json, sys
from pathlib import Path
from datetime import datetime

MUSICA_DIR = Path(__file__).parent.parent / "musica"
RAW_DIR = MUSICA_DIR / "raw"
OUT_DIR = MUSICA_DIR / "tracks"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_env():
    env = {}
    for line in (Path(__file__).parent.parent / ".env").read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

env = load_env()
GROQ_KEY = env.get("GROQ_API_KEY", "")

def list_raw():
    """Lista grabaciones sin procesar."""
    files = list(RAW_DIR.glob("*.wav")) + list(RAW_DIR.glob("*.mp3"))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files

def process(input_file, output_name=None):
    """
    Procesa una grabación:
    1. Normaliza volumen
    2. Aplica compresión suave
    3. Exporta MP3
    Nota: El autotune (Graillon/MAutoPitch) se aplica en Cakewalk Sonar,
    no por script. Este script hace pre-producción.
    """
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"[ERROR] No existe: {input_file}")
        return

    if not output_name:
        output_name = input_path.stem
    out_path = OUT_DIR / f"{output_name}_{datetime.now():%Y%m%d}.mp3"

    # Normalizar + compresión + exportar MP3
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,acompressor=threshold=-20dB:ratio=3:attack=5:release=100",
        "-b:a", "192k",
        str(out_path)
    ]

    print(f"[PROD] Procesando: {input_path.name}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        size = out_path.stat().st_size // 1024
        print(f"[PROD] ✅ {out_path.name} ({size} KB)")
        return str(out_path)
    else:
        print(f"[PROD] ❌ Error: {r.stderr[:200]}")
        return None

def generate_portada(titulo, estilo="dark"):
    """Genera una portada simple con ffmpeg (colores + texto)."""
    out_path = OUT_DIR / f"portada_{titulo.replace(' ','_')}.png"
    # Fondo oscuro con texto
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x1a1a2e:s=1000x1000:d=1",
        "-vf", f"drawtext=text='{titulo}':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2",
        "-frames:v", "1",
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        print(f"[PORTADA] ✅ {out_path.name}")
    return str(out_path)

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            files = list_raw()
            if not files:
                print("No hay grabaciones en musica/raw/")
            for f in files:
                print(f"  • {f.name} ({f.stat().st_size//1024} KB) — {datetime.fromtimestamp(f.stat().st_mtime):%d/%m %H:%M}")
        elif cmd == "process":
            if len(sys.argv) > 2:
                process(sys.argv[2])
            else:
                files = list_raw()
                if files:
                    process(files[0])
                else:
                    print("No hay grabaciones para procesar.")
        elif cmd == "portada":
            titulo = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Track"
            generate_portada(titulo)
        else:
            print("Uso: python agente_produccion.py [list|process|portada]")
    else:
        print("=== AGENTE PRODUCCIÓN ===")
        print("Comandos:")
        print("  list     — ver grabaciones")
        print("  process  — procesar la más reciente (normalizar + comprimir)")
        print("  portada  — generar portada")
        print("")
        print("Para autotune: abre Cakewalk Sonar → arrastra Graillon/MAutoPitch a la pista")

if __name__ == "__main__":
    main()
