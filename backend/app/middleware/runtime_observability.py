"""Safe, non-invasive runtime request telemetry middleware."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.correlation import ensure_request_context
from app.services import runtime_observability_service
from app.core import opentelemetry

logger = logging.getLogger(__name__)


class RuntimeObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        settings = getattr(request.app.state, "settings", None)
        context = ensure_request_context(request, getattr(settings, "request_id_header", "X-Request-ID"))
        capture = bool(getattr(settings, "runtime_observability_enabled", True) and getattr(settings, "runtime_observability_capture_requests", True) and runtime_observability_service.is_captured_path(request.url.path, bool(getattr(settings, "runtime_observability_capture_health", False))))
        started_at = datetime.now(timezone.utc)
        timer = perf_counter()
        try:
            response = await call_next(request)
        except Exception as error:
            if capture:
                self._record(request, context, started_at, timer, 500, str(error))
            raise
        duration_ms = max(0, int((perf_counter() - timer) * 1000))
        if capture:
            self._record(request, context, started_at, timer, response.status_code, None)
        response.headers["X-Request-ID"] = context["request_id"]
        response.headers["X-Correlation-ID"] = context["correlation_id"]
        response.headers["X-EOS-Runtime-Trace-ID"] = context["runtime_trace_id"]
        otel_trace_id, _ = opentelemetry.current_ids()
        if otel_trace_id:
            response.headers["X-EOS-OTEL-Trace-ID"] = otel_trace_id
        return response

    @staticmethod
    def _record(request: Request, context: dict[str, str], started_at: datetime, timer: float, status_code: int, error_message: str | None) -> None:
        factory = getattr(request.app.state, "runtime_observability_session_factory", None)
        if factory is None:
            return
        db = None
        try:
            db = factory()
            duration_ms = max(0, int((perf_counter() - timer) * 1000))
            otel_trace_id, otel_span_id = opentelemetry.current_ids()
            runtime_observability_service.record_http_request_trace(db, method=request.method, path=request.url.path, status_code=status_code, duration_ms=duration_ms, started_at=started_at, request_id=context["request_id"], correlation_id=context["correlation_id"], runtime_trace_id=context["runtime_trace_id"], traceparent=context.get("traceparent"), client_host=request.client.host if request.client else None, error_message=error_message, otel_trace_id=otel_trace_id, otel_span_id=otel_span_id)
            db.commit()
        except Exception:
            if db is not None:
                try: db.rollback()
                except Exception: pass
            logger.exception("Runtime telemetry recording failed; original request is unaffected.", extra={"request_id": context.get("request_id"), "correlation_id": context.get("correlation_id")})
        finally:
            if db is not None:
                try: db.close()
                except Exception: pass
