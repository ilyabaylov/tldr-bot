"""Тексты интерфейса."""

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "start": (
            "Привет! Пришли текст, ссылку, YouTube, PDF или голосовое — "
            "я сделаю короткую выжимку.\n\n"
            "Под ответом будут кнопки: сменить формат, задать вопрос или скачать .md.\n\n"
            "/settings — язык и длина ответа\n"
            "/help — помощь"
        ),
        "help": (
            "Что можно отправить:\n"
            "• длинный текст\n"
            "• ссылку на статью\n"
            "• YouTube\n"
            "• PDF, TXT или MD\n"
            "• голосовое или аудио\n\n"
            "Форматы ответа:\n"
            "• TL;DR — суть одним абзацем\n"
            "• Тезисы — факты списком\n"
            "• Идеи — главные мысли и выводы\n"
            "• Действия — план шагов\n"
            "• Просто — объяснение без жаргона\n\n"
            "Можно спросить что-то по материалу или скачать выжимку файлом .md."
        ),
        "settings_title": "⚙️ Настройки",
        "settings_lang": "Язык ответа",
        "settings_length": "Длина выжимки",
        "settings_hint": "Выбери параметры ниже.",
        "len_short": "кратко",
        "len_medium": "средне",
        "len_detailed": "подробно",
        "saved": "Сохранено",
        "reading": "Читаю статью…",
        "reading_youtube": "Беру субтитры YouTube…",
        "summarizing": "Делаю выжимку…",
        "transcribing": "Распознаю аудио…",
        "doc_reading": "Читаю документ…",
        "regenerating": "Меняю формат…",
        "thinking": "Ищу ответ в материале…",
        "ask_prompt": "Напиши вопрос по этому материалу.",
        "export_caption": "Готово — выжимка в файле .md",
        "too_short": "Текст слишком короткий. Пришли материал подлиннее.",
        "rate_limited": "Слишком много запросов. Подожди минуту 🙏",
        "ctx_expired": "Материал устарел. Пришли его заново.",
        "youtube_unavailable": "Не нашёл доступные субтитры для этого видео.",
        "voice_unavailable": "Голосовые сейчас отключены. Проверь TRANSCRIBE_PROVIDER в .env.",
        "model_auth_error": "Проблема с API-ключом. Проверь .env и перезапусти бота.",
        "model_unavailable": "Провайдер модели сейчас не ответил. Попробуй ещё раз позже.",
        "doc_unsupported": "Поддерживаю PDF, TXT и MD.",
        "doc_too_big": "Файл слишком большой. Лимит — 20 МБ.",
        "error": "Не получилось обработать. Попробуй ещё раз.",
    },
    "en": {
        "start": (
            "Hi! Send text, a link, YouTube, PDF or a voice message — "
            "I'll make a short summary.\n\n"
            "Buttons under the reply let you change the format, ask about the material or export .md.\n\n"
            "/settings — language and length\n"
            "/help — help"
        ),
        "help": (
            "You can send:\n"
            "• long text\n"
            "• an article link\n"
            "• YouTube\n"
            "• PDF, TXT or MD\n"
            "• voice or audio\n\n"
            "Answer formats:\n"
            "• TL;DR — the gist in one paragraph\n"
            "• Points — facts as a list\n"
            "• Ideas — main thoughts and takeaways\n"
            "• Actions — a step plan\n"
            "• Simple — a jargon-free explanation\n\n"
            "You can ask about the material or export the summary as a .md file."
        ),
        "settings_title": "⚙️ Settings",
        "settings_lang": "Reply language",
        "settings_length": "Summary length",
        "settings_hint": "Pick the options below.",
        "len_short": "short",
        "len_medium": "medium",
        "len_detailed": "detailed",
        "saved": "Saved",
        "reading": "Reading the article…",
        "reading_youtube": "Getting YouTube subtitles…",
        "summarizing": "Summarizing…",
        "transcribing": "Transcribing audio…",
        "doc_reading": "Reading the document…",
        "regenerating": "Changing the format…",
        "thinking": "Looking for the answer…",
        "ask_prompt": "Type your question about this material.",
        "export_caption": "Done — summary as a .md file",
        "too_short": "The text is too short. Send something longer.",
        "rate_limited": "Too many requests. Please wait a minute 🙏",
        "ctx_expired": "The material has expired. Send it again.",
        "youtube_unavailable": "No available subtitles found for this video.",
        "voice_unavailable": "Voice messages are disabled. Check TRANSCRIBE_PROVIDER in .env.",
        "model_auth_error": "API key problem. Check .env and restart the bot.",
        "model_unavailable": "The model provider did not respond. Try again later.",
        "doc_unsupported": "PDF, TXT and MD are supported.",
        "doc_too_big": "The file is too large. Limit: 20 MB.",
        "error": "Couldn't process that. Please try again.",
    },
}

_LENGTH_KEYS = {"short": "len_short", "medium": "len_medium", "detailed": "len_detailed"}


def t(lang: str, key: str) -> str:
    """Возвращает текст по ключу."""
    table = TEXTS.get(lang, TEXTS["ru"])
    return table.get(key) or TEXTS["ru"].get(key, key)


def settings_text(user) -> str:
    """Собирает текст экрана настроек с текущими значениями."""
    lang = user.lang
    length_label = t(lang, _LENGTH_KEYS.get(user.length, "len_medium"))
    lang_label = "🇷🇺 RU" if lang == "ru" else "🇬🇧 EN"
    return (
        f"{t(lang, 'settings_title')}\n\n"
        f"{t(lang, 'settings_lang')}: {lang_label}\n"
        f"{t(lang, 'settings_length')}: {length_label}\n\n"
        f"{t(lang, 'settings_hint')}"
    )
