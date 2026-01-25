from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    token = Column(String)
    timeframe = Column(String)
    direction = Column(String)
    entry = Column(Float)
    tp = Column(Float)
    sl = Column(Float)
    confidence = Column(Float)
    rationale = Column(Text)
    source = Column(String)
    mode = Column(String)  # LITE, PRO, ADVISOR
    raw_response = Column(Text, nullable=True)
    strategy_id = Column(String, nullable=True)

    # Validation / Isolation
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Idempotency constraint (Strict)
    idempotency_key = Column(String, unique=True, index=True, nullable=True)

    # Relationship to evaluation
    evaluation = relationship(
        lambda: SignalEvaluation, back_populates="signal", uselist=False, viewonly=True
    )

    # Soft Delete / Admin Visibility
    is_hidden = Column(
        Integer, default=0
    )  # 0=Visible, 1=Hidden (Boolean as Integer for SQLite/Postgres compatibility)
    is_saved = Column(Integer, default=0)  # 0=Transient, 1=Saved/Tracked by user
    extra = Column(Text, nullable=True)  # JSON Metadata encoded as string

    # [HARDENING] Persistent Deduplication
    __table_args__ = (
        UniqueConstraint(
            "strategy_id", "token", "timestamp", "direction", name="uq_signal_dedup"
        ),
    )


class SignalEvaluation(Base):
    __tablename__ = "signal_evaluations"

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signals.id"))
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    result = Column(String)  # WIN, LOSS, BE
    pnl_r = Column(Float)
    exit_price = Column(Float)

    signal = relationship(
        lambda: Signal, back_populates="evaluation", overlaps="signal"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String(120), nullable=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # admin, user
    created_at = Column(DateTime, default=datetime.utcnow)

    # Plans / Entitlements
    plan = Column(String, default="FREE")  # FREE, PRO, OWNER
    plan_expires_at = Column(DateTime, nullable=True)

    # ---------------------------
    # Billing / Stripe
    # ---------------------------
    billing_provider = Column(String, nullable=True)          # e.g. "stripe"
    stripe_customer_id = Column(String, nullable=True, index=True)        # cus_...
    stripe_subscription_id = Column(String, nullable=True, index=True)    # sub_...
    stripe_price_id = Column(String, nullable=True)           # price_...
    plan_status = Column(String, nullable=True)               # active/inactive/canceled, etc.
    # Optional owner checks / integrations
    telegram_chat_id = Column(String, nullable=True)

    # Relationship to signals
    signals = relationship(lambda: Signal, backref="user")
class StrategyConfig(Base):
    __tablename__ = "strategy_configs"
    tokens = Column(Text, nullable=True)  # JSON list as string
    timeframes = Column(Text, nullable=True)  # JSON list as string











    id = Column(Integer, primary_key=True)


    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)





    # Strategy enabling + params


    strategy_id = Column(String)


    persona_id = Column(String(128), index=True, nullable=True)

    # Display / Metadata
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    risk_profile = Column(String, nullable=True)
    expected_roi = Column(String, nullable=True)
    color = Column(String, default="indigo")
    icon = Column(String, default="Zap") # lucide icon name
    is_public = Column(Integer, default=0) # 0=Private, 1=Public

    enabled = Column(Integer, default=1)  # bool as int
    total_signals = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

    params_json = Column(Text, nullable=True)





    __table_args__ = (


        UniqueConstraint("user_id", "persona_id", name="uq_user_persona"),


    )








class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    endpoint = Column(Text)
    p256dh = Column(Text)
    auth = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "endpoint", name="uq_user_endpoint"),
    )


class SchedulerLock(Base):
    __tablename__ = "scheduler_locks"

    id = Column(Integer, primary_key=True)
    lock_name = Column(String, unique=True, index=True)
    acquired_at = Column(DateTime, default=datetime.utcnow)


class AdminAuditLog(Base):
    """
    Registro inmutable de acciones administrativas.
    REQ: Trazabilidad completa (Sale-Ready).
    """

    __tablename__ = "admin_audit_logs"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # UPDATE_PLAN, HIDE_SIGNAL, UNHIDE_SIGNAL
    target_id = Column(String)  # ID del recurso afectado (User ID o Signal ID)
    details = Column(Text)  # JSON o texto descriptivo

    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class DailyUsage(Base):
    """
    Control de cuotas diarias por usuario.
    Clave compuesta Ãºnica: (user_id, feature, date).
    """

    __tablename__ = "daily_usage"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    feature = Column(String)
    date = Column(String)  # YYYY-MM-DD
    count = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("user_id", "feature", "date", name="uq_user_feature_date"),
    )


class CopilotProfile(Base):
    __tablename__ = "copilot_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)

    # Minimal profile fields for Advisor
    trader_style = Column(String, nullable=True, default="BALANCED")
    risk_tolerance = Column(String, nullable=True, default="MODERATE")
    time_horizon = Column(String, nullable=True, default="SWING")
    custom_instructions = Column(Text, nullable=True)
    
    # Legacy fields mapping if needed, or just clean replacement
    # notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class WatchAlert(Base):
    __tablename__ = "watch_alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    token = Column(String, index=True)
    timeframe = Column(String, index=True)
    direction = Column(String, nullable=True)
    condition = Column(Text, nullable=True)  # JSON/text rule

    enabled = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)






