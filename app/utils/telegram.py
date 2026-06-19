"""Отправка сообщений в Telegram."""
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message

from app.utils.text import split_text


async def answer_safe(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> Message | None:
    """Отправляет длинный текст частями и повторяет без Markdown при ошибке."""
    chunks = split_text(text)
    sent: Message | None = None
    for index, chunk in enumerate(chunks):
        markup = reply_markup if index == len(chunks) - 1 else None
        try:
            sent = await message.answer(chunk, reply_markup=markup)
        except TelegramBadRequest:
            sent = await message.answer(chunk, reply_markup=markup, parse_mode=None)
    return sent
