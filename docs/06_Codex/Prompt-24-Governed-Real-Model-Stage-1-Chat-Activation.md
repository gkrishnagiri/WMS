# Prompt 24 – Governed Real-Model Stage 1 Chat Activation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 18 added agent chat and case intake.

Prompt 19 added deterministic knowledge and RAG foundation.

Prompt 20 added governed real model provider foundation, disabled by default.

Prompt 21 added contextual agent investigation handoff.

Prompt 22 added the Agent Investigation Workspace and Evidence Timeline.

Prompt 23 added Stage 2 approval-gated local safe actions.

Your task now is to implement:

```text
Governed Real-Model Stage 1 Chat Activation
```

---

## Business Goal

The platform should now be able to use a real model for Stage 1 read-only support chat responses when explicitly enabled and requested.

The goal is to move from:

```text
deterministic-only agent guidance
```

to:

```text
governed model-assisted Stage 1 investigation chat
```

while preserving:

```text
mock/deterministic default behavior
no default external model calls
no autonomous remediation
no unapproved actions
no shell execution
no ServiceNow integration
full auditability
safe fallback
cost controls
clear UI visibility
```

This is the demo story:

```text
Engineer opens an investigation workspace
        ->
Engineer asks the agent a question
        ->
System gathers source context, evidence, timeline, knowledge, known errors, and safe action status
        ->
If real model is explicitly enabled and requested, governed provider produces a Stage 1 read-only answer
        ->
Safety checks run before and after the model call
        ->
Response is saved with invocation audit and citations to evidence/knowledge
        ->
If real model is unavailable, blocked, or failed, deterministic fallback is returned
        ->
No remediation is executed
```

---

## Critical Scope Clarification

Prompt 24 implements:

```text
real-model-assisted Stage 1 chat answers
real-model-assisted investigation Q&A
context packaging from evidence and knowledge
prompt governance
response grounding/citation metadata
real-model audit visibility
token/cost guardrails
deterministic fallback
manual optional real-model smoke test
```

Prompt 24 must **not** implement:

```text
autonomous remediation
unapproved action execution
shell command execution
arbitrary SQL execution
ServiceNow updates
customer communication sends
external system execution
real-time voice/audio
browser/computer use
vector database
new agent framework
```

Stage 2 approval-gated actions from Prompt 23 remain local and human-approved only.

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

Do not break existing Prompt 13–23 behavior.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve deterministic/mock behavior as the default.

You must not enable real model calls by default.

You must not require an OpenAI API key for local startup, tests, frontend build, seeds, or demo validation.

You must not call an external LLM in tests.

You must not call an external LLM unless all governance conditions are satisfied.

You must not introduce autonomous remediation.

You must not execute shell commands.

You must not execute arbitrary SQL.

You must not execute arbitrary user-provided code.

You must not integrate with ServiceNow.

You must not send customer communications externally.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

All real-model responses must be:

```text
Stage 1 read-only
evidence-aware
knowledge-aware
safety-checked
audited
fallback-safe
clearly labeled in UI
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

Implement governed real-model chat activation for Stage 1 investigation.

The platform should support:

```text
real-model Stage 1 chat response
real-model investigation question answer
model context package from case/evidence/knowledge/actions
provider readiness validation
model availability validation
input safety pre-check
output safety post-check
token/cost guardrails
response grounding metadata
invocation audit detail
deterministic fallback
UI toggle and status visibility
no remediation execution
```

---

# When Real Model Calls Are Allowed

A real model call may happen only when **all** of the following are true:

```text
REAL_MODEL_ENABLED=true
provider is configured
provider is enabled
model is configured
model is enabled
API key is present in environment
request explicitly asks for real model
request source is allowed
task type is allowed
input safety pre-check passes
token/cost guardrails pass
case remains Stage 1 read-only
```

If any condition fails:

```text
do not call external model
record audit/log if appropriate
return deterministic fallback
display clear reason
```

---

# Model Configuration Rules

Do not hardcode one model as the only option.

Use existing governed AI model configuration.

Use:

```text
OPENAI_DEFAULT_MODEL
ai_model_configs.external_model_name
ai_model_configs.model_code
```

Existing configured model codes may include:

```text
OPENAI_GPT_5_4_MINI
```

But the implementation must tolerate model unavailability.

Add or improve provider/model status so the UI can show:

```text
configured model name
model enabled
provider enabled
API key present yes/no
feature flag enabled yes/no
safe_to_invoke yes/no
last failure reason
```

Optional: add a model availability check using the provider SDK/API only when explicitly requested by a status/test endpoint and only when credentials are present.

---

# Environment Variables

Use existing Prompt 20 variables where possible.

Support:

```text
REAL_MODEL_ENABLED=false
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_ORG_ID=
OPENAI_PROJECT_ID=
OPENAI_DEFAULT_MODEL=
OPENAI_REQUEST_TIMEOUT_SECONDS=30
OPENAI_MAX_OUTPUT_TOKENS=1200
OPENAI_REASONING_EFFORT=low
OPENAI_STORE_RESPONSES=false
```

Add optional guardrail variables:

```text
REAL_MODEL_ALLOWED_TASK_TYPES=AGENT_STAGE_1_CHAT,AGENT_INVESTIGATION_QA,AGENT_EVIDENCE_SUMMARY
REAL_MODEL_MAX_INPUT_CHARS=24000
REAL_MODEL_MAX_CONTEXT_ITEMS=40
REAL_MODEL_MAX_DAILY_INVOCATIONS=100
REAL_MODEL_MAX_DAILY_ESTIMATED_COST=10
REAL_MODEL_STAGE1_ONLY=true
```

Defaults must be conservative.

Do not update:

```text
backend/.env
```

Update only:

```text
backend/.env.example
README.md
ARCHITECTURE.md
```

Do not commit API keys.

---

# Backend Services

Extend or create services as needed.

Recommended service:

```text
backend/app/services/agent_model_chat_service.py
```

Responsibilities:

```text
build Stage 1 model context package
select governed provider/model
validate provider readiness
apply input safety pre-check
apply token/cost guardrails
invoke provider through ai_provider_gateway
apply output safety post-check
save assistant message
link ai_invocation_id to message/run
return deterministic fallback if blocked/disabled/failed
record response grounding metadata
```

Reuse existing:

```text
ai_provider_gateway
agent_orchestrator_service
agent_investigation_service
agent_knowledge_service
ai_config routes/services
ai_invocation_logs
ai_guardrail_events
agent_chat_messages
agent_orchestration_runs
```

Do not bypass the provider gateway.

---

# Context Package

For a model-assisted Stage 1 answer, build a compact context package from:

```text
agent case
source object metadata
investigation source summary
linked AMS ticket
linked alert
linked batch run
linked user report
linked diagnostic case
linked monitoring triage
linked operations exception
latest chat messages
evidence timeline summary
evidence items
retrieved knowledge
known errors
action proposals
approved/executed local safe actions
Stage 1/Stage 2 safety state
```

Context must be curated and bounded.

Do not dump unlimited records.

Do not include API keys, secrets, environment variables, or sensitive tokens.

Context item schema:

```text
context_item_id
context_item_type
title
summary
source_id
source_url
timestamp
confidence
```

Context item types:

```text
CASE
SOURCE_OBJECT
AMS_TICKET
ALERT
BATCH_RUN
USER_REPORT
DIAGNOSTIC_CASE
MONITORING_TRIAGE
OPERATIONS_EXCEPTION
EVIDENCE
TIMELINE_EVENT
KNOWLEDGE_CHUNK
KNOWN_ERROR
ACTION_PROPOSAL
ACTION_EXECUTION
CHAT_HISTORY
```

---

# Prompt Governance

Add or update governed prompt templates for:

```text
AGENT_STAGE_1_CHAT
AGENT_INVESTIGATION_QA
AGENT_EVIDENCE_SUMMARY
AGENT_KNOWLEDGE_GROUNDED_ANSWER
```

The system instruction must include:

```text
You are an enterprise AMS support agent operating in Stage 1 read-only mode.
Use only the provided context.
Do not claim to have executed actions.
Do not instruct anyone to run shell commands.
Do not request passwords, tokens, API keys, or secrets.
Do not send customer communications.
Do not post to ServiceNow.
Do not resolve or close production objects.
You may recommend human-reviewed next steps.
You may refer to approved local safe actions only as already recorded.
If evidence is insufficient, say what evidence is missing.
Cite the context items used.
Keep the answer concise and structured.
```

---

# Output Requirements

Real-model answer should return structured response fields.

Preferred response schema:

```json
{
  "answer": "...",
  "likely_cause": "...",
  "evidence_used": [
    {
      "context_item_id": "...",
      "title": "...",
      "reason": "..."
    }
  ],
  "knowledge_used": [
    {
      "context_item_id": "...",
      "title": "...",
      "reason": "..."
    }
  ],
  "recommended_next_steps": [
    "..."
  ],
  "human_review_required": true,
  "actions_executed": 0,
  "stage_mode": "STAGE_1_READ_ONLY",
  "limitations": [
    "..."
  ]
}
```

If structured output is not available or fails:

```text
parse best effort
store raw answer safely
display fallback structure
```

---

# Safety Pre-Check

Before calling the real model, block or fallback for:

```text
request to execute commands
request to run SQL
request to bypass approval
request to post externally
request to send email/customer update
request to close/resolve ticket externally
API keys/secrets/passwords in input
prompt injection telling the model to ignore rules
attempt to reveal hidden instructions
attempt to use tools not available
attempt to perform autonomous remediation
```

For blocked request:

```text
do not call model
record guardrail event
return deterministic safe response
```

---

# Safety Post-Check

After model response, block/fallback if output:

```text
claims an action was executed
contains shell commands as instructions
contains arbitrary SQL
asks for secrets
says it posted to ServiceNow
says it sent a customer update
claims autonomous remediation
recommends bypassing approval
contains unsafe destructive action
```

For blocked output:

```text
do not display unsafe raw output
record guardrail event
return deterministic safe response
```

---

# Token and Cost Guardrails

Add simple guardrails.

Track or estimate:

```text
input character count
context item count
model code
provider code
daily invocation count
token usage if returned by provider
estimated cost if available
```

If over limit:

```text
do not call model
return fallback
record audit reason
```

Do not require exact pricing.

If pricing is unknown:

```text
estimated_cost = null
cost_tracking_status = UNKNOWN_PRICING
```

---

# Backend API Updates

Extend existing agent chat endpoint:

```text
POST /api/v1/agent-chat/sessions/{session_id}/messages
```

Support:

```json
{
  "message_text": "What is the likely cause?",
  "use_real_model": true,
  "provider_code": "OPENAI_RESPONSES",
  "model_code": "OPENAI_GPT_5_4_MINI",
  "task_type": "AGENT_STAGE_1_CHAT",
  "dry_run": false
}
```

Default:

```text
use_real_model=false
dry_run=false
task_type=AGENT_STAGE_1_CHAT
```

If real model is disabled/unavailable:

```text
fallback deterministic response
generation_mode=FALLBACK_DETERMINISTIC or REAL_MODEL_DISABLED
ai_invocation_id set when audit log exists
```

---

## Add model chat endpoints

Add route prefix:

```text
/api/v1/agent-model-chat
```

Expose on:

```text
Full backend 8050
Operations BFF 8062
Agentic BFF 8065
```

Do not expose on:

```text
Business BFF 8061
Simulation BFF 8063
Observability BFF 8064
```

Required endpoints:

```text
GET  /api/v1/agent-model-chat/status
POST /api/v1/agent-model-chat/sessions/{session_id}/preview-context
POST /api/v1/agent-model-chat/sessions/{session_id}/dry-run
POST /api/v1/agent-model-chat/sessions/{session_id}/ask
GET  /api/v1/agent-model-chat/invocations
GET  /api/v1/agent-model-chat/invocations/{invocation_id}
```

Behavior:

## status

Return:

```text
real model feature flag
provider/model status
API key presence yes/no
allowed task types
max context items
max input chars
daily usage summary
safe_to_invoke
reason
```

## preview-context

Build and return the curated context package.

Must not call the model.

## dry-run

Validate context, prompt, provider readiness, safety, and guardrails.

Must not call the model.

## ask

Calls real model only if explicitly requested and all governance checks pass.

Otherwise returns deterministic fallback.

---

# Invocation Audit

Every attempted real-model path should be auditable.

Record:

```text
request_source
case_id
session_id
message_id
task_type
provider_code
model_code
external_model_name
generation_mode
status
safety_status
fallback_used
input_char_count
context_item_count
latency_ms
prompt_token_count
completion_token_count
total_token_count
estimated_cost
guardrail events
error_message
```

Do not record:

```text
API key
secrets
raw environment values
unbounded sensitive payload
```

---

# Agent Chat Message Fields

If needed, extend message schemas/responses to include:

```text
generation_mode
ai_invocation_id
provider_code
model_code
fallback_used
safety_status
evidence_used
knowledge_used
human_review_required
actions_executed
```

Add migration only if required.

Prefer existing fields where already available.

---

# Investigation Workspace Integration

Update Prompt 22 workspace to show:

```text
model status
generation mode for latest agent answer
real-model availability
invocation audit link/details
evidence used by response
knowledge used by response
fallback reason if used
```

Add a panel:

```text
Model-Assisted Chat
```

It should show:

```text
Real model: Off by default
Provider/model readiness
Preview context
Dry run
Ask with governed real model
Fallback status
```

---

# Frontend UI

Update:

```text
frontend/src/pages/AgentInvestigationPages.tsx
frontend/src/pages/AgentChatPages.tsx
```

Add service if useful:

```text
frontend/src/services/agentModelChatApi.ts
```

UI requirements:

```text
real-model status badge
use real model toggle, off by default
provider/model display
preview context button
dry-run button
ask button
fallback reason display
invocation audit link/details
evidence/knowledge used display
Stage 1 read-only warning
credit/cost caution banner
```

Important:

```text
The toggle must be off by default.
Business UI must not show the toggle.
Operations and Agentic may show it.
Full UI may show it.
```

Do not show:

```text
API key entry field
send customer update button
post to ServiceNow button
execute remediation button
shell command capability
```

---

# BFF Exposure

## Full backend

Expose all Prompt 24 routes.

## Operations BFF

Expose:

```text
agent-model-chat status
preview-context
dry-run
ask
invocations
```

## Agentic BFF

Expose all Prompt 24 routes.

## Business BFF

Do not expose agent-model-chat routes.

## Simulation BFF

Do not expose agent-model-chat routes.

## Observability BFF

Do not expose agent-model-chat routes.

---

# Demo Control Integration

Update demo control components/readiness to include:

```text
Governed Stage 1 Model Chat
Model Context Preview
Model Invocation Audit
```

Readiness should check:

```text
http://localhost:8050/api/v1/agent-model-chat/status
```

Do not call the real model during readiness.

---

# Tests

Add backend tests for:

```text
model chat status default disabled
preview-context does not call model
dry-run does not call model
ask with use_real_model=false returns deterministic response
ask with use_real_model=true but feature disabled returns fallback
ask with use_real_model=true but API key missing returns fallback
input safety pre-check blocks shell/SQL/secret/autonomous-remediation request
output safety post-check blocks unsafe mocked response
mocked successful provider call saves assistant message
mocked successful provider call records ai_invocation_id
mocked successful provider call returns evidence_used and knowledge_used
token/context guardrail blocks oversized context
invocation audit list/detail
agent chat endpoint supports real-model fields
investigation workspace shows model metadata in response payload
BFF exposure rules
Business BFF does not expose agent-model-chat
Simulation BFF does not expose agent-model-chat
Observability BFF does not expose agent-model-chat
demo control includes model-chat readiness
no external LLM/API key required
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

# Optional Manual Real-Model Smoke Test

Do not require this for Definition of Done.

Only run if the user intentionally provides a key in the shell environment.

Recommended local approach:

```bash
export REAL_MODEL_ENABLED=true
export OPENAI_API_KEY="..."
export OPENAI_DEFAULT_MODEL="<configured model available to the account>"
```

Then enable provider/model in the governed catalog if your implementation requires it.

Run a single short test only.

Do not commit API keys.

Do not paste API keys into logs.

Do not run repeated model tests.

Do not make this required for CI or local validation.

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

Create or reuse an investigation case:

```bash
TICKET_ID=$(
  curl -sS http://localhost:8050/api/v1/ams/tickets \
  | jq -r 'if type=="array" then (.[0].ticket_id // .[0].id) elif has("items") then (.items[0].ticket_id // .items[0].id) elif has("tickets") then (.tickets[0].ticket_id // .tickets[0].id) else empty end'
)

HANDOFF=$(
  curl -sS -X POST "http://localhost:8050/api/v1/agent-chat/intake/from-ams-ticket/${TICKET_ID}" \
    -H "Content-Type: application/json" \
    -d '{
      "initial_message": "Investigate this AMS ticket and prepare for model-assisted Stage 1 Q&A.",
      "reuse_existing": true,
      "use_real_model": false
    }'
)

echo "$HANDOFF" | jq .

CASE_ID=$(echo "$HANDOFF" | jq -r '.case_id')
SESSION_ID=$(echo "$HANDOFF" | jq -r '.session_id')

echo "$CASE_ID"
echo "$SESSION_ID"
```

Status:

```bash
curl -sS http://localhost:8050/api/v1/agent-model-chat/status | jq .
curl -sS http://localhost:8065/api/v1/agent-model-chat/status | jq .
```

Expected by default:

```text
real_model_enabled=false
safe_to_invoke=false
no API key required
```

Preview context:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-model-chat/sessions/${SESSION_ID}/preview-context" \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "What is the likely cause and what evidence supports it?",
    "task_type": "AGENT_STAGE_1_CHAT"
  }' | jq .
```

Expected:

```text
context package returned
no external model call
case/evidence/knowledge/action context included
bounded item count
```

Dry run:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-model-chat/sessions/${SESSION_ID}/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "What is the likely cause and what evidence supports it?",
    "use_real_model": true,
    "provider_code": "OPENAI_RESPONSES",
    "model_code": "OPENAI_GPT_5_4_MINI",
    "task_type": "AGENT_STAGE_1_CHAT"
  }' | jq .
```

Expected:

```text
validates prompt/context/safety
does not call external model
returns disabled/not safe reason by default
```

Ask with deterministic default:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-model-chat/sessions/${SESSION_ID}/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "What is the likely cause and what should the engineer check next?",
    "use_real_model": false,
    "task_type": "AGENT_STAGE_1_CHAT"
  }' | jq .
```

Expected:

```text
deterministic response
actions_executed=0
no external model call
```

Ask with real model requested but disabled:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-model-chat/sessions/${SESSION_ID}/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "Use the governed real model if available. What is the likely cause?",
    "use_real_model": true,
    "provider_code": "OPENAI_RESPONSES",
    "model_code": "OPENAI_GPT_5_4_MINI",
    "task_type": "AGENT_STAGE_1_CHAT"
  }' | jq .
```

Expected by default:

```text
fallback deterministic response
real model disabled or not safe reason
audit record if implemented
actions_executed=0
```

Invocation audit:

```bash
curl -sS http://localhost:8050/api/v1/agent-model-chat/invocations | jq .
```

BFF exposure:

```bash
curl -sS http://localhost:8062/api/v1/agent-model-chat/status | jq .
curl -sS http://localhost:8065/api/v1/agent-model-chat/status | jq .

curl -i -sS http://localhost:8061/api/v1/agent-model-chat/status | head
curl -i -sS http://localhost:8063/api/v1/agent-model-chat/status | head
curl -i -sS http://localhost:8064/api/v1/agent-model-chat/status | head
```

Expected:

```text
Operations BFF: 200
Agentic BFF: 200
Business BFF: 404
Simulation BFF: 404
Observability BFF: 404
```

---

# Manual UI Validation

Open:

```text
http://localhost:4015/agent-investigations
http://localhost:4015/agent-investigations/<CASE_ID>
http://localhost:4012/agent-investigations/<CASE_ID>
```

Validate:

```text
Model-assisted chat panel visible
real-model toggle off by default
provider/model status visible
Preview Context works
Dry Run works
Ask with deterministic default works
Ask with real model requested but disabled falls back safely
Stage 1 read-only warning visible
actions_executed remains 0
invocation audit details visible where available
no API key input field exists
no remediation/send/post/command controls exist
```

Open Business UI:

```text
http://localhost:4011/agent-model-chat/status
```

Expected:

```text
not available / experience boundary / 404
```

---

# Documentation Updates

Update `README.md` with:

```text
Governed Stage 1 real-model chat overview
how to keep real model disabled
how to preview context
how to dry-run
how to optionally run a single real-model smoke test
credit/cost caution
no API key storage
no autonomous remediation
```

Update `ARCHITECTURE.md` with:

```text
model-assisted Stage 1 chat architecture
context package builder
prompt governance
safety pre-check/post-check
provider gateway usage
invocation audit
deterministic fallback
relationship with Stage 2 approval-gated actions
future real-time user chat path
future Stage 3 boundary
```

Document clearly:

```text
Prompt 24 introduces governed Stage 1 real-model answers only.
It does not make real-model usage the default.
It does not execute actions.
It does not introduce autonomous remediation.
It does not send customer communications.
It does not post to ServiceNow.
It does not require OpenAI API keys for tests.
```

---

# Definition of Done

Prompt 24 is complete only when:

- model chat service exists
- context package builder exists
- model chat status endpoint exists
- preview-context endpoint exists and does not call model
- dry-run endpoint exists and does not call model
- ask endpoint exists
- ask with use_real_model=false remains deterministic
- ask with real model requested but disabled falls back safely
- input safety pre-check blocks unsafe requests
- output safety post-check blocks unsafe model outputs
- token/context guardrails exist
- provider gateway is used for all real calls
- invocation audit exists
- assistant messages include generation metadata
- investigation workspace shows model status/metadata
- Agentic UI has model-assisted chat controls
- Operations UI has model-assisted chat controls
- Business UI does not expose model chat
- BFF exposure rules are respected
- demo control includes model chat readiness
- backend tests pass
- frontend build passes
- demo stack validation passes
- no OpenAI API key is required
- no default external model call occurs
- no autonomous remediation is introduced
- no shell commands are executed
- no arbitrary SQL execution is introduced
- no ServiceNow integration is introduced
- no authentication is introduced
- no Docker Compose change unless justified
- no observability infrastructure change unless justified
- README updated
- ARCHITECTURE.md updated
- Prompt 24 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. Model chat service behavior
5. Context package behavior
6. Prompt governance behavior
7. Safety pre-check behavior
8. Safety post-check behavior
9. Token/cost guardrail behavior
10. Provider gateway behavior
11. Invocation audit behavior
12. Agent chat integration summary
13. Investigation workspace integration summary
14. Backend APIs added
15. BFF exposure summary
16. Frontend routes/pages/controls added
17. Demo control integration summary
18. Backend test results
19. Frontend build results
20. Demo stack validation results
21. Manual API validation results
22. Manual UI validation results
23. Confirmation deterministic/mock remains default
24. Confirmation no real model call occurs by default
25. Confirmation no autonomous remediation was introduced
26. Confirmation no shell command/arbitrary SQL/external system execution was introduced
27. Confirmation no ServiceNow/authentication was introduced
28. TODOs or limitations
29. Recommended Git commit message

Recommended commit message:

```text
feat: add governed stage1 model chat
```

Do not proceed beyond this prompt.
## Implementation record

Prompt 24 is implemented as governed, optional Stage 1 model-assisted chat.
The implementation preserves deterministic/mock defaults, uses the existing
provider gateway, bounds and curates investigation context, applies pre- and
post-call safety checks, records invocation audit metadata, and falls back
safely when any readiness or guardrail condition fails. It does not execute
actions, call external systems by default, send communications, post to
ServiceNow, run shell/SQL/code, or introduce autonomous remediation.
