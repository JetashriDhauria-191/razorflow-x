import uuid
from typing import Dict, Any, Optional
from backend.gateways.base import PaymentGateway, GatewayOrderResult, GatewayVerifyResult

class MockGateway(PaymentGateway):
    def __init__(self, name: str = "simulator"):
        self.name = name

    def create_order(self, amount: float, currency: str = "INR", receipt: Optional[str] = None, notes: Optional[Dict[str, Any]] = None) -> GatewayOrderResult:
        receipt_id = receipt or f"rcpt_{uuid.uuid4().hex[:10]}"
        mock_order_id = f"ord_{self.name}_{uuid.uuid4().hex[:12]}"
        return GatewayOrderResult(
            order_id=receipt_id,
            gateway_order_id=mock_order_id,
            amount=amount,
            currency=currency,
            key_id=f"key_{self.name}_test",
            raw_response={
                "id": mock_order_id,
                "gateway": self.name,
                "amount": amount,
                "currency": currency,
                "status": "created",
                "receipt": receipt_id
            }
        )

    def verify_payment(self, order_id: str, payment_id: str, signature: str) -> GatewayVerifyResult:
        if signature and "fail" in signature.lower():
            return GatewayVerifyResult(
                is_valid=False,
                status="failed",
                payment_id=payment_id,
                error_code="GATEWAY_DECLINED",
                error_description="Simulated gateway decline response"
            )
        return GatewayVerifyResult(
            is_valid=True,
            status="success",
            payment_id=payment_id,
            raw_response={"status": "captured", "payment_id": payment_id}
        )

    def verify_webhook_signature(self, body_bytes: bytes, signature_header: str) -> bool:
        return bool(signature_header and len(signature_header) > 5)
