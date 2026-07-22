"""
AmEx Pulse — Main Application Entry Point
===========================================
AI-Powered Cross-Channel Customer Journey Intelligence Platform

FastAPI application with:
- REST API (v1)
- WebSocket for real-time events
- CORS middleware
- Database initialization & seeding
- AI pipeline preloading
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.infrastructure.database.session import init_db, close_db, async_session_factory
from app.infrastructure.database.seed import seed_database
from app.api.v1.router import api_router

settings = get_settings()


# ── WebSocket Connection Manager ─────────────────────────────────
class ConnectionManager:
    """Manages WebSocket connections for real-time event broadcasting."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


ws_manager = ConnectionManager()


# ── Application Lifespan ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database
    await init_db()
    print("Database initialized")

    # Seed data
    async with async_session_factory() as session:
        await seed_database(session)

    print("Application ready")

    yield

    # Shutdown
    await close_db()
    print("Application shutdown complete")


# ── Create Application ───────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include API Routes ───────────────────────────────────────────
app.include_router(api_router)


# ── WebSocket Endpoint ───────────────────────────────────────────
@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """Real-time event stream via WebSocket."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ── Health Check ─────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Application health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "description": settings.APP_DESCRIPTION,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
