try:
    from backend.gateways.base import PaymentGateway, GatewayOrderResult, GatewayVerifyResult
except (ImportError, ModuleNotFoundError):
    from gateways.base import PaymentGateway, GatewayOrderResult, GatewayVerifyResult
try:
    from backend.gateways.razorpay_gateway import RazorpayGateway
except (ImportError, ModuleNotFoundError):
    from gateways.razorpay_gateway import RazorpayGateway
try:
    from backend.gateways.mock_gateway import MockGateway
except (ImportError, ModuleNotFoundError):
    from gateways.mock_gateway import MockGateway

def get_payment_gateway(gateway_name: str = "razorpay") -> PaymentGateway:
    if gateway_name.lower() == "razorpay":
        return RazorpayGateway()
    return MockGateway(name=gateway_name)
