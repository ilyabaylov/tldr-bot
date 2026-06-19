"""Сборка файла экспорта. Чистые функции — без сети, легко тестируются."""
from __future__ import annotations

import re
from datetime import datetime

_SLUG_RE = re.compile(r"[^\w\-]+", re.UNICODE)


def export_filename(title: str, *, now: datetime | None = None) -> str:
    """Имя файла вида 'slug-YYYYMMDD-HHMM.md' с безопасным slug."""
    now = now or datetime.now()
    stamp = now.strftime("%Y%m%d-%H%M")
    slug = _SLUG_RE.sub("-", (title or "").strip().lower()).strip("-")
    slug = slug[:40].strip("-") or "summary"
    return f"{slug}-{stamp}.md"


def build_export_md(title: str, body: str) -> str:
    """Собирает .md: заголовок и тело выжимки."""
    heading = (title or "").strip() or "Конспект"
    return f"# {heading}\n\n{body.strip()}\n"
