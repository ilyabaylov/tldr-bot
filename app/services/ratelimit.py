"""Простой in-memory rate limit со скользящим окном на пользователя."""
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_calls: int, period: float = 60.0) -> None:
        self.max_calls = max_calls
        self.period = period
        self._hits: dict[int, deque[float]] = defaultdict(deque)

    def allow(self, user_id: int, *, now: float | None = None) -> bool:
        """True, если запрос в пределах лимита. Параметр now — для тестов."""
        now = time.monotonic() if now is None else now
        hits = self._hits[user_id]
        while hits and now - hits[0] > self.period:
            hits.popleft()
        if len(hits) >= self.max_calls:
            return False
        hits.append(now)
        return True
