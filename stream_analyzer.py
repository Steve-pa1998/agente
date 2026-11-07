import os, subprocess, json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)
MODEL = "openai/gpt-oss-120b"

def analyze_vod(vod_path):
    """Analiza el VOD y devuelve un reporte de problemas."""
    print(f"\n🔍 Analizando: {os.path.basename(vod_path)}")
    print("-" * 40)
    issues = []
    stats = {}

    # 1. Metadatos básicos
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", vod_path],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        data = json.loads(r.stdout)
        fmt = data.get("format", {})
        stats["duration"] = int(float(fmt.get("duration", 0)))
        stats["bitrate_total"] = int(fmt.get("bit_rate", 0)) // 1000

        for s in data.get("streams", []):
            if s["codec_type"] == "video":
                stats["res"] = f"{s.get('width')}x{s.get('height')}"
                stats["fps"] = eval(s.get("r_frame_rate", "0/1"))
                stats["video_bitrate"] = int(s.get("bit_rate", 0)) // 1000
                stats["codec"] = s.get("codec_name")

            elif s["codec_type"] == "audio":
                stats["audio_codec"] = s.get("codec_name")
                stats["audio_sample_rate"] = s.get("sample_rate")
                stats["audio_bitrate"] = int(s.get("bit_rate", 0)) // 1000

        # Check: bitrate de video
        expected_bitrate = 6000 if "1080" in stats.get("res", "") else 4000
        if stats.get("video_bitrate", 0) < expected_bitrate:
            issues.append(f"⚠️ Bitrate de video bajo: {stats['video_bitrate']}kbps (recomendado: {expected_bitrate}kbps para {stats.get('res')})")

        # Check: fps
        if stats.get("fps", 0) < 30:
            issues.append(f"⚠️ FPS bajo: {stats['fps']} (recomendado: 30+)")

        # Check: codec
        if stats.get("codec") not in ("h264", "hevc"):
            issues.append(f"⚠️ Codec no estándar: {stats.get('codec')} (usa H.264)")

        # Check: audio
        if "audio" not in str(stats):
            issues.append("🚨 NO HAY AUDIO en el VOD")

    # 2. Volumen de audio
    r = subprocess.run(
        ["ffmpeg", "-i", vod_path, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True
    )
    for line in r.stderr.split("\n"):
        if "mean_volume" in line:
            vol = float(line.split(":")[1].strip().replace("dB", ""))
            stats["mean_volume"] = vol
            if vol < -30:
                issues.append(f"🚨 Audio muy bajo: {vol} dB (debería ser -15 a -20 dB)")
            elif vol > -10:
                issues.append(f"⚠️ Audio muy alto: {vol} dB (riesgo de distorsión)")
        if "max_volume" in line:
            vol = float(line.split(":")[1].strip().replace("dB", ""))
            stats["max_volume"] = vol
            if vol > -1:
                issues.append(f"🚨 Audio con clipping: {vol} dB (debe ser < -1 dB)")

    # 3. Silencios largos
    r = subprocess.run(
        ["ffmpeg", "-i", vod_path, "-af", "silencedetect=noise=-40dB:d=10", "-f", "null", "-"],
        capture_output=True, text=True
    )
    silences = []
    for line in r.stderr.split("\n"):
        if "silence_start" in line:
            silences.append(line.split(":")[1].strip())
    if silences:
        stats["silencios_10s+"] = len(silences)
        if len(silences) > 5:
            issues.append(f"⚠️ {len(silences)} silencios de 10+ segundos (te quedaste callado mucho)")

    # 4. Duración
    if stats.get("duration", 0) < 600:
        issues.append(f"⚠️ Stream corto: {stats['duration']//60} min (recomendado: 30+ min para generar VOD útil)")

    # 5. Reporte
    print(f"📊 STATS: {stats}")
    print(f"\n🔧 PROBLEMAS ({len(issues)}):")
    for i in issues:
        print(f"   {i}")

    if not issues:
        print("   ✅ No se detectaron problemas técnicos.")

    # 6. El agente genera recomendaciones
    report = f"""Stream: {os.path.basename(vod_path)}
Duración: {stats.get('duration', 0)//60} min
Resolución: {stats.get('res')}
FPS: {stats.get('fps')}
Bitrate video: {stats.get('video_bitrate')} kbps
Audio: {stats.get('audio_codec')} @ {stats.get('audio_sample_rate')} Hz
Volumen medio: {stats.get('mean_volume')} dB
Volumen máx: {stats.get('max_volume')} dB
Silencios 10s+: {stats.get('silencios_10s+', 0)}

Problemas detectados:
{chr(10).join(issues) if issues else 'Ninguno'}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Eres un técnico de streaming. Analiza el reporte y dame 3-5 recomendaciones accionables en español. Sé específico: qué cambiar, en qué app (OBS, Discord, etc.), y a qué valor. No seas genérico."},
            {"role": "user", "content": report}
        ]
    )

    print(f"\n💡 RECOMENDACIONES DEL AGENTE:")
    print(response.choices[0].message.content)
    print("-" * 40)

    return {"stats": stats, "issues": issues, "recomendaciones": response.choices[0].message.content}


if __name__ == "__main__":
    # Buscar el VOD más reciente
    clips_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clips_lib", "clips_output")
    if os.path.exists(clips_dir):
        vods = [f for f in os.listdir(clips_dir) if f.endswith(".mp4")]
        if vods:
            latest = max(vods, key=lambda f: os.path.getmtime(os.path.join(clips_dir, f)))
            analyze_vod(os.path.join(clips_dir, latest))
        else:
            print("No hay VODs en clips_lib/clips_output/")
    else:
        print("Carpeta clips_lib/clips_output/ no existe.")   
