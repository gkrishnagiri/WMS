"""Governed AI configuration, safety, audit, and mock-invocation APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai_config import AiConfigSummary, GuardrailEventResponse, InvocationResponse, ModelConfigResponse, PromptTemplateResponse, ProviderResponse, SafetyCheckRequest, SafetyCheckResponse, SafetyPolicyResponse, SafetyRuleResponse, TestInvocationRequest, UsageDailyResponse
from app.services import ai_config_service, ai_provider_gateway, ai_safety_service

router = APIRouter(prefix="/api/v1/ai-config", tags=["ai-config"])


def _error(error: Exception) -> HTTPException:
    status_code = getattr(error, "status_code", 409)
    return HTTPException(status_code=status_code, detail=getattr(error, "message", str(error)))


@router.get("/summary", response_model=AiConfigSummary)
def summary(db: Session = Depends(get_db)) -> AiConfigSummary:
    return ai_config_service.get_summary(db)


@router.get("/providers", response_model=list[ProviderResponse])
def providers(db: Session = Depends(get_db)) -> list[ProviderResponse]:
    return ai_config_service.list_providers(db)


@router.get("/models", response_model=list[ModelConfigResponse])
def models(db: Session = Depends(get_db)) -> list[ModelConfigResponse]:
    return ai_config_service.list_models(db)


@router.get("/prompt-templates", response_model=list[PromptTemplateResponse])
def prompt_templates(db: Session = Depends(get_db)) -> list[PromptTemplateResponse]:
    return ai_config_service.list_templates(db)


@router.get("/safety-policies", response_model=list[SafetyPolicyResponse])
def safety_policies(db: Session = Depends(get_db)) -> list[SafetyPolicyResponse]:
    return ai_config_service.list_policies(db)


@router.get("/safety-rules", response_model=list[SafetyRuleResponse])
def safety_rules(db: Session = Depends(get_db)) -> list[SafetyRuleResponse]:
    return ai_config_service.list_rules(db)


@router.get("/invocations", response_model=list[InvocationResponse])
def invocations(status: str | None = None, task_type: str | None = None, provider_code: str | None = None, model_code: str | None = None, safety_status: str | None = None, request_source: str | None = None, db: Session = Depends(get_db)) -> list[InvocationResponse]:
    return ai_config_service.list_invocations(db, status, task_type, provider_code, model_code, safety_status, request_source)


@router.get("/invocations/{invocation_id}", response_model=InvocationResponse)
def invocation_detail(invocation_id: UUID, db: Session = Depends(get_db)) -> InvocationResponse:
    try: return ai_config_service.get_invocation(db, invocation_id)
    except ai_config_service.AiConfigError as error: raise _error(error) from error


@router.get("/usage-daily", response_model=list[UsageDailyResponse])
def usage_daily(db: Session = Depends(get_db)) -> list[UsageDailyResponse]:
    return ai_config_service.list_usage(db)


@router.get("/guardrail-events", response_model=list[GuardrailEventResponse])
def guardrail_events(db: Session = Depends(get_db)) -> list[GuardrailEventResponse]:
    return ai_config_service.list_guardrail_events(db)


@router.post("/test-invocation", response_model=InvocationResponse, status_code=201)
def test_invocation(request: TestInvocationRequest, db: Session = Depends(get_db)) -> InvocationResponse:
    try:
        return ai_provider_gateway.invoke(db, task_type=request.task_type, input_payload=request.input_payload, request_source=request.request_source, request_source_id=request.request_source_id, template_code=request.template_code, model_code=request.model_code, created_by=request.created_by)
    except ai_provider_gateway.AiGatewayError as error: raise _error(error) from error


@router.post("/safety-check", response_model=SafetyCheckResponse)
def safety_check(request: SafetyCheckRequest, db: Session = Depends(get_db)) -> SafetyCheckResponse:
    return ai_safety_service.response(ai_safety_service.evaluate(db, request.text))
