from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    role: Optional[str] = "analyst"

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# --- Catalogue & Product Schemas ---
class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    name: str
    description: Optional[str] = None
    category: str
    brand: Optional[str] = "ProTech"
    price: float
    discount: float = 0.0
    inventory: int = 50
    rating: float = 4.8
    review_count: int = 120
    delivery_days: int = 1
    margin: float = 0.25
    features: List[str] = []
    tags: List[str] = []
    compatible_products: List[str] = []
    upsell_products: List[str] = []
    cross_sell_products: List[str] = []
    image_url: Optional[str] = None
    is_active: bool = True

class CatalogSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    max_price: Optional[float] = None
    tag: Optional[str] = None
    in_stock_only: bool = True

# --- Recommendation & Personalization Schemas ---
class ExplainableFactor(BaseModel):
    factor_name: str
    weight: float
    score: float
    description: str

class RecommendationOption(BaseModel):
    product: ProductSchema
    rank: int
    recommendation_score: float
    is_top_pick: bool = False
    why_recommended: List[str] = []
    explainable_factors: List[ExplainableFactor] = []
    cross_sell_opportunity: Optional[ProductSchema] = None
    upsell_opportunity: Optional[ProductSchema] = None

class RecommendationResponse(BaseModel):
    intent_detected: str
    customer_id: str
    budget_limit: Optional[float] = None
    options: List[RecommendationOption]
    suggested_bundle: Optional[Dict[str, Any]] = None
    decision_rationale: str

# --- Cart & Agentic Checkout Schemas ---
class CartItemSchema(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int = 1
    category: Optional[str] = None

class CartSessionSchema(BaseModel):
    session_id: str
    customer_id: str
    items: List[CartItemSchema]
    base_total: float
    discount_total: float
    final_total: float
    is_bundled: bool = False
    cross_sell_added: bool = False
    upsell_added: bool = False
    status: str

class AgentChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    customer_id: Optional[str] = "cust_coding_01"
    customer_budget: Optional[float] = None
    current_cart: Optional[List[CartItemSchema]] = None

class AgentChatResponse(BaseModel):
    session_id: str
    message: str
    intent: str
    recommendations: List[RecommendationOption] = []
    cross_sell_offer: Optional[ProductSchema] = None
    upsell_offer: Optional[ProductSchema] = None
    bundle_offer: Optional[Dict[str, Any]] = None
    cart: Optional[CartSessionSchema] = None
    policy_status: str = "PASSED"
    policy_details: Optional[Dict[str, Any]] = None
    ready_for_checkout: bool = False
    razorpay_order_payload: Optional[Dict[str, Any]] = None
    audit_trace_id: Optional[int] = None

# --- Policy & Safety Gate Schemas ---
class PolicyEvaluationRequest(BaseModel):
    action_type: str = "ORDER_CREATION" # ORDER_CREATION, DISCOUNT_APPLY, CAMPAIGN_LAUNCH, AUTO_PURCHASE
    amount: float
    discount_percentage: float = 0.0
    product_ids: List[str] = []
    customer_confirmed: bool = True
    session_id: Optional[str] = None

class PolicyRuleResult(BaseModel):
    rule_name: str
    passed: bool
    threshold: Any
    actual_value: Any
    message: str

class PolicyEvaluationResponse(BaseModel):
    is_allowed: bool
    status: str # PASSED, BLOCKED, CONFIRMATION_REQUIRED
    reason: str
    rules_evaluated: List[PolicyRuleResult]
    evaluated_at: str

# --- Campaign Orchestrator Schemas ---
class CampaignProposalRequest(BaseModel):
    prompt: str = "Increase sales of keyboards this week"
    target_category: Optional[str] = "keyboard"
    suggested_budget: Optional[float] = 5000.0

class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: str
    name: str
    goal: str
    target_segment: str
    offer: str
    expected_aov_lift: str
    budget: float
    duration_days: int
    status: str
    policy_checked: bool
    merchant_approved: bool
    revenue_generated: float
    conversions_count: int
    created_at: datetime.datetime

class CampaignApprovalRequest(BaseModel):
    approved: bool

# --- Audit Trace Schemas ---
class AgentAuditTraceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    step_index: int
    stage: str
    action_name: str
    decision_explanation: str
    policy_status: str
    money_amount: Optional[float] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime

# --- Growth & A/B Experiment Schemas ---
class GrowthImpactMetrics(BaseModel):
    total_gmv_processed: float
    ai_assisted_revenue: float
    baseline_revenue_comparison: float
    incremental_revenue_gained: float
    aov_baseline: float
    aov_ai_assisted: float
    aov_uplift_percentage: float
    conversion_lift_percentage: float
    cross_sell_acceptance_rate: float
    upsell_acceptance_rate: float
    recommendation_accuracy: float
    total_ai_actions_count: int
    money_actions_breakdown: Dict[str, int]

class ABExperimentSummary(BaseModel):
    total_sessions_simulated: int
    control_metrics: Dict[str, Any]
    treatment_metrics: Dict[str, Any]
    uplift_metrics: Dict[str, Any]
    sample_sessions: List[Dict[str, Any]]
    explanation: str

# --- Payment Schemas ---
class CreateOrderRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount in standard currency units (e.g. INR)")
    currency: str = "INR"
    receipt: Optional[str] = None
    customer_id: Optional[str] = "cust_default_01"
    customer_email: Optional[str] = "customer@example.com"
    customer_phone: Optional[str] = "+919876543210"
    device_ip: Optional[str] = "192.168.1.50"
    device_id: Optional[str] = "device_fingerprint_abc"
    is_ai_assisted: bool = False
    baseline_amount: Optional[float] = None
    upsell_applied: bool = False
    cross_sell_applied: bool = False
    session_id: Optional[str] = None
    notes: Optional[Dict[str, Any]] = None

class CreateOrderResponse(BaseModel):
    order_id: str
    razorpay_order_id: Optional[str]
    amount: float
    currency: str
    key_id: Optional[str]
    risk_score: float
    risk_level: str
    risk_factors: List[str]
    ml_failure_probability: float
    policy_passed: bool = True
    status: str

class VerifyPaymentRequest(BaseModel):
    order_id: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    amount: Optional[float] = None
    simulated_failure: Optional[str] = None # For testing & demo: e.g. TIMEOUT, BANK_FAILURE, etc.
    session_id: Optional[str] = None

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_id: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    gateway: str
    customer_id: Optional[str] = None
    customer_email: Optional[str] = None
    
    # Growth
    is_ai_assisted: bool = False
    baseline_amount: Optional[float] = None
    incremental_revenue: float = 0.0
    upsell_applied: bool = False
    cross_sell_applied: bool = False
    
    # Risk & ML
    risk_score: float
    risk_level: str
    risk_factors: Optional[List[str]] = None
    ml_failure_probability: float
    ml_anomaly_detected: bool
    
    # Failure Intelligence
    failure_category: Optional[str] = None
    failure_severity: Optional[str] = None
    failure_reason: Optional[str] = None
    diagnostic_insight: Optional[str] = None
    recommended_recovery: Optional[str] = None
    recovery_probability: float = 0.0
    
    # Autonomous Recovery
    retry_count: int
    recovery_status: str
    recovery_strategy_used: Optional[str] = None
    
    created_at: datetime.datetime
    updated_at: datetime.datetime

# --- Risk & ML Schemas ---
class RiskEvaluationRequest(BaseModel):
    amount: float
    customer_id: Optional[str] = "cust_001"
    retry_count: int = 0
    failure_count: int = 0
    transaction_frequency_10min: int = 1
    hour_of_day: Optional[int] = None
    device_trust_score: float = 0.9
    previous_success_rate: float = 0.95
    velocity_score: float = 1.0

class RiskEvaluationResponse(BaseModel):
    risk_score: float
    risk_level: str # LOW, MEDIUM, HIGH
    factors: List[str]
    ml_failure_probability: float
    is_anomaly: bool
    recommended_action: str

# --- Recovery Engine Schemas ---
class TriggerRecoveryRequest(BaseModel):
    payment_id: str
    custom_strategy: Optional[str] = None # SMART_BACKOFF_RETRY, ALTERNATE_GATEWAY, METHOD_FALLBACK

class RecoveryResultResponse(BaseModel):
    payment_id: str
    final_status: str
    recovery_status: str
    attempts_made: int
    timeline: List[Dict[str, Any]]
    recovered_revenue: float
    message: str

# --- Simulation Schemas ---
class SimulationScenarioRequest(BaseModel):
    scenario: int = Field(..., ge=1, le=5, description="Scenario ID (1: Normal, 2: High Risk, 3: Auto Recovery, 4: Conversational AI Growth Flow, 5: Custom Failure)")
    amount: Optional[float] = None
    custom_failure_type: Optional[str] = None

# --- Analytics Schemas ---
class AnalyticsOverview(BaseModel):
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    recovered_transactions: int
    total_volume: float
    recovered_revenue: float
    raw_success_rate: float # Before recovery
    effective_success_rate: float # After recovery
    recovery_rate: float
    avg_risk_score: float
    
    # Growth metrics
    ai_assisted_revenue: float = 0.0
    aov_uplift_percentage: float = 0.0
    conversion_lift_percentage: float = 0.0
    cross_sell_acceptance_rate: float = 0.0
    upsell_acceptance_rate: float = 0.0
    
    risk_breakdown: Dict[str, int]
    failure_breakdown: Dict[str, int]
    hourly_trend: List[Dict[str, Any]]

# --- AI Assistant Schemas ---
class AIAssistantQuery(BaseModel):
    query: str

class AIAssistantResponse(BaseModel):
    query: str
    answer: str
    key_metrics: Dict[str, Any]
    contributors: List[str]
    recommended_actions: List[str]
