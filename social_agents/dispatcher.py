import logging
from typing import Optional

from config import (
    FB_PAGE_ID, FB_PAGE_TOKEN,
    IG_USER_ID, IG_TOKEN,
    X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET,
)
from agents_.facebook_agent import FacebookAgent
from agents_.instagram_agent import InstagramAgent
from agents_.x_agent import XAgent

logger = logging.getLogger(__name__)


def _get_agents() -> dict:
    """Instancia solo los agentes que tienen tokens configurados."""
    agents = {}
    if FB_PAGE_ID and FB_PAGE_TOKEN:
        agents["facebook"] = FacebookAgent(FB_PAGE_ID, FB_PAGE_TOKEN)
    if IG_USER_ID and IG_TOKEN:
        agents["instagram"] = InstagramAgent(IG_USER_ID, IG_TOKEN)
    if X_API_KEY and X_API_SECRET and X_ACCESS_TOKEN and X_ACCESS_SECRET:
        agents["x"] = XAgent(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
    return agents


def post(
    platform: str,
    content: str,
    media_url: Optional[str] = None,
    media_path: Optional[str] = None,
    is_video: bool = False,
) -> str:
    """
    Publica en la plataforma indicada.

    Args:
        platform: "facebook", "instagram", "x"
        content: Texto/caption
        media_url: URL pública (para FB/IG)
        media_path: Ruta local (para X)
        is_video: Si el media es video (para IG Reel/Story)
    """
    agents = _get_agents()

    if platform not in agents:
        configured = list(agents.keys())
        return f"ERROR: plataforma '{platform}' no configurada. Disponibles: {configured}"

    agent = agents[platform]
    try:
        if platform == "facebook":
            if media_url:
                return agent.publish_photo(content, media_url)
            return agent.publish_text(content)

        elif platform == "instagram":
            if not media_url:
                return "ERROR: Instagram requiere media_url (URL pública HTTPS)."
            if is_video:
                return agent.publish_reel(media_url, content)
            return agent.publish_image(media_url, content)

        elif platform == "x":
            if media_path:
                return agent.publish_with_media(content, media_path)
            return agent.publish_text(content)

    except Exception as e:
        logger.exception("Error publicando en %s", platform)
        return f"ERROR en {platform}: {e}"


def post_all(
    content: str,
    media_url: Optional[str] = None,
    media_path: Optional[str] = None,
    is_video: bool = False,
) -> dict:
    """Publica en TODAS las plataformas configuradas."""
    agents = _get_agents()
    results = {}
    for platform in agents:
        results[platform] = post(platform, content, media_url, media_path, is_video)
    return results
