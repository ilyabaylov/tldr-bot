"""Построение промптов. Чистые функции — без сети и конфига, легко тестируются."""

LANG_NAMES: dict[str, str] = {"ru": "Russian", "en": "English"}

# Разные форматы выжимки. У каждого — своя форма ответа, чтобы они не были похожи.
FORMAT_HINTS: dict[str, dict[str, str]] = {
    "ru": {
        "tldr": (
            "Передай суть одним связным абзацем из 2–4 предложений — без списков, заголовков и маркеров. "
            "Читатель должен понять, о чём материал и каков главный вывод, не открывая оригинал."
        ),
        "bullets": (
            "Сделай маркированный список ключевых пунктов, каждая строка начинается с «- ». "
            "Один пункт — один факт или тезис с конкретикой: цифры, имена, причины, итоги. "
            "Пункты не должны повторять друг друга."
        ),
        "ideas": (
            "Выдели не пересказ, а главные мысли и неочевидные выводы. "
            "Каждый пункт списка строй по схеме «<идея> — <чем важна или что из неё следует>». "
            "Сосредоточься на смысле, а не на перечислении фактов."
        ),
        "actions": (
            "Преврати материал в практический план. Дай нумерованный список (1., 2., 3.) "
            "конкретных шагов в повелительном наклонении: что сделать, проверить, применить. "
            "Если прямых действий нет — сформулируй, как использовать выводы на практике."
        ),
        "eli5": (
            "Объясни простыми словами, как умному другу без подготовки. Никакого жаргона; "
            "если без термина никак — тут же поясни его бытовой аналогией. "
            "Пиши связным текстом в 1–2 коротких абзаца, дружелюбно и без снисхождения."
        ),
    },
    "en": {
        "tldr": (
            "Give the gist as one connected paragraph of 2-4 sentences — no lists, headings or bullets. "
            "The reader should understand what the material is about and the main takeaway without opening the original."
        ),
        "bullets": (
            "Make a bulleted list of key points, each line starting with '- '. "
            "One bullet is one fact or point with specifics: numbers, names, reasons, outcomes. "
            "Bullets must not repeat each other."
        ),
        "ideas": (
            "Capture the main ideas and non-obvious conclusions, not a retelling. "
            "Build each list item as '<idea> — <why it matters or what follows from it>'. "
            "Focus on meaning, not on listing facts."
        ),
        "actions": (
            "Turn the material into a practical plan. Give a numbered list (1., 2., 3.) "
            "of concrete steps in the imperative: what to do, check, apply. "
            "If there are no direct actions, state how to use the conclusions in practice."
        ),
        "eli5": (
            "Explain it in plain words, like to a smart friend with no background. No jargon; "
            "if a term is unavoidable, immediately explain it with an everyday analogy. "
            "Write as connected text in 1-2 short paragraphs, friendly and without condescension."
        ),
    },
}

# Детальность ответа — управляет объёмом независимо от формата.
LENGTH_HINTS: dict[str, dict[str, str]] = {
    "ru": {
        "short": "Объём — минимальный: только самое важное, ничего лишнего.",
        "medium": "Объём — средний: раскрой главное, но без второстепенных деталей.",
        "detailed": "Объём — подробный: разбери все значимые моменты, ничего важного не упускай.",
    },
    "en": {
        "short": "Length — minimal: only the most important, nothing extra.",
        "medium": "Length — medium: cover the essentials without minor details.",
        "detailed": "Length — detailed: cover every significant point, miss nothing important.",
    },
}


def _pick(table: dict[str, dict[str, str]], lang: str, key: str, default_key: str) -> str:
    section = table.get(lang, table["ru"])
    return section.get(key, section[default_key])


def build_summary_prompt(
    text: str,
    *,
    lang: str = "ru",
    length: str = "medium",
    fmt: str = "bullets",
) -> str:
    """Собирает промпт с учётом языка, формата и детальности."""
    fmt_hint = _pick(FORMAT_HINTS, lang, fmt, "bullets")
    len_hint = _pick(LENGTH_HINTS, lang, length, "medium")
    lang_name = LANG_NAMES.get(lang, "Russian")
    return (
        f"{fmt_hint}\n\n"
        f"{len_hint}\n"
        f"Write the answer in {lang_name}. "
        "Stay strictly faithful to the source: do not invent facts, keep a neutral tone, "
        "cut filler, and give no preamble or sign-off.\n\n"
        f"--- CONTENT ---\n{text}"
    )


def build_qa_prompt(text: str, question: str, *, lang: str = "ru") -> str:
    """Промпт для ответа на вопрос строго по содержимому источника."""
    lang_name = LANG_NAMES.get(lang, "Russian")
    return (
        "Answer the question using ONLY the content below. "
        "If the answer is not in the content, say so honestly. "
        f"Answer in {lang_name}.\n\n"
        f"QUESTION: {question}\n\n"
        f"--- CONTENT ---\n{text}"
    )
