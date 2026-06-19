"""Выбор провайдера модели."""
from app.config import settings
from app.llm.base import ChatProvider

_OPENAI_COMPATIBLE = {"openai", "openrouter", "nvidia", "groq"}


class ModelError(Exception):
    """Ошибка при обращении к модели."""


class ModelAuthError(ModelError):
    """Неверный или пустой ключ API."""


class ModelUnavailableError(ModelError):
    """Модель или провайдер временно недоступны."""


class TranscriptionUnavailable(Exception):
    """Распознавание речи не настроено."""


def get_chat_provider() -> ChatProvider:
    """Возвращает провайдера для текстовых запросов."""
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        from app.llm.gemini import GeminiChat

        return GeminiChat(settings.chat_model)
    if provider in _OPENAI_COMPATIBLE:
        from app.llm.openai_compat import OpenAICompatChat

        return OpenAICompatChat(settings.chat_model)
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider!r}")


async def transcribe_audio(audio: bytes, *, mime_type: str = "audio/ogg") -> str:
    """Распознаёт аудио выбранным провайдером."""
    provider = settings.transcribe_provider.lower()
    if provider == "none":
        raise TranscriptionUnavailable
    if provider == "gemini":
        from app.llm.gemini import transcribe

        return await transcribe(audio, model=settings.transcribe_model, mime_type=mime_type)
    if provider in _OPENAI_COMPATIBLE:
        from app.llm.openai_compat import transcribe

        return await transcribe(audio, model=settings.transcribe_model, mime_type=mime_type)
    raise TranscriptionUnavailable
