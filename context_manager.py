from collections import deque

class ContextManager:
    def __init__(self, max_msgs: int = 25):
        self.max_msgs = max_msgs
        self._msgs: deque = deque(maxlen=max_msgs)

    def add(self, msg: dict):
        self._msgs.append(msg)

    def rotate(self) -> list[dict]:
        return list(self._msgs)

    def clear(self):
        self._msgs.clear()

    @property
    def size(self) -> int:
        return len(self._msgs)

    def to_context(self) -> str | None:
        if not self._msgs:
            return None
        lines = []
        for m in self._msgs:
            line = f"[{m.get('ts', '?')}] {m.get('agente', '?')}"
            if m.get('estado'):
                line += f" - {m['estado']}"
            if m.get('problema'):
                line += f" Problema: {m['problema']}"
            lines.append(line)
        return "\n".join(lines)   
