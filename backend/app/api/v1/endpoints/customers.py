"""
AmEx Pulse — Customer Endpoints
=================================
Customer CRUD, profile views, and timeline data.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.models import Customer, Event, Journey, Recommendation, SupportCase, Prediction, Channel
from app.domain.schemas.schemas import (
    CustomerResponse,
    CustomerListResponse,
    CustomerDetailResponse,
    JourneyResponse,
    JourneyStepResponse,
    EventResponse,
    RecommendationResponse,
    SupportCaseResponse,
    PredictionResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    card_type: str | None = None,
    risk_level: str | None = None,
    sort_by: str = "health_score",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db_session),
):
    """
    List customers with filtering, pagination, and sorting.
    Supports search by name/email, filter by card type and risk level.
    """
    query = select(Customer)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Customer.first_name.ilike(search_term)) |
            (Customer.last_name.ilike(search_term)) |
            (Customer.email.ilike(search_term)) |
            (Customer.universal_id.ilike(search_term))
        )

    if card_type:
        query = query.where(Customer.card_type == card_type)

    if risk_level:
        if risk_level == "high":
            query = query.where(Customer.churn_risk >= 0.6)
        elif risk_level == "medium":
            query = query.where(Customer.churn_risk.between(0.3, 0.6))
        elif risk_level == "low":
            query = query.where(Customer.churn_risk < 0.3)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    sort_column = getattr(Customer, sort_by, Customer.health_score)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    customers = result.scalars().all()

    return CustomerListResponse(
        customers=[CustomerResponse.model_validate(c) for c in customers],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get detailed customer profile with all related data."""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Fetch related data
    journeys_result = await db.execute(
        select(Journey)
        .options(selectinload(Journey.steps))
        .where(Journey.customer_id == customer_id)
        .order_by(desc(Journey.started_at))
    )
    journeys = journeys_result.scalars().all()

    events_result = await db.execute(
        select(Event)
        .where(Event.customer_id == customer_id)
        .order_by(desc(Event.occurred_at))
        .limit(50)
    )
    events = events_result.scalars().all()

    # Get channel names for events
    channels_result = await db.execute(select(Channel))
    channels_map = {c.id: c.name for c in channels_result.scalars().all()}

    recs_result = await db.execute(
        select(Recommendation)
        .where(Recommendation.customer_id == customer_id)
        .order_by(desc(Recommendation.created_at))
    )
    recommendations = recs_result.scalars().all()

    cases_result = await db.execute(
        select(SupportCase)
        .where(SupportCase.customer_id == customer_id)
        .order_by(desc(SupportCase.created_at))
    )
    cases = cases_result.scalars().all()

    preds_result = await db.execute(
        select(Prediction)
        .where(Prediction.customer_id == customer_id)
        .order_by(desc(Prediction.predicted_at))
    )
    predictions = preds_result.scalars().all()

    # Build response
    event_responses = []
    for e in events:
        er = EventResponse.model_validate(e)
        er.channel_name = channels_map.get(e.channel_id, "unknown")
        event_responses.append(er)

    journey_responses = []
    for j in journeys:
        jr = JourneyResponse(
            id=j.id,
            customer_id=j.customer_id,
            journey_type=j.journey_type,
            status=j.status,
            progress=j.progress,
            detected_intent=j.detected_intent,
            intent_confidence=j.intent_confidence,
            started_at=j.started_at,
            completed_at=j.completed_at,
            ai_summary=j.ai_summary,
            steps=[JourneyStepResponse.model_validate(s) for s in j.steps],
        )
        journey_responses.append(jr)

    return CustomerDetailResponse(
        id=customer.id,
        universal_id=customer.universal_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone,
        card_last_four=customer.card_last_four,
        member_since=customer.member_since,
        card_type=customer.card_type,
        health_score=customer.health_score,
        frustration_score=customer.frustration_score,
        churn_risk=customer.churn_risk,
        created_at=customer.created_at,
        journeys=journey_responses,
        recent_events=event_responses,
        recommendations=[RecommendationResponse.model_validate(r) for r in recommendations],
        support_cases=[SupportCaseResponse.model_validate(c) for c in cases],
        predictions=[PredictionResponse.model_validate(p) for p in predictions],
    )


@router.get("/{customer_id}/timeline")
async def get_customer_timeline(
    customer_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
):
    """Get chronological event timeline for a customer."""
    events_result = await db.execute(
        select(Event)
        .where(Event.customer_id == customer_id)
        .order_by(desc(Event.occurred_at))
        .limit(limit)
    )
    events = events_result.scalars().all()

    channels_result = await db.execute(select(Channel))
    channels_map = {c.id: {"name": c.name, "icon": c.icon, "color": c.color} for c in channels_result.scalars().all()}

    timeline = []
    for e in events:
        ch = channels_map.get(e.channel_id, {"name": "unknown", "icon": "❓", "color": "#666"})
        timeline.append({
            "id": e.id,
            "event_type": e.event_type,
            "event_name": e.event_name,
            "channel": ch["name"],
            "channel_icon": ch["icon"],
            "channel_color": ch["color"],
            "sentiment_score": e.sentiment_score,
            "detected_emotion": e.detected_emotion,
            "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
            "event_data": json.loads(e.event_data) if e.event_data else {},
        })

    return {"customer_id": customer_id, "timeline": timeline}
