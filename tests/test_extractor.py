"""Тесты распознавания ссылок и извлечения текста."""
from app.services.extractor import extract_main_text, find_url, youtube_id


def test_find_url_present():
    assert find_url("смотри https://example.com/post тут") == "https://example.com/post"


def test_find_url_absent():
    assert find_url("просто текст без ссылок") is None


def test_extract_main_text_keeps_paragraphs():
    html = (
        "<html><body><nav>menu</nav>"
        "<article><p>" + "A" * 60 + "</p><p>" + "B" * 60 + "</p></article>"
        "</body></html>"
    )
    text = extract_main_text(html)
    assert "A" * 60 in text
    assert "menu" not in text


def test_youtube_id_watch():
    assert youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_youtube_id_short_link():
    assert youtube_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_youtube_id_shorts():
    assert youtube_id("https://youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_youtube_id_with_extra_params():
    assert youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s") == "dQw4w9WgXcQ"


def test_youtube_id_none_for_plain_url():
    assert youtube_id("https://example.com/article") is None
