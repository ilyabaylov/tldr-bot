"""Извлечение текста из файлов (PDF / TXT / Markdown)."""
import io


class DocumentUnsupported(Exception):
    """Формат файла не поддерживается."""


_TEXT_EXTS = (".txt", ".md", ".markdown", ".rst", ".csv", ".log")


def extract_document_text(data: bytes, *, filename: str = "", mime: str | None = None) -> str:
    """Возвращает текст документа по имени/MIME. PDF разбирается лениво."""
    name = (filename or "").lower()
    mime = (mime or "").lower()

    if name.endswith(_TEXT_EXTS) or mime.startswith("text/"):
        return data.decode("utf-8", errors="ignore").strip()
    if name.endswith(".pdf") or mime == "application/pdf":
        return _extract_pdf(data)
    raise DocumentUnsupported(name or mime or "unknown")


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    parts = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(parts).strip()
