# clips_lib/cookie_extractor.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import subprocess
import json

# Extrae cookies de Chrome/Firefox para TikTok
def extract_cookies():
    # Opción A: desde Chrome (si tienes Chrome)
    chrome_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies")
    
    # Opción B: manual (más confiable)
    print("[INFO] Para extraer cookies de TikTok:")
    print("  1. Abre TikTok en Chrome")
    print("  2. F12 → Application → Cookies → tiktok.com")
    print("  3. Copia el valor de 'sessionid'")
    print("  4. Pégalo abajo:")
    
    sessionid = input("  sessionid: ").strip()
    
    if sessionid:
        output = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")
        with open(output, "w", encoding="utf-8") as f:
            f.write(f"sessionid={sessionid}\n")
        print(f"[OK] cookies.txt creado: {os.path.abspath(output)}")
    else:
        print("[ERROR] No se ingresó sessionid.")

if __name__ == "__main__":
    extract_cookies()   
