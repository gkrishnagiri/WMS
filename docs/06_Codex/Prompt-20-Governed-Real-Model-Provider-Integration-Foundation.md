# Prompt 20 – Governed Real Model Provider Integration Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 18 added agent chat and case intake.

Prompt 19 added deterministic knowledge retrieval and RAG foundation.

Your task now is to implement:

```text
Governed Real Model Provider Integration Foundation
```

---

## Business Goal

The platform should now be ready to use a real LLM provider for agentic support workflows, but only under explicit governance controls.

The goal is to move from:

```text
deterministic mock-only responses
```

toward:

```text
governed optional real-model responses
```

while preserving:

```text
safety
auditability
cost controls
prompt governance
provider abstraction
mock-first default behavior
no autonomous remediation
```

This prompt should create the real-model integration foundation, not enable unrestricted agent autonomy.

---

## Critical Safety Position

The current default must remain:

```text
MOCK_GOVERNED
DETERMINISTIC_STAGE_1
No external LLM call unless explicitly enabled
No action execution
No autonomous remediation
```

Real model invocation must require all of the following:

```text
provider enabled
model enabled
real-model feature flag enabled
API key available in environment
safety policy passed
request source allowed
explicit API call path
```

Tests must not require a real OpenAI API key.

Tests must not call any external model.

---

## Intended Model Direction

Add support for an OpenAI-compatible real provider using the OpenAI Responses API style.

Recommended candidate model configuration:

```text
gpt-5.4-mini
```

But do not hardcode this as the only option.

The model name must remain configurable in the governed AI model configuration table.

The implementation should allow future models such as:

```text
gpt-5.4-mini
gpt-5.4
gpt-5.1
gpt-5-mini
other OpenAI-compatible configured model names
```

Do not assume all models are available in the local environment.

If the configured model is unavailable or the API call fails, return a governed failure response and keep audit logs.

---

## Current Baseline

The current system includes:

## Infrastructure

```text
PostgreSQL                 localhost:15432
Redis                      localhost:6379
OpenTelemetry Collector    localhost:4317 / 4318 / 8889 / 13133
Prometheus                 http://localhost:9090
Grafana                    http://localhost:3001
Tempo                      http://localhost:3200
Loki                       http://localhost:3100
```

## Backend/BFF processes

```text
Full backend               http://localhost:8050
Business BFF               http://localhost:8061
Operations BFF             http://localhost:8062
Simulation Lab BFF         http://localhost:8063
Observability Control BFF  http://localhost:8064
Agentic Support BFF        http://localhost:8065
```

## Frontend processes

```text
Full UI                    http://localhost:4001
Business UI                http://localhost:4011
Operations UI              http://localhost:4012
Simulation Lab UI          http://localhost:4013
Observability UI           http://localhost:4014
Agentic UI                 http://localhost:4015
```

Existing AI/agent foundation includes:

```text
governed AI config
mock provider
AI invocation logs
guardrail events
usage tracking
copilot governed mock drafts
agent chat
agent cases
deterministic Stage 1 orchestrator
knowledge/RAG foundation with deterministic retrieval
retrieval audit
```

Current backend test baseline:

```text
123 passed
```

Do not break existing functionality.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve all frontend and backend/BFF URLs.

You must preserve mock mode as the default.

You must not require an OpenAI API key for tests, local startup, seed, frontend build, or demo stack validation.

You must not store API keys in the database.

You must not write API keys to logs.

You must not modify local runtime files:

```text
backend/.env
frontend/.env
```

You may update:

```text
backend/.env.example
```

with placeholder variable names only.

You must not introduce autonomous remediation.

You must not execute shell commands from the model.

You must not allow the model to execute database-changing remediation actions.

You must not introduce ServiceNow integration.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

All real-model calls must be auditable.

All real-model calls must be optional.

All real-model calls must be disabled by default.

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

Implement governed real model provider support that includes:

```text
OpenAI-compatible provider adapter
environment-based API key handling
feature flags
provider health/test endpoint
model configuration
real invocation audit
safety pre-checks
response safety post-checks
cost/token tracking where available
agent chat optional real-model generation mode
fallback to deterministic guidance
UI controls for provider status and real-model test
documentation for safe enablement
```

---

# Dependency Policy

Add the minimum backend dependency needed for OpenAI API support.

Preferred:

```text
openai
```

Add it to:

```text
backend/requirements.txt
```

Do not add LangChain.

Do not add LlamaIndex.

Do not add vector DB dependencies.

Do not add agent frameworks.

Do not add browser automation or computer-use tools.

---

# Environment Variables

Add settings, but do not require them.

Suggested variables:

```text
REAL_MODEL_ENABLED=false
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_ORG_ID=
OPENAI_PROJECT_ID=
OPENAI_DEFAULT_MODEL=gpt-5.4-mini
OPENAI_REQUEST_TIMEOUT_SECONDS=30
OPENAI_MAX_OUTPUT_TOKENS=1200
OPENAI_REASONING_EFFORT=low
OPENAI_STORE_RESPONSES=false
```

Rules:

```text
REAL_MODEL_ENABLED=false by default
OPENAI_API_KEY must never be committed
OPENAI_API_KEY must be read only from environment
OPENAI_BASE_URL optional
OPENAI_ORG_ID optional
OPENAI_PROJECT_ID optional
OPENAI_STORE_RESPONSES=false by default
```

Update:

```text
backend/.env.example
README.md
ARCHITECTURE.md
```

Do not update:

```text
backend/.env
```

---

# Data Model

Use existing AI config and invocation tables where possible.

Add migration only if needed.

If current `ai_providers`, `ai_model_configs`, `ai_invocation_logs`, `ai_usage_daily`, and `ai_guardrail_events` are sufficient, do not create a migration.

If additional fields are needed, add migration:

```text
0015_governed_real_model_provider
```

Possible fields if needed:

```text
ai_providers.provider_kind
ai_providers.requires_api_key
ai_providers.api_key_env_var
ai_model_configs.external_model_name
ai_model_configs.supports_reasoning_effort
ai_model_configs.supports_structured_output
ai_model_configs.max_output_tokens
ai_invocation_logs.external_request_id
ai_invocation_logs.provider_latency_ms
ai_invocation_logs.prompt_token_count
ai_invocation_logs.completion_token_count
ai_invocation_logs.total_token_count
ai_invocation_logs.estimated_cost
ai_invocation_logs.fallback_used
```

Do not add secrets to the database.

---

# Seed Updates

Update:

```text
backend/app/db/seed_ai_config.py
```

Seed or update an OpenAI real provider entry.

Example provider:

```text
provider_code: OPENAI_RESPONSES
provider_name: OpenAI Responses API
provider_type: REAL_MODEL
enabled: false by default
requires_api_key: true
api_key_env_var: OPENAI_API_KEY
```

Seed or update model config:

```text
model_code: OPENAI_GPT_5_4_MINI
external_model_name: gpt-5.4-mini
provider_code: OPENAI_RESPONSES
enabled: false by default
use_case: AGENT_STAGE_1_GUIDANCE
```

Important:

```text
Mock provider remains enabled.
Real provider remains disabled by default.
Seed must be idempotent.
Seed must not require OPENAI_API_KEY.
```

---

# Provider Gateway

Update or extend:

```text
backend/app/services/ai_provider_gateway.py
```

Add provider adapter:

```text
OpenAIResponsesProvider
```

The gateway should support:

```text
mock provider invocation
OpenAI Responses API invocation
feature-flag validation
provider enabled validation
model enabled validation
environment key validation
timeout handling
error handling
audit logging
usage capture
fallback behavior
```

---

## Invocation Modes

Support these invocation modes:

```text
MOCK_GOVERNED
REAL_MODEL_DISABLED
REAL_MODEL_DRY_RUN
REAL_MODEL_OPENAI_RESPONSES
REAL_MODEL_FAILED
REAL_MODEL_BLOCKED
FALLBACK_DETERMINISTIC
```

Default behavior:

```text
MOCK_GOVERNED
```

If real model is requested but not enabled:

```text
REAL_MODEL_DISABLED
```

If real model is enabled but API key missing:

```text
REAL_MODEL_FAILED or REAL_MODEL_DISABLED
clear message
no external call attempted
audit log created
```

If real model fails:

```text
REAL_MODEL_FAILED
fallback_used = true
fallback deterministic response returned where appropriate
```

---

# Request/Response Contract

Create or update schemas to support real model request options.

Suggested request fields:

```text
provider_code
model_code
task_type
request_source
input_text
system_instruction
context_items
temperature
max_output_tokens
reasoning_effort
allow_real_model
dry_run
metadata
```

Rules:

```text
allow_real_model must be true to call a real model
dry_run must not call real provider
request_source must be logged
context_items must be logged safely or summarized
```

Suggested response fields:

```text
invocation_id
provider_code
model_code
generation_mode
status
safety_status
output_text
fallback_used
external_request_id
latency_ms
usage
guardrail_events
error_message
notes
```

---

# Prompt Governance

Real-model prompts must be constructed through governed prompt templates.

Add or update prompt templates for:

```text
AGENT_STAGE_1_GUIDANCE
AGENT_KNOWLEDGE_SUMMARY
AGENT_EVIDENCE_SUMMARY
CUSTOMER_FACING_ISSUE_GUIDANCE
SERVICE_ENGINEER_INVESTIGATION_GUIDANCE
```

Prompt must include clear boundaries:

```text
You are Stage 1 read-only.
Do not claim you executed any action.
Do not instruct the system to run shell commands.
Do not ask for secrets.
Do not provide autonomous remediation.
Use only provided context.
When uncertain, say what evidence is missing.
Return concise structured guidance.
```

---

# Safety Controls

Use existing AI safety policy where possible.

Before real model call:

```text
check input against safety rules
block disallowed content
block secrets / API keys / passwords if detected
block autonomous action requests
block external-send/customer-send instructions if not approved
```

After real model response:

```text
check response for forbidden claims
block if it says actions were executed
block if it asks for secrets
block if it proposes unsafe/unapproved destructive action
record guardrail events
```

For blocked outputs:

```text
do not return unsafe output as final answer
return safe fallback message
record invocation log
record guardrail event
```

---

# Agent Chat Integration

Update:

```text
backend/app/services/agent_orchestrator_service.py
```

Add optional real-model generation for Stage 1 guidance.

Rules:

```text
deterministic remains default
real model only used if explicitly requested/configured
agent case remains STAGE_1_READ_ONLY
actions_executed must remain 0
action proposals remain DISABLED_IN_STAGE_1
evidence retrieval remains deterministic
knowledge retrieval remains deterministic
model receives curated context from evidence + knowledge
model does not receive raw secrets
model output goes through safety post-check
fallback deterministic response if blocked/failed
```

Add fields to orchestration run or messages if needed:

```text
ai_invocation_id
generation_mode
model_code
provider_code
fallback_used
```

Existing message generation modes can be extended:

```text
REAL_MODEL_OPENAI_RESPONSES
REAL_MODEL_BLOCKED
REAL_MODEL_FAILED
FALLBACK_DETERMINISTIC
```

---

# Agent Chat API Updates

Extend existing endpoints to optionally request real model.

For message send:

```text
POST /api/v1/agent-chat/sessions/{session_id}/messages
```

Add optional request fields:

```json
{
  "message_text": "Investigate this failed batch",
  "use_real_model": false,
  "provider_code": "OPENAI_RESPONSES",
  "model_code": "OPENAI_GPT_5_4_MINI",
  "dry_run": false
}
```

Default:

```text
use_real_model=false
dry_run=false
```

If `use_real_model=true` but not enabled/configured, return safe fallback and audit.

---

# Backend APIs

Add or extend routes under:

```text
/api/v1/ai-config
```

Required additions:

```text
GET  /api/v1/ai-config/real-model/status
POST /api/v1/ai-config/real-model/test
POST /api/v1/ai-config/real-model/dry-run
GET  /api/v1/ai-config/real-model/providers
GET  /api/v1/ai-config/real-model/models
```

Behavior:

## Status

Return:

```text
feature flag enabled/disabled
provider configured
model configured
api key present yes/no
provider enabled
model enabled
default model
safe to invoke yes/no
reason if not safe
```

Do not return the API key.

## Dry run

Should validate:

```text
provider exists
model exists
feature flag state
safety checks
prompt construction
```

But must not call the external provider.

## Test

Should call the real provider only when:

```text
REAL_MODEL_ENABLED=true
allow_real_model=true
provider enabled
model enabled
API key present
safety passed
```

Otherwise return a controlled disabled/failed response.

---

# BFF Route Exposure

## Full backend

Expose all real-model governance APIs.

## Agentic BFF

Expose all real-model governance APIs.

## Operations BFF

Expose status and dry-run.

Optional test endpoint if useful.

## Business BFF

Do not expose real-model admin/config endpoints.

Business chat may use real model only indirectly in future through safe backend policy, not in this prompt.

## Simulation BFF

Do not expose real-model config endpoints.

## Observability BFF

Do not expose real-model config endpoints unless needed.

---

# Frontend UI

Update AI Config / Agentic UI.

Suggested files to modify or add:

```text
frontend/src/services/aiConfigApi.ts
frontend/src/pages/AIConfigPages.tsx
frontend/src/pages/AgentChatPages.tsx
```

Add page or panel:

```text
/ai-config/real-model
```

Visible in:

```text
full
agentic
```

Optional read-only status in:

```text
operations
```

Do not show in:

```text
business
simulation
observability
```

---

## Real Model UI Capabilities

The UI should show:

```text
real model feature flag status
provider status
model status
API key presence yes/no
safe to invoke yes/no
default configured model
last invocation logs if available
dry-run button
test button with clear warnings
```

Important UI labels:

```text
Mock mode remains default.
Real model calls require explicit backend configuration.
API keys are read from environment variables only.
No autonomous remediation is enabled.
Stage 1 read-only only.
```

Do not provide a UI field to enter or display API keys.

---

## Agent Chat UI Update

In Agentic UI only, optionally add:

```text
Use governed real model if enabled
```

Default unchecked.

When checked:

```text
send use_real_model=true
provider/model from default config or selected config
```

If disabled/not configured, display returned safe fallback.

Business UI must not show this toggle.

Operations UI may show read-only generation mode but not necessarily a toggle.

---

# Demo Control Integration

Update demo control readiness/components to include:

```text
Real Model Provider
OpenAI Responses Provider
Real Model Feature Flag
```

Readiness should check:

```text
http://localhost:8050/api/v1/ai-config/real-model/status
```

It should not call the real model.

---

# Logging and Audit

Every real-model attempt must create an invocation log, including disabled/blocked/failed attempts.

Log:

```text
request_source
provider_code
model_code
task_type
status
safety_status
generation_mode
fallback_used
latency_ms
token usage if available
error message if failed
```

Do not log:

```text
API key
secrets
full sensitive user payload if safety policy identifies it as secret
```

---

# Tests

Add backend tests for:

```text
real model status default disabled
dry-run does not call external provider
test endpoint blocked/disabled without feature flag
test endpoint blocked/disabled without API key
provider/model seed idempotency
OpenAI provider adapter mocked success
OpenAI provider adapter mocked failure
invocation logs created for disabled/failed/success paths
safety pre-check blocks forbidden input
safety post-check blocks forbidden output
agent chat default remains deterministic
agent chat use_real_model=true falls back safely when disabled
agent chat mocked real model path records ai_invocation_id
BFF exposure
Business BFF does not expose real-model config
Demo control includes real-model readiness
```

Tests must mock external calls.

Tests must not require network.

Tests must not require OpenAI API key.

Existing tests must continue to pass.

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

## Status

```bash
curl -sS http://localhost:8050/api/v1/ai-config/real-model/status | jq .
curl -sS http://localhost:8065/api/v1/ai-config/real-model/status | jq .
```

Expected by default:

```text
real model disabled
safe_to_invoke false
api_key_present false unless environment variable is set
mock remains default
```

## Dry run

```bash
curl -sS -X POST http://localhost:8050/api/v1/ai-config/real-model/dry-run \
  -H "Content-Type: application/json" \
  -d '{
    "provider_code": "OPENAI_RESPONSES",
    "model_code": "OPENAI_GPT_5_4_MINI",
    "task_type": "AGENT_STAGE_1_GUIDANCE",
    "request_source": "MANUAL_VALIDATION",
    "input_text": "Order is stuck during fulfillment. What should I check?",
    "allow_real_model": false,
    "dry_run": true
  }' | jq .
```

Expected:

```text
prompt validated
safety passed
no external call made
invocation/audit recorded if implemented
```

## Disabled real-model test

```bash
curl -sS -X POST http://localhost:8050/api/v1/ai-config/real-model/test \
  -H "Content-Type: application/json" \
  -d '{
    "provider_code": "OPENAI_RESPONSES",
    "model_code": "OPENAI_GPT_5_4_MINI",
    "task_type": "AGENT_STAGE_1_GUIDANCE",
    "request_source": "MANUAL_VALIDATION",
    "input_text": "Summarize the current issue in Stage 1 read-only mode.",
    "allow_real_model": true,
    "dry_run": false
  }' | jq .
```

Expected by default:

```text
real model disabled or API key missing
no external call made
safe controlled response
audit log created
```

## Agent chat default deterministic

```bash
curl -sS -X POST http://localhost:8065/api/v1/agent-chat/intake/engineer-investigation \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Investigate stuck order with default deterministic agent",
    "description": "Verify default remains deterministic.",
    "initial_message": "Order is stuck during fulfillment and inventory allocation failed. What should I check?"
  }' | jq .
```

Expected:

```text
generation_mode deterministic
no real model
Relevant Knowledge still included
actions_executed = 0
```

## Agent chat real-model requested but disabled

```bash
curl -sS -X POST http://localhost:8065/api/v1/agent-chat/sessions/<SESSION_ID>/messages \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "Use the governed real model if available and summarize likely next steps.",
    "use_real_model": true,
    "provider_code": "OPENAI_RESPONSES",
    "model_code": "OPENAI_GPT_5_4_MINI"
  }' | jq .
```

Expected by default:

```text
safe fallback
audit log
no action execution
no autonomous remediation
```

## BFF exposure

```bash
curl -sS http://localhost:8065/api/v1/ai-config/real-model/status | jq .
curl -sS http://localhost:8062/api/v1/ai-config/real-model/status | jq .
curl -i -sS http://localhost:8061/api/v1/ai-config/real-model/status | head
curl -i -sS http://localhost:8063/api/v1/ai-config/real-model/status | head
```

Expected:

```text
Agentic BFF: works
Operations BFF: status works
Business BFF: 404
Simulation BFF: 404
```

---

# Optional Manual Real Model Validation

Do not require this for Definition of Done.

Only run manually when an API key is intentionally available.

Example:

```bash
export REAL_MODEL_ENABLED=true
export OPENAI_API_KEY="..."
export OPENAI_DEFAULT_MODEL="gpt-5.4-mini"
```

Then restart only the target backend/BFF process.

Run:

```bash
curl -sS -X POST http://localhost:8050/api/v1/ai-config/real-model/test \
  -H "Content-Type: application/json" \
  -d '{
    "provider_code": "OPENAI_RESPONSES",
    "model_code": "OPENAI_GPT_5_4_MINI",
    "task_type": "AGENT_STAGE_1_GUIDANCE",
    "request_source": "MANUAL_REAL_MODEL_TEST",
    "input_text": "Provide Stage 1 read-only guidance for an order stuck during fulfillment.",
    "allow_real_model": true,
    "dry_run": false
  }' | jq .
```

Validation expectations:

```text
real provider called
invocation log created
usage captured if returned
output safety checked
no remediation executed
```

Do not commit API keys.

Do not paste API keys into logs or screenshots.

---

# Manual UI Validation

Open:

```text
http://localhost:4015/ai-config/real-model
http://localhost:4001/ai-config/real-model
```

Validate:

```text
real model status loads
provider/model status visible
API key presence shown as yes/no only
dry run works
test call returns disabled/fallback by default
warning banners visible
no API key entry field exists
no autonomous remediation controls exist
```

Open Agentic chat:

```text
http://localhost:4015/agent-chat/engineer
```

Validate:

```text
default remains deterministic
real-model toggle is off by default
toggle is visible only in Agentic/Full where appropriate
disabled/fallback behavior is clear when real model is unavailable
```

---

# Documentation Updates

Update `README.md` with:

```text
real model provider setup
environment variables
mock-first default
how to run dry run
how to run disabled test
optional real model manual test
safety warnings
no API key storage
no autonomous remediation
```

Update `ARCHITECTURE.md` with:

```text
governed real model provider architecture
provider gateway
OpenAI-compatible provider adapter
feature flag and API key controls
prompt governance
safety pre-check/post-check
agent chat optional real-model path
fallback deterministic path
audit and usage tracking
future model/RAG/action roadmap
```

Document clearly:

```text
Prompt 20 introduces optional governed real-model integration foundation.
It does not make real-model use the default.
It does not require API keys.
It does not enable autonomous remediation.
It does not introduce ServiceNow.
It does not add vector RAG.
```

---

# Definition of Done

Prompt 20 is complete only when:

- OpenAI-compatible provider adapter exists
- mock provider remains default
- real provider is disabled by default
- API key is read only from environment
- API key is never stored or logged
- seed_ai_config creates disabled real provider/model config idempotently
- real-model status endpoint exists
- dry-run endpoint exists and does not call external provider
- test endpoint exists and is controlled by feature flag/API key/provider/model settings
- provider gateway handles disabled/missing-key/failure paths safely
- external calls are mocked in tests
- invocation logs are created for disabled/blocked/failed/success paths where applicable
- safety pre-check exists
- safety post-check exists
- agent chat default remains deterministic
- agent chat optional real-model request falls back safely when disabled
- Agentic UI has real model config/status page
- Full UI has real model config/status page
- Business UI does not expose real-model admin config
- Demo control includes real model readiness
- backend tests pass
- frontend build passes
- demo stack validation passes
- no test requires OpenAI API key
- no default external LLM call occurs
- no autonomous remediation is introduced
- no ServiceNow integration is introduced
- no authentication is introduced
- no Docker Compose change unless justified
- no observability infrastructure change unless justified
- README updated
- ARCHITECTURE.md updated
- Prompt 20 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. Dependency changes
5. Real provider configuration summary
6. Environment variable summary
7. Provider gateway behavior
8. Real-model status behavior
9. Dry-run behavior
10. Disabled/missing-key behavior
11. Safety pre-check/post-check behavior
12. Agent chat integration summary
13. Backend APIs added
14. BFF exposure summary
15. Frontend routes/pages added
16. Demo control integration summary
17. Backend test results
18. Frontend build results
19. Demo stack validation results
20. Manual API validation results
21. Manual UI validation results
22. Confirmation mock remains default
23. Confirmation no API key is stored/logged
24. Confirmation no real model call occurs by default
25. Confirmation tests do not require OpenAI API key
26. Confirmation no autonomous remediation was introduced
27. Confirmation no ServiceNow/authentication/vector DB/agent framework was introduced
28. TODOs or limitations
29. Recommended Git commit message

Recommended commit message:

```text
feat: add governed real model provider foundation
```

Do not proceed beyond this prompt.