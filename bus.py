import json, time
from pathlib import Path
from datetime import datetime

BUS_FILE = Path(__file__).parent / "bus.json"

def init():
    if not BUS_FILE.exists():
        BUS_FILE.write_text(json.dumps({"messages": []}, indent=2))

def read_all():
    if not BUS_FILE.exists():
        return []
    return json.loads(BUS_FILE.read_text())["messages"]

def write(agent, estado, problema=None, propuesta=None, resultado=None):
    data = json.loads(BUS_FILE.read_text()) if BUS_FILE.exists() else {"messages": []}
    data["messages"].append({
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
        "estado": estado,
        "problema": problema,
        "propuesta": propuesta,
        "resultado": resultado
    })
    # Mantener solo últimas 50 entradas
    data["messages"] = data["messages"][-50:]
    BUS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def clear():
    BUS_FILE.write_text(json.dumps({"messages": []}, indent=2))

if __name__ == "__main__":
    init()
    print("Bus inicializado.")
