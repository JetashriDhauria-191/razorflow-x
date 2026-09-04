import pytest
from backend.recommender import recommender_engine

def test_explainable_scoring_and_recommendations():
    options = recommender_engine.recommend(
        intent_query="wireless keyboard for coding",
        customer_id="cust_coding_01",
        budget=3000.0
    )
    assert len(options) > 0
    top_pick = options[0]
    assert top_pick["recommendation_score"] > 50.0
    assert len(top_pick["why_recommended"]) > 0
    assert len(top_pick["explainable_factors"]) == 6

def test_budget_constraint_handling():
    # Strict low budget should prioritize budget items
    options = recommender_engine.recommend(
        intent_query="keyboard",
        customer_id="cust_budget_02",
        budget=1500.0
    )
    assert len(options) > 0
    # Option within 1500 should rank highest
    assert options[0]["product"]["price"] <= 1500.0
