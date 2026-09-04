from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GatewayOrderResult:
    order_id: str
    gateway_order_id: str
    amount: float
    currency: str
    key_id: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

@dataclass
class GatewayVerifyResult:
    is_valid: bool
    status: str # success, failed, pending
    payment_id: Optional[str] = None
    error_code: Optional[str] = None
    error_description: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

class PaymentGateway(ABC):
    @abstractmethod
    def create_order(self, amount: float, currency: str = "INR", receipt: Optional[str] = None, notes: Optional[Dict[str, Any]] = None) -> GatewayOrderResult:
        """Create an order on the payment gateway."""
        pass

    @abstractmethod
    def verify_payment(self, order_id: str, payment_id: str, signature: str) -> GatewayVerifyResult:
        """Verify the signature and payment validity on the gateway."""
        pass

    @abstractmethod
    def verify_webhook_signature(self, body_bytes: bytes, signature_header: str) -> bool:
        """Verify the authenticity of incoming webhook signatures."""
        pass
