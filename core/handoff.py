"""
Handoff atómico: genera UN solo mensaje que contiene
todo el contexto necesario para que un chat nuevo
continúe donde el anterior se quedó, con acceso al index.
"""

import json
from pathlib import Path

from .config import settings
from .context_manager import Message


def perform_handoff(
    session_id: str,
    messages: list[Message],
    llm_call,  # callable(prompt: str) -> str
) -> str:
    """
    Genera el mensaje de handoff.
    Este ES el primer mensaje del nuevo chat.
    """
    # --- Extraer puntos clave del index (top-k relevante) ---
    index_context = _fetch_relevant_index(messages)

    # --- Prompt para que el LLM resuma ---
    summary_prompt = f"""Eres un sistema de handoff. Resume la siguiente conversación
en un mensaje de contexto compacto (máx {settings.handoff_context_tokens} tokens).

Incluye OBLIGATORIAMENTE:
1. **Objetivo actual**: qué se está resolviendo
2. **Estado**: dónde quedó, qué falta
3. **Decisiones tomadas**: opciones descartadas y por qué
4. **Próximos pasos**: 1-3 acciones concretas
5. **Contexto del index**: (se adjunta abajo)

NO incluyas saludos, despedidas ni metacomentarios.
Solo el contexto operativo.

--- CONVERSACIÓN ---
{format_for_summary(messages)}

--- INDEX RELEVANTE ---
{index_context or '(sin resultados)'}

---
Resumen:
"""

    summary = llm_call(summary_prompt)

    # --- Ensamblar el mensaje final ---
    handoff = f"""[HANDOFF — sesión {session_id} → nueva]
Fecha: {messages[-1].timestamp if messages else 'N/A'}
Mensajes anteriores: {len(messages)}

{summary}

[INSTRUCCIÓN]
Tienes acceso al index vectorial (colección: {settings.chroma_collection}).
Úsalo para recuperar detalles si el resumen es insuficiente.
Continúa la conversación desde donde quedó, sin pedir confirmación."""

    return handoff


def _fetch_relevant_index(messages: list[Message], top_k: int = 5) -> str:
    """Busca en ChromaDB lo más relevante a la conversación actual."""
    try:
        from ..index.chroma import get_collection
        import chromadb

        client = chromadb.PersistentClient(path=str(settings.chroma_path))
        col = client.get_collection(settings.chroma_collection)

        # Usar el último mensaje como query
        query = messages[-1].content if messages else ""
        results = col.query(query_texts=[query], n_results=top_k)

        if not results["documents"] or not results["documents"][0]:
            return ""

        lines = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            lines.append(f"- {doc[:200]}")
        return "\n".join(lines)
    except Exception:
        return ""


def format_for_summary(messages: list[Message], max_messages: int = 50) -> str:
    """Formatea mensajes para el prompt de resumen (recorta si es largo)."""
    msgs = messages[-max_messages:]  # últimos N
    lines = []
    for m in msgs:
        lines.append(f"[{m.role}] {m.content[:500]}")
    return "\n".join(lines)   
