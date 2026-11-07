from agente_planificador import Planificador
from agente_calendario import AgenteCalendario
from agente_stream import AgenteStream

def flujo_contenido_semanal(tema: str, objetivo: str):
    print("=== Flujo de contenido y stream ===\n")

    # 1. Plan
    planificador = Planificador()
    plan = planificador.crear_plan(
        informacion=f"Tema principal: {tema}",
        objetivo=objetivo,
        usar_investigaciones=True
    )

    if not plan.get("aprobado"):
        print("Plan no aprobado. Detenido.")
        return

    # 2. Calendario
    print("\n--- Generando calendario ---")
    calendario = AgenteCalendario()
    calendario.crear_calendario(tema)

    # 3. Ideas de stream
    print("\n--- Generando ideas de stream ---")
    stream = AgenteStream()
    stream.generar_ideas(tema)

    print("\n=== Listo ===")

if __name__ == "__main__":
    flujo_contenido_semanal(
        tema="Crecimiento en redes y generación de leads",
        objetivo="Plan semanal de contenido + ideas para stream"
    )
