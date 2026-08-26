import pytest


@pytest.mark.anyio
async def test_openai_costing_catalog_can_add_and_archive_model(warehouse_client):
    payload = {
        "model_code": "OPENAI_DYNAMIC_TEST",
        "external_model_name": "gpt-dynamic-test",
        "display_name": "Dynamic Test Model",
        "input_cost_per_million_tokens": 1.25,
        "completion_cost_per_million_tokens": 2.5,
        "pricing_source_note": "Local test assumption",
        "pricing_effective_from": "2026-08-26",
    }
    created = await warehouse_client.post("/api/v1/ai-costing/models", json=payload)
    assert created.status_code == 201
    assert created.json()["model_code"] == "OPENAI_DYNAMIC_TEST"
    assert created.json()["catalog_active"] is True

    duplicate = await warehouse_client.post("/api/v1/ai-costing/models", json=payload)
    assert duplicate.status_code == 409

    archived = await warehouse_client.delete("/api/v1/ai-costing/models/OPENAI_DYNAMIC_TEST")
    assert archived.status_code == 200
    assert archived.json()["deletion_mode"] == "ARCHIVED"
    assert archived.json()["historical_pricing_preserved"] is True

    active = await warehouse_client.get("/api/v1/ai-costing/models")
    assert all(row["model_code"] != "OPENAI_DYNAMIC_TEST" for row in active.json())
    inactive = await warehouse_client.get("/api/v1/ai-costing/models?include_inactive=true")
    archived_row = next(row for row in inactive.json() if row["model_code"] == "OPENAI_DYNAMIC_TEST")
    assert archived_row["catalog_active"] is False


@pytest.mark.anyio
async def test_openai_costing_pricing_rejects_negative_values(warehouse_client):
    response = await warehouse_client.put(
        "/api/v1/ai-costing/models/DISABLED-EXTERNAL-001/pricing",
        json={"input_cost_per_million_tokens": -1, "completion_cost_per_million_tokens": 1, "pricing_effective_from": "2026-08-26"},
    )
    assert response.status_code == 422
