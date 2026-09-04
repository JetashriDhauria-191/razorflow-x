from backend.failure_engine import failure_engine

def test_timeout_failure_analysis():
    res = failure_engine.analyze_failure("GATEWAY_TIMEOUT", "Connection to issuer timed out after 30000ms")
    assert res["failure_category"] == "TIMEOUT"
    assert res["failure_severity"] == "MEDIUM"
    assert res["recommended_strategy"] == "SMART_BACKOFF_RETRY"
    assert res["recovery_probability"] > 0.8

def test_bank_failure_analysis():
    res = failure_engine.analyze_failure("ISSUER_DOWN", "Bank node returned 503 service unavailable")
    assert res["failure_category"] == "BANK_FAILURE"
    assert res["failure_severity"] == "HIGH"
    assert res["recommended_strategy"] == "ALTERNATE_GATEWAY"
