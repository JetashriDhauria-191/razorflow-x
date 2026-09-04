import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
try:
    from backend.database import Base
except (ImportError, ModuleNotFoundError):
    from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=False)
    price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    inventory = Column(Integer, default=50)
    rating = Column(Float, default=4.8)
    margin = Column(Float, default=0.25)
    features = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    compatible_products = Column(JSON, default=list)
    upsell_products = Column(JSON, default=list)
    cross_sell_products = Column(JSON, default=list)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    budget = Column(Float, default=3000.0)
    interests = Column(JSON, default=list)
    purchase_history = Column(JSON, default=list)
    preference = Column(String(50), default="premium")
    conversion_score = Column(Float, default=0.85)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CartSession(Base):
    __tablename__ = "cart_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    customer_id = Column(String(100), index=True, default="guest")
    items = Column(JSON, default=list)
    base_total = Column(Float, default=0.0)
    discount_total = Column(Float, default=0.0)
    final_total = Column(Float, default=0.0)
    is_bundled = Column(Boolean, default=False)
    cross_sell_added = Column(Boolean, default=False)
    upsell_added = Column(Boolean, default=False)
    status = Column(String(50), default="ACTIVE")
    policy_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    goal = Column(String(255), nullable=False)
    target_segment = Column(String(255), nullable=False)
    offer = Column(Text, nullable=False)
    expected_aov_lift = Column(String(50), default="+12-18%")
    budget = Column(Float, default=5000.0)
    duration_days = Column(Integer, default=7)
    status = Column(String(50), default="PROPOSED")
    policy_checked = Column(Boolean, default=False)
    merchant_approved = Column(Boolean, default=False)
    revenue_generated = Column(Float, default=0.0)
    conversions_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AgentAuditTrace(Base):
    __tablename__ = "agent_audit_traces"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    step_index = Column(Integer, default=1)
    stage = Column(String(100), index=True, nullable=False)
    action_name = Column(String(100), nullable=False)
    decision_explanation = Column(Text, nullable=False)
    policy_status = Column(String(50), default="PASSED")
    money_amount = Column(Float, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ABExperimentSession(Base):
    __tablename__ = "ab_experiment_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    cohort = Column(String(50), nullable=False)
    customer_segment = Column(String(100), default="General")
    intent = Column(String(255), nullable=True)
    items_count = Column(Integer, default=1)
    cart_total = Column(Float, default=0.0)
    cross_sell_accepted = Column(Boolean, default=False)
    upsell_accepted = Column(Boolean, default=False)
    converted = Column(Boolean, default=False)
    failure_encountered = Column(Boolean, default=False)
    recovered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class MerchantPolicy(Base):
    __tablename__ = "merchant_policies"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    max_order_amount = Column(Float, default=10000.0)
    max_discount_percentage = Column(Float, default=20.0)
    auto_purchase_enabled = Column(Boolean, default=False)
    customer_confirmation_required = Column(Boolean, default=True)
    max_campaign_budget = Column(Float, default=50000.0)
    block_out_of_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {'extend_existing': True}

    id = Column(String(64), primary_key=True, index=True)
    order_id = Column(String(64), index=True, nullable=False)
    razorpay_order_id = Column(String(64), index=True, nullable=True)
    razorpay_payment_id = Column(String(64), index=True, nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    gateway = Column(String(50), default="razorpay")
    status = Column(String(50), index=True, default="created")
    customer_id = Column(String(100), index=True, nullable=True)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(50), nullable=True)
    device_ip = Column(String(50), nullable=True)
    device_id = Column(String(100), nullable=True)
    is_ai_assisted = Column(Boolean, default=False)
    baseline_amount = Column(Float, nullable=True)
    incremental_revenue = Column(Float, default=0.0)
    upsell_applied = Column(Boolean, default=False)
    cross_sell_applied = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="LOW")
    risk_factors = Column(JSON, nullable=True)
    ml_failure_probability = Column(Float, default=0.0)
    ml_anomaly_detected = Column(Boolean, default=False)
    failure_category = Column(String(64), nullable=True)
    failure_severity = Column(String(20), nullable=True)
    failure_reason = Column(Text, nullable=True)
    diagnostic_insight = Column(Text, nullable=True)
    recommended_recovery = Column(Text, nullable=True)
    recovery_probability = Column(Float, default=0.0)
    retry_count = Column(Integer, default=0)
    recovery_status = Column(String(50), default="NONE")
    recovery_strategy_used = Column(String(64), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    recovery_attempts = relationship("RecoveryAttempt", back_populates="payment", cascade="all, delete-orphan")

class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(64), ForeignKey("payments.id"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    strategy = Column(String(64), nullable=False)
    status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    recovery_delay_ms = Column(Integer, default=0)
    gateway_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    payment = relationship("Payment", back_populates="recovery_attempts")

class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    gateway = Column(String(50), default="razorpay")
    event_type = Column(String(100), index=True, nullable=False)
    signature_valid = Column(Boolean, default=False)
    payload_json = Column(JSON, nullable=False)
    processed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=False)
    entity_id = Column(String(100), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class MLMetricLog(Base):
    __tablename__ = "ml_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=True)
    trained_samples = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
