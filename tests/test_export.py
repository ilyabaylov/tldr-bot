"""Тесты сборки экспорта (чистые функции)."""
from datetime import datetime

from app.services.export import build_export_md, export_filename

_NOW = datetime(2026, 6, 19, 17, 30)


def test_export_filename_has_slug_and_stamp():
    assert export_filename("My Article", now=_NOW) == "my-article-20260619-1730.md"


def test_export_filename_fallback_when_empty():
    assert export_filename("", now=_NOW) == "summary-20260619-1730.md"


def test_export_filename_sanitizes_url():
    name = export_filename("https://example.com/post?x=1", now=_NOW)
    assert name.endswith("-20260619-1730.md")
    assert "/" not in name
    assert "?" not in name


def test_build_export_md_has_heading_and_body():
    md = build_export_md("Title", "- a\n- b")
    assert md.startswith("# Title")
    assert "- a" in md
    assert "- b" in md


def test_build_export_md_default_heading():
    md = build_export_md("", "body")
    assert md.startswith("# ")
    assert "body" in md
