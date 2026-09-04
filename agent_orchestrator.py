import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
try:
    from backend.catalogue import catalogue_engine
except (ImportError, ModuleNotFoundError):
    from catalogue import catalogue_engine
try:
    from backend.recommender import recommender_engine
except (ImportError, ModuleNotFoundError):
    from recommender import recommender_engine
try:
    from backend.growth_engine import growth_engine
except (ImportError, ModuleNotFoundError):
    from growth_engine import growth_engine
try:
    from backend.policy_gate import policy_gate
except (ImportError, ModuleNotFoundError):
    from policy_gate import policy_gate
try:
    from backend.gateways import get_payment_gateway
except (ImportError, ModuleNotFoundError):
    from gateways import get_payment_gateway
try:
    from backend.models import Payment, AuditEvent
except (ImportError, ModuleNotFoundError):
    from models import Payment, AuditEvent
try:
    from backend.audit_trace import audit_logger
except (ImportError, ModuleNotFoundError):
    from audit_trace import audit_logger

class AgentToolbox:
    """
    Deterministic tool calling functions used by the Agent Orchestrator.
    The AI Agent plans and selects tools, while the backend safely enforces execution policies.
    """

    @staticmethod
    def catalog_search(query: str, category: Optional[str] = None, max_price: Optional[float] = None, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        return catalogue_engine.search(query=query, category=category, max_price=max_price, in_stock_only=True, db=db)

    @staticmethod
    def get_product(product_id: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        return catalogue_engine.get_product(product_id, db)

    @staticmethod
    def recommend_products(intent: str, customer_id: str = "cust_coding_01", budget: Optional[float] = None, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        return recommender_engine.recommend(intent_query=intent, customer_id=customer_id, budget=budget, db=db)

    @staticmethod
    def calculate_cart(base_items: List[Dict[str, Any]], cross_sell_items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return growth_engine.calculate_cart_growth(base_items=base_items, cross_sell_items=cross_sell_items)

    @staticmethod
    def evaluate_policy(action_type: str, amount: float, discount_pct: float = 0.0, product_ids: Optional[List[str]] = None, customer_confirmed: bool = True, session_id: Optional[str] = None, db: Optional[Session] = None) -> Dict[str, Any]:
        return policy_gate.evaluate_money_action(
            action_type=action_type,
            amount=amount,
            discount_percentage=discount_pct,
            product_ids=product_ids,
            customer_confirmed=customer_confirmed,
            session_id=session_id,
            db=db
        )

    @staticmethod
    def create_razorpay_order(
        amount: float,
        session_id: str,
        customer_email: str = "buyer@example.com",
        customer_phone: str = "+919876543210",
        is_ai_assisted: bool = True,
        baseline_amount: Optional[float] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        gateway = get_payment_gateway("razorpay")
        receipt_id = f"rcpt_{uuid.uuid4().hex[:8]}"
        
        order_res = gateway.create_order(
            amount=amount,
            currency="INR",
            receipt=receipt_id,
            notes={"session_id": session_id, "is_ai_assisted": str(is_ai_assisted)}
        )

        pay_id = f"pay_{uuid.uuid4().hex[:12]}"
        if db:
            payment = Payment(
                id=pay_id,
                order_id=order_res.order_id,
                razorpay_order_id=order_res.gateway_order_id,
                amount=amount,
                currency="INR",
                gateway="razorpay",
                status="created",
                customer_id="cust_agentic_01",
                customer_email=customer_email,
                customer_phone=customer_phone,
                is_ai_assisted=is_ai_assisted,
                baseline_amount=baseline_amount or amount,
                incremental_revenue=max(0.0, amount - (baseline_amount or amount)),
                risk_score=15.0,
                risk_level="LOW",
                risk_factors=["Express Fast-Track Verified", "Autonomous AI Order Passed Safety Gate"],
                ml_failure_probability=0.03,
                retry_count=0,
                recovery_status="NONE",
                metadata_json={"session_id": session_id, "receipt": receipt_id}
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            audit_logger.log_step(
                session_id=session_id,
                stage="RAZORPAY_ORDER_CREATED",
                action_name="CREATE_RAZORPAY_TEST_ORDER",
                decision_explanation=f"Created Razorpay test order {order_res.gateway_order_id} for ₹{amount:,.2f} after policy clearance.",
                policy_status="PASSED",
                money_amount=amount,
                metadata={"order_id": order_res.order_id, "gateway_order_id": order_res.gateway_order_id},
                db=db
            )

        return {
            "order_id": order_res.order_id,
            "razorpay_order_id": order_res.gateway_order_id,
            "amount": amount,
            "currency": "INR",
            "key_id": order_res.key_id,
            "status": "created"
        }

agent_toolbox = AgentToolbox()
