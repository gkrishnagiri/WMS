"""Synchronous deterministic batch execution and support artifact services."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.ams import AmsTicket
from app.models.batch import BatchJob, BatchJobStep, BatchRun, BatchRunEvent, BatchStepRun
from app.models.operations import OpsException
from app.models.observability import ObsDiagnosticCase
from app.schemas.batch import BatchJobResponse, BatchRunBrief, BatchRunEventResponse, BatchRunResponse, BatchSimulationResult, BatchStepResponse, BatchStepRunResponse, BatchSummary, BatchSuiteResult
from app.services.operations_exception_service import create_or_refresh_exception

ACTIVE_TICKET_STATUSES = ("NEW", "ACKNOWLEDGED", "IN_PROGRESS")
SEVERITY_BY_FAILURE = {"TIMEOUT": "HIGH", "EXTERNAL_SYSTEM_ERROR": "HIGH", "DATABASE_LATENCY": "HIGH", "DATA_VALIDATION_ERROR": "HIGH", "BUSINESS_RULE_FAILURE": "MEDIUM", "PARTIAL_RECORD_FAILURE": "MEDIUM"}


class BatchError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_number(db: Session) -> str:
    prefix = f"BATCH-RUN-{_now():%Y%m%d}-"
    current = db.scalar(select(func.max(BatchRun.run_number)).where(BatchRun.run_number.like(f"{prefix}%")))
    sequence = 1
    if current:
        try: sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError): sequence = 1
    return f"{prefix}{sequence:04d}"


def _event(db: Session, run: BatchRun, event_type: str, message: str, from_status: str | None = None, to_status: str | None = None, payload: dict | None = None) -> None:
    db.add(BatchRunEvent(batch_run_id=run.id, event_type=event_type, from_status=from_status, to_status=to_status, message=message, event_payload=payload, created_by="system", created_at=_now()))


def _step_response(row: BatchStepRun) -> BatchStepRunResponse:
    return BatchStepRunResponse.model_validate(row, from_attributes=True)


def _run_response(db: Session, run: BatchRun, include_children: bool = True) -> BatchRunResponse:
    job = db.get(BatchJob, run.job_id)
    steps = db.scalars(select(BatchStepRun).where(BatchStepRun.batch_run_id == run.id).order_by(BatchStepRun.step_order)).all() if include_children else []
    events = db.scalars(select(BatchRunEvent).where(BatchRunEvent.batch_run_id == run.id).order_by(BatchRunEvent.created_at, BatchRunEvent.id)).all() if include_children else []
    exception = db.get(OpsException, run.linked_exception_id) if run.linked_exception_id else None
    ticket = db.get(AmsTicket, run.linked_ticket_id) if run.linked_ticket_id else None
    diagnostic = db.get(ObsDiagnosticCase, run.linked_diagnostic_case_id) if run.linked_diagnostic_case_id else None
    return BatchRunResponse(
        id=run.id, run_number=run.run_number, job_id=run.job_id, job_code=job.job_code if job else "UNKNOWN", job_name=job.name if job else "Unknown",
        status=run.status, trigger_type=run.trigger_type, scenario_code=run.scenario_code, started_at=run.started_at, completed_at=run.completed_at, duration_ms=run.duration_ms,
        records_processed=run.records_processed, records_succeeded=run.records_succeeded, records_failed=run.records_failed, failure_type=run.failure_type, failure_message=run.failure_message, summary=run.summary,
        linked_exception_id=run.linked_exception_id, linked_exception_number=exception.exception_number if exception else None, linked_ticket_id=run.linked_ticket_id, linked_ticket_number=ticket.ticket_number if ticket else None,
        linked_alert_id=run.linked_alert_id, linked_diagnostic_case_id=run.linked_diagnostic_case_id, linked_diagnostic_number=diagnostic.diagnostic_number if diagnostic else None,
        created_by=run.created_by, created_at=run.created_at, updated_at=run.updated_at, steps=[_step_response(row) for row in steps], events=[BatchRunEventResponse.model_validate(row, from_attributes=True) for row in events],
    )


def list_jobs(db: Session, enabled: bool | None = None, job_type: str | None = None) -> list[BatchJobResponse]:
    statement = select(BatchJob).order_by(BatchJob.job_code)
    if enabled is not None: statement = statement.where(BatchJob.enabled == enabled)
    if job_type: statement = statement.where(BatchJob.job_type == job_type.upper())
    return [_job_response(db, row, True) for row in db.scalars(statement).all()]


def _job_response(db: Session, job: BatchJob, include_details: bool = False) -> BatchJobResponse:
    steps = db.scalars(select(BatchJobStep).where(BatchJobStep.job_id == job.id).order_by(BatchJobStep.step_order)).all() if include_details else []
    runs = db.scalars(select(BatchRun).where(BatchRun.job_id == job.id).order_by(BatchRun.created_at.desc()).limit(5)).all()
    return BatchJobResponse(
        id=job.id, job_code=job.job_code, name=job.name, description=job.description, job_type=job.job_type, module=job.module, business_service=job.business_service,
        application_name=job.application_name, enabled=job.enabled, default_severity=job.default_severity, sla_minutes=job.sla_minutes, step_count=db.scalar(select(func.count(BatchJobStep.id)).where(BatchJobStep.job_id == job.id)) or 0,
        steps=[BatchStepResponse.model_validate(row, from_attributes=True) for row in steps], recent_runs=[BatchRunBrief.model_validate(row, from_attributes=True) for row in runs], created_at=job.created_at, updated_at=job.updated_at,
    )


def get_job(db: Session, identifier: str) -> BatchJobResponse:
    row = None
    try: row = db.get(BatchJob, UUID(identifier))
    except ValueError: pass
    if row is None: row = db.scalar(select(BatchJob).where(BatchJob.job_code == identifier))
    if row is None: raise BatchError("Batch job not found.", 404)
    return _job_response(db, row, True)


def list_runs(db: Session, job_code: str | None = None, status: str | None = None, failure_type: str | None = None, linked_ticket: bool | None = None) -> list[BatchRunResponse]:
    statement = select(BatchRun).join(BatchJob).order_by(BatchRun.created_at.desc()).limit(100)
    if job_code: statement = statement.where(BatchJob.job_code == job_code)
    if status: statement = statement.where(BatchRun.status == status.upper())
    if failure_type: statement = statement.where(BatchRun.failure_type == failure_type.upper())
    if linked_ticket is True: statement = statement.where(BatchRun.linked_ticket_id.is_not(None))
    if linked_ticket is False: statement = statement.where(BatchRun.linked_ticket_id.is_(None))
    return [_run_response(db, row) for row in db.scalars(statement).all()]


def get_run(db: Session, identifier: str) -> BatchRunResponse:
    row = None
    try: row = db.get(BatchRun, UUID(identifier))
    except ValueError: pass
    if row is None: row = db.scalar(select(BatchRun).where(BatchRun.run_number == identifier))
    if row is None: raise BatchError("Batch run not found.", 404)
    return _run_response(db, row)


def list_events(db: Session, identifier: str) -> list[BatchRunEventResponse]:
    run = None
    try: run = db.get(BatchRun, UUID(identifier))
    except ValueError: pass
    if run is None: run = db.scalar(select(BatchRun).where(BatchRun.run_number == identifier))
    if run is None: raise BatchError("Batch run not found.", 404)
    return [BatchRunEventResponse.model_validate(row, from_attributes=True) for row in db.scalars(select(BatchRunEvent).where(BatchRunEvent.batch_run_id == run.id).order_by(BatchRunEvent.created_at, BatchRunEvent.id)).all()]


SCENARIOS = {
    "inventory-reconciliation-success": {"job": "BATCH-INV-RECON", "final": "SUCCESS", "failure": None, "fail_step": None, "processed": 250, "succeeded": 250, "failed": 0, "message": None},
    "inventory-reconciliation-failure": {"job": "BATCH-INV-RECON", "final": "FAILED", "failure": "DATA_VALIDATION_ERROR", "fail_step": "RECONCILE_ON_HAND", "processed": 250, "succeeded": 248, "failed": 2, "message": "Inventory reconciliation detected negative available quantity for one or more balances."},
    "order-release-validation-failure": {"job": "BATCH-ORDER-RELEASE", "final": "FAILED", "failure": "BUSINESS_RULE_FAILURE", "fail_step": "VALIDATE_RELEASE_PREREQUISITES", "processed": 120, "succeeded": 112, "failed": 8, "message": "Order release batch found orders that cannot be released because allocation prerequisites are incomplete."},
    "shipment-sync-timeout": {"job": "BATCH-SHIP-SYNC", "final": "TIMEOUT", "failure": "EXTERNAL_SYSTEM_ERROR", "fail_step": "SYNC_CARRIER_STATUS", "processed": 80, "succeeded": 70, "failed": 10, "message": "Shipment status synchronization timed out while waiting for carrier status response."},
    "low-stock-notification-partial-failure": {"job": "BATCH-LOW-STOCK", "final": "PARTIAL_SUCCESS", "failure": "PARTIAL_RECORD_FAILURE", "fail_step": "PUBLISH_NOTIFICATIONS", "processed": 40, "succeeded": 32, "failed": 8, "message": "Low stock notification publishing partially failed for eight records."},
}


def _execute(db: Session, scenario_code: str) -> BatchRun:
    config = SCENARIOS.get(scenario_code)
    if config is None: raise BatchError("Unknown batch simulation.", 404)
    job = db.scalar(select(BatchJob).where(BatchJob.job_code == config["job"]))
    if job is None: raise BatchError(f"Batch job {config['job']} is not seeded.", 409)
    steps = db.scalars(select(BatchJobStep).where(BatchJobStep.job_id == job.id, BatchJobStep.enabled.is_(True)).order_by(BatchJobStep.step_order)).all()
    if not steps: raise BatchError("Batch job has no enabled steps.", 409)
    now = _now()
    run = BatchRun(run_number=_next_number(db), job_id=job.id, status="RUNNING", trigger_type="SIMULATION", scenario_code=scenario_code, started_at=now, summary=f"Batch run {scenario_code} is executing deterministically.", created_by="system", created_at=now, updated_at=now)
    db.add(run); db.flush()
    _event(db, run, "BATCH_RUN_CREATED", "Batch run created.", to_status="PENDING")
    _event(db, run, "BATCH_RUN_STARTED", "Batch run started.", from_status="PENDING", to_status="RUNNING")
    elapsed = 0
    failed = False
    for step in steps:
        step_started = _now()
        _event(db, run, "BATCH_STEP_STARTED", f"Step {step.step_code} started.", payload={"step_code": step.step_code})
        is_failure = step.step_code == config["fail_step"]
        is_partial = is_failure and config["final"] == "PARTIAL_SUCCESS"
        if failed:
            step_status, step_processed, step_success, step_failed = "SKIPPED", 0, 0, 0
            step_message = None
        elif is_failure:
            step_status = "PARTIAL_SUCCESS" if is_partial else "TIMEOUT" if config["final"] == "TIMEOUT" else "FAILED"
            step_processed, step_success, step_failed = config["processed"], config["succeeded"], config["failed"]
            step_message = config["message"]
            failed = not is_partial
        else:
            step_status, step_processed, step_success, step_failed, step_message = "SUCCESS", config["processed"], config["processed"], 0, None
        duration = step.expected_duration_ms + elapsed
        elapsed += step.expected_duration_ms
        step_run = BatchStepRun(batch_run_id=run.id, job_step_id=step.id, step_code=step.step_code, step_name=step.step_name, step_order=step.step_order, status=step_status, started_at=step_started, completed_at=_now(), duration_ms=duration, records_processed=step_processed, records_succeeded=step_success, records_failed=step_failed, failure_type=config["failure"] if is_failure else None, failure_message=step_message, technical_context={"scenario_code": scenario_code} if is_failure else None, created_at=_now(), updated_at=_now())
        db.add(step_run); db.flush()
        _event(db, run, "BATCH_STEP_FAILED" if is_failure and not is_partial else "BATCH_STEP_COMPLETED", step_message or f"Step {step.step_code} completed.", from_status="RUNNING", to_status=step_status, payload={"step_code": step.step_code, "records_failed": step_failed})
    run.status = config["final"]
    run.completed_at = _now()
    run.duration_ms = elapsed
    run.records_processed, run.records_succeeded, run.records_failed = config["processed"], config["succeeded"], config["failed"]
    run.failure_type, run.failure_message = config["failure"], config["message"]
    run.summary = config["message"] or f"{job.name} completed successfully with {run.records_processed} records processed."
    run.updated_at = _now()
    final_event = "BATCH_RUN_COMPLETED" if run.status == "SUCCESS" else "BATCH_RUN_PARTIAL_SUCCESS" if run.status == "PARTIAL_SUCCESS" else "BATCH_RUN_FAILED"
    _event(db, run, final_event, run.summary, from_status="RUNNING", to_status=run.status)
    db.flush()
    return run


def run_simulation(db: Session, scenario_code: str, create_exception: bool = False, create_ticket: bool = False, create_observability: bool = False) -> BatchSimulationResult:
    run = _execute(db, scenario_code)
    db.commit()
    if run.status != "SUCCESS" and create_exception:
        exception = create_exception_from_run(db, run.id, commit=True)
    if run.status != "SUCCESS" and create_ticket:
        from app.services.ams_ticket_service import create_ticket_from_batch_run
        create_ticket_from_batch_run(db, run.id)
    if run.status != "SUCCESS" and create_observability:
        from app.services.observability_service import create_diagnostic_from_batch_run
        create_diagnostic_from_batch_run(db, run.id)
    response = get_run(db, str(run.id))
    return BatchSimulationResult(run=response, exception_id=response.linked_exception_id, exception_number=response.linked_exception_number, ticket_id=response.linked_ticket_id, ticket_number=response.linked_ticket_number, diagnostic_case_id=response.linked_diagnostic_case_id, diagnostic_number=response.linked_diagnostic_number)


def run_suite(db: Session, create_exception: bool = True, create_ticket: bool = True, create_observability: bool = True) -> BatchSuiteResult:
    results: list[BatchSimulationResult] = []
    for scenario in ("inventory-reconciliation-success", "inventory-reconciliation-failure", "order-release-validation-failure", "shipment-sync-timeout", "low-stock-notification-partial-failure"):
        results.append(run_simulation(db, scenario, create_exception, create_ticket, create_observability))
    return BatchSuiteResult(
        runs_created=len(results), successful_runs=sum(item.run.status == "SUCCESS" for item in results), failed_runs=sum(item.run.status in ("FAILED", "TIMEOUT") for item in results), partial_runs=sum(item.run.status == "PARTIAL_SUCCESS" for item in results),
        tickets_created=sum(item.ticket_id is not None for item in results), exceptions_created=sum(item.exception_id is not None for item in results), diagnostics_created=sum(item.diagnostic_case_id is not None for item in results),
        summary="Ran the deterministic batch success, failure, timeout, and partial-success scenarios.", results=results,
    )


def create_exception_from_run(db: Session, run_id: UUID, commit: bool = True):
    run = db.get(BatchRun, run_id)
    if run is None: raise BatchError("Batch run not found.", 404)
    if run.linked_exception_id:
        existing = db.get(OpsException, run.linked_exception_id)
        if existing: return existing
    if run.status == "SUCCESS": raise BatchError("Successful batch runs cannot create failure exceptions.", 409)
    exception_type = "SYSTEM_INTEGRATION_FAILURE" if run.failure_type in ("EXTERNAL_SYSTEM_ERROR", "TIMEOUT", "DATABASE_LATENCY") else "WORKFLOW_VALIDATION_FAILURE"
    severity = "HIGH" if run.status == "TIMEOUT" or run.failure_type in ("EXTERNAL_SYSTEM_ERROR", "DATABASE_LATENCY", "DATA_VALIDATION_ERROR") else "MEDIUM"
    exception = create_or_refresh_exception(db, exception_type=exception_type, severity=severity, source_entity_type="BATCH_RUN", source_entity_id=run.id, source_reference=run.run_number, title=f"{run.job.name} {run.run_number} failed", description=run.failure_message or run.summary, detection_method="SYSTEM", business_impact="Batch processing did not complete as expected.", technical_context={"scenario_code": run.scenario_code, "failure_type": run.failure_type})
    exception.source_module = "BATCH_OPERATIONS"
    run.linked_exception_id, run.updated_at = exception.id, _now()
    _event(db, run, "BATCH_EXCEPTION_CREATED", f"Operational exception {exception.exception_number} created.", payload={"exception_id": str(exception.id)})
    if commit: db.commit()
    return exception


def create_diagnostic_from_run(db: Session, run_id: UUID):
    from app.services.observability_service import create_diagnostic_from_batch_run
    return create_diagnostic_from_batch_run(db, run_id)


def get_summary(db: Session) -> BatchSummary:
    jobs = db.scalar(select(func.count(BatchJob.id))) or 0
    total = db.scalar(select(func.count(BatchRun.id))) or 0
    success = db.scalar(select(func.count(BatchRun.id)).where(BatchRun.status == "SUCCESS")) or 0
    failed = db.scalar(select(func.count(BatchRun.id)).where(BatchRun.status == "FAILED")) or 0
    partial = db.scalar(select(func.count(BatchRun.id)).where(BatchRun.status == "PARTIAL_SUCCESS")) or 0
    timeout = db.scalar(select(func.count(BatchRun.id)).where(BatchRun.status == "TIMEOUT")) or 0
    open_tickets = db.scalar(select(func.count(BatchRun.id)).join(AmsTicket, AmsTicket.id == BatchRun.linked_ticket_id).where(AmsTicket.status.in_(ACTIVE_TICKET_STATUSES))) or 0
    open_exceptions = db.scalar(select(func.count(BatchRun.id)).join(OpsException, OpsException.id == BatchRun.linked_exception_id).where(OpsException.status.in_(("OPEN", "ACKNOWLEDGED", "LINKED_TO_TICKET")))) or 0
    last_status = db.scalar(select(BatchRun.status).order_by(BatchRun.created_at.desc()).limit(1))
    return BatchSummary(batch_jobs=jobs, runs_total=total, runs_success=success, runs_failed=failed, runs_partial=partial, runs_timeout=timeout, open_batch_tickets=open_tickets, open_batch_exceptions=open_exceptions, last_run_status=last_status)
