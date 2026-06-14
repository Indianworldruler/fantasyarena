"""
Structured JSON logging for FantasyArena.

System Design: Monitoring
In production this feeds into an ELK stack (Elasticsearch + Logstash + Kibana)
or Datadog. Each log line is valid JSON for easy parsing by log aggregators.

Three observability pillars implemented here:
  1. Logging  — structured JSON per request/event
  2. Metrics  — in-memory counters (production: Prometheus)
  3. Tracing  — request_id correlation across log lines (production: Jaeger/Zipkin)
"""

import json
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# ── In-memory metrics store ─────────────────────────────────────────────────
# Production replacement: Prometheus with push-gateway or /metrics scrape endpoint

class MetricsStore:
    def __init__(self):
        self.request_count: dict[str, int]     = defaultdict(int)
        self.error_count: dict[str, int]        = defaultdict(int)
        self.event_count: dict[str, int]        = defaultdict(int)
        self.latency_total: dict[str, float]    = defaultdict(float)
        self.started_at: datetime               = datetime.now(timezone.utc)

    def record_request(self, method: str, path: str, status: int, latency_ms: float):
        key = f"{method} {path}"
        self.request_count[key] += 1
        self.latency_total[key] += latency_ms
        if status >= 400:
            self.error_count[key] += 1

    def record_event(self, event_type: str):
        self.event_count[event_type] += 1

    def snapshot(self) -> dict:
        uptime = (datetime.now(timezone.utc) - self.started_at).total_seconds()
        total_requests = sum(self.request_count.values())
        total_errors   = sum(self.error_count.values())

        avg_latencies = {
            k: round(self.latency_total[k] / self.request_count[k], 2)
            for k in self.request_count
        }

        return {
            "uptime_seconds":   round(uptime, 1),
            "total_requests":   total_requests,
            "total_errors":     total_errors,
            "error_rate_pct":   round(total_errors / max(total_requests, 1) * 100, 2),
            "requests_by_route": dict(self.request_count),
            "avg_latency_ms":    avg_latencies,
            "event_counts":      dict(self.event_count),
        }


metrics = MetricsStore()


# ── JSON log formatter ───────────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "ts":      datetime.now(timezone.utc).isoformat(),
            "level":   record.levelname,
            "service": record.name,
            "msg":     record.getMessage(),
        }
        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)
        return json.dumps(log)


def setup_json_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for handler in root.handlers:
        handler.setFormatter(JSONFormatter())


# ── Request logging middleware ───────────────────────────────────────────────

logger = logging.getLogger("http")

SKIP_LOG_PATHS = {"/health", "/", "/docs", "/openapi.json", "/redoc"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Intercepts every HTTP request/response.
    Assigns a unique request_id for distributed tracing correlation.
    Records latency in the metrics store.

    Production equivalent: OpenTelemetry auto-instrumentation middleware.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in SKIP_LOG_PATHS:
            return await call_next(request)

        request_id = str(uuid.uuid4())[:8]
        start      = time.perf_counter()

        response   = await call_next(request)

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        metrics.record_request(request.method, request.url.path, response.status_code, latency_ms)

        logger.info(json.dumps({
            "request_id": request_id,
            "method":     request.method,
            "path":       request.url.path,
            "status":     response.status_code,
            "latency_ms": latency_ms,
        }))

        response.headers["X-Request-ID"] = request_id
        return response
