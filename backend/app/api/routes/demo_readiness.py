"""Readiness, reset, and showcase APIs scoped to local EOS demo data."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.demo_readiness import DemoResetRequest, PrepareShowcaseRequest
from app.services import demo_readiness_service as service

router = APIRouter(prefix="/api/v1/demo-readiness", tags=["demo-readiness"])


def _error(error: service.DemoReadinessError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.summary(db)


@router.get("/checks")
def readiness_checks(db: Session = Depends(get_db)) -> dict[str, Any]:
    items = service.checks(db)
    return {"checks": items, "summary": service.summary(db)}


@router.get("/showcase")
def showcase(db: Session = Depends(get_db)) -> dict[str, Any]:
    return {"mode": "SHOWCASE_READY", "readiness": service.summary(db), "reset_profiles": service.reset_profiles(), "suggested_flow": ["Verify readiness", "Prepare showcase with SHOWCASE_RESET", "Open the Executive Demo", "Run a guided scenario", "Review investigation evidence", "Review approval-gated actions", "Close with the audit and smoke report"], "urls": service.urls()["urls"]}


@router.get("/urls")
def launcher_urls() -> dict[str, Any]:
    return service.urls()


@router.get("/ui-test-guide")
def test_guide() -> dict[str, Any]:
    return service.ui_test_guide()


@router.get("/smoke-report")
def smoke(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.smoke_report(db)


@router.get("/reset-profiles")
def profiles() -> dict[str, Any]:
    return service.reset_profiles()


@router.post("/reset")
def reset(request: DemoResetRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.reset(db, request.profile, request.reset_reason, request.confirmation)
    except service.DemoReadinessError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/prepare-showcase")
def prepare(request: PrepareShowcaseRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.prepare_showcase(db, request.profile, request.create_prepared_runs, request.created_by_role)
    except service.DemoReadinessError as error:
        db.rollback()
        raise _error(error) from error
