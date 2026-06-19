"""Команды и настройки."""
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from app.keyboards import settings_keyboard
from app.services.users import get_or_create_user, update_user
from app.texts import settings_text, t

router = Router()
log = logging.getLogger(__name__)

_LANGS = {"ru", "en"}
_LENGTHS = {"short", "medium", "detailed"}


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = await get_or_create_user(message.from_user.id)
    await message.answer(t(user.lang, "start"))


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    user = await get_or_create_user(message.from_user.id)
    await message.answer(t(user.lang, "help"))


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    user = await get_or_create_user(message.from_user.id)
    await message.answer(settings_text(user), reply_markup=settings_keyboard(user))


@router.callback_query(F.data == "ui:close")
async def cb_close(callback: CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()


@router.callback_query(F.data.startswith("set:"))
async def cb_set(callback: CallbackQuery) -> None:
    try:
        _, field, value = callback.data.split(":", 2)
    except ValueError:
        await callback.answer()
        return

    if (field == "lang" and value not in _LANGS) or (field == "length" and value not in _LENGTHS):
        await callback.answer()
        return

    user = await update_user(callback.from_user.id, **{field: value})
    # Если значение не изменилось, Telegram вернёт "message is not modified" — это не ошибка.
    try:
        await callback.message.edit_text(settings_text(user), reply_markup=settings_keyboard(user))
    except TelegramBadRequest:
        pass
    await callback.answer(t(user.lang, "saved"))
