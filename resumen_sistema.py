import os
import json
from datetime import datetime

def generar_resumen():
    archivos = [
        "historial_investigaciones.json",
        "historial_planes.json",
        "historial_leads.json",
        "historial_engagement.json"
    ]
    
    resumen = f"Resumen del sistema - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    resumen += "=" * 50 + "\n\n"

    for archivo in archivos:
        resumen += f"## {archivo}\n"
        if os.path.exists(archivo):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    data = json.load(f)
                resumen += f"Entradas: {len(data)}\n"
                if data:
                    ultimo = data[-1]
                    resumen += f"Último: {str(ultimo)[:300]}...\n"
            except Exception as e:
                resumen += f"Error leyendo: {e}\n"
        else:
            resumen += "No existe aún.\n"
        resumen += "\n"

    with open("resumen_sistema.txt", "w", encoding="utf-8") as f:
        f.write(resumen)
    
    print(resumen)
    print("Resumen guardado en: resumen_sistema.txt")

if __name__ == "__main__":
    generar_resumen()
