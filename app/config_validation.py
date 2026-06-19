"""Проверка настроек перед запуском."""
from __future__ import annotations

from dataclasses import dataclass

_OPENAI_COMPATIBLE = {"openai", "openrouter", "nvidia", "groq"}
_PROVIDERS = _OPENAI_COMPATIBLE | {"gemini"}
_TRANSCRIBE_PROVIDERS = _OPENAI_COMPATIBLE | {"gemini", "none"}
_PLACEHOLDERS = {
    "",
    "...",
    "your-openai-api-key",
    "your-gemini-api-key",
    "your-telegram-bot-token",
    "твой_openai_key",
    "твой_telegram_bot_token",
}


@dataclass(frozen=True)
class ConfigReport:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _empty(value: str | None) -> bool:
    return (value or "").strip() in _PLACEHOLDERS


def validate_settings(settings) -> ConfigReport:
    errors: list[str] = []
    warnings: list[str] = []

    llm_provider = settings.llm_provider.lower().strip()
    transcribe_provider = settings.transcribe_provider.lower().strip() or "none"

    if _empty(settings.bot_token):
        errors.append("BOT_TOKEN is empty. Get it from @BotFather and put it into .env.")

    if llm_provider not in _PROVIDERS:
        errors.append(
            "LLM_PROVIDER must be one of: " + ", ".join(sorted(_PROVIDERS))
        )
    elif llm_provider == "gemini":
        if _empty(settings.gemini_api_key):
            errors.append("LLM_PROVIDER=gemini, but GEMINI_API_KEY is empty.")
    elif llm_provider in _OPENAI_COMPATIBLE:
        if _empty(settings.llm_api_key):
            errors.append(f"LLM_PROVIDER={llm_provider}, but LLM_API_KEY is empty.")

    if _empty(settings.chat_model):
        errors.append("CHAT_MODEL is empty.")

    if transcribe_provider not in _TRANSCRIBE_PROVIDERS:
        errors.append(
            "TRANSCRIBE_PROVIDER must be one of: "
            + ", ".join(sorted(_TRANSCRIBE_PROVIDERS))
        )
    elif transcribe_provider == "gemini":
        if _empty(settings.gemini_api_key):
            errors.append("TRANSCRIBE_PROVIDER=gemini, but GEMINI_API_KEY is empty.")
        if llm_provider in _OPENAI_COMPATIBLE:
            warnings.append(
                "Text uses OpenAI-compatible provider, but voice uses Gemini. "
                "If you have only an OpenAI key, set TRANSCRIBE_PROVIDER=openai."
            )
    elif transcribe_provider in _OPENAI_COMPATIBLE:
        if _empty(settings.transcribe_api_key) and _empty(settings.llm_api_key):
            errors.append(
                f"TRANSCRIBE_PROVIDER={transcribe_provider}, but neither "
                "TRANSCRIBE_API_KEY nor LLM_API_KEY is set."
            )
    elif transcribe_provider == "none":
        warnings.append("Voice messages are disabled: TRANSCRIBE_PROVIDER=none.")

    if transcribe_provider != "none" and _empty(settings.transcribe_model):
        errors.append("TRANSCRIBE_MODEL is empty.")

    if settings.rate_limit_per_min <= 0:
        errors.append("RATE_LIMIT_PER_MIN must be greater than 0.")
    if settings.max_input_chars < 1000:
        warnings.append("MAX_INPUT_CHARS is very small; long summaries may be cut too early.")

    return ConfigReport(errors=errors, warnings=warnings)


def format_report(report: ConfigReport) -> str:
    lines: list[str] = []
    if report.errors:
        lines.append("Config errors:")
        lines.extend(f"- {item}" for item in report.errors)
    if report.warnings:
        if lines:
            lines.append("")
        lines.append("Config warnings:")
        lines.extend(f"- {item}" for item in report.warnings)
    return "\n".join(lines) if lines else "Config OK"


def validate_or_raise(settings) -> None:
    report = validate_settings(settings)
    if not report.ok:
        raise RuntimeError(format_report(report))
