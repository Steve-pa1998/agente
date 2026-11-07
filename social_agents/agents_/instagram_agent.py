import logging
import time
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class InstagramAgent:
    """
    Publica en Instagram usando la Graph API de Meta.
    Requiere cuenta profesional vinculada a una página de Facebook.
    Flujo: crear container → poll hasta FINISHED → media_publish.
    """

    BASE_URL = "https://graph.instagram.com/v26.0"
    POLL_INTERVAL_SEC = 60
    MAX_POLL_ATTEMPTS = 5

    def __init__(self, ig_user_id: str, ig_token: str) -> None:
        self.ig_user_id = ig_user_id
        self.ig_token = ig_token

    def _post(self, path: str, **params) -> dict:
        url = f"{self.BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {self.ig_token}"}
        resp = requests.post(url, json=params, headers=headers, timeout=30)
        body = resp.json()
        if "error" in body:
            err = body["error"]
            raise RuntimeError(
                f"Instagram Graph error {err.get('code')}: {err.get('message')}"
            )
        return body

    def _get(self, path: str, **params) -> dict:
        url = f"{self.BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {self.ig_token}"}
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        body = resp.json()
        if "error" in body:
            err = body["error"]
            raise RuntimeError(
                f"Instagram Graph error {err.get('code')}: {err.get('message')}"
            )
        return body

    def _wait_until_finished(self, container_id: str) -> None:
        for attempt in range(1, self.MAX_POLL_ATTEMPTS + 1):
            status = self._get(f"/{container_id}", fields="status_code")
            code = status["status_code"]
            if code == "FINISHED":
                return
            if code in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Container {container_id} en estado {code}")
            logger.debug("Container %s: %s (intento %d)", container_id, code, attempt)
            time.sleep(self.POLL_INTERVAL_SEC)
        raise TimeoutError(f"Container {container_id} no terminó a tiempo")

    def publish_image(self, image_url: str, caption: str = "") -> str:
        """Publica una imagen (URL pública HTTPS, JPEG)."""
        container = self._post(
            f"/{self.ig_user_id}/media",
            image_url=image_url,
            caption=caption,
        )
        container_id = container["id"]
        logger.info("Container creado: %s", container_id)
        self._wait_until_finished(container_id)
        result = self._post(
            f"/{self.ig_user_id}/media_publish", creation_id=container_id
        )
        media_id = result["id"]
        logger.info("Instagram imagen publicada: %s", media_id)
        return media_id

    def publish_reel(self, video_url: str, caption: str = "") -> str:
        """Publica un Reel (URL pública HTTPS, MP4)."""
        container = self._post(
            f"/{self.ig_user_id}/media",
            media_type="REELS",
            video_url=video_url,
            caption=caption,
            share_to_feed="true",
        )
        container_id = container["id"]
        logger.info("Container Reel creado: %s", container_id)
        self._wait_until_finished(container_id)
        result = self._post(
            f"/{self.ig_user_id}/media_publish", creation_id=container_id
        )
        media_id = result["id"]
        logger.info("Instagram Reel publicado: %s", media_id)
        return media_id

    def publish_story(self, media_url: str, media_type: str = "image") -> str:
        """Publica una historia. media_type: 'image' o 'video'."""
        params: dict = {
            "media_type": "STORIES",
            **({"image_url": media_url} if media_type == "image" else {"video_url": media_url}),
        }
        container = self._post(f"/{self.ig_user_id}/media", **params)
        container_id = container["id"]
        self._wait_until_finished(container_id)
        result = self._post(
            f"/{self.ig_user_id}/media_publish", creation_id=container_id
        )
        media_id = result["id"]
        logger.info("Instagram story publicada: %s", media_id)
        return media_id   
