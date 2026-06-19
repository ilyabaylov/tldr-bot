"""Инлайн-клавиатуры."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import User

_LENGTH_LABELS = {
    "ru": {"short": "Кратко", "medium": "Средне", "detailed": "Подробно"},
    "en": {"short": "Short", "medium": "Medium", "detailed": "Detailed"},
}

# Кнопки форматов под каждой выжимкой.
_FORMATS = {
    "ru": [
        ("tldr", "📝 TL;DR"),
        ("bullets", "🔑 Тезисы"),
        ("ideas", "💡 Идеи"),
        ("actions", "✅ Действия"),
        ("eli5", "🧒 Просто"),
    ],
    "en": [
        ("tldr", "📝 TL;DR"),
        ("bullets", "🔑 Points"),
        ("ideas", "💡 Ideas"),
        ("actions", "✅ Actions"),
        ("eli5", "🧒 Simple"),
    ],
}
_ASK_LABEL = {"ru": "❓ Спросить по тексту", "en": "❓ Ask about this"}
_EXPORT_LABEL = {"ru": "📄 Экспорт .md", "en": "📄 Export .md"}
_CLOSE_LABEL = {"ru": "✕ Закрыть", "en": "✕ Close"}


def _pick(table: dict[str, dict], lang: str) -> dict:
    return table.get(lang, table["ru"])


def _label(table: dict[str, str], lang: str) -> str:
    return table.get(lang, table["ru"])


def _mark(active: bool) -> str:
    return "✅ " if active else ""


def settings_keyboard(user: User) -> InlineKeyboardMarkup:
    """Клавиатура настроек: длина ответа и язык."""
    length_labels = _pick(_LENGTH_LABELS, user.lang)
    length_row = [
        InlineKeyboardButton(
            text=f"{_mark(user.length == value)}{label}",
            callback_data=f"set:length:{value}",
        )
        for value, label in length_labels.items()
    ]
    lang_row = [
        InlineKeyboardButton(text=f"{_mark(user.lang == 'ru')}🇷🇺 RU", callback_data="set:lang:ru"),
        InlineKeyboardButton(text=f"{_mark(user.lang == 'en')}🇬🇧 EN", callback_data="set:lang:en"),
    ]
    close_row = [
        InlineKeyboardButton(text=_label(_CLOSE_LABEL, user.lang), callback_data="ui:close"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[length_row, lang_row, close_row])


def summary_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопки смены формата, вопроса по тексту и экспорта."""
    formats = _pick(_FORMATS, lang)
    row1 = [
        InlineKeyboardButton(text=label, callback_data=f"fmt:{key}")
        for key, label in formats[:3]
    ]
    row2 = [
        InlineKeyboardButton(text=label, callback_data=f"fmt:{key}")
        for key, label in formats[3:]
    ]
    action_row = [
        InlineKeyboardButton(text=_label(_ASK_LABEL, lang), callback_data="ask:on"),
        InlineKeyboardButton(text=_label(_EXPORT_LABEL, lang), callback_data="export:md"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, action_row])
