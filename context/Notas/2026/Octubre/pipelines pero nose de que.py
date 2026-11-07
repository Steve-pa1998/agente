"""
pipeline_redes.py
Pipeline multi-agente para redes sociales.
Independiente de agentes.py — no lo modifica.
"""

import os
import json
import time
import requests
import ollama

# ============================================================
# CONFIGURACIÓN
# ============================================================

OLLAMA_MODEL = "llama3.2"  # ← cambia por el que tengas

# Tokens (ponlos en .env o exportalos)
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN", "")
IG_USER_ID = os.getenv("IG_USER_ID", "")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")

GRAPH_API = "https://graph.facebook.com/v26.0"


# ============================================================
# FASE 1: RECOLECTOR — Obtiene datos de cada red
# ============================================================

def recolectar_x() -> dict:
    """Obtiene métricas básicas de tu cuenta en X."""
    if not X_ACCESS_TOKEN:
        return {"red": "X", "error": "Sin token"}
    try:
        # GET /2/users/me?user.fields=public_metrics
        r = requests.get(
            "https://api.twitter.com/2/users/me",
            headers={"Authorization": f"Bearer {X_ACCESS_TOKEN}"},
            params={"user.fields": "public_metrics"}
        )
        r.raise_for_status()
        data = r.json()["data"]
        return {
            "red": "X",
            "seguidores": data.get("public_metrics", {}).get("followers_count", 0),
            "seguimientos": data.get("public_metrics", {}).get("following_count", 0),
            "tuits": data.get("public_metrics", {}).get("tweet_count", 0),
            "likes_recibidos": data.get("public_metrics", {}).get("like_count", 0),
        }
    except Exception as e:
        return {"red": "X", "error": str(e)}


def recolectar_facebook() -> dict:
    """Obtiene métricas de tu página de Facebook."""
    if not FB_PAGE_TOKEN:
        return {"red": "Facebook", "error": "Sin token"}
    try:
        r = requests.get(
            f"{GRAPH_API}/{FB_PAGE_ID}",
            params={
                "fields": "followers,likes,talk_about_count",
                "access_token": FB_PAGE_TOKEN
            }
        )
        r.raise_for_status()
        data = r.json()
        return {
            "red": "Facebook",
            "seguidores": data.get("followers", 0),
            "me_gusta": data.get("likes", 0),
            "hablan_de": data.get("talk_about_count", 0),
        }
    except Exception as e:
        return {"red": "Facebook", "error": str(e)}


def recolectar_instagram() -> dict:
    """Obtiene métricas de tu cuenta de Instagram (Business/Creator)."""
    if not IG_ACCESS_TOKEN:
        return {"red": "Instagram", "error": "Sin token"}
    try:
        r = requests.get(
            f"{GRAPH_API}/{IG_USER_ID}",
            params={
                "fields": "followers_count,media_count",
                "access_token": IG_ACCESS_TOKEN
            }
        )
        r.raise_for_status()
        data = r.json()
        return {
            "red": "Instagram",
            "seguidores": data.get("followers_count", 0),
            "publicaciones": data.get("media_count", 0),
        }
    except Exception as e:
        return {"red": "Instagram", "error": str(e)}


def recolectar_tiktok() -> dict:
    """Obtiene info básica de tu cuenta en TikTok."""
    if not TIKTOK_ACCESS_TOKEN:
        return {"red": "TikTok", "error": "Sin token"}
    try:
        r = requests.get(
            "https://open.tiktokapis.com/v2/user/info/?fields=[\"follower_count\",\"following_count\",\"video_count\",\"heart_count\"]",
            headers={"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"}
        )
        r.raise_for_status()
        data = r.json().get("data", {})
        return {
            "red": "TikTok",
            "seguidores": data.get("follower_count", 0),
            "videos": data.get("video_count", 0),
            "likes": data.get("heart_count", 0),
        }
    except Exception as e:
        return {"red": "TikTok", "error": str(e)}


def fase_recolectar() -> list[dict]:
    """Llama a todos los recolectores y devuelve la lista de resultados."""
    print("\n📡 [FASE 1] Recopilando datos de redes...")
    resultados = [
        recolectar_x(),
        recolectar_facebook(),
        recolectar_instagram(),
        recolectar_tiktok(),
    ]
    for r in resultados:
        status = "❌" if "error" in r else "✅"
        print(f"  {status} {r.get('red', '?')}: {r}")
    return resultados


# ============================================================
# FASE 2: ESTRATEGA — Analiza y propone
# ============================================================

def fase_estratega(datos: list[dict], tema: str) -> dict:
    """
    El LLM analiza los datos y propone un plan de publicación.
    Devuelve un dict con el plan por red.
    """
    print("\n🧠 [FASE 2] Analizando y generando estrategia...")

    prompt = f"""Eres un estratega de redes sociales y publicidad.

DATOS ACTUALES DE LAS CUENTAS:
{json.dumps(datos, indent=2, ensure_ascii=False)}

TEMA DEL DÍA: "{tema}"

Analiza qué red tiene mejor momento para publicar y genera un plan.
Responde SOLO con JSON válido en este formato:

{{
  "analisis": "breve resumen de qué red priorizar y por qué",
  "publicaciones": [
    {{
      "red": "X|Facebook|Instagram|TikTok",
      "tipo": "texto|imagen|video",
      "contenido": "el texto exacto a publicar (adapta tono y formato a la red)",
      "angulo_publicitario": "qué CTA o ángulo de venta usa",
      "prioridad": 1
    }}
  ]
}}

Reglas:
- Máximo 3 publicaciones (prioriza las redes con mejor engagement)
- Adapta el tono: X=directo/corto, FB=conversacional, IG=visual/inspiracional, TikTok=tendy/corto
- El contenido debe ser original, no genérico
- Incluye hashtags relevantes para IG y TikTok
"""

    resp = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": "Eres un estratega de marketing digital. Responde SIEMPRE solo con JSON válido, sin markdown, sin explicaciones."},
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0.4, "num_predict": 1024}
    )

    # Parsear la respuesta JSON
    texto = resp["message"]["content"].strip()
    # Limpiar si el modelo envuelve en ```json
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1] if "\n" in texto else texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]
    try:
        plan = json.loads(texto)
    except json.JSONDecodeError:
        plan = {"analisis": "Error parseando", "publicaciones": []}

    print(f"  📋 Análisis: {plan.get('analisis', 'N/A')}")
    for pub in plan.get("publicaciones", []):
        print(f"  → {pub['red']} (prioridad {pub.get('prioridad', '?')}): {pub['contenido'][:60]}...")

    return plan


# ============================================================
# FASE 3: EJECUTORES — Publican en cada red
# ============================================================

def publicar_x(texto: str) -> str:
    """Publica en X (Twitter)."""
    if not X_ACCESS_TOKEN:
        return "⚠️ Sin token de X"
    r = requests.post(
        "https://api.twitter.com/2/tweets",
        headers={"Authorization": f"Bearer {X_ACCESS_TOKEN}"},
        json={"text": texto[:280]}
    )
    if r.status_code == 201:
        return f"✅ X: Publicado (ID: {r.json()['data']['id']})"
    return f"❌ X: Error {r.status_code}: {r.text[:100]}"


def publicar_facebook(texto: str) -> str:
    """Publica en una página de Facebook."""
    if not FB_PAGE_TOKEN:
        return "⚠️ Sin token de Facebook"
    r = requests.post(
        f"{GRAPH_API}/{FB_PAGE_ID}/feed",
        data={
            "message": texto,
            "access_token": FB_PAGE_TOKEN
        }
    )
    data = r.json()
    if "id" in data:
        return f"✅ Facebook: Publicado (ID: {data['id']})"
    return f"❌ Facebook: {data.get('error', {}).get('message', r.text[:100])}"


def publicar_instagram(texto: str, imagen_url: str = None) -> str:
    """
    Publica en Instagram (Business/Creator).
    Requiere imagen o video — no soporta texto solo.
    Si no hay imagen_url, solo crea el caption y avisa.
    """
    if not IG_ACCESS_TOKEN:
        return "⚠️ Sin token de Instagram"

    if not imagen_url:
        return "⚠️ Instagram: Se requiere imagen_url para publicar (no soporta texto solo)"

    try:
        # Paso 1: Crear container
        r = requests.post(
            f"{GRAPH_API}/{IG_USER_ID}/media",
            data={
                "image_url": imagen_url,
                "caption": texto,
                "access_token": IG_ACCESS_TOKEN
            }
        )
        container_id = r.json().get("id")
        if not container_id:
            return f"❌ Instagram: {r.json()}"

        # Paso 2: Esperar a que esté listo
        time.sleep(5)
        r = requests.get(
            f"{GRAPH_API}/{container_id}",
            params={"fields": "status_code", "access_token": IG_ACCESS_TOKEN}
        )
        if r.json().get("status_code") != "FINISHED":
            return f"❌ Instagram: Container no listo ({r.json()})"

        # Paso 3: Publicar
        r = requests.post(
            f"{GRAPH_API}/{IG_USER_ID}/media_publish",
            data={"creation_id": container_id, "access_token": IG_ACCESS_TOKEN}
        )
        data = r.json()
        if "id" in data:
            return f"✅ Instagram: Publicado (ID: {data['id']})"
        return f"❌ Instagram: {data.get('error', {}).get('message', '')}"
    except Exception as e:
        return f"❌ Instagram: {e}"


def publicar_tiktok(texto: str, video_url: str = None) -> str:
    """
    Publica en TikTok.
    Requiere video. Si no hay video_url, solo avisa.
    """
    if not TIKTOK_ACCESS_TOKEN:
        return "⚠️ Sin token de TikTok"

    if not video_url:
        return "⚠️ TikTok: Se requiere video_url para publicar"

    try:
        r = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers={
                "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "post_info": {
                    "title": texto[:2200],
                    "privacy_level": "PUBLIC_TO_EVERYONE"
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_url
                }
            }
        )
        data = r.json()
        if data.get("data", {}).get("publish_id"):
            return f"✅ TikTok: Enviado (publish_id: {data['data']['publish_id']})"
        return f"❌ TikTok: {data}"
    except Exception as e:
        return f"❌ TikTok: {e}"


# Dispatcher: elige la función según la red
EJECUTORES = {
    "X": publicar_x,
    "Facebook": publicar_facebook,
    "Instagram": publicar_instagram,
    "TikTok": publicar_tiktok,
}


def fase_ejecutar(plan: dict) -> list[str]:
    """Itera el plan y publica en cada red."""
    print("\n🚀 [FASE 3] Publicando...")
    resultados = []
    for pub in plan.get("publicaciones", []):
        red = pub["red"]
        contenido = pub["contenido"]
        print(f"\n  → Publicando en {red}...")

        # Instagram y TikTok necesitan media
        if red == "Instagram":
            img = pub.get("imagen_url")
            resultado = publicar_instagram(contenido, img)
        elif red == "TikTok":
            vid = pub.get("video_url")
            resultado = publicar_tiktok(contenido, vid)
        else:
            resultado = EJECUTORES.get(red, lambda t: "❌ Red desconocida")(contenido)

        print(f"  {resultado}")
        resultados.append(resultado)

    return resultados


# ============================================================
# PIPELINE COMPLETO
# ============================================================

def ejecutar_pipeline(tema: str, imagen_url: str = None, video_url: str = None):
    """
    Ejecuta el pipeline completo:
    1. Recolecta datos
    2. Genera estrategia
    3. Publica
    """
    print("=" * 60)
    print(f"  PIPELINE DE REDES SOCIALES")
    print(f"  Tema: {tema}")
    print("=" * 60)

    # Fase 1
    datos = fase_recolectar()

    # Fase 2
    plan = fase_estratega(datos, tema)

    # Agregar URLs de media si las hay
    for pub in plan.get("publicaciones", []):
        if pub["red"] == "Instagram" and imagen_url:
            pub["imagen_url"] = imagen_url
        if pub["red"] == "TikTok" and video_url:
            pub["video_url"] = video_url

    # Fase 3
    resultados = fase_ejecutar(plan)

    print("\n" + "=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    for r in resultados:
        print(f"  {r}")
    print()

    return {"datos": datos, "plan": plan, "resultados": resultados}


# ============================================================
# USO DESDE CLI (o desde tu agentes.py)
# ============================================================

if __name__ == "__main__":
    tema = input("📌 Tema del día: ")
    img = input("🖼️  URL de imagen (para IG, o deja vacío): ").strip() or None
    vid = input("🎬 URL de video (para TikTok, o deja vacío): ").strip() or None

    ejecutar_pipeline(tema, img, vid)   
