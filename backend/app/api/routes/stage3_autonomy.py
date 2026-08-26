"""APIs for the explicitly requested local Stage 3 sandbox."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stage3_autonomy import SandboxControlRequest, SandboxDryRunRequest, SandboxKillSwitchRequest, SandboxRunCreateRequest, SandboxStartRequest
from app.services import stage3_autonomous_service as service

router = APIRouter(prefix="/api/v1/stage3-autonomy", tags=["stage3-autonomy"])


def _error(error: service.Stage3AutonomyError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/status")
def status(db: Session = Depends(get_db)) -> dict[str, Any]: return service.status(db)


@router.get("/profiles")
def profiles(db: Session = Depends(get_db)) -> list[dict[str, Any]]: return service.profiles(db)


@router.get("/runs")
def runs(case_id: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[dict[str, Any]]: return service.list_runs(db, case_id)


@router.get("/runs/{run_id}")
def run_detail(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try: return service._run_dict(db, service.get_run(db, run_id))
    except service.Stage3AutonomyError as error: raise _error(error) from error


@router.get("/runs/{run_id}/steps")
def steps(run_id: str, db: Session = Depends(get_db)):
    try: return service._run_dict(db, service.get_run(db, run_id))["steps"]
    except service.Stage3AutonomyError as error: raise _error(error) from error


@router.get("/runs/{run_id}/events")
def events(run_id: str, db: Session = Depends(get_db)):
    try: return service._run_dict(db, service.get_run(db, run_id))["events"]
    except service.Stage3AutonomyError as error: raise _error(error) from error


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict[str, Any]: return service.summary(db)


@router.post("/runs")
def create_run(request: SandboxRunCreateRequest, db: Session = Depends(get_db)):
    try: return service.create_run(db, request)
    except service.Stage3AutonomyError as error: db.rollback(); raise _error(error) from error


@router.post("/runs/{run_id}/dry-run")
def dry_run(run_id: str, request: SandboxDryRunRequest, db: Session = Depends(get_db)):
    try: return service.dry_run(db, run_id, request.requested_by_role)
    except service.Stage3AutonomyError as error: db.rollback(); raise _error(error) from error


@router.post("/runs/{run_id}/start")
def start(run_id: str, request: SandboxStartRequest, db: Session = Depends(get_db)):
    try: return service.start(db, run_id, request)
    except service.Stage3AutonomyError as error: db.rollback(); raise _error(error) from error


@router.post("/runs/{run_id}/pause")
def pause(run_id: str, request: SandboxControlRequest, db: Session = Depends(get_db)):
    try: return service.pause(db, run_id, request.reason)
    except service.Stage3AutonomyError as error: db.rollback(); raise _error(error) from error


@router.post("/runs/{run_id}/stop")
def stop(run_id: str, request: SandboxControlRequest, db: Session = Depends(get_db)):
    try: return service.stop(db, run_id, request.reason)
    except service.Stage3AutonomyError as error: db.rollback(); raise _error(error) from error


@router.post("/kill-switch")
def set_kill_switch(request: SandboxKillSwitchRequest, db: Session = Depends(get_db)):
    return service.kill_switch(db, request.enabled, request.requested_by_role, request.reason)
