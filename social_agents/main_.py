import logging
from agents.facebook_agent import FacebookAgent
from agents.instagram_agent import InstagramAgent
from agents.x_agent import XAgent
from agents.groq_agent import GroqContentAgent
from config import MetaConfig, XConfig, GroqConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("social_agents")


def main() -> None:
    meta = MetaConfig()
    x_cfg = XConfig()
    groq_cfg = GroqConfig()

    # --- Generar contenido con Groq ---
    groq = GroqContentAgent(groq_cfg.api_key, groq_cfg.model)
    topic = "Lanzamiento de nuestra nueva app de productividad"

    logger.info("=== Generando contenido con Groq ===")
    content = groq.generate_content_pack(topic)

    for platform, text in content.items():
        logger.info("[%s] %s", platform, text[:80] + "...")

    # --- Publicar ---
    fb = FacebookAgent(meta.page_id, meta.page_token)
    ig = InstagramAgent(meta.ig_user_id, meta.ig_token)
    x = XAgent(
        x_cfg.api_key, x_cfg.api_secret,
        x_cfg.access_token, x_cfg.access_secret,
    )

    # Facebook
    try:
        fb_id = fb.publish_text(content["facebook"])
        logger.info("Facebook OK: %s", fb_id)
    except Exception as e:
        logger.error("Facebook falló: %s", e)

    # Instagram (requiere imagen; aquí usas una URL de ejemplo)
    try:
        ig_id = ig.publish_image(
            image_url="https://cdn.example.com/post.jpg",
            caption=content["instagram"],
        )
        logger.info("Instagram OK: %s", ig_id)
    except Exception as e:
        logger.error("Instagram falló: %s", e)

    # X
    try:
        x_id = x.publish_text(content["x"])
        logger.info("X OK: %s", x_id)
    except Exception as e:
        logger.error("X falló: %s", e)


if __name__ == "__main__":
    main()   
