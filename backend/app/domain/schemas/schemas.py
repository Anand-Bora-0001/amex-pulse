"""
AmEx Pulse — Pydantic Schemas
==============================
Request/Response models for all API endpoints.
Separated from ORM models to maintain clean architecture boundaries.
"""

from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# ═══════════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class LoginRequest(BaseModel):
    email: str = Field(..., example="admin@amexpulse.com")
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# CUSTOMER SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class CustomerResponse(BaseModel):
    id: str
    universal_id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    card_last_four: str | None
    member_since: str | None
    card_type: str
    health_score: float
    frustration_score: float
    churn_risk: float
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    customers: list[CustomerResponse]
    total: int
    page: int
    page_size: int


class CustomerDetailResponse(CustomerResponse):
    """Extended customer response with related data."""
    journeys: list["JourneyResponse"] = []
    recent_events: list["EventResponse"] = []
    recommendations: list["RecommendationResponse"] = []
    support_cases: list["SupportCaseResponse"] = []
    predictions: list["PredictionResponse"] = []


# ═══════════════════════════════════════════════════════════════════
# JOURNEY SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class JourneyStepResponse(BaseModel):
    id: str
    step_order: int
    step_name: str
    step_status: str

    class Config:
        from_attributes = True


class JourneyResponse(BaseModel):
    id: str
    customer_id: str
    journey_type: str
    status: str
    progress: float
    detected_intent: str | None
    intent_confidence: float | None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    ai_summary: str | None = None
    steps: list[JourneyStepResponse] = []

    class Config:
        from_attributes = True


class JourneyGraphNode(BaseModel):
    """Node in the journey graph visualization."""
    id: str
    type: str  # customer, channel, event, journey
    label: str
    data: dict = {}


class JourneyGraphEdge(BaseModel):
    """Edge in the journey graph visualization."""
    id: str
    source: str
    target: str
    label: str = ""
    animated: bool = False


class JourneyGraphResponse(BaseModel):
    nodes: list[JourneyGraphNode]
    edges: list[JourneyGraphEdge]


# ═══════════════════════════════════════════════════════════════════
# EVENT SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class EventResponse(BaseModel):
    id: str
    customer_id: str
    channel_name: str | None = None
    event_type: str
    event_name: str
    sentiment_score: float | None
    detected_emotion: str | None
    occurred_at: datetime | None = None

    class Config:
        from_attributes = True


class EventIngestRequest(BaseModel):
    customer_id: str
    channel: str
    event_type: str
    event_name: str
    event_data: dict = {}


class LiveEventResponse(BaseModel):
    """Real-time event broadcast format."""
    event: EventResponse
    customer_name: str
    channel_icon: str
    channel_color: str
    timestamp: str


# ═══════════════════════════════════════════════════════════════════
# PREDICTION SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class PredictionResponse(BaseModel):
    id: str
    customer_id: str
    prediction_type: str
    confidence: float
    explanation: str | None
    model_version: str
    predicted_at: datetime | None = None

    class Config:
        from_attributes = True


class PredictionRunRequest(BaseModel):
    customer_id: str
    prediction_types: list[str] = ["intent", "churn", "frustration", "health", "nba"]


class PredictionRunResponse(BaseModel):
    customer_id: str
    results: dict  # prediction_type -> result


# ═══════════════════════════════════════════════════════════════════
# RECOMMENDATION SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class RecommendationResponse(BaseModel):
    id: str
    customer_id: str
    action_type: str
    action_description: str
    confidence: float
    reasoning: str | None
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# SUPPORT CASE SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class SupportCaseResponse(BaseModel):
    id: str
    customer_id: str
    case_number: str
    subject: str
    description: str | None
    priority: str
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD SCHEMAS
# ═══════════════════════════════════════════════════════════════════
class DashboardStatsResponse(BaseModel):
    total_customers: int
    active_journeys: int
    avg_health_score: float
    avg_frustration_score: float
    high_risk_customers: int
    open_cases: int
    total_events_today: int
    channel_distribution: dict  # channel -> count
    health_distribution: dict  # range -> count
    journey_status_distribution: dict  # status -> count
    recent_events: list[LiveEventResponse] = []
    top_risk_customers: list[CustomerResponse] = []


class KPIResponse(BaseModel):
    name: str
    value: float | int | str
    change: float | None = None  # percentage change
    trend: str = "stable"  # up, down, stable
    icon: str = ""


class FunnelStageResponse(BaseModel):
    stage: str
    count: int
    percentage: float
    drop_off_rate: float = 0.0


class AnalyticsResponse(BaseModel):
    kpis: list[KPIResponse]
    funnel: list[FunnelStageResponse]
    channel_distribution: dict
    journey_trends: list[dict]
    sentiment_over_time: list[dict]
    frustration_heatmap: list[dict]
