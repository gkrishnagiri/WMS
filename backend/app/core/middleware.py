"""HTTP middleware shared by all API routes."""

from __future__ import annotations

import logging

from app.core.correlation import ensure_request_context
from app.core import opentelemetry
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        context = ensure_request_context(request, self.header_name)
        request_id = context["request_id"]
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Request failed",
                extra={"request_id": request_id, "method": request.method, "path": request.url.path},
            )
            raise
        response.headers[self.header_name] = request_id
        response.headers["X-Correlation-ID"] = context["correlation_id"]
        response.headers["X-EOS-Runtime-Trace-ID"] = context["runtime_trace_id"]
        otel_trace_id, _ = opentelemetry.current_ids()
        if otel_trace_id:
            response.headers["X-EOS-OTEL-Trace-ID"] = otel_trace_id
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
        )
        return response
