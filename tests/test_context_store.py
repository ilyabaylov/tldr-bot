"""Тесты LRU+TTL хранилища контекста."""
from app.services.context_store import ContextStore, SourceContext


def _ctx(text="hello"):
    return SourceContext(text=text)


def test_set_and_get():
    store = ContextStore()
    store.set(1, _ctx("a"), now=100.0)
    got = store.get(1, now=101.0)
    assert got is not None and got.text == "a"


def test_missing_returns_none():
    store = ContextStore()
    assert store.get(999, now=1.0) is None


def test_ttl_expiry():
    store = ContextStore(ttl=10)
    store.set(1, _ctx(), now=0.0)
    assert store.get(1, now=5.0) is not None
    assert store.get(1, now=20.0) is None


def test_lru_eviction_by_size():
    store = ContextStore(max_items=2)
    store.set(1, _ctx("1"), now=0.0)
    store.set(2, _ctx("2"), now=1.0)
    store.set(3, _ctx("3"), now=2.0)  # вытесняет самый старый (1)
    assert store.get(1, now=2.0) is None
    assert store.get(2, now=2.0) is not None
    assert store.get(3, now=2.0) is not None


def test_get_refreshes_lru_order():
    store = ContextStore(max_items=2)
    store.set(1, _ctx("1"), now=0.0)
    store.set(2, _ctx("2"), now=1.0)
    store.get(1, now=2.0)  # 1 становится свежим
    store.set(3, _ctx("3"), now=3.0)  # вытесняет 2, а не 1
    assert store.get(1, now=3.0) is not None
    assert store.get(2, now=3.0) is None
