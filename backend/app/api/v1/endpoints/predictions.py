"""
AmEx Pulse — AI Prediction & Recommendation Endpoints
=======================================================
Run AI predictions, get recommendations, and manage actions.
"""

import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.models import Customer, Prediction, Recommendation, Event, Journey
from app.domain.schemas.schemas import (
    PredictionResponse,
    PredictionRunRequest,
    RecommendationResponse,
)
from app.ai.pipeline import AIPipeline

router = APIRouter(tags=["Predictions & Recommendations"])


@router.get("/predictions/{customer_id}", response_model=list[PredictionResponse])
async def get_predictions(
    customer_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get all predictions for a customer."""
    result = await db.execute(
        select(Prediction)
        .where(Prediction.customer_id == customer_id)
        .order_by(desc(Prediction.predicted_at))
    )
    predictions = result.scalars().all()
    return [PredictionResponse.model_validate(p) for p in predictions]


@router.post("/predictions/run")
async def run_predictions(
    request: PredictionRunRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Run AI prediction pipeline for a customer.
    Executes all requested prediction types and stores results.
    """
    # Get customer
    cust_result = await db.execute(
        select(Customer).where(Customer.id == request.customer_id)
    )
    customer = cust_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get customer events
    events_result = await db.execute(
        select(Event)
        .where(Event.customer_id == request.customer_id)
        .order_by(desc(Event.occurred_at))
        .limit(50)
    )
    events = events_result.scalars().all()

    # Get journeys
    journeys_result = await db.execute(
        select(Journey)
        .where(Journey.customer_id == request.customer_id)
        .order_by(desc(Journey.started_at))
    )
    journeys = journeys_result.scalars().all()

    # Run AI pipeline
    pipeline = AIPipeline()
    results = pipeline.run_full_pipeline(
        customer=customer,
        events=events,
        journeys=journeys,
        prediction_types=request.prediction_types,
    )

    # Store predictions
    stored_predictions = []
    for pred_type, result_data in results.items():
        prediction = Prediction(
            id=str(uuid.uuid4()),
            customer_id=request.customer_id,
            prediction_type=pred_type,
            prediction_result=json.dumps(result_data.get("result", {})),
            confidence=result_data.get("confidence", 0.0),
            explanation=result_data.get("explanation", ""),
            model_version="v1.0.0",
            predicted_at=datetime.now(timezone.utc),
        )
        db.add(prediction)
        stored_predictions.append({
            "type": pred_type,
            "result": result_data,
        })

    # Update customer scores based on predictions
    if "health" in results:
        customer.health_score = results["health"].get("result", {}).get("score", customer.health_score)
    if "frustration" in results:
        customer.frustration_score = results["frustration"].get("result", {}).get("score", customer.frustration_score)
    if "churn" in results:
        customer.churn_risk = results["churn"].get("result", {}).get("risk", customer.churn_risk)

    # Generate recommendations if NBA is requested
    if "nba" in results and results["nba"].get("result", {}).get("actions"):
        for action in results["nba"]["result"]["actions"]:
            rec = Recommendation(
                id=str(uuid.uuid4()),
                customer_id=request.customer_id,
                action_type=action["type"],
                action_description=action["description"],
                confidence=action.get("confidence", 0.0),
                reasoning=action.get("reasoning", ""),
                status="pending",
            )
            db.add(rec)

    await db.commit()

    return {
        "customer_id": request.customer_id,
        "predictions": stored_predictions,
        "scores_updated": {
            "health_score": customer.health_score,
            "frustration_score": customer.frustration_score,
            "churn_risk": customer.churn_risk,
        },
    }


@router.get("/recommendations/{customer_id}", response_model=list[RecommendationResponse])
async def get_recommendations(
    customer_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get all recommendations for a customer."""
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.customer_id == customer_id)
        .order_by(desc(Recommendation.created_at))
    )
    return [RecommendationResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/recommendations/{recommendation_id}/act")
async def act_on_recommendation(
    recommendation_id: str,
    action: str = "accepted",
    db: AsyncSession = Depends(get_db_session),
):
    """Accept or reject a recommendation."""
    result = await db.execute(
        select(Recommendation).where(Recommendation.id == recommendation_id)
    )
    rec = result.scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = action
    rec.acted_at = datetime.now(timezone.utc)
    await db.commit()

    return {"status": "ok", "recommendation_id": recommendation_id, "new_status": action}
