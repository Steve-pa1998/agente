import logging
import tweepy

logger = logging.getLogger(__name__)


class XAgent:
    """Publica en X (Twitter) usando la API v2 vía tweepy."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_secret: str,
    ) -> None:
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
            wait_on_rate_limit=True,
        )

    def publish_text(self, text: str) -> str:
        """Publica un tweet. Máximo 280 caracteres."""
        if len(text) > 280:
            raise ValueError(f"Tweet excede 280 caracteres (tiene {len(text)})")
        response = self.client.create_tweet(text=text)
        tweet_id = response.data["id"]
        logger.info("Tweet publicado: %s", tweet_id)
        return tweet_id

    def publish_thread(self, messages: list[str]) -> list[str]:
        """Publica un hilo (cadena de tweets en respuesta)."""
        tweet_ids: list[str] = []
        for i, msg in enumerate(messages):
            if len(msg) > 280:
                raise ValueError(f"Mensaje {i+1} excede 280 caracteres")
            kwargs: dict = {"text": msg}
            if i > 0:
                kwargs["in_reply_to_tweet_id"] = tweet_ids[-1]
            resp = self.client.create_tweet(**kwargs)
            tweet_ids.append(resp.data["id"])
        logger.info("Hilo publicado: %s", tweet_ids)
        return tweet_ids

    def publish_with_media(self, text: str, media_path: str) -> str:
        """Publica un tweet con imagen local."""
        with open(media_path, "rb") as f:
            upload = self.client.media_upload(f)
        response = self.client.create_tweet(text=text, media_ids=[upload.media_id])
        tweet_id = response.data["id"]
        logger.info("Tweet con media publicado: %s", tweet_id)
        return tweet_id   
