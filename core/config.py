from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Ruta base del proyecto
    base_dir: Path = Path(__file__).resolve().parent.parent

    # Umbral de mensajes antes de rotar
    max_messages_per_session: int = 25

    # Cuánto contexto (tokens aprox) llevar al nuevo chat
    handoff_context_tokens: int = 2048

    # Ruta de sesiones guardadas
    sessions_dir: Path = Path(__file__).resolve().parent.parent / "data" / "sessions"

    # ChromaDB
    chroma_path: Path = Path(__file__).resolve().parent.parent / "chroma.sqlite3"
    chroma_collection: str = "agent_memory"

    class Config:
        env_file = ".env"

settings = Settings()
settings.sessions_dir.mkdir(parents=True, exist_ok=True)   
