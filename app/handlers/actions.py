"""Кнопки под выжимкой: формат, вопросы и экспорт."""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.keyboards import summary_keyboard
from app.llm import ModelAuthError, ModelUnavailableError
from app.services.context_store import store
from app.services.export import build_export_md, export_filename
from app.services.summarizer import answer_question, summarize
from app.texts import t
from app.utils.telegram import answer_safe

router = Router()
log = logging.getLogger(__name__)

_VALID_FORMATS = {"tldr", "bullets", "ideas", "actions", "eli5"}


class Ask(StatesGroup):
    waiting = State()


@router.callback_query(F.data.startswith("fmt:"))
async def cb_format(callback: CallbackQuery) -> None:
    fmt = callback.data.split(":", 1)[1]
    ctx = store.get(callback.from_user.id)
    if ctx is None or fmt not in _VALID_FORMATS:
        await callback.answer(t("ru", "ctx_expired"), show_alert=True)
        return

    await callback.answer(t(ctx.lang, "regenerating"))
    try:
        summary = await summarize(ctx.text, lang=ctx.lang, length=ctx.length, fmt=fmt)
    except ModelAuthError:
        await callback.message.answer(t(ctx.lang, "model_auth_error"))
        return
    except ModelUnavailableError:
        await callback.message.answer(t(ctx.lang, "model_unavailable"))
        return
    except Exception:
        log.exception("regenerate failed")
        await callback.message.answer(t(ctx.lang, "error"))
        return

    ctx.last_summary = summary
    ctx.last_fmt = fmt
    await answer_safe(callback.message, summary, reply_markup=summary_keyboard(ctx.lang))


@router.callback_query(F.data == "export:md")
async def cb_export(callback: CallbackQuery) -> None:
    ctx = store.get(callback.from_user.id)
    if ctx is None or not ctx.last_summary:
        await callback.answer(t("ru", "ctx_expired"), show_alert=True)
        return

    await callback.answer()
    md = build_export_md(ctx.title, ctx.last_summary)
    document = BufferedInputFile(md.encode("utf-8"), filename=export_filename(ctx.title))
    await callback.message.answer_document(document, caption=t(ctx.lang, "export_caption"))


@router.callback_query(F.data == "ask:on")
async def cb_ask(callback: CallbackQuery, state: FSMContext) -> None:
    ctx = store.get(callback.from_user.id)
    if ctx is None:
        await callback.answer(t("ru", "ctx_expired"), show_alert=True)
        return
    await state.set_state(Ask.waiting)
    await callback.answer()
    await callback.message.answer(t(ctx.lang, "ask_prompt"))


@router.message(Ask.waiting, F.text)
async def on_question(message: Message, state: FSMContext) -> None:
    await state.clear()
    ctx = store.get(message.from_user.id)
    if ctx is None:
        await message.answer(t("ru", "ctx_expired"))
        return

    note = await message.answer(t(ctx.lang, "thinking"))
    try:
        reply = await answer_question(ctx.text, message.text, lang=ctx.lang)
    except ModelAuthError:
        await note.edit_text(t(ctx.lang, "model_auth_error"))
        return
    except ModelUnavailableError:
        await note.edit_text(t(ctx.lang, "model_unavailable"))
        return
    except Exception:
        log.exception("qa failed")
        await note.edit_text(t(ctx.lang, "error"))
        return

    await note.delete()
    await answer_safe(message, reply, reply_markup=summary_keyboard(ctx.lang))
