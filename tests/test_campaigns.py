import pytest
from backend.campaign_engine import campaign_engine

def test_campaign_proposal_generation():
    camp = campaign_engine.propose_campaign(
        prompt="Increase sales of mechanical keyboards this week",
        target_category="keyboard",
        suggested_budget=5000.0
    )
    assert camp["campaign_id"].startswith("cmp_")
    assert camp["status"] == "PROPOSED"
    assert camp["policy_checked"] is True
    assert camp["merchant_approved"] is False
    assert camp["budget"] == 5000.0
