import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
try:
    from backend.models import AgentAuditTrace
except (ImportError, ModuleNotFoundError):
    from models import AgentAuditTrace

class AgentAuditLogger:
    """
    Records an immutable, explainable trace of every AI decision, tool call,
    policy evaluation, and payment event.
    """

    def log_step(
        self,
        session_id: str,
        stage: str,
        action_name: str,
        decision_explanation: str,
        policy_status: str = "PASSED",
        money_amount: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        trace_entry = {
            "session_id": session_id,
            "stage": stage,
            "action_name": action_name,
            "decision_explanation": decision_explanation,
            "policy_status": policy_status,
            "money_amount": money_amount,
            "metadata_json": metadata or {},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        if db:
            # Determine step index
            last_step = db.query(AgentAuditTrace).filter(AgentAuditTrace.session_id == session_id).order_by(AgentAuditTrace.step_index.desc()).first()
            step_idx = (last_step.step_index + 1) if last_step else 1

            db_trace = AgentAuditTrace(
                session_id=session_id,
                step_index=step_idx,
                stage=stage,
                action_name=action_name,
                decision_explanation=decision_explanation,
                policy_status=policy_status,
                money_amount=money_amount,
                metadata_json=metadata or {}
            )
            db.add(db_trace)
            db.commit()
            db.refresh(db_trace)
            trace_entry["id"] = db_trace.id
            trace_entry["step_index"] = step_idx

        return trace_entry

    def get_traces_for_session(self, session_id: str, db: Session) -> List[Dict[str, Any]]:
        traces = db.query(AgentAuditTrace).filter(AgentAuditTrace.session_id == session_id).order_by(AgentAuditTrace.step_index.asc()).all()
        return [{
            "id": t.id,
            "session_id": t.session_id,
            "step_index": t.step_index,
            "stage": t.stage,
            "action_name": t.action_name,
            "decision_explanation": t.decision_explanation,
            "policy_status": t.policy_status,
            "money_amount": t.money_amount,
            "metadata_json": t.metadata_json,
            "created_at": t.created_at.isoformat()
        } for t in traces]

    def get_all_recent_traces(self, limit: int = 50, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        if not db:
            return []
        traces = db.query(AgentAuditTrace).order_by(AgentAuditTrace.created_at.desc()).limit(limit).all()
        return [{
            "id": t.id,
            "session_id": t.session_id,
            "step_index": t.step_index,
            "stage": t.stage,
            "action_name": t.action_name,
            "decision_explanation": t.decision_explanation,
            "policy_status": t.policy_status,
            "money_amount": t.money_amount,
            "metadata_json": t.metadata_json,
            "created_at": t.created_at.isoformat()
        } for t in traces]

audit_logger = AgentAuditLogger()
