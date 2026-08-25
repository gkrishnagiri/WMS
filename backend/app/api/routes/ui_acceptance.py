"""Manual browser-first UI acceptance testing APIs."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ui_acceptance import RunSummaryRequest, StartUiTestRunRequest, StepResultRequest
from app.services import ui_acceptance_service as service

router = APIRouter(prefix="/api/v1/ui-acceptance", tags=["ui-acceptance"])


def _error(error: service.UiAcceptanceError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.summary(db)


@router.get("/suites")
def suites(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return service.list_suites(db)


@router.get("/cases")
def cases(suite_code: str | None = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return service.list_cases(db, suite_code)


@router.get("/cases/{case_code}")
def case_detail(case_code: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.get_case(db, case_code)
    except service.UiAcceptanceError as error:
        raise _error(error) from error


@router.get("/runs")
def runs(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return service.list_runs(db)


@router.get("/runs/{run_id}")
def run_detail(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service._run_dict(db, service.get_run(db, run_id))
    except service.UiAcceptanceError as error:
        raise _error(error) from error


@router.get("/runs/{run_id}/report")
def run_report(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.report(db, run_id)
    except service.UiAcceptanceError as error:
        raise _error(error) from error


@router.get("/runs/{run_id}/report.md")
def run_report_markdown(run_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        return Response(content=service.report_markdown(db, run_id), media_type="text/markdown")
    except service.UiAcceptanceError as error:
        raise _error(error) from error


@router.get("/coverage")
def coverage(run_id: str | None = None, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.coverage(db, run_id)
    except service.UiAcceptanceError as error:
        raise _error(error) from error


@router.post("/runs/start")
def start_run(request: StartUiTestRunRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.start_run(db, request.run_title, request.tester_role, request.suite_codes)
    except service.UiAcceptanceError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/runs/{run_id}/step-results")
def step_result(run_id: str, request: StepResultRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.record_step_result(db, run_id, request.suite_code, request.case_code, request.step_code, request.status, request.observed_result, request.evidence_note, request.screenshot_reference, request.defect_note, request.tested_by_role)
    except service.UiAcceptanceError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/runs/{run_id}/complete")
def complete_run(run_id: str, request: RunSummaryRequest = RunSummaryRequest(), db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.complete_run(db, run_id, request.summary)
    except service.UiAcceptanceError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/runs/{run_id}/abort")
def abort_run(run_id: str, request: RunSummaryRequest = RunSummaryRequest(), db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.abort_run(db, run_id, request.summary)
    except service.UiAcceptanceError as error:
        db.rollback()
        raise _error(error) from error
