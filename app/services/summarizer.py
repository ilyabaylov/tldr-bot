"""Суммаризация и вопросы по тексту через выбранный чат-провайдер."""
from app.llm import get_chat_provider
from app.services.prompts import build_qa_prompt, build_summary_prompt


async def summarize(
    text: str,
    *,
    lang: str = "ru",
    length: str = "medium",
    fmt: str = "bullets",
) -> str:
    provider = get_chat_provider()
    prompt = build_summary_prompt(text, lang=lang, length=length, fmt=fmt)
    return await provider.complete(prompt)


async def answer_question(text: str, question: str, *, lang: str = "ru") -> str:
    provider = get_chat_provider()
    prompt = build_qa_prompt(text, question, lang=lang)
    return await provider.complete(prompt)
