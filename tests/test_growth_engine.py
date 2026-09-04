import pytest
from backend.growth_engine import growth_engine

def test_cart_growth_and_aov_calculation():
    base_items = [{"product_id": "KB001", "name": "Mechanical Keyboard", "price": 1499.0, "quantity": 1}]
    cross_sell = [{"product_id": "MS001", "name": "Wireless Mouse", "price": 599.0, "quantity": 1}]
    
    growth = growth_engine.calculate_cart_growth(base_items, cross_sell, bundle_discount_pct=5.0)
    
    assert growth["baseline_amount"] == 1499.0
    assert growth["raw_total"] == 2098.0
    assert growth["discount_amount"] > 0
    assert growth["final_total"] < 2098.0
    assert growth["incremental_revenue"] > 0
    assert growth["aov_lift_percentage"] > 30.0

def test_bundle_generation():
    bundle = growth_engine.generate_bundle("KB001")
    assert bundle is not None
    assert bundle["individual_total"] > bundle["bundle_price"]
    assert bundle["customer_savings"] > 0
