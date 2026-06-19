"""OpenAI и OpenAI-совместимые API."""
import io
from functools import lru_cache

from openai import APIConnectionError, APIStatusError, AuthenticationError, AsyncOpenAI, RateLimitError

from app.config import settings
from app.llm import ModelAuthError, ModelUnavailableError

_MIME_EXT = {
    "audio/ogg": "ogg",
    "audio/mpeg": "mp3",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
}


@lru_cache(maxsize=1)
def _chat_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url or None)


@lru_cache(maxsize=1)
def _transcribe_client() -> AsyncOpenAI:
    api_key = settings.transcribe_api_key or settings.llm_api_key
    base_url = settings.transcribe_base_url or settings.llm_base_url or None
    return AsyncOpenAI(api_key=api_key, base_url=base_url)


def _raise_readable_error(exc: Exception) -> None:
    if isinstance(exc, AuthenticationError):
        raise ModelAuthError("OpenAI API key is invalid or missing") from exc
    if isinstance(exc, RateLimitError):
        raise ModelUnavailableError("OpenAI rate limit exceeded") from exc
    if isinstance(exc, APIConnectionError):
        raise ModelUnavailableError("OpenAI connection failed") from exc
    if isinstance(exc, APIStatusError):
        raise ModelUnavailableError(f"OpenAI API error: {exc.status_code}") from exc
    raise exc


class OpenAICompatChat:
    def __init__(self, model: str) -> None:
        self.model = model

    async def complete(self, prompt: str) -> str:
        try:
            resp = await _chat_client().chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # noqa: BLE001
            _raise_readable_error(exc)
        return (resp.choices[0].message.content or "").strip()


async def transcribe(audio: bytes, *, model: str, mime_type: str = "audio/ogg") -> str:
    buffer = io.BytesIO(audio)
    buffer.name = f"audio.{_MIME_EXT.get(mime_type, 'ogg')}"
    try:
        resp = await _transcribe_client().audio.transcriptions.create(model=model, file=buffer)
    except Exception as exc:  # noqa: BLE001
        _raise_readable_error(exc)
    return (resp.text or "").strip()
