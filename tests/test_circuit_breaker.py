from promptbridge.services.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState


def test_circuit_opens_after_failures():
    breaker = CircuitBreaker("mock", CircuitBreakerConfig(failure_threshold=2))
    assert breaker.allow_request() is True
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    assert breaker.allow_request() is False


def test_circuit_recovers_after_timeout(monkeypatch):
    breaker = CircuitBreaker("mock", CircuitBreakerConfig(failure_threshold=1, recovery_timeout_seconds=0.01))
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    monkeypatch.setattr("promptbridge.services.circuit_breaker.time.monotonic", lambda: breaker.opened_at + 1)
    assert breaker.allow_request() is True
    assert breaker.state == CircuitState.HALF_OPEN
