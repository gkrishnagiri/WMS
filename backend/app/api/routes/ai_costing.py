from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai_costing import ModelCreateRequest, PricingUpdateRequest, SmokeTestRequest
from app.services import ai_model_cost_service
from app.services import ai_provider_gateway
from app.schemas.ai_config import RealModelRequest

router = APIRouter(prefix="/api/v1/ai-costing", tags=["ai-costing"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 409), detail=getattr(error, "message", str(error)))


@router.get("/summary")
def summary(db: Session = Depends(get_db)): return ai_model_cost_service.summary(db)


@router.get("/models")
def models(include_inactive: bool = False, db: Session = Depends(get_db)): return ai_model_cost_service.model_catalog(db, include_inactive=include_inactive)


@router.post("/models", status_code=201)
def create_model(request: ModelCreateRequest, db: Session = Depends(get_db)):
    try: return ai_model_cost_service.add_model(db, request)
    except Exception as error: raise _error(error) from error


@router.get("/models/{model_code}")
def model(model_code: str, db: Session = Depends(get_db)):
    try: return ai_model_cost_service.get_model(db, model_code)
    except Exception as error: raise _error(error) from error


@router.delete("/models/{model_code}")
def delete_model(model_code: str, db: Session = Depends(get_db)):
    try: return ai_model_cost_service.archive_model(db, model_code)
    except Exception as error: raise _error(error) from error


@router.put("/models/{model_code}/pricing")
def pricing(model_code: str, request: PricingUpdateRequest, db: Session = Depends(get_db)):
    try: return ai_model_cost_service.update_pricing(db, model_code, request)
    except Exception as error: raise _error(error) from error


@router.get("/usage")
def usage(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)): return ai_model_cost_service.usage(db, limit)


@router.get("/usage/by-model")
def usage_by_model(db: Session = Depends(get_db)): return ai_model_cost_service.grouped_usage(db, "model")


@router.get("/usage/by-day")
def usage_by_day(db: Session = Depends(get_db)): return ai_model_cost_service.grouped_usage(db, "day")


@router.get("/invocations/{invocation_id}/cost")
def cost(invocation_id: UUID, db: Session = Depends(get_db)):
    try: return ai_model_cost_service.invocation_cost(db, invocation_id)
    except Exception as error: raise _error(error) from error


@router.get("/guardrails")
def guardrail_config(): return ai_model_cost_service.guardrails()


@router.post("/smoke-test/dry-run")
def smoke_dry_run(request: SmokeTestRequest, db: Session = Depends(get_db)):
    try:
        result = ai_model_cost_service.validate_smoke(db, request.model_code, request.message_text, request.max_output_tokens, allow_real_model=request.allow_real_model, acknowledge_cost=request.acknowledge_cost, allow_missing_pricing=request.allow_missing_pricing)
        result["status"] = "DRY_RUN"; result["message"] = "No external model was called."
        return result
    except Exception as error: raise _error(error) from error


@router.post("/smoke-test/run")
def smoke_run(request: SmokeTestRequest, db: Session = Depends(get_db)):
    try:
        check = ai_model_cost_service.validate_smoke(db, request.model_code, request.message_text, request.max_output_tokens, allow_real_model=request.allow_real_model, acknowledge_cost=request.acknowledge_cost, allow_missing_pricing=request.allow_missing_pricing)
        if check["would_call_model"]:
            result = ai_provider_gateway.invoke_real_model(db, RealModelRequest(provider_code="OPENAI_RESPONSES", model_code=request.model_code, task_type="MODEL_SMOKE_TEST", request_source="AI_COSTING_SMOKE_TEST", input_text=request.message_text, context_items=[], allow_real_model=True, max_output_tokens=request.max_output_tokens))
            body = result.model_dump(mode="json")
            body.update({"status": "COMPLETED", "preflight": check, "model_call_made": True})
            return body
        # Record the explicit attempt through the governed gateway, but force
        # allow_real_model=False so a blocked preflight can never cross the
        # external provider boundary.
        audit_id = None
        try:
            audit = ai_provider_gateway.invoke_real_model(db, RealModelRequest(provider_code="OPENAI_RESPONSES", model_code=request.model_code, task_type="MODEL_SMOKE_TEST", request_source="AI_COSTING_SMOKE_TEST", input_text=request.message_text, context_items=[], allow_real_model=False, max_output_tokens=request.max_output_tokens))
            audit_id = str(audit.invocation_id) if audit.invocation_id else None
        except Exception:
            pass
        return {"status": "BLOCKED", "model_call_made": False, "invocation_id": audit_id, "preflight": check, "blocked_reasons": check["blocked_reasons"], "message": "No external model was called."}
    except Exception as error: raise _error(error) from error
