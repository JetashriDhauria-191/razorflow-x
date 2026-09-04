import pytest
from backend.policy_gate import policy_gate

def test_policy_gate_allows_valid_order():
    res = policy_gate.evaluate_money_action(
        action_type="ORDER_CREATION",
        amount=2098.0,
        discount_percentage=5.0,
        product_ids=["KB001", "MS001"],
        customer_confirmed=True
    )
    assert res["is_allowed"] is True
    assert res["status"] == "PASSED"

def test_policy_gate_blocks_excessive_amount():
    res = policy_gate.evaluate_money_action(
        action_type="ORDER_CREATION",
        amount=50000.0,  # Exceeds 10,000 ceiling
        discount_percentage=0.0,
        customer_confirmed=True
    )
    assert res["is_allowed"] is False
    assert res["status"] == "BLOCKED"
    assert "exceeds merchant maximum policy ceiling" in res["reason"]

def test_policy_gate_blocks_excessive_discount():
    res = policy_gate.evaluate_money_action(
        action_type="ORDER_CREATION",
        amount=1500.0,
        discount_percentage=45.0,  # Exceeds 20% max discount
        customer_confirmed=True
    )
    assert res["is_allowed"] is False
    assert res["status"] == "BLOCKED"
    assert "exceeds merchant discount cap" in res["reason"]

def test_policy_gate_blocks_unconfirmed_action():
    res = policy_gate.evaluate_money_action(
        action_type="ORDER_CREATION",
        amount=1500.0,
        discount_percentage=0.0,
        customer_confirmed=False  # Auto-purchase attempt
    )
    assert res["is_allowed"] is False
    assert res["status"] == "BLOCKED"
    assert "explicit customer confirmation" in res["reason"]
