"""Governed Stage 1 model-assisted chat APIs."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent_model_chat import AgentModelAskResponse, AgentModelContextRequest, AgentModelContextResponse, AgentModelChatRequest, AgentModelStatusResponse
from app.schemas.agent_chat import AgentMessageCreate
from app.services import agent_model_chat_service, agent_orchestrator_service

router = APIRouter(prefix="/api/v1/agent-model-chat", tags=["agent-model-chat"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 409), detail=getattr(error, "message", str(error)))


@router.get("/status", response_model=AgentModelStatusResponse)
def model_status(db: Session = Depends(get_db)) -> AgentModelStatusResponse:
    return AgentModelStatusResponse.model_validate(agent_model_chat_service.status(db))


@router.post("/sessions/{session_id}/preview-context", response_model=AgentModelContextResponse)
def preview_context(session_id: str, request: AgentModelContextRequest, db: Session = Depends(get_db)) -> AgentModelContextResponse:
    try:
        record_id = agent_model_chat_service.resolve_session_id(db, session_id)
        package = agent_model_chat_service.build_context(db, record_id, request.message_text)
        issues = agent_model_chat_service.validate(db, record_id, request.message_text, task_type=request.task_type, use_real_model=False, context=package)
        return AgentModelContextResponse(session_id=str(session_id), task_type=request.task_type.upper(), context_package=package, validation_issues=issues)
    except Exception as error:
        raise _error(error) from error


@router.post("/sessions/{session_id}/dry-run", response_model=AgentModelContextResponse)
def dry_run(session_id: str, request: AgentModelChatRequest, db: Session = Depends(get_db)) -> AgentModelContextResponse:
    try:
        record_id = agent_model_chat_service.resolve_session_id(db, session_id)
        package = agent_model_chat_service.build_context(db, record_id, request.message_text)
        issues = agent_model_chat_service.validate(db, record_id, request.message_text, task_type=request.task_type, use_real_model=request.use_real_model, context=package)
        if request.use_real_model:
            issues = [*issues, *([agent_model_chat_service.status(db).get("reason")] if not agent_model_chat_service.status(db).get("safe_to_invoke") else [])]
        return AgentModelContextResponse(session_id=str(session_id), task_type=request.task_type.upper(), context_package={**package, "dry_run": True, "provider_code": request.provider_code, "model_code": request.model_code, "would_call_model": bool(request.use_real_model and not issues)}, validation_issues=list(dict.fromkeys(item for item in issues if item)), model_call_made=False)
    except Exception as error:
        raise _error(error) from error


@router.post("/sessions/{session_id}/ask", response_model=AgentModelAskResponse)
def ask(session_id: str, request: AgentModelChatRequest, db: Session = Depends(get_db)) -> AgentModelAskResponse:
    try:
        record_id = agent_model_chat_service.resolve_session_id(db, session_id)
        response = agent_orchestrator_service.send_message(db, record_id, AgentMessageCreate(message_text=request.message_text, use_real_model=request.use_real_model, provider_code=request.provider_code, model_code=request.model_code, dry_run=request.dry_run, task_type=request.task_type))
        assistant = next((message for message in reversed(response.messages) if message.sender_type == "AGENT"), None)
        metadata = assistant.metadata_json if assistant else {}
        return AgentModelAskResponse(session_id=str(session_id), answer=assistant.message_text if assistant else "No response was generated.", generation_mode=assistant.generation_mode if assistant else "FALLBACK_DETERMINISTIC", safety_status=assistant.safety_status if assistant else "SAFE", fallback_used=bool((metadata or {}).get("fallback_used")), invocation_id=(metadata or {}).get("ai_invocation_id"), invocation_number=(metadata or {}).get("invocation_number"), metadata=metadata or {}, actions_executed=0)
    except Exception as error:
        raise _error(error) from error


@router.get("/invocations")
def invocations(db: Session = Depends(get_db)):
    return agent_model_chat_service.invocation_list(db)


@router.get("/invocations/{invocation_id}")
def invocation(invocation_id: UUID, db: Session = Depends(get_db)):
    try:
        return agent_model_chat_service.invocation_detail(db, invocation_id)
    except Exception as error:
        raise _error(error) from error
