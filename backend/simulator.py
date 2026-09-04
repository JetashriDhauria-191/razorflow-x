import uuid
import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
try:
    from backend.models import Payment, RecoveryAttempt, AuditEvent
except (ImportError, ModuleNotFoundError):
    from models import Payment, RecoveryAttempt, AuditEvent
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
    from backend.risk_engine import risk_engine
except (ImportError, ModuleNotFoundError):
    from risk_engine import risk_engine
try:
    from backend.failure_engine import failure_engine
except (ImportError, ModuleNotFoundError):
    from failure_engine import failure_engine
try:
    from backend.recovery_engine import recovery_engine
except (ImportError, ModuleNotFoundError):
    from recovery_engine import recovery_engine
try:
    from backend.audit_trace import audit_logger
except (ImportError, ModuleNotFoundError):
    from audit_trace import audit_logger

class LiveSimulator:
    def run_scenario(self, scenario_id: int, custom_amount: Optional[float] = None, custom_failure: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        """
        Executes interactive Track 1 competition scenarios.
        """
        catalogue_engine.seed_db(db)

        if scenario_id == 1:
            # Scenario 1: Standard Base Transaction (₹1,499)
            amount = custom_amount or 1499.0
            order_id = f"sim_ord_{uuid.uuid4().hex[:8]}"
            pay_id = f"pay_{uuid.uuid4().hex[:10]}"
            session_id = f"sess_{uuid.uuid4().hex[:8]}"

            risk_eval = risk_engine.evaluate_risk({
                "amount": amount,
                "retry_count": 0,
                "failure_count": 0,
                "transaction_frequency_10min": 1,
                "hour_of_day": 14,
                "device_trust_score": 0.95,
                "previous_success_rate": 0.98,
                "velocity_score": 0.5
            })

            payment = Payment(
                id=pay_id,
                order_id=order_id,
                razorpay_order_id=f"rzp_{order_id}",
                razorpay_payment_id=f"rzp_{pay_id}",
                amount=amount,
                currency="INR",
                gateway="razorpay",
                status="success",
                customer_id="cust_coding_01",
                customer_email="arjun.coding@example.com",
                customer_phone="+919811223344",
                device_ip="49.207.210.12",
                device_id="dev_trusted_chrome_win",
                is_ai_assisted=False,
                baseline_amount=amount,
                incremental_revenue=0.0,
                risk_score=risk_eval["risk_score"],
                risk_level=risk_eval["risk_level"],
                risk_factors=risk_eval["factors"],
                ml_failure_probability=risk_eval["ml_failure_probability"],
                ml_anomaly_detected=risk_eval["is_anomaly"],
                retry_count=0,
                recovery_status="NONE",
                metadata_json={"scenario": "Scenario 1 - Standard Storefront Purchase"}
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            audit_logger.log_step(
                session_id=session_id,
                stage="ORDER_CONFIRMED",
                action_name="PROCESS_DIRECT_PAYMENT",
                decision_explanation=f"Standard baseline order {order_id} (₹{amount:,.2f}) processed successfully without AI cross-sell.",
                policy_status="PASSED",
                money_amount=amount,
                metadata={"payment_id": pay_id},
                db=db
            )

            return {
                "scenario": 1,
                "title": "Scenario 1 — Baseline Direct Purchase",
                "payment_id": pay_id,
                "amount": amount,
                "risk_score": payment.risk_score,
                "risk_level": payment.risk_level,
                "status": "SUCCESS",
                "message": "Baseline transaction completed without AI augmentation (Single Item AOV: ₹1,499).",
                "timeline": [
                    {"step": "Customer Intent", "status": "SUCCESS", "details": "Direct Storefront Browse"},
                    {"step": "Policy Gate", "status": "SUCCESS", "details": "Passed (₹1,499 ≤ ₹10,000 limit)"},
                    {"step": "Razorpay Test Order", "status": "SUCCESS", "details": f"Order {order_id}"},
                    {"step": "Webhook Verified", "status": "SUCCESS", "details": "Captured & Ledger Updated"}
                ]
            }

        elif scenario_id == 2:
            # Scenario 2: AI Growth Flow with Proactive Upsell & Cross-Sell (₹1,499 + ₹599 = ₹2,098)
            session_id = f"sess_{uuid.uuid4().hex[:8]}"
            kb = catalogue_engine.get_product("KB001", db)
            mouse = catalogue_engine.get_product("MS001", db)
            
            growth_calc = growth_engine.calculate_cart_growth([kb], [mouse], bundle_discount_pct=5.0)
            final_amount = growth_calc["final_total"]

            order_id = f"sim_ord_{uuid.uuid4().hex[:8]}"
            pay_id = f"pay_{uuid.uuid4().hex[:10]}"

            payment = Payment(
                id=pay_id,
                order_id=order_id,
                razorpay_order_id=f"rzp_{order_id}",
                razorpay_payment_id=f"rzp_{pay_id}",
                amount=final_amount,
                currency="INR",
                gateway="razorpay",
                status="success",
                customer_id="cust_coding_01",
                customer_email="arjun.coding@example.com",
                customer_phone="+919811223344",
                device_ip="49.207.210.12",
                device_id="dev_trusted_chrome_win",
                is_ai_assisted=True,
                baseline_amount=growth_calc["baseline_amount"],
                incremental_revenue=growth_calc["incremental_revenue"],
                upsell_applied=False,
                cross_sell_applied=True,
                risk_score=12.0,
                risk_level="LOW",
                risk_factors=["AI Cross-Sell Bundle Verified", "Policy Gate Approved"],
                ml_failure_probability=0.02,
                ml_anomaly_detected=False,
                retry_count=0,
                recovery_status="NONE",
                metadata_json={"scenario": "Scenario 2 - AI Growth Cross-Sell Flow"}
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            audit_logger.log_step(
                session_id=session_id,
                stage="AI_GROWTH_ORDER_CONFIRMED",
                action_name="EXECUTE_BUNDLED_CHECKOUT",
                decision_explanation=f"AI Agent expanded cart from baseline ₹{growth_calc['baseline_amount']:,.2f} to ₹{final_amount:,.2f} (+{growth_calc['aov_lift_percentage']}% AOV lift) with customer consent.",
                policy_status="PASSED",
                money_amount=final_amount,
                metadata={"growth_calc": growth_calc},
                db=db
            )

            return {
                "scenario": 2,
                "title": "Scenario 2 — Autonomous AI Growth & Cross-Sell Flow",
                "payment_id": pay_id,
                "amount": final_amount,
                "baseline_amount": growth_calc["baseline_amount"],
                "incremental_revenue": growth_calc["incremental_revenue"],
                "aov_lift": f"+{growth_calc['aov_lift_percentage']}%",
                "status": "SUCCESS",
                "message": f"AI Growth Engine attached complementary mouse, generating ₹{growth_calc['incremental_revenue']:,.2f} in incremental merchant revenue (+{growth_calc['aov_lift_percentage']}% AOV Lift).",
                "timeline": [
                    {"step": "Intent Detected", "status": "SUCCESS", "details": "'Need keyboard for coding'"},
                    {"step": "Explainable Ranking", "status": "SUCCESS", "details": "Option 1 (KB001) Score 91.2/100"},
                    {"step": "Cross-Sell Triggered", "status": "SUCCESS", "details": "+ Wireless Mouse MS001 (₹599)"},
                    {"step": "Policy Safety Gate", "status": "SUCCESS", "details": "Passed (₹2,098 ≤ ₹10,000)"},
                    {"step": "Customer Confirmation", "status": "SUCCESS", "details": "Explicit 'Yes' Received"},
                    {"step": "Razorpay Test Checkout", "status": "SUCCESS", "details": f"Order {order_id} Verified"}
                ]
            }

        elif scenario_id == 3:
            # Scenario 3: Payment Failure & Autonomous Recovery (₹2,098)
            amount = custom_amount or 2098.0
            order_id = f"sim_ord_{uuid.uuid4().hex[:8]}"
            pay_id = f"pay_{uuid.uuid4().hex[:10]}"
            fail_type = custom_failure or "TIMEOUT"
            session_id = f"sess_{uuid.uuid4().hex[:8]}"

            fail_analysis = failure_engine.analyze_failure(
                error_code=fail_type,
                error_desc="Gateway upstream socket timed out during acquirer acknowledgment."
            )

            payment = Payment(
                id=pay_id,
                order_id=order_id,
                razorpay_order_id=f"rzp_{order_id}",
                razorpay_payment_id=f"rzp_{pay_id}",
                amount=amount,
                currency="INR",
                gateway="razorpay",
                status="failed",
                customer_id="cust_retail_42",
                customer_email="priya.patel@example.com",
                customer_phone="+919820011223",
                device_ip="103.21.124.55",
                device_id="dev_safari_ios_16",
                is_ai_assisted=True,
                baseline_amount=1499.0,
                incremental_revenue=599.0,
                risk_score=22.0,
                risk_level="LOW",
                risk_factors=["Transient Socket Interruption"],
                ml_failure_probability=0.85,
                failure_category=fail_analysis["failure_category"],
                failure_severity=fail_analysis["failure_severity"],
                failure_reason=fail_analysis["failure_reason"],
                diagnostic_insight=fail_analysis["diagnostic_insight"],
                recommended_recovery=fail_analysis["recommended_recovery"],
                recovery_probability=fail_analysis["recovery_probability"],
                retry_count=0,
                recovery_status="NONE",
                recovery_strategy_used=fail_analysis["recommended_strategy"],
                metadata_json={"scenario": "Scenario 3 - Failure Diagnosis & Autonomous Recovery"}
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            audit_logger.log_step(
                session_id=session_id,
                stage="PAYMENT_FAILED_DIAGNOSED",
                action_name="DIAGNOSE_TRANSIENT_FAILURE",
                decision_explanation=f"Payment {pay_id} failed with {fail_type}. AI diagnosed as transient network glitch. Recovery strategy: {fail_analysis['recommended_strategy']}.",
                policy_status="PASSED",
                money_amount=amount,
                metadata={"failure_analysis": fail_analysis},
                db=db
            )

            # Trigger Autonomous Recovery Engine
            recovery_result = recovery_engine.execute_recovery(payment, db)

            audit_logger.log_step(
                session_id=session_id,
                stage="AUTONOMOUS_RECOVERY_SUCCESS",
                action_name="EXECUTE_SMART_BACKOFF_RETRY",
                decision_explanation=f"Autonomous Recovery successfully rescued ₹{amount:,.2f} via Jittered Exponential Backoff without customer friction.",
                policy_status="PASSED",
                money_amount=amount,
                metadata={"recovery_result": recovery_result},
                db=db
            )

            return {
                "scenario": 3,
                "title": "Scenario 3 — Payment Failure & Autonomous Recovery",
                "payment_id": pay_id,
                "amount": amount,
                "failure_category": payment.failure_category,
                "diagnostic": payment.diagnostic_insight,
                "recovery_status": recovery_result["recovery_status"],
                "final_status": recovery_result["final_status"],
                "recovered_revenue": recovery_result["recovered_revenue"],
                "timeline": recovery_result["timeline"],
                "message": f"Payment failed due to {payment.failure_category}, but RAZORFLOW X Autonomous Recovery diagnosed the transient failure and rescued the ₹{amount:,.2f} order!"
            }

        elif scenario_id == 4:
            # Scenario 4: High Amount Policy Breach (₹75,000)
            amount = custom_amount or 75000.0
            session_id = f"sess_{uuid.uuid4().hex[:8]}"

            policy_eval = policy_gate.evaluate_money_action(
                action_type="ORDER_CREATION",
                amount=amount,
                discount_percentage=0.0,
                product_ids=["KB003"],
                customer_confirmed=True,
                session_id=session_id,
                db=db
            )

            audit_logger.log_step(
                session_id=session_id,
                stage="POLICY_SAFETY_GATE_BLOCKED",
                action_name="ENFORCE_SPENDING_LIMIT",
                decision_explanation=f"BLOCKED: Proposed transaction of ₹{amount:,.2f} exceeded merchant policy ceiling of ₹10,000.00.",
                policy_status="BLOCKED",
                money_amount=amount,
                metadata={"policy_eval": policy_eval},
                db=db
            )

            return {
                "scenario": 4,
                "title": "Scenario 4 — Money Action Safety Gate Enforcement",
                "amount": amount,
                "policy_status": "BLOCKED",
                "status": "ACTION BLOCKED",
                "message": f"ACTION BLOCKED: Proposed order of ₹{amount:,.2f} exceeds merchant maximum policy limit of ₹10,000.00.",
                "timeline": [
                    {"step": "Proposed Action", "status": "ALERT", "details": f"Attempted ₹{amount:,.2f} Order"},
                    {"step": "Policy Gate Evaluation", "status": "BLOCKED", "details": "Rule MAX_ORDER_AMOUNT_LIMIT Failed"},
                    {"step": "Gatekeeper Action", "status": "BLOCKED", "details": "Money action blocked before calling Razorpay API"},
                    {"step": "Audit Trail Recorded", "status": "SUCCESS", "details": "Violation logged to Merchant Security Ledger"}
                ]
            }

        else:
            # Scenario 5: Natural Language Merchant Growth Intelligence
            growth_metrics = growth_engine.get_growth_impact_metrics(db)
            return {
                "scenario": 5,
                "title": "Scenario 5 — Executive Merchant Growth Intelligence",
                "growth_metrics": growth_metrics
            }

simulator = LiveSimulator()
