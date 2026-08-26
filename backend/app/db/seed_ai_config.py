"""Idempotently seed governed AI configuration for the deterministic mock phase."""

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.models.ai_config import AiModelConfig, AiPromptTemplate, AiProvider, AiSafetyPolicy, AiSafetyPolicyRule

PROVIDERS = [
    ("MOCK_GOVERNED", "Governed Mock Provider", "MOCK", "Deterministic local provider used for governed tests.", None, "NONE", True, True),
    ("OPENAI_RESPONSES", "OpenAI Responses API", "REAL_MODEL", "Disabled by default; optional governed OpenAI-compatible Responses API provider.", None, "API_KEY_REFERENCE", False, False),
    ("OPENAI_DISABLED_PLACEHOLDER", "OpenAI Placeholder", "OPENAI_COMPATIBLE", "Disabled placeholder; no credentials or calls are configured.", "https://api.openai.com", "API_KEY_REFERENCE", False, False),
    ("AZURE_OPENAI_DISABLED_PLACEHOLDER", "Azure OpenAI Placeholder", "AZURE_OPENAI", "Disabled placeholder; no credentials or calls are configured.", None, "API_KEY_REFERENCE", False, False),
    ("LOCAL_MODEL_DISABLED_PLACEHOLDER", "Local Model Placeholder", "LOCAL", "Disabled placeholder for a future local runtime.", None, "NONE", False, False),
]

TEMPLATES = [
    ("TPL-COPILOT-CONTEXT-SUMMARY", "Copilot Context Summary", "Summarize governed support context.", "COPILOT_CONTEXT_SUMMARY", "You summarize only supplied EOS context.", "Summarize this support context: {input}", {"input": "object"}, {"summary": "string"}),
    ("TPL-COPILOT-RECOMMENDATION", "Copilot Recommendation", "Draft a support recommendation from supplied evidence.", "COPILOT_RECOMMENDATION", "You recommend reviewable support steps only.", "Recommend next steps for: {input}", {"input": "object"}, {"recommendation": "string"}),
    ("TPL-WORK-NOTE-DRAFT", "Work Note Draft", "Draft an internal ticket work note.", "WORK_NOTE_DRAFT", "You draft internal support notes for human review.", "Draft a work note for: {input}", {"input": "object"}, {"work_note": "string"}),
    ("TPL-CUSTOMER-UPDATE-DRAFT", "Customer Update Draft", "Draft a customer-safe support update.", "CUSTOMER_UPDATE_DRAFT", "You draft plain-language customer communications.", "Draft a customer update for: {input}", {"input": "object"}, {"customer_update": "string"}),
    ("TPL-INVESTIGATION-CHECKLIST", "Investigation Checklist", "Draft a support investigation checklist.", "INVESTIGATION_CHECKLIST", "You produce a reviewable checklist and do not execute actions.", "Create an investigation checklist for: {input}", {"input": "object"}, {"checklist": "array"}),
    ("TPL-GENERAL-TEST", "General Governed Test", "Run a safe deterministic provider test.", "GENERAL_TEST", "You return a concise deterministic test response.", "Respond safely to: {input}", {"input": "object"}, {"response": "string"}),
    ("TPL-AGENT-STAGE-1-GUIDANCE", "Agent Stage 1 Guidance", "Governed read-only guidance for an agent case.", "AGENT_STAGE_1_GUIDANCE", "You are a Stage 1 read-only support assistant. Use only the supplied EOS context. Do not claim that you executed an action, do not ask for secrets, do not provide autonomous remediation, and say what evidence is missing when uncertain. Return concise structured guidance.", "Provide Stage 1 guidance for this case and its curated evidence: {input}", {"input": "object"}, {"guidance": "string"}),
    ("TPL-AGENT-KNOWLEDGE-SUMMARY", "Agent Knowledge Summary", "Summarize curated knowledge for a support case.", "AGENT_KNOWLEDGE_SUMMARY", "Summarize only supplied knowledge. This is read-only support guidance; do not claim actions were executed and do not ask for secrets.", "Summarize the relevant knowledge: {input}", {"input": "object"}, {"summary": "string"}),
    ("TPL-AGENT-EVIDENCE-SUMMARY", "Agent Evidence Summary", "Summarize curated operational evidence.", "AGENT_EVIDENCE_SUMMARY", "Summarize only supplied evidence. Do not invent current state, execute tools, or propose autonomous remediation.", "Summarize the supplied evidence: {input}", {"input": "object"}, {"summary": "string"}),
    ("TPL-CUSTOMER-FACING-ISSUE-GUIDANCE", "Customer Issue Guidance", "Draft safe user-facing issue guidance.", "CUSTOMER_FACING_ISSUE_GUIDANCE", "Provide cautious, plain-language Stage 1 guidance. Do not ask for credentials or claim that EOS changed anything.", "Provide customer-safe guidance for: {input}", {"input": "object"}, {"guidance": "string"}),
    ("TPL-SERVICE-ENGINEER-INVESTIGATION-GUIDANCE", "Service Engineer Investigation Guidance", "Draft read-only service engineer guidance.", "SERVICE_ENGINEER_INVESTIGATION_GUIDANCE", "Provide reviewable Stage 1 investigation guidance from supplied context only. Do not execute actions or request secrets.", "Provide engineer investigation guidance for: {input}", {"input": "object"}, {"guidance": "string"}),
    ("TPL-AGENT-STAGE-1-CHAT", "Agent Stage 1 Chat", "Governed model-assisted read-only support chat.", "AGENT_STAGE_1_CHAT", "You are an enterprise AMS support agent operating in Stage 1 read-only mode. Use only the provided context. Do not claim to have executed actions. Do not instruct anyone to run shell commands. Do not request passwords, tokens, API keys, or secrets. Do not send customer communications. Do not post to ServiceNow. Do not resolve or close production objects. You may recommend human-reviewed next steps. Cite the context items used. Keep the answer concise and structured.", "Answer the engineer's question using only this curated context: {input}", {"input": "object"}, {"answer": "string"}),
    ("TPL-AGENT-INVESTIGATION-QA", "Agent Investigation Q&A", "Governed read-only investigation question answering.", "AGENT_INVESTIGATION_QA", "You are an enterprise AMS support agent operating in Stage 1 read-only mode. Use only the provided context and identify missing evidence when uncertain. Never execute or claim execution of actions, use tools, run commands, access secrets, send messages, post to ServiceNow, or resolve production objects. Cite context items used.", "Answer this investigation question from the supplied context: {input}", {"input": "object"}, {"answer": "string"}),
    ("TPL-AGENT-KNOWLEDGE-GROUNDED-ANSWER", "Knowledge Grounded Answer", "Governed answer grounded in curated knowledge and evidence.", "AGENT_KNOWLEDGE_GROUNDED_ANSWER", "You are an enterprise AMS support agent operating in Stage 1 read-only mode. Use only the provided evidence and curated knowledge. Do not claim actions were executed, request secrets, issue shell or SQL instructions, communicate externally, or bypass human approval. Cite context items used.", "Produce a concise grounded answer: {input}", {"input": "object"}, {"answer": "string"}),
    ("TPL-MODEL-SMOKE-TEST", "OpenAI Model Smoke Test", "One concise governed connectivity response.", "MODEL_SMOKE_TEST", "You are a governed connectivity check. Reply with one short sentence only. Do not execute actions, request secrets, or claim remediation.", "Reply with one short sentence confirming governed model reachability: {input}", {"input": "object"}, {"answer": "string"}),
]

RULES = [
    ("RULE-BLOCK-API-KEY", "Block API key disclosure", "Block obvious API key markers.", "BLOCK_SECRET_DISCLOSURE", "HIGH", "sk-", "BLOCK"),
    ("RULE-BLOCK-PASSWORD", "Block raw passwords", "Block password assignments in invocation text.", "BLOCK_RAW_CREDENTIALS", "CRITICAL", "password=", "BLOCK"),
    ("RULE-BLOCK-AUTO-CLOSE-TICKET", "Block automatic ticket closure", "Prevent autonomous ticket closure requests.", "BLOCK_DESTRUCTIVE_AUTOMATION", "HIGH", "automatically close ticket", "BLOCK"),
    ("RULE-BLOCK-AUTO-CLOSE-TICKET-ALT", "Block auto-close wording", "Prevent abbreviated autonomous ticket closure requests.", "BLOCK_DESTRUCTIVE_AUTOMATION", "HIGH", "auto close ticket", "BLOCK"),
    ("RULE-BLOCK-AUTO-DELETE-DATA", "Block production data deletion", "Prevent destructive production data requests.", "BLOCK_DESTRUCTIVE_AUTOMATION", "CRITICAL", "delete production data", "BLOCK"),
    ("RULE-BLOCK-EXTERNAL-SEND", "Block external message sending", "Prevent external email or Slack sends from a model request.", "BLOCK_EXTERNAL_ACTION", "HIGH", "send external email", "BLOCK"),
    ("RULE-WARN-LOW-CONFIDENCE", "Warn on low confidence", "Flag low-confidence language for human review.", "WARN_LOW_CONFIDENCE", "MEDIUM", "low confidence", "WARN"),
]


def seed() -> None:
    manager = DatabaseManager(get_settings())
    manager.initialize()
    assert manager.session_factory is not None
    with manager.session_factory() as db:
        for code, name, provider_type, description, base_url, auth_type, enabled, is_mock in PROVIDERS:
            row = db.scalar(select(AiProvider).where(AiProvider.provider_code == code))
            if row is None:
                row = AiProvider(provider_code=code, name=name, provider_type=provider_type, description=description, base_url=base_url, auth_type=auth_type, enabled=enabled, is_mock=is_mock, default_timeout_seconds=30)
                db.add(row)
            else:
                row.name, row.provider_type, row.description, row.base_url, row.auth_type, row.enabled, row.is_mock = name, provider_type, description, base_url, auth_type, enabled, is_mock
        db.flush()
        mock = db.scalar(select(AiProvider).where(AiProvider.provider_code == "MOCK_GOVERNED"))
        assert mock is not None
        model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == "MOCK-SUPPORT-COPILOT-001"))
        if model is None:
            db.add(AiModelConfig(model_code="MOCK-SUPPORT-COPILOT-001", provider_id=mock.id, display_name="Mock Support Copilot", model_name="mock-governed-v1", model_family="DETERMINISTIC", purpose="GENERAL_TEST", enabled=True, is_default=True, temperature=0, top_p=1, max_output_tokens=1000, context_window_tokens=8000, cost_per_1k_input_tokens=0, cost_per_1k_output_tokens=0))
        else:
            model.provider_id, model.enabled, model.is_default = mock.id, True, True
        real_provider = db.scalar(select(AiProvider).where(AiProvider.provider_code == "OPENAI_RESPONSES"))
        assert real_provider is not None
        real_model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == "OPENAI_GPT_5_4_MINI"))
        if real_model is None:
            db.add(AiModelConfig(model_code="OPENAI_GPT_5_4_MINI", provider_id=real_provider.id, display_name="GPT-5.4 Mini (Governed, Disabled)", model_name="gpt-5.4-mini", model_family="OPENAI_RESPONSES", purpose="AGENT_STAGE_1_GUIDANCE", enabled=False, is_default=False, temperature=0, top_p=1, max_output_tokens=1200, context_window_tokens=128000, cost_per_1k_input_tokens=0, cost_per_1k_output_tokens=0))
        else:
            real_model.provider_id, real_model.model_name, real_model.enabled, real_model.is_default = real_provider.id, "gpt-5.4-mini", False, False
        for code, name, description, task_type, system_template, user_template, input_schema, output_schema in TEMPLATES:
            row = db.scalar(select(AiPromptTemplate).where(AiPromptTemplate.template_code == code, AiPromptTemplate.template_version == 1))
            if row is None:
                db.add(AiPromptTemplate(template_code=code, name=name, description=description, task_type=task_type, template_version=1, system_template=system_template, user_template=user_template, input_schema=input_schema, output_schema=output_schema, enabled=True, is_default=code == "TPL-GENERAL-TEST"))
            else:
                row.name, row.description, row.task_type, row.system_template, row.user_template, row.enabled = name, description, task_type, system_template, user_template, True
        policy = db.scalar(select(AiSafetyPolicy).where(AiSafetyPolicy.policy_code == "POL-COPILOT-GOVERNANCE"))
        if policy is None:
            policy = AiSafetyPolicy(policy_code="POL-COPILOT-GOVERNANCE", name="Copilot Governance", description="Deterministic safety controls for governed AI invocations.", policy_scope="GENERAL_INVOCATION", enabled=True, blocking_mode="BLOCK")
            db.add(policy); db.flush()
        for code, name, description, rule_type, severity, pattern, action in RULES:
            row = db.scalar(select(AiSafetyPolicyRule).where(AiSafetyPolicyRule.policy_id == policy.id, AiSafetyPolicyRule.rule_code == code))
            if row is None:
                db.add(AiSafetyPolicyRule(policy_id=policy.id, rule_code=code, name=name, description=description, rule_type=rule_type, severity=severity, enabled=True, match_pattern=pattern, action=action))
            else:
                row.name, row.description, row.rule_type, row.severity, row.enabled, row.match_pattern, row.action = name, description, rule_type, severity, True, pattern, action
        db.commit()
        print(f"AI config seed complete: providers={db.query(AiProvider).count()}, models={db.query(AiModelConfig).count()}, templates={db.query(AiPromptTemplate).count()}, policies={db.query(AiSafetyPolicy).count()}, rules={db.query(AiSafetyPolicyRule).count()}")
    manager.dispose()


if __name__ == "__main__":
    seed()
