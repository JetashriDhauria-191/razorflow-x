from typing import Dict, Any, Optional

class FailureIntelligenceEngine:
    FAILURE_RULES = {
        "TIMEOUT": {
            "category": "TIMEOUT",
            "severity": "MEDIUM",
            "cause": "Gateway upstream socket timeout or unresponsive banking server connection.",
            "diagnostic": "Transaction dropped during authorization handshake. Temporary infrastructure latency spike.",
            "recovery_strategy": "SMART_BACKOFF_RETRY",
            "recovery_recommendation": "Execute automated retry with 5-15s exponential jitter backoff.",
            "recovery_probability": 0.88
        },
        "NETWORK_FAILURE": {
            "category": "NETWORK_FAILURE",
            "severity": "MEDIUM",
            "cause": "Transient network connection reset or SSL handshake termination.",
            "diagnostic": "Packet drop during gateway roundtrip; customer side or middlebox connection dropped.",
            "recovery_strategy": "SMART_BACKOFF_RETRY",
            "recovery_recommendation": "Perform autonomous background status sync and retry via resilient circuit breaker.",
            "recovery_probability": 0.85
        },
        "BANK_FAILURE": {
            "category": "BANK_FAILURE",
            "severity": "HIGH",
            "cause": "Issuing bank core banking system (CBS) downtime or intermittent node throttling.",
            "diagnostic": "Bank declined with 503 Service Unavailable. Node queue congestion at issuer.",
            "recovery_strategy": "ALTERNATE_GATEWAY",
            "recovery_recommendation": "Reroute transaction through alternate acquirer channel or suggest alternate bank.",
            "recovery_probability": 0.72
        },
        "GATEWAY_FAILURE": {
            "category": "GATEWAY_FAILURE",
            "severity": "HIGH",
            "cause": "Primary payment gateway internal processing error or 5xx server fault.",
            "diagnostic": "Gateway returned INTERNAL_SERVER_ERROR during capture phase.",
            "recovery_strategy": "ALTERNATE_GATEWAY",
            "recovery_recommendation": "Failover to secondary backup payment gateway route immediately.",
            "recovery_probability": 0.80
        },
        "AUTHENTICATION_FAILURE": {
            "category": "AUTHENTICATION_FAILURE",
            "severity": "MEDIUM",
            "cause": "3D Secure (3DS) authentication failed, OTP timeout, or incorrect credentials entered.",
            "diagnostic": "Customer failed second-factor authentication challenge (3DS2 OTP expired or cancelled).",
            "recovery_strategy": "CUSTOMER_ALERT",
            "recovery_recommendation": "Send pre-authenticated instant checkout recovery link via WhatsApp/SMS.",
            "recovery_probability": 0.64
        },
        "INSUFFICIENT_FUNDS": {
            "category": "INSUFFICIENT_FUNDS",
            "severity": "LOW",
            "cause": "Cardholder account balance is insufficient for requested transaction amount.",
            "diagnostic": "Issuer returned decline code 51 (Insufficient Funds). Hard authorization decline.",
            "recovery_strategy": "METHOD_FALLBACK",
            "recovery_recommendation": "Prompt user for alternate payment method (UPI / Credit Card / NetBanking / BNPL).",
            "recovery_probability": 0.45
        },
        "DUPLICATE_TRANSACTION": {
            "category": "DUPLICATE_TRANSACTION",
            "severity": "HIGH",
            "cause": "Idempotency key collision or rapid double submission detected.",
            "diagnostic": "Identical order amount and receipt ID submitted within 30 seconds.",
            "recovery_strategy": "SMART_BACKOFF_RETRY",
            "recovery_recommendation": "Verify existing transaction status before generating a fresh idempotency receipt.",
            "recovery_probability": 0.90
        }
    }

    def analyze_failure(self, error_code: Optional[str] = None, error_desc: Optional[str] = None, raw_payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classifies error codes and descriptions into structured diagnostics and recovery actionable intelligence.
        """
        combined = f"{error_code or ''} {error_desc or ''}".upper()

        matched_category = "UNKNOWN"
        for key in self.FAILURE_RULES.keys():
            if key in combined or (key == "TIMEOUT" and "TIME_OUT" in combined) or (key == "NETWORK_FAILURE" and ("CONNECTION" in combined or "NETWORK" in combined)):
                matched_category = key
                break
        
        if matched_category == "UNKNOWN":
            if "AUTHENTICATION" in combined or "3DS" in combined or "OTP" in combined or "SIGNATURE" in combined:
                matched_category = "AUTHENTICATION_FAILURE"
            elif "BANK" in combined or "ISSUER" in combined:
                matched_category = "BANK_FAILURE"
            elif "FUNDS" in combined or "BALANCE" in combined or "LIMIT" in combined:
                matched_category = "INSUFFICIENT_FUNDS"
            elif "TIMEOUT" in combined or "TIMED OUT" in combined or "GATEWAY TIMEOUT" in combined:
                matched_category = "TIMEOUT"
            elif "GATEWAY" in combined or "SERVER" in combined or "500" in combined or "502" in combined or "503" in combined:
                matched_category = "GATEWAY_FAILURE"

        rule = self.FAILURE_RULES.get(matched_category, {
            "category": "UNKNOWN",
            "severity": "MEDIUM",
            "cause": "Unspecified payment authorization decline from processing gateway.",
            "diagnostic": "General decline response received without standard sub-code.",
            "recovery_strategy": "SMART_BACKOFF_RETRY",
            "recovery_recommendation": "Attempt status reconciliation query and initiate smart retry.",
            "recovery_probability": 0.50
        })

        return {
            "failure_category": rule["category"],
            "failure_severity": rule["severity"],
            "failure_reason": error_desc or rule["cause"],
            "diagnostic_insight": rule["diagnostic"],
            "recommended_recovery": rule["recovery_recommendation"],
            "recommended_strategy": rule["recovery_strategy"],
            "recovery_probability": rule["recovery_probability"]
        }

failure_engine = FailureIntelligenceEngine()
