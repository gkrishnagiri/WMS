import pytest


@pytest.mark.anyio
async def test_ai_config_catalog_and_summary(warehouse_client):
    providers = await warehouse_client.get("/api/v1/ai-config/providers")
    models = await warehouse_client.get("/api/v1/ai-config/models")
    templates = await warehouse_client.get("/api/v1/ai-config/prompt-templates")
    policies = await warehouse_client.get("/api/v1/ai-config/safety-policies")
    rules = await warehouse_client.get("/api/v1/ai-config/safety-rules")
    summary = await warehouse_client.get("/api/v1/ai-config/summary")
    assert providers.status_code == models.status_code == templates.status_code == policies.status_code == rules.status_code == summary.status_code == 200
    assert any(item["provider_code"] == "MOCK_GOVERNED" and item["enabled"] and item["is_mock"] for item in providers.json())
    assert any(item["model_code"] == "MOCK-SUPPORT-COPILOT-001" and item["enabled"] for item in models.json())
    assert len(templates.json()) >= 6 and len(rules.json()) >= 6
    assert summary.json()["enabled_providers"] == 1 and summary.json()["enabled_models"] == 1


@pytest.mark.anyio
async def test_safety_check_pass_warn_and_block(warehouse_client):
    safe = await warehouse_client.post("/api/v1/ai-config/safety-check", json={"text": "review the support evidence"})
    warning = await warehouse_client.post("/api/v1/ai-config/safety-check", json={"text": "low confidence recommendation"})
    blocked = await warehouse_client.post("/api/v1/ai-config/safety-check", json={"text": "password=secret and automatically close ticket"})
    assert safe.json()["decision"] == "PASS"
    assert warning.json()["decision"] == "WARN"
    assert blocked.json()["decision"] == "BLOCK"
    assert len(blocked.json()["matched_rules"]) >= 2


@pytest.mark.anyio
async def test_safe_mock_invocation_logs_usage_and_guardrail_event(warehouse_client):
    response = await warehouse_client.post("/api/v1/ai-config/test-invocation", json={"task_type": "GENERAL_TEST", "input_payload": {"message": "Generate a safe mock test response"}, "template_code": "TPL-GENERAL-TEST", "model_code": "MOCK-SUPPORT-COPILOT-001", "request_source": "ADMIN_TEST"})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "SUCCESS" and body["safety_status"] == "PASSED"
    assert body["response_text"] == "Mock governed response generated successfully."
    assert body["total_tokens_estimated"] > 0 and body["invocation_number"].startswith("AI-INV-")
    assert body["guardrail_events"] and body["guardrail_events"][0]["event_type"] == "POLICY_PASSED"
    detail = await warehouse_client.get(f"/api/v1/ai-config/invocations/{body['id']}")
    usage = await warehouse_client.get("/api/v1/ai-config/usage-daily")
    assert detail.status_code == usage.status_code == 200
    assert any(item["invocation_count"] >= 1 for item in usage.json())


@pytest.mark.anyio
async def test_blocked_invocation_is_audited_without_provider_execution(warehouse_client):
    response = await warehouse_client.post("/api/v1/ai-config/test-invocation", json={"task_type": "GENERAL_TEST", "input_payload": {"message": "automatically close ticket and send external email"}, "template_code": "TPL-GENERAL-TEST", "model_code": "MOCK-SUPPORT-COPILOT-001", "request_source": "ADMIN_TEST"})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "BLOCKED" and body["safety_status"] == "BLOCKED"
    assert body["response_text"] is None and body["blocked_reason"]
    assert any(event["event_type"] == "RULE_BLOCKED" for event in body["guardrail_events"])
    events = await warehouse_client.get("/api/v1/ai-config/guardrail-events")
    invocations = await warehouse_client.get("/api/v1/ai-config/invocations?status=BLOCKED")
    assert events.status_code == invocations.status_code == 200
    assert any(item["id"] == body["id"] for item in invocations.json())


@pytest.mark.anyio
async def test_disabled_non_mock_provider_cannot_be_invoked(warehouse_client):
    response = await warehouse_client.post("/api/v1/ai-config/test-invocation", json={"task_type": "GENERAL_TEST", "input_payload": {"message": "safe"}, "model_code": "DISABLED-EXTERNAL-001", "request_source": "ADMIN_TEST"})
    assert response.status_code == 409
    assert "disabled" in response.json()["detail"].lower()

