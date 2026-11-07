import os, time, json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from tiktok_uploader.upload import TikTokUploader

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

MODEL = "openai/gpt-oss-120b"
POST_HOUR = 18  # 6 PM
POST_MINUTE = 0

def generar_caption(tema):
    """El agente decide qué caption postear."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Eres un copywriter para TikTok de un streamer. Escribe captions cortas, con hook, y 3 hashtags. Máximo 150 caracteres. No expliques, solo da la caption."},
            {"role": "user", "content": f"Tema del video: {tema}\nEscribe la caption."}
        ]
    )
    return response.choices[0].message.content.strip()

def postear(video_path, caption):
    """Sube el video a TikTok."""
    uploader = TikTokUploader(cookies="cookies.txt")
    result = uploader.upload_video(video_path, description=caption)
    if result:
        print(f"✅ Publicado: {caption[:50]}...")
    else:
        print("❌ Falló la publicación.")

def job_diario():
    """Se ejecuta todos los días a la hora programada."""
    print(f"\n📅 [{datetime.now().strftime('%Y-%m-%d %H:%M')}] Job diario iniciado.\n")

    # 1. Buscar el video más reciente en la carpeta clips/
    clips_dir = "clips"
    if not os.path.exists(clips_dir):
        print("⚠️ No existe la carpeta 'clips/'. Crea uno.")
        return

    videos = [f for f in os.listdir(clips_dir) if f.endswith((".mp4", ".mov"))]
    if not videos:
        print("⚠️ No hay videos en clips/. Agrega uno.")
        return

    # El más reciente
    video = max(videos, key=lambda f: os.path.getmtime(os.path.join(clips_dir, f)))
    video_path = os.path.join(clips_dir, video)
    print(f"🎬 Video: {video}")

    # 2. El agente genera la caption
    tema = input("¿De qué es el video? (o 'auto' para que el agente decida): ").strip()
    if tema.lower() == "auto":
        tema = f"Clip de stream: {video}"
    caption = generar_caption(tema)
    print(f"📝 Caption: {caption}")

    # 3. HITL: tú apruebas
    confirm = input("¿Publicar? (s/n): ").strip().lower()
    if confirm != "s":
        print("❌ Cancelado.")
        return

    # 4. Postear
    postear(video_path, caption)

# --- Scheduler ---

def run_scheduler():
    print(f"🤖 Poster diario activo. Se ejecutará todos los días a las {POST_HOUR:02d}:{POST_MINUTE:02d}.")
    print("Escribe 'postear' para postear ahora, o 'salir' para cerrar.\n")

    while True:
        now = datetime.now()
        next_post = now.replace(hour=POST_HOUR, minute=POST_MINUTE, second=0)
        if now >= next_post:
            next_post = next_post.replace(day=next_post.day + 1) if (next_post.day < now.day) else next_post + __import__('datetime').timedelta(days=1)

        # Esperar hasta la hora (o comando manual)
        while True:
            cmd = input().strip().lower()
            if cmd == "postear":
                job_diario()
                break
            elif cmd == "salir":
                print("👋 Cerrando scheduler.")
                return
            elif cmd == "":
                # Esperar 60 seg y re-check
                time.sleep(60)
                now = datetime.now()
                if now.hour == POST_HOUR and now.minute >= POST_MINUTE:
                    job_diario()
                    break

if __name__ == "__main__":
    run_scheduler()   
