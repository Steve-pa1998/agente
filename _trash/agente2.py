from datetime import datetime
from langchain_ollama import ChatOllama

class Planificador:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:7b",
            temperature=0.4,
            num_ctx=8192,
        )

    def crear_plan(self, informacion: str, objetivo: str = "") -> str:
        """
        Recibe información (por ejemplo de una investigación)
        y genera un plan claro. Siempre pide confirmación.
        """
        print("Generando plan...\n")

        prompt = f"""Eres un agente planificador.
Tu trabajo es tomar información y convertirla en un plan claro y accionable.

Información recibida:
{informacion}

Objetivo (si se proporcionó):
{objetivo if objetivo else "No especificado"}

Instrucciones:
- Organiza la información.
- Propón pasos concretos y ordenados.
- Sé realista.
- Al final pregunta explícitamente si el usuario aprueba el plan o quiere cambios.
"""

        respuesta = self.llm.invoke(prompt)
        plan = respuesta.content

        print("=" * 60)
        print(plan)
        print("=" * 60)

        # Consulta al usuario
        aprobacion = input("\n¿Apruebas este plan? (sí / no / cambios): ").strip().lower()

        if aprobacion in ("sí", "si", "s", "yes", "y"):
            print("\nPlan aprobado.")
            return plan
        else:
            print("\nPlan no aprobado. Puedes pedir cambios o generar uno nuevo.")
            return f"PLAN NO APROBADO\n\n{plan}"

# Prueba rápida
if __name__ == "__main__":
    planificador = Planificador()
    
    info_ejemplo = """
    Los algoritmos de TikTok priorizan el tiempo de visualización, 
    interacciones rápidas (likes, comentarios, shares) y la finalización del video.
    El contenido nuevo se prueba con un grupo pequeño antes de escalar.
    """
    
    planificador.crear_plan(
        informacion=info_ejemplo,
        objetivo="Crear una estrategia de contenido para crecer en TikTok"
    )
