import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows standard out
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
try:
    from backend.main import app
except (ImportError, ModuleNotFoundError):
    from main import app

def run_verification():
    print("\n================================================================================")
    print("🔥 RAZORFLOW X — TRACK 01: AI GROWTH & AGENTIC COMMERCE VERIFICATION SUITE")
    print("================================================================================")
    client = TestClient(app)

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print(f"[PASS] 1. Health check passed: {health['platform']} | {health['track']}")

    # 2. Seed Demo Data & Catalogue
    res = client.post("/api/demo/seed")
    assert res.status_code == 200, f"Seed demo failed: {res.text}"
    print(f"[PASS] 2. Database seed & structured catalogue loaded.")

    # 3. Test Agent-Readable Product Catalogue
    res = client.get("/api/catalog?category=keyboard")
    assert res.status_code == 200
    prods = res.json()
    assert len(prods) >= 3
    print(f"[PASS] 3. Agent-Readable Catalogue verified: Found {len(prods)} keyboards (SKU {prods[0]['product_id']}, Price ₹{prods[0]['price']:,.0f}, Margin {int(prods[0]['margin']*100)}%).")

    # 4. Test Multi-Factor Explainable Recommender Engine
    res = client.get("/api/recommendations?intent=wireless%20keyboard%20for%20coding&budget=3000")
    assert res.status_code == 200
    rec_data = res.json()
    top_opt = rec_data["options"][0]
    print(f"[PASS] 4. Explainable Recommender Engine verified: Top Pick '{top_opt['product']['name']}' (Score {top_opt['recommendation_score']}/100) with {len(top_opt['why_recommended'])} explainability factors.")

    # 5. Test Conversational AI Checkout & Bounded Order Creation
    res = client.post("/api/agent/chat", json={
        "message": "I need a wireless keyboard under 2000 for coding",
        "customer_id": "cust_coding_01"
    })
    assert res.status_code == 200
    chat_res = res.json()
    sess_id = chat_res["session_id"]
    print(f"[PASS] 5a. Conversational Agent turn 1 (Discovery) verified: Intent={chat_res['intent']}, Options={len(chat_res['recommendations'])}.")

    # Proactive cross-sell add turn
    res = client.post("/api/agent/chat", json={
        "message": "yes add mouse to combo",
        "session_id": sess_id,
        "customer_id": "cust_coding_01"
    })
    assert res.status_code == 200
    cs_res = res.json()
    print(f"[PASS] 5b. Conversational Agent turn 2 (Cross-Sell Bundle) verified: Cart items={len(cs_res['cart']['items'])}, Total=₹{cs_res['cart']['final_total']:,.2f}.")

    # Bounded checkout order creation turn
    res = client.post("/api/agent/chat", json={
        "message": "buy now confirm order",
        "session_id": sess_id,
        "current_cart": cs_res["cart"]["items"]
    })
    assert res.status_code == 200
    order_res = res.json()
    assert order_res["ready_for_checkout"] is True
    assert order_res["policy_status"] == "PASSED"
    print(f"[PASS] 5c. Conversational Agent turn 3 (Bounded Order Creation) verified: Razorpay Order={order_res['razorpay_order_payload']['razorpay_order_id']}, Policy=PASSED.")

    # 6. Test Money Action Safety Gate (Limits & Blocking)
    # Test valid order
    res = client.post("/api/policy/evaluate", json={"action_type": "ORDER_CREATION", "amount": 2098.0, "customer_confirmed": True})
    assert res.status_code == 200 and res.json()["is_allowed"] is True

    # Test blocked over-budget order (₹75,000 > ₹10,000)
    res = client.post("/api/policy/evaluate", json={"action_type": "ORDER_CREATION", "amount": 75000.0, "customer_confirmed": True})
    assert res.status_code == 200
    policy_blocked = res.json()
    assert policy_blocked["is_allowed"] is False
    assert policy_blocked["status"] == "BLOCKED"
    print(f"[PASS] 6. Money Action Safety Gate verified: ₹75,000 unauthorized order successfully BLOCKED. ({policy_blocked['reason'][:70]}...)")

    # 7. Test Campaign Orchestrator (Proposal & Merchant Approval)
    res = client.post("/api/campaigns/propose", json={"prompt": "Increase sales of mechanical keyboards this week"})
    assert res.status_code == 200
    camp = res.json()
    assert camp["status"] == "PROPOSED"
    
    # Merchant approves campaign
    res = client.post(f"/api/campaigns/{camp['campaign_id']}/approve", json={"approved": True})
    assert res.status_code == 200
    assert res.json()["status"] == "ACTIVE"
    print(f"[PASS] 7. Campaign Orchestrator verified: Proposed '{camp['name']}' & Activated upon merchant approval.")

    # 8. Test Failure Demonstration & Autonomous Recovery
    res = client.post("/api/simulator/run", json={"scenario": 3, "custom_failure_type": "TIMEOUT"})
    assert res.status_code == 200
    s3 = res.json()
    assert s3["recovery_status"] == "RECOVERED"
    print(f"[PASS] 8. Failure Demonstration & Autonomous Recovery verified: Transient timeout diagnosed & self-healed. (Salvaged ₹{s3['recovered_revenue']:,.2f}).")

    # 9. Test 1,000+ Session A/B Growth Experiments Dataset
    res = client.get("/api/experiments/summary?n_sessions=1000")
    assert res.status_code == 200
    exp = res.json()
    c = exp["control_metrics"]
    t = exp["treatment_metrics"]
    u = exp["uplift_metrics"]
    print(f"[PASS] 9. 1,000-Session A/B Benchmark verified:")
    print(f"       • Conversion Rate: Control {c['conversion_rate']}% vs AI Agent {t['conversion_rate']}% ({u['conversion_lift_relative']})")
    print(f"       • Average Order Value (AOV): Control ₹{c['aov']:,.0f} vs AI Agent ₹{t['aov']:,.0f} ({u['aov_uplift']})")
    print(f"       • Revenue per Session: Control ₹{c['revenue_per_session']:,.0f} vs AI Agent ₹{t['revenue_per_session']:,.0f} ({u['revenue_per_session_lift']})")
    print(f"       • Cross-Sell Acceptance: Control {c['cross_sell_acceptance']} vs AI Agent {t['cross_sell_acceptance']}")

    # 10. Test Agent Decision Audit Trail
    res = client.get(f"/api/audit/traces/{sess_id}")
    assert res.status_code == 200
    traces = res.json()
    assert len(traces) >= 3
    print(f"[PASS] 10. Agent Decision Audit Trail verified: Found {len(traces)} timestamped decision steps for session {sess_id}.")

    # 11. Test Frontend Serving
    res = client.get("/")
    assert res.status_code == 200
    print("[PASS] 11. Frontend Single Page UI successfully served at '/'")

    print("\n================================================================================")
    print("🏆 ALL 11 VERIFICATION MODULES PASSED WITH 100% SUCCESS RATE!")
    print("🎯 RAZORFLOW X IS READY FOR TRACK 01 — AI GROWTH & AGENTIC COMMERCE SUBMISSION")
    print("================================================================================\n")

if __name__ == "__main__":
    run_verification()
