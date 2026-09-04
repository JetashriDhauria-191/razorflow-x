import uuid
from backend.database import SessionLocal
from backend.models import Payment
from backend.recovery_engine import recovery_engine

def test_autonomous_recovery_execution():
    db = SessionLocal()
    pay_id = f"pay_test_rec_{uuid.uuid4().hex[:8]}"
    
    payment = Payment(
        id=pay_id,
        order_id=f"ord_{pay_id}",
        amount=2000.0,
        currency="INR",
        gateway="razorpay",
        status="failed",
        failure_category="TIMEOUT",
        failure_severity="MEDIUM",
        failure_reason="Upstream gateway timeout",
        retry_count=0,
        recovery_status="NONE",
        recovery_strategy_used="SMART_BACKOFF_RETRY"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Trigger recovery
    result = recovery_engine.execute_recovery(payment, db)
    
    assert result["payment_id"] == pay_id
    assert result["recovery_status"] in ["RECOVERED", "EXHAUSTED"]
    assert len(result["timeline"]) >= 2
    assert result["final_status"] in ["recovered", "failed"]
    
    db.close()
