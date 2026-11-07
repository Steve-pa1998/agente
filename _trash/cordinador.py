from agente_investigación import Investigador
from agente_planificador import Planificador

class Coordinador:
    def __init__(self):
        self.investigador = Investigador()
        self.planificador = Planificador()

    def ejecutar(self, tema: str, objetivo: str):
        print(f"=== Iniciando proceso para: {tema} ===\n")

        # 1. Investigar
        print("1. Investigando...")
        investigacion = self.investigador.investigar(tema)
        info = investigacion.get("respuesta", "")

        # 2. Planificar
        print("\n2. Generando plan...")
        plan = self.planificador.crear_plan(
            informacion=info,
            objetivo=objetivo,
            usar_investigaciones=True
        )

        print("\n=== Proceso terminado ===")
        return plan

if __name__ == "__main__":
    coord = Coordinador()
    coord.ejecutar(
        tema="Tácticas de engagement y crecimiento en TikTok e Instagram para generar leads",
        objetivo="Crecer en redes sociales para obtener leads y clientes potenciales"
    )
