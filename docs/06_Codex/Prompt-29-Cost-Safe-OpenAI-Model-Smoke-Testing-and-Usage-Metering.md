# Prompt 29 – Cost-Safe OpenAI Model Smoke Testing and Usage Metering

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 20 added governed real model provider foundation.

Prompt 24 added governed Stage 1 real-model chat activation, disabled by default.

Prompt 27 added demo readiness and showcase mode.

Prompt 28 added UI acceptance testing and evidence capture.

Your task now is to implement:

```text
Cost-Safe OpenAI Model Smoke Testing and Usage Metering
```

---

## Business Goal

The platform can now support governed real-model calls, but before repeated real-model testing, the user needs full visibility and control over:

```text
which OpenAI model is used
whether real calls are enabled
how many calls were made
input tokens consumed
completion/output tokens consumed
total tokens consumed
estimated runtime cost
per-model pricing assumptions
daily/monthly cost summaries
cost guardrails
auditability
```

The user wants the Agentic UI to support selecting the OpenAI model and updating per-million-token prices manually.

This prompt should introduce a cost-safe real-model validation layer before broader real model usage.

---

## Critical Scope

Prompt 29 implements:

```text
OpenAI-only model catalog
model selection UI
editable input/output cost per million tokens
cost estimate configuration
runtime token usage capture
runtime cost calculation
usage dashboard
cost guardrails
one-shot smoke test workflow
model availability/status validation
invocation cost audit
Agentic UI cost visibility
```

Prompt 29 must not implement:

```text
autonomous remediation
fully autonomous model execution
unbounded chat loops
background model polling
ServiceNow integration
customer communication sends
shell command execution
arbitrary SQL execution
authentication / authorization
multi-provider marketplace
```

This prompt is **not** Stage 3 autonomous remediation.

It is a controlled cost-safe foundation for real OpenAI model calls.

---

## OpenAI API Direction

Use the existing Prompt 20/24 OpenAI provider gateway.

Do not bypass:

```text
ai_provider_gateway
ai_invocation_logs
guardrail checks
model governance settings
```

OpenAI model calls must remain disabled unless explicitly enabled and requested.

The implementation should continue using environment-based API keys. Do not store API keys in the database or UI.

---

## Current Baseline

Current ports and URLs must remain unchanged.

## Backend/BFFs

```text
Full backend               http://localhost:8050
Business BFF               http://localhost:8061
Operations BFF             http://localhost:8062
Simulation Lab BFF         http://localhost:8063
Observability Control BFF  http://localhost:8064
Agentic Support BFF        http://localhost:8065
```

## Frontends

```text
Full UI                    http://localhost:4001
Business UI                http://localhost:4011
Operations UI              http://localhost:4012
Simulation Lab UI          http://localhost:4013
Observability UI           http://localhost:4014
Agentic UI                 http://localhost:4015
```

Do not break existing Prompt 13–28 behavior.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve deterministic/mock behavior as the default.

You must not enable real model calls by default.

You must not require an OpenAI API key for tests, seed, build, startup, or demo validation.

You must not call an external LLM in tests.

You must not call an external model unless explicitly requested and all governance checks pass.

You must not execute shell commands from backend APIs.

You must not execute arbitrary SQL from backend APIs.

You must not execute arbitrary user-provided code.

You must not introduce autonomous remediation.

You must not integrate with ServiceNow.

You must not send customer communications externally.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

All model-cost values must be presented as:

```text
estimated
based on configured local pricing assumptions
not an OpenAI invoice
```

---

## Files You May Modify

You may modify:

```text
backend/
frontend/
scripts/
README.md
ARCHITECTURE.md
docs/06_Codex/
```

Avoid modifying:

```text
docker-compose.yml
observability/
```

Do not modify local runtime files:

```text
backend/.env
backend/.venv/
frontend/.env
frontend/node_modules/
frontend/dist/
```

---

# Target Capability

Implement OpenAI model usage and cost metering.

The platform should support:

```text
OpenAI model catalog
editable per-model pricing
input token cost per million tokens
completion/output token cost per million tokens
model selection for governed smoke tests
model selection for Stage 1 model chat
usage capture per invocation
runtime cost calculation
usage summaries by model/provider/task/date
cost guardrails
Agentic UI usage dashboard
one-shot real model smoke test
disabled/fallback behavior when not configured
```

---

# Terminology

Use these terms consistently:

```text
input_tokens
completion_tokens
total_tokens
input_cost_per_million_tokens
completion_cost_per_million_tokens
estimated_input_cost
estimated_completion_cost
estimated_total_cost
pricing_effective_from
pricing_source_note
```

For OpenAI Responses API usage, if returned field names differ, normalize into the EOS fields above.

---

# Data Model

Add migration:

```text
0019_openai_model_cost_metering
```

Create or extend tables as needed.

## Recommended table: ai_model_pricing

Fields:

```text
id
pricing_id
provider_code
model_code
external_model_name
currency
input_cost_per_million_tokens
completion_cost_per_million_tokens
cached_input_cost_per_million_tokens
reasoning_cost_per_million_tokens
pricing_source_note
pricing_effective_from
is_active
created_at
updated_at
```

Rules:

```text
provider_code must be OPENAI_RESPONSES for this prompt
currency default USD
input/completion prices editable
cached/reasoning prices optional
pricing_source_note editable
do not hardcode prices as authoritative forever
```

## Recommended table: ai_model_usage_metering

Fields:

```text
id
usage_id
invocation_id
provider_code
model_code
external_model_name
task_type
request_source
session_id
case_id
input_tokens
completion_tokens
total_tokens
cached_input_tokens
reasoning_tokens
estimated_input_cost
estimated_completion_cost
estimated_cached_input_cost
estimated_reasoning_cost
estimated_total_cost
currency
pricing_id
pricing_snapshot_json
usage_source
created_at
```

Usage source values:

```text
PROVIDER_REPORTED
ESTIMATED
UNAVAILABLE
```

If existing `ai_invocation_logs` already stores token counts, keep it, but add this metering table for cost snapshots.

Reason:

```text
pricing can change later, but historical invocations must retain the pricing snapshot used at the time of call.
```

---

# Seed Data

Update or create:

```text
backend/app/db/seed_ai_model_pricing.py
```

Seed OpenAI model pricing rows idempotently.

Seed model entries for current local demo selection, for example:

```text
OPENAI_GPT_5_4_MINI
OPENAI_GPT_5_4
OPENAI_GPT_5_MINI
OPENAI_GPT_5
```

Do not assume every model is available to the user.

Each seeded row should include:

```text
is_active=true
pricing_source_note="User-editable placeholder. Verify against current OpenAI pricing before real use."
```

Prices may be initialized to placeholder values such as 0.0 if necessary, but the UI must clearly warn that pricing should be updated before relying on estimated cost.

Preferred:

```text
seed editable placeholder rows
do not claim pricing is current unless manually updated
```

Add the seed to validation instructions.

---

# Model Catalog Behavior

OpenAI model catalog should be visible and editable in the Agentic UI.

Backend should expose:

```text
model_code
external_model_name
provider_code
enabled
supports_real_invocation
pricing configured yes/no
input cost per million
completion cost per million
last updated
```

Model availability and model configuration are separate:

```text
configured in EOS catalog
enabled in EOS governance
available in OpenAI account
```

Do not imply availability until an explicit status/test confirms it.

---

# Cost Calculation Formula

Use:

```text
estimated_input_cost =
  input_tokens * input_cost_per_million_tokens / 1000000
```

```text
estimated_completion_cost =
  completion_tokens * completion_cost_per_million_tokens / 1000000
```

```text
estimated_total_cost =
  estimated_input_cost
  + estimated_completion_cost
  + optional cached/reasoning estimates if present
```

If token counts are unavailable:

```text
estimated_total_cost = null
usage_source = UNAVAILABLE
```

If pricing is missing:

```text
estimated_total_cost = null
pricing_status = MISSING_PRICING
```

If pricing is zero placeholder:

```text
estimated_total_cost = 0
pricing_status = PLACEHOLDER_OR_ZERO
show warning in UI
```

---

# Backend Service

Create service:

```text
backend/app/services/ai_model_cost_service.py
```

Responsibilities:

```text
list OpenAI model catalog
get/update model pricing
validate model pricing
record usage metering from invocation logs
calculate invocation cost
aggregate usage by date/model/task/provider
enforce cost guardrails
return dashboard summaries
```

Extend:

```text
agent_model_chat_service
ai_provider_gateway
ai_config routes
```

so that every real-model attempt can create or update usage metering.

---

# Cost Guardrails

Add conservative configurable guardrails.

Environment variables:

```text
REAL_MODEL_MAX_SINGLE_CALL_ESTIMATED_COST=1.00
REAL_MODEL_MAX_DAILY_ESTIMATED_COST=10.00
REAL_MODEL_MAX_DAILY_INVOCATIONS=100
REAL_MODEL_MAX_INPUT_TOKENS=32000
REAL_MODEL_MAX_OUTPUT_TOKENS=1200
```

Defaults must be conservative.

If estimated cost cannot be calculated because pricing is missing:

```text
allow only dry-run
block real call unless allow_missing_pricing=true is explicitly supplied
```

For smoke tests:

```text
default max_output_tokens <= 300
default task type = MODEL_SMOKE_TEST
default context minimal
```

---

# Backend APIs

Add route prefix:

```text
/api/v1/ai-costing
```

Expose on:

```text
Full backend 8050
Agentic BFF 8065
Operations BFF 8062 read-only plus smoke-test if justified
```

Do not expose mutation endpoints on:

```text
Business BFF 8061
Simulation BFF 8063
Observability BFF 8064
```

Business may expose read-only summary if useful, but no model smoke test or pricing mutation.

---

## Required endpoints

Read-only:

```text
GET  /api/v1/ai-costing/summary
GET  /api/v1/ai-costing/models
GET  /api/v1/ai-costing/models/{model_code}
GET  /api/v1/ai-costing/usage
GET  /api/v1/ai-costing/usage/by-model
GET  /api/v1/ai-costing/usage/by-day
GET  /api/v1/ai-costing/invocations/{invocation_id}/cost
GET  /api/v1/ai-costing/guardrails
```

Mutation:

```text
PUT  /api/v1/ai-costing/models/{model_code}/pricing
POST /api/v1/ai-costing/smoke-test/dry-run
POST /api/v1/ai-costing/smoke-test/run
```

---

## Pricing update request

```json
{
  "currency": "USD",
  "input_cost_per_million_tokens": 0.0,
  "completion_cost_per_million_tokens": 0.0,
  "cached_input_cost_per_million_tokens": null,
  "reasoning_cost_per_million_tokens": null,
  "pricing_source_note": "Manually updated from OpenAI pricing page on YYYY-MM-DD.",
  "pricing_effective_from": "2026-08-26"
}
```

Rules:

```text
no negative prices
currency required
source note recommended
update preserves history if possible
current active pricing used for future invocations
usage records store snapshot
```

---

## Smoke test dry-run

```json
{
  "model_code": "OPENAI_GPT_5_4_MINI",
  "message_text": "Reply with one short sentence confirming the model is reachable.",
  "max_output_tokens": 100,
  "allow_real_model": false
}
```

Must:

```text
validate provider readiness
validate model enabled
validate API key presence
validate pricing configured
estimate maximum cost if possible
not call the model
return reasons if blocked
```

---

## Smoke test run

```json
{
  "model_code": "OPENAI_GPT_5_4_MINI",
  "message_text": "Reply with one short sentence confirming the model is reachable.",
  "max_output_tokens": 100,
  "allow_real_model": true,
  "acknowledge_cost": true
}
```

Must call real model only if:

```text
REAL_MODEL_ENABLED=true
OPENAI_API_KEY present
provider enabled
model enabled
pricing configured or explicitly allowed
guardrails pass
allow_real_model=true
acknowledge_cost=true
safety checks pass
```

Must:

```text
record invocation
record usage metering
capture input/completion/total tokens if provider returns them
calculate estimated cost
return concise result
```

Must not:

```text
start agent action
approve action
execute action
call ServiceNow
send customer communication
```

---

# Agent Chat Model Selection

Update model-assisted chat controls from Prompt 24.

In Agentic UI and Full UI, allow user to select:

```text
OpenAI model
```

from enabled OpenAI catalog.

For each model show:

```text
model name
enabled status
pricing status
input cost per million
completion cost per million
estimated cost warning
```

Default remains deterministic/fallback.

Real-model toggle remains off by default.

When a real model is selected for ask:

```text
include model_code in request
display estimated cost after response
display actual input/completion/total tokens if available
display invocation ID
```

---

# Agentic UI Cost Dashboard

Create or extend UI under Agentic experience.

Routes:

```text
/ai-costing
/ai-costing/models
/ai-costing/usage
/ai-costing/smoke-test
```

Visible in:

```text
Full UI
Agentic UI
```

Operations UI may show read-only costing summary.

Business UI should not expose pricing mutation or smoke test.

---

## AI Costing Summary Page

Show:

```text
real model enabled status
API key present yes/no
provider enabled
active model count
pricing configured count
total invocations
total input tokens
total completion tokens
total tokens
estimated total cost
cost today
cost by model
latest invocations
guardrail status
```

---

## Model Pricing Page

Show editable table:

```text
model code
external model name
enabled
input cost per million tokens
completion cost per million tokens
currency
pricing note
effective date
last updated
```

Allow update for:

```text
input cost
completion cost
cached input cost optional
reasoning cost optional
currency
source note
effective date
```

Warn:

```text
These prices are local EOS cost assumptions. Update them whenever OpenAI pricing changes.
```

---

## Usage Page

Show:

```text
usage by model
usage by day
invocation list
task type
request source
input tokens
completion tokens
total tokens
estimated cost
fallback used
status
```

---

## Smoke Test Page

Show:

```text
model selector
provider readiness
pricing readiness
estimated maximum cost
dry run button
run one-shot smoke test button
cost acknowledgement checkbox
latest smoke test result
tokens used
estimated cost
invocation ID
```

Real smoke test run button must be disabled unless:

```text
real model enabled
API key present
provider/model enabled
pricing configured
cost acknowledgement checked
```

---

# Usage Capture

Extend provider gateway response normalization to capture:

```text
provider usage object
input_tokens
completion_tokens
total_tokens
cached_input_tokens if available
reasoning_tokens if available
external_request_id
latency_ms
```

If provider returns usage in a different shape, map best effort.

If unavailable, record:

```text
usage_source=UNAVAILABLE
```

---

# Demo Readiness Integration

Update demo readiness to include:

```text
AI Costing Model Catalog
AI Costing Pricing Config
AI Usage Metering
Cost Guardrails
Real Model Smoke Test Controls
```

Readiness must not run smoke tests.

---

# UI Acceptance Integration

Update UI acceptance test catalog to include new suite:

```text
AI_COSTING_AND_SMOKE_TEST_VALIDATION
```

Steps:

```text
Open AI Costing dashboard
Verify real model disabled/default status
Open model pricing table
Update placeholder pricing for a test model if allowed
Open smoke test page
Run dry-run only
Verify real smoke test button is disabled unless prerequisites are met
Verify no model call occurs by default
Verify usage dashboard loads
```

Do not require actual real model call.

---

# Scripts

Add scripts:

```text
scripts/ai-costing-summary.sh
scripts/ai-costing-smoke-dry-run.sh
```

Optional:

```text
scripts/ai-costing-smoke-run.sh
```

If adding smoke-run script, it must require explicit confirmation argument:

```bash
./scripts/ai-costing-smoke-run.sh --confirm-real-model-call
```

Without confirmation, it must refuse.

---

# Tests

Add backend tests for:

```text
model pricing seed idempotency
costing summary endpoint
list models endpoint
update pricing endpoint
reject negative pricing
usage summary endpoint
guardrails endpoint
smoke dry-run does not call model
smoke run blocked by default
smoke run blocked without API key
smoke run blocked without pricing unless explicitly allowed
mocked smoke run records usage metering
mocked smoke run calculates cost from input/completion tokens
usage record stores pricing snapshot
agent model chat records usage metering when mocked provider returns usage
BFF exposure rules
Business BFF mutation blocked
demo readiness includes AI costing checks
UI acceptance includes AI costing suite
no OpenAI API key required
no external model call required in tests
```

Existing tests must continue to pass.

Tests must not require:

```text
OpenAI API key
external model call
Prometheus/Grafana/Tempo/Loki
ServiceNow
browser automation
```

---

# Validation Commands

## Start stack

```bash
cd ~/giri/AIProjects/WMS

./scripts/start-demo-stack.sh
./scripts/status-demo-stack.sh
./scripts/validate-demo-stack.sh
```

## Backend validation

```bash
cd ~/giri/AIProjects/WMS/backend

source .venv/bin/activate

alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
python -m app.db.seed_batch
python -m app.db.seed_copilot
python -m app.db.seed_ai_config
python -m app.db.seed_observability_alerts
python -m app.db.seed_agent_knowledge
python -m app.db.seed_demo_scenarios
python -m app.db.seed_ui_acceptance_tests
python -m app.db.seed_ai_model_pricing

pytest
```

## Frontend validation

```bash
cd ~/giri/AIProjects/WMS/frontend

npm install
npm run build
```

---

# Manual API Validation

## Costing summary

```bash
curl -sS http://localhost:8050/api/v1/ai-costing/summary | jq .
curl -sS http://localhost:8050/api/v1/ai-costing/models | jq .
curl -sS http://localhost:8050/api/v1/ai-costing/usage | jq .
curl -sS http://localhost:8050/api/v1/ai-costing/guardrails | jq .
```

## Update model pricing

```bash
curl -sS -X PUT http://localhost:8050/api/v1/ai-costing/models/OPENAI_GPT_5_4_MINI/pricing \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "USD",
    "input_cost_per_million_tokens": 0.0,
    "completion_cost_per_million_tokens": 0.0,
    "cached_input_cost_per_million_tokens": null,
    "reasoning_cost_per_million_tokens": null,
    "pricing_source_note": "Manual placeholder for local Prompt 29 validation. Update before real use.",
    "pricing_effective_from": "2026-08-26"
  }' | jq .
```

Expected:

```text
pricing updated
marked as local/manual assumption
no model call
```

## Dry-run smoke test

```bash
curl -sS -X POST http://localhost:8050/api/v1/ai-costing/smoke-test/dry-run \
  -H "Content-Type: application/json" \
  -d '{
    "model_code": "OPENAI_GPT_5_4_MINI",
    "message_text": "Reply with one short sentence confirming the model is reachable.",
    "max_output_tokens": 100,
    "allow_real_model": false
  }' | jq .
```

Expected:

```text
dry-run completed
no model call
shows readiness reasons
shows estimated maximum cost if pricing exists
```

## Smoke run blocked by default

```bash
curl -sS -X POST http://localhost:8050/api/v1/ai-costing/smoke-test/run \
  -H "Content-Type: application/json" \
  -d '{
    "model_code": "OPENAI_GPT_5_4_MINI",
    "message_text": "Reply with one short sentence confirming the model is reachable.",
    "max_output_tokens": 100,
    "allow_real_model": true,
    "acknowledge_cost": true
  }' | jq .
```

Expected by default:

```text
blocked or fallback because REAL_MODEL_ENABLED=false and/or API key missing
no external call
audit record if implemented
```

## BFF validation

```bash
curl -sS http://localhost:8065/api/v1/ai-costing/summary | jq .
curl -sS http://localhost:8062/api/v1/ai-costing/summary | jq .

curl -i -sS -X PUT http://localhost:8061/api/v1/ai-costing/models/OPENAI_GPT_5_4_MINI/pricing \
  -H "Content-Type: application/json" \
  -d '{}' | head

curl -i -sS http://localhost:8063/api/v1/ai-costing/summary | head
curl -i -sS http://localhost:8064/api/v1/ai-costing/summary | head
```

Expected:

```text
Agentic BFF: works
Operations BFF: read-only works if exposed
Business BFF mutation blocked/404
Simulation BFF not exposed or read-only only if intentionally implemented
Observability BFF 404
```

---

# Optional Real Model Smoke Test

Do not require this for Definition of Done.

Only run manually if the user explicitly wants to spend credits.

Before running:

```text
verify pricing assumptions
verify REAL_MODEL_ENABLED=true
verify OPENAI_API_KEY present
verify provider enabled
verify model enabled
verify max_output_tokens is low
verify cost acknowledgement checked
```

Recommended one-shot only.

Do not run from tests.

Do not run repeatedly.

---

# Manual UI Validation

Open:

```text
http://localhost:4015/ai-costing
http://localhost:4015/ai-costing/models
http://localhost:4015/ai-costing/usage
http://localhost:4015/ai-costing/smoke-test
```

Also check Full UI:

```text
http://localhost:4001/ai-costing
```

Validate:

```text
cost dashboard loads
OpenAI model catalog visible
model selector visible
pricing fields editable
input cost per million editable
completion cost per million editable
pricing note editable
usage dashboard visible
dry-run smoke test works
real smoke test disabled by default
cost acknowledgement required
estimated cost visible
token fields visible
no API key field exists
no autonomous remediation controls exist
```

In Agent Investigation Workspace:

```text
open model-assisted chat panel
verify model dropdown appears
select OpenAI model
verify pricing/cost warning appears
ask deterministic/default question
verify no real model call by default
```

---

# Documentation Updates

Update `README.md` with:

```text
AI costing overview
OpenAI-only model catalog
how to update pricing
how cost is estimated
how tokens are captured
how to run dry-run smoke test
how to optionally run one real smoke test
credit/cost warning
```

Update `ARCHITECTURE.md` with:

```text
AI model costing architecture
pricing table
usage metering table
provider usage normalization
cost snapshot design
guardrail design
Agentic UI costing workflow
relationship to model chat and invocation audit
```

Document clearly:

```text
Prompt 29 adds OpenAI model costing and smoke-test controls.
It does not enable real model calls by default.
It does not add autonomous remediation.
It does not execute shell commands.
It does not integrate with ServiceNow.
Estimated cost is based on local pricing assumptions, not an invoice.
```

---

# Definition of Done

Prompt 29 is complete only when:

- OpenAI model pricing table exists
- usage metering table exists
- pricing seed exists
- model pricing can be viewed
- model pricing can be updated
- negative pricing is rejected
- invocation usage can be recorded
- input tokens are tracked
- completion tokens are tracked
- total tokens are tracked
- estimated cost is calculated
- pricing snapshot is stored per usage record
- costing summary endpoint works
- usage endpoints work
- guardrails endpoint works
- smoke dry-run works without model call
- smoke run is blocked by default
- mocked smoke run records token usage and cost
- agent model chat records usage when provider returns tokens
- Agentic UI has costing dashboard
- Agentic UI has model pricing page
- Agentic UI has usage page
- Agentic UI has smoke-test page
- model-assisted chat supports model selection
- demo readiness includes costing checks
- UI acceptance includes costing validation suite
- scripts exist and work
- backend tests pass
- frontend build passes
- demo stack validation passes
- no OpenAI API key is required
- no default external model call occurs
- no autonomous remediation is introduced
- no shell commands are executed from APIs
- no arbitrary SQL execution is introduced
- no ServiceNow integration is introduced
- no authentication is introduced
- no Docker Compose change unless justified
- no observability infrastructure change unless justified
- README updated
- ARCHITECTURE.md updated
- Prompt 29 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary
4. OpenAI model catalog summary
5. Pricing update behavior
6. Usage metering behavior
7. Token capture behavior
8. Cost calculation behavior
9. Cost guardrail behavior
10. Smoke dry-run behavior
11. Smoke run behavior
12. Agent chat model selection behavior
13. Backend APIs added
14. BFF exposure summary
15. Frontend routes/pages added
16. Demo readiness integration summary
17. UI acceptance integration summary
18. Scripts added
19. Backend test results
20. Frontend build results
21. Demo stack validation results
22. Manual API validation results
23. Script validation results
24. Manual UI validation results
25. Confirmation deterministic/mock remains default
26. Confirmation no real model call occurs by default
27. Confirmation no autonomous remediation was introduced
28. Confirmation no shell command/arbitrary SQL/external system execution was introduced
29. Confirmation no ServiceNow/authentication was introduced
30. TODOs or limitations
31. Recommended Git commit message

Recommended commit message:

```text
feat: add ai model costing and smoke tests
```

Do not proceed beyond this prompt.