import argparse
import importlib.util
import logging
import sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("main")

AGENTES_DIR = BASE / "agents"


def _modo_interactivo() -> None:
    from agent import meta_loop
    print("Agente autónomo. Escribe 'salir' para terminar.\n")
    while True:
        try:
            user_input = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("salir", "exit", "q"):
            break
        if not user_input:
            continue
        print(f"\n[AGENTE]\n{meta_loop(user_input)}\n")


def _modo_tarea(task: str) -> None:
    from agent import meta_loop
    print(f"[TAREA] {task}\n")
    print(meta_loop(task))


def _modo_daemon() -> None:
    logger.info("Arrancando coordinador (scheduler por intervalos)...")
    import coordinador
    coordinador.main()


def _modo_roadmap() -> None:
    logger.info("Arrancando daemon roadmap (executor de roadmap.json)...")
    import daemon
    daemon.main()


def _listar_agentes() -> None:
    print(f"Agentes en {AGENTES_DIR}:\n")
    if not AGENTES_DIR.exists():
        print("  (carpeta no existe)")
        return
    for f in sorted(AGENTES_DIR.glob("*.py")):
        if f.name.startswith("__"):
            continue
        print(f"  • {f.stem}")
    for f in sorted(AGENTES_DIR.glob("*.md")):
        print(f"  • {f.stem}  [prompt]")


def _run_agente(name: str) -> None:
    path = AGENTES_DIR / f"{name}.py"
    if not path.exists():
        path = BASE / f"{name}.py"
    if not path.exists():
        print(f"ERROR: agente '{name}' no encontrado.")
        return
    logger.info("Ejecutando agente: %s", name)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "run"):
        result = mod.run()
        print(f"\nResultado: {result}")
    else:
        print(f"WARNING: {name}.py no tiene función run()")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sistema de agentes — entry point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py                  modo interactivo
  python main.py "busca leads"    tarea one-shot
  python main.py --daemon         arrancar scheduler (coordinador)
  python main.py --roadmap        arrancar executor de roadmap.json
  python main.py --agents         listar agentes
  python main.py --run encuestas  ejecutar un agente específico
        """
    )
    parser.add_argument("task", nargs="*", help="Tarea para el agente LLM")
    parser.add_argument("--daemon", action="store_true", help="Arrancar coordinador (scheduler)")
    parser.add_argument("--roadmap", action="store_true", help="Arrancar daemon roadmap (executor)")
    parser.add_argument("--agents", action="store_true", help="Listar agentes")
    parser.add_argument("--run", metavar="AGENTE", help="Ejecutar agente específico")

    args = parser.parse_args()

    if args.daemon:
        _modo_daemon()
    elif args.roadmap:
        _modo_roadmap()
    elif args.agents:
        _listar_agentes()
    elif args.run:
        _run_agente(args.run)
    elif args.task:
        _modo_tarea(" ".join(args.task))
    else:
        _modo_interactivo()


if __name__ == "__main__":
    main()
