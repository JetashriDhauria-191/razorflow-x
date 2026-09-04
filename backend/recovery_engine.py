import datetime
import time
import random
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
try:
    from backend.models import Payment, RecoveryAttempt, AuditEvent
except (ImportError, ModuleNotFoundError):
    from models import Payment, RecoveryAttempt, AuditEvent
try:
    from backend.failure_engine import failure_engine
except (ImportError, ModuleNotFoundError):
    from failure_engine import failure_engine

class AutonomousRecoveryEngine:
    MAX_RETRIES = 3

    def execute_recovery(self, payment: Payment, db: Session, custom_strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes an autonomous recovery sequence for a failed transaction.
        Evaluates failure cause, executes multi-attempt recovery strategy,
        and logs full timeline telemetry.
        """
        if payment.status in ["success", "recovered"]:
            return {
                "payment_id": payment.id,
                "final_status": payment.status,
                "recovery_status": payment.recovery_status,
                "attempts_made": payment.retry_count,
                "timeline": self._build_timeline(payment),
                "recovered_revenue": payment.amount,
                "message": "Payment is already successful or recovered."
            }

        strategy = custom_strategy or payment.recovery_strategy_used or "SMART_BACKOFF_RETRY"
        payment.recovery_status = "IN_PROGRESS"
        db.commit()

        # Execute recovery attempts
        start_attempt = payment.retry_count + 1
        timeline_events = []
        is_recovered = False

        for attempt_num in range(start_attempt, self.MAX_RETRIES + 1):
            payment.retry_count = attempt_num
            
            # Calculate backoff delay (simulated or real delay)
            delay_ms = int(attempt_num * 1500 + random.randint(100, 500))
            
            # Simulation of recovery outcome based on strategy & failure category
            attempt_success = self._simulate_recovery_attempt(payment, strategy, attempt_num)

            attempt_record = RecoveryAttempt(
                payment_id=payment.id,
                attempt_number=attempt_num,
                strategy=strategy,
                status="SUCCESS" if attempt_success else "FAILED",
                error_message=None if attempt_success else f"Transient bottleneck persisted during {strategy}",
                recovery_delay_ms=delay_ms,
                gateway_response={
                    "attempt": attempt_num,
                    "strategy": strategy,
                    "latency_ms": delay_ms,
                    "recovered": attempt_success
                }
            )
            db.add(attempt_record)
            db.commit()
            db.refresh(attempt_record)

            timeline_events.append({
                "attempt_number": attempt_num,
                "strategy": strategy,
                "status": "SUCCESS" if attempt_success else "FAILED",
                "delay_ms": delay_ms,
                "timestamp": attempt_record.created_at.isoformat()
            })

            if attempt_success:
                is_recovered = True
                payment.status = "recovered"
                payment.recovery_status = "RECOVERED"
                payment.recovery_strategy_used = strategy
                
                # Log audit event
                audit = AuditEvent(
                    event_type="PAYMENT_RECOVERED",
                    description=f"Payment {payment.id} of ₹{payment.amount:,.2f} successfully salvaged on attempt #{attempt_num} using {strategy}.",
                    entity_id=payment.id,
                    metadata_json={"attempts": attempt_num, "amount": payment.amount}
                )
                db.add(audit)
                db.commit()
                break
            else:
                # Switch strategy for next attempt if initial backoff failed
                if strategy == "SMART_BACKOFF_RETRY" and attempt_num == 1:
                    strategy = "ALTERNATE_GATEWAY"
                elif strategy == "ALTERNATE_GATEWAY" and attempt_num == 2:
                    strategy = "METHOD_FALLBACK"

        if not is_recovered:
            payment.recovery_status = "EXHAUSTED"
            db.commit()

        db.refresh(payment)

        return {
            "payment_id": payment.id,
            "final_status": payment.status,
            "recovery_status": payment.recovery_status,
            "attempts_made": payment.retry_count,
            "timeline": self._build_timeline(payment),
            "recovered_revenue": payment.amount if is_recovered else 0.0,
            "message": f"Autonomous recovery completed: Status is {payment.recovery_status}."
        }

    def _simulate_recovery_attempt(self, payment: Payment, strategy: str, attempt_num: int) -> bool:
        """
        Determines recovery probability based on failure type and strategy.
        High success for TIMEOUT and NETWORK_FAILURE on attempt 2 or 3.
        """
        cat = payment.failure_category or "TIMEOUT"
        
        # High recovery probability on attempt 2/3 for timeouts & network glitches
        if cat in ["TIMEOUT", "NETWORK_FAILURE", "GATEWAY_FAILURE"]:
            if attempt_num >= 2:
                return True
            return False
        elif cat == "BANK_FAILURE":
            if strategy == "ALTERNATE_GATEWAY" and attempt_num >= 2:
                return True
            return False
        elif cat == "INSUFFICIENT_FUNDS":
            # Hard declines rarely succeed without method switch
            if strategy == "METHOD_FALLBACK" and attempt_num >= 3:
                return True
            return False
        elif cat == "AUTHENTICATION_FAILURE":
            if strategy == "CUSTOMER_ALERT" or attempt_num >= 2:
                return True
            return False
        
        return attempt_num >= 2

    def _build_timeline(self, payment: Payment) -> List[Dict[str, Any]]:
        timeline = []
        # Initial transaction attempt
        timeline.append({
            "step": "Initial Payment Request",
            "status": "FAILED" if payment.failure_category else "SUCCESS",
            "details": payment.failure_reason or "Initial submission",
            "category": payment.failure_category or "NONE",
            "timestamp": payment.created_at.isoformat() if payment.created_at else ""
        })

        for att in payment.recovery_attempts:
            timeline.append({
                "step": f"Recovery Attempt #{att.attempt_number} ({att.strategy})",
                "status": att.status,
                "details": att.error_message or "Successfully recovered and confirmed with acquirer network.",
                "delay_ms": att.recovery_delay_ms,
                "timestamp": att.created_at.isoformat() if att.created_at else ""
            })
        return timeline

recovery_engine = AutonomousRecoveryEngine()
