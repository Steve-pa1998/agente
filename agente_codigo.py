import json
import os
from datetime import datetime
from openai import OpenAI
from ddgs import DDGS

# ==================== CONFIGURACIÓN GROQ (GRATIS) ====================
# Pega tu API key aquí o usa variable de entorno
GROQ_API_KEY = "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"  # <-- REEMPLAZA ESTO

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# Modelos recomendados en el free tier:
# "llama-3.3-70b-versatile"     → bueno y equilibrado
# "openai/gpt-oss-120b"         → más potente (si está disponible)
# "llama-3.1-8b-instant"        → más rápido y con más límite diario
MODEL = "openai/gpt-oss-120b"

KNOWLEDGE_FILE = "agent_knowledge.json"
PROMPT_FILE = "system_prompt.txt"

DEFAULT_SYSTEM_PROMPT = """Eres un agente autónomo experto en construir agentes de IA.
Tu misión es investigar continuamente las mejores técnicas, frameworks, patrones y herramientas para crear agentes de IA potentes, autónomos y auto-mejorables.
Debes ser preciso y enfocarte en soluciones prácticas y actualizadas.
"""

class AutonomousAIAgentResearcher:
    def __init__(self):
        self.knowledge = []
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.load_state()

    def load_state(self):
        if os.path.exists(KNOWLEDGE_FILE):
            with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                self.knowledge = json.load(f)
        if os.path.exists(PROMPT_FILE):
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()

    def save_state(self):
        with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(self.system_prompt)

    def search_web(self, query: str, max_results: int = 5) -> list:
        print(f"🔍 Buscando: {query}")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            return results
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            return []

    def llm(self, messages: list, temperature: float = 0.3) -> str:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=1500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error con Groq: {e}")
            return "Error al llamar al modelo."

    def research(self, topic: str):
        results = self.search_web(topic)
        if not results:
            print("No se encontraron resultados.")
            return

        results_text = "\n\n".join([
            f"Título: {r.get('title', '')}\nURL: {r.get('href', '')}\nSnippet: {r.get('body', '')[:400]}"
            for r in results
        ])

        prompt = f"""Analiza estos resultados sobre "{topic}" y extrae las mejores prácticas, técnicas y consejos útiles para construir agentes de IA.

Resultados:
{results_text}

Genera un resumen claro con técnicas clave, frameworks y consejos prácticos.
"""

        summary = self.llm([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ])

        entry = {
            "topic": topic,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "sources_count": len(results)
        }
        self.knowledge.append(entry)
        self.save_state()
        
        print(f"✅ Aprendizaje guardado sobre: {topic}\n")
        print(summary[:600] + "...\n")

    def optimize_self(self):
        if len(self.knowledge) < 2:
            print("Necesita más conocimiento para optimizarse.")
            return

        recent_knowledge = "\n\n".join([
            f"Tema: {k['topic']}\n{k['summary']}"
            for k in self.knowledge[-6:]
        ])

        optimization_prompt = f"""Reescribe este system prompt para que sea mejor, incorporando el conocimiento reciente:

Prompt actual:
{self.system_prompt}

Conocimiento reciente:
{recent_knowledge}

Devuelve únicamente el nuevo system prompt mejorado.
"""

        new_prompt = self.llm([
            {"role": "system", "content": "Eres un experto optimizando prompts de agentes de IA."},
            {"role": "user", "content": optimization_prompt}
        ], temperature=0.4)

        print("\n🔄 Optimizando system prompt...")
        print(f"Nuevo prompt (inicio):\n{new_prompt[:400]}...\n")

        self.system_prompt = new_prompt
        self.save_state()
        print("✅ Prompt optimizado.\n")

    def decide_next_research(self) -> str:
        knowledge_summary = "\n".join([k["topic"] for k in self.knowledge[-8:]]) or "Ninguno todavía"

        prompt = f"""Basado en lo que ya investigaste:
{knowledge_summary}

¿Cuál es el siguiente tema más importante que deberías investigar para mejorar como constructor de agentes de IA?
Devuelve solo el tema (una frase).
"""

        next_topic = self.llm([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ], temperature=0.6)

        return next_topic.strip()

    def run(self, iterations: int = 5, optimize_every: int = 2):
        print("🚀 Agente autónomo con Groq (gratis)\n")
        for i in range(1, iterations + 1):
            print(f"\n{'='*60}")
            print(f"ITERACIÓN {i}/{iterations}")
            print(f"{'='*60}")

            topic = self.decide_next_research()
            print(f"📌 Tema: {topic}")
            self.research(topic)

            if i % optimize_every == 0:
                self.optimize_self()

        print("\n🎉 Terminado. Revisa agent_knowledge.json y system_prompt.txt")


if __name__ == "__main__":
    agent = AutonomousAIAgentResearcher()
    agent.run(iterations=5, optimize_every=2)
