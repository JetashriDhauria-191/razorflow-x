import pytest
from backend.catalogue import catalogue_engine

def test_catalogue_search_by_category():
    results = catalogue_engine.search(category="keyboard")
    assert len(results) >= 3
    for p in results:
        assert p["category"] == "keyboard"

def test_catalogue_search_by_budget():
    results = catalogue_engine.search(max_price=1000.0)
    assert len(results) >= 2
    for p in results:
        assert p["price"] <= 1000.0

def test_catalogue_product_details_and_tags():
    prod = catalogue_engine.get_product("KB001")
    assert prod is not None
    assert prod["name"] == "Mechanical Coding Keyboard (Tenkeyless)"
    assert "coding" in prod["tags"]
    assert "MS001" in prod["cross_sell_products"]
