import json
from typing import Dict, Any
from sqlalchemy.orm import Session
try:
    from backend.models import Payment, WebhookLog, AuditEvent
except (ImportError, ModuleNotFoundError):
    from models import Payment, WebhookLog, AuditEvent
try:
    from backend.gateways import get_payment_gateway
except (ImportError, ModuleNotFoundError):
    from gateways import get_payment_gateway
try:
    from backend.failure_engine import failure_engine
except (ImportError, ModuleNotFoundError):
    from failure_engine import failure_engine
try:
    from backend.recovery_engine import recovery_engine
except (ImportError, ModuleNotFoundError):
    from recovery_engine import recovery_engine
try:
    from backend.risk_engine import risk_engine
except (ImportError, ModuleNotFoundError):
    from risk_engine import risk_engine

class WebhookEngine:
    def process_razorpay_webhook(self, raw_body: bytes, signature_header: str, db: Session) -> Dict[str, Any]:
        gateway = get_payment_gateway("razorpay")
        is_valid = gateway.verify_webhook_signature(raw_body, signature_header)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception:
            payload = {"raw": raw_body.decode("utf-8", errors="ignore")}

        event_type = payload.get("event", "unknown")

        # Save Webhook Log
        w_log = WebhookLog(
            gateway="razorpay",
            event_type=event_type,
            signature_valid=is_valid,
            payload_json=payload,
            processed=True
        )
        db.add(w_log)
        db.commit()

        if not is_valid:
            return {"status": "error", "message": "Invalid webhook signature", "event": event_type}

        # Extract payment entity
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment_entity.get("order_id") or payload.get("payload", {}).get("order", {}).get("entity", {}).get("id")
        rzp_payment_id = payment_entity.get("id")

        if not order_id and not rzp_payment_id:
            return {"status": "ignored", "message": "No order/payment entity in payload", "event": event_type}

        payment = None
        if rzp_payment_id:
            payment = db.query(Payment).filter(Payment.razorpay_payment_id == rzp_payment_id).first()
        if not payment and order_id:
            payment = db.query(Payment).filter(Payment.order_id == order_id).first()

        if not payment:
            # Create payment if webhook arrives before client verify
            amount = float(payment_entity.get("amount", 0)) / 100.0 if payment_entity.get("amount") else 100.0
            payment = Payment(
                id=rzp_payment_id or f"pay_wh_{order_id}",
                order_id=order_id or "ord_unknown",
                razorpay_order_id=order_id,
                razorpay_payment_id=rzp_payment_id,
                amount=amount,
                currency=payment_entity.get("currency", "INR"),
                gateway="razorpay",
                status="processing",
                customer_email=payment_entity.get("email"),
                customer_phone=payment_entity.get("contact")
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

        # Process event
        if event_type in ["payment.captured", "order.paid"]:
            payment.status = "success"
            db.add(AuditEvent(
                event_type="WEBHOOK_PAYMENT_CAPTURED",
                description=f"Webhook event '{event_type}' confirmed capture for payment {payment.id}.",
                entity_id=payment.id
            ))
            db.commit()
            return {"status": "processed", "payment_status": "success", "event": event_type}

        elif event_type == "payment.failed":
            error_code = payment_entity.get("error_code")
            error_desc = payment_entity.get("error_description") or payment_entity.get("error_reason")
            
            fail_info = failure_engine.analyze_failure(error_code, error_desc, payment_entity)
            payment.status = "failed"
            payment.failure_category = fail_info["failure_category"]
            payment.failure_severity = fail_info["failure_severity"]
            payment.failure_reason = fail_info["failure_reason"]
            payment.diagnostic_insight = fail_info["diagnostic_insight"]
            payment.recommended_recovery = fail_info["recommended_recovery"]
            payment.recovery_probability = fail_info["recovery_probability"]
            payment.recovery_strategy_used = fail_info["recommended_strategy"]
            db.commit()

            # Autonomously trigger recovery
            rec_res = recovery_engine.execute_recovery(payment, db)
            return {
                "status": "processed",
                "payment_status": payment.status,
                "recovery_status": rec_res["recovery_status"],
                "event": event_type
            }

        return {"status": "acknowledged", "event": event_type}

webhook_engine = WebhookEngine()
