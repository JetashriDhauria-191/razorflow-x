import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_create_order_and_verify():
    # 1. Create order
    create_res = client.post("/api/payments/create-order", json={
        "amount": 750.0,
        "currency": "INR",
        "customer_id": "cust_test_unit",
        "customer_email": "unit_test@example.com"
    })
    assert create_res.status_code == 200
    data = create_res.json()
    assert "order_id" in data
    assert data["amount"] == 750.0
    assert "risk_score" in data
    assert data["status"] == "created"

    order_id = data["order_id"]
    rzp_order_id = data["razorpay_order_id"]

    # 2. Verify payment (Success flow)
    verify_res = client.post("/api/payments/verify", json={
        "order_id": order_id,
        "razorpay_order_id": rzp_order_id,
        "razorpay_payment_id": f"pay_rzp_test_{order_id}",
        "razorpay_signature": "test_signature_valid"
    })
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["status"] == "success"

def test_verify_payment_simulated_failure():
    # 1. Create order
    create_res = client.post("/api/payments/create-order", json={
        "amount": 1200.0,
        "currency": "INR"
    })
    order_id = create_res.json()["order_id"]

    # 2. Verify with injected failure
    verify_res = client.post("/api/payments/verify", json={
        "order_id": order_id,
        "simulated_failure": "TIMEOUT"
    })
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["status"] == "failed"
    assert v_data["failure_category"] == "TIMEOUT"
    assert v_data["recovery_probability"] > 0.7
