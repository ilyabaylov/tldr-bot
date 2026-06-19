"""Ссылки и текст веб-страницы."""
import re

from bs4 import BeautifulSoup

_URL_RE = re.compile(r"https?://\S+")
_YT_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?(?:[^ ]*&)?v=|shorts/|embed/|live/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{11})"
)
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; tldr-bot/1.0)"}


def find_url(text: str) -> str | None:
    """Находит первую ссылку в тексте."""
    match = _URL_RE.search(text or "")
    return match.group(0) if match else None


def youtube_id(url: str) -> str | None:
    """Возвращает ID YouTube-ролика из ссылки."""
    match = _YT_RE.search(url or "")
    return match.group(1) if match else None


def extract_main_text(html: str) -> str:
    """Возвращает основной текст страницы."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    node = soup.find("article") or soup.find("main") or soup.body or soup
    paragraphs = [p.get_text(" ", strip=True) for p in node.find_all("p")]
    text = "\n".join(p for p in paragraphs if len(p) > 40)
    return text.strip() or node.get_text(" ", strip=True).strip()


async def fetch_article(url: str, *, timeout: float = 15.0) -> str:
    """Скачивает страницу и возвращает основной текст."""
    import httpx

    async with httpx.AsyncClient(
        follow_redirects=True, timeout=timeout, headers=_HEADERS
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    return extract_main_text(resp.text)
