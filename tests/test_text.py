"""Тесты разбиения длинного текста (без aiogram)."""
from app.utils.text import TELEGRAM_LIMIT, split_text


def test_short_text_one_chunk():
    assert split_text("hello") == ["hello"]


def test_long_text_split_within_limit():
    text = "\n".join("line %d" % i for i in range(5000))
    chunks = split_text(text)
    assert len(chunks) > 1
    assert all(len(chunk) <= TELEGRAM_LIMIT for chunk in chunks)


def test_very_long_single_line_is_hard_split():
    text = "x" * (TELEGRAM_LIMIT * 2 + 10)
    chunks = split_text(text)
    assert all(len(chunk) <= TELEGRAM_LIMIT for chunk in chunks)
    assert "".join(chunks) == text


def test_custom_limit():
    chunks = split_text("a\nb\nc\nd", limit=3)
    assert all(len(chunk) <= 3 for chunk in chunks)
