import sys
import time
import json
import importlib.util
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from context_manager import ContextManager

BASE = Path(__file__).parent
LOG_FILE = BASE / "coordinador_log.txt"
STATE_FILE = BASE / "coordinador_state.json"

AGENT_INTERVALS = {
    "encuestas": 6 * 3600,
    "leads": 12 * 3600,
    "propuestas": 12 * 3600,
    "optimizer": 24 * 3600,
}

AGENT_FILES = {
    "encuestas": BASE / "agents" / "agente_encuestas.py",
    "leads": BASE / "agents" / "agentes_leads.py",
    "propuestas": BASE / "agents" / "agente_propuestas.py",
    "optimizer": BASE / "optimizer_loop.py",
}

_module_cache = {}


def _log(msg: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _ensure_path(filepath: Path) -> None:
    parent = filepath.parent
    if str(parent) not in sys.path:
        sys.path.insert(0, str(parent))


def _load_module(filepath: Path, name: str):
    if name in _module_cache:
        return _module_cache[name]
    _ensure_path(filepath)
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    _module_cache[name] = mod
    return mod


def _run_agent(name: str) -> None:
    filepath = AGENT_FILES.get(name)
    if filepath is None:
        _log(f"agente '{name}': no existe, skip")
        return
    try:
        mod = _load_module(filepath, name)
        candidates = [f for f in ("run", "main", "run_optimizer_cycle")
                      if hasattr(mod, f) and callable(getattr(mod, f))]
        if candidates:
            fn = getattr(mod, candidates[0])
            fn()
            _log(f"agente '{name}': ok ({candidates[0]}())")
        else:
            _log(f"agente '{name}': no funcion ejecutable encontrada")
    except Exception as e:
        _log(f"agente '{name}': ERROR {e}")


def _run_cerebro(ctx: ContextManager = None) -> None:
    try:
        mod = _load_module(BASE / "cerebro.py", "cerebro")
        candidates = [f for f in ("run", "think", "main")
                      if hasattr(mod, f) and callable(getattr(mod, f))]
        if "run" in candidates:
            mod.run()
            _log("cerebro: ok")
        elif "think" in candidates:
            items = ctx.rotate() if ctx else []
            contexto_str = "\n".join(
                f"[{m['ts']}] {m['agente']}" for m in items
            ) if items else None
            mod.think(contexto=contexto_str)
            _log("cerebro: ok (think())")
        elif candidates:
            func_name = candidates[0]
            getattr(mod, func_name)()
            _log(f"cerebro: ok ({func_name}())")
        else:
            _log("cerebro: no funcion encontrada")
    except Exception as e:
        _log(f"cerebro: ERROR {e}")


def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main() -> None:
    _log("--- Coordinador iniciado ---")
    state = _load_state()
    ctx = ContextManager(max_msgs=25)

    while True:
        now = time.time()
        for agent_name, interval in AGENT_INTERVALS.items():
            if now - state.get(agent_name, 0) >= interval:
                _log(f"--- Ejecutando: {agent_name} ---")
                _run_agent(agent_name)
                state[agent_name] = now
                ctx.add({"agente": agent_name, "ts": now})
                _save_state(state)

        _run_cerebro(ctx)
        _log("Durmiendo 300s...")
        time.sleep(300)


if __name__ == "__main__":
    main()   
