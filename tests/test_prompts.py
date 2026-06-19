"""Тесты чистых промптов (без сети и внешних зависимостей)."""
from app.services.prompts import (
    FORMAT_HINTS,
    LENGTH_HINTS,
    build_qa_prompt,
    build_summary_prompt,
)

_FORMATS = ["tldr", "bullets", "ideas", "actions", "eli5"]


def test_summary_prompt_contains_content_and_lang():
    prompt = build_summary_prompt("Hello world", lang="en", length="short", fmt="tldr")
    assert "Hello world" in prompt
    assert "English" in prompt


def test_summary_prompt_uses_format_hint():
    prompt = build_summary_prompt("text", lang="ru", fmt="actions")
    assert FORMAT_HINTS["ru"]["actions"] in prompt


def test_summary_prompt_uses_length_hint():
    prompt = build_summary_prompt("text", lang="ru", length="detailed", fmt="tldr")
    assert LENGTH_HINTS["ru"]["detailed"] in prompt


def test_summary_prompt_unknown_format_falls_back_to_bullets():
    prompt = build_summary_prompt("text", lang="ru", fmt="does-not-exist")
    assert FORMAT_HINTS["ru"]["bullets"] in prompt


def test_all_formats_available_in_both_langs():
    keys = set(_FORMATS)
    assert keys <= set(FORMAT_HINTS["ru"])
    assert keys <= set(FORMAT_HINTS["en"])


def test_formats_produce_distinct_prompts():
    prompts = {f: build_summary_prompt("text", lang="ru", fmt=f) for f in _FORMATS}
    assert len(set(prompts.values())) == len(_FORMATS)


def test_lengths_produce_distinct_prompts():
    prompts = {
        length: build_summary_prompt("text", lang="ru", length=length, fmt="bullets")
        for length in ("short", "medium", "detailed")
    }
    assert len(set(prompts.values())) == 3


def test_qa_prompt_contains_question_and_content():
    prompt = build_qa_prompt("some content", "What is it?", lang="en")
    assert "What is it?" in prompt
    assert "some content" in prompt
    assert "English" in prompt
