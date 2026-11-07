"""
Social Media Growth System
- Local Ollama
- Human approval of plan before execution
- Structured outputs
- Easy to extend
"""

from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
import logging
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────
# Configuration (change model here later)
# ────────────────────────────────────────────────
MODEL_NAME = "qwen2.5:7b"          # Easy to swap later
TEMPERATURES = {
    "research": 0.2,
    "plan": 0.1,
    "content": 0.7,
    "leads": 0.4,
    "engagement": 0.6,
}

def get_llm(role: str = "plan") -> ChatOllama:
    return ChatOllama(
        model=MODEL_NAME,
        temperature=TEMPERATURES.get(role, 0.3),
        num_ctx=8192,
        num_predict=1024,
    )

# ────────────────────────────────────────────────
# Structured Outputs (reliability)
# ────────────────────────────────────────────────
class InvestigacionResult(BaseModel):
    resumen: str = Field(description="Resumen ejecutivo")
    insights_clave: list[str]
    oportunidades: list[str]
    riesgos_o_consideraciones: list[str]

class PlanResult(BaseModel):
    aprobado_sugerido: bool = Field(description="¿El plan es sólido?")
    razon: str
    plan_detallado: str
    pilares_contenido: list[str]
    tacticas_prioritarias: list[str]
    metricas_exito: list[str]
    timeline_sugerido: str

class ContenidoResult(BaseModel):
    ideas_contenido: list[str]
    formatos_recomendados: list[str]
    hooks_sugeridos: list[str]
    ejemplos_de_titulos: list[str]

class LeadsResult(BaseModel):
    estrategia: str
    lead_magnets: list[str]
    canales_prioritarios: list[str]
    secuencia_sugerida: list[str]

class EngagementResult(BaseModel):
    ideas_engagement: list[str]
    formatos_interactivos: list[str]
    community_tactics: list[str]

class ApprovalDecision(BaseModel):
    approved: bool
    feedback: str = ""

# ────────────────────────────────────────────────
# Shared State
# ────────────────────────────────────────────────
class SocialMediaState(TypedDict):
    tema: str
    objetivo: str
    investigacion: dict | None
    plan: dict | None
    human_approved: bool | None
    contenido: dict | None
    estrategia_leads: dict | None
    ideas_engagement: dict | None
    messages: Annotated[list, add_messages]
    status: str

# ────────────────────────────────────────────────
# Nodes
# ────────────────────────────────────────────────
def investigador_node(state: SocialMediaState) -> dict:
    logger.info("→ Investigador")
    llm = get_llm("research")
    structured = llm.with_structured_output(InvestigacionResult)

    prompt = f"""
    Eres un investigador experto en crecimiento orgánico de TikTok e Instagram.
    Tema: {state['tema']}
    Objetivo: {state['objetivo']}

    Investiga y entrega insights accionables, tendencias actuales, y oportunidades
    reales para generar engagement y leads.
    """
    result = structured.invoke(prompt)
    return {
        "investigacion": result.model_dump(),
        "messages": [HumanMessage(content=f"[Investigación] {result.resumen[:300]}...")],
        "status": "investigacion_done",
    }

def planificador_node(state: SocialMediaState) -> dict:
    logger.info("→ Planificador")
    llm = get_llm("plan")
    structured = llm.with_structured_output(PlanResult)

    inv = state.get("investigacion") or {}
    prompt = f"""
    Eres un estratega senior de marketing en redes sociales.

    Investigación previa:
    {json.dumps(inv, ensure_ascii=False, indent=2)}

    Objetivo: {state['objetivo']}

    Crea un plan claro, realista y accionable.
    Indica si lo recomiendas para continuar (aprobado_sugerido).
    """
    result = structured.invoke(prompt)
    return {
        "plan": result.model_dump(),
        "messages": [HumanMessage(content=f"[Plan] {result.razon}")],
        "status": "plan_ready",
    }

def approval_node(state: SocialMediaState) -> dict:
    """Human approval gate using interrupt()."""
    logger.info("→ Esperando aprobación humana")
    plan = state.get("plan") or {}

    decision = interrupt({
        "question": "¿Apruebas este plan para continuar?",
        "plan": plan,
        "options": ["approve", "reject"],
    })

    # When resumed, `decision` is whatever you pass to Command(resume=...)
    approved = False
    feedback = ""
    if isinstance(decision, dict):
        approved = decision.get("approved", False)
        feedback = decision.get("feedback", "")
    elif isinstance(decision, str):
        approved = decision.lower() in ("approve", "yes", "si", "sí", "true")

    return {
        "human_approved": approved,
        "messages": [HumanMessage(content=f"[Aprobación] {'Aprobado' if approved else 'Rechazado'} — {feedback}")],
        "status": "approved" if approved else "rejected",
    }

def contenido_node(state: SocialMediaState) -> dict:
    logger.info("→ Generador de Contenido")
    llm = get_llm("content")
    structured = llm.with_structured_output(ContenidoResult)
    plan = state.get("plan") or {}
    prompt = f"Tema: {state['tema']}\nPlan aprobado:\n{json.dumps(plan, ensure_ascii=False, indent=2)}\n\nGenera ideas de contenido concretas, hooks y formatos."
    result = structured.invoke(prompt)
    return {"contenido": result.model_dump(), "status": "contenido_done"}

def leads_node(state: SocialMediaState) -> dict:
    logger.info("→ Estrategia de Leads")
    llm = get_llm("leads")
    structured = llm.with_structured_output(LeadsResult)
    plan = state.get("plan") or {}
    prompt = f"Objetivo: {state['objetivo']}\nPlan:\n{json.dumps(plan, ensure_ascii=False, indent=2)}\n\nDiseña una estrategia de generación de leads."
    result = structured.invoke(prompt)
    return {"estrategia_leads": result.model_dump(), "status": "leads_done"}

def engagement_node(state: SocialMediaState) -> dict:
    logger.info("→ Ideas de Engagement")
    llm = get_llm("engagement")
    structured = llm.with_structured_output(EngagementResult)
    prompt = f"Tema: {state['tema']}\nGenera ideas de engagement y community building."
    result = structured.invoke(prompt)
    return {"ideas_engagement": result.model_dump(), "status": "completed"}

# ────────────────────────────────────────────────
# Routing
# ────────────────────────────────────────────────
def route_after_approval(state: SocialMediaState) -> Literal["contenido", END]:
    if state.get("human_approved"):
        return "contenido"
    return END

# ────────────────────────────────────────────────
# Build Graph
# ────────────────────────────────────────────────
def build_graph():
    builder = StateGraph(SocialMediaState)

    builder.add_node("investigador", investigador_node)
    builder.add_node("planificador", planificador_node)
    builder.add_node("approval", approval_node)
    builder.add_node("contenido", contenido_node)
    builder.add_node("leads", leads_node)
    builder.add_node("engagement", engagement_node)

    builder.add_edge(START, "investigador")
    builder.add_edge("investigador", "planificador")
    builder.add_edge("planificador", "approval")
    builder.add_conditional_edges("approval", route_after_approval)
    builder.add_edge("contenido", "leads")
    builder.add_edge("leads", "engagement")
    builder.add_edge("engagement", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

# ────────────────────────────────────────────────
# Usage
# ────────────────────────────────────────────────
def run_until_approval(tema: str, objetivo: str, thread_id: str = "sm-001"):
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    initial = {
        "tema": tema,
        "objetivo": objetivo,
        "investigacion": None,
        "plan": None,
        "human_approved": None,
        "contenido": None,
        "estrategia_leads": None,
        "ideas_engagement": None,
        "messages": [],
        "status": "started",
    }

    result = graph.invoke(initial, config)
    return result, config, graph

def resume_with_decision(graph, config, approved: bool, feedback: str = ""):
    decision = {"approved": approved, "feedback": feedback}
    return graph.invoke(Command(resume=decision), config)

# ────────────────────────────────────────────────
# Example
# ────────────────────────────────────────────────
if __name__ == "__main__":
    tema = "Tácticas de engagement y crecimiento en TikTok e Instagram para generar leads"
    objetivo = "Crecer en redes sociales para obtener leads y clientes potenciales"

    print("=== Fase 1: Investigación + Plan ===")
    result, config, graph = run_until_approval(tema, objetivo)

    if result.get("__interrupt__"):
        plan = result["plan"]
        print("\n" + "="*60)
        print("PLAN GENERADO — REVISA ANTES DE CONTINUAR")
        print("="*60)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        print("="*60)

        # Simulate human approval (in real use you would ask the user)
        user_input = input("\n¿Apruebas el plan? (si/no): ").strip().lower()
        approved = user_input in ("si", "sí", "yes", "y", "approve")

        print("\n=== Fase 2: Continuando tras aprobación ===")
        final = resume_with_decision(graph, config, approved, feedback="Aprobado por usuario")

        print("\n=== RESULTADO FINAL ===")
        print(f"Status: {final.get('status')}")
        if final.get("contenido"):
            print("\n--- Contenido ---")
            print(json.dumps(final["contenido"], ensure_ascii=False, indent=2))
        if final.get("estrategia_leads"):
            print("\n--- Leads ---")
            print(json.dumps(final["estrategia_leads"], ensure_ascii=False, indent=2))
        if final.get("ideas_engagement"):
            print("\n--- Engagement ---")
            print(json.dumps(final["ideas_engagement"], ensure_ascii=False, indent=2))
    else:
        print("No se generó interrupt. Resultado:", result)
