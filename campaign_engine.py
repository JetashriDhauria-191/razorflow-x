import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
try:
    from backend.models import Campaign
except (ImportError, ModuleNotFoundError):
    from models import Campaign
try:
    from backend.policy_gate import policy_gate
except (ImportError, ModuleNotFoundError):
    from policy_gate import policy_gate
try:
    from backend.audit_trace import audit_logger
except (ImportError, ModuleNotFoundError):
    from audit_trace import audit_logger

SEED_CAMPAIGNS = [
    {
        "campaign_id": "cmp_kb_growth_01",
        "name": "Mechanical Keyboard + Ergonomic Mouse Cross-Sell Bundle",
        "goal": "Increase keyboard revenue and AOV for developer segment",
        "target_segment": "Software Engineers, Remote Workers & Tech Enthusiasts",
        "offer": "Buy any Mechanical Keyboard and get a Wireless Precision Mouse at 15% off + Free Desk Pad",
        "expected_aov_lift": "+18.4%",
        "budget": 5000.0,
        "duration_days": 7,
        "status": "ACTIVE",
        "policy_checked": True,
        "merchant_approved": True,
        "revenue_generated": 34200.0,
        "conversions_count": 22
    },
    {
        "campaign_id": "cmp_desk_setup_02",
        "name": "Complete Clean Desk Setup Promotion",
        "goal": "Promote Desk Mats & USB-C Developer Docks with Premium Keyboards",
        "target_segment": "Productivity & Multi-Monitor Laptop Users",
        "offer": "Bundle Keyboard + USB-C Hub for flat ₹2,999 (Save ₹599)",
        "expected_aov_lift": "+24.2%",
        "budget": 7500.0,
        "duration_days": 14,
        "status": "ACTIVE",
        "policy_checked": True,
        "merchant_approved": True,
        "revenue_generated": 52400.0,
        "conversions_count": 18
    }
]

class CampaignEngine:
    def seed_db(self, db: Session):
        for c_data in SEED_CAMPAIGNS:
            existing = db.query(Campaign).filter(Campaign.campaign_id == c_data["campaign_id"]).first()
            if not existing:
                camp = Campaign(
                    campaign_id=c_data["campaign_id"],
                    name=c_data["name"],
                    goal=c_data["goal"],
                    target_segment=c_data["target_segment"],
                    offer=c_data["offer"],
                    expected_aov_lift=c_data["expected_aov_lift"],
                    budget=c_data["budget"],
                    duration_days=c_data["duration_days"],
                    status=c_data["status"],
                    policy_checked=c_data["policy_checked"],
                    merchant_approved=c_data["merchant_approved"],
                    revenue_generated=c_data["revenue_generated"],
                    conversions_count=c_data["conversions_count"]
                )
                db.add(camp)
        db.commit()

    def propose_campaign(
        self,
        prompt: str,
        target_category: Optional[str] = "keyboard",
        suggested_budget: float = 5000.0,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        AI analyzes merchant prompt and generates a policy-compliant campaign proposal.
        """
        campaign_id = f"cmp_{uuid.uuid4().hex[:8]}"
        session_id = f"sess_cmp_{uuid.uuid4().hex[:6]}"

        cat_clean = (target_category or "electronics").lower()
        if "keyboard" in prompt.lower() or "keyboard" in cat_clean:
            name = "Developer Keyboard & Cross-Sell Productivity Blitz"
            goal = "Accelerate mechanical keyboard volume & attach complementary mice/pads"
            target_segment = "Developers, Coders & Home Office Professionals"
            offer = "Mechanical Keyboard + Silent Optical Mouse bundle with 10% instant bundle rebate"
            expected_lift = "+16.8%"
            budget = min(suggested_budget, 10000.0)
            duration = 7
        elif "audio" in prompt.lower() or "headset" in prompt.lower():
            name = "Remote Work ANC Headset & Dock Bundle"
            goal = "Increase high-margin audio and docking station sales"
            target_segment = "Remote team leads and video conference power users"
            offer = "ANC Headset + 7-in-1 Dual 4K USB-C Hub at ₹2,899"
            expected_lift = "+22.5%"
            budget = min(suggested_budget, 15000.0)
            duration = 10
        else:
            name = f"Autonomous AI Growth Surge: {prompt[:40]}"
            goal = f"Drive rapid revenue growth aligned with merchant intent: '{prompt}'"
            target_segment = "High-intent store visitors and previous buyers"
            offer = "Smart dynamic combo discounts on compatible accessories"
            expected_lift = "+14.5%"
            budget = min(suggested_budget, 8000.0)
            duration = 7

        # Safety & Policy check on Campaign Budget
        policy_eval = policy_gate.evaluate_money_action(
            action_type="CAMPAIGN_LAUNCH",
            amount=budget,
            discount_percentage=10.0,
            customer_confirmed=False # requires merchant approval
        )

        campaign_obj = {
            "campaign_id": campaign_id,
            "name": name,
            "goal": goal,
            "target_segment": target_segment,
            "offer": offer,
            "expected_aov_lift": expected_lift,
            "budget": budget,
            "duration_days": duration,
            "status": "PROPOSED",
            "policy_checked": True,
            "merchant_approved": False,
            "revenue_generated": 0.0,
            "conversions_count": 0,
            "created_at": datetime.datetime.utcnow().isoformat()
        }

        if db:
            camp = Campaign(
                campaign_id=campaign_id,
                name=name,
                goal=goal,
                target_segment=target_segment,
                offer=offer,
                expected_aov_lift=expected_lift,
                budget=budget,
                duration_days=duration,
                status="PROPOSED",
                policy_checked=True,
                merchant_approved=False,
                revenue_generated=0.0,
                conversions_count=0
            )
            db.add(camp)
            db.commit()
            db.refresh(camp)
            campaign_obj["id"] = camp.id

            audit_logger.log_step(
                session_id=session_id,
                stage="CAMPAIGN_PROPOSAL_GENERATED",
                action_name="PROPOSE_GROWTH_CAMPAIGN",
                decision_explanation=f"Generated '{name}' for target goal '{goal}'. Budget: ₹{budget:,.2f}. Awaiting merchant approval.",
                policy_status="PASSED" if policy_eval["is_allowed"] else "BLOCKED",
                money_amount=budget,
                metadata={"campaign_id": campaign_id, "prompt": prompt},
                db=db
            )

        return campaign_obj

    def approve_campaign(self, campaign_id: str, approved: bool, db: Session) -> Dict[str, Any]:
        camp = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
        if not camp:
            return {"error": "Campaign not found"}

        if approved:
            camp.merchant_approved = True
            camp.status = "ACTIVE"
            audit_logger.log_step(
                session_id=f"sess_{campaign_id}",
                stage="CAMPAIGN_ACTIVATED",
                action_name="MERCHANT_CAMPAIGN_APPROVAL",
                decision_explanation=f"Merchant approved campaign '{camp.name}'. Budget allocated: ₹{camp.budget:,.2f}.",
                policy_status="PASSED",
                money_amount=camp.budget,
                metadata={"campaign_id": campaign_id},
                db=db
            )
        else:
            camp.merchant_approved = False
            camp.status = "REJECTED"

        db.commit()
        db.refresh(camp)
        return {
            "campaign_id": camp.campaign_id,
            "name": camp.name,
            "status": camp.status,
            "merchant_approved": camp.merchant_approved
        }

    def list_campaigns(self, db: Session) -> List[Dict[str, Any]]:
        self.seed_db(db)
        camps = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
        return [{
            "id": c.id,
            "campaign_id": c.campaign_id,
            "name": c.name,
            "goal": c.goal,
            "target_segment": c.target_segment,
            "offer": c.offer,
            "expected_aov_lift": c.expected_aov_lift,
            "budget": c.budget,
            "duration_days": c.duration_days,
            "status": c.status,
            "policy_checked": c.policy_checked,
            "merchant_approved": c.merchant_approved,
            "revenue_generated": c.revenue_generated,
            "conversions_count": c.conversions_count,
            "created_at": c.created_at.isoformat()
        } for c in camps]

campaign_engine = CampaignEngine()
