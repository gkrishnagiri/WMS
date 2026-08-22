# Prompt 10 – Governed LLM Configuration and Provider Abstraction Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 01 created the enterprise application foundation.

Prompt 02 created the Warehouse & Fulfillment domain foundation.

Prompt 03 created warehouse transaction workflows.

Prompt 04 created operational exceptions and the AMS ticket foundation.

Prompt 05 created synthetic users and user-reported functional issues.

Prompt 06 created monitoring alert noise and manual triage without observability.

Prompt 07 created observability-enabled support diagnosis using deterministic traces, spans, logs, metrics, and diagnostic cases.

Prompt 08 created batch jobs and batch failure scenarios.

Prompt 09 created the deterministic AI-native support engineer copilot foundation.

Your task now is to implement the next foundation layer:

```text
Governed LLM Configuration and Provider Abstraction Foundation
```

This prompt introduces the governed configuration layer required before any real LLM or agentic behavior is enabled.

It must not call external LLMs yet.

It must not introduce LangGraph, LiteLLM, OpenAI SDKs, Anthropic SDKs, embedding libraries, vector databases, RAG frameworks, autonomous agents, or ServiceNow integration yet.

This prompt creates:

```text
LLM provider catalog
Model configuration catalog
Prompt template registry
Safety policy registry
Mock provider abstraction
LLM request/response audit logs
Usage accounting foundation
Governed test invocation endpoint
Admin UI for configuration visibility
```

The only executable provider in this prompt should be a deterministic mock provider.

---

## Current Confirmed Baseline

The repository currently has:

- FastAPI backend
- React/Vite/MUI frontend
- PostgreSQL
- Redis
- Health and version endpoints
- Warehouse domain tables
- Warehouse seed data
- Warehouse read APIs
- Warehouse transaction workflows
- Inventory transaction ledger
- Order event history
- Operational exceptions
- AMS ticket foundation
- AMS ticket lifecycle
- Synthetic users
- Synthetic journeys
- User-reported issues
- Monitoring components
- Monitoring rules
- Monitoring alert noise simulations
- Monitoring triage cases
- Application-level observability evidence
- Diagnostic cases and diagnostic evidence
- Batch jobs
- Batch runs
- Batch failures
- Batch-to-exception/ticket/diagnostic flow
- Deterministic support engineer copilot
- Copilot context snapshots
- Copilot recommendations
- Copilot action plans
- Copilot generated drafts/checklists
- Backend running on port `8050`
- Frontend running on port `4001`

Recent committed capabilities include:

```text
feat: add EOS enterprise foundation
feat: add warehouse fulfillment domain foundation
feat: add warehouse transaction workflows
feat: add operational exceptions and AMS ticket foundation
feat: add synthetic users and user-reported issues
feat: add monitoring alert noise and triage foundation
feat: add observability-enabled support diagnosis
feat: add batch jobs and batch failure scenarios
feat: add ai-native support copilot foundation
```

Use the current repository structure and coding patterns.

Do not redesign prior prompt output.

---

## Critical Instructions

You must not redesign the project.

You must not rename the application.

You must not change infrastructure.

You must not modify Docker Compose.

You must not modify observability configuration.

You must not introduce new major frameworks.

You must preserve backend port `8050`.

You must preserve frontend port `4001`.

You must preserve all existing APIs and frontend routes.

You must implement only the scope described in this prompt.

If something is unclear, leave a clear TODO comment instead of inventing architecture.

---

## Files and Paths You Must Not Modify

Do not modify:

```text
docker-compose.yml
observability/
data/
load-tests/
.git/
```

Do not modify local runtime files:

```text
backend/.env
backend/.venv/
frontend/.env
frontend/node_modules/
frontend/dist/
```

You may modify:

```text
backend/
frontend/
README.md
ARCHITECTURE.md
docs/06_Codex/
```

You may create a new Alembic migration.

You may update `.gitignore` only if needed to exclude local runtime artifacts.

---

## Technology Constraints

Use only the technologies already selected.

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- pydantic-settings
- psycopg
- redis-py
- pytest
- httpx

### Frontend

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Material UI

Do not add:

- LangGraph
- LiteLLM
- OpenAI SDK
- Anthropic SDK
- local model runtimes
- vector databases
- embedding libraries
- RAG frameworks
- agent frameworks
- workflow engines
- Celery
- Kafka
- Temporal
- ServiceNow connectors
- browser automation
- charting libraries

The only LLM-like execution allowed in this prompt is a deterministic internal mock provider.

No external network LLM call should be made.

---

# Objective

Implement a governed LLM configuration and provider abstraction foundation.

This layer should allow EOS to safely introduce real LLMs in later prompts without changing the copilot architecture.

Prompt 09 created a deterministic copilot.

Prompt 10 creates the governed AI configuration substrate behind it.

The intended future flow is:

```text
Copilot request
        ↓
Prompt template selected
        ↓
Safety policy evaluated
        ↓
Provider/model selected
        ↓
Invocation logged
        ↓
Usage recorded
        ↓
Response returned
```

In Prompt 10, this flow must use a deterministic mock provider only.

No real LLM call.

---

# Architectural Intent

This prompt should separate:

```text
AI configuration
Prompt templates
Safety controls
Provider/model selection
Invocation logging
Usage accounting
```

from:

```text
Copilot business logic
Support workflows
AMS ticket lifecycle
Monitoring
Observability
Batch operations
```

The copilot should not be tightly coupled to any one LLM provider.

This prompt prepares for future provider enablement while keeping the current system safe and deterministic.

---

# Scope

Implement:

1. AI provider catalog
2. AI model configuration catalog
3. Prompt template registry
4. Safety policy registry
5. Safety rule checks
6. Mock provider abstraction
7. Invocation request/response audit logging
8. Usage accounting foundation
9. Governed test invocation endpoint
10. Admin/config frontend pages
11. Backend tests
12. Documentation updates

Do not implement:

- real external LLM calls
- streaming responses
- embeddings
- vector search
- RAG
- LangGraph
- autonomous agents
- tool execution by LLM
- ServiceNow integration
- prompt optimization
- fine-tuning
- secret management beyond placeholder fields
- production credential storage

---

# Database Additions

Create a new Alembic migration.

Add the following tables:

```text
ai_providers
ai_model_configs
ai_prompt_templates
ai_safety_policies
ai_safety_policy_rules
ai_invocation_logs
ai_usage_daily
ai_guardrail_events
```

Use UUID primary keys consistent with existing project style.

Use timestamp conventions consistent with existing project.

---

## Table: `ai_providers`

Purpose:

Represent configured AI/LLM providers.

Fields:

```text
id
provider_code
name
provider_type
description
base_url
auth_type
enabled
is_mock
default_timeout_seconds
created_at
updated_at
```

Rules:

- `provider_code` must be unique
- `is_mock` defaults to false
- `enabled` defaults to false
- no API keys should be stored in this table
- real providers may be listed but disabled

Suggested provider types:

```text
MOCK
OPENAI_COMPATIBLE
AZURE_OPENAI
ANTHROPIC_COMPATIBLE
LOCAL
OTHER
```

Seed provider:

```text
MOCK_GOVERNED
```

This should be enabled and marked `is_mock = true`.

Optional disabled placeholder providers:

```text
OPENAI_DISABLED_PLACEHOLDER
AZURE_OPENAI_DISABLED_PLACEHOLDER
LOCAL_MODEL_DISABLED_PLACEHOLDER
```

These must be disabled and must not be callable.

---

## Table: `ai_model_configs`

Purpose:

Represent model-level configuration.

Fields:

```text
id
model_code
provider_id
display_name
model_name
model_family
purpose
enabled
is_default
temperature
top_p
max_output_tokens
context_window_tokens
cost_per_1k_input_tokens
cost_per_1k_output_tokens
created_at
updated_at
```

Rules:

- `model_code` must be unique
- `provider_id` references `ai_providers.id`
- only mock model should be enabled in this prompt
- only one model should be default if simple to enforce
- cost fields may be zero for mock provider

Suggested purposes:

```text
COPILOT_SUMMARY
COPILOT_RECOMMENDATION
WORK_NOTE_DRAFT
CUSTOMER_UPDATE_DRAFT
INVESTIGATION_CHECKLIST
GENERAL_TEST
```

Seed enabled model:

```text
MOCK-SUPPORT-COPILOT-001
```

Provider:

```text
MOCK_GOVERNED
```

---

## Table: `ai_prompt_templates`

Purpose:

Govern reusable prompt templates.

Fields:

```text
id
template_code
name
description
task_type
template_version
system_template
user_template
input_schema
output_schema
enabled
is_default
created_at
updated_at
```

Rules:

- unique constraint on `(template_code, template_version)`
- `input_schema` and `output_schema` should be JSON/JSONB if supported
- templates must be deterministic and safe
- no external LLM is called in this prompt

Suggested task types:

```text
COPILOT_CONTEXT_SUMMARY
COPILOT_RECOMMENDATION
WORK_NOTE_DRAFT
CUSTOMER_UPDATE_DRAFT
INVESTIGATION_CHECKLIST
GENERAL_TEST
```

Seed templates:

```text
TPL-COPILOT-CONTEXT-SUMMARY
TPL-COPILOT-RECOMMENDATION
TPL-WORK-NOTE-DRAFT
TPL-CUSTOMER-UPDATE-DRAFT
TPL-INVESTIGATION-CHECKLIST
TPL-GENERAL-TEST
```

---

## Table: `ai_safety_policies`

Purpose:

Represent safety/governance policy groups.

Fields:

```text
id
policy_code
name
description
policy_scope
enabled
blocking_mode
created_at
updated_at
```

Rules:

- `policy_code` must be unique
- `enabled` defaults to true
- `blocking_mode` determines whether a rule violation blocks or warns

Suggested policy scopes:

```text
COPILOT
SUPPORT_WORKFLOW
GENERAL_INVOCATION
```

Suggested blocking modes:

```text
BLOCK
WARN
LOG_ONLY
```

Seed policy:

```text
POL-COPILOT-GOVERNANCE
```

---

## Table: `ai_safety_policy_rules`

Purpose:

Represent deterministic safety rules.

Fields:

```text
id
policy_id
rule_code
name
description
rule_type
severity
enabled
match_pattern
action
created_at
updated_at
```

Rules:

- `policy_id` references `ai_safety_policies.id`
- unique constraint on `(policy_id, rule_code)`
- `match_pattern` is a deterministic string or simple pattern
- do not implement complex unsafe regex behavior unless already safe and easy

Suggested rule types:

```text
BLOCK_SECRET_DISCLOSURE
BLOCK_DESTRUCTIVE_AUTOMATION
BLOCK_EXTERNAL_ACTION
BLOCK_RAW_CREDENTIALS
WARN_PERSONAL_DATA
WARN_LOW_CONFIDENCE
```

Suggested actions:

```text
BLOCK
WARN
LOG
```

Seed rules:

```text
RULE-BLOCK-API-KEY
RULE-BLOCK-PASSWORD
RULE-BLOCK-AUTO-CLOSE-TICKET
RULE-BLOCK-AUTO-DELETE-DATA
RULE-BLOCK-EXTERNAL-SEND
RULE-WARN-LOW-CONFIDENCE
```

---

## Table: `ai_invocation_logs`

Purpose:

Audit every governed AI/mock invocation.

Fields:

```text
id
invocation_number
provider_id
model_config_id
template_id
policy_id
request_source
request_source_id
task_type
status
input_summary
prompt_rendered
response_text
response_json
safety_status
blocked_reason
latency_ms
input_tokens_estimated
output_tokens_estimated
total_tokens_estimated
cost_estimated
created_by
created_at
```

Rules:

- `invocation_number` must be unique
- `response_json` should be JSON/JSONB if supported
- this table may store rendered prompt because this is a local demo, but do not include secrets
- safety block should still create an invocation log with blocked status

Suggested statuses:

```text
SUCCESS
BLOCKED
FAILED
SKIPPED
```

Suggested safety statuses:

```text
PASSED
WARNED
BLOCKED
NOT_EVALUATED
```

Invocation number format:

```text
AI-INV-YYYYMMDD-0001
```

---

## Table: `ai_usage_daily`

Purpose:

Aggregate daily usage counts.

Fields:

```text
id
usage_date
provider_code
model_code
task_type
invocation_count
blocked_count
input_tokens_estimated
output_tokens_estimated
total_tokens_estimated
cost_estimated
created_at
updated_at
```

Rules:

- unique constraint on `(usage_date, provider_code, model_code, task_type)`
- update after each invocation

---

## Table: `ai_guardrail_events`

Purpose:

Audit safety rule warnings and blocks.

Fields:

```text
id
invocation_id
policy_id
rule_id
event_type
severity
message
matched_text_summary
created_at
```

Rules:

- `invocation_id` references `ai_invocation_logs.id`
- `policy_id` references `ai_safety_policies.id`
- `rule_id` nullable, references `ai_safety_policy_rules.id`
- `matched_text_summary` should avoid storing secrets directly

Suggested event types:

```text
RULE_WARNED
RULE_BLOCKED
POLICY_PASSED
```

---

# Seed Data

Create an idempotent seed module:

```text
backend/app/db/seed_ai_config.py
```

Runnable as:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_ai_config
```

It should seed:

```text
1 enabled mock provider
1 enabled mock model
at least 6 prompt templates
1 safety policy
at least 6 safety rules
optional disabled provider placeholders
```

Running it multiple times must not create duplicates.

Update README validation commands to include this seed command.

Do not modify existing seed behavior for warehouse, synthetic users, monitoring, batch, copilot, operations, AMS, or observability.

---

# Provider Abstraction

Create service modules such as:

```text
backend/app/services/ai_config_service.py
backend/app/services/ai_prompt_service.py
backend/app/services/ai_safety_service.py
backend/app/services/ai_provider_gateway.py
backend/app/services/ai_usage_service.py
```

You may organize differently if consistent with existing project style.

The provider abstraction should define a simple internal contract:

```text
invoke(
  task_type,
  input_payload,
  request_source,
  request_source_id,
  template_code optional,
  model_code optional
)
```

The gateway should:

1. resolve enabled provider/model
2. resolve prompt template
3. render deterministic prompt text
4. evaluate safety policy/rules
5. block if required
6. call mock provider
7. estimate tokens using simple deterministic approximation
8. log invocation
9. update usage aggregate
10. return governed response

---

## Mock Provider

Implement only one executable provider in this prompt:

```text
MOCK_GOVERNED
```

Behavior:

- deterministic
- no external network call
- no model SDK
- response based on task type and input payload
- should return structured response where useful

Example behavior:

### `GENERAL_TEST`

Return:

```text
Mock governed response generated successfully.
```

### `COPILOT_CONTEXT_SUMMARY`

Return a concise deterministic summary from supplied context.

### `WORK_NOTE_DRAFT`

Return deterministic work note style text.

### `CUSTOMER_UPDATE_DRAFT`

Return deterministic customer-safe update text.

### `INVESTIGATION_CHECKLIST`

Return deterministic checklist.

The mock provider can use existing copilot-style deterministic text generation logic if safe.

Do not call external APIs.

---

# Safety Policy Evaluation

Implement deterministic safety evaluation before mock invocation.

Safety checks should inspect:

```text
input payload as text
rendered prompt text
request source metadata
```

Minimum required behavior:

- block if text contains obvious raw API key markers
- block if text contains `password=`
- block if text requests automatic ticket closure
- block if text requests deleting production data
- block if text requests sending external email/message
- warn on low confidence phrasing if applicable

Example blocked phrases:

```text
sk-
api_key
password=
auto close ticket
automatically close ticket
delete production data
send external email
send slack message
```

Blocking should:

- not invoke provider
- create invocation log with `status = BLOCKED`
- create guardrail event
- return clear blocked response

Warnings should:

- still invoke provider
- create guardrail event
- mark safety status `WARNED`

Do not over-engineer safety.

---

# Backend APIs

Create AI configuration APIs.

Suggested files:

```text
backend/app/models/ai_config.py
backend/app/schemas/ai_config.py
backend/app/services/ai_config_service.py
backend/app/services/ai_prompt_service.py
backend/app/services/ai_safety_service.py
backend/app/services/ai_provider_gateway.py
backend/app/api/routes/ai_config.py
backend/app/db/seed_ai_config.py
```

Use prefix:

```text
/api/v1/ai-config
```

Add:

```text
GET  /api/v1/ai-config/summary
GET  /api/v1/ai-config/providers
GET  /api/v1/ai-config/models
GET  /api/v1/ai-config/prompt-templates
GET  /api/v1/ai-config/safety-policies
GET  /api/v1/ai-config/safety-rules
GET  /api/v1/ai-config/invocations
GET  /api/v1/ai-config/invocations/{invocation_id}
GET  /api/v1/ai-config/usage-daily
GET  /api/v1/ai-config/guardrail-events
POST /api/v1/ai-config/test-invocation
POST /api/v1/ai-config/safety-check
```

Do not expose endpoints for storing secrets.

Do not expose endpoints that enable real providers yet unless they remain disabled and safe.

---

## AI Config Summary

Endpoint:

```text
GET /api/v1/ai-config/summary
```

Return:

```json
{
  "providers": 4,
  "enabled_providers": 1,
  "models": 1,
  "enabled_models": 1,
  "prompt_templates": 6,
  "safety_policies": 1,
  "safety_rules": 6,
  "invocations_today": 3,
  "blocked_invocations_today": 1,
  "estimated_tokens_today": 1200,
  "estimated_cost_today": 0.0
}
```

Use actual database queries.

---

## Test Invocation

Endpoint:

```text
POST /api/v1/ai-config/test-invocation
```

Request:

```json
{
  "task_type": "GENERAL_TEST",
  "input_payload": {
    "message": "Generate a safe mock test response"
  },
  "template_code": "TPL-GENERAL-TEST",
  "model_code": "MOCK-SUPPORT-COPILOT-001",
  "request_source": "ADMIN_TEST",
  "request_source_id": null
}
```

Behavior:

- use provider gateway
- evaluate safety
- invoke mock provider if safe
- create invocation log
- update usage
- return response and invocation metadata

---

## Safety Check

Endpoint:

```text
POST /api/v1/ai-config/safety-check
```

Request:

```json
{
  "text": "automatically close ticket and send external email"
}
```

Behavior:

- run safety rules only
- do not invoke provider
- return pass/warn/block result and matched rules
- log guardrail event only if simple; otherwise just return evaluation

---

## Invocation List

Endpoint:

```text
GET /api/v1/ai-config/invocations
```

Support filters:

```text
status
task_type
provider_code
model_code
safety_status
request_source
```

Default sort:

```text
newest first
```

Limit default:

```text
100
```

---

# Optional Copilot Integration

Do only minimal safe integration.

The existing deterministic copilot from Prompt 09 must continue to work even if AI config is unavailable.

Add optional copilot API endpoint only if straightforward:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-governed-ai-draft
```

Behavior:

- use latest copilot context snapshot
- call AI provider gateway with mock provider
- create copilot message from mock response
- create AI invocation log linked by request source
- no external LLM call

If this is too invasive, skip and document as deferred.

Do not replace existing deterministic copilot draft generation.

---

# Frontend Implementation

Extend the existing EOS frontend.

Do not replace the application shell.

Do not change frontend port `4001`.

Do not change backend base URL away from `http://localhost:8050`.

---

## Navigation

Add sidebar entries:

```text
AI Config
AI Invocations
AI Safety
```

Keep existing entries:

```text
Dashboard
Warehouse
Inventory
Orders
Fulfillment Tasks
Shipments
Inventory Transactions
Operations
AMS Tickets
Synthetic Journeys
Journey Runs
User Reports
Monitoring
Monitoring Simulations
Monitoring Triage
Observability
Traces
Diagnostics
Batch Jobs
Batch Runs
Batch Simulations
Copilot
Copilot Sessions
Health
About
```

---

## Required Frontend Routes

Add:

```text
/ai-config
/ai-config/providers
/ai-config/prompts
/ai-config/safety
/ai-config/invocations
/ai-config/usage
/ai-config/test
```

Existing routes must continue working.

---

## AI Config Overview Page

Route:

```text
/ai-config
```

Display:

- summary cards from `/api/v1/ai-config/summary`
- explanatory text:

```text
This module provides governed AI configuration and provider abstraction. Only the deterministic mock provider is executable in this phase. No external LLM calls are enabled.
```

Cards:

```text
providers
enabled providers
models
enabled models
prompt templates
safety policies
safety rules
invocations today
blocked today
estimated tokens today
estimated cost today
```

---

## Providers Page

Route:

```text
/ai-config/providers
```

Display tables for:

```text
providers
models
```

Provider columns:

```text
provider code
name
provider type
enabled
mock
auth type
timeout
```

Model columns:

```text
model code
display name
provider
purpose
enabled
default
temperature
max output tokens
```

No secret fields.

---

## Prompt Templates Page

Route:

```text
/ai-config/prompts
```

Display table:

```text
template code
name
task type
version
enabled
default
```

Allow viewing template detail in a dialog or expanded panel:

```text
system template
user template
input schema
output schema
```

Read-only in this prompt is acceptable.

---

## AI Safety Page

Route:

```text
/ai-config/safety
```

Display:

- safety policies
- safety rules
- safety check tester

Safety check tester:

```text
textarea
Run Safety Check
result panel
matched rules
decision
```

---

## AI Invocations Page

Route:

```text
/ai-config/invocations
```

Display table:

```text
invocation number
task type
provider
model
status
safety status
tokens
cost
request source
created at
```

Invocation row should show detail:

```text
input summary
rendered prompt
response text
blocked reason
guardrail events
```

---

## AI Usage Page

Route:

```text
/ai-config/usage
```

Display table:

```text
date
provider
model
task type
invocations
blocked
input tokens
output tokens
total tokens
cost
```

No charting library.

---

## AI Test Page

Route:

```text
/ai-config/test
```

Form:

```text
task_type
template_code
model_code
request_source
message/input payload
```

Defaults:

```text
task_type = GENERAL_TEST
template_code = TPL-GENERAL-TEST
model_code = MOCK-SUPPORT-COPILOT-001
request_source = ADMIN_TEST
```

On submit:

- call `/api/v1/ai-config/test-invocation`
- display:
  - response text
  - safety status
  - invocation number
  - estimated tokens
  - blocked reason if any

Add a second test message example that should be blocked:

```text
automatically close ticket and send external email
```

---

# Frontend API Client

Create or extend typed API client.

Suggested file:

```text
frontend/src/services/aiConfigApi.ts
```

Use `VITE_API_BASE_URL`.

Use TanStack Query for data loading.

Use mutations for safety check and test invocation.

Show loading and error states.

---

# Backend Tests

Add tests covering:

1. Existing health/version tests still pass
2. Existing warehouse read tests still pass
3. Existing warehouse workflow tests still pass
4. Existing operations/AMS tests still pass
5. Existing synthetic user tests still pass
6. Existing monitoring tests still pass
7. Existing observability tests still pass
8. Existing batch tests still pass
9. Existing copilot tests still pass
10. AI config seed is idempotent
11. AI config summary endpoint works
12. Provider list works
13. Model list works
14. Prompt template list works
15. Safety policy and rule list works
16. Safety check passes safe text
17. Safety check blocks API-key-like text
18. Safety check blocks auto-close-ticket request
19. Test invocation succeeds with mock provider
20. Test invocation creates invocation log
21. Test invocation updates usage aggregate
22. Blocked invocation does not call mock provider
23. Blocked invocation creates guardrail event
24. Invocation list endpoint works
25. Invocation detail endpoint works
26. Usage daily endpoint works
27. Guardrail event endpoint works
28. Disabled non-mock provider cannot be invoked
29. No external LLM SDK dependency is required

Tests should be runnable with:

```bash
cd backend
source .venv/bin/activate
pytest
```

When local PostgreSQL and Redis are running and database is migrated/seeded, tests should pass.

If integration prerequisites are missing, tests may skip clearly, but do not hide real application errors.

---

# Frontend Validation

Ensure:

```bash
cd frontend
npm run build
```

passes.

Do not add unnecessary frontend test complexity in this prompt.

---

# Documentation Updates

Update `README.md` with:

- Prompt 10 governed LLM configuration summary
- mock provider behavior
- provider catalog
- model configuration catalog
- prompt template registry
- safety policy registry
- invocation logging
- usage accounting
- guardrail events
- test invocation
- new APIs
- new frontend routes
- seed commands
- validation commands
- backend port `8050`
- frontend port `4001`
- explicit deferred items:
  - real external LLM calls
  - OpenAI/Azure/Anthropic SDK integration
  - LangGraph
  - LiteLLM
  - RAG
  - embeddings/vector store
  - autonomous remediation
  - ServiceNow integration

Update `ARCHITECTURE.md` with:

- governed AI configuration module
- provider abstraction
- mock provider
- prompt template registry
- safety policy flow
- invocation logging and usage accounting
- relationship to copilot
- current deferred items

If `docs/06_Codex/` exists, do not modify prior prompt files unless necessary.

---

# Validation Commands

Run or provide results for:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
python -m app.db.seed_batch
python -m app.db.seed_copilot
python -m app.db.seed_ai_config
pytest
```

Then validate live backend:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/ai-config/summary | jq .
curl -sS http://localhost:8050/api/v1/ai-config/providers | jq .
curl -sS http://localhost:8050/api/v1/ai-config/models | jq .
curl -sS http://localhost:8050/api/v1/ai-config/prompt-templates | jq .
curl -sS http://localhost:8050/api/v1/ai-config/safety-policies | jq .
curl -sS http://localhost:8050/api/v1/ai-config/safety-rules | jq .
```

Run a safe mock invocation:

```bash
curl -sS -X POST http://localhost:8050/api/v1/ai-config/test-invocation \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "GENERAL_TEST",
    "input_payload": {
      "message": "Generate a safe mock test response"
    },
    "template_code": "TPL-GENERAL-TEST",
    "model_code": "MOCK-SUPPORT-COPILOT-001",
    "request_source": "ADMIN_TEST",
    "request_source_id": null
  }' | jq .
```

Run a blocked safety test:

```bash
curl -sS -X POST http://localhost:8050/api/v1/ai-config/test-invocation \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "GENERAL_TEST",
    "input_payload": {
      "message": "automatically close ticket and send external email"
    },
    "template_code": "TPL-GENERAL-TEST",
    "model_code": "MOCK-SUPPORT-COPILOT-001",
    "request_source": "ADMIN_TEST",
    "request_source_id": null
  }' | jq .
```

Then validate logs and usage:

```bash
curl -sS http://localhost:8050/api/v1/ai-config/invocations | jq .
curl -sS http://localhost:8050/api/v1/ai-config/usage-daily | jq .
curl -sS http://localhost:8050/api/v1/ai-config/guardrail-events | jq .
```

Then validate frontend:

```bash
cd frontend
npm install
npm run build
./start_frontend.sh
```

Confirm UI pages are available at:

```text
http://localhost:4001/ai-config
http://localhost:4001/ai-config/providers
http://localhost:4001/ai-config/prompts
http://localhost:4001/ai-config/safety
http://localhost:4001/ai-config/invocations
http://localhost:4001/ai-config/usage
http://localhost:4001/ai-config/test
```

Manual UI validation:

```text
Open AI Config overview
Confirm mock provider and model are visible
Open Prompt Templates
Confirm seeded templates are visible
Open AI Safety
Run safe safety check
Run blocked safety check
Open AI Test
Run safe mock invocation
Run blocked mock invocation
Open AI Invocations
Confirm success and blocked invocations are visible
Open AI Usage
Confirm usage aggregate updated
Confirm no external LLM call occurred
```

---

# Definition of Done

Prompt 10 is complete only when:

- migration exists
- `ai_providers` exists
- `ai_model_configs` exists
- `ai_prompt_templates` exists
- `ai_safety_policies` exists
- `ai_safety_policy_rules` exists
- `ai_invocation_logs` exists
- `ai_usage_daily` exists
- `ai_guardrail_events` exists
- AI config seed exists and is idempotent
- enabled mock provider exists
- enabled mock model exists
- prompt templates are seeded
- safety policy and rules are seeded
- provider list API works
- model list API works
- prompt template list API works
- safety policy/rule APIs work
- safety check API works
- safe mock invocation works
- blocked mock invocation works
- invocation logging works
- guardrail event logging works
- usage accounting works
- disabled non-mock providers cannot be invoked
- frontend AI config overview works
- frontend providers page works
- frontend prompt templates page works
- frontend safety page works
- frontend invocations page works
- frontend usage page works
- frontend test page works
- existing warehouse APIs still work
- existing operations/AMS APIs still work
- existing synthetic user APIs still work
- existing monitoring APIs still work
- existing observability APIs still work
- existing batch APIs still work
- existing copilot APIs still work
- backend tests pass
- frontend build passes
- backend remains on port `8050`
- frontend remains on port `4001`
- README updated
- ARCHITECTURE.md updated
- no infrastructure files modified
- no external LLM SDK or agent framework introduced
- no external LLM calls made

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Alembic migration name
4. Backend AI config APIs added
5. Frontend routes added
6. Seed command and result
7. Backend validation results
8. Frontend validation results
9. Manual governed mock invocation validation result
10. Manual safety blocking validation result
11. Confirmation that infrastructure files were not modified
12. Confirmation that no external LLM SDK/agent framework was introduced
13. Confirmation that no external LLM call is made
14. Any TODOs
15. Recommended Git commit message

Recommended commit message:

```text
feat: add governed ai provider configuration foundation
```

Do not proceed beyond this prompt.