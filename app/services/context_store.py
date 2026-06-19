"""In-memory хранилище последнего источника на пользователя.

Нужно для перегенерации выжимки в другом формате, вопросов по тексту
и экспорта — без повторной отправки исходника. LRU по размеру + TTL по времени.
"""
import time
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class SourceContext:
    text: str
    title: str = ""
    lang: str = "ru"
    length: str = "medium"
    # Последняя показанная выжимка — для экспорта без повторного запроса к модели.
    last_summary: str = ""
    last_fmt: str = ""


class ContextStore:
    def __init__(self, max_items: int = 500, ttl: float = 86_400.0) -> None:
        self.max_items = max_items
        self.ttl = ttl
        self._data: OrderedDict[int, tuple[float, SourceContext]] = OrderedDict()

    def set(self, user_id: int, ctx: SourceContext, *, now: float | None = None) -> None:
        now = time.time() if now is None else now
        self._data[user_id] = (now, ctx)
        self._data.move_to_end(user_id)
        self._evict(now)

    def get(self, user_id: int, *, now: float | None = None) -> SourceContext | None:
        now = time.time() if now is None else now
        item = self._data.get(user_id)
        if item is None:
            return None
        timestamp, ctx = item
        if now - timestamp > self.ttl:
            del self._data[user_id]
            return None
        self._data.move_to_end(user_id)
        return ctx

    def _evict(self, now: float) -> None:
        expired = [uid for uid, (ts, _) in self._data.items() if now - ts > self.ttl]
        for uid in expired:
            del self._data[uid]
        while len(self._data) > self.max_items:
            self._data.popitem(last=False)


# Общий экземпляр для хендлеров.
store = ContextStore()
