import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_webhook_processing():
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_wh_unit_test_99",
                    "order_id": "ord_wh_unit_test_99",
                    "amount": 250000, # ₹2,500.00
                    "currency": "INR",
                    "status": "captured",
                    "email": "webhook_customer@example.com"
                }
            }
        }
    }

    body_bytes = json.dumps(payload).encode('utf-8')
    res = client.post(
        "/api/webhook/razorpay",
        content=body_bytes,
        headers={"x-razorpay-signature": "demo_valid_sig_123", "content-type": "application/json"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["processed", "acknowledged"]
