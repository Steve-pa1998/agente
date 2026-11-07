import logging
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from config import PROJECT_ROOT

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., str]
    strict: bool = False

    def to_api(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                
            },
        }


def _resolve(path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    try:
        p.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        raise PermissionError(f"Ruta fuera del proyecto: {path}")
    return p


def list_files_in_dir(directory: str) -> str:
    target = _resolve(directory)
    if not target.exists():
        return f"ERROR: '{target}' no existe."
    files = [f.name for f in target.iterdir() if f.is_file()]
    return "\n".join(files) if files else "(carpeta vacía)"


def read_file(path: str) -> str:
    target = _resolve(path)
    if not target.exists():
        return f"ERROR: '{target}' no existe."
    return target.read_text(encoding="utf-8")[:5000]


def write_file(path: str, content: str) -> str:
    target = _resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"OK: {target} escrito."


def edit_file(path: str, old_text: str, new_text: str) -> str:
    target = _resolve(path)
    if not target.exists():
        return f"ERROR: '{target}' no existe."
    content = target.read_text(encoding="utf-8")
    if old_text not in content:
        return f"ERROR: old_text no encontrado en {target}"
    target.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
    return f"OK: editado {target}"


def search(query: str, directory: str = ".") -> str:
    target = _resolve(directory)
    results = []
    for ext in ("*.py", "*.md"):
        for f in target.rglob(ext):
            try:
                text = f.read_text(encoding="utf-8")
                for i, line in enumerate(text.splitlines(), 1):
                    if query.lower() in line.lower():
                        results.append(f"{f.name}:{i}: {line.strip()}")
            except (UnicodeDecodeError, PermissionError):
                continue
    return "\n".join(results[:30]) if results else "Sin resultados."


def run_command(command: str) -> str:
    cmd = command.strip()
    BLOCKED = {"rm", "del", "format", "shutdown", "taskkill", "reg"}
    ALLOWED_PREFIXES = ("python", "pip", "git", "dir", "type", "mkdir",
                        "ffmpeg", "ffprobe", "yt-dlp", "ollama")
    parts = shlex.split(cmd)
    if not parts:
        return "ERROR: comando vacío."
    if parts[0] in BLOCKED:
        return f"BLOQUEADO: '{parts[0]}'"
    if not any(cmd.lower().startswith(p) for p in ALLOWED_PREFIXES):
        return f"BLOQUEADO: '{parts[0]}' no en whitelist."
    try:
        r = subprocess.run(parts, capture_output=True, text=True, timeout=120, shell=False)
        return f"OUT: {r.stdout[:1500]}\nERR: {r.stderr[:500]}"
    except subprocess.TimeoutExpired:
        return "ERROR: timeout (120s)"


def process_vod(path: str) -> str:
    from clips_lib.clips_editor import process_vod as _pv
    return str(_pv(str(_resolve(path))))


def post_clip(path: str) -> str:
    from clips_lib.clips_poster import post as _post
    return str(_post(str(_resolve(path))))


def analyze_stream(path: str) -> str:
    from clips_lib.clips_editor import detect_silences, detect_highlights
    s = detect_silences(str(_resolve(path)))
    p = detect_highlights(str(_resolve(path)))
    return f"Silencios: {len(s)}, Picos: {len(p)}"


def report(summary: str) -> str:
    return f"Reporte: {summary}"


TOOLS: list[Tool] = [
    Tool("list_files_in_dir", "Lista archivos en una carpeta",
         {"type": "object", "properties": {"directory": {"type": "string"}}, "required": ["directory"]},
         list_files_in_dir),
    Tool("read_file", "Lee el contenido de un archivo (máx 5000 chars)",
         {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
         read_file),
    Tool("write_file", "Crea o sobrescribe un archivo",
         {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
         write_file),
    Tool("edit_file", "Reemplaza texto en un archivo",
         {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]},
         edit_file),
    Tool("search", "Busca texto en archivos .py y .md",
         {"type": "object", "properties": {"query": {"type": "string"}, "directory": {"type": "string"}}, "required": ["query"]},
         search),
    Tool("run", "Ejecuta un comando en la terminal (whitelist)",
         {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
         run_command),
    Tool("process_vod", "Procesa un VOD y genera clips",
         {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
         process_vod),
    Tool("post_clip", "Sube un clip a TikTok",
         {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
         post_clip),
    Tool("analyze_stream", "Analiza audio (silencios y picos)",
         {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
         analyze_stream),
    Tool("report", "Genera un reporte de lo que se hizo",
         {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]},
         report),
]

DISPATCH: dict[str, Callable[..., str]] = {t.name: t.handler for t in TOOLS}
TOOL_SCHEMAS: list[dict] = [t.to_api() for t in TOOLS]


def execute_tool(func_name: str, func_args: dict) -> str:
    handler = DISPATCH.get(func_name)
    if not handler:
        return f"Tool '{func_name}' no encontrada."
    try:
        return handler(**func_args)
    except PermissionError as e:
        return f"PERMISO DENEGADO: {e}"
    except Exception as e:
        logger.exception("Error en tool %s", func_name)
        return f"ERROR en {func_name}: {e}"


