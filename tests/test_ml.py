from backend.ml_engine import ml_engine

def test_ml_inference_and_metrics():
    # Test inference
    pred = ml_engine.predict({
        "amount": 500.0,
        "retry_count": 0,
        "failure_count": 0,
        "transaction_frequency_10min": 1,
        "hour_of_day": 14,
        "previous_success_rate": 0.95,
        "velocity_score": 1.0,
        "device_trust_score": 0.9
    })
    assert "failure_probability" in pred
    assert 0.0 <= pred["failure_probability"] <= 1.0
    assert "ml_risk_score" in pred
    assert "is_anomaly" in pred
    assert "feature_contributions" in pred

def test_ml_metrics_structure():
    metrics = ml_engine.get_metrics()
    assert "random_forest" in metrics
    assert "logistic_regression" in metrics
    rf = metrics["random_forest"]
    assert rf["accuracy"] > 0.80
    assert rf["f1_score"] > 0.70
