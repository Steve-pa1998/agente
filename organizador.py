"""
organizador.py
==============
Organiza notas por año/mes, genera índices y resúmenes diarios.

Uso:
    python organizador.py              # genera resumen de hoy + índice del mes
    python organizador.py --mes 10     # genera índice de octubre
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
CONTEXT = BASE / "context"
NOTAS = CONTEXT / "Notas"
RESUME_FILE = CONTEXT / "RESUME.md"
CHATS_DIR = CONTEXT

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

EXTENSIONES_NOTA = {".txt", ".md", ".py"}


def _mes_dir(ano: int, mes: int) -> Path:
    d = NOTAS / str(ano) / MESES[mes]
    d.mkdir(parents=True, exist_ok=True)
    return d


def _tamano_humano(path: Path) -> str:
    b = path.stat().st_size
    if b < 1024:
        return f"{b} B"
    if b < 1024 * 1024:
        return f"{b // 1024} KB"
    return f"{b // (1024 * 1024)} MB"


def _estado_sistema() -> str:
    log = BASE / "coordinador_log.txt"
    if log.exists():
        mtime = datetime.fromtimestamp(log.stat().st_mtime)
        return f"- Último coordinador: {mtime.strftime('%d/%m/%Y %H:%M')}"
    return "- Último coordinador: no existe"


def _leer_resume() -> str:
    if RESUME_FILE.exists():
        return RESUME_FILE.read_text(encoding="utf-8")
    return "(RESUME.md no encontrado)"


def _chat_del_dia(fecha: datetime) -> str:
    prefix = f"chat_{fecha.strftime('%Y%m%d')}"
    chats = sorted(CHATS_DIR.glob(f"{prefix}_*.md"))
    if not chats:
        return "(sin chat para esta fecha)"
    ultimo = chats[-1]
    contenido = ultimo.read_text(encoding="utf-8")
    lineas = contenido.splitlines()
    if len(lineas) > 200:
        contenido = "\n".join(lineas[:200]) + f"\n\n... ({len(lineas) - 200} líneas más en {ultimo.name})"
    return f"### Chat: `{ultimo.name}`\n\n{contenido}"


def _avance_del_dia(fecha: datetime) -> str:
    """Busca el archivo de avance/logros del día en context/."""
    candidatos = list(CONTEXT.glob("lo que se logro*.txt"))
    if not candidatos:
        return ""
    # Tomar el más reciente
    ultimo = max(candidatos, key=lambda f: f.stat().st_mtime)
    contenido = ultimo.read_text(encoding="utf-8")
    return f"### Avance del día (`{ultimo.name}`)\n\n{contenido}"


def generar_resumen(fecha: datetime) -> Path:
    mes_dir = _mes_dir(fecha.year, fecha.month)
    out = mes_dir / f"resumen_{fecha.strftime('%d_%m_%Y')}.md"

    avance = _avance_del_dia(fecha)
    avance_sec = f"## Avance del día\n{avance}\n\n" if avance else ""

    contenido = (
        f"# Resumen del día — {fecha.strftime('%d/%m/%Y %H:%M')}\n\n"
        f"## Estado del sistema\n{_estado_sistema()}\n\n"
        f"## RESUME (actual)\n```\n{_leer_resume()}\n```\n\n"
        f"{avance_sec}"
        f"## Chat del día\n{_chat_del_dia(fecha)}\n"
    )
    out.write_text(contenido, encoding="utf-8")
    print(f"[organizador] ✅ {out}")
    return out   


def generar_indice(ano: int, mes: int) -> Path:
    mes_dir = _mes_dir(ano, mes)
    out = mes_dir / f"INDEX_{MESES[mes]}.md"

    archivos = sorted(mes_dir.iterdir())
    chats = [a for a in archivos if a.name.startswith("chat_") and a.suffix == ".md"]
    resumenes = [a for a in archivos if a.name.startswith("resumen_") and a.suffix == ".md"]
    otros = [a for a in archivos if a not in chats and a not in resumenes and a.suffix in EXTENSIONES_NOTA]

    lines = [f"# Índice — {MESES[mes]} {ano}\n"]

    if chats:
        lines.append(f"\n## Chats ({len(chats)})\n")
        for c in chats:
            lines.append(f"- `{c.name}` — {_tamano_humano(c)} — {c.name.replace('chat_', '').replace('.md', '')}")

    if resumenes:
        lines.append(f"\n## Resúmenes diarios ({len(resumenes)})\n")
        for r in resumenes:
            lines.append(f"- `{r.name}`")

    if otros:
        lines.append(f"\n## Otros ({len(otros)})\n")
        for o in otros:
            lines.append(f"- `{o.name}` — {_tamano_humano(o)}")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[organizador] ✅ {out}")
    return out


def generar_handoff() -> Path:
    """Genera HANDOFF.md listo para pegar al inicio de un chat nuevo."""
    hoy = datetime.now()
    mes_dir = _mes_dir(hoy.year, hoy.month)

    # Último resumen del día
    resumenes = sorted(mes_dir.glob("resumen_*.md"))
    ultimo_resumen = resumenes[-1].read_text(encoding="utf-8") if resumenes else "(sin resumen aún)"

    # RESUME
    resume = _leer_resume()

    # Estado
    estado = _estado_sistema()

    handoff = (
        f"# HANDOFF — {hoy.strftime('%d/%m/%Y')}\n\n"
        f"## Estado\n{estado}\n\n"
        f"## RESUME\n```\n{resume}\n```\n\n"
        f"## Último resumen\n{ultimo_resumen}\n"
    )

    out = BASE / "HANDOFF.md"
    out.write_text(handoff, encoding="utf-8")
    print(f"[organizador] ✅ {out}")
    print("[organizador] Copia el contenido de HANDOFF.md al inicio de tu próximo chat.")
    return out   


def main():
    parser = argparse.ArgumentParser(description="Organizador de notas")
    parser.add_argument("--mes", type=int, help="Mes (1-12) para generar índice")
    parser.add_argument("--ano", type=int, default=datetime.now().year)
    parser.add_argument("--handoff", action="store_true", help="Generar HANDOFF.md para nuevo chat")
    args = parser.parse_args()

    hoy = datetime.now()
    mes = args.mes or hoy.month

    generar_resumen(hoy)
    generar_indice(args.ano, mes)

    if args.handoff:
        generar_handoff()


if __name__ == "__main__":
    main()   
