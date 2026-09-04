from backend.risk_engine import risk_engine

def test_low_risk_evaluation():
    res = risk_engine.evaluate_risk({
        "amount": 450.0,
        "retry_count": 0,
        "failure_count": 0,
        "transaction_frequency_10min": 1,
        "hour_of_day": 15,
        "device_trust_score": 0.95,
        "previous_success_rate": 0.99,
        "velocity_score": 0.5
    })
    assert res["risk_score"] < 40.0
    assert res["risk_level"] in ["LOW", "MEDIUM"]
    assert len(res["factors"]) > 0

def test_high_risk_evaluation():
    res = risk_engine.evaluate_risk({
        "amount": 95000.0,
        "retry_count": 4,
        "failure_count": 5,
        "transaction_frequency_10min": 12,
        "hour_of_day": 3,
        "device_trust_score": 0.1,
        "previous_success_rate": 0.10,
        "velocity_score": 7.5
    })
    assert res["risk_score"] >= 70.0
    assert res["risk_level"] == "HIGH"
    assert "Step-up" in res["recommended_action"]
