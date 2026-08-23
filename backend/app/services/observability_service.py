"""Deterministic observability evidence and support diagnosis services."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.ams import AmsTicket
from app.models.batch import BatchRun, BatchRunEvent, BatchStepRun
from app.models.monitoring import MonAlert, MonTriageCase, MonTriageCaseAlert
from app.models.observability import ObsDiagnosticCase, ObsDiagnosticEvidence, ObsLogEvent, ObsMetricSample, ObsSpan, ObsTrace
from app.schemas.observability import DiagnosticCaseResponse, DiagnosticSummary, EvidenceResponse, LogEventResponse, MetricSampleResponse, SimulationResult, SpanResponse, SuiteResult, TraceResponse
from app.services import monitoring_service

SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
ACTIVE_DIAGNOSTIC_STATUSES = ("OPEN", "UNDER_REVIEW", "DIAGNOSED", "LINKED_TO_TICKET")


class ObservabilityError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_number(db: Session, field: object, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))  # type: ignore[union-attr]
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            sequence = 1
    return f"{prefix}{sequence:04d}"


def _trace_response(db: Session, trace: ObsTrace, include_children: bool = False) -> TraceResponse:
    spans = db.scalars(select(ObsSpan).where(ObsSpan.trace_id == trace.id).order_by(ObsSpan.started_at, ObsSpan.id)).all() if include_children else []
    logs = db.scalars(select(ObsLogEvent).where(ObsLogEvent.trace_id == trace.id).order_by(ObsLogEvent.logged_at, ObsLogEvent.id)).all() if include_children else []
    metrics = db.scalars(select(ObsMetricSample).where(ObsMetricSample.trace_id == trace.id).order_by(ObsMetricSample.recorded_at, ObsMetricSample.id)).all() if include_children else []
    return TraceResponse(
        id=trace.id, trace_id=trace.trace_id, trace_name=trace.trace_name, trace_type=trace.trace_type, status=trace.status,
        source_module=trace.source_module, root_entity_type=trace.root_entity_type, root_entity_id=trace.root_entity_id, root_reference=trace.root_reference,
        linked_alert_id=trace.linked_alert_id, linked_triage_case_id=trace.linked_triage_case_id, linked_ticket_id=trace.linked_ticket_id,
        started_at=trace.started_at, ended_at=trace.ended_at, duration_ms=trace.duration_ms, summary=trace.summary,
        spans=[SpanResponse.model_validate(item, from_attributes=True) for item in spans],
        logs=[LogEventResponse.model_validate(item, from_attributes=True) for item in logs],
        metrics=[MetricSampleResponse.model_validate(item, from_attributes=True) for item in metrics],
    )


def create_trace(db: Session, *, trace_name: str, trace_type: str, status: str, source_module: str, summary: str, linked_alert_id: UUID | None = None, linked_triage_case_id: UUID | None = None, linked_ticket_id: UUID | None = None, root_entity_type: str | None = None, root_entity_id: UUID | None = None, root_reference: str | None = None, started_at: datetime | None = None, duration_ms: int | None = None, trace_identifier: str | None = None) -> ObsTrace:
    started = started_at or _now()
    trace = ObsTrace(trace_id=trace_identifier or f"trace-{started:%Y%m%d%H%M%S}-{uuid4().hex[:10]}", trace_name=trace_name, trace_type=trace_type, status=status, source_module=source_module, root_entity_type=root_entity_type, root_entity_id=root_entity_id, root_reference=root_reference, linked_alert_id=linked_alert_id, linked_triage_case_id=linked_triage_case_id, linked_ticket_id=linked_ticket_id, started_at=started, ended_at=started + timedelta(milliseconds=duration_ms) if duration_ms is not None else None, duration_ms=duration_ms, summary=summary, created_at=_now(), updated_at=_now())
    db.add(trace)
    db.flush()
    return trace


def create_span(db: Session, trace: ObsTrace, *, span_id: str, span_name: str, service_name: str, component_code: str | None, operation_type: str, status: str, started_at: datetime, duration_ms: int, parent_span_id: str | None = None, error_type: str | None = None, error_message: str | None = None, attributes: dict | None = None) -> ObsSpan:
    span = ObsSpan(trace_id=trace.id, span_id=span_id, parent_span_id=parent_span_id, span_name=span_name, service_name=service_name, component_code=component_code, operation_type=operation_type, status=status, started_at=started_at, ended_at=started_at + timedelta(milliseconds=duration_ms), duration_ms=duration_ms, error_type=error_type, error_message=error_message, attributes=attributes, created_at=_now(), updated_at=_now())
    db.add(span)
    db.flush()
    return span


def create_log_event(db: Session, *, message: str, event_type: str, level: str, logger_name: str, source_module: str, trace_id: UUID | None = None, span_id: UUID | None = None, component_code: str | None = None, entity_type: str | None = None, entity_id: UUID | None = None, linked_alert_id: UUID | None = None, linked_ticket_id: UUID | None = None, context: dict | None = None, logged_at: datetime | None = None) -> ObsLogEvent:
    now = logged_at or _now()
    event = ObsLogEvent(log_number=_next_number(db, ObsLogEvent.log_number, f"LOG-{now:%Y%m%d}-"), trace_id=trace_id, span_id=span_id, level=level, logger_name=logger_name, message=message, event_type=event_type, source_module=source_module, component_code=component_code, entity_type=entity_type, entity_id=entity_id, linked_alert_id=linked_alert_id, linked_ticket_id=linked_ticket_id, context=context, logged_at=now, created_at=_now())
    db.add(event)
    db.flush()
    return event


def create_metric_sample(db: Session, *, metric_name: str, metric_value: float, metric_unit: str, component_code: str | None, severity: str | None, trace_id: UUID | None = None, linked_alert_id: UUID | None = None, attributes: dict | None = None, recorded_at: datetime | None = None) -> ObsMetricSample:
    now = recorded_at or _now()
    sample = ObsMetricSample(sample_number=_next_number(db, ObsMetricSample.sample_number, f"MET-{now:%Y%m%d}-"), metric_name=metric_name, metric_value=metric_value, metric_unit=metric_unit, component_code=component_code, severity=severity, trace_id=trace_id, linked_alert_id=linked_alert_id, recorded_at=now, attributes=attributes, created_at=_now())
    db.add(sample)
    db.flush()
    return sample


def _evidence(db: Session, diagnostic: ObsDiagnosticCase, evidence_type: str, source_table: str, source_id: UUID, title: str, details: str, weight: float) -> ObsDiagnosticEvidence:
    row = ObsDiagnosticEvidence(diagnostic_case_id=diagnostic.id, evidence_type=evidence_type, source_table=source_table, source_id=source_id, title=title, details=details, weight=weight, created_at=_now())
    db.add(row)
    return row


def _diagnostic_response(db: Session, row: ObsDiagnosticCase) -> DiagnosticCaseResponse:
    evidence = db.scalars(select(ObsDiagnosticEvidence).where(ObsDiagnosticEvidence.diagnostic_case_id == row.id).order_by(ObsDiagnosticEvidence.created_at, ObsDiagnosticEvidence.id)).all()
    trace = db.get(ObsTrace, row.primary_trace_id) if row.primary_trace_id else None
    return DiagnosticCaseResponse(
        id=row.id, diagnostic_number=row.diagnostic_number, title=row.title, description=row.description, status=row.status, severity=row.severity,
        source_type=row.source_type, source_id=row.source_id, linked_alert_id=row.linked_alert_id, linked_triage_case_id=row.linked_triage_case_id,
        linked_ticket_id=row.linked_ticket_id, primary_trace_id=row.primary_trace_id, primary_trace_identifier=trace.trace_id if trace else None,
        probable_cause=row.probable_cause, confidence_level=row.confidence_level, recommended_next_steps=row.recommended_next_steps,
        diagnosis_summary=row.diagnosis_summary, created_by=row.created_by, created_at=row.created_at, updated_at=row.updated_at, resolved_at=row.resolved_at,
        evidence=[EvidenceResponse.model_validate(item, from_attributes=True) for item in evidence],
    )


def _add_trace_evidence(db: Session, diagnostic: ObsDiagnosticCase, trace: ObsTrace) -> None:
    for span in db.scalars(select(ObsSpan).where(ObsSpan.trace_id == trace.id).order_by(ObsSpan.started_at)).all():
        _evidence(db, diagnostic, "SPAN", "obs_spans", span.id, span.span_name, f"{span.service_name} / {span.component_code or 'unknown'} returned {span.status} in {span.duration_ms} ms. {span.error_message or ''}".strip(), 3 if span.status in ("ERROR", "TIMEOUT") else 2)
    for log in db.scalars(select(ObsLogEvent).where(ObsLogEvent.trace_id == trace.id).order_by(ObsLogEvent.logged_at)).all():
        _evidence(db, diagnostic, "LOG", "obs_log_events", log.id, log.event_type, f"{log.level}: {log.message}", 3 if log.level in ("ERROR", "CRITICAL") else 1)
    for metric in db.scalars(select(ObsMetricSample).where(ObsMetricSample.trace_id == trace.id).order_by(ObsMetricSample.recorded_at)).all():
        _evidence(db, diagnostic, "METRIC", "obs_metric_samples", metric.id, metric.metric_name, f"{metric.metric_value} {metric.metric_unit} on {metric.component_code or 'unknown'}.", 2)


def _create_diagnostic(db: Session, *, title: str, description: str, severity: str, source_type: str, source_id: UUID | None, probable_cause: str, confidence_level: str, recommended_next_steps: str, diagnosis_summary: str, trace: ObsTrace | None = None, alert: MonAlert | None = None, triage: MonTriageCase | None = None, ticket: AmsTicket | None = None) -> ObsDiagnosticCase:
    now = _now()
    row = ObsDiagnosticCase(diagnostic_number=_next_number(db, ObsDiagnosticCase.diagnostic_number, f"DGN-{now:%Y%m%d}-"), title=title[:200], description=description[:1500], status="DIAGNOSED", severity=severity, source_type=source_type, source_id=source_id, linked_alert_id=alert.id if alert else None, linked_triage_case_id=triage.id if triage else None, linked_ticket_id=ticket.id if ticket else None, primary_trace_id=trace.id if trace else None, probable_cause=probable_cause[:1000], confidence_level=confidence_level, recommended_next_steps=recommended_next_steps[:1500], diagnosis_summary=diagnosis_summary[:2000], created_by="support-engineer", created_at=now, updated_at=now)
    db.add(row)
    db.flush()
    if alert:
        _evidence(db, row, "ALERT", "mon_alerts", alert.id, alert.alert_number, f"{alert.title}; observed {alert.observed_value} against threshold {alert.threshold_value}.", 2)
    if triage:
        _evidence(db, row, "TRIAGE_CASE", "mon_triage_cases", triage.id, triage.case_number, triage.description, 1)
    if ticket:
        _evidence(db, row, "TICKET", "ams_tickets", ticket.id, ticket.ticket_number, ticket.short_description, 1)
    if trace:
        _add_trace_evidence(db, row, trace)
    return row


def get_trace(db: Session, identifier: str) -> TraceResponse:
    trace = None
    try:
        trace = db.get(ObsTrace, UUID(identifier))
    except ValueError:
        pass
    if trace is None:
        trace = db.scalar(select(ObsTrace).where(ObsTrace.trace_id == identifier))
    if trace is None:
        raise ObservabilityError("Observability trace not found.", 404)
    return _trace_response(db, trace, True)


def correlate_alert_to_observability(db: Session, alert_id: UUID) -> list[TraceResponse]:
    return [_trace_response(db, row, True) for row in db.scalars(select(ObsTrace).where(ObsTrace.linked_alert_id == alert_id).order_by(ObsTrace.started_at.desc())).all()]


def correlate_triage_case_to_observability(db: Session, case_id: UUID) -> list[TraceResponse]:
    return [_trace_response(db, row, True) for row in db.scalars(select(ObsTrace).where(ObsTrace.linked_triage_case_id == case_id).order_by(ObsTrace.started_at.desc())).all()]


def correlate_ticket_to_observability(db: Session, ticket_id: UUID) -> list[TraceResponse]:
    return [_trace_response(db, row, True) for row in db.scalars(select(ObsTrace).where(ObsTrace.linked_ticket_id == ticket_id).order_by(ObsTrace.started_at.desc())).all()]


def list_traces(db: Session, status: str | None = None, trace_type: str | None = None, source_module: str | None = None, linked_ticket_id: UUID | None = None, linked_alert_id: UUID | None = None) -> list[TraceResponse]:
    statement = select(ObsTrace).order_by(ObsTrace.started_at.desc())
    if status: statement = statement.where(ObsTrace.status == status.upper())
    if trace_type: statement = statement.where(ObsTrace.trace_type == trace_type.upper())
    if source_module: statement = statement.where(ObsTrace.source_module == source_module.upper())
    if linked_ticket_id: statement = statement.where(ObsTrace.linked_ticket_id == linked_ticket_id)
    if linked_alert_id: statement = statement.where(ObsTrace.linked_alert_id == linked_alert_id)
    return [_trace_response(db, row) for row in db.scalars(statement).all()]


def list_logs(db: Session, level: str | None = None, event_type: str | None = None, trace_id: UUID | None = None, component_code: str | None = None, linked_ticket_id: UUID | None = None) -> list[LogEventResponse]:
    statement = select(ObsLogEvent).order_by(ObsLogEvent.logged_at.desc())
    if level: statement = statement.where(ObsLogEvent.level == level.upper())
    if event_type: statement = statement.where(ObsLogEvent.event_type == event_type.upper())
    if trace_id: statement = statement.where(ObsLogEvent.trace_id == trace_id)
    if component_code: statement = statement.where(ObsLogEvent.component_code == component_code)
    if linked_ticket_id: statement = statement.where(ObsLogEvent.linked_ticket_id == linked_ticket_id)
    return [LogEventResponse.model_validate(row, from_attributes=True) for row in db.scalars(statement.limit(200)).all()]


def list_metrics(db: Session, metric_name: str | None = None, component_code: str | None = None, severity: str | None = None, trace_id: UUID | None = None, linked_alert_id: UUID | None = None) -> list[MetricSampleResponse]:
    statement = select(ObsMetricSample).order_by(ObsMetricSample.recorded_at.desc())
    if metric_name: statement = statement.where(ObsMetricSample.metric_name == metric_name)
    if component_code: statement = statement.where(ObsMetricSample.component_code == component_code)
    if severity: statement = statement.where(ObsMetricSample.severity == severity.upper())
    if trace_id: statement = statement.where(ObsMetricSample.trace_id == trace_id)
    if linked_alert_id: statement = statement.where(ObsMetricSample.linked_alert_id == linked_alert_id)
    return [MetricSampleResponse.model_validate(row, from_attributes=True) for row in db.scalars(statement.limit(200)).all()]


def list_diagnostics(db: Session, status: str | None = None, severity: str | None = None, confidence_level: str | None = None, source_type: str | None = None, linked_ticket_id: UUID | None = None) -> list[DiagnosticCaseResponse]:
    active_first = case((ObsDiagnosticCase.status.in_(ACTIVE_DIAGNOSTIC_STATUSES), 0), else_=1)
    statement = select(ObsDiagnosticCase).order_by(active_first, ObsDiagnosticCase.created_at.desc())
    if status: statement = statement.where(ObsDiagnosticCase.status == status.upper())
    if severity: statement = statement.where(ObsDiagnosticCase.severity == severity.upper())
    if confidence_level: statement = statement.where(ObsDiagnosticCase.confidence_level == confidence_level.upper())
    if source_type: statement = statement.where(ObsDiagnosticCase.source_type == source_type.upper())
    if linked_ticket_id: statement = statement.where(ObsDiagnosticCase.linked_ticket_id == linked_ticket_id)
    return [_diagnostic_response(db, row) for row in db.scalars(statement).all()]


def get_diagnostic(db: Session, case_id: UUID) -> DiagnosticCaseResponse:
    row = db.get(ObsDiagnosticCase, case_id)
    if row is None: raise ObservabilityError("Diagnostic case not found.", 404)
    return _diagnostic_response(db, row)


def _alert_for_rule(db: Session, rule_code: str, observed: float, title: str, description: str) -> tuple[MonAlert, bool]:
    alert, created, repeated = monitoring_service.create_alert(db, rule_code, observed, title, description, signal_type="METRIC_THRESHOLD", dedupe_key=f"{rule_code}:observability")
    return alert, created


def _simulation_database(db: Session) -> tuple[ObsTrace, ObsDiagnosticCase, list[MonAlert]]:
    db_alert, _ = _alert_for_rule(db, "MON-DB-LATENCY", 2450, "Database response time is high", "Deterministic database degradation evidence.")
    api_alert, _ = _alert_for_rule(db, "MON-API-LATENCY", 3200, "API latency is above threshold", "API latency is downstream of simulated database degradation.")
    allocation_alert, _ = _alert_for_rule(db, "MON-INV-ALLOC", 3, "Allocation failures are elevated", "Inventory allocation failures accompany the database symptom.")
    start = _now() - timedelta(seconds=4)
    trace = create_trace(db, trace_name="Warehouse order allocation degraded by database latency", trace_type="WAREHOUSE_WORKFLOW", status="DEGRADED", source_module="WAREHOUSE_FULFILLMENT", summary="A slow database query is visible in the allocation request path.", linked_alert_id=db_alert.id, started_at=start, duration_ms=3200)
    root = create_span(db, trace, span_id="span-http", span_name="HTTP POST /api/v1/warehouse/orders/{id}/allocate", service_name="eos-backend-api", component_code="EOS-BACKEND-API", operation_type="HTTP_REQUEST", status="SLOW", started_at=start, duration_ms=3200)
    workflow = create_span(db, trace, span_id="span-workflow", span_name="WarehouseWorkflowService.allocate_order", service_name="warehouse-workflow", component_code="WF-ORDER-WORKFLOW", operation_type="WORKFLOW_STEP", status="ERROR", started_at=start + timedelta(milliseconds=30), duration_ms=3100, parent_span_id=root.span_id, error_type="ALLOCATION_DEGRADED", error_message="Allocation completed outside the expected response window.")
    lookup = create_span(db, trace, span_id="span-lookup", span_name="InventoryBalanceRepository.find_available_stock", service_name="warehouse-inventory", component_code="WF-INVENTORY-SERVICE", operation_type="SERVICE_METHOD", status="SLOW", started_at=start + timedelta(milliseconds=80), duration_ms=3000, parent_span_id=workflow.span_id)
    query = create_span(db, trace, span_id="span-db", span_name="PostgreSQL SELECT wf_inventory_balances", service_name="postgresql", component_code="EOS-POSTGRES", operation_type="DATABASE_QUERY", status="SLOW", started_at=start + timedelta(milliseconds=120), duration_ms=2450, parent_span_id=lookup.span_id, error_type="DB_QUERY_SLOW", error_message="Inventory balance query exceeded the response threshold.")
    create_log_event(db, message="Inventory balance query exceeded the response threshold.", event_type="DB_QUERY_SLOW", level="WARN", logger_name="eos.warehouse.inventory", source_module="WAREHOUSE_FULFILLMENT", trace_id=trace.id, span_id=query.id, component_code="EOS-POSTGRES", linked_alert_id=db_alert.id, context={"duration_ms": 2450})
    create_log_event(db, message="Order allocation degraded while waiting for inventory data.", event_type="WORKFLOW_STEP_FAILED", level="ERROR", logger_name="eos.warehouse.workflow", source_module="WAREHOUSE_FULFILLMENT", trace_id=trace.id, span_id=workflow.id, component_code="WF-ORDER-WORKFLOW", linked_alert_id=allocation_alert.id, context={"allocation_failure_count": 3})
    create_metric_sample(db, metric_name="db_latency_ms", metric_value=2450, metric_unit="ms", component_code="EOS-POSTGRES", severity="HIGH", trace_id=trace.id, linked_alert_id=db_alert.id)
    create_metric_sample(db, metric_name="api_latency_ms", metric_value=3200, metric_unit="ms", component_code="EOS-BACKEND-API", severity="HIGH", trace_id=trace.id, linked_alert_id=api_alert.id)
    create_metric_sample(db, metric_name="allocation_failure_count", metric_value=3, metric_unit="count", component_code="WF-INVENTORY-SERVICE", severity="HIGH", trace_id=trace.id, linked_alert_id=allocation_alert.id)
    diagnostic = _create_diagnostic(db, title="Database degradation affecting allocation", description="Correlated trace, span, log, and metric evidence supports a database-latency diagnosis.", severity="HIGH", source_type="SIMULATION", source_id=trace.id, probable_cause="Database latency affecting inventory allocation queries", confidence_level="HIGH", recommended_next_steps="Review PostgreSQL response time\nCheck inventory balance query performance\nCheck concurrent allocation load", diagnosis_summary="The allocation request is slow because the inventory balance query and database span are both degraded.", trace=trace, alert=db_alert)
    return trace, diagnostic, [db_alert, api_alert, allocation_alert]


def _simulation_redis(db: Session) -> tuple[ObsTrace, ObsDiagnosticCase, list[MonAlert]]:
    redis_alert, _ = _alert_for_rule(db, "MON-REDIS-FLAP", 11, "Redis connection failures are elevated", "Deterministic Redis cache failure evidence.")
    api_alert, _ = _alert_for_rule(db, "MON-API-ERROR", 5, "API error rate is elevated", "API errors accompany simulated cache instability.")
    start = _now() - timedelta(seconds=2)
    trace = create_trace(db, trace_name="API response degraded after Redis cache failure", trace_type="API_REQUEST", status="DEGRADED", source_module="MONITORING", summary="Cache lookup fails, a fallback path is used, and the API response is degraded.", linked_alert_id=redis_alert.id, started_at=start, duration_ms=920)
    root = create_span(db, trace, span_id="span-http", span_name="HTTP GET /api/v1/warehouse/orders", service_name="eos-backend-api", component_code="EOS-BACKEND-API", operation_type="HTTP_REQUEST", status="SLOW", started_at=start, duration_ms=920)
    cache = create_span(db, trace, span_id="span-cache", span_name="OrderSummaryCache.get", service_name="redis-client", component_code="EOS-REDIS", operation_type="CACHE_OPERATION", status="ERROR", started_at=start + timedelta(milliseconds=20), duration_ms=410, parent_span_id=root.span_id, error_type="CACHE_CONNECTION_FAILURE", error_message="Redis connection reset during cache lookup.")
    fallback = create_span(db, trace, span_id="span-fallback", span_name="OrderRepository.fallback_query", service_name="eos-backend-api", component_code="EOS-BACKEND-API", operation_type="DATABASE_QUERY", status="OK", started_at=start + timedelta(milliseconds=450), duration_ms=430, parent_span_id=root.span_id)
    create_log_event(db, message="Redis connection reset during cache lookup; fallback path used.", event_type="WORKFLOW_CACHE_FAILURE", level="ERROR", logger_name="eos.platform.cache", source_module="MONITORING", trace_id=trace.id, span_id=cache.id, component_code="EOS-REDIS", linked_alert_id=redis_alert.id)
    create_log_event(db, message="API completed using degraded fallback path.", event_type="REQUEST_COMPLETED", level="WARN", logger_name="eos.platform.api", source_module="MONITORING", trace_id=trace.id, span_id=fallback.id, component_code="EOS-BACKEND-API", linked_alert_id=api_alert.id)
    create_metric_sample(db, metric_name="redis_connection_failures", metric_value=11, metric_unit="count", component_code="EOS-REDIS", severity="HIGH", trace_id=trace.id, linked_alert_id=redis_alert.id)
    create_metric_sample(db, metric_name="api_error_rate", metric_value=5, metric_unit="percent", component_code="EOS-BACKEND-API", severity="MEDIUM", trace_id=trace.id, linked_alert_id=api_alert.id)
    diagnostic = _create_diagnostic(db, title="Redis cache instability degraded API response", description="Trace evidence connects a Redis failure to a fallback API path and elevated API errors.", severity="HIGH", source_type="SIMULATION", source_id=trace.id, probable_cause="Redis cache instability causing degraded API response path", confidence_level="MEDIUM", recommended_next_steps="Review Redis connection resets\nCheck cache client retry behavior\nConfirm fallback API latency", diagnosis_summary="The cache span and correlated API log support a Redis-related degraded response, but the evidence does not prove the broader infrastructure cause.", trace=trace, alert=redis_alert)
    return trace, diagnostic, [redis_alert, api_alert]


def _simulation_allocation(db: Session) -> tuple[ObsTrace, ObsDiagnosticCase, list[MonAlert]]:
    alert, _ = _alert_for_rule(db, "MON-INV-ALLOC", 9, "Allocation failures are elevated", "Deterministic insufficient-stock evidence.")
    start = _now() - timedelta(seconds=1)
    trace = create_trace(db, trace_name="Order allocation blocked by insufficient inventory", trace_type="WAREHOUSE_WORKFLOW", status="ERROR", source_module="WAREHOUSE_FULFILLMENT", summary="The inventory business rule correctly blocks allocation when available quantity is insufficient.", linked_alert_id=alert.id, started_at=start, duration_ms=180)
    root = create_span(db, trace, span_id="span-http", span_name="HTTP POST /api/v1/warehouse/orders/{id}/allocate", service_name="eos-backend-api", component_code="EOS-BACKEND-API", operation_type="HTTP_REQUEST", status="ERROR", started_at=start, duration_ms=180)
    validation = create_span(db, trace, span_id="span-validation", span_name="InventoryAvailability.validate", service_name="warehouse-inventory", component_code="WF-INVENTORY-SERVICE", operation_type="VALIDATION", status="ERROR", started_at=start + timedelta(milliseconds=20), duration_ms=80, parent_span_id=root.span_id, error_type="INSUFFICIENT_STOCK", error_message="Available inventory is below requested quantity.")
    create_log_event(db, message="Allocation rejected by inventory availability business rule.", event_type="BUSINESS_RULE_BLOCKED", level="INFO", logger_name="eos.warehouse.inventory", source_module="WAREHOUSE_FULFILLMENT", trace_id=trace.id, span_id=validation.id, component_code="WF-INVENTORY-SERVICE", linked_alert_id=alert.id, context={"available_quantity": 2, "requested_quantity": 999})
    create_metric_sample(db, metric_name="allocation_failure_count", metric_value=9, metric_unit="count", component_code="WF-INVENTORY-SERVICE", severity="HIGH", trace_id=trace.id, linked_alert_id=alert.id)
    diagnostic = _create_diagnostic(db, title="Allocation blocked by insufficient stock", description="Business-rule evidence distinguishes a valid inventory rejection from a technical application outage.", severity="HIGH", source_type="SIMULATION", source_id=trace.id, probable_cause="Inventory availability below requested quantity; system correctly blocked allocation.", confidence_level="HIGH", recommended_next_steps="Review inventory balance and replenishment position\nConfirm requested quantity with the order manager\nNo application rollback is required", diagnosis_summary="The validation span and business rule log show a deterministic insufficient-stock rejection rather than a technical system degradation.", trace=trace, alert=alert)
    return trace, diagnostic, [alert]


def _simulation_shipment(db: Session) -> tuple[ObsTrace, ObsDiagnosticCase, list[MonAlert]]:
    alert, _ = _alert_for_rule(db, "MON-SHIPMENT-EXC", 6, "Shipment exceptions are elevated", "Deterministic carrier label failure evidence.")
    start = _now() - timedelta(seconds=1)
    trace = create_trace(db, trace_name="Ship order request failed during carrier label generation", trace_type="WAREHOUSE_WORKFLOW", status="ERROR", source_module="WAREHOUSE_FULFILLMENT", summary="The shipment workflow fails at the simulated external carrier label step.", linked_alert_id=alert.id, started_at=start, duration_ms=700)
    root = create_span(db, trace, span_id="span-ship", span_name="ShipOrderWorkflow.ship_order", service_name="warehouse-shipment", component_code="WF-SHIPMENT-SERVICE", operation_type="WORKFLOW_STEP", status="ERROR", started_at=start, duration_ms=700)
    service = create_span(db, trace, span_id="span-service", span_name="ShipmentService.create_shipment", service_name="warehouse-shipment", component_code="WF-SHIPMENT-SERVICE", operation_type="SERVICE_METHOD", status="ERROR", started_at=start + timedelta(milliseconds=20), duration_ms=680, parent_span_id=root.span_id)
    carrier = create_span(db, trace, span_id="span-carrier", span_name="CarrierLabelClient.generate_label", service_name="carrier-label-client", component_code="WF-SHIPMENT-SERVICE", operation_type="EXTERNAL_CALL", status="TIMEOUT", started_at=start + timedelta(milliseconds=50), duration_ms=650, parent_span_id=service.span_id, error_type="CARRIER_LABEL_TIMEOUT", error_message="Carrier label generation timed out.")
    create_log_event(db, message="Carrier label generation timed out.", event_type="EXTERNAL_CALL_FAILED", level="ERROR", logger_name="eos.warehouse.shipment", source_module="WAREHOUSE_FULFILLMENT", trace_id=trace.id, span_id=carrier.id, component_code="WF-SHIPMENT-SERVICE", linked_alert_id=alert.id)
    create_log_event(db, message="Shipment workflow stopped after carrier label failure.", event_type="WORKFLOW_STEP_FAILED", level="ERROR", logger_name="eos.warehouse.shipment", source_module="WAREHOUSE_FULFILLMENT", trace_id=trace.id, span_id=root.id, component_code="WF-SHIPMENT-SERVICE", linked_alert_id=alert.id)
    create_metric_sample(db, metric_name="shipment_exception_count", metric_value=6, metric_unit="count", component_code="WF-SHIPMENT-SERVICE", severity="HIGH", trace_id=trace.id, linked_alert_id=alert.id)
    create_metric_sample(db, metric_name="api_latency_ms", metric_value=900, metric_unit="ms", component_code="EOS-BACKEND-API", severity="MEDIUM", trace_id=trace.id)
    diagnostic = _create_diagnostic(db, title="Shipment integration failure during label generation", description="The shipment trace ends at a simulated carrier label call and contains matching error logs.", severity="HIGH", source_type="SIMULATION", source_id=trace.id, probable_cause="Carrier label generation integration failure", confidence_level="MEDIUM", recommended_next_steps="Review carrier label endpoint availability\nCheck timeout and retry configuration\nConfirm shipment status before retrying", diagnosis_summary="The external-call span and correlated logs support a carrier label failure, while external system health remains unverified.", trace=trace, alert=alert)
    return trace, diagnostic, [alert]


def _result(db: Session, code: str, trace: ObsTrace, diagnostic: ObsDiagnosticCase, alerts: list[MonAlert], ticket_id: UUID | None = None) -> SimulationResult:
    return SimulationResult(simulation_code=code, trace_id=trace.id, trace_identifier=trace.trace_id, diagnostic_case_id=diagnostic.id, diagnostic_number=diagnostic.diagnostic_number, alert_ids=[item.id for item in alerts], ticket_id=ticket_id, tickets_created_or_linked=1 if ticket_id else 0, summary=f"{diagnostic.probable_cause} Confidence: {diagnostic.confidence_level}. Evidence is deterministic and application-level.")


def run_simulation(db: Session, code: str, create_ticket: bool = False) -> SimulationResult:
    builders = {"database-degradation": _simulation_database, "redis-cache-failure": _simulation_redis, "allocation-failure": _simulation_allocation, "shipment-integration-failure": _simulation_shipment}
    if code not in builders: raise ObservabilityError("Unknown observability simulation.", 404)
    trace, diagnostic, alerts = builders[code](db)
    ticket_id = None
    if create_ticket:
        from app.services.ams_ticket_service import create_ticket_from_diagnostic
        ticket = create_ticket_from_diagnostic(db, diagnostic.id)
        ticket_id = ticket.id
    db.commit()
    return _result(db, code, trace, diagnostic, alerts, ticket_id)


def run_suite(db: Session, create_ticket: bool = False) -> SuiteResult:
    results = []
    for code in ("database-degradation", "redis-cache-failure", "allocation-failure", "shipment-integration-failure"):
        try:
            results.append(run_simulation(db, code, create_ticket))
        except ObservabilityError:
            db.rollback()
    severities = []
    for result in results:
        diagnostic = db.get(ObsDiagnosticCase, result.diagnostic_case_id) if result.diagnostic_case_id else None
        if diagnostic: severities.append(diagnostic.severity)
    return SuiteResult(simulation_code="observability-demo-suite", traces_created=len(results), diagnostic_cases_created=len(results), alerts_created_or_reused=sum(len(item.alert_ids) for item in results), tickets_created_or_linked=sum(item.tickets_created_or_linked for item in results), highest_severity=min(severities, key=lambda item: SEVERITY_RANK[item], default=None), summary="Ran deterministic database, Redis, allocation, and shipment observability scenarios with correlated evidence.", results=results)


def diagnosis_from_alert(db: Session, alert_id: UUID) -> DiagnosticCaseResponse:
    alert = db.get(MonAlert, alert_id)
    if alert is None: raise ObservabilityError("Monitoring alert not found.", 404)
    existing = db.scalar(select(ObsDiagnosticCase).where(ObsDiagnosticCase.linked_alert_id == alert.id, ObsDiagnosticCase.status.in_(ACTIVE_DIAGNOSTIC_STATUSES)).order_by(ObsDiagnosticCase.created_at.desc()))
    if existing: return _diagnostic_response(db, existing)
    trace = db.scalar(select(ObsTrace).where(ObsTrace.linked_alert_id == alert.id).order_by(ObsTrace.started_at.desc()))
    if trace:
        row = _create_diagnostic(db, title=f"Diagnosis for {alert.alert_number}", description="Diagnosis assembled from correlated monitoring and observability evidence.", severity=alert.severity, source_type="ALERT", source_id=alert.id, probable_cause="Correlated evidence supports manual investigation; no single root cause is confirmed." if trace.status not in ("ERROR", "TIMEOUT") else "Correlated trace evidence identifies an error path requiring manual validation.", confidence_level="MEDIUM", recommended_next_steps="Review the primary trace and error spans\nValidate related logs and metric samples\nConfirm impact with the owning support team", diagnosis_summary="Observability evidence is available for this alert, but diagnosis remains deterministic and support-engineer validated.", trace=trace, alert=alert)
    else:
        row = _create_diagnostic(db, title=f"Diagnosis for {alert.alert_number}", description="No correlated trace, log, or metric evidence was found for this alert.", severity=alert.severity, source_type="ALERT", source_id=alert.id, probable_cause="Insufficient observability evidence to determine a probable cause.", confidence_level="LOW", recommended_next_steps="Collect a trace for an affected request\nReview structured logs around the alert time\nCompare component metrics", diagnosis_summary="Only the monitoring symptom is available; no root cause is inferred.", alert=alert)
    db.commit()
    return _diagnostic_response(db, row)


def diagnosis_from_triage(db: Session, case_id: UUID) -> DiagnosticCaseResponse:
    triage = db.get(MonTriageCase, case_id)
    if triage is None: raise ObservabilityError("Triage case not found.", 404)
    existing = db.scalar(select(ObsDiagnosticCase).where(ObsDiagnosticCase.linked_triage_case_id == triage.id, ObsDiagnosticCase.status.in_(ACTIVE_DIAGNOSTIC_STATUSES)).order_by(ObsDiagnosticCase.created_at.desc()))
    if existing: return _diagnostic_response(db, existing)
    alert_ids = [link.alert_id for link in db.scalars(select(MonTriageCaseAlert).where(MonTriageCaseAlert.triage_case_id == triage.id)).all()]
    trace = db.scalar(select(ObsTrace).where(ObsTrace.linked_alert_id.in_(alert_ids)).order_by(ObsTrace.started_at.desc())) if alert_ids else None
    alert = db.get(MonAlert, alert_ids[0]) if alert_ids else None
    evidence_count = len(_trace_evidence_ids(db, trace.id)) if trace else 0
    confidence = "HIGH" if evidence_count >= 4 else "MEDIUM" if evidence_count >= 2 else "LOW"
    row = _create_diagnostic(db, title=f"Diagnosis for {triage.case_number}", description=triage.description, severity=triage.severity, source_type="TRIAGE_CASE", source_id=triage.id, probable_cause="Correlated observability evidence supports the manually grouped alert symptoms." if trace else "No correlated observability trace was found for the manually grouped alerts.", confidence_level=confidence, recommended_next_steps="Review the correlated trace path\nValidate component logs and metrics\nConfirm the suspected impact with the support owner", diagnosis_summary="The diagnostic case extends manual triage with deterministic evidence; it does not infer an autonomous root cause.", trace=trace, alert=alert, triage=triage)
    db.commit()
    return _diagnostic_response(db, row)


def diagnosis_from_ticket(db: Session, ticket_id: UUID) -> DiagnosticCaseResponse:
    ticket = db.get(AmsTicket, ticket_id)
    if ticket is None: raise ObservabilityError("AMS ticket not found.", 404)
    existing = db.scalar(select(ObsDiagnosticCase).where(ObsDiagnosticCase.linked_ticket_id == ticket.id, ObsDiagnosticCase.status.in_(ACTIVE_DIAGNOSTIC_STATUSES)).order_by(ObsDiagnosticCase.created_at.desc()))
    if existing: return _diagnostic_response(db, existing)
    trace = db.scalar(select(ObsTrace).where(ObsTrace.linked_ticket_id == ticket.id).order_by(ObsTrace.started_at.desc()))
    alert = None
    if ticket.source == "MONITORING" and ticket.affected_entity_type == "COMPONENT" and ticket.affected_entity_id:
        alert = db.scalar(select(MonAlert).where(MonAlert.linked_ticket_id == ticket.id).order_by(MonAlert.last_seen_at.desc()))
    row = _create_diagnostic(db, title=f"Diagnosis for {ticket.ticket_number}", description=ticket.description, severity=ticket.severity, source_type="AMS_TICKET", source_id=ticket.id, probable_cause="Observability evidence must be correlated with this support ticket before a cause is confirmed." if not trace else "Correlated observability evidence identifies a probable failure path for this ticket.", confidence_level="MEDIUM" if trace else "UNKNOWN", recommended_next_steps="Review the linked trace and evidence records\nValidate the affected component\nRecord support-engineer findings", diagnosis_summary="Ticket-linked diagnosis remains evidence-backed and non-autonomous.", trace=trace, alert=alert, ticket=ticket)
    db.commit()
    return _diagnostic_response(db, row)


def _trace_evidence_ids(db: Session, trace_id: UUID) -> list[UUID]:
    return [*db.scalars(select(ObsSpan.id).where(ObsSpan.trace_id == trace_id)).all(), *db.scalars(select(ObsLogEvent.id).where(ObsLogEvent.trace_id == trace_id)).all(), *db.scalars(select(ObsMetricSample.id).where(ObsMetricSample.trace_id == trace_id)).all()]


def link_diagnostic_ticket(db: Session, case_id: UUID, ticket_id: UUID | None) -> DiagnosticCaseResponse:
    row = db.get(ObsDiagnosticCase, case_id)
    if row is None: raise ObservabilityError("Diagnostic case not found.", 404)
    if ticket_id:
        ticket = db.get(AmsTicket, ticket_id)
        if ticket is None: raise ObservabilityError("AMS ticket not found.", 404)
    else:
        from app.services.ams_ticket_service import create_ticket_from_diagnostic
        ticket = create_ticket_from_diagnostic(db, case_id, commit=False)
    row.linked_ticket_id, row.status, row.updated_at = ticket.id, "LINKED_TO_TICKET", _now()
    db.commit()
    return _diagnostic_response(db, row)


def resolve_diagnostic(db: Session, case_id: UUID, notes: str) -> DiagnosticCaseResponse:
    row = db.get(ObsDiagnosticCase, case_id)
    if row is None: raise ObservabilityError("Diagnostic case not found.", 404)
    if row.status not in ACTIVE_DIAGNOSTIC_STATUSES: raise ObservabilityError(f"Diagnostic case cannot transition from {row.status} to RESOLVED.")
    row.status, row.diagnosis_summary, row.resolved_at, row.updated_at = "RESOLVED", notes.strip(), _now(), _now()
    db.commit()
    return _diagnostic_response(db, row)


def get_summary(db: Session) -> DiagnosticSummary:
    traces = db.scalar(select(func.count(ObsTrace.id))) or 0
    errors = db.scalar(select(func.count(ObsTrace.id)).where(ObsTrace.status == "ERROR")) or 0
    slow = db.scalar(select(func.count(ObsSpan.id)).where(ObsSpan.status.in_(("SLOW", "TIMEOUT")))) or 0
    error_logs = db.scalar(select(func.count(ObsLogEvent.id)).where(ObsLogEvent.level.in_(("ERROR", "CRITICAL")))) or 0
    metrics = db.scalar(select(func.count(ObsMetricSample.id))) or 0
    open_cases = db.scalar(select(func.count(ObsDiagnosticCase.id)).where(ObsDiagnosticCase.status.in_(ACTIVE_DIAGNOSTIC_STATUSES))) or 0
    high_confidence = db.scalar(select(func.count(ObsDiagnosticCase.id)).where(ObsDiagnosticCase.confidence_level == "HIGH")) or 0
    linked = db.scalar(select(func.count(ObsDiagnosticCase.id)).where(ObsDiagnosticCase.linked_ticket_id.is_not(None))) or 0
    return DiagnosticSummary(traces=traces, error_traces=errors, slow_spans=slow, error_logs=error_logs, metric_samples=metrics, open_diagnostic_cases=open_cases, high_confidence_diagnoses=high_confidence, linked_tickets=linked)


def create_diagnostic_from_batch_run(db: Session, run_id: UUID) -> DiagnosticCaseResponse:
    run = db.get(BatchRun, run_id)
    if run is None:
        raise ObservabilityError("Batch run not found.", 404)
    if run.linked_diagnostic_case_id:
        existing = db.get(ObsDiagnosticCase, run.linked_diagnostic_case_id)
        if existing is not None:
            return _diagnostic_response(db, existing)
    if run.status == "SUCCESS":
        raise ObservabilityError("Successful batch runs do not require diagnostic cases.", 409)
    failed_steps = db.scalars(select(BatchStepRun).where(BatchStepRun.batch_run_id == run.id, BatchStepRun.status.in_(("FAILED", "TIMEOUT", "PARTIAL_SUCCESS"))).order_by(BatchStepRun.step_order)).all()
    alert = db.get(MonAlert, run.linked_alert_id) if run.linked_alert_id else None
    ticket = db.get(AmsTicket, run.linked_ticket_id) if run.linked_ticket_id else None
    confidence = "HIGH" if run.failure_type and failed_steps else "MEDIUM" if run.failure_type else "LOW"
    probable = {
        "DATA_VALIDATION_ERROR": "Batch validation or reconciliation data was invalid.",
        "BUSINESS_RULE_FAILURE": "Batch processing was blocked by an order-release business rule.",
        "EXTERNAL_SYSTEM_ERROR": "The batch external dependency failed or timed out.",
        "PARTIAL_RECORD_FAILURE": "A subset of batch records failed during notification processing.",
    }.get(run.failure_type or "", "Batch failure requires additional evidence.")
    row = _create_diagnostic(db, title=f"Diagnosis for {run.run_number}", description=run.summary, severity="HIGH" if run.status in ("FAILED", "TIMEOUT") else "MEDIUM", source_type="SIMULATION", source_id=run.id, probable_cause=probable, confidence_level=confidence, recommended_next_steps="Review the failed batch step and its technical context\nValidate affected records and business impact\nConfirm whether a retry is safe", diagnosis_summary=f"The batch run ended with {run.status}; the failed step and persisted failure type provide deterministic support evidence.", alert=alert, ticket=ticket)
    _evidence(db, row, "BUSINESS_ENTITY", "batch_runs", run.id, run.run_number, f"{run.job.name}: {run.summary}", 2)
    for step in failed_steps:
        _evidence(db, row, "SPAN", "batch_step_runs", step.id, step.step_code, f"{step.status}: {step.failure_message or 'step failed'}", 3)
    for event in db.scalars(select(BatchRunEvent).where(BatchRunEvent.batch_run_id == run.id, BatchRunEvent.event_type.in_(("BATCH_STEP_FAILED", "BATCH_RUN_FAILED", "BATCH_RUN_PARTIAL_SUCCESS"))).order_by(BatchRunEvent.created_at)).all():
        _evidence(db, row, "LOG", "batch_run_events", event.id, event.event_type, event.message, 2)
    run.linked_diagnostic_case_id, run.updated_at = row.id, _now()
    db.add(BatchRunEvent(batch_run_id=run.id, event_type="BATCH_DIAGNOSTIC_CREATED", message=f"Diagnostic case {row.diagnostic_number} created.", event_payload={"diagnostic_case_id": str(row.id)}, created_by="system", created_at=_now()))
    db.commit()
    return _diagnostic_response(db, row)
