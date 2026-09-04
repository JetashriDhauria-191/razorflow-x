from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_os_reliability_score_endpoint():
    res = client.post("/api/os/reliability-score", json={
        "amount": 24990.0,
        "payment_method": "upi",
        "bank": "State Bank of India (SBI)",
        "velocity": 1.0
    })
    assert res.status_code == 200
    data = res.json()
    assert "reliability_score" in data
    assert 0 <= data["reliability_score"] <= 100
    assert data["reliability_level"] in ["EXCELLENT", "HIGH RELIABILITY", "MODERATE RISK", "HIGH RISK", "CRITICAL RISK"]
    assert len(data["contributing_signals"]) >= 4

def test_os_preventive_intelligence_endpoint():
    res = client.post("/api/os/preventive-intelligence", json={
        "amount": 24990.0,
        "payment_method": "upi"
    })
    assert res.status_code == 200
    data = res.json()
    assert "has_preventive_alert" in data
    assert "recommended_method" in data
    assert "safety_rule" in data

def test_os_digital_twin_endpoint():
    res = client.post("/api/os/digital-twin", json={
        "amount": 24990.0,
        "payment_method": "UPI",
        "order_id": "ord_twin_demo"
    })
    assert res.status_code == 200
    data = res.json()
    assert "digital_twin_id" in data
    assert "transaction" in data
    assert "intelligence" in data
    assert "action" in data

def test_os_explain_decision_endpoint():
    res = client.post("/api/os/explain-decision", json={
        "scenario_id": "scenario_1",
        "amount": 24990.0
    })
    assert res.status_code == 200
    data = res.json()
    assert "ai_layer" in data
    assert "policy_layer" in data
    assert data["policy_layer"]["decision"] == "APPROVED"
    assert data["boundary_integrity"] == "STRICT_SEPARATION_ENFORCED"

def test_os_adaptive_recovery_endpoint():
    res = client.get("/api/os/adaptive-recovery")
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    assert len(data["categories"]) >= 5
    assert data["summary"]["overall_success_rate_pct"] > 0

def test_os_revenue_rescue_endpoint():
    res = client.get("/api/os/revenue-rescue")
    assert res.status_code == 200
    data = res.json()
    assert "total_payment_volume" in data
    assert "revenue_at_risk" in data
    assert "revenue_recovered" in data
    assert "recovery_success_rate_pct" in data

def test_os_idempotency_metrics_endpoint():
    res = client.get("/api/os/idempotency-metrics")
    assert res.status_code == 200
    data = res.json()
    assert data["duplicates_blocked_count"] >= 0
    assert data["double_charges_prevented_count"] >= 0

def test_os_system_resilience_run_endpoint():
    res = client.post("/api/os/system-resilience/run")
    assert res.status_code == 200
    data = res.json()
    assert data["total_tests"] == 8
    assert data["passed_tests"] == 8
    assert data["resilience_score_pct"] == 100.0
    assert data["status"] == "ALL_TESTS_PASSED"
