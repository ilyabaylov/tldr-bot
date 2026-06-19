"""Чистые текстовые утилиты (без зависимости от aiogram)."""

# Лимит Telegram на длину одного сообщения.
TELEGRAM_LIMIT = 4096


def split_text(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    """Режет длинный текст на куски по границам строк, не превышая limit."""
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        if len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            for start in range(0, len(line), limit):
                chunks.append(line[start : start + limit])
            continue
        if current and len(current) + len(line) + 1 > limit:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks
