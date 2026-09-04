import datetime
from typing import List, Dict, Any, Optional

class LearningLoopEngine:
    """
    RAZORFLOW X CLOSED-LOOP COMMERCE INTELLIGENCE
    Tracks shopper journey lifecycle events:
    Intent -> AI Recommendation -> Customer Action -> Cart / Dropoff -> Outcome Analysis
    Uses outcome signals to dynamically refine recommendation ranking weights.
    """

    def __init__(self):
        self.events_log: List[Dict[str, Any]] = [
            {
                "id": "evt_init_01",
                "event_type": "SEARCH",
                "intent": "running shoes under 5000",
                "customer_id": "cust_demo_01",
                "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=15)).isoformat(),
                "outcome": "INTENT_PARSED",
                "tag": "DEMO DATA"
            },
            {
                "id": "evt_init_02",
                "event_type": "RECOMMENDATION_RENDERED",
                "intent": "running shoes under 5000",
                "recommended_products": ["SH001", "SH002", "SH003"],
                "customer_id": "cust_demo_01",
                "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=14)).isoformat(),
                "outcome": "RENDERED_6_FACTOR",
                "tag": "DEMO DATA"
            },
            {
                "id": "evt_init_03",
                "event_type": "CART_ADDED",
                "product_id": "SH001",
                "product_name": "Nike Air Zoom Pegasus Running Shoes",
                "price": 4999.0,
                "quantity": 1,
                "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=12)).isoformat(),
                "outcome": "CART_UPDATED",
                "tag": "DEMO DATA"
            },
            {
                "id": "evt_init_04",
                "event_type": "PAYMENT_SUCCESS",
                "order_id": "ORD-78421",
                "amount": 4999.0,
                "payment_method": "UPI Fast Track",
                "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=10)).isoformat(),
                "outcome": "ORDER_DELIVERED",
                "tag": "DEMO DATA"
            }
        ]
        
        self.ranking_weights = {
            "intent_weight": 0.30,
            "budget_weight": 0.25,
            "rating_weight": 0.25,
            "sla_weight": 0.10,
            "margin_weight": 0.10
        }

    def record_event(self, event_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        evt = {
            "id": f"evt_{len(self.events_log) + 1}",
            "event_type": event_type,
            **details,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "tag": "LIVE INTERACTION"
        }
        self.events_log.insert(0, evt)
        if len(self.events_log) > 200:
            self.events_log = self.events_log[:200]
        
        # Adaptive learning trigger
        if event_type == "PAYMENT_SUCCESS":
            amt = float(details.get("amount", 0))
            if amt < 2500:
                # If budget items are converting faster, boost budget weight by 2%
                self.ranking_weights["budget_weight"] = min(0.35, round(self.ranking_weights["budget_weight"] + 0.01, 2))
                self.ranking_weights["margin_weight"] = max(0.05, round(self.ranking_weights["margin_weight"] - 0.01, 2))
            else:
                self.ranking_weights["rating_weight"] = min(0.35, round(self.ranking_weights["rating_weight"] + 0.01, 2))
                
        return evt

    def get_dashboard_data(self) -> Dict[str, Any]:
        total_searches = sum(1 for e in self.events_log if e.get("event_type") == "SEARCH") + 420
        total_adds = sum(1 for e in self.events_log if e.get("event_type") == "CART_ADDED") + 184
        total_purchases = sum(1 for e in self.events_log if e.get("event_type") == "PAYMENT_SUCCESS") + 156
        total_recovers = sum(1 for e in self.events_log if "RECOVER" in str(e.get("event_type", ""))) + 28
        
        ctr = round((total_adds / max(1, total_searches)) * 100.0, 1)
        cvr = round((total_purchases / max(1, total_adds)) * 100.0, 1)

        matrix = [
            {"intent": "Running shoes under ₹5000", "top_rec": "Nike Air Zoom Pegasus (₹4,999)", "action": "Add to Cart + Buy", "outcome": "Converted (1-Day SLA)", "aov_lift": "+18.5%", "status": "SUCCESS"},
            {"intent": "Wireless ANC Headphones", "top_rec": "Sony WH-1000XM5 (₹24,990)", "action": "Attached Fast Charger Bundle", "outcome": "Upsell Converted", "aov_lift": "+35.2%", "status": "SUCCESS"},
            {"intent": "Budget Mechanical Keyboard", "top_rec": "Ant Esports MK1000 (₹1,999)", "action": "Selected Budget Saver", "outcome": "Converted (0 Abandonment)", "aov_lift": "+12.0%", "status": "SUCCESS"},
            {"intent": "Flagship 4K OLED Monitor", "top_rec": "LG UltraGear 27-inch OLED (₹72,999)", "action": "Checkout Timeout Injected", "outcome": "Auto-Recovered via UPI", "aov_lift": "+100% Retained", "status": "RECOVERED"}
        ]

        return {
            "demo_label": "SIMULATED / DEMO DATA (Labeled for Transparency)",
            "summary_metrics": {
                "total_intents_parsed": total_searches,
                "recommendation_click_rate": f"{ctr}%",
                "cart_to_checkout_conversion": f"{cvr}%",
                "autonomous_recovery_rate": "99.8%",
                "aov_expansion_yield": "+24.5% Net"
            },
            "ranking_weights": self.ranking_weights,
            "intent_outcome_matrix": matrix,
            "recent_events": self.events_log[:15]
        }

learning_loop = LearningLoopEngine()
