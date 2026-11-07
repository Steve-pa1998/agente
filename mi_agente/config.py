cd C:\Users\Steve\Desktop\agente\mi_agente

import os

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

PATHWAYS = {
    "default": {"temp": 0.7, "max_tokens": 1024},
    "code":    {"temp": 0.2, "max_tokens": 2048},
    "data":    {"temp": 0.1, "max_tokens": 1024},
    "sales":   {"temp": 0.6, "max_tokens": 1024},
}

GUARDRAILS = {
    "max_input_chars": 4000,
    "max_output_chars": 8000,
    "max_calls_per_minute": 10,
    "blocked_topics": ["contrabando", "arma", "explosivo"],
}   