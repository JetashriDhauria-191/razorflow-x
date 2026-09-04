import datetime
from typing import Dict, Any, List, Tuple
try:
    from backend.ml_engine import ml_engine
except (ImportError, ModuleNotFoundError):
    from ml_engine import ml_engine

class RiskEngine:
    def evaluate_risk(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates transaction risk across heuristic velocity indicators, device trust,
        and machine learning prediction models. Returns composite 0-100 score and risk factors.
        """
        amount = float(payment_data.get("amount", 0.0))
        retry_count = int(payment_data.get("retry_count", 0))
        failure_count = int(payment_data.get("failure_count", 0))
        frequency = int(payment_data.get("transaction_frequency_10min", 1))
        hour = payment_data.get("hour_of_day")
        if hour is None:
            hour = datetime.datetime.now().hour
        else:
            hour = int(hour)

        device_trust = float(payment_data.get("device_trust_score", 0.9))
        prev_success_rate = float(payment_data.get("previous_success_rate", 0.95))
        velocity = float(payment_data.get("velocity_score", 1.0))

        factors: List[str] = []
        heuristic_score = 10.0 # Base floor

        # Factor 1: High Transaction Amount Anomaly
        if amount >= 50000:
            heuristic_score += 30.0
            factors.append(f"High ticket value (₹{amount:,.2f}) significantly above median basket size")
        elif amount >= 20000:
            heuristic_score += 15.0
            factors.append(f"Elevated transaction value (₹{amount:,.2f})")

        # Factor 2: High Velocity & Frequency
        if frequency >= 5 or velocity >= 4.0:
            heuristic_score += 25.0
            factors.append(f"Abnormal burst velocity ({frequency} attempts in 10-minute window)")
        elif frequency >= 3 or velocity >= 2.0:
            heuristic_score += 12.0
            factors.append(f"Increased attempt frequency ({frequency} attempts)")

        # Factor 3: Prior Consecutive Failures & Retries
        if failure_count >= 3 or retry_count >= 3:
            heuristic_score += 25.0
            factors.append(f"Multiple consecutive prior payment failures ({failure_count} failures, {retry_count} retries)")
        elif failure_count >= 1 or retry_count >= 1:
            heuristic_score += 10.0
            factors.append(f"Previous attempt retry detected (Retry #{retry_count})")

        # Factor 4: Unusual Transaction Timing (Midnight - 4 AM)
        if 1 <= hour <= 4:
            heuristic_score += 15.0
            factors.append(f"Unusual transaction time window ({hour:02d}:00 HRS)")

        # Factor 5: Low Device Trust or IP Reputation
        if device_trust < 0.5:
            heuristic_score += 20.0
            factors.append(f"Unverified or new device fingerprint (Trust score: {device_trust*100:.0f}%)")

        # Factor 6: Poor Historical Customer Success Rate
        if prev_success_rate < 0.5:
            heuristic_score += 18.0
            factors.append(f"Low historical customer settlement rate ({prev_success_rate*100:.0f}%)")

        # Get ML Inference
        ml_features = {
            "amount": amount,
            "retry_count": retry_count,
            "failure_count": failure_count,
            "transaction_frequency_10min": frequency,
            "hour_of_day": hour,
            "previous_success_rate": prev_success_rate,
            "velocity_score": velocity,
            "device_trust_score": device_trust
        }
        ml_res = ml_engine.predict(ml_features)
        ml_risk = ml_res["ml_risk_score"]
        prob_failed = ml_res["failure_probability"]
        is_anomaly = ml_res["is_anomaly"]

        if is_anomaly:
            factors.append("Isolation Forest detected multi-dimensional transaction vector anomaly")

        # Blended Composite Score (60% ML Model + 40% Heuristics)
        final_risk_score = round((0.60 * ml_risk) + (0.40 * heuristic_score), 1)
        final_risk_score = min(100.0, max(0.0, final_risk_score))

        # Risk Classification Level
        if final_risk_score >= 70.0:
            risk_level = "HIGH"
            recommended_action = "Step-up authentication required (3DS2/OTP verification, review velocity limits)"
        elif final_risk_score >= 31.0:
            risk_level = "MEDIUM"
            recommended_action = "Allow transaction with enhanced monitoring and automated retry fallback"
        else:
            risk_level = "LOW"
            recommended_action = "Approve immediately via express fast-track checkout"

        if not factors:
            factors.append("Standard verified transaction profile with healthy historical velocity")

        return {
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "factors": factors,
            "ml_failure_probability": prob_failed,
            "is_anomaly": is_anomaly,
            "recommended_action": recommended_action
        }

risk_engine = RiskEngine()
