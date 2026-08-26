"""Local OpenAI pricing assumptions, usage snapshots, and smoke-test guardrails."""

from __future__ import annotations

from datetime import date, datetime, timezone
from math import ceil
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.ai_config import AiInvocationLog, AiModelConfig, AiProvider
from app.models.ai_costing import AiModelPricing, AiModelUsageMetering


class AiCostingError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message, self.status_code = message, status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _row(row: AiModelPricing) -> dict[str, Any]:
    return {"id": str(row.id), "pricing_id": row.pricing_id, "provider_code": row.provider_code, "model_code": row.model_code, "external_model_name": row.external_model_name, "currency": row.currency, "input_cost_per_million_tokens": row.input_cost_per_million_tokens, "completion_cost_per_million_tokens": row.completion_cost_per_million_tokens, "cached_input_cost_per_million_tokens": row.cached_input_cost_per_million_tokens, "reasoning_cost_per_million_tokens": row.reasoning_cost_per_million_tokens, "pricing_source_note": row.pricing_source_note, "pricing_effective_from": row.pricing_effective_from.isoformat() if row.pricing_effective_from else None, "is_active": row.is_active, "updated_at": row.updated_at.isoformat() if row.updated_at else None}


def _active_pricing(db: Session, model_code: str) -> AiModelPricing | None:
    return db.scalar(select(AiModelPricing).where(AiModelPricing.provider_code == "OPENAI_RESPONSES", AiModelPricing.model_code == model_code, AiModelPricing.is_active.is_(True)).order_by(AiModelPricing.updated_at.desc()))


def _model(db: Session, model_code: str) -> tuple[AiProvider | None, AiModelConfig | None]:
    model = db.scalar(select(AiModelConfig).where((AiModelConfig.model_code == model_code) | (AiModelConfig.model_name == model_code)))
    return (db.get(AiProvider, model.provider_id), model) if model else (None, None)


def pricing_status(pricing: AiModelPricing | None) -> str:
    if pricing is None:
        return "MISSING_PRICING"
    if pricing.input_cost_per_million_tokens == 0 and pricing.completion_cost_per_million_tokens == 0:
        return "PLACEHOLDER_OR_ZERO"
    return "CONFIGURED"


def model_catalog(db: Session, include_inactive: bool = False) -> list[dict[str, Any]]:
    query = select(AiModelConfig, AiProvider).join(AiProvider, AiProvider.id == AiModelConfig.provider_id).where(AiProvider.provider_code == "OPENAI_RESPONSES").order_by(AiModelConfig.model_code)
    if not include_inactive:
        query = query.where(AiModelConfig.catalog_active.is_(True))
    rows = db.execute(query).all()
    result = []
    for model, provider in rows:
        pricing = _active_pricing(db, model.model_code)
        result.append({"model_code": model.model_code, "external_model_name": model.model_name, "display_name": model.display_name, "provider_code": provider.provider_code, "enabled": model.enabled, "catalog_active": model.catalog_active, "provider_enabled": provider.enabled, "supports_real_invocation": bool(model.catalog_active and model.enabled and provider.enabled and not provider.is_mock), "pricing_configured": pricing is not None, "pricing_status": pricing_status(pricing), "pricing": _row(pricing) if pricing else None, "last_updated": model.updated_at})
    return result


def get_model(db: Session, model_code: str) -> dict[str, Any]:
    for item in model_catalog(db):
        if item["model_code"] == model_code or item["external_model_name"] == model_code:
            return item
    raise AiCostingError("OpenAI model is not present in the governed catalog.", 404)


def add_model(db: Session, payload: Any) -> dict[str, Any]:
    provider = db.scalar(select(AiProvider).where(AiProvider.provider_code == "OPENAI_RESPONSES"))
    if provider is None:
        raise AiCostingError("OPENAI_RESPONSES provider is not configured.", 409)
    code = payload.model_code.strip().upper()
    model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == code))
    if model is not None and model.catalog_active:
        raise AiCostingError("An active model with this model_code already exists.", 409)
    if model is None:
        model = AiModelConfig(model_code=code, provider_id=provider.id, display_name=payload.display_name or code, model_name=payload.external_model_name.strip(), model_family="OPENAI_RESPONSES", purpose="AGENT_STAGE_1_CHAT", enabled=payload.enabled, catalog_active=True, is_default=False, temperature=0, top_p=1, max_output_tokens=1200, context_window_tokens=128000, cost_per_1k_input_tokens=0, cost_per_1k_output_tokens=0)
        db.add(model); db.flush()
    else:
        model.provider_id, model.display_name, model.model_name, model.enabled, model.catalog_active, model.is_default = provider.id, payload.display_name or code, payload.external_model_name.strip(), payload.enabled, True, False
    for old in db.scalars(select(AiModelPricing).where(AiModelPricing.provider_code == "OPENAI_RESPONSES", AiModelPricing.model_code == code, AiModelPricing.is_active.is_(True))).all():
        old.is_active = False
    pricing = AiModelPricing(pricing_id=f"PRICE-{code}-{uuid4().hex[:10]}", provider_code="OPENAI_RESPONSES", model_code=code, external_model_name=model.model_name, currency="USD", input_cost_per_million_tokens=payload.input_cost_per_million_tokens, completion_cost_per_million_tokens=payload.completion_cost_per_million_tokens, cached_input_cost_per_million_tokens=payload.cached_input_cost_per_million_tokens, reasoning_cost_per_million_tokens=payload.reasoning_cost_per_million_tokens, pricing_source_note=payload.pricing_source_note, pricing_effective_from=payload.pricing_effective_from, is_active=True, created_at=_now(), updated_at=_now())
    db.add(pricing); db.commit(); db.refresh(model)
    return get_model(db, code)


def archive_model(db: Session, model_code: str) -> dict[str, Any]:
    provider, model = _model(db, model_code)
    if provider is None or model is None or provider.provider_code != "OPENAI_RESPONSES" or not model.catalog_active:
        raise AiCostingError("OpenAI model is not present in the active catalog.", 404)
    model.catalog_active, model.enabled, model.is_default = False, False, False
    for pricing in db.scalars(select(AiModelPricing).where(AiModelPricing.provider_code == "OPENAI_RESPONSES", AiModelPricing.model_code == model.model_code, AiModelPricing.is_active.is_(True))).all():
        pricing.is_active = False
    db.commit()
    return {"model_code": model.model_code, "catalog_active": False, "deleted": True, "deletion_mode": "ARCHIVED", "historical_pricing_preserved": True, "usage_history_preserved": True, "message": "Model was removed from the active costing catalog without deleting audit or usage history."}


def update_pricing(db: Session, model_code: str, payload: Any) -> dict[str, Any]:
    provider, model = _model(db, model_code)
    if provider is None or provider.provider_code != "OPENAI_RESPONSES" or model is None or not model.catalog_active:
        raise AiCostingError("Only configured OPENAI_RESPONSES models can receive pricing.", 404)
    current = _active_pricing(db, model.model_code)
    if current:
        current.is_active = False
    pricing = AiModelPricing(pricing_id=f"PRICE-{model.model_code}-{uuid4().hex[:10]}", provider_code="OPENAI_RESPONSES", model_code=model.model_code, external_model_name=model.model_name, currency=payload.currency.upper(), input_cost_per_million_tokens=payload.input_cost_per_million_tokens, completion_cost_per_million_tokens=payload.completion_cost_per_million_tokens, cached_input_cost_per_million_tokens=payload.cached_input_cost_per_million_tokens, reasoning_cost_per_million_tokens=payload.reasoning_cost_per_million_tokens, pricing_source_note=payload.pricing_source_note, pricing_effective_from=payload.pricing_effective_from, is_active=True, created_at=_now(), updated_at=_now())
    db.add(pricing); db.commit(); db.refresh(pricing)
    return {**_row(pricing), "pricing_status": pricing_status(pricing), "historical_pricing_preserved": bool(current)}


def calculate_cost(input_tokens: int | None, completion_tokens: int | None, pricing: AiModelPricing | None, cached_tokens: int | None = None, reasoning_tokens: int | None = None) -> dict[str, Any]:
    if pricing is None or input_tokens is None or completion_tokens is None:
        return {"estimated_input_cost": None, "estimated_completion_cost": None, "estimated_cached_input_cost": None, "estimated_reasoning_cost": None, "estimated_total_cost": None, "pricing_status": pricing_status(pricing)}
    values = {"estimated_input_cost": input_tokens * pricing.input_cost_per_million_tokens / 1_000_000, "estimated_completion_cost": completion_tokens * pricing.completion_cost_per_million_tokens / 1_000_000, "estimated_cached_input_cost": None, "estimated_reasoning_cost": None}
    if cached_tokens is not None and pricing.cached_input_cost_per_million_tokens is not None: values["estimated_cached_input_cost"] = cached_tokens * pricing.cached_input_cost_per_million_tokens / 1_000_000
    if reasoning_tokens is not None and pricing.reasoning_cost_per_million_tokens is not None: values["estimated_reasoning_cost"] = reasoning_tokens * pricing.reasoning_cost_per_million_tokens / 1_000_000
    values["estimated_total_cost"] = sum(value or 0 for value in values.values())
    values["pricing_status"] = pricing_status(pricing)
    return values


def _usage_values(invocation: AiInvocationLog, usage: dict[str, Any]) -> tuple[int | None, int | None, int | None, int | None, int | None, str]:
    def val(*keys: str) -> int | None:
        for key in keys:
            if usage.get(key) is not None:
                return int(usage[key])
        return None
    input_tokens, completion_tokens, total_tokens = val("input_tokens"), val("completion_tokens", "output_tokens"), val("total_tokens")
    cached, reasoning = val("cached_input_tokens", "cache_read_input_tokens"), val("reasoning_tokens")
    source = "PROVIDER_REPORTED" if input_tokens is not None or completion_tokens is not None or total_tokens is not None else "ESTIMATED"
    input_tokens = input_tokens if input_tokens is not None else invocation.input_tokens_estimated
    completion_tokens = completion_tokens if completion_tokens is not None else invocation.output_tokens_estimated
    total_tokens = total_tokens if total_tokens is not None else (input_tokens + completion_tokens if input_tokens is not None and completion_tokens is not None else invocation.total_tokens_estimated)
    if input_tokens is None and completion_tokens is None and total_tokens is None: source = "UNAVAILABLE"
    return input_tokens, completion_tokens, total_tokens, cached, reasoning, source


def record_usage_for_invocation(db: Session, invocation: AiInvocationLog, *, provider: AiProvider | None = None, model: AiModelConfig | None = None, usage: dict[str, Any] | None = None) -> AiModelUsageMetering | None:
    provider = provider or db.get(AiProvider, invocation.provider_id)
    model = model or db.get(AiModelConfig, invocation.model_config_id)
    if provider is None or model is None or provider.provider_code != "OPENAI_RESPONSES":
        return None
    existing = db.scalar(select(AiModelUsageMetering).where(AiModelUsageMetering.invocation_id == invocation.id))
    if existing:
        return existing
    pricing = _active_pricing(db, model.model_code)
    input_tokens, completion_tokens, total_tokens, cached, reasoning, source = _usage_values(invocation, usage or {})
    costs = calculate_cost(input_tokens, completion_tokens, pricing, cached, reasoning)
    snapshot = _row(pricing) if pricing else None
    item = AiModelUsageMetering(usage_id=f"USAGE-{uuid4().hex}", invocation_id=invocation.id, provider_code=provider.provider_code, model_code=model.model_code, external_model_name=model.model_name, task_type=invocation.task_type, request_source=invocation.request_source, session_id=invocation.request_source_id if invocation.request_source.upper().find("SESSION") >= 0 else None, input_tokens=input_tokens, completion_tokens=completion_tokens, total_tokens=total_tokens, cached_input_tokens=cached, reasoning_tokens=reasoning, estimated_input_cost=costs["estimated_input_cost"], estimated_completion_cost=costs["estimated_completion_cost"], estimated_cached_input_cost=costs["estimated_cached_input_cost"], estimated_reasoning_cost=costs["estimated_reasoning_cost"], estimated_total_cost=costs["estimated_total_cost"], currency=pricing.currency if pricing else "USD", pricing_id=pricing.pricing_id if pricing else None, pricing_snapshot_json=snapshot, usage_source=source, created_at=_now())
    db.add(item); db.flush()
    return item


def _meter_dict(item: AiModelUsageMetering) -> dict[str, Any]:
    return {"id": str(item.id), "usage_id": item.usage_id, "invocation_id": str(item.invocation_id), "provider_code": item.provider_code, "model_code": item.model_code, "external_model_name": item.external_model_name, "task_type": item.task_type, "request_source": item.request_source, "input_tokens": item.input_tokens, "completion_tokens": item.completion_tokens, "total_tokens": item.total_tokens, "cached_input_tokens": item.cached_input_tokens, "reasoning_tokens": item.reasoning_tokens, "estimated_input_cost": item.estimated_input_cost, "estimated_completion_cost": item.estimated_completion_cost, "estimated_cached_input_cost": item.estimated_cached_input_cost, "estimated_reasoning_cost": item.estimated_reasoning_cost, "estimated_total_cost": item.estimated_total_cost, "currency": item.currency, "pricing_id": item.pricing_id, "pricing_snapshot": item.pricing_snapshot_json, "usage_source": item.usage_source, "created_at": item.created_at}


def usage(db: Session, limit: int = 100) -> list[dict[str, Any]]:
    return [_meter_dict(item) for item in db.scalars(select(AiModelUsageMetering).order_by(AiModelUsageMetering.created_at.desc()).limit(limit)).all()]


def summary(db: Session) -> dict[str, Any]:
    from app.services.ai_provider_gateway import real_model_status
    settings = get_settings(); catalog = model_catalog(db); status = real_model_status(db)
    rows = db.scalars(select(AiModelUsageMetering)).all()
    total_cost = sum(row.estimated_total_cost or 0 for row in rows)
    today = _now().date(); today_rows = [row for row in rows if row.created_at and row.created_at.date() == today]
    return {"provider_code": "OPENAI_RESPONSES", "real_model_enabled": settings.real_model_enabled, "api_key_present": bool((settings.openai_api_key or "").strip()), "provider_enabled": status.provider_enabled, "active_model_count": sum(1 for item in catalog if item["enabled"]), "pricing_configured_count": sum(1 for item in catalog if item["pricing_configured"]), "total_invocations": len(rows), "total_input_tokens": sum(row.input_tokens or 0 for row in rows), "total_completion_tokens": sum(row.completion_tokens or 0 for row in rows), "total_tokens": sum(row.total_tokens or 0 for row in rows), "estimated_total_cost": total_cost, "estimated_cost_currency": "USD", "cost_today": sum(row.estimated_total_cost or 0 for row in today_rows), "safe_to_invoke": status.safe_to_invoke and all(item["pricing_configured"] for item in catalog if item["enabled"]), "reason": status.reason, "pricing_warning": "Estimated cost uses local editable assumptions and is not an OpenAI invoice."}


def grouped_usage(db: Session, by: str) -> list[dict[str, Any]]:
    rows = db.scalars(select(AiModelUsageMetering).order_by(AiModelUsageMetering.created_at.desc())).all(); groups: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row.model_code if by == "model" else (row.created_at.date().isoformat() if row.created_at else "unknown")
        group = groups.setdefault(key, {"key": key, "invocations": 0, "input_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "estimated_total_cost": 0})
        group["invocations"] += 1; group["input_tokens"] += row.input_tokens or 0; group["completion_tokens"] += row.completion_tokens or 0; group["total_tokens"] += row.total_tokens or 0; group["estimated_total_cost"] += row.estimated_total_cost or 0
    return list(groups.values())


def guardrails(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    return {"max_single_call_estimated_cost": settings.real_model_max_single_call_estimated_cost, "max_daily_estimated_cost": settings.real_model_max_daily_estimated_cost, "max_daily_invocations": settings.real_model_max_daily_invocations, "max_input_tokens": settings.real_model_max_input_tokens, "max_output_tokens": min(settings.real_model_max_output_tokens, 1200), "pricing_required_for_real_calls": True, "unknown_pricing_policy": "BLOCK_REAL_CALL", "safety_note": "All values are local guardrails; estimated cost is not an invoice."}


def validate_smoke(db: Session, model_code: str, message_text: str, max_output_tokens: int, *, allow_real_model: bool, acknowledge_cost: bool, allow_missing_pricing: bool = False, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings(); reasons: list[str] = []
    item = get_model(db, model_code); pricing = _active_pricing(db, item["model_code"]); input_tokens = max(1, ceil(len(message_text) / 4)); output_tokens = max_output_tokens; costs = calculate_cost(input_tokens, output_tokens, pricing)
    status = __import__("app.services.ai_provider_gateway", fromlist=["real_model_status"]).real_model_status(db, model_code=item["model_code"], settings=settings)
    allowed_tasks = {part.strip().upper() for part in settings.real_model_allowed_task_types.split(",") if part.strip()}
    if "MODEL_SMOKE_TEST" not in allowed_tasks: reasons.append("MODEL_SMOKE_TEST is not an allowed governed task type")
    if not allow_real_model: reasons.append("allow_real_model must be true for an external call")
    if not acknowledge_cost: reasons.append("cost acknowledgement is required")
    if not status.safe_to_invoke: reasons.append(status.reason)
    if pricing is None and not allow_missing_pricing: reasons.append("pricing is missing; real calls are blocked")
    if input_tokens > settings.real_model_max_input_tokens: reasons.append("estimated input tokens exceed the guardrail")
    if output_tokens > min(settings.real_model_max_output_tokens, 1200): reasons.append("requested output tokens exceed the guardrail")
    if costs["estimated_total_cost"] is not None and costs["estimated_total_cost"] > settings.real_model_max_single_call_estimated_cost: reasons.append("estimated single-call cost exceeds the guardrail")
    rows = db.scalars(select(AiModelUsageMetering)).all(); today = _now().date(); today_rows = [row for row in rows if row.created_at and row.created_at.date() == today]
    if len(today_rows) >= settings.real_model_max_daily_invocations: reasons.append("daily invocation guardrail reached")
    if sum(row.estimated_total_cost or 0 for row in today_rows) + (costs["estimated_total_cost"] or 0) > settings.real_model_max_daily_estimated_cost: reasons.append("daily estimated cost guardrail reached")
    return {"model": item, "provider_status": status.model_dump(), "input_tokens_estimate": input_tokens, "max_output_tokens": output_tokens, "estimated_cost": costs, "pricing_status": pricing_status(pricing), "would_call_model": not reasons, "blocked_reasons": list(dict.fromkeys(reasons)), "model_call_made": False}


def real_call_guardrail(db: Session, model_code: str, prompt: str, output_tokens: int, settings: Settings | None = None) -> list[str]:
    """Guardrail used immediately before the gateway crosses the external boundary."""
    settings = settings or get_settings(); reasons: list[str] = []
    pricing = _active_pricing(db, model_code); input_tokens = max(1, ceil(len(prompt) / 4))
    costs = calculate_cost(input_tokens, output_tokens, pricing)
    if pricing is None: reasons.append("pricing is missing; real calls are blocked")
    if input_tokens > settings.real_model_max_input_tokens: reasons.append("estimated input tokens exceed the guardrail")
    if output_tokens > min(settings.real_model_max_output_tokens, 1200): reasons.append("requested output tokens exceed the guardrail")
    if costs["estimated_total_cost"] is not None and costs["estimated_total_cost"] > settings.real_model_max_single_call_estimated_cost: reasons.append("estimated single-call cost exceeds the guardrail")
    today = _now().date(); rows = db.scalars(select(AiModelUsageMetering)).all(); today_rows = [row for row in rows if row.created_at and row.created_at.date() == today]
    if len(today_rows) >= settings.real_model_max_daily_invocations: reasons.append("daily invocation guardrail reached")
    if sum(row.estimated_total_cost or 0 for row in today_rows) + (costs["estimated_total_cost"] or 0) > settings.real_model_max_daily_estimated_cost: reasons.append("daily estimated cost guardrail reached")
    return list(dict.fromkeys(reasons))


def invocation_cost(db: Session, invocation_id: UUID) -> dict[str, Any]:
    item = db.scalar(select(AiModelUsageMetering).where(AiModelUsageMetering.invocation_id == invocation_id))
    if item is None:
        raise AiCostingError("Usage metering for invocation was not found.", 404)
    return _meter_dict(item)
