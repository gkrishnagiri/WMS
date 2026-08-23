"""Runtime request telemetry persisted in the existing observability tables."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from uuid import UUID, uuid4

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.observability import ObsLogEvent, ObsMetricSample, ObsSpan, ObsTrace
from app.schemas.observability import LogEventResponse, MetricSampleResponse, SpanResponse, TraceResponse
from app.schemas.runtime_observability import RuntimeSummary, RuntimeTraceDetail, RuntimeProbeResponse
from app.services import observability_service

RUNTIME_MODULE = "RUNTIME_OBSERVABILITY"
RUNTIME_COMPONENT = "EOS-BACKEND-API"
EXCLUDED_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/favicon.ico", "/static")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def is_captured_path(path: str, capture_health: bool) -> bool:
    if any(path == excluded or path.startswith(f"{excluded}/") for excluded in EXCLUDED_PREFIXES):
        return False
    return capture_health or path != "/health"


def _runtime_attributes(trace: ObsTrace, db: Session) -> dict:
    span = db.scalar(select(ObsSpan).where(ObsSpan.trace_id == trace.id).order_by(ObsSpan.started_at))
    return (span.attributes or {}) if span else {}


def record_http_request_trace(
    db: Session,
    *,
    method: str,
    path: str,
    status_code: int,
    duration_ms: int,
    started_at: datetime,
    request_id: str,
    correlation_id: str,
    runtime_trace_id: str,
    traceparent: str | None,
    client_host: str | None,
    error_message: str | None = None,
    otel_trace_id: str | None = None,
    otel_span_id: str | None = None,
) -> ObsTrace:
    is_error = status_code >= 400 or error_message is not None
    is_slow = duration_ms >= 1000
    trace_status = "ERROR" if is_error else "DEGRADED" if is_slow else "SUCCESS"
    span_status = "ERROR" if is_error else "SLOW" if is_slow else "OK"
    finished_at = _now()
    attributes = {"method": method, "path": path, "status_code": status_code, "request_id": request_id, "correlation_id": correlation_id, "client_host": client_host, "traceparent": traceparent, "otel_trace_id": otel_trace_id, "otel_span_id": otel_span_id}
    trace = observability_service.create_trace(db, trace_name=f"{method} {path}"[:200], trace_type="API_REQUEST", status=trace_status, source_module=RUNTIME_MODULE, root_entity_type="API_REQUEST", root_reference=f"{method} {path}"[:160], summary=f"Runtime backend request {method} {path} completed with status {status_code} in {duration_ms} ms.", started_at=started_at, duration_ms=duration_ms, trace_identifier=runtime_trace_id)
    span = observability_service.create_span(db, trace, span_id=f"span-{uuid4().hex}", span_name="HTTP request", service_name="eos-backend", component_code=RUNTIME_COMPONENT, operation_type="HTTP_REQUEST", status=span_status, started_at=started_at, duration_ms=duration_ms, error_type="HTTP_ERROR" if is_error else None, error_message=(error_message or f"HTTP {status_code}") if is_error else None, attributes=attributes)
    observability_service.create_log_event(db, message=f"Runtime request started: {method} {path}.", event_type="REQUEST_STARTED", level="INFO", logger_name="eos.runtime", source_module=RUNTIME_MODULE, trace_id=trace.id, span_id=span.id, component_code=RUNTIME_COMPONENT, context=attributes, logged_at=started_at)
    observability_service.create_log_event(db, message=(f"Runtime request failed: {method} {path} returned {status_code}." if is_error else f"Runtime request completed: {method} {path} returned {status_code}."), event_type="REQUEST_FAILED" if is_error else "REQUEST_COMPLETED", level="ERROR" if is_error else "WARN" if is_slow else "INFO", logger_name="eos.runtime", source_module=RUNTIME_MODULE, trace_id=trace.id, span_id=span.id, component_code=RUNTIME_COMPONENT, context=attributes, logged_at=finished_at)
    observability_service.create_metric_sample(db, metric_name="api_latency_ms", metric_value=duration_ms, metric_unit="ms", component_code=RUNTIME_COMPONENT, severity="HIGH" if is_error else "MEDIUM" if is_slow else "LOW", trace_id=trace.id, attributes=attributes, recorded_at=finished_at)
    observability_service.create_metric_sample(db, metric_name="api_request_count", metric_value=1, metric_unit="count", component_code=RUNTIME_COMPONENT, severity="LOW", trace_id=trace.id, attributes=attributes, recorded_at=finished_at)
    if is_error:
        observability_service.create_metric_sample(db, metric_name="api_error_count", metric_value=1, metric_unit="count", component_code=RUNTIME_COMPONENT, severity="HIGH", trace_id=trace.id, attributes=attributes, recorded_at=finished_at)
    return trace


def _trace_response(db: Session, trace: ObsTrace, detail: bool) -> TraceResponse:
    spans = db.scalars(select(ObsSpan).where(ObsSpan.trace_id == trace.id).order_by(ObsSpan.started_at, ObsSpan.id)).all() if detail else []
    logs = db.scalars(select(ObsLogEvent).where(ObsLogEvent.trace_id == trace.id).order_by(ObsLogEvent.logged_at, ObsLogEvent.id)).all() if detail else []
    metrics = db.scalars(select(ObsMetricSample).where(ObsMetricSample.trace_id == trace.id).order_by(ObsMetricSample.recorded_at, ObsMetricSample.id)).all() if detail else []
    return TraceResponse(id=trace.id, trace_id=trace.trace_id, trace_name=trace.trace_name, trace_type=trace.trace_type, status=trace.status, source_module=trace.source_module, root_entity_type=trace.root_entity_type, root_entity_id=trace.root_entity_id, root_reference=trace.root_reference, linked_alert_id=trace.linked_alert_id, linked_triage_case_id=trace.linked_triage_case_id, linked_ticket_id=trace.linked_ticket_id, started_at=trace.started_at, ended_at=trace.ended_at, duration_ms=trace.duration_ms, summary=trace.summary, spans=[SpanResponse.model_validate(row, from_attributes=True) for row in spans], logs=[LogEventResponse.model_validate(row, from_attributes=True) for row in logs], metrics=[MetricSampleResponse.model_validate(row, from_attributes=True) for row in metrics])


def list_runtime_traces(db: Session, status: str | None = None, method: str | None = None, path: str | None = None, correlation_id: str | None = None, request_id: str | None = None) -> list[TraceResponse]:
    rows = db.scalars(select(ObsTrace).where(ObsTrace.source_module == RUNTIME_MODULE).order_by(ObsTrace.started_at.desc()).limit(200)).all()
    result = []
    for row in rows:
        attrs = _runtime_attributes(row, db)
        if status and row.status != status.upper(): continue
        if method and attrs.get("method") != method.upper(): continue
        if path and attrs.get("path") != path: continue
        if correlation_id and attrs.get("correlation_id") != correlation_id: continue
        if request_id and attrs.get("request_id") != request_id: continue
        result.append(_trace_response(db, row, False))
        if len(result) >= 100: break
    return result


def get_runtime_trace(db: Session, identifier: str) -> RuntimeTraceDetail:
    trace = db.scalar(select(ObsTrace).where(ObsTrace.source_module == RUNTIME_MODULE, ObsTrace.trace_id == identifier))
    if trace is None:
        try: trace = db.get(ObsTrace, UUID(identifier))
        except ValueError: trace = None
    if trace is None or trace.source_module != RUNTIME_MODULE:
        raise ValueError("Runtime trace not found.")
    response = _trace_response(db, trace, True)
    attrs = _runtime_attributes(trace, db)
    return RuntimeTraceDetail(**response.model_dump(), request_id=attrs.get("request_id"), correlation_id=attrs.get("correlation_id"), traceparent=attrs.get("traceparent"))


def list_runtime_logs(db: Session, level: str | None = None, event_type: str | None = None, trace_id: str | None = None, correlation_id: str | None = None) -> list[LogEventResponse]:
    rows = db.scalars(select(ObsLogEvent).where(ObsLogEvent.source_module == RUNTIME_MODULE).order_by(ObsLogEvent.logged_at.desc()).limit(200)).all()
    result = []
    for row in rows:
        if level and row.level != level.upper(): continue
        if event_type and row.event_type != event_type.upper(): continue
        if trace_id and (not row.trace or row.trace.trace_id != trace_id): continue
        if correlation_id and (not row.context or row.context.get("correlation_id") != correlation_id): continue
        result.append(LogEventResponse.model_validate(row, from_attributes=True))
    return result


def list_runtime_metrics(db: Session, metric_name: str | None = None, trace_id: str | None = None, component_code: str | None = None, severity: str | None = None) -> list[MetricSampleResponse]:
    rows = db.scalars(select(ObsMetricSample).where(ObsMetricSample.component_code == RUNTIME_COMPONENT).order_by(ObsMetricSample.recorded_at.desc()).limit(200)).all()
    result = []
    for row in rows:
        if metric_name and row.metric_name != metric_name: continue
        if component_code and row.component_code != component_code: continue
        if severity and row.severity != severity.upper(): continue
        if trace_id and (not row.trace or row.trace.trace_id != trace_id): continue
        result.append(MetricSampleResponse.model_validate(row, from_attributes=True))
    return result


def runtime_summary(db: Session, slow_threshold_ms: int) -> RuntimeSummary:
    query = select(ObsTrace).where(ObsTrace.source_module == RUNTIME_MODULE)
    total = db.scalar(select(func.count(ObsTrace.id)).where(ObsTrace.source_module == RUNTIME_MODULE)) or 0
    avg = db.scalar(select(func.avg(ObsTrace.duration_ms)).where(ObsTrace.source_module == RUNTIME_MODULE)) or 0
    maximum = db.scalar(select(func.max(ObsTrace.duration_ms)).where(ObsTrace.source_module == RUNTIME_MODULE)) or 0
    last = db.scalar(query.order_by(ObsTrace.started_at.desc()).limit(1))
    return RuntimeSummary(runtime_traces=total, successful_requests=db.scalar(select(func.count(ObsTrace.id)).where(ObsTrace.source_module == RUNTIME_MODULE, ObsTrace.status == "SUCCESS")) or 0, degraded_requests=db.scalar(select(func.count(ObsTrace.id)).where(ObsTrace.source_module == RUNTIME_MODULE, ObsTrace.status == "DEGRADED")) or 0, error_requests=db.scalar(select(func.count(ObsTrace.id)).where(ObsTrace.source_module == RUNTIME_MODULE, ObsTrace.status == "ERROR")) or 0, average_latency_ms=round(float(avg), 2), max_latency_ms=int(maximum), slow_request_threshold_ms=slow_threshold_ms, runtime_logs=db.scalar(select(func.count(ObsLogEvent.id)).where(ObsLogEvent.source_module == RUNTIME_MODULE)) or 0, runtime_metric_samples=db.scalar(select(func.count(ObsMetricSample.id)).where(ObsMetricSample.component_code == RUNTIME_COMPONENT)) or 0, last_runtime_trace_at=last.started_at if last else None)


async def run_backend_health_probe(db: Session, redis_manager) -> RuntimeProbeResponse:
    started = _now()
    wall_start = perf_counter()
    trace_identifier = f"runtime-probe-{uuid4().hex}"
    db_ok = False
    redis_ok = False
    db_ms = 0
    redis_ms = 0
    try:
        db_start = perf_counter(); db.execute(text("SELECT 1")); db_ok = True; db_ms = int((perf_counter() - db_start) * 1000)
    except Exception:
        db_ms = int((perf_counter() - db_start) * 1000) if "db_start" in locals() else 0
    try:
        redis_start = perf_counter(); redis_ok = bool(await redis_manager.ping()); redis_ms = int((perf_counter() - redis_start) * 1000)
    except Exception:
        redis_ms = int((perf_counter() - redis_start) * 1000) if "redis_start" in locals() else 0
    duration_ms = max(0, int((perf_counter() - wall_start) * 1000))
    status = "SUCCESS" if db_ok and redis_ok else "DEGRADED"
    trace = observability_service.create_trace(db, trace_name="Runtime backend health probe", trace_type="API_REQUEST", status=status, source_module=RUNTIME_MODULE, root_entity_type="API_REQUEST", root_reference="POST /api/v1/runtime-observability/probes/backend-health", summary="Runtime probe checks PostgreSQL and Redis connectivity without changing business data.", started_at=started, duration_ms=duration_ms, trace_identifier=trace_identifier)
    root = observability_service.create_span(db, trace, span_id=f"span-{uuid4().hex}", span_name="Backend probe request", service_name="eos-backend", component_code=RUNTIME_COMPONENT, operation_type="HTTP_REQUEST", status="OK" if status == "SUCCESS" else "SLOW", started_at=started, duration_ms=duration_ms)
    db_span = observability_service.create_span(db, trace, span_id=f"span-{uuid4().hex}", span_name="PostgreSQL connectivity check", service_name="eos-backend", component_code="EOS-POSTGRES", operation_type="DATABASE_QUERY", status="OK" if db_ok else "ERROR", started_at=started, duration_ms=db_ms, parent_span_id=root.span_id, error_type=None if db_ok else "DATABASE_UNAVAILABLE", error_message=None if db_ok else "PostgreSQL connectivity check failed.", attributes={"status": "healthy" if db_ok else "unhealthy"})
    redis_span = observability_service.create_span(db, trace, span_id=f"span-{uuid4().hex}", span_name="Redis connectivity check", service_name="eos-backend", component_code="EOS-REDIS", operation_type="CACHE_OPERATION", status="OK" if redis_ok else "ERROR", started_at=started, duration_ms=redis_ms, parent_span_id=root.span_id, error_type=None if redis_ok else "REDIS_UNAVAILABLE", error_message=None if redis_ok else "Redis connectivity check failed.", attributes={"status": "healthy" if redis_ok else "unhealthy"})
    context = {"trace_id": trace.trace_id, "database": db_ok, "redis": redis_ok}
    observability_service.create_log_event(db, message="Runtime backend health probe started.", event_type="REQUEST_STARTED", level="INFO", logger_name="eos.runtime.probe", source_module=RUNTIME_MODULE, trace_id=trace.id, span_id=root.id, component_code=RUNTIME_COMPONENT, context=context, logged_at=started)
    observability_service.create_log_event(db, message=f"PostgreSQL connectivity check: {'healthy' if db_ok else 'unhealthy'}.", event_type="PROBE_DATABASE_RESULT", level="INFO" if db_ok else "ERROR", logger_name="eos.runtime.probe", source_module=RUNTIME_MODULE, trace_id=trace.id, span_id=db_span.id, component_code="EOS-POSTGRES", context={"latency_ms": db_ms, "healthy": db_ok})
    observability_service.create_log_event(db, message=f"Redis connectivity check: {'healthy' if redis_ok else 'unhealthy'}.", event_type="PROBE_REDIS_RESULT", level="INFO" if redis_ok else "ERROR", logger_name="eos.runtime.probe", source_module=RUNTIME_MODULE, trace_id=trace.id, span_id=redis_span.id, component_code="EOS-REDIS", context={"latency_ms": redis_ms, "healthy": redis_ok})
    observability_service.create_log_event(db, message=f"Runtime backend health probe completed with status {status}.", event_type="REQUEST_COMPLETED", level="INFO" if status == "SUCCESS" else "WARN", logger_name="eos.runtime.probe", source_module=RUNTIME_MODULE, trace_id=trace.id, span_id=root.id, component_code=RUNTIME_COMPONENT, context=context)
    observability_service.create_metric_sample(db, metric_name="runtime_probe_duration_ms", metric_value=duration_ms, metric_unit="ms", component_code=RUNTIME_COMPONENT, severity="LOW" if status == "SUCCESS" else "HIGH", trace_id=trace.id)
    observability_service.create_metric_sample(db, metric_name="db_probe_latency_ms", metric_value=db_ms, metric_unit="ms", component_code="EOS-POSTGRES", severity="LOW" if db_ok else "HIGH", trace_id=trace.id)
    observability_service.create_metric_sample(db, metric_name="redis_probe_latency_ms", metric_value=redis_ms, metric_unit="ms", component_code="EOS-REDIS", severity="LOW" if redis_ok else "HIGH", trace_id=trace.id)
    db.commit()
    return RuntimeProbeResponse(status=status, trace_id=trace.id, trace_identifier=trace.trace_id, database_status="healthy" if db_ok else "unhealthy", redis_status="healthy" if redis_ok else "unhealthy", duration_ms=duration_ms, db_latency_ms=db_ms, redis_latency_ms=redis_ms)
