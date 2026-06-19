"""Логирование и стартовый баннер."""
from __future__ import annotations

import logging
import sys

__version__ = "1.0.0"

# Шумные библиотеки логгируют каждый HTTP-запрос на INFO — приглушаем.
_NOISY_LOGGERS = (
    "httpx",
    "httpcore",
    "google_genai",
    "google.genai",
    "aiogram.event",
)

_BOX_WIDTH = 31


class _Colors:
    RESET = "\033[0m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"


_LEVEL_COLORS = {
    logging.DEBUG: _Colors.DIM,
    logging.INFO: _Colors.GREEN,
    logging.WARNING: _Colors.YELLOW,
    logging.ERROR: _Colors.RED,
    logging.CRITICAL: _Colors.RED,
}


class _Formatter(logging.Formatter):
    """Аккуратный формат с мягким цветом уровня, если терминал его поддерживает."""

    def __init__(self, *, color: bool) -> None:
        super().__init__("%(asctime)s  %(levelname)-7s  %(name)s  %(message)s", "%H:%M:%S")
        self.color = color

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        if not self.color:
            return text
        tint = _LEVEL_COLORS.get(record.levelno, "")
        return f"{tint}{text}{_Colors.RESET}" if tint else text


def _supports_color() -> bool:
    return bool(getattr(sys.stderr, "isatty", lambda: False)())


def setup_logging(level: int = logging.INFO) -> None:
    """Настраивает корневой логгер и приглушает шумные библиотеки."""
    handler = logging.StreamHandler()
    handler.setFormatter(_Formatter(color=_supports_color()))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)


def _line(label: str, value: str) -> str:
    return f"  {label:<13}{value}"


def startup_banner(settings) -> str:
    """Собирает компактный баннер с ключевыми настройками (без секретов)."""
    voice = settings.transcribe_provider.lower()
    voice_line = "off" if voice == "none" else f"{voice} / {settings.transcribe_model}"
    title = "t l d r - b o t".center(_BOX_WIDTH)
    rows = [
        "",
        "  ┌" + "─" * _BOX_WIDTH + "┐",
        "  │" + title + "│",
        "  └" + "─" * _BOX_WIDTH + "┘",
        _line("version", __version__),
        _line("text", f"{settings.llm_provider} / {settings.chat_model}"),
        _line("voice", voice_line),
        _line("rate limit", f"{settings.rate_limit_per_min}/min"),
        _line("db", settings.db_path),
        "",
    ]
    return "\n".join(rows)
