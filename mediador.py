import sys, os, json, subprocess
from pathlib import Path
from datetime import datetime

# --- Voz → Texto ---
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# --- Texto → Voz (ONNX local) ---
try:
    from faster_whisper import WhisperModel  # solo si usas whisper para STT
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

# TTS: usar pyttsx3 (offline, sin internet) o el ONNX
try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from bus import write, read_all

def listen():
    """Escucha lo que el usuario dice."""
    if not HAS_SR:
        print("[VOZ] SpeechRecognition no instalado. pip install SpeechRecognition")
        return ""

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("[VOZ] Habla...")
        audio = r.listen(source, timeout=10)

    try:
        text = r.recognize_google(audio, language="es-MX")
        print(f"[VOZ] Te escuché: {text}")
        return text
    except sr.UnknownValueError:
        print("[VOZ] No entendí.")
        return ""
    except sr.RequestError:
        print("[VOZ] Error de red.")
        return ""

def speak(text):
    """Habla el texto."""
    if HAS_TTS:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.say(text)
        engine.runAndWait()
    else:
        # Fallback: solo imprimir
        print(f"[VOZ] {text}")

def process_command(text):
    """Procesa lo que el usuario dijo y lo guarda en el bus."""
    if not text:
        return

    write("usuario", "orden", resultado=text)
    print(f"[BUS] Orden guardada: {text}")

    # Ejecutar cerebro para que piense qué hacer
    try:
        r = subprocess.run([sys.executable, str(BASE / "cerebro.py")],
                         capture_output=True, text=True, timeout=30)
        if r.stdout:
            try:
                result = json.loads(r.stdout)
                voz = result.get("voz", "")
                if voz:
                    speak(voz)
                alerta = result.get("alerta")
                if alerta:
                    speak(f"Alerta: {alerta}")
            except:
                pass
    except:
        pass

def main():
    print(f"[MEDIADOR] Iniciado — {datetime.now():%H:%M}")
    print("[MEDIADOR] Di algo (o escribe 'quit' para salir).")

    while True:
        text = listen()
        if text.lower() in ("quit", "salir", "adiós", "adios"):
            speak("Hasta luego.")
            break
        process_command(text)

if __name__ == "__main__":
    main()
