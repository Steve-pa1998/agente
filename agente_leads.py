import os
import json
from datetime import datetime
from langchain_ollama import ChatOllama

class AgenteLeads:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:7b",
            temperature=0.6,
            num_ctx=4096,
            num_predict=1000,
        )
        self.carpeta = "leads"
        self.historial_path = "historial_leads.json"
        self.historial_planes = "historial_planes.json"
        os.makedirs(self.carpeta, exist_ok=True)

    def cargar_ultimo_plan(self) -> str:
        if not os.path.exists(self.historial_planes):
            return ""
        try:
            with open(self.historial_planes, "r", encoding="utf-8") as f:
                planes = json.load(f)
            for plan in reversed(planes):
                if plan.get("aprobado"):
                    return plan.get("plan", "")[:1500]
            return ""
        except:
            return ""

    def generar_estrategia(self, nicho: str = "", objetivo: str = "") -> dict:
        print("Generando estrategia de leads...\n")
        plan = self.cargar_ultimo_plan()

        prompt = f"""Eres un experto en generación de leads para TikTok e Instagram.

Nicho: {nicho or "Contenido y stream"}
Objetivo: {objetivo or "Conseguir clientes potenciales"}

Plan de referencia:
{plan if plan else "Ninguno"}

Genera una estrategia práctica con:
1. Formas de captar leads
2. CTAs concretos
3. Ideas de contenido para leads
4. Cómo dar seguimiento
5. Oferta o siguiente paso simple
"""

        respuesta = self.llm.invoke(prompt)
        estrategia = respuesta.content

        resultado = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "nicho": nicho,
            "objetivo": objetivo,
            "estrategia": estrategia
        }

        nombre = "".join(c if c.isalnum() or c in " _-" else "_" for c in (nicho or "leads")[:40])
        ruta = os.path.join(self.carpeta, f"{nombre}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(estrategia)

        historial = []
        if os.path.exists(self.historial_path):
            try:
                with open(self.historial_path, "r", encoding="utf-8") as f:
                    historial = json.load(f)
            except:
                pass
        historial.append(resultado)
        with open(self.historial_path, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)

        print(f"Estrategia guardada en: {ruta}\n")
        print("=" * 60)
        print(estrategia)
        print("=" * 60)
        return resultado

if __name__ == "__main__":
    AgenteLeads().generar_estrategia(
        nicho="Contenido en stream y redes sociales",
        objetivo="Leads y clientes potenciales"
    )
