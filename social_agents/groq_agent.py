import logging
from groq import Groq

logger = logging.getLogger(__name__)


class GroqContentAgent:
    """
    Genera contenido para redes sociales usando Groq (free tier).
    Rate limits free: 30 req/min, ~1000 req/día.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile") -> None:
        self.client = Groq(api_key=api_key)
        self.model = model

    def _generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Eres un copywriter experto en redes sociales. Responde SOLO con el texto final, sin explicaciones ni comillas."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.8,
        )
        text = response.choices[0].message.content.strip()
        logger.info("Groq generó %d caracteres", len(text))
        return text

    def generate_facebook_post(self, topic: str, tone: str = "profesional") -> str:
        """Genera un post para Facebook."""
        prompt = (
            f"Escribe un post para Facebook sobre: '{topic}'.\n"
            f"Tono: {tone}. Máximo 200 palabras. Incluye 1-2 emojis relevantes. "
            f"Termina con una pregunta o llamada a la acción."
        )
        return self._generate(prompt)

    def generate_instagram_caption(self, topic: str, hashtags: int = 5) -> str:
        """Genera un caption para Instagram."""
        prompt = (
            f"Escribe un caption para Instagram sobre: '{topic}'.\n"
            f"Máximo 80 palabras. Incluye exactamente {hashtags} hashtags relevantes "
            f"al final separados por espacio. Tono cercano y atractivo."
        )
        return self._generate(prompt)

    def generate_tweet(self, topic: str) -> str:
        """Genera un tweet de máximo 280 caracteres."""
        prompt = (
            f"Escribe un tweet sobre: '{topic}'.\n"
            f"Máximo 270 caracteres (deja margen). Tono directo, sin hashtags "
            f"si no aportan. Debe ser impactante en la primera línea."
        )
        result = self._generate(prompt)
        if len(result) > 280:
            result = result[:277] + "..."
        return result

    def generate_content_pack(self, topic: str) -> dict[str, str]:
        """Genera contenido para las 3 plataformas de una vez (3 llamadas)."""
        logger.info("Generando pack de contenido para: %s", topic)
        return {
            "facebook": self.generate_facebook_post(topic),
            "instagram": self.generate_instagram_caption(topic),
            "x": self.generate_tweet(topic),
        }   
