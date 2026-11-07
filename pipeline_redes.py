#┌─────────────────────────────────────────────────────────────────┐
#│  AGENTE 1: RECOLECTOR (1 por red, o uno que itera)              │
#│  Obtiene métricas/insights de: X, FB, IG, TikTok                │
#│  → Output: dict con datos por red                                │
#└──────────────────────────┬──────────────────────────────────────┘
#                           ▼
#┌─────────────────────────────────────────────────────────────────┐
#│  AGENTE 2: ESTRATEGA                                            │
#│  Recibe los datos, analiza qué funcionó, propone:               │
#│  - Qué red priorizar                                             │
#│  - Tipo de contenido (texto, imagen, video)                     │
#│  - Ángulo de publicidad / CTA                                    │
#│  → Output: plan de publicación por red                           │
#└──────────────────────────┬──────────────────────────────────────┘
#                           ▼
#┌─────────────────────────────────────────────────────────────────┐
#│  AGENTE 3: EJECUTORES (1 por red)                               │
#│  Recibe el plan específico para su red y publica                │
#│  → Output: confirmación + ID del post                            │
#└─────────────────────────────────────────────────────────────────┘   
