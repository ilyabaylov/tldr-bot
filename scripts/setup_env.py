"""Interactive .env setup for tldr-bot.

Run:
    python scripts/setup_env.py
"""
from __future__ import annotations

import json
import shutil
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

OPENAI_CHAT_MODELS = [
    ("gpt-5-mini", "recommended: good quality/cost balance"),
    ("gpt-5-nano", "cheapest, weaker quality"),
    ("gpt-4.1-mini", "older fallback, still usable"),
]

OPENAI_TRANSCRIBE_MODELS = [
    ("gpt-4o-mini-transcribe", "recommended: cheap voice transcription"),
    ("gpt-4o-transcribe", "better quality, more expensive"),
    ("whisper-1", "stable fallback"),
]

PROVIDERS = {
    "1": "openai",
    "2": "gemini",
    "3": "openrouter",
    "4": "nvidia",
    "5": "groq",
}

BASE_URLS = {
    "openai": "",
    "openrouter": "https://openrouter.ai/api/v1",
    "nvidia": "https://integrate.api.nvidia.com/v1",
    "groq": "https://api.groq.com/openai/v1",
}


def ask(prompt: str, default: str = "") -> str:
    label = f"{prompt} [{default}]: " if default else f"{prompt}: "
    value = input(label).strip()
    return value or default


def ask_secret(prompt: str, default: str = "") -> str:
    # Plain input is intentional: Windows terminals are more predictable this way.
    # The key is written only to the local .env file.
    return ask(prompt, default)


def yes_no(prompt: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{suffix}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "д", "да"}


def choose(title: str, options: list[tuple[str, str]], default_index: int = 0) -> str:
    print(f"\n{title}")
    for index, (value, note) in enumerate(options, start=1):
        print(f"  {index}. {value} — {note}")
    while True:
        raw = ask("Choose number", str(default_index + 1))
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][0]
        print("Please enter a valid number.")


def fetch_openai_models(api_key: str) -> set[str]:
    if not api_key:
        return set()
    req = urllib.request.Request(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return set()
    return {item.get("id", "") for item in data.get("data", []) if item.get("id")}


def pick_openai_chat_model(api_key: str) -> str:
    available = fetch_openai_models(api_key)
    options = OPENAI_CHAT_MODELS
    if available:
        filtered = [(model, note) for model, note in OPENAI_CHAT_MODELS if model in available]
        if filtered:
            options = filtered
        else:
            print("\nCould not find recommended models in /v1/models. You can type a model manually.")
    model = choose("OpenAI chat model", options, 0)
    if yes_no("Type a custom model instead?", False):
        model = ask("Model name", model)
    return model


def pick_provider() -> str:
    print("\nProvider for text summaries:")
    print("  1. openai — normal default if you have an OpenAI key")
    print("  2. gemini — Google Gemini")
    print("  3. openrouter — OpenRouter")
    print("  4. nvidia — NVIDIA NIM")
    print("  5. groq — Groq")
    while True:
        raw = ask("Choose provider", "1")
        if raw in PROVIDERS:
            return PROVIDERS[raw]
        if raw in PROVIDERS.values():
            return raw
        print("Please choose 1-5.")


def backup_existing_env() -> None:
    if not ENV_PATH.exists():
        return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ENV_PATH.with_name(f".env.backup-{stamp}")
    shutil.copy2(ENV_PATH, backup)
    print(f"Existing .env backed up to {backup.name}")


def write_env(values: dict[str, str]) -> None:
    lines = [
        "# Telegram",
        f"BOT_TOKEN={values['BOT_TOKEN']}",
        "",
        "# Text model",
        f"LLM_PROVIDER={values['LLM_PROVIDER']}",
        f"CHAT_MODEL={values['CHAT_MODEL']}",
        f"LLM_API_KEY={values['LLM_API_KEY']}",
        f"LLM_BASE_URL={values['LLM_BASE_URL']}",
        "",
        "# Gemini, only if LLM_PROVIDER=gemini or TRANSCRIBE_PROVIDER=gemini",
        f"GEMINI_API_KEY={values['GEMINI_API_KEY']}",
        "",
        "# Voice",
        f"TRANSCRIBE_PROVIDER={values['TRANSCRIBE_PROVIDER']}",
        f"TRANSCRIBE_MODEL={values['TRANSCRIBE_MODEL']}",
        f"TRANSCRIBE_API_KEY={values['TRANSCRIBE_API_KEY']}",
        f"TRANSCRIBE_BASE_URL={values['TRANSCRIBE_BASE_URL']}",
        "",
        "# App",
        f"DB_PATH={values['DB_PATH']}",
        f"RATE_LIMIT_PER_MIN={values['RATE_LIMIT_PER_MIN']}",
        f"MAX_INPUT_CHARS={values['MAX_INPUT_CHARS']}",
        "",
    ]
    ENV_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("tldr-bot setup")
    print("This script creates a local .env file. Do not commit it to Git.")

    bot_token = ask_secret("Telegram BOT_TOKEN")
    provider = pick_provider()

    llm_api_key = ""
    llm_base_url = BASE_URLS.get(provider, "")
    gemini_api_key = ""

    if provider == "gemini":
        gemini_api_key = ask_secret("GEMINI_API_KEY")
        chat_model = ask("CHAT_MODEL", "gemini-2.5-flash")
    else:
        llm_api_key = ask_secret("LLM_API_KEY")
        if provider == "openai":
            chat_model = pick_openai_chat_model(llm_api_key)
            llm_base_url = ask("LLM_BASE_URL (empty for normal OpenAI)", "")
        elif provider == "openrouter":
            chat_model = ask("CHAT_MODEL", "openai/gpt-5-mini")
            llm_base_url = ask("LLM_BASE_URL", BASE_URLS[provider])
        elif provider == "nvidia":
            chat_model = ask("CHAT_MODEL", "meta/llama-3.1-70b-instruct")
            llm_base_url = ask("LLM_BASE_URL", BASE_URLS[provider])
        elif provider == "groq":
            chat_model = ask("CHAT_MODEL", "llama-3.1-8b-instant")
            llm_base_url = ask("LLM_BASE_URL", BASE_URLS[provider])
        else:
            chat_model = ask("CHAT_MODEL")

    print("\nVoice messages:")
    print("  1. disabled — safest default")
    print("  2. openai — use your OpenAI key")
    print("  3. gemini — requires Gemini key")
    voice_choice = ask("Choose voice mode", "1")

    transcribe_provider = "none"
    transcribe_model = "whisper-1"
    transcribe_api_key = ""
    transcribe_base_url = ""

    if voice_choice == "2" or voice_choice.lower() == "openai":
        transcribe_provider = "openai"
        transcribe_model = choose("OpenAI transcription model", OPENAI_TRANSCRIBE_MODELS, 0)
        # Empty means: reuse LLM_API_KEY and LLM_BASE_URL.
        transcribe_api_key = ask("TRANSCRIBE_API_KEY (empty = reuse LLM_API_KEY)", "")
        transcribe_base_url = ask("TRANSCRIBE_BASE_URL (empty = reuse LLM_BASE_URL)", "")
    elif voice_choice == "3" or voice_choice.lower() == "gemini":
        transcribe_provider = "gemini"
        transcribe_model = ask("TRANSCRIBE_MODEL", "gemini-2.5-flash")
        if not gemini_api_key:
            gemini_api_key = ask_secret("GEMINI_API_KEY for voice")
    else:
        transcribe_provider = "none"

    values = {
        "BOT_TOKEN": bot_token,
        "LLM_PROVIDER": provider,
        "CHAT_MODEL": chat_model,
        "LLM_API_KEY": llm_api_key,
        "LLM_BASE_URL": llm_base_url,
        "GEMINI_API_KEY": gemini_api_key,
        "TRANSCRIBE_PROVIDER": transcribe_provider,
        "TRANSCRIBE_MODEL": transcribe_model,
        "TRANSCRIBE_API_KEY": transcribe_api_key,
        "TRANSCRIBE_BASE_URL": transcribe_base_url,
        "DB_PATH": ask("DB_PATH", "data/tldr.db"),
        "RATE_LIMIT_PER_MIN": ask("RATE_LIMIT_PER_MIN", "10"),
        "MAX_INPUT_CHARS": ask("MAX_INPUT_CHARS", "20000"),
    }

    backup_existing_env()
    write_env(values)

    print("\n.env created")
    print("Run:")
    print("  python -m app.bot")
    print("\nCurrent voice mode:")
    print(f"  TRANSCRIBE_PROVIDER={values['TRANSCRIBE_PROVIDER']}")
    print(f"  TRANSCRIBE_MODEL={values['TRANSCRIBE_MODEL']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
