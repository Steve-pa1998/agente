import os
import json
from datetime import datetime
from langchain_ollama import ChatOllama

class Planificador:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:7b",
            temperature=0.4,
            num_ctx=4096,
            num_predict=1200,
        )
        self.carpeta_planes = "planes"
        self.historial_path = "historial_planes.json"
        self.historial_investigaciones = "historial_investigaciones.json"
        os.makedirs(self.carpeta_planes, exist_ok=True)

    def cargar_investigaciones(self, limite: int = 3) -> str:
        """Carga las últimas investigaciones guardadas."""
        if not os.path.exists(self.historial_investigaciones):
            return "No hay investigaciones previas."
        
        try:
            with open(self.historial_investigaciones, "r", encoding="utf-8") as f:
                investigaciones = json.load(f)
            
            if not investigaciones:
                return "No hay investigaciones previas."
            
            # Tomar las más recientes
            recientes = investigaciones[-limite:]
            texto = ""
            for inv in recientes:
                texto += f"- Pregunta: {inv.get('pregunta', 'N/A')}\n"
                texto += f"  Resumen: {inv.get('respuesta', '')[:500]}...\n\n"
            return texto
        except Exception as e:
            return f"Error cargando investigaciones: {e}"

    def crear_plan(self, informacion: str = "", objetivo: str = "", usar_investigaciones: bool = True) -> dict:
        print("Generando plan...\n")

        contexto_investigaciones = ""
        if usar_investigaciones:
            contexto_investigaciones = self.cargar_investigaciones()
            print("Investigaciones previas cargadas.\n")

        prompt = f"""Eres un agente planificador práctico enfocado en crecimiento en redes sociales, generación de leads y clientes.

Información adicional proporcionada:
{informacion if informacion else "Ninguna"}

Investigaciones previas:
{contexto_investigaciones}

Objetivo:
{objetivo if objetivo else "No especificado"}

Crea un plan claro y accionable. Incluye:
- Pasos numerados
- Ideas de contenido (incluyendo engagement: comentarios, preguntas, encuestas)
- Posibles riesgos
- Al final pregunta si se aprueba el plan
"""

        respuesta = self.llm.invoke(prompt)
        plan_texto = respuesta.content

        resultado = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "objetivo": objetivo,
            "informacion": informacion,
            "uso_investigaciones": usar_investigaciones,
            "plan": plan_texto,
            "aprobado": None
        }

        print("=" * 60)
        print(plan_texto)
        print("=" * 60)

        aprobacion = input("\n¿Apruebas este plan? (sí / no): ").strip().lower()
        resultado["aprobado"] = aprobacion in ("sí", "si", "s", "yes", "y")

        # Guardar
        nombre = objetivo[:40] if objetivo else "plan_sin_objetivo"
        nombre = "".join(c if c.isalnum() or c in " _-" else "_" for c in nombre)
        ruta = os.path.join(self.carpeta_planes, f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(plan_texto)

        historial = []
        if os.path.exists(self.historial_path):
            try:
                with open(self.historial_path, "r", encoding="utf-8") as f:
                    historial = json.load(f)
            except:
                historial = []
        historial.append(resultado)
        with open(self.historial_path, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)

        print(f"\nPlan guardado en: {ruta}")
        return resultado

if __name__ == "__main__":
    p = Planificador()
    p.crear_plan(
        objetivo="Crecer en redes sociales para generar leads y clientes potenciales",
        usar_investigaciones=True
    )
