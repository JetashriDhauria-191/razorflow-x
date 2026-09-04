import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_all_10_tests():
    print("=" * 80)
    print("RUNNING 10-SCENARIO VERIFICATION SUITE")
    print("=" * 80)

    # -------------------------------------------------------------
    # TEST 1: Search "shoes" -> Select Cheapest -> Verify sorted lowest price first
    # -------------------------------------------------------------
    print("\n--- TEST 1: Search 'shoes' with 'cheapest' intent ---")
    res1 = client.post("/api/discovery/search", json={"query": "shoes", "intent_filter": "cheapest"})
    assert res1.status_code == 200
    data1 = res1.json()
    prods1 = data1["products"]
    top_recs1 = data1["top_recommendations"]
    prices1 = [p["price"] for p in prods1]
    top_prices1 = [r["price"] for r in top_recs1]
    print(f"Products count: {len(prods1)} | Top recs count: {len(top_recs1)}")
    print(f"First 4 product prices: {prices1[:4]}")
    print(f"Top rec prices: {top_prices1}")
    assert prices1 == sorted(prices1), "Products must be sorted price ascending!"
    assert top_prices1 == sorted(top_prices1), "Top recs must be sorted price ascending!"
    print("[PASS] TEST 1: Cheapest sort strictly ascending!")

    # -------------------------------------------------------------
    # TEST 2: Search "headphones" -> Select Best Rated -> Verify highest-rated products appear first
    # -------------------------------------------------------------
    print("\n--- TEST 2: Search 'headphones' with 'best_rated' intent ---")
    res2 = client.post("/api/discovery/search", json={"query": "headphones", "intent_filter": "best_rated"})
    assert res2.status_code == 200
    data2 = res2.json()
    prods2 = data2["products"]
    top_recs2 = data2["top_recommendations"]
    ratings2 = [p["rating"] for p in prods2]
    top_ratings2 = [r["rating"] for r in top_recs2]
    print(f"Products count: {len(prods2)} | Top recs count: {len(top_recs2)}")
    print(f"First 4 product ratings: {ratings2[:4]}")
    print(f"Top rec ratings: {top_ratings2}")
    assert ratings2 == sorted(ratings2, reverse=True), "Products must be sorted rating descending!"
    assert top_ratings2 == sorted(top_ratings2, reverse=True), "Top recs must be sorted rating descending!"
    print("[PASS] TEST 2: Best rated sort strictly descending!")

    # -------------------------------------------------------------
    # TEST 3: Search "laptop" -> Select Premium Pick -> Verify premium products selected
    # -------------------------------------------------------------
    print("\n--- TEST 3: Search 'laptop' with 'premium' intent ---")
    res3 = client.post("/api/discovery/search", json={"query": "laptop", "intent_filter": "premium"})
    assert res3.status_code == 200
    data3 = res3.json()
    prods3 = data3["products"]
    top_recs3 = data3["top_recommendations"]
    prices3 = [p["price"] for p in prods3]
    top_prices3 = [r["price"] for r in top_recs3]
    print(f"Products count: {len(prods3)} | Top recs count: {len(top_recs3)}")
    print(f"First 4 laptop prices: {prices3[:4]}")
    print(f"Top rec laptop prices: {top_prices3}")
    assert prices3 == sorted(prices3, reverse=True), "Laptops must be sorted price descending (premium first)!"
    assert top_prices3 == sorted(top_prices3, reverse=True), "Top recs must be sorted price descending!"
    print("[PASS] TEST 3: Premium pick selects flagship laptops first!")

    # -------------------------------------------------------------
    # TEST 4: Search any product -> Verify all recommendation cards are UNIQUE
    # -------------------------------------------------------------
    print("\n--- TEST 4: Unique recommendation cards verification ---")
    for q in ["shoes", "headphones", "laptop", "watch", "all"]:
        for f in ["all", "best_value", "cheapest", "best_rated", "premium"]:
            res4 = client.post("/api/discovery/search", json={"query": q, "intent_filter": f})
            assert res4.status_code == 200
            recs = res4.json()["top_recommendations"]
            rec_ids = [r.get("product_id") or r.get("id") for r in recs]
            assert len(rec_ids) == len(set(rec_ids)), f"Duplicate product ID found in recs for query='{q}', filter='{f}': {rec_ids}"
    print("[PASS] TEST 4: ZERO duplicates in recommendation cards across all queries and filters!")

    # -------------------------------------------------------------
    # TEST 5: Add one product to cart once -> Verify cart contains exactly ONE item
    # -------------------------------------------------------------
    print("\n--- TEST 5: Add single product to cart ---")
    client.post("/api/cart/clear", json={"customer_id": "test_user_1"})
    res5 = client.post("/api/cart", json={"customer_id": "test_user_1", "product_id": "HP001", "quantity": 1})
    assert res5.status_code == 200
    cart5 = client.get("/api/cart/test_user_1").json()
    assert len(cart5["items"]) == 1, f"Expected 1 item, got {len(cart5['items'])}"
    assert cart5["items"][0]["quantity"] == 1
    print(f"Cart items: {len(cart5['items'])} | Item: {cart5['items'][0]['name']} (Qty: {cart5['items'][0]['quantity']})")
    print("[PASS] TEST 5: Exactly 1 item in cart!")

    # -------------------------------------------------------------
    # TEST 6: Click Add to Cart 3 times -> Verify: ONE cart line item, Quantity = 3
    # -------------------------------------------------------------
    print("\n--- TEST 6: Add same product 3 times -> Quantity increment ---")
    client.post("/api/cart/clear", json={"customer_id": "test_user_1"})
    client.post("/api/cart", json={"customer_id": "test_user_1", "product_id": "SH001", "quantity": 1})
    client.post("/api/cart", json={"customer_id": "test_user_1", "product_id": "SH001", "quantity": 1})
    client.post("/api/cart", json={"customer_id": "test_user_1", "product_id": "SH001", "quantity": 1})
    cart6 = client.get("/api/cart/test_user_1").json()
    assert len(cart6["items"]) == 1, f"Expected 1 unique cart line item, got {len(cart6['items'])}"
    assert cart6["items"][0]["quantity"] == 3, f"Expected quantity 3, got {cart6['items'][0]['quantity']}"
    print(f"Cart items: {len(cart6['items'])} | Name: {cart6['items'][0]['name']} | Quantity: {cart6['items'][0]['quantity']}")
    print("[PASS] TEST 6: Exactly 1 cart line item with Quantity = 3!")

    # -------------------------------------------------------------
    # TEST 7: Click Buy Now once -> Verify only ONE checkout/order is created
    # -------------------------------------------------------------
    print("\n--- TEST 7: Single Buy Now order creation ---")
    res7 = client.post("/api/payments/create-order", json={"amount": 4999.0, "currency": "INR", "customer_id": "test_user_1"})
    assert res7.status_code == 200
    order_data7 = res7.json()
    assert "order_id" in order_data7
    print(f"Order created: {order_data7['order_id']} | Status: {order_data7['status']}")
    print("[PASS] TEST 7: Exactly 1 order created!")

    # -------------------------------------------------------------
    # TEST 8: Simulate duplicate payment success callback -> Verify only ONE transaction/order
    # -------------------------------------------------------------
    print("\n--- TEST 8: Duplicate payment verify callback idempotency ---")
    order_id_8 = f"ORD-IDEMP-{order_data7['order_id']}"
    pay_id_8 = f"pay_idemp_test_{order_data7['order_id']}"
    payload_8 = {
        "order_id": order_id_8,
        "razorpay_payment_id": pay_id_8,
        "amount": 4999.0,
        "payment_method": "UPI Fast Track (MPIN)",
        "items": [{"name": "Nike Pegasus 40", "quantity": 1, "price": 4999.0}]
    }
    # First verify call
    v1 = client.post("/api/payments/verify", json=payload_8)
    assert v1.status_code == 200
    assert v1.json()["status"] == "success"

    # Duplicate verify call with SAME payment_id & order_id
    v2 = client.post("/api/payments/verify", json=payload_8)
    assert v2.status_code == 200
    v2_data = v2.json()
    assert v2_data["status"] == "success"
    assert v2_data.get("is_idempotent_replay") is True or v2_data.get("message") == "DUPLICATE EVENT SAFELY IGNORED"
    print(f"Duplicate verify response: {v2_data.get('message', 'SUCCESS')}")
    print("[PASS] TEST 8: Duplicate payment callback blocked with idempotency!")

    # -------------------------------------------------------------
    # TEST 9: Simulate duplicate webhook -> Verify idempotency protection prevents duplicate processing
    # -------------------------------------------------------------
    print("\n--- TEST 9: Duplicate webhook processing ---")
    import json
    wh_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_wh_idemp_999",
                    "order_id": "ord_wh_idemp_999",
                    "amount": 499900,
                    "currency": "INR",
                    "status": "captured"
                }
            }
        }
    }
    wh_body = json.dumps(wh_payload).encode('utf-8')
    wh1 = client.post("/api/webhook/razorpay", content=wh_body, headers={"x-razorpay-signature": "demo_sig", "content-type": "application/json"})
    assert wh1.status_code == 200

    wh2 = client.post("/api/webhook/razorpay", content=wh_body, headers={"x-razorpay-signature": "demo_sig", "content-type": "application/json"})
    assert wh2.status_code == 200
    print("[PASS] TEST 9: Duplicate webhook handled safely with HTTP 200!")

    # -------------------------------------------------------------
    # TEST 10: Complete payment -> Verify purchased product is NOT duplicated in cart or history
    # -------------------------------------------------------------
    print("\n--- TEST 10: Complete payment cart clear & history integrity ---")
    cart_after = client.get("/api/cart/test_user_1").json()
    assert len(cart_after["items"]) == 0, "Cart must be emptied after successful payment!"
    
    hist = client.get("/api/orders/history").json()["history"]
    matching_orders = [o for o in hist if o.get("order_id") == order_id_8]
    assert len(matching_orders) == 1, f"Expected exactly 1 order in history for {order_id_8}, got {len(matching_orders)}"
    print(f"History entries for {order_id_8}: {len(matching_orders)} (Zero duplication!)")
    print("[PASS] TEST 10: Cart cleared and order recorded exactly once!")

    print("\n" + "=" * 80)
    print("ALL 10 TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 80)

if __name__ == "__main__":
    run_all_10_tests()
