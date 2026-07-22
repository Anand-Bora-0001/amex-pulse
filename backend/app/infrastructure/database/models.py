"""
AmEx Pulse — SQLAlchemy ORM Models
===================================
Complete database schema for the Customer Journey Intelligence Platform.
All models use UUID primary keys for enterprise-grade distribution readiness.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════
# USERS — Platform users (agents, managers, analysts, admins)
# ═══════════════════════════════════════════════════════════════════
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="agent")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    # Relationships
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user", lazy="selectin")
    assigned_cases: Mapped[list["SupportCase"]] = relationship(back_populates="assigned_agent", lazy="selectin")


# ═══════════════════════════════════════════════════════════════════
# CUSTOMERS — Card members with unified profiles
# ═══════════════════════════════════════════════════════════════════
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    universal_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    card_last_four: Mapped[str] = mapped_column(String(4), nullable=True)
    member_since: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    card_type: Mapped[str] = mapped_column(String(20), nullable=False, default="blue")

    # AI-computed scores (updated in real-time)
    health_score: Mapped[float] = mapped_column(Float, default=75.0)
    frustration_score: Mapped[float] = mapped_column(Float, default=0.0)
    churn_risk: Mapped[float] = mapped_column(Float, default=0.1)

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    # Relationships
    identifiers: Mapped[list["CustomerIdentifier"]] = relationship(back_populates="customer", lazy="selectin")
    journeys: Mapped[list["Journey"]] = relationship(back_populates="customer", lazy="selectin")
    events: Mapped[list["Event"]] = relationship(back_populates="customer", lazy="selectin")
    sessions: Mapped[list["Session"]] = relationship(back_populates="customer", lazy="selectin")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="customer", lazy="selectin")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="customer", lazy="selectin")
    support_cases: Mapped[list["SupportCase"]] = relationship(back_populates="customer", lazy="selectin")
    activity_logs: Mapped[list["ActivityLog"]] = relationship(back_populates="customer", lazy="selectin")


# ═══════════════════════════════════════════════════════════════════
# CUSTOMER IDENTIFIERS — For cross-channel identity resolution
# ═══════════════════════════════════════════════════════════════════
class CustomerIdentifier(Base):
    __tablename__ = "customer_identifiers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    identifier_type: Mapped[str] = mapped_column(String(50), nullable=False)  # email, phone, device, cookie, account
    identifier_value: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="identifiers")


# ═══════════════════════════════════════════════════════════════════
# CHANNELS — Interaction channels
# ═══════════════════════════════════════════════════════════════════
class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), nullable=True)
    color: Mapped[str] = mapped_column(String(10), nullable=True)

    # Relationships
    sessions: Mapped[list["Session"]] = relationship(back_populates="channel", lazy="selectin")
    events: Mapped[list["Event"]] = relationship(back_populates="channel", lazy="selectin")


# ═══════════════════════════════════════════════════════════════════
# SESSIONS — Customer interaction sessions per channel
# ═══════════════════════════════════════════════════════════════════
class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    channel_id: Mapped[str] = mapped_column(String(36), ForeignKey("channels.id"), nullable=False)
    session_token: Mapped[str] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    is_abandoned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="sessions")
    channel: Mapped["Channel"] = relationship(back_populates="sessions")
    events: Mapped[list["Event"]] = relationship(back_populates="session", lazy="selectin")


# ═══════════════════════════════════════════════════════════════════
# JOURNEYS — Business-level customer journeys
# ═══════════════════════════════════════════════════════════════════
class Journey(Base):
    __tablename__ = "journeys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    journey_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    detected_intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    intent_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="journeys")
    steps: Mapped[list["JourneyStep"]] = relationship(back_populates="journey", lazy="selectin")


# ═══════════════════════════════════════════════════════════════════
# JOURNEY STEPS — Individual steps within a journey
# ═══════════════════════════════════════════════════════════════════
class JourneyStep(Base):
    __tablename__ = "journey_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("journeys.id"), nullable=False)
    event_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("events.id"), nullable=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(200), nullable=False)
    step_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # Relationships
    journey: Mapped["Journey"] = relationship(back_populates="steps")
    event: Mapped["Event | None"] = relationship(back_populates="journey_step")


# ═══════════════════════════════════════════════════════════════════
# EVENTS — Raw customer interaction events
# ═══════════════════════════════════════════════════════════════════
class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=True)
    channel_id: Mapped[str] = mapped_column(String(36), ForeignKey("channels.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(200), nullable=False)
    event_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # -1 to 1
    detected_emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="events")
    session: Mapped["Session | None"] = relationship(back_populates="events")
    channel: Mapped["Channel"] = relationship(back_populates="events")
    journey_step: Mapped["JourneyStep | None"] = relationship(back_populates="event")


# ═══════════════════════════════════════════════════════════════════
# PREDICTIONS — AI model predictions for customers
# ═══════════════════════════════════════════════════════════════════
class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_result: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0.0")
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="predictions")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="prediction", lazy="selectin")


# ═══════════════════════════════════════════════════════════════════
# RECOMMENDATIONS — Next Best Action recommendations
# ═══════════════════════════════════════════════════════════════════
class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    prediction_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("predictions.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    acted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="recommendations")
    prediction: Mapped["Prediction | None"] = relationship(back_populates="recommendations")


# ═══════════════════════════════════════════════════════════════════
# SUPPORT CASES — Customer support tickets
# ═══════════════════════════════════════════════════════════════════
class SupportCase(Base):
    __tablename__ = "support_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    assigned_agent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    case_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="open")
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="support_cases")
    assigned_agent: Mapped["User | None"] = relationship(back_populates="assigned_cases")


# ═══════════════════════════════════════════════════════════════════
# AUDIT LOGS — Security audit trail
# ═══════════════════════════════════════════════════════════════════
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="audit_logs")


# ═══════════════════════════════════════════════════════════════════
# ACTIVITY LOGS — Customer activity tracking
# ═══════════════════════════════════════════════════════════════════
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="activity_logs")
