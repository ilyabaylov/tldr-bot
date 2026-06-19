"""Настройки приложения."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    # Модель для выжимок и вопросов.
    llm_provider: str = "openai"
    chat_model: str = "gpt-5-mini"

    gemini_api_key: str = ""

    # Для OpenAI и OpenAI-совместимых API.
    llm_api_key: str = ""
    llm_base_url: str = ""

    # Распознавание речи.
    # Если ключ тот же, TRANSCRIBE_API_KEY можно оставить пустым.
    transcribe_provider: str = "openai"
    transcribe_model: str = "gpt-4o-mini-transcribe"
    transcribe_api_key: str = ""
    transcribe_base_url: str = ""

    db_path: str = "data/tldr.db"
    rate_limit_per_min: int = 10
    max_input_chars: int = 20000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
