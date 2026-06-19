"""Обработка контента: текст, ссылка, YouTube, голосовое, документ."""
import logging
import time

from aiogram import Bot, F, Router
from aiogram.types import Message

from app.config import settings
from app.keyboards import summary_keyboard
from app.llm import (
    ModelAuthError,
    ModelUnavailableError,
    TranscriptionUnavailable,
    transcribe_audio,
)
from app.services.context_store import SourceContext, store
from app.services.documents import DocumentUnsupported, extract_document_text
from app.services.extractor import fetch_article, find_url, youtube_id
from app.services.ratelimit import RateLimiter
from app.services.summarizer import summarize
from app.services.users import get_or_create_user
from app.services.youtube import TranscriptUnavailable, fetch_transcript
from app.texts import t
from app.utils.telegram import answer_safe

router = Router()
limiter = RateLimiter(settings.rate_limit_per_min)
log = logging.getLogger("tldr.content")

_MAX_FILE_BYTES = 20 * 1024 * 1024
_DEFAULT_FMT = "bullets"


async def _deliver(
    message: Message, user, source_text: str, *, kind: str, title: str = ""
) -> None:
    """Суммаризирует источник, сохраняет контекст и отвечает с кнопками."""
    source_text = source_text[: settings.max_input_chars]
    started = time.monotonic()
    try:
        summary = await summarize(source_text, lang=user.lang, length=user.length, fmt=_DEFAULT_FMT)
    except ModelAuthError:
        await message.answer(t(user.lang, "model_auth_error"))
        return
    except ModelUnavailableError:
        await message.answer(t(user.lang, "model_unavailable"))
        return

    store.set(
        message.from_user.id,
        SourceContext(
            text=source_text,
            title=title,
            lang=user.lang,
            length=user.length,
            last_summary=summary,
            last_fmt=_DEFAULT_FMT,
        ),
    )
    await answer_safe(message, summary, reply_markup=summary_keyboard(user.lang))
    elapsed = time.monotonic() - started
    log.info("summary done: kind=%s chars=%d in %.1fs", kind, len(source_text), elapsed)


@router.message(F.voice | F.audio)
async def handle_voice(message: Message, bot: Bot) -> None:
    user = await get_or_create_user(message.from_user.id)
    if not limiter.allow(user.id):
        await message.answer(t(user.lang, "rate_limited"))
        return

    note = await message.answer(t(user.lang, "transcribing"))
    source = message.voice or message.audio
    mime = getattr(source, "mime_type", None) or "audio/ogg"
    try:
        buffer = await bot.download(source)
        transcript = await transcribe_audio(buffer.read(), mime_type=mime)
    except TranscriptionUnavailable:
        await note.edit_text(t(user.lang, "voice_unavailable"))
        return
    except ModelAuthError:
        await note.edit_text(t(user.lang, "model_auth_error"))
        return
    except ModelUnavailableError:
        await note.edit_text(t(user.lang, "model_unavailable"))
        return
    except Exception:
        log.exception("voice transcription failed")
        await note.edit_text(t(user.lang, "error"))
        return
    await note.delete()
    await _deliver(message, user, transcript, kind="voice", title="voice")


@router.message(F.document)
async def handle_document(message: Message, bot: Bot) -> None:
    user = await get_or_create_user(message.from_user.id)
    if not limiter.allow(user.id):
        await message.answer(t(user.lang, "rate_limited"))
        return

    doc = message.document
    if doc.file_size and doc.file_size > _MAX_FILE_BYTES:
        await message.answer(t(user.lang, "doc_too_big"))
        return

    note = await message.answer(t(user.lang, "doc_reading"))
    try:
        buffer = await bot.download(doc)
        text = extract_document_text(buffer.read(), filename=doc.file_name or "", mime=doc.mime_type)
    except DocumentUnsupported:
        await note.edit_text(t(user.lang, "doc_unsupported"))
        return
    except Exception:
        log.exception("document parsing failed")
        await note.edit_text(t(user.lang, "error"))
        return

    if len(text) < 200:
        await note.edit_text(t(user.lang, "too_short"))
        return
    await note.delete()
    await _deliver(message, user, text, kind="document", title=doc.file_name or "document")


@router.message(F.text)
async def handle_text(message: Message) -> None:
    user = await get_or_create_user(message.from_user.id)
    if not limiter.allow(user.id):
        await message.answer(t(user.lang, "rate_limited"))
        return

    url = find_url(message.text)
    video_id = youtube_id(url) if url else None
    kind = "text"

    if video_id:
        kind = "youtube"
        note = await message.answer(t(user.lang, "reading_youtube"))
        try:
            source_text = await fetch_transcript(video_id)
        except TranscriptUnavailable:
            try:
                source_text = await fetch_article(url)
                kind = "link"
            except Exception:
                log.exception("youtube + article fallback failed")
                await note.edit_text(t(user.lang, "youtube_unavailable"))
                return
    elif url:
        kind = "link"
        note = await message.answer(t(user.lang, "reading"))
        try:
            source_text = await fetch_article(url)
        except Exception:
            log.exception("article fetch failed")
            await note.edit_text(t(user.lang, "error"))
            return
    else:
        if len((message.text or "").strip()) < 200:
            await message.answer(t(user.lang, "too_short"))
            return
        note = await message.answer(t(user.lang, "summarizing"))
        source_text = message.text

    if not (source_text or "").strip():
        await note.edit_text(t(user.lang, "error"))
        return
    await note.delete()
    await _deliver(message, user, source_text, kind=kind, title=url or "text")
