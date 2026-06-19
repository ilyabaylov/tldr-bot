"""Check tldr-bot .env without external dependencies.

Run:
    python scripts/check_config.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config_validation import format_report, validate_settings  # noqa: E402

DEFAULTS = {
    "BOT_TOKEN": "",
    "LLM_PROVIDER": "openai",
    "CHAT_MODEL": "gpt-5-mini",
    "LLM_API_KEY": "",
    "LLM_BASE_URL": "",
    "GEMINI_API_KEY": "",
    "TRANSCRIBE_PROVIDER": "openai",
    "TRANSCRIBE_MODEL": "gpt-4o-mini-transcribe",
    "TRANSCRIBE_API_KEY": "",
    "TRANSCRIBE_BASE_URL": "",
    "DB_PATH": "data/tldr.db",
    "RATE_LIMIT_PER_MIN": "10",
    "MAX_INPUT_CHARS": "20000",
}


def _clean(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = _clean(value)
    return values


def as_int(value: str, default: int) -> int:
    try:
        return int(value)
    except ValueError:
        return default


def load_settings() -> SimpleNamespace:
    raw = DEFAULTS | read_env_file(ENV_PATH)
    for key in DEFAULTS:
        if key in os.environ:
            raw[key] = os.environ[key]

    return SimpleNamespace(
        bot_token=raw["BOT_TOKEN"],
        llm_provider=raw["LLM_PROVIDER"],
        chat_model=raw["CHAT_MODEL"],
        llm_api_key=raw["LLM_API_KEY"],
        llm_base_url=raw["LLM_BASE_URL"],
        gemini_api_key=raw["GEMINI_API_KEY"],
        transcribe_provider=raw["TRANSCRIBE_PROVIDER"],
        transcribe_model=raw["TRANSCRIBE_MODEL"],
        transcribe_api_key=raw["TRANSCRIBE_API_KEY"],
        transcribe_base_url=raw["TRANSCRIBE_BASE_URL"],
        db_path=raw["DB_PATH"],
        rate_limit_per_min=as_int(raw["RATE_LIMIT_PER_MIN"], 0),
        max_input_chars=as_int(raw["MAX_INPUT_CHARS"], 0),
    )


def main() -> int:
    if not ENV_PATH.exists():
        print(".env not found")
        print("Run: python scripts/setup_env.py")
        return 1

    settings = load_settings()
    report = validate_settings(settings)
    print(format_report(report))
    if report.ok:
        print("\nActive config:")
        print(f"- LLM_PROVIDER={settings.llm_provider}")
        print(f"- CHAT_MODEL={settings.chat_model}")
        print(f"- TRANSCRIBE_PROVIDER={settings.transcribe_provider}")
        print(f"- TRANSCRIBE_MODEL={settings.transcribe_model}")
        return 0

    print("\nFix .env or run: python scripts/setup_env.py")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
