"""
AmEx Pulse — Journey Endpoints
================================
Journey data, graph visualization, and AI summary.
"""

import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.models import Journey, JourneyStep, Customer, Event, Channel
from app.domain.schemas.schemas import (
    JourneyResponse,
    JourneyStepResponse,
    JourneyGraphResponse,
    JourneyGraphNode,
    JourneyGraphEdge,
)
from app.core.constants import CHANNEL_METADATA, ChannelType

router = APIRouter(prefix="/journeys", tags=["Journeys"])


@router.get("", response_model=list[JourneyResponse])
async def list_journeys(
    customer_id: str | None = None,
    status: str | None = None,
    journey_type: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
):
    """List journeys with optional filters."""
    query = select(Journey).options(selectinload(Journey.steps))

    if customer_id:
        query = query.where(Journey.customer_id == customer_id)
    if status:
        query = query.where(Journey.status == status)
    if journey_type:
        query = query.where(Journey.journey_type == journey_type)

    query = query.order_by(desc(Journey.started_at)).limit(limit)
    result = await db.execute(query)
    journeys = result.scalars().all()

    return [
        JourneyResponse(
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
        for j in journeys
    ]


@router.get("/{journey_id}", response_model=JourneyResponse)
async def get_journey(
    journey_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get journey detail with all steps."""
    result = await db.execute(
        select(Journey)
        .options(selectinload(Journey.steps))
        .where(Journey.id == journey_id)
    )
    journey = result.scalar_one_or_none()

    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")

    return JourneyResponse(
        id=journey.id,
        customer_id=journey.customer_id,
        journey_type=journey.journey_type,
        status=journey.status,
        progress=journey.progress,
        detected_intent=journey.detected_intent,
        intent_confidence=journey.intent_confidence,
        started_at=journey.started_at,
        completed_at=journey.completed_at,
        ai_summary=journey.ai_summary,
        steps=[JourneyStepResponse.model_validate(s) for s in journey.steps],
    )


@router.get("/{journey_id}/graph", response_model=JourneyGraphResponse)
async def get_journey_graph(
    journey_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Generate graph visualization data for React Flow.
    Creates a node-edge graph showing Customer → Channels → Events → Journey relationships.
    """
    result = await db.execute(
        select(Journey)
        .options(selectinload(Journey.steps))
        .where(Journey.id == journey_id)
    )
    journey = result.scalar_one_or_none()

    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")

    # Get customer
    cust_result = await db.execute(
        select(Customer).where(Customer.id == journey.customer_id)
    )
    customer = cust_result.scalar_one_or_none()

    # Get events for this journey's customer
    events_result = await db.execute(
        select(Event)
        .where(Event.customer_id == journey.customer_id)
        .order_by(Event.occurred_at)
        .limit(20)
    )
    events = events_result.scalars().all()

    # Get channels
    channels_result = await db.execute(select(Channel))
    channels_map = {c.id: c for c in channels_result.scalars().all()}

    nodes = []
    edges = []
    used_channels = set()

    # Customer node (center)
    if customer:
        nodes.append(JourneyGraphNode(
            id=f"customer-{customer.id}",
            type="customer",
            label=f"{customer.first_name} {customer.last_name}",
            data={
                "card_type": customer.card_type,
                "health_score": customer.health_score,
                "frustration_score": customer.frustration_score,
            },
        ))

    # Journey node
    nodes.append(JourneyGraphNode(
        id=f"journey-{journey.id}",
        type="journey",
        label=journey.journey_type.replace("_", " ").title(),
        data={
            "status": journey.status,
            "progress": journey.progress,
            "intent": journey.detected_intent,
        },
    ))

    if customer:
        edges.append(JourneyGraphEdge(
            id=f"edge-customer-journey",
            source=f"customer-{customer.id}",
            target=f"journey-{journey.id}",
            label="undertakes",
            animated=journey.status == "in_progress",
        ))

    # Channel and event nodes
    for event in events:
        ch = channels_map.get(event.channel_id)
        if ch and ch.id not in used_channels:
            used_channels.add(ch.id)
            nodes.append(JourneyGraphNode(
                id=f"channel-{ch.id}",
                type="channel",
                label=ch.display_name,
                data={"icon": ch.icon, "color": ch.color},
            ))
            if customer:
                edges.append(JourneyGraphEdge(
                    id=f"edge-customer-ch-{ch.id}",
                    source=f"customer-{customer.id}",
                    target=f"channel-{ch.id}",
                    label="interacts via",
                ))

        # Event node
        nodes.append(JourneyGraphNode(
            id=f"event-{event.id}",
            type="event",
            label=event.event_name[:40],
            data={
                "event_type": event.event_type,
                "sentiment": event.sentiment_score,
                "emotion": event.detected_emotion,
            },
        ))

        if ch:
            edges.append(JourneyGraphEdge(
                id=f"edge-ch-event-{event.id}",
                source=f"channel-{ch.id}",
                target=f"event-{event.id}",
                label=event.event_type,
            ))

    # Journey step nodes
    for step in journey.steps:
        nodes.append(JourneyGraphNode(
            id=f"step-{step.id}",
            type="step",
            label=step.step_name,
            data={"status": step.step_status, "order": step.step_order},
        ))
        edges.append(JourneyGraphEdge(
            id=f"edge-journey-step-{step.id}",
            source=f"journey-{journey.id}",
            target=f"step-{step.id}",
            label=f"Step {step.step_order}",
            animated=step.step_status == "pending",
        ))

    return JourneyGraphResponse(nodes=nodes, edges=edges)
