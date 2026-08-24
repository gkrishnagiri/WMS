# Prompt 21 – Contextual Agent Investigation Handoff

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 18 added:

```text
Agent Chat and Case Intake Foundation
```

Prompt 19 added:

```text
Knowledge and RAG Foundation
```

Prompt 20 added:

```text
Governed Real Model Provider Integration Foundation
```

Your task now is to implement:

```text
Contextual Agent Investigation Handoff
```

---

## Business Goal

The platform should now demonstrate how a service engineer can move from any operational signal into an agent-assisted investigation.

Today, the agent chat exists, but users still need to manually start agent sessions.

Prompt 21 should add contextual handoffs from operational pages such as:

```text
AMS ticket
Observability alert
Batch run
User report
Monitoring triage case
Operations exception
Diagnostic case
```

into:

```text
Agent case
Agent chat session
Deterministic Stage 1 investigation
Evidence bundle
Knowledge retrieval
Recommended next steps
```

This is the customer demo story:

```text
An issue appears in operations
        ->
Engineer clicks "Investigate with Agent"
        ->
Agent opens a contextual investigation
        ->
Agent gathers operational evidence
        ->
Agent retrieves relevant runbooks / known errors
        ->
Agent provides Stage 1 read-only guidance
        ->
Engineer continues chat from the investigation context
```

---

## Current Baseline

The system currently includes:

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

Existing agent capabilities include:

```text
Agent cases
Agent chat sessions
Agent messages
Orchestration runs
Evidence items
Action proposals
Deterministic Stage 1 orchestrator
Knowledge retrieval
Known-error retrieval
Optional governed real-model foundation, disabled by default
```

Existing contextual intake endpoints already include at least:

```text
POST /api/v1/agent-chat/intake/from-ams-ticket/{ticket_id}
POST /api/v1/agent-chat/intake/from-observability-alert/{event_id}
POST /api/v1/agent-chat/intake/from-batch-run/{run_id}
```

Prompt 21 should expand and integrate these into the UI and operations workflows.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve all existing frontend and backend/BFF URLs.

You must preserve mock/deterministic behavior as the default.

You must not enable real model calls by default.

You must not require an OpenAI API key.

You must not call an external LLM in tests.

You must not introduce autonomous remediation.

You must not execute shell commands from the agent.

You must not execute remediation actions from the agent.

You must not introduce ServiceNow integration.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

You must not break Prompt 18, 19, or 20 behavior.

The handoff must clearly remain:

```text
Stage 1 read-only investigation
No remediation executed
No external LLM call by default
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

Implement contextual agent handoff from operational objects.

The user should be able to click:

```text
Investigate with Agent
```

from supported detail pages.

The system should:

```text
create or reuse an agent case
create or reuse an agent chat session
link the source object
gather contextual evidence
retrieve relevant knowledge
generate Stage 1 guidance
navigate to the agent chat session
show the source context in the agent UI
preserve auditability
avoid duplicate agent cases when appropriate
```

---

# Supported Source Objects

Implement contextual handoff for the following, in priority order.

## 1. AMS ticket

Source:

```text
AMS ticket detail page
```

Handoff behavior:

```text
Create agent case type AMS_TICKET
Link linked_ams_ticket_id
Retrieve ticket details and ticket events
Retrieve related user report / alert / batch / diagnostic context if linked
Retrieve relevant knowledge
Open agent chat session
```

Frontend button:

```text
Investigate with Agent
```

---

## 2. Observability alert event

Source:

```text
Observability alert event detail page
```

Handoff behavior:

```text
Create agent case type OBSERVABILITY_ALERT
Link linked_alert_event_id
Retrieve alert event details
Retrieve alert evidence
Retrieve linked AMS ticket if exists
Retrieve relevant knowledge
Open agent chat session
```

Frontend button:

```text
Investigate with Agent
```

---

## 3. Batch run

Source:

```text
Batch run detail page
```

Handoff behavior:

```text
Create agent case type BATCH_FAILURE
Link linked_batch_run_id
Retrieve batch run details
Retrieve batch run events
Retrieve linked exception / diagnostic / AMS ticket if exists
Retrieve batch recovery knowledge
Open agent chat session
```

Frontend button:

```text
Investigate with Agent
```

---

## 4. User report

Source:

```text
AMS user report detail page
```

Handoff behavior:

```text
Create agent case type USER_ISSUE
Link linked_user_report_id
Retrieve user report details
Retrieve linked AMS ticket if exists
Retrieve warehouse/order/shipment context if available
Retrieve relevant knowledge
Open agent chat session
```

Frontend button:

```text
Investigate with Agent
```

---

## 5. Diagnostic case

Source:

```text
Observability diagnostic case detail page
```

Handoff behavior:

```text
Create agent case type DIAGNOSTIC_CASE
Link linked_diagnostic_case_id
Retrieve diagnostic case details
Retrieve diagnostic evidence
Retrieve related trace/log/metric records if available
Retrieve relevant knowledge
Open agent chat session
```

Frontend button:

```text
Investigate with Agent
```

---

## 6. Monitoring triage case

Source:

```text
Monitoring triage detail page
```

Handoff behavior:

```text
Create agent case type MONITORING_TRIAGE
Link monitoring triage context
Retrieve triage case details
Retrieve linked monitoring alerts
Retrieve linked AMS ticket if exists
Retrieve relevant knowledge
Open agent chat session
```

Frontend button:

```text
Investigate with Agent
```

If the existing agent case model does not have a dedicated field for monitoring triage, add a safe optional field through migration or store a structured source reference if already supported.

---

## 7. Operations exception

Source:

```text
Operations exception detail page or exception list row
```

Handoff behavior:

```text
Create agent case type OPERATIONS_EXCEPTION or SERVICE_ENGINEER_INVESTIGATION
Link exception context
Retrieve exception details
Retrieve linked AMS ticket if exists
Retrieve relevant knowledge
Open agent chat session
```

Frontend button:

```text
Investigate with Agent
```

If a full detail page does not exist, add the action at list/table level.

---

# Data Model

Add a migration only if needed.

Suggested migration if needed:

```text
0015_agent_contextual_handoff
```

Potential additions to `agent_cases`:

```text
linked_monitoring_triage_case_id
linked_operations_exception_id
source_object_type
source_object_id
source_object_display
source_object_url
```

Recommended approach:

Use explicit fields where already available:

```text
linked_ams_ticket_id
linked_user_report_id
linked_alert_event_id
linked_batch_run_id
linked_diagnostic_case_id
```

For new source types, prefer a generic source reference if it avoids repeated schema churn:

```text
source_object_type
source_object_id
source_object_display
source_object_url
```

Do not remove existing fields.

Do not break existing agent cases.

---

# Handoff Reuse / Deduplication

Implement safe handoff deduplication.

When a user clicks “Investigate with Agent” for the same source object:

```text
if an OPEN or IN_PROGRESS agent case already exists for that source
  reuse the existing case
  create a new chat session only if needed
  or return the existing active session
else
  create a new case and session
```

This prevents duplicate agent cases for the same AMS ticket / alert / batch run.

The response should indicate:

```text
created_new_case: true/false
created_new_session: true/false
reused_existing_case: true/false
```

---

# Backend Service

Extend:

```text
backend/app/services/agent_orchestrator_service.py
```

or add:

```text
backend/app/services/agent_handoff_service.py
```

Preferred: add a dedicated handoff service that uses the orchestrator.

Suggested service:

```text
AgentHandoffService
```

Responsibilities:

```text
validate source object exists
derive case title and description
create or reuse agent case
create or reuse chat session
create source-specific initial message
call deterministic orchestrator
return handoff response with navigation target
```

The orchestrator remains responsible for:

```text
classification
evidence retrieval
knowledge retrieval
guidance generation
orchestration run creation
agent response
```

---

# Backend APIs

Extend existing route prefix:

```text
/api/v1/agent-chat/intake
```

Required endpoints:

```text
POST /api/v1/agent-chat/intake/from-ams-ticket/{ticket_id}
POST /api/v1/agent-chat/intake/from-observability-alert/{event_id}
POST /api/v1/agent-chat/intake/from-batch-run/{run_id}
POST /api/v1/agent-chat/intake/from-user-report/{report_id}
POST /api/v1/agent-chat/intake/from-diagnostic-case/{diagnostic_case_id}
POST /api/v1/agent-chat/intake/from-monitoring-triage/{triage_case_id}
POST /api/v1/agent-chat/intake/from-operations-exception/{exception_id}
```

Add optional body:

```json
{
  "initial_message": "Investigate this issue and summarize likely next steps.",
  "reuse_existing": true,
  "use_real_model": false,
  "provider_code": null,
  "model_code": null
}
```

Defaults:

```text
reuse_existing=true
use_real_model=false
```

Real model behavior:

```text
Even if use_real_model=true, existing Prompt 20 governance applies.
Default remains deterministic.
No external call occurs unless explicitly enabled and configured.
```

---

## Handoff response shape

Return:

```json
{
  "case_id": "AGC-...",
  "session_id": "AGS-...",
  "source_object_type": "AMS_TICKET",
  "source_object_id": "AMS-...",
  "created_new_case": true,
  "created_new_session": true,
  "reused_existing_case": false,
  "stage_mode": "STAGE_1_READ_ONLY",
  "generation_mode": "DETERMINISTIC_AGENT",
  "actions_executed": 0,
  "agent_chat_url": "/agent-chat/sessions/AGS-...",
  "message": "Agent investigation started in Stage 1 read-only mode."
}
```

---

# BFF Exposure

Expose contextual handoff endpoints on:

## Full backend

```text
/api/v1/agent-chat/intake/*
```

## Operations BFF

```text
/api/v1/agent-chat/intake/*
```

## Agentic BFF

```text
/api/v1/agent-chat/intake/*
```

## Business BFF

Expose only:

```text
/api/v1/agent-chat/intake/from-user-report/*
```

and any existing user-facing issue intake routes.

Do not expose operational investigation handoffs on Business BFF if route-level filtering is practical.

## Simulation BFF

Do not expose agent-chat handoff endpoints.

## Observability BFF

Optional:

Expose observability-alert and diagnostic-case handoff if useful for observability control plane.

If exposed:

```text
/api/v1/agent-chat/intake/from-observability-alert/*
/api/v1/agent-chat/intake/from-diagnostic-case/*
```

Do not expose all agent-chat APIs unless already intentionally exposed.

Document exposure clearly.

---

# Frontend Integration

Add “Investigate with Agent” actions to the relevant UI pages.

Suggested shared component:

```text
frontend/src/components/agent/InvestigateWithAgentButton.tsx
```

or similar.

The component should:

```text
accept source_type
accept source_id
accept optional label
call the correct intake endpoint
show loading state
show error state
navigate to returned agent_chat_url
```

---

## Required frontend pages/actions

Add button or action to:

```text
AMS ticket detail
Observability alert event detail
Batch run detail
AMS user report detail
Observability diagnostic case detail
Monitoring triage case detail
Operations exception list/detail
```

If a specific detail page is missing, add the button in the nearest list/table row or document TODO.

---

## Navigation after handoff

After successful handoff:

```text
navigate to /agent-chat/sessions/{session_id}
```

Use the current experience routing rules.

Examples:

```text
Operations UI should navigate within http://localhost:4012
Agentic UI should navigate within http://localhost:4015
Full UI should navigate within http://localhost:4001
```

If the current experience does not own the session detail route, navigate to Agentic UI URL or show a link.

Preferred for Operations UI:

```text
Operations experience should have access to /agent-chat/sessions/:sessionId
```

---

# Agent Chat UI Enhancements

Update agent case/session detail pages to display:

```text
source object type
source object id
source object display
source object link
created/reused handoff metadata
linked AMS ticket
linked alert
linked batch run
linked user report
linked diagnostic case
```

Add a section:

```text
Investigation Source
```

Add clear banner:

```text
This investigation is Stage 1 read-only. The agent has not executed any remediation action.
```

---

# Contextual Evidence Improvements

Improve evidence retrieval for handoff contexts.

At minimum:

## AMS ticket handoff should include

```text
AMS ticket summary
AMS ticket lifecycle events
linked alert/ticket/source data if available
recent related tickets by category/module if simple
```

## Observability alert handoff should include

```text
alert event
alert evidence items
linked AMS ticket if created
relevant observability rule
```

## Batch run handoff should include

```text
batch run summary
batch step runs
batch events
linked AMS ticket / exception / diagnostic if available
batch runbook knowledge
```

## User report handoff should include

```text
user report summary
linked AMS ticket if available
reported issue text
related order/shipment hints if available
```

## Diagnostic case handoff should include

```text
diagnostic case summary
diagnostic evidence
related traces/logs/metrics if available
```

Keep the implementation simple but useful.

---

# Demo Control Integration

Update demo control summary/readiness/components to include:

```text
Contextual Agent Handoff
AMS-to-Agent Handoff
Alert-to-Agent Handoff
Batch-to-Agent Handoff
```

Readiness should check:

```text
http://localhost:8050/api/v1/agent-chat/summary
```

and optionally verify route registration using a safe endpoint if available.

Do not create or trigger real handoff during readiness checks.

---

# Tests

Add backend tests for:

```text
handoff from AMS ticket creates agent case/session
handoff from AMS ticket reuses existing case when reuse_existing=true
handoff from observability alert creates evidence
handoff from batch run creates evidence
handoff from user report works
handoff from diagnostic case works if implemented
handoff from monitoring triage works if implemented
handoff from operations exception works if implemented
agent response remains Stage 1 read-only
actions_executed remains 0
use_real_model=false by default
use_real_model=true falls back safely when real model disabled
BFF exposure rules
Business BFF does not expose operational handoff endpoints
Simulation BFF does not expose handoff endpoints
agent chat session detail includes source metadata
demo control includes contextual handoff readiness
```

Tests must not require:

```text
external LLM
OpenAI API key
Prometheus/Grafana/Tempo/Loki
ServiceNow
browser automation
```

Existing tests must continue to pass.

---

# Frontend Build Validation

No frontend test framework is required, but:

```bash
npm run build
```

must pass.

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

## AMS ticket handoff

Use an existing AMS ticket ID from the API.

```bash
curl -sS http://localhost:8050/api/v1/ams/tickets | jq '.[0]'
```

Then:

```bash
curl -sS -X POST http://localhost:8050/api/v1/agent-chat/intake/from-ams-ticket/<TICKET_ID> \
  -H "Content-Type: application/json" \
  -d '{
    "initial_message": "Investigate this AMS ticket and summarize likely next steps.",
    "reuse_existing": true,
    "use_real_model": false
  }' | jq .
```

Expected:

```text
case_id returned
session_id returned
stage_mode STAGE_1_READ_ONLY
actions_executed 0
agent_chat_url returned
```

Run the same command again.

Expected:

```text
reused_existing_case true
no duplicate case explosion
```

---

## Observability alert handoff

```bash
curl -sS http://localhost:8050/api/v1/observability-alerts/events | jq '.[0]'
```

Then:

```bash
curl -sS -X POST http://localhost:8050/api/v1/agent-chat/intake/from-observability-alert/<EVENT_ID> \
  -H "Content-Type: application/json" \
  -d '{
    "initial_message": "Investigate this observability alert and identify likely next steps.",
    "reuse_existing": true,
    "use_real_model": false
  }' | jq .
```

---

## Batch run handoff

```bash
curl -sS http://localhost:8050/api/v1/batch/runs | jq '.[0]'
```

Then:

```bash
curl -sS -X POST http://localhost:8050/api/v1/agent-chat/intake/from-batch-run/<RUN_ID> \
  -H "Content-Type: application/json" \
  -d '{
    "initial_message": "Investigate this batch run and summarize recovery guidance.",
    "reuse_existing": true,
    "use_real_model": false
  }' | jq .
```

---

## User report handoff

```bash
curl -sS http://localhost:8050/api/v1/ams/user-reports | jq '.[0]'
```

Then:

```bash
curl -sS -X POST http://localhost:8050/api/v1/agent-chat/intake/from-user-report/<REPORT_ID> \
  -H "Content-Type: application/json" \
  -d '{
    "initial_message": "Investigate this user-reported issue and summarize guidance.",
    "reuse_existing": true,
    "use_real_model": false
  }' | jq .
```

---

## BFF exposure validation

```bash
curl -sS -X POST http://localhost:8062/api/v1/agent-chat/intake/from-ams-ticket/<TICKET_ID> \
  -H "Content-Type: application/json" \
  -d '{"reuse_existing": true, "use_real_model": false}' | jq .

curl -sS -X POST http://localhost:8065/api/v1/agent-chat/intake/from-ams-ticket/<TICKET_ID> \
  -H "Content-Type: application/json" \
  -d '{"reuse_existing": true, "use_real_model": false}' | jq .

curl -i -sS -X POST http://localhost:8063/api/v1/agent-chat/intake/from-ams-ticket/<TICKET_ID> \
  -H "Content-Type: application/json" \
  -d '{"reuse_existing": true, "use_real_model": false}' | head
```

Expected:

```text
Operations BFF: works
Agentic BFF: works
Simulation BFF: 404
```

Business BFF operational handoff should be unavailable:

```bash
curl -i -sS -X POST http://localhost:8061/api/v1/agent-chat/intake/from-ams-ticket/<TICKET_ID> \
  -H "Content-Type: application/json" \
  -d '{"reuse_existing": true, "use_real_model": false}' | head
```

Expected:

```text
404 Not Found
```

---

# Manual UI Validation

Open Operations UI:

```text
http://localhost:4012/ams/tickets
```

Open a ticket detail page.

Validate:

```text
Investigate with Agent button appears
Click creates/reuses agent investigation
Navigates to /agent-chat/sessions/{sessionId}
Agent response is visible
Investigation Source section is visible
Evidence and knowledge are visible
Stage 1 read-only warning is visible
```

Open Observability Alert UI:

```text
http://localhost:4014/observability-alerts/events
```

Validate:

```text
alert event detail has Investigate with Agent
handoff opens agent session
alert evidence appears in agent case evidence
```

Open Batch UI:

```text
http://localhost:4013/batch/runs
```

or Operations UI if batch runs are visible there.

Validate:

```text
batch run detail has Investigate with Agent
handoff opens agent session
batch evidence and batch knowledge appear
```

Open Business UI:

```text
http://localhost:4011/ams/user-reports
```

or the available user report route.

Validate:

```text
user report can be handed off to user-facing agent help if exposed
operational handoff controls are not exposed to business users
```

---

# Documentation Updates

Update `README.md` with:

```text
contextual agent handoff overview
supported source objects
manual API examples
manual UI demo flow
BFF exposure
Stage 1 safety posture
real model disabled by default
no remediation execution
```

Update `ARCHITECTURE.md` with:

```text
contextual handoff architecture
source object to agent case/session flow
handoff reuse/deduplication
evidence bundle flow
knowledge retrieval flow
future Stage 2 approval-gated action path
future ServiceNow handoff path
```

Document clearly:

```text
Prompt 21 adds contextual investigation handoff only.
It does not add autonomous remediation.
It does not enable real model calls by default.
It does not execute actions.
It does not integrate with ServiceNow.
```

---

# Definition of Done

Prompt 21 is complete only when:

- handoff service exists
- AMS ticket handoff works
- observability alert handoff works
- batch run handoff works
- user report handoff works
- diagnostic case handoff works if page/API exists
- monitoring triage handoff works if page/API exists
- operations exception handoff works if page/API exists
- handoff creates or reuses agent case
- handoff creates or reuses agent session
- source object metadata is stored
- evidence is gathered
- knowledge retrieval is triggered
- Stage 1 guidance is generated
- actions_executed remains 0
- real model remains off by default
- duplicate handoff suppression/reuse works
- frontend Investigate with Agent button exists on supported pages
- agent session page shows Investigation Source
- BFF exposure rules are respected
- demo control includes contextual handoff readiness
- backend tests pass
- frontend build passes
- demo stack validation passes
- no OpenAI API key is required
- no default external model call occurs
- no autonomous remediation is introduced
- no ServiceNow integration is introduced
- no authentication is introduced
- no Docker Compose change unless justified
- no observability infrastructure change unless justified
- README updated
- ARCHITECTURE.md updated
- Prompt 21 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. Handoff service behavior
5. Supported source object handoffs
6. Handoff reuse/deduplication behavior
7. Evidence retrieval summary
8. Knowledge retrieval summary
9. Agent response behavior
10. Backend APIs added/extended
11. BFF exposure summary
12. Frontend buttons/pages added
13. Agent chat UI enhancements
14. Demo control integration summary
15. Backend test results
16. Frontend build results
17. Demo stack validation results
18. Manual API validation results
19. Manual UI validation results
20. Confirmation mock/deterministic remains default
21. Confirmation no real model call occurs by default
22. Confirmation no remediation execution was introduced
23. Confirmation no ServiceNow/authentication/autonomous remediation was introduced
24. TODOs or limitations
25. Recommended Git commit message

Recommended commit message:

```text
feat: add contextual agent investigation handoff
```

Do not proceed beyond this prompt.