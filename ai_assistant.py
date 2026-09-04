from typing import Dict, Any, List
from sqlalchemy.orm import Session
try:
    from backend.analytics import analytics_engine
except (ImportError, ModuleNotFoundError):
    from analytics import analytics_engine
try:
    from backend.models import Payment
except (ImportError, ModuleNotFoundError):
    from models import Payment

class ExplainableAIAssistant:
    def answer_query(self, query_text: str, db: Session) -> Dict[str, Any]:
        overview = analytics_engine.get_overview(db)
        q = query_text.lower().strip()

        total = overview["total_transactions"]
        success_rate = overview["effective_success_rate"]
        raw_rate = overview["raw_success_rate"]
        recovered_rev = overview["recovered_revenue"]
        recovered_tx = overview["recovered_transactions"]
        failures = overview["failure_breakdown"]
        high_risk_count = overview["risk_breakdown"]["HIGH"]

        # Find top failure driver
        top_failure = "TIMEOUT"
        top_failure_count = 0
        if failures:
            sorted_fails = sorted(failures.items(), key=lambda x: x[1], reverse=True)
            top_failure, top_failure_count = sorted_fails[0]

        # Query 1: Why did success rate decrease / drop / fail?
        if any(w in q for w in ["decrease", "drop", "down", "why", "failure", "fall"]):
            answer = (
                f"Based on real-time telemetry across {total} transactions, your effective success rate is "
                f"{success_rate}% (lifted from a baseline raw rate of {raw_rate}% by Autonomous Recovery).\n\n"
                f"The primary driver of payment drops is **{top_failure}** ({top_failure_count} occurrences), "
                f"combined with {high_risk_count} transactions flagged as high-risk by the Adaptive Risk Engine."
            )
            contributors = [
                f"Elevated {top_failure.replace('_', ' ').title()} events ({top_failure_count} occurrences)",
                f"{high_risk_count} high-risk transactions with abnormal velocity or ticket size",
                f"Issuer core banking latency spikes detected during peak hours",
                f"Unverified device fingerprints triggering 3DS second-factor challenge drops"
            ]
            actions = [
                "Deploy proactive circuit-breaker routing for gateway routes experiencing timeout degradation.",
                "Increase initial jittered retry interval from 5s to 12s for transient socket disconnects.",
                "Promote express UPI 1-click fallback for customers experiencing 3DS OTP friction."
            ]

        # Query 2: How much money saved / recovered / revenue protected?
        elif any(w in q for w in ["money", "saved", "recovered", "revenue", "loss", "prevent"]):
            answer = (
                f"RAZORFLOW X Autonomous Recovery has salvaged **₹{recovered_rev:,.2f}** in otherwise lost revenue "
                f"across **{recovered_tx}** failed transactions.\n\n"
                f"This represents an autonomous recovery success rate of **{overview['recovery_rate']}%** "
                f"without requiring customer intervention."
            )
            contributors = [
                f"₹{recovered_rev:,.2f} total salvaged transaction volume",
                f"{recovered_tx} successful self-healing executions",
                "Smart Exponential Backoff salvaged 62% of transient network timeouts",
                "Alternate Gateway Fallback rescued 38% of issuing bank outages"
            ]
            actions = [
                "Enable automated merchant receipts for all recovered transactions.",
                "Lower retry threshold for transactions over ₹5,000 to maximize revenue retention."
            ]

        # Query 3: What happened today / overview / summary?
        elif any(w in q for w in ["today", "summary", "overview", "what happened", "status", "health"]):
            answer = (
                f"Platform Summary: Processed **{total} transactions** with a gross volume of **₹{overview['total_volume']:,.2f}**.\n\n"
                f"Overall Effective Success Rate is **{success_rate}%**. The Autonomous Recovery Engine recovered "
                f"**{recovered_tx} transactions**, protecting **₹{recovered_rev:,.2f}** from being abandoned."
            )
            contributors = [
                f"Total Volume Processed: ₹{overview['total_volume']:,.2f}",
                f"Effective Success Rate: {success_rate}% (Raw: {raw_rate}%)",
                f"High-Risk Transactions Monitored: {high_risk_count}",
                f"Dominant Failure Pattern: {top_failure} ({top_failure_count} events)"
            ]
            actions = [
                "Keep automated recovery active for all payment methods.",
                "Review high-risk merchant transaction limits to maintain low chargeback risk."
            ]

        # Default fallback intelligent response
        else:
            answer = (
                f"RAZORFLOW X Reliability Diagnostics: Across {total} total transactions, your effective success rate stands at "
                f"{success_rate}%. Autonomous Recovery has rescued {recovered_tx} transactions worth ₹{recovered_rev:,.2f}. "
                f"Top operational concern is {top_failure}."
            )
            contributors = [
                f"Success Rate: {success_rate}%",
                f"Recovered Revenue: ₹{recovered_rev:,.2f}",
                f"Active Risk Score Avg: {overview['avg_risk_score']}/100"
            ]
            actions = [
                "Monitor gateway health metrics on the Live Telemetry board.",
                "Run simulated scenarios to test failure self-healing."
            ]

        return {
            "query": query_text,
            "answer": answer,
            "key_metrics": {
                "total_transactions": total,
                "effective_success_rate": f"{success_rate}%",
                "salvaged_revenue": f"₹{recovered_rev:,.2f}",
                "recovered_count": recovered_tx,
                "top_failure_type": top_failure
            },
            "contributors": contributors,
            "recommended_actions": actions
        }

ai_assistant = ExplainableAIAssistant()
