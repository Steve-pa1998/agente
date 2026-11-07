import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path

from .config import settings


@dataclass
class Message:
    role: str          # "user" | "assistant" | "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ContextManager:
    """
    Trackea el chat actual y decide cuándo rotar.
    La rotación es atómica: un solo mensaje dispara todo.
    """

    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or uuid.uuid4().hex[:12]
        self.messages: list[Message] = []
        self._handoff = None  # lazy import

    @property
    def should_rotate(self) -> bool:
        return len(self.messages) >= settings.max_messages_per_session

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def get_history(self) -> list[dict]:
        """Formato listo para enviar a la API."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def rotate(self, llm_call) -> str:
        """
        Operación atómica de rotación.
        Devuelve el ID de la nueva sesión.
        Todo ocurre en UN solo mensaje de handoff.
        """
        from .handoff import perform_handoff

        # 1. Guardar sesión actual
        self._save_session()

        # 2. Generar el mensaje de handoff (único)
        handoff_message = perform_handoff(
            session_id=self.session_id,
            messages=self.messages,
            llm_call=llm_call,
        )

        # 3. Inicializar nueva sesión con ese mensaje
        new_session_id = uuid.uuid4().hex[:12]
        self.session_id = new_session_id
        self.messages = [Message(role="system", content=handoff_message)]

        return new_session_id

    def _save_session(self) -> Path:
        path = settings.sessions_dir / f"{self.session_id}.json"
        data = {
            "session_id": self.session_id,
            "created": self.messages[0].timestamp if self.messages else None,
            "ended": datetime.now(timezone.utc).isoformat(),
            "message_count": len(self.messages),
            "messages": [m.__dict__ for m in self.messages],
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path   
