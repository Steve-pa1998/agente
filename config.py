import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).parent))
AGENTS_DIR = PROJECT_ROOT / "agents"
MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")
BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "10"))


def validate_api_key() -> str:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY no está definida en el entorno.")
    return key
