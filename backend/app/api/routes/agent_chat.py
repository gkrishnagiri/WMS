"""REST API for user issue intake and deterministic Stage 1 agent chat."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ams import AmsTicket
from app.models.batch import BatchRun
from app.models.observability_alerts import ObsAlertEvent
from app.schemas.agent_chat import AgentActionProposalResponse, AgentCaseCreate, AgentCaseResponse, AgentChatMessageResponse, AgentChatSessionResponse, AgentEvidenceResponse, AgentIntakeRequest, AgentMessageCreate, AgentRunResponse, AgentSessionCreate
from app.services import agent_orchestrator_service as service

router = APIRouter(prefix="/api/v1/agent-chat", tags=["agent-chat"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 409), detail=getattr(error, "message", str(error)))


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.summary(db)


@router.post("/cases", response_model=AgentCaseResponse, status_code=201)
def create_case(request: AgentCaseCreate, db: Session = Depends(get_db)) -> AgentCaseResponse:
    try: return service.create_case(db, request)
    except service.AgentChatError as error: raise _error(error) from error


@router.get("/cases", response_model=list[AgentCaseResponse])
def cases(db: Session = Depends(get_db)) -> list[AgentCaseResponse]: return service.list_cases(db)


@router.get("/cases/{case_id}", response_model=AgentCaseResponse)
def case_detail(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_case(db, case_id)
    except service.AgentChatError as error: raise _error(error) from error


@router.post("/cases/{case_id}/close", response_model=AgentCaseResponse)
def close_case(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.close_case(db, case_id)
    except service.AgentChatError as error: db.rollback(); raise _error(error) from error


@router.post("/sessions", response_model=AgentChatSessionResponse, status_code=201)
def create_session(request: AgentSessionCreate, db: Session = Depends(get_db)):
    try: return service.create_session(db, request)
    except service.AgentChatError as error: raise _error(error) from error


@router.get("/sessions", response_model=list[AgentChatSessionResponse])
def sessions(db: Session = Depends(get_db)): return service.list_sessions(db)


@router.get("/sessions/{session_id}", response_model=AgentChatSessionResponse)
def session_detail(session_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_session(db, session_id)
    except service.AgentChatError as error: raise _error(error) from error


@router.post("/sessions/{session_id}/messages", response_model=AgentChatSessionResponse)
def send_message(session_id: UUID, request: AgentMessageCreate, db: Session = Depends(get_db)):
    try: return service.send_message(db, session_id, request)
    except service.AgentChatError as error: db.rollback(); raise _error(error) from error


@router.post("/sessions/{session_id}/close", response_model=AgentChatSessionResponse)
def close_session(session_id: UUID, db: Session = Depends(get_db)):
    try: return service.close_session(db, session_id)
    except service.AgentChatError as error: db.rollback(); raise _error(error) from error


@router.get("/sessions/{session_id}/messages", response_model=list[AgentChatMessageResponse])
def messages(session_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_messages(db, session_id)
    except service.AgentChatError as error: raise _error(error) from error


@router.get("/cases/{case_id}/evidence", response_model=list[AgentEvidenceResponse])
def evidence(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_evidence(db, case_id)
    except service.AgentChatError as error: raise _error(error) from error


@router.get("/cases/{case_id}/orchestration-runs", response_model=list[AgentRunResponse])
def runs(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_runs(db, case_id)
    except service.AgentChatError as error: raise _error(error) from error


@router.get("/cases/{case_id}/action-proposals", response_model=list[AgentActionProposalResponse])
def proposals(case_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_proposals(db, case_id)
    except service.AgentChatError as error: raise _error(error) from error


def _intake(request: AgentIntakeRequest, db: Session, audience: str, engineer: bool):
    try: return service.intake(db, request, audience, engineer)
    except service.AgentChatError as error: db.rollback(); raise _error(error) from error


@router.post("/intake/user-issue", response_model=AgentChatSessionResponse, status_code=201)
def user_issue_intake(request: AgentIntakeRequest, db: Session = Depends(get_db)): return _intake(request, db, "USER", False)


@router.post("/intake/engineer-investigation", response_model=AgentChatSessionResponse, status_code=201)
def engineer_intake(request: AgentIntakeRequest, db: Session = Depends(get_db)): return _intake(request, db, "SERVICE_ENGINEER", True)


@router.post("/intake/from-ams-ticket/{ticket_id}", response_model=AgentChatSessionResponse, status_code=201)
def from_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    ticket = db.get(AmsTicket, ticket_id)
    if ticket is None: raise HTTPException(status_code=404, detail="AMS ticket not found.")
    return _intake(AgentIntakeRequest(title=f"Investigate {ticket.ticket_number}", description=ticket.description, initial_message=f"Investigate this AMS ticket: {ticket.short_description}", created_by_role="SERVICE_ENGINEER", linked_ams_ticket_id=ticket.id), db, "SERVICE_ENGINEER", True)


@router.post("/intake/from-observability-alert/{event_id}", response_model=AgentChatSessionResponse, status_code=201)
def from_alert(event_id: UUID, db: Session = Depends(get_db)):
    event = db.get(ObsAlertEvent, event_id)
    if event is None: raise HTTPException(status_code=404, detail="Observability alert event not found.")
    return _intake(AgentIntakeRequest(title=f"Investigate {event.event_id}", description=event.description, initial_message=f"Summarize evidence for this observability alert: {event.title}", created_by_role="SERVICE_ENGINEER", linked_alert_event_id=event.id), db, "SERVICE_ENGINEER", True)


@router.post("/intake/from-batch-run/{run_id}", response_model=AgentChatSessionResponse, status_code=201)
def from_batch(run_id: UUID, db: Session = Depends(get_db)):
    batch = db.get(BatchRun, run_id)
    if batch is None: raise HTTPException(status_code=404, detail="Batch run not found.")
    return _intake(AgentIntakeRequest(title=f"Investigate {batch.run_number}", description=batch.failure_message or batch.summary, initial_message=f"Why did this batch run fail and what should I check next? {batch.run_number}", created_by_role="SERVICE_ENGINEER", linked_batch_run_id=batch.id), db, "SERVICE_ENGINEER", True)
