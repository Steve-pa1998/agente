import json
import os

SAVE_FILE = "savepoints.json"

def guardar_punto(nombre, historial):
    saves = {}
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            saves = json.load(f)
    saves[nombre] = historial
    with open(SAVE_FILE, "w") as f:
        json.dump(saves, f, indent=2)

def cargar_punto(nombre):
    with open(SAVE_FILE) as f:
        saves = json.load(f)
    return saves.get(nombre, None)
