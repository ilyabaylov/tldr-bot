"""Тесты проверки конфигурации."""
from types import SimpleNamespace

from app.config_validation import validate_settings


def _settings(**overrides):
    values = dict(
        bot_token="bot-token",
        llm_provider="openai",
        chat_model="gpt-5-mini",
        llm_api_key="sk-test",
        llm_base_url="",
        gemini_api_key="",
        transcribe_provider="openai",
        transcribe_model="gpt-4o-mini-transcribe",
        transcribe_api_key="",
        transcribe_base_url="",
        rate_limit_per_min=10,
        max_input_chars=20000,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_openai_config_ok():
    report = validate_settings(_settings())
    assert report.ok


def test_openai_requires_key():
    report = validate_settings(_settings(llm_api_key=""))
    assert not report.ok
    assert any("LLM_API_KEY" in item for item in report.errors)


def test_gemini_requires_gemini_key():
    report = validate_settings(_settings(llm_provider="gemini", gemini_api_key=""))
    assert not report.ok
    assert any("GEMINI_API_KEY" in item for item in report.errors)


def test_voice_gemini_warns_when_text_openai():
    report = validate_settings(
        _settings(transcribe_provider="gemini", gemini_api_key="gemini-key")
    )
    assert report.ok
    assert any("voice uses Gemini" in item for item in report.warnings)


def test_voice_none_is_ok_with_warning():
    report = validate_settings(_settings(transcribe_provider="none"))
    assert report.ok
    assert any("Voice messages are disabled" in item for item in report.warnings)


def test_bad_rate_limit_is_error():
    report = validate_settings(_settings(rate_limit_per_min=0))
    assert not report.ok
    assert any("RATE_LIMIT_PER_MIN" in item for item in report.errors)
