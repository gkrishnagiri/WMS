"""Request correlation identifiers used by runtime observability."""

from __future__ import annotations

import uuid

from starlette.requests import Request


def ensure_request_context(request: Request, request_id_header: str = "X-Request-ID") -> dict[str, str]:
    """Assign stable per-request identifiers without inspecting request bodies."""
    request_id = getattr(request.state, "request_id", None) or request.headers.get(request_id_header) or str(uuid.uuid4())
    correlation_id = getattr(request.state, "correlation_id", None) or request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    runtime_trace_id = getattr(request.state, "runtime_trace_id", None) or f"runtime-{uuid.uuid4().hex}"
    traceparent = request.headers.get("traceparent")
    request.state.request_id = request_id
    request.state.correlation_id = correlation_id
    request.state.runtime_trace_id = runtime_trace_id
    request.state.traceparent = traceparent
    return {"request_id": request_id, "correlation_id": correlation_id, "runtime_trace_id": runtime_trace_id, "traceparent": traceparent or ""}
