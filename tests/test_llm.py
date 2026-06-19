"""Тесты фабрики провайдеров (без реальных вызовов API)."""
import importlib

import pytest


def _load(monkeypatch, **env):
    monkeypatch.setenv("BOT_TOKEN", "test-token")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import app.config

    importlib.reload(app.config)
    import app.llm

    importlib.reload(app.llm)
    return app.llm


def test_gemini_provider_selected(monkeypatch):
    llm = _load(monkeypatch, LLM_PROVIDER="gemini", GEMINI_API_KEY="k")
    provider = llm.get_chat_provider()
    assert provider.__class__.__name__ == "GeminiChat"


def test_openai_compatible_provider_selected(monkeypatch):
    llm = _load(
        monkeypatch,
        LLM_PROVIDER="openrouter",
        LLM_API_KEY="k",
        LLM_BASE_URL="https://openrouter.ai/api/v1",
        CHAT_MODEL="openai/gpt-4o-mini",
    )
    provider = llm.get_chat_provider()
    assert provider.__class__.__name__ == "OpenAICompatChat"
    assert provider.model == "openai/gpt-4o-mini"


def test_unknown_provider_raises(monkeypatch):
    llm = _load(monkeypatch, LLM_PROVIDER="bogus")
    with pytest.raises(ValueError):
        llm.get_chat_provider()


@pytest.mark.asyncio
async def test_transcription_none_raises(monkeypatch):
    llm = _load(monkeypatch, TRANSCRIBE_PROVIDER="none")
    with pytest.raises(llm.TranscriptionUnavailable):
        await llm.transcribe_audio(b"\x00\x01")
