"""
AmEx Pulse — API v1 Router
============================
Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, customers, journeys, dashboard, predictions

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(customers.router)
api_router.include_router(journeys.router)
api_router.include_router(dashboard.router)
api_router.include_router(predictions.router)
