"""Lightweight runtime ASGI instrumentation using the OpenTelemetry SDK."""

from __future__ import annotations

from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.correlation import ensure_request_context
from app.core import opentelemetry


class OpenTelemetryRuntimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if not opentelemetry.is_enabled(request.app):
            return await call_next(request)
        settings = getattr(request.app.state, "settings", None)
        context = ensure_request_context(request, getattr(settings, "request_id_header", "X-Request-ID"))
        started = perf_counter()
        attributes = {
            "eos.request_id": context["request_id"],
            "eos.correlation_id": context["correlation_id"],
            "http.method": request.method,
            "http.route": request.url.path,
        }
        try:
            from opentelemetry.trace import Status, StatusCode

            with opentelemetry.start_span(f"{request.method} {request.url.path}", **attributes) as span:
                response = await call_next(request)
                duration_ms = max(0, int((perf_counter() - started) * 1000))
                if span is not None:
                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("eos.duration_ms", duration_ms)
                    if response.status_code >= 500:
                        span.set_status(Status(StatusCode.ERROR))
                opentelemetry.record_request_metrics(method=request.method, path=request.url.path, status_code=response.status_code, duration_ms=duration_ms, environment=getattr(settings, "otel_environment", "development"))
                trace_id, _ = opentelemetry.current_ids()
                if trace_id:
                    response.headers["X-EOS-OTEL-Trace-ID"] = trace_id
                return response
        except Exception as error:
            with opentelemetry.start_span("request exception") as span:
                if span is not None:
                    span.record_exception(error)
                opentelemetry.record_request_metrics(method=request.method, path=request.url.path, status_code=500, duration_ms=max(0, int((perf_counter() - started) * 1000)), environment=getattr(settings, "otel_environment", "development"))
            raise
