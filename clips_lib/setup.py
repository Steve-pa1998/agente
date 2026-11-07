from pathlib import Path

ROOT = Path(r"C:\Users\Steve\Desktop\agente")

STRUCTURE = [
    "agents",
    "clips_lib",
    "clips_lib/clips_output",
    "clips_lib/brand",
    "clips_lib/brand/clips_template",
    "clips_lib/brand/logo",
    "freelance",
    "freelance/plantillas",
    "freelance/jales",
    "freelance/entregables",
    "freelance/portafolio",
    "freelance/portafolio/scrapers",
    "freelance/leads",
    "docs",
]

def setup():
    created = []
    for d in STRUCTURE:
        p = ROOT / d
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            created.append(d)
    if created:
        print(f"[SETUP] Creadas: {', '.join(created)}")
    else:
        print("[SETUP] Todo en orden. Nada que crear.")

if __name__ == "__main__":
    setup()
