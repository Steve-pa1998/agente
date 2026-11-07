import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class FacebookAgent:
    """Publica en una página de Facebook usando la Graph API de Meta."""

    BASE_URL = "https://graph.facebook.com/v26.0"

    def __init__(self, page_id: str, page_token: str) -> None:
        self.page_id = page_id
        self.page_token = page_token

    def _post(self, path: str, **params) -> dict:
        url = f"{self.BASE_URL}{path}"
        data = {**params, "access_token": self.page_token}
        resp = requests.post(url, data=data, timeout=30)
        body = resp.json()
        if "error" in body:
            err = body["error"]
            raise RuntimeError(
                f"Facebook Graph error {err.get('code')}: {err.get('message')}"
            )
        return body

    def publish_text(self, message: str, link: Optional[str] = None) -> str:
        """Publica texto (y opcionalmente un enlace) en el feed de la página."""
        params: dict = {"message": message}
        if link:
            params["link"] = link
        result = self._post(f"/{self.page_id}/feed", **params)
        post_id = result["id"]
        logger.info("Facebook post publicado: %s", post_id)
        return post_id

    def publish_photo(self, message: str, photo_url: str) -> str:
        """Publica una foto desde URL pública."""
        result = self._post(
            f"/{self.page_id}/photos",
            message=message,
            url=photo_url,
        )
        post_id = result["id"]
        logger.info("Facebook foto publicada: %s", post_id)
        return post_id

    def schedule_post(
        self, message: str, scheduled_publish_time: int
    ) -> str:
        """Programa una publicación. scheduled_publish_time = Unix timestamp."""
        result = self._post(
            f"/{self.page_id}/feed",
            message=message,
            published="false",
            scheduled_publish_time=str(scheduled_publish_time),
        )
        post_id = result["id"]
        logger.info("Facebook post programado: %s", post_id)
        return post_id   
