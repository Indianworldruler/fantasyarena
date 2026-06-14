"""
FantasyArena — Main Application Entry Point

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHITECTURE PATTERNS DEMONSTRATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Facade    : This FastAPI app works as the API Gateway — single entry point
            for all microservice domains such as auth, contests, teams,
            scoring, leaderboard, payments, notifications, and admin.

Proxy     : JWT middleware intercepts protected routes before business
            logic executes. auth_middleware.py → get_current_user

Observer  : match.event → EventBus → handle_match_event
            → leaderboard.updated → WebSocket broadcast
            → notification.send → DB persist + user push

Factory   : ContestFactory.create() encapsulates contest creation rules
            and validation.

Strategy  : ScoringStrategyFactory selects CricketScoringStrategy /
            FootballScoringStrategy / BasketballScoringStrategy at runtime
            based on sport type.

Adapter   : Sports feed adapter converts raw match events into internal
            scoring events.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM DESIGN CONCEPTS DEMONSTRATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAP Theorem   : SQLite is used for local consistency-focused storage.
                In production: Cassandra for leaderboard-heavy AP use cases,
                PostgreSQL for wallet/payment CP/ACID requirements.

Caching       : Leaderboard uses in-memory Python sorting.
                Production: Redis sorted sets using ZADD/ZRANGE.

Message Queue : EventBus simulates Kafka-style pub/sub.
                Production: Kafka topic such as match.events with consumer
                groups for scoring, leaderboard, and notifications.

Sharding      : Users can shard by user_id % N.
                Leaderboards can shard by contest_id.

Replication   : SQLite is single-node for academic/demo use.
                Production: PostgreSQL primary + read replicas.

Load Balancing: Single Uvicorn process for demo.
                Production: Nginx/API Gateway + multiple Uvicorn workers.

Horizontal Scaling: WebSocket manager uses in-process rooms.
                    Production: Redis Pub/Sub for cross-instance fan-out.

Rate Limiting : Not implemented in demo.
                Production: token-bucket middleware or gateway-level limits.
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import init_db
from logger import setup_json_logging, RequestLoggingMiddleware, metrics
from routers import (
    auth,
    users,
    payments,
    contests,
    teams,
    scoring,
    leaderboard,
    notifications,
    websocket,
)
from admin.router import router as admin_router
from event_handlers import register_handlers


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("fantasyarena.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.APP_NAME, settings.VERSION)

    setup_json_logging()

    init_db()
    logger.info("Database tables initialised")

    try:
        from seed import seed_players

        seed_players()
        logger.info("Seed data loaded")
    except Exception as exc:
        logger.warning("Seed data skipped or failed: %s", exc)

    register_handlers()
    logger.info("Event bus handlers registered — Observer pipeline active")

    yield

    logger.info("Shutting down FantasyArena gracefully")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Fantasy Sports Platform — System Design + Implementation",
    lifespan=lifespan,
)


app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(payments.router)
app.include_router(contests.router)
app.include_router(teams.router)
app.include_router(scoring.router)
app.include_router(leaderboard.router)
app.include_router(notifications.router)
app.include_router(websocket.router)
app.include_router(admin_router)


frontend_path = Path(__file__).resolve().parent.parent / "frontend"

if frontend_path.exists():
    app.mount(
        "/app",
        StaticFiles(directory=str(frontend_path), html=True),
        name="frontend",
    )
    logger.info("Frontend mounted at /app from %s", frontend_path)
else:
    logger.info("Frontend folder not mounted because it was not found at %s", frontend_path)


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "FantasyArena API is running",
        "docs": "/docs",
        "health": "/health",
        "frontend": "/app" if frontend_path.exists() else "Use separate Render frontend URL",
    }


@app.get("/health", tags=["System"])
async def health():
    from routers.websocket import manager

    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "active_ws_rooms": manager.active_connections(),
    }


@app.get("/metrics", tags=["System"])
async def public_metrics():
    """
    Public lightweight metrics endpoint.
    Production usage: Prometheus scrape target.
    """
    return metrics.snapshot()