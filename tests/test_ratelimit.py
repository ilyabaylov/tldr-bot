from app.services.ratelimit import RateLimiter


def test_allows_up_to_limit():
    rl = RateLimiter(max_calls=3, period=60)
    assert rl.allow(1, now=0)
    assert rl.allow(1, now=1)
    assert rl.allow(1, now=2)
    assert not rl.allow(1, now=3)


def test_window_resets_after_period():
    rl = RateLimiter(max_calls=1, period=60)
    assert rl.allow(1, now=0)
    assert not rl.allow(1, now=30)
    assert rl.allow(1, now=61)


def test_users_are_isolated():
    rl = RateLimiter(max_calls=1, period=60)
    assert rl.allow(1, now=0)
    assert rl.allow(2, now=0)
