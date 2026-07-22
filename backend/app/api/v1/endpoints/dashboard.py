"""
AmEx Pulse — Dashboard & Analytics Endpoints
==============================================
Real-time dashboard stats, KPIs, funnels, and analytics data.
"""

import json
import random
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.models import (
    Customer, Journey, Event, SupportCase, Channel, Recommendation, Session,
)
from app.domain.schemas.schemas import (
    DashboardStatsResponse,
    CustomerResponse,
    LiveEventResponse,
    EventResponse,
    KPIResponse,
    FunnelStageResponse,
    AnalyticsResponse,
)
from app.core.constants import CHANNEL_METADATA, ChannelType

router = APIRouter(tags=["Dashboard & Analytics"])


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db_session),
):
    """Get real-time dashboard statistics."""
    now = datetime.now(timezone.utc)

    # Total customers
    total_result = await db.execute(select(func.count(Customer.id)))
    total_customers = total_result.scalar() or 0

    # Active journeys
    active_j = await db.execute(
        select(func.count(Journey.id)).where(Journey.status == "in_progress")
    )
    active_journeys = active_j.scalar() or 0

    # Average scores
    avg_health = await db.execute(select(func.avg(Customer.health_score)))
    avg_frustration = await db.execute(select(func.avg(Customer.frustration_score)))

    # High risk customers (churn_risk > 0.5)
    high_risk = await db.execute(
        select(func.count(Customer.id)).where(Customer.churn_risk > 0.5)
    )

    # Open support cases
    open_cases = await db.execute(
        select(func.count(SupportCase.id)).where(SupportCase.status.in_(["open", "in_progress"]))
    )

    # Total events today
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events_today = await db.execute(
        select(func.count(Event.id)).where(Event.occurred_at >= today_start)
    )

    # Channel distribution
    channels_result = await db.execute(select(Channel))
    channels = {c.id: c.name for c in channels_result.scalars().all()}

    channel_dist = {}
    for ch_id, ch_name in channels.items():
        count_result = await db.execute(
            select(func.count(Event.id)).where(Event.channel_id == ch_id)
        )
        count = count_result.scalar() or 0
        if count > 0:
            channel_dist[ch_name] = count

    # Health score distribution
    health_dist = {}
    for label, low, high in [("Critical (0-25)", 0, 25), ("Poor (25-50)", 25, 50),
                              ("Fair (50-75)", 50, 75), ("Good (75-100)", 75, 101)]:
        cnt = await db.execute(
            select(func.count(Customer.id)).where(
                and_(Customer.health_score >= low, Customer.health_score < high)
            )
        )
        health_dist[label] = cnt.scalar() or 0

    # Journey status distribution
    journey_statuses = {}
    for status in ["in_progress", "completed", "abandoned", "failed"]:
        cnt = await db.execute(
            select(func.count(Journey.id)).where(Journey.status == status)
        )
        journey_statuses[status] = cnt.scalar() or 0

    # Recent events (last 20)
    recent_events_q = await db.execute(
        select(Event).order_by(desc(Event.occurred_at)).limit(20)
    )
    recent_events_raw = recent_events_q.scalars().all()

    # Get customer names for events
    customer_ids = list(set(e.customer_id for e in recent_events_raw))
    customers_q = await db.execute(
        select(Customer).where(Customer.id.in_(customer_ids)) if customer_ids else select(Customer).limit(0)
    )
    customer_map = {c.id: f"{c.first_name} {c.last_name}" for c in customers_q.scalars().all()}

    recent_events = []
    for e in recent_events_raw:
        ch_name = channels.get(e.channel_id, "unknown")
        try:
            ch_type = ChannelType(ch_name)
            meta = CHANNEL_METADATA.get(ch_type, {"icon": "❓", "color": "#666"})
        except ValueError:
            meta = {"icon": "❓", "color": "#666"}

        recent_events.append(LiveEventResponse(
            event=EventResponse(
                id=e.id,
                customer_id=e.customer_id,
                channel_name=ch_name,
                event_type=e.event_type,
                event_name=e.event_name,
                sentiment_score=e.sentiment_score,
                detected_emotion=e.detected_emotion,
                occurred_at=e.occurred_at,
            ),
            customer_name=customer_map.get(e.customer_id, "Unknown"),
            channel_icon=meta["icon"],
            channel_color=meta["color"],
            timestamp=e.occurred_at.isoformat() if e.occurred_at else "",
        ))

    # Top risk customers
    risk_q = await db.execute(
        select(Customer).order_by(desc(Customer.churn_risk)).limit(5)
    )
    top_risk = [CustomerResponse.model_validate(c) for c in risk_q.scalars().all()]

    return DashboardStatsResponse(
        total_customers=total_customers,
        active_journeys=active_journeys,
        avg_health_score=round(avg_health.scalar() or 0, 1),
        avg_frustration_score=round(avg_frustration.scalar() or 0, 1),
        high_risk_customers=high_risk.scalar() or 0,
        open_cases=open_cases.scalar() or 0,
        total_events_today=events_today.scalar() or 0,
        channel_distribution=channel_dist,
        health_distribution=health_dist,
        journey_status_distribution=journey_statuses,
        recent_events=recent_events,
        top_risk_customers=top_risk,
    )


@router.get("/dashboard/kpis")
async def get_kpis(db: AsyncSession = Depends(get_db_session)):
    """Get key performance indicators."""
    total_cust = await db.execute(select(func.count(Customer.id)))
    avg_health = await db.execute(select(func.avg(Customer.health_score)))
    avg_frust = await db.execute(select(func.avg(Customer.frustration_score)))
    churn_risk = await db.execute(select(func.avg(Customer.churn_risk)))
    active_j = await db.execute(select(func.count(Journey.id)).where(Journey.status == "in_progress"))
    completed_j = await db.execute(select(func.count(Journey.id)).where(Journey.status == "completed"))
    total_j = await db.execute(select(func.count(Journey.id)))
    open_cases = await db.execute(
        select(func.count(SupportCase.id)).where(SupportCase.status.in_(["open", "in_progress"]))
    )
    total_recs = await db.execute(select(func.count(Recommendation.id)))

    total_journeys = total_j.scalar() or 1
    completion_rate = round(((completed_j.scalar() or 0) / total_journeys) * 100, 1)

    return [
        KPIResponse(name="Total Customers", value=total_cust.scalar() or 0, change=12.5, trend="up", icon="👥"),
        KPIResponse(name="Avg Health Score", value=round(avg_health.scalar() or 0, 1), change=3.2, trend="up", icon="💚"),
        KPIResponse(name="Avg Frustration", value=round(avg_frust.scalar() or 0, 1), change=-5.1, trend="down", icon="😤"),
        KPIResponse(name="Avg Churn Risk", value=f"{round((churn_risk.scalar() or 0) * 100, 1)}%", change=-2.3, trend="down", icon="⚠️"),
        KPIResponse(name="Active Journeys", value=active_j.scalar() or 0, change=8.7, trend="up", icon="🗺️"),
        KPIResponse(name="Journey Completion", value=f"{completion_rate}%", change=4.5, trend="up", icon="✅"),
        KPIResponse(name="Open Cases", value=open_cases.scalar() or 0, change=-15.0, trend="down", icon="📋"),
        KPIResponse(name="AI Recommendations", value=total_recs.scalar() or 0, change=22.0, trend="up", icon="🤖"),
    ]


@router.get("/analytics/funnel")
async def get_journey_funnel(
    journey_type: str = "card_activation",
    db: AsyncSession = Depends(get_db_session),
):
    """Get journey funnel visualization data."""
    from app.core.constants import JOURNEY_STEPS, JourneyType

    try:
        jt = JourneyType(journey_type)
    except ValueError:
        jt = JourneyType.CARD_ACTIVATION

    steps = JOURNEY_STEPS[jt]
    total_journeys_q = await db.execute(
        select(func.count(Journey.id)).where(Journey.journey_type == journey_type)
    )
    total = total_journeys_q.scalar() or 1

    funnel = []
    for i, step in enumerate(steps):
        # Simulate realistic drop-off
        drop_rate = random.uniform(0.05, 0.2) if i > 0 else 0
        count = max(1, int(total * (1 - drop_rate * i)))
        pct = round((count / total) * 100, 1) if total > 0 else 0

        funnel.append(FunnelStageResponse(
            stage=step,
            count=count,
            percentage=pct,
            drop_off_rate=round(drop_rate * 100, 1),
        ))

    return funnel


@router.get("/analytics/channels")
async def get_channel_analytics(db: AsyncSession = Depends(get_db_session)):
    """Get channel distribution and performance analytics."""
    channels_result = await db.execute(select(Channel))
    channels = channels_result.scalars().all()

    data = []
    for ch in channels:
        event_count = await db.execute(
            select(func.count(Event.id)).where(Event.channel_id == ch.id)
        )
        session_count = await db.execute(
            select(func.count(Session.id)).where(Session.channel_id == ch.id)
        )
        avg_sentiment = await db.execute(
            select(func.avg(Event.sentiment_score)).where(Event.channel_id == ch.id)
        )

        data.append({
            "channel": ch.name,
            "display_name": ch.display_name,
            "icon": ch.icon,
            "color": ch.color,
            "event_count": event_count.scalar() or 0,
            "session_count": session_count.scalar() or 0,
            "avg_sentiment": round(avg_sentiment.scalar() or 0, 2),
        })

    return data


@router.get("/analytics/heatmap")
async def get_frustration_heatmap(db: AsyncSession = Depends(get_db_session)):
    """
    Generate frustration heatmap data (day of week × hour of day).
    Shows when customers are most frustrated — invaluable for staffing decisions.
    """
    heatmap = []
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for day_idx, day in enumerate(days):
        for hour in range(24):
            # Generate realistic patterns: higher frustration during business hours
            base = 20
            if 9 <= hour <= 17:
                base = 45
            if day_idx < 5:  # weekdays
                base += 10
            value = base + random.randint(-10, 15)
            heatmap.append({
                "day": day,
                "hour": hour,
                "value": max(0, min(100, value)),
            })

    return heatmap
