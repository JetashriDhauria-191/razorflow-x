import pytest
from backend.agentic_checkout import agentic_checkout

def test_intent_parsing_and_discovery():
    res = agentic_checkout.process_customer_turn("I need a wireless keyboard under 2000 for coding")
    assert res["intent"] == "DISCOVERY"
    assert len(res["recommendations"]) > 0
    assert "cross_sell_offer" in res

def test_add_cross_sell_flow():
    res = agentic_checkout.process_customer_turn("yes add mouse to combo")
    assert res["intent"] == "ADD_CROSS_SELL"
    assert res["cart"]["is_bundled"] is True
    assert len(res["cart"]["items"]) == 2

def test_bounded_checkout_order_creation():
    res = agentic_checkout.process_customer_turn(
        message="buy now confirm order",
        current_cart=[{"product_id": "KB001", "name": "Keyboard", "price": 1499.0, "quantity": 1}]
    )
    assert res["ready_for_checkout"] is True
    assert res["policy_status"] == "PASSED"
    assert "razorpay_order_payload" in res
