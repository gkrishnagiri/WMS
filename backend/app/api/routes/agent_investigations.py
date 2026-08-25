"""Read-only consolidated agent investigation workspace APIs."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import agent_investigation_service as service

router = APIRouter(prefix="/api/v1/agent-investigations", tags=["agent-investigations"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 404), detail=getattr(error, "message", str(error)))


@router.get("/summary")
def summary(db: Session = Depends(get_db)): return service.summary(db)


@router.get("/cases")
def cases(db: Session = Depends(get_db)): return service.list_workspaces(db)


@router.get("/cases/{case_id}")
def case_detail(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_workspace(db, case_id)
    except service.AgentInvestigationError as error: raise _error(error) from error


@router.get("/cases/{case_id}/timeline")
def case_timeline(case_id: UUID, descending: bool = Query(default=False), db: Session = Depends(get_db)):
    try: return service.timeline(db, case_id, descending)
    except service.AgentInvestigationError as error: raise _error(error) from error


@router.get("/cases/{case_id}/evidence")
def case_evidence(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.evidence(db, case_id)
    except service.AgentInvestigationError as error: raise _error(error) from error


@router.get("/cases/{case_id}/knowledge")
def case_knowledge(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.knowledge(db, case_id)
    except service.AgentInvestigationError as error: raise _error(error) from error


@router.get("/cases/{case_id}/orchestration-runs")
def case_runs(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_workspace(db, case_id)["orchestration_runs"]
    except service.AgentInvestigationError as error: raise _error(error) from error


@router.get("/cases/{case_id}/action-proposals")
def case_proposals(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_workspace(db, case_id)["action_proposals"]
    except service.AgentInvestigationError as error: raise _error(error) from error


@router.get("/cases/{case_id}/drafts")
def case_drafts(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.drafts(db, case_id)
    except service.AgentInvestigationError as error: raise _error(error) from error


@router.post("/cases/{case_id}/generate-drafts")
def generate_drafts(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.drafts(db, case_id)
    except service.AgentInvestigationError as error: raise _error(error) from error
