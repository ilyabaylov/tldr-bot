"""Протокол чат-провайдера: любой бэкенд умеет превратить промпт в текст."""
from typing import Protocol


class ChatProvider(Protocol):
    async def complete(self, prompt: str) -> str:
        ...
