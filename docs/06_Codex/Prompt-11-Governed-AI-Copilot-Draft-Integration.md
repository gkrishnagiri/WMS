# Prompt 11 – Governed AI Copilot Draft Integration

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

Prompt 07 created application-level observability evidence and support diagnostics.

Prompt 08 created batch jobs and batch failure scenarios.

Prompt 09 created the deterministic AI-native support engineer copilot foundation.

Prompt 10 created governed AI provider configuration, prompt templates, safety policies, mock provider abstraction, invocation logging, usage accounting, and AI configuration UI.

Your task now is to implement:

```text
Governed AI Copilot Draft Integration
```

This prompt connects the existing copilot to the governed AI provider gateway created in Prompt 10.

The integration must continue to use only the deterministic mock provider.

Do not integrate external LLMs yet.

Do not add LangGraph, LiteLLM, OpenAI SDKs, Anthropic SDKs, local model runtimes, vector databases, embeddings, RAG frameworks, autonomous agents, or ServiceNow integration.

---

## Important Clarification

This prompt is **not** the real observability-system prompt.

Prompt 07 already created application-level observability evidence in PostgreSQL.

Real runtime instrumentation and external observability backend integration should come later.

Do not modify:

```text
docker-compose.yml
observability/
Prometheus config
Grafana config
OpenTelemetry Collector config
```

The expected future sequence is:

```text
Prompt 11 – Governed AI Copilot Draft Integration
Prompt 12 – Runtime Observability Instrumentation Foundation
Prompt 13 – Local Observability Stack Expansion
```

Prompt 11 must focus only on governed AI usage inside the copilot.

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
- Batch failure support flows
- Deterministic support engineer copilot
- Copilot sessions
- Copilot context snapshots
- Copilot recommendations
- Copilot action plans
- Copilot deterministic drafts
- Governed AI configuration
- Mock AI provider
- Prompt template registry
- Safety policy registry
- Invocation logs
- Guardrail events
- Usage accounting
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
feat: add governed ai provider configuration foundation
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

You may create a new Alembic migration only if required.

Prefer using existing Prompt 09 and Prompt 10 tables if no schema change is necessary.

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

The only AI-like execution allowed is the existing deterministic mock provider from Prompt 10.

No external network LLM call should be made.

---

# Objective

Integrate the governed AI provider gateway into the copilot workbench.

Prompt 09 created deterministic copilot-generated artifacts.

Prompt 10 created governed AI configuration and mock provider invocation.

Prompt 11 should allow the copilot to generate governed mock-AI drafts through the provider gateway while preserving all safety controls and auditability.

The intended flow:

```text
Support engineer opens copilot session
        ↓
Copilot builds context snapshot
        ↓
Engineer selects governed AI draft generation
        ↓
Copilot sends context to AI provider gateway
        ↓
Safety policy is evaluated
        ↓
Mock provider generates deterministic governed response
        ↓
Invocation is logged
        ↓
Usage is updated
        ↓
Copilot message is created
        ↓
Engineer reviews draft manually
```

The copilot must not apply drafts automatically.

The copilot must not close tickets, resolve alerts, resolve diagnostics, suppress alerts, send emails, post messages, or modify production data.

---

# Architectural Intent

This prompt creates the first bridge between:

```text
Copilot
```

and:

```text
Governed AI Configuration
```

But it remains controlled:

```text
No real LLM
No autonomous action
No external call
No tool execution by model
No production change
```

The copilot should support both:

```text
existing deterministic draft generation
governed mock-AI draft generation
```

Do not remove or replace the deterministic draft methods from Prompt 09.

Add governed AI as a parallel, optional capability.

---

# Scope

Implement:

1. Copilot governed AI generation endpoints
2. Request mapping from copilot context snapshot to AI gateway input
3. Governed AI work note draft generation
4. Governed AI customer update draft generation
5. Governed AI investigation checklist generation
6. Governed AI context summary generation
7. Copilot message records linked to AI invocation metadata where practical
8. Frontend controls to generate governed AI drafts
9. AI invocation visibility from copilot session detail
10. Backend tests
11. Documentation updates

Do not implement:

- real external LLM calls
- streaming
- chat memory beyond existing copilot session state
- RAG
- embeddings
- vector search
- autonomous remediation
- automatic ticket updates
- external notifications
- ServiceNow integration
- real observability infrastructure changes

---

# Schema Guidance

Prefer not to create a new migration unless needed.

If existing `copilot_messages` can store governed AI drafts, use it.

If existing `ai_invocation_logs` can be referenced through message metadata, use that.

If a schema change is necessary, keep it minimal.

Acceptable minimal schema addition:

```text
copilot_messages.ai_invocation_id nullable FK to ai_invocation_logs.id
copilot_messages.generation_mode text nullable
```

Suggested `generation_mode` values:

```text
DETERMINISTIC
GOVERNED_AI_MOCK
```

If adding these fields is too invasive, store invocation number in message content or metadata only if a suitable JSON field already exists. Prefer proper fields if easy.

Do not create unnecessary tables.

---

# Backend Integration

Create or extend services such as:

```text
backend/app/services/copilot_ai_service.py
```

or add to existing copilot service if consistent.

The service should:

1. Load copilot session
2. Load latest context snapshot
3. Build safe input payload
4. Select task type and prompt template
5. Call AI provider gateway
6. Receive governed mock response
7. Create copilot message
8. Store or reference invocation metadata
9. Return generated message and invocation summary

---

## Supported Governed AI Draft Types

Implement these draft types:

```text
CONTEXT_SUMMARY
WORK_NOTE_DRAFT
CUSTOMER_UPDATE_DRAFT
INVESTIGATION_CHECKLIST
```

Map them to Prompt 10 task types and templates:

```text
CONTEXT_SUMMARY           -> COPILOT_CONTEXT_SUMMARY      -> TPL-COPILOT-CONTEXT-SUMMARY
WORK_NOTE_DRAFT           -> WORK_NOTE_DRAFT              -> TPL-WORK-NOTE-DRAFT
CUSTOMER_UPDATE_DRAFT     -> CUSTOMER_UPDATE_DRAFT        -> TPL-CUSTOMER-UPDATE-DRAFT
INVESTIGATION_CHECKLIST   -> INVESTIGATION_CHECKLIST      -> TPL-INVESTIGATION-CHECKLIST
```

Use model:

```text
MOCK-SUPPORT-COPILOT-001
```

Use request source:

```text
COPILOT_SESSION
```

Use request source id:

```text
copilot session id
```

---

# Safe Input Payload

When sending copilot context to the AI provider gateway, include only safe summarized context.

Do not dump full raw database rows if avoidable.

Suggested payload:

```json
{
  "session_number": "COPILOT-20260822-0001",
  "session_title": "Analyze failed batch run",
  "primary_entity_type": "BATCH_RUN",
  "severity": "HIGH",
  "confidence_level": "MEDIUM",
  "context_summary": "...",
  "impact_summary": "...",
  "technical_summary": "...",
  "business_summary": "...",
  "timeline_summary": "...",
  "evidence_summary": "...",
  "related_entities": []
}
```

Do not include secrets.

Do not include environment variables.

Do not include credentials.

Do not include raw connection strings.

---

# Safety Behavior

The AI gateway from Prompt 10 must evaluate safety before mock invocation.

If blocked:

- do not create a normal copilot draft
- create a copilot message of type `GOVERNED_AI_BLOCKED` or equivalent if schema allows
- include blocked reason
- include invocation number if available
- do not apply anything to tickets or alerts

If warned:

- create the draft
- show safety status `WARNED`
- include warning summary

If passed:

- create the draft
- show safety status `PASSED`

---

# Backend APIs

Extend copilot APIs.

Use existing prefix:

```text
/api/v1/copilot
```

Add:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-governed-context-summary
POST /api/v1/copilot/sessions/{session_id}/generate-governed-work-note
POST /api/v1/copilot/sessions/{session_id}/generate-governed-customer-update
POST /api/v1/copilot/sessions/{session_id}/generate-governed-investigation-checklist
GET  /api/v1/copilot/sessions/{session_id}/ai-invocations
```

Optional convenience endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-governed-draft
```

Request:

```json
{
  "draft_type": "WORK_NOTE_DRAFT"
}
```

If implemented, keep the specific endpoints too or document clearly.

---

## Generate Governed Context Summary

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-governed-context-summary
```

Behavior:

- require latest context snapshot
- call AI provider gateway with task type `COPILOT_CONTEXT_SUMMARY`
- create copilot message type `CONTEXT_SUMMARY`
- generation mode should be `GOVERNED_AI_MOCK`
- return message and AI invocation summary

---

## Generate Governed Work Note

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-governed-work-note
```

Behavior:

- require latest context snapshot
- call AI provider gateway with task type `WORK_NOTE_DRAFT`
- create copilot message type `WORK_NOTE_DRAFT`
- do not apply note to AMS ticket
- return message and AI invocation summary

---

## Generate Governed Customer Update

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-governed-customer-update
```

Behavior:

- require latest context snapshot
- call AI provider gateway with task type `CUSTOMER_UPDATE_DRAFT`
- create copilot message type `CUSTOMER_UPDATE_DRAFT`
- do not send externally
- return message and AI invocation summary

---

## Generate Governed Investigation Checklist

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-governed-investigation-checklist
```

Behavior:

- require latest context snapshot
- call AI provider gateway with task type `INVESTIGATION_CHECKLIST`
- create copilot message type `INVESTIGATION_CHECKLIST`
- return message and AI invocation summary

---

## Copilot Session AI Invocations

Endpoint:

```text
GET /api/v1/copilot/sessions/{session_id}/ai-invocations
```

Behavior:

- return AI invocation logs where:
  - `request_source = COPILOT_SESSION`
  - `request_source_id = session_id`
- newest first

---

# Frontend Implementation

Extend the existing copilot frontend.

Do not replace the application shell.

Do not change frontend port `4001`.

Do not change backend base URL away from `http://localhost:8050`.

---

## Copilot Session Detail Page

Route:

```text
/copilot/sessions/:sessionId
```

Add a new section:

```text
Governed AI Drafts
```

Display explanation:

```text
These drafts are generated through the governed AI provider gateway using the deterministic mock provider. No external LLM call is made.
```

Add buttons:

```text
Generate Governed Context Summary
Generate Governed Work Note
Generate Governed Customer Update
Generate Governed Investigation Checklist
```

After generation, show:

```text
message title
message content
generation mode
safety status
invocation number
task type
estimated tokens
blocked reason if any
```

---

## AI Invocation Panel in Copilot Session

Add a section:

```text
AI Invocation Audit
```

Fetch:

```text
GET /api/v1/copilot/sessions/{session_id}/ai-invocations
```

Display table:

```text
invocation number
task type
status
safety status
tokens
cost
created at
```

Link or reference the AI Invocations admin page if simple.

---

## Copilot Analyze Flow

Do not break existing `/copilot/analyze`.

Optional enhancement:

After analyze creates a session and deterministic checklist, allow user to open the session and run governed AI drafts manually.

Do not automatically run governed AI during analyze unless the API explicitly requests it.

---

# Frontend API Client

Extend:

```text
frontend/src/services/copilotApi.ts
```

Add methods for:

```text
generateGovernedContextSummary
generateGovernedWorkNote
generateGovernedCustomerUpdate
generateGovernedInvestigationChecklist
getSessionAiInvocations
```

Use TanStack Query mutations.

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
10. Existing AI config tests still pass
11. Governed AI context summary requires context snapshot
12. Governed AI work note requires context snapshot
13. Governed AI context summary creates AI invocation log
14. Governed AI work note creates copilot message
15. Governed AI customer update creates copilot message
16. Governed AI investigation checklist creates copilot message
17. Generated messages use generation mode `GOVERNED_AI_MOCK` if field exists
18. Copilot AI invocations endpoint returns session invocations
19. Safety blocked governed AI draft does not create normal draft
20. Existing deterministic copilot draft endpoints still work
21. Governed AI generation does not close tickets
22. Governed AI generation does not resolve alerts
23. No external LLM SDK dependency is required
24. Disabled non-mock providers are not invoked

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

- Prompt 11 governed AI copilot draft integration summary
- governed AI draft types
- mock provider usage
- safety behavior
- AI invocation audit from copilot sessions
- confirmation that deterministic copilot still exists
- new APIs
- frontend updates
- validation commands
- backend port `8050`
- frontend port `4001`
- explicit deferred items:
  - real external LLM calls
  - LangGraph
  - LiteLLM
  - RAG
  - embeddings/vector store
  - autonomous remediation
  - ServiceNow integration
  - runtime observability instrumentation
  - observability stack expansion

Update `ARCHITECTURE.md` with:

- copilot-to-AI-provider-gateway integration
- governed mock provider flow
- safety policy evaluation before draft generation
- invocation logging and usage accounting from copilot
- continued separation from autonomous execution
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
curl -sS http://localhost:8050/api/v1/copilot/summary | jq .
curl -sS http://localhost:8050/api/v1/ai-config/summary | jq .
```

Create a failed batch run for analysis:

```bash
BATCH_RUN_ID=$(
  curl -sS -X POST http://localhost:8050/api/v1/batch/simulations/inventory-reconciliation-failure \
    -H "Content-Type: application/json" \
    -d '{"create_exception": true, "create_ticket": true, "create_observability": true}' \
  | jq -r '.id // .batch_run_id // .run.id'
)

echo "$BATCH_RUN_ID"
```

Create copilot session through analyze:

```bash
COPILOT_SESSION_ID=$(
  curl -sS -X POST http://localhost:8050/api/v1/copilot/analyze \
    -H "Content-Type: application/json" \
    -d "{
      \"entity_type\": \"BATCH_RUN\",
      \"entity_id\": \"${BATCH_RUN_ID}\",
      \"title\": \"Analyze failed inventory reconciliation batch\"
    }" \
  | jq -r '.id // .session.id // .session_id'
)

echo "$COPILOT_SESSION_ID"
```

Generate governed AI drafts:

```bash
curl -sS -X POST http://localhost:8050/api/v1/copilot/sessions/${COPILOT_SESSION_ID}/generate-governed-context-summary \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

curl -sS -X POST http://localhost:8050/api/v1/copilot/sessions/${COPILOT_SESSION_ID}/generate-governed-work-note \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

curl -sS -X POST http://localhost:8050/api/v1/copilot/sessions/${COPILOT_SESSION_ID}/generate-governed-customer-update \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

curl -sS -X POST http://localhost:8050/api/v1/copilot/sessions/${COPILOT_SESSION_ID}/generate-governed-investigation-checklist \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
```

Validate AI invocation audit:

```bash
curl -sS http://localhost:8050/api/v1/copilot/sessions/${COPILOT_SESSION_ID}/ai-invocations | jq .
curl -sS http://localhost:8050/api/v1/ai-config/invocations | jq .
curl -sS http://localhost:8050/api/v1/ai-config/usage-daily | jq .
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
http://localhost:4001/copilot
http://localhost:4001/copilot/sessions
http://localhost:4001/copilot/analyze
http://localhost:4001/ai-config/invocations
http://localhost:4001/ai-config/usage
```

Manual UI validation:

```text
Open Batch Simulations
Run Inventory Reconciliation Failure with exception/ticket/observability enabled
Copy the generated batch run ID
Open Copilot Analyze
Analyze BATCH_RUN
Open created Copilot Session
Confirm deterministic context and recommendations still appear
Generate Governed Context Summary
Generate Governed Work Note
Generate Governed Customer Update
Generate Governed Investigation Checklist
Confirm each draft appears in the session
Confirm AI Invocation Audit shows records
Open AI Invocations
Confirm COPILOT_SESSION invocations are visible
Open AI Usage
Confirm usage aggregate updated
Confirm no ticket was automatically updated
Confirm no alert was automatically resolved
Confirm no external LLM call occurred
```

---

# Definition of Done

Prompt 11 is complete only when:

- governed AI generation works from copilot sessions
- existing deterministic copilot generation still works
- governed context summary generation works
- governed work note generation works
- governed customer update generation works
- governed investigation checklist generation works
- AI provider gateway is used
- mock provider is used
- AI safety policy is evaluated
- AI invocation logs are created
- AI usage is updated
- copilot messages are created for generated drafts
- copilot session AI invocation audit endpoint works
- frontend copilot session detail shows governed AI draft controls
- frontend copilot session detail shows AI invocation audit
- existing AI config pages still work
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
- no external LLM call is made

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Alembic migration name, or confirmation no migration was needed
4. Backend copilot governed AI APIs added
5. Frontend updates added
6. Backend validation results
7. Frontend validation results
8. Manual governed AI copilot validation result
9. AI invocation audit validation result
10. Safety behavior validation result
11. Confirmation that infrastructure files were not modified
12. Confirmation that no external LLM SDK/agent framework was introduced
13. Confirmation that no external LLM call is made
14. Any TODOs
15. Recommended Git commit message

Recommended commit message:

```text
feat: add governed ai copilot draft integration
```

Do not proceed beyond this prompt.