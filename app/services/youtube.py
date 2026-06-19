"""Получение субтитров YouTube."""
import asyncio

_DEFAULT_LANGS = ("ru", "en", "en-US", "en-GB")


class TranscriptUnavailable(Exception):
    """Субтитры недоступны."""


def _fetch_sync(video_id: str, languages: tuple[str, ...]) -> str:
    from youtube_transcript_api import YouTubeTranscriptApi

    langs = list(languages)
    try:
        api = YouTubeTranscriptApi()
        fetch = getattr(api, "fetch", None)
        if fetch is not None:
            fetched = fetch(video_id, languages=langs)
            return " ".join(snippet.text for snippet in fetched).strip()

        data = YouTubeTranscriptApi.get_transcript(video_id, languages=langs)
        return " ".join(item["text"] for item in data).strip()
    except Exception as exc:  # noqa: BLE001
        raise TranscriptUnavailable(str(exc)) from exc


async def fetch_transcript(video_id: str, *, languages: tuple[str, ...] = _DEFAULT_LANGS) -> str:
    """Возвращает текст субтитров."""
    text = await asyncio.to_thread(_fetch_sync, video_id, tuple(languages))
    if not text:
        raise TranscriptUnavailable("empty transcript")
    return text
