"""Google Gemini."""
from functools import lru_cache

from google import genai
from google.genai import errors, types

from app.config import settings
from app.llm import ModelAuthError, ModelUnavailableError


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def _raise_readable_error(exc: Exception) -> None:
    if isinstance(exc, errors.ClientError):
        message = str(exc).lower()
        if "api key" in message or "permission" in message or "unauthorized" in message:
            raise ModelAuthError("Gemini API key is invalid or missing") from exc
        raise ModelUnavailableError("Gemini API error") from exc
    raise exc


class GeminiChat:
    def __init__(self, model: str) -> None:
        self.model = model

    async def complete(self, prompt: str) -> str:
        try:
            resp = await _client().aio.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        except Exception as exc:  # noqa: BLE001
            _raise_readable_error(exc)
        return (resp.text or "").strip()


async def transcribe(audio: bytes, *, model: str, mime_type: str = "audio/ogg") -> str:
    try:
        resp = await _client().aio.models.generate_content(
            model=model,
            contents=[
                "Transcribe this audio verbatim. Return only the transcript text.",
                types.Part.from_bytes(data=audio, mime_type=mime_type),
            ],
        )
    except Exception as exc:  # noqa: BLE001
        _raise_readable_error(exc)
    return (resp.text or "").strip()
