"""Small deterministic safety-policy evaluator for governed AI requests."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_config import AiSafetyPolicy, AiSafetyPolicyRule
from app.schemas.ai_config import SafetyCheckResponse, SafetyMatchResponse


@dataclass
class SafetyEvaluation:
    decision: str
    safety_status: str
    matched_rules: list[AiSafetyPolicyRule]


def _default_policy(db: Session) -> AiSafetyPolicy | None:
    return db.scalar(select(AiSafetyPolicy).where(AiSafetyPolicy.enabled.is_(True)).order_by(AiSafetyPolicy.policy_code))


def evaluate(db: Session, text: str, policy: AiSafetyPolicy | None = None) -> SafetyEvaluation:
    policy = policy or _default_policy(db)
    if policy is None:
        return SafetyEvaluation("PASS", "NOT_EVALUATED", [])
    rules = db.scalars(select(AiSafetyPolicyRule).where(AiSafetyPolicyRule.policy_id == policy.id, AiSafetyPolicyRule.enabled.is_(True)).order_by(AiSafetyPolicyRule.rule_code)).all()
    lowered = text.lower()
    matched = [rule for rule in rules if rule.match_pattern.lower() in lowered]
    if any(rule.action == "BLOCK" for rule in matched):
        return SafetyEvaluation("BLOCK", "BLOCKED", matched)
    if matched:
        return SafetyEvaluation("WARN", "WARNED", matched)
    return SafetyEvaluation("PASS", "PASSED", [])


def response(evaluation: SafetyEvaluation) -> SafetyCheckResponse:
    matches = [SafetyMatchResponse(rule_code=rule.rule_code, name=rule.name, action=rule.action, severity=rule.severity, message=f"Safety rule {rule.rule_code} matched.") for rule in evaluation.matched_rules]
    if evaluation.decision == "BLOCK":
        message = "Safety policy blocked this request before provider invocation."
    elif evaluation.decision == "WARN":
        message = "Safety policy issued a warning; the request may proceed with review."
    else:
        message = "Safety policy passed this request."
    return SafetyCheckResponse(decision=evaluation.decision, safety_status=evaluation.safety_status, matched_rules=matches, message=message)
