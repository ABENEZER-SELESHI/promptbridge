from promptbridge.services.rate_limiter import RateLimitConfig, RateLimiter


def test_rate_limiter_allows_under_limit():
    limiter = RateLimiter(RateLimitConfig(max_requests=3, window_seconds=60))
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True


def test_rate_limiter_blocks_over_limit():
    limiter = RateLimiter(RateLimitConfig(max_requests=2, window_seconds=60))
    assert limiter.allow("client-b") is True
    assert limiter.allow("client-b") is True
    assert limiter.allow("client-b") is False


def test_rate_limiter_remaining():
    limiter = RateLimiter(RateLimitConfig(max_requests=5, window_seconds=60))
    limiter.allow("client-c")
    assert limiter.remaining("client-c") == 4
