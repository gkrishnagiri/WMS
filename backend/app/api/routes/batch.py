"""Deterministic batch job, run, and support-artifact APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.batch import BatchJobResponse, BatchRunEventResponse, BatchRunResponse, BatchSimulationRequest, BatchSimulationResult, BatchSummary, BatchSuiteResult
from app.schemas.ams import TicketResponse
from app.schemas.operations import ExceptionResponse
from app.schemas.observability import DiagnosticCaseResponse
from app.services import ams_ticket_service, batch_service, observability_service
from app.services.operations_exception_service import exception_to_response

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 409), detail=getattr(error, "message", str(error)))


@router.get("/summary", response_model=BatchSummary)
def summary(db: Session = Depends(get_db)) -> BatchSummary: return batch_service.get_summary(db)


@router.get("/jobs", response_model=list[BatchJobResponse])
def jobs(enabled: bool | None = None, job_type: str | None = None, db: Session = Depends(get_db)) -> list[BatchJobResponse]: return batch_service.list_jobs(db, enabled, job_type)


@router.get("/jobs/{job_identifier}", response_model=BatchJobResponse)
def job_detail(job_identifier: str, db: Session = Depends(get_db)):
    try: return batch_service.get_job(db, job_identifier)
    except batch_service.BatchError as error: raise _error(error) from error


@router.get("/runs", response_model=list[BatchRunResponse])
def runs(job_code: str | None = None, status_filter: str | None = Query(default=None, alias="status"), failure_type: str | None = None, linked_ticket: bool | None = None, db: Session = Depends(get_db)) -> list[BatchRunResponse]: return batch_service.list_runs(db, job_code, status_filter, failure_type, linked_ticket)


@router.get("/runs/{run_identifier}", response_model=BatchRunResponse)
def run_detail(run_identifier: str, db: Session = Depends(get_db)):
    try: return batch_service.get_run(db, run_identifier)
    except batch_service.BatchError as error: raise _error(error) from error


@router.get("/runs/{run_identifier}/events", response_model=list[BatchRunEventResponse])
def run_events(run_identifier: str, db: Session = Depends(get_db)):
    try: return batch_service.list_events(db, run_identifier)
    except batch_service.BatchError as error: raise _error(error) from error


@router.post("/runs/{run_identifier}/create-exception", response_model=ExceptionResponse)
def create_exception(run_identifier: str, db: Session = Depends(get_db)):
    try:
        run = batch_service.get_run(db, run_identifier)
        return exception_to_response(db, batch_service.create_exception_from_run(db, run.id))
    except batch_service.BatchError as error:
        db.rollback(); raise _error(error) from error


@router.post("/runs/{run_identifier}/create-ticket", response_model=TicketResponse)
def create_ticket(run_identifier: str, db: Session = Depends(get_db)):
    try:
        run = batch_service.get_run(db, run_identifier)
        return ams_ticket_service.create_ticket_from_batch_run(db, run.id)
    except (batch_service.BatchError, ams_ticket_service.AmsError) as error:
        db.rollback(); raise _error(error) from error


@router.post("/runs/{run_identifier}/create-diagnostic", response_model=DiagnosticCaseResponse)
def create_diagnostic(run_identifier: str, db: Session = Depends(get_db)):
    try:
        run = batch_service.get_run(db, run_identifier)
        return observability_service.create_diagnostic_from_batch_run(db, run.id)
    except (batch_service.BatchError, observability_service.ObservabilityError) as error:
        db.rollback(); raise _error(error) from error


def _simulate(code: str, request: BatchSimulationRequest, db: Session) -> BatchSimulationResult:
    try: return batch_service.run_simulation(db, code, request.create_exception, request.create_ticket, request.create_observability)
    except batch_service.BatchError as error: db.rollback(); raise _error(error) from error


@router.post("/simulations/inventory-reconciliation-success", response_model=BatchSimulationResult)
def inventory_success(request: BatchSimulationRequest = BatchSimulationRequest(), db: Session = Depends(get_db)): return _simulate("inventory-reconciliation-success", request, db)


@router.post("/simulations/inventory-reconciliation-failure", response_model=BatchSimulationResult)
def inventory_failure(request: BatchSimulationRequest = BatchSimulationRequest(), db: Session = Depends(get_db)): return _simulate("inventory-reconciliation-failure", request, db)


@router.post("/simulations/order-release-validation-failure", response_model=BatchSimulationResult)
def order_release_failure(request: BatchSimulationRequest = BatchSimulationRequest(), db: Session = Depends(get_db)): return _simulate("order-release-validation-failure", request, db)


@router.post("/simulations/shipment-sync-timeout", response_model=BatchSimulationResult)
def shipment_timeout(request: BatchSimulationRequest = BatchSimulationRequest(), db: Session = Depends(get_db)): return _simulate("shipment-sync-timeout", request, db)


@router.post("/simulations/low-stock-notification-partial-failure", response_model=BatchSimulationResult)
def low_stock_partial(request: BatchSimulationRequest = BatchSimulationRequest(), db: Session = Depends(get_db)): return _simulate("low-stock-notification-partial-failure", request, db)


@router.post("/simulations/batch-failure-suite", response_model=BatchSuiteResult)
def failure_suite(request: BatchSimulationRequest = BatchSimulationRequest(create_exception=True, create_ticket=True, create_observability=True), db: Session = Depends(get_db)) -> BatchSuiteResult:
    try: return batch_service.run_suite(db, request.create_exception, request.create_ticket, request.create_observability)
    except batch_service.BatchError as error: db.rollback(); raise _error(error) from error
