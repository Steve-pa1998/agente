from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 1. Structured outputs (reliability)
# ──────────────────────────────────────────────
class Investigacion(BaseModel):
    resumen: str
    insights_clave: list[str]
    oportunidades: list[str]

class Plan(BaseModel):
    aprobado_por_modelo: bool
    razon: str
    plan_detallado: str
    pilares: list[str]
    tacticas: list[str]
    metricas: list[str]

class Contenido(BaseModel):
    ideas: list[str]
    formatos: list[str]
    hooks: list[str]

class Leads(BaseModel):
    estrategia: str
    canales: list[str]
    lead_magnets: list[str]

class Engagement(BaseModel):
    ideas: list[str]
    tipos_interactivos: list[str]

# ──────────────────────────────────────────────
# 2. Shared state
# ──────────────────────────────────────────────
class State(TypedDict):
    tema: str
    objetivo: str
    investigacion: Optional[dict]
    plan: Optional[dict]
    humano_aprobo: bool
    contenido: Optional[dict]
    leads: Optional[dict]
    engagement: Optional[dict]

# ──────────────────────────────────────────────
# 3. LLM factory (easy to swap later)
# ──────────────────────────────────────────────
def get_llm(model: str = "qwen2.5:7b", temperature: float = 0.3):
    return ChatOllama(
        model=model,
        temperature=temperature,
        num_ctx=8192,
        num_predict=1024,
    )

# ──────────────────────────────────────────────
# 4. Nodes
# ──────────────────────────────────────────────
def investigador(state: State) -> dict:
    logger.info("Investigador")
    llm = get_llm(temperature=0.2)
    structured = llm.with_structured_output(Investigacion)
    result = structured.invoke(
        f"Investiga tácticas de crecimiento y leads en TikTok e Instagram.\n"
        f"Tema: {state['tema']}\nObjetivo: {state['objetivo']}"
    )
    return {"investigacion": result.model_dump()}

def planificador(state: State) -> dict:
    logger.info("Planificador")
    llm = get_llm(temperature=0.1)
    structured = llm.with_structured_output(Plan)
    inv = state.get("investigacion") or {}
    result = structured.invoke(
        f"Crea un plan de crecimiento en redes sociales.\n"
        f"Investigación: {inv}\nObjetivo: {state['objetivo']}\n"
        f"Sé crítico con la aprobación."
    )
    return {"plan": result.model_dump()}

def human_approval(state: State) -> dict:
    """Pauses the graph so a human can approve or reject the plan."""
    plan = state.get("plan", {})
    print("\n" + "="*60)
    print("PLAN GENERADO — REVISIÓN HUMANA")
    print("="*60)
    print(plan.get("plan_detallado", "No plan"))
    print("\nPilares:", plan.get("pilares"))
    print("Tácticas:", plan.get("tacticas"))
    print("="*60)

    # This pauses execution until you resume the graph
    decision = interrupt(
        "¿Aprobar este plan? Responde 'si' o 'no' al reanudar."
    )
    approved = str(decision).strip().lower() in ("si", "sí", "yes", "y", "approve")
    logger.info(f"Human decision: {approved}")
    return {"humano_aprobo": approved}

def contenido(state: State) -> dict:
    logger.info("Contenido")
    llm = get_llm(temperature=0.7)
    structured = llm.with_structured_output(Contenido)
    result = structured.invoke(
        f"Tema: {state['tema']}\nPlan: {state.get('plan')}\n"
        f"Genera ideas de contenido concretas."
    )
    return {"contenido": result.model_dump()}

def leads(state: State) -> dict:
    logger.info("Leads")
    llm = get_llm(temperature=0.4)
    structured = llm.with_structured_output(Leads)
    result = structured.invoke(
        f"Tema: {state['tema']}\nPlan: {state.get('plan')}\n"
        f"Diseña estrategia de generación de leads."
    )
    return {"leads": result.model_dump()}

def engagement(state: State) -> dict:
    logger.info("Engagement")
    llm = get_llm(temperature=0.6)
    structured = llm.with_structured_output(Engagement)
    result = structured.invoke(
        f"Tema: {state['tema']}\nGenera ideas de engagement."
    )
    return {"engagement": result.model_dump()}

# ──────────────────────────────────────────────
# 5. Routing
# ──────────────────────────────────────────────
def route_after_approval(state: State) -> Literal["contenido", END]:
    if state.get("humano_aprobo"):
        return "contenido"
    return END

# ──────────────────────────────────────────────
# 6. Build graph
# ──────────────────────────────────────────────
def build_graph():
    builder = StateGraph(State)

    builder.add_node("investigador", investigador)
    builder.add_node("planificador", planificador)
    builder.add_node("human_approval", human_approval)
    builder.add_node("contenido", contenido)
    builder.add_node("leads", leads)
    builder.add_node("engagement", engagement)

    builder.add_edge(START, "investigador")
    builder.add_edge("investigador", "planificador")
    builder.add_edge("planificador", "human_approval")
    builder.add_conditional_edges("human_approval", route_after_approval)
    builder.add_edge("contenido", "leads")
    builder.add_edge("leads", "engagement")
    builder.add_edge("engagement", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

# ──────────────────────────────────────────────
# 7. Usage
# ──────────────────────────────────────────────
def run(tema: str, objetivo: str, thread_id: str = "run-1"):
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    initial = {
        "tema": tema,
        "objetivo": objetivo,
        "investigacion": None,
        "plan": None,
        "humano_aprobo": False,
        "contenido": None,
        "leads": None,
        "engagement": None,
    }

    # First invocation runs until the interrupt
    result = graph.invoke(initial, config)

    # If it paused for approval, resume with the human decision
    if result.get("__interrupt__"):
        decision = input("\n¿Aprobar el plan? (si/no): ")
        result = graph.invoke(decision, config)

    return result

if __name__ == "__main__":
    final = run(
        tema="Tácticas de engagement y crecimiento en TikTok e Instagram para generar leads",
        objetivo="Crecer en redes sociales para obtener leads y clientes potenciales",
    )
    print("\n=== RESULTADO FINAL ===")
    print(final)
