# Prompt 22 – Agent Investigation Workspace and Evidence Timeline

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 18 added agent chat and case intake.

Prompt 19 added deterministic knowledge and RAG foundation.

Prompt 20 added governed real model provider foundation, disabled by default.

Prompt 21 added contextual “Investigate with Agent” handoff from operational objects.

Your task now is to implement:

```text
Agent Investigation Workspace and Evidence Timeline
```

---

## Business Goal

The agent now receives contextual investigation handoffs from:

```text
AMS tickets
Observability alerts
Batch runs
User reports
Diagnostic cases
Monitoring triage cases
Operations exceptions
```

However, the current agent chat screen is still mostly a chat view.

Prompt 22 should create a service-engineer-ready investigation workspace that shows:

```text
source context
agent case status
chat
evidence timeline
retrieved knowledge
known errors
orchestration runs
action proposals
linked AMS ticket
work-note draft
customer-update draft
investigation summary
Stage 1 safety posture
```

The customer demo story should become:

```text
Engineer opens an operational issue
        ->
Clicks Investigate with Agent
        ->
Agent workspace opens
        ->
Engineer sees source context, evidence, timeline, knowledge, and guidance
        ->
Engineer can copy work notes or customer updates
        ->
No remediation is executed
```

This prompt remains Stage 1 read-only.

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

Current agent capabilities include:

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
Optional governed real-model path, disabled by default
Contextual investigation handoff
```

Do not break existing functionality.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve all frontend and backend/BFF URLs.

You must preserve deterministic/mock behavior as the default.

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

You must not break Prompt 18, 19, 20, or 21 behavior.

This prompt must remain:

```text
Stage 1 read-only investigation workspace
No remediation execution
No external LLM call by default
No ServiceNow integration
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

Implement a unified investigation workspace for an agent case.

The workspace should be available from:

```text
Agentic UI
Operations UI
Full UI
```

Primary route:

```text
/agent-investigations
/agent-investigations/:caseId
```

It may also be linked from:

```text
/agent-chat/cases/:caseId
/agent-chat/sessions/:sessionId
```

The workspace should give the service engineer one place to understand:

```text
What issue is being investigated?
Where did it come from?
What evidence has the agent gathered?
What knowledge/runbooks were retrieved?
What is the likely cause?
What should the human do next?
What action proposals exist, but remain disabled?
What can be copied into an AMS work note?
What can be sent as a customer update after human review?
```

---

# Backend Investigation Workspace Service

Create a service such as:

```text
backend/app/services/agent_investigation_service.py
```

It should build a consolidated investigation workspace view for an `agent_case`.

The service should aggregate:

```text
agent case
source object metadata
linked AMS ticket
linked user report
linked observability alert
linked batch run
linked diagnostic case
linked monitoring triage case
linked operations exception
chat sessions
chat messages
orchestration runs
evidence items
retrieval queries/results
knowledge articles/chunks
known errors
action proposals
deterministic summary
deterministic work-note draft
deterministic customer-update draft
```

Do not call real models by default.

Do not execute actions.

---

# Data Model

Add a migration only if needed.

Preferred approach:

Use existing agent tables and compute workspace views dynamically.

Add a table only if useful for persisted generated artifacts.

Optional migration:

```text
0016_agent_investigation_workspace
```

Optional table:

```text
agent_investigation_artifacts
```

Suggested fields:

```text
id
artifact_id
case_id
artifact_type
title
content
generation_mode
source_run_id
created_by
created_at
updated_at
```

Artifact types:

```text
INVESTIGATION_SUMMARY
WORK_NOTE_DRAFT
CUSTOMER_UPDATE_DRAFT
EVIDENCE_TIMELINE_SNAPSHOT
NEXT_STEPS_CHECKLIST
```

Generation modes:

```text
DETERMINISTIC
REAL_MODEL_DISABLED
REAL_MODEL_FALLBACK
```

If you can generate these dynamically without persistence, skip the migration.

Do not add action execution fields.

---

# Investigation Workspace API

Add route prefix:

```text
/api/v1/agent-investigations
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

unless there is a clear route-specific reason.

---

## Required endpoints

```text
GET  /api/v1/agent-investigations/summary
GET  /api/v1/agent-investigations/cases
GET  /api/v1/agent-investigations/cases/{case_id}
GET  /api/v1/agent-investigations/cases/{case_id}/timeline
GET  /api/v1/agent-investigations/cases/{case_id}/evidence
GET  /api/v1/agent-investigations/cases/{case_id}/knowledge
GET  /api/v1/agent-investigations/cases/{case_id}/orchestration-runs
GET  /api/v1/agent-investigations/cases/{case_id}/action-proposals
GET  /api/v1/agent-investigations/cases/{case_id}/drafts
POST /api/v1/agent-investigations/cases/{case_id}/generate-drafts
```

Optional:

```text
POST /api/v1/agent-investigations/cases/{case_id}/refresh
```

If implemented, refresh should:

```text
run deterministic evidence/knowledge refresh
append a new orchestration run
not execute remediation
not call real model by default
```

---

## Workspace detail response

`GET /cases/{case_id}` should return a consolidated object such as:

```json
{
  "case": {
    "case_id": "AGC-...",
    "title": "Investigate AMS ticket ...",
    "status": "IN_PROGRESS",
    "stage_mode": "STAGE_1_READ_ONLY",
    "source_object_type": "AMS_TICKET",
    "source_object_id": "AMS-..."
  },
  "source": {
    "type": "AMS_TICKET",
    "display": "AMS Ticket AMS-...",
    "url": "/ams/tickets/AMS-...",
    "summary": "..."
  },
  "linked_objects": {
    "ams_ticket": {},
    "observability_alert": {},
    "batch_run": {},
    "user_report": {},
    "diagnostic_case": {}
  },
  "counts": {
    "evidence_items": 6,
    "knowledge_items": 3,
    "known_errors": 1,
    "orchestration_runs": 2,
    "action_proposals": 1,
    "actions_executed": 0
  },
  "stage_safety": {
    "mode": "STAGE_1_READ_ONLY",
    "real_model_default": false,
    "remediation_execution_enabled": false,
    "message": "The agent has not executed any remediation action."
  }
}
```

---

# Evidence Timeline

Implement a deterministic timeline builder.

Timeline items should be generated from:

```text
case created
source object linked
chat session created
user/service engineer messages
agent responses
orchestration runs
evidence items
knowledge retrievals
known-error matches
action proposals
linked AMS ticket events
alert evidence
batch run events
diagnostic evidence
case closed
```

Timeline item fields:

```text
timestamp
item_type
title
description
source_type
source_id
severity
status
link_url
metadata
```

Suggested item types:

```text
CASE_CREATED
SOURCE_LINKED
CHAT_MESSAGE
AGENT_RESPONSE
ORCHESTRATION_RUN
EVIDENCE_CAPTURED
KNOWLEDGE_RETRIEVED
KNOWN_ERROR_MATCHED
ACTION_PROPOSED
AMS_TICKET_EVENT
OBSERVABILITY_ALERT_EVENT
BATCH_RUN_EVENT
DIAGNOSTIC_EVIDENCE
USER_REPORT_EVENT
```

The timeline should be sorted ascending by timestamp by default, with optional descending query parameter.

---

# Deterministic Draft Generation

Add deterministic draft generation for:

```text
work note
customer update
investigation summary
next steps checklist
```

These should be based on existing evidence and knowledge.

Do not call a real model by default.

Do not send updates anywhere.

Do not update AMS ticket automatically unless existing safe work-note functionality already exists and is explicitly called by the human.

Drafts should clearly state:

```text
Draft only. Human review required.
No action has been executed by the agent.
```

---

## Work-note draft content

Should include:

```text
source object
summary of issue
evidence reviewed
knowledge/runbooks retrieved
likely cause
recommended next steps
current stage mode
actions executed = 0
```

---

## Customer-update draft content

Should include plain-language summary:

```text
We are investigating the issue.
Current findings suggest ...
The support team is checking ...
No customer-impacting action has been performed by the agent.
```

Avoid overly technical internal details.

---

## Next-steps checklist

Should include human-executable steps only:

```text
review source ticket/alert/batch run
verify current status
check evidence items
review retrieved runbook
perform manual validation
update AMS ticket
communicate status to user
```

Do not include shell commands.

Do not include autonomous execution.

---

# Agent Chat Integration

Update agent chat case/session detail pages to link to the investigation workspace.

Add:

```text
Open Investigation Workspace
```

For session detail route:

```text
/agent-chat/sessions/:sessionId
```

Add a prominent button/link:

```text
View Investigation Workspace
```

For case detail route:

```text
/agent-chat/cases/:caseId
```

Add:

```text
Open Investigation Workspace
```

---

# Frontend Investigation Workspace

Create pages/services such as:

```text
frontend/src/services/agentInvestigationApi.ts
frontend/src/pages/AgentInvestigationPages.tsx
```

Routes:

```text
/agent-investigations
/agent-investigations/:caseId
```

Visible in:

```text
full
operations
agentic
```

Not visible in:

```text
business
simulation
observability
```

---

## Investigation list page

Show:

```text
case id
title
status
source object type
source object display
stage mode
latest orchestration run
evidence count
knowledge count
open workspace button
```

Filters, if simple:

```text
status
source object type
case type
stage mode
```

---

## Investigation detail workspace

Use a multi-section layout.

Required sections:

```text
Header / case summary
Stage 1 safety banner
Investigation source
Linked objects
Agent guidance summary
Evidence timeline
Evidence items
Relevant knowledge
Known errors
Orchestration runs
Action proposals
Drafts
Chat panel or link to chat session
```

The UI should clearly show:

```text
Actions executed: 0
Remediation execution: Disabled
Real model default: Off
Human review required
```

---

## Drafts UI

The workspace should show:

```text
Investigation summary draft
AMS work-note draft
Customer-update draft
Next-steps checklist
```

Add buttons:

```text
Generate/Refresh Drafts
Copy Draft
```

Copy button can use browser clipboard if already acceptable.

Do not add:

```text
Send to customer
Post to ServiceNow
Execute remediation
Run command
```

---

# Contextual Handoff Button Update

After Prompt 21, handoff currently navigates to:

```text
/agent-chat/sessions/{sessionId}
```

Update or extend behavior so that supported operational pages can navigate to:

```text
/agent-investigations/{caseId}
```

Preferred:

```text
Investigate with Agent
```

opens the investigation workspace.

Inside the workspace, user can continue chat.

If changing navigation broadly is risky, keep existing session navigation and add clear “Open Investigation Workspace” links.

---

# Demo Control Integration

Update demo control readiness/components to include:

```text
Agent Investigation Workspace
Evidence Timeline
Investigation Drafts
```

Readiness should check:

```text
http://localhost:8050/api/v1/agent-investigations/summary
```

Do not trigger draft generation in readiness.

---

# Tests

Add backend tests for:

```text
investigation summary endpoint
list investigation cases
get investigation workspace by case id
timeline includes case/source/message/evidence/knowledge entries
evidence endpoint returns case evidence
knowledge endpoint returns knowledge evidence
orchestration endpoint returns runs
action proposal endpoint returns proposals
draft generation creates deterministic drafts or returns dynamic drafts
drafts contain human review / Stage 1 warning
actions_executed remains 0
BFF exposure
Business BFF does not expose investigation workspace
Simulation BFF does not expose investigation workspace
Observability BFF does not expose investigation workspace
agent chat pages link to workspace if backend response supports it
demo control includes investigation workspace readiness
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

## Create investigation source using AMS handoff

```bash
TICKET_ID=$(
  curl -sS http://localhost:8050/api/v1/ams/tickets \
  | jq -r 'if type=="array" then (.[0].ticket_id // .[0].id) elif has("items") then (.items[0].ticket_id // .items[0].id) elif has("tickets") then (.tickets[0].ticket_id // .tickets[0].id) else empty end'
)

echo "$TICKET_ID"

curl -sS -X POST "http://localhost:8050/api/v1/agent-chat/intake/from-ams-ticket/${TICKET_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_message": "Investigate this AMS ticket and summarize likely next steps.",
    "reuse_existing": true,
    "use_real_model": false
  }' | jq .
```

Capture returned:

```text
CASE_ID
SESSION_ID
```

---

## Investigation workspace

```bash
curl -sS http://localhost:8050/api/v1/agent-investigations/summary | jq .
curl -sS http://localhost:8050/api/v1/agent-investigations/cases | jq .
curl -sS "http://localhost:8050/api/v1/agent-investigations/cases/${CASE_ID}" | jq .
curl -sS "http://localhost:8050/api/v1/agent-investigations/cases/${CASE_ID}/timeline" | jq .
curl -sS "http://localhost:8050/api/v1/agent-investigations/cases/${CASE_ID}/evidence" | jq .
curl -sS "http://localhost:8050/api/v1/agent-investigations/cases/${CASE_ID}/knowledge" | jq .
curl -sS "http://localhost:8050/api/v1/agent-investigations/cases/${CASE_ID}/orchestration-runs" | jq .
curl -sS "http://localhost:8050/api/v1/agent-investigations/cases/${CASE_ID}/action-proposals" | jq .
curl -sS "http://localhost:8050/api/v1/agent-investigations/cases/${CASE_ID}/drafts" | jq .
```

Generate drafts:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-investigations/cases/${CASE_ID}/generate-drafts" \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
```

Expected:

```text
work-note draft exists
customer-update draft exists
investigation summary exists
next-steps checklist exists
drafts say human review required
actions_executed remains 0
```

---

## BFF exposure validation

```bash
curl -sS http://localhost:8062/api/v1/agent-investigations/summary | jq .
curl -sS http://localhost:8065/api/v1/agent-investigations/summary | jq .

curl -i -sS http://localhost:8061/api/v1/agent-investigations/summary | head
curl -i -sS http://localhost:8063/api/v1/agent-investigations/summary | head
curl -i -sS http://localhost:8064/api/v1/agent-investigations/summary | head
```

Expected:

```text
Operations BFF: works
Agentic BFF: works
Business BFF: 404
Simulation BFF: 404
Observability BFF: 404
```

---

# Manual UI Validation

Open Agentic UI:

```text
http://localhost:4015/agent-investigations
```

Validate:

```text
investigation list loads
case source is visible
open workspace works
```

Open case detail:

```text
http://localhost:4015/agent-investigations/<CASE_ID>
```

Validate:

```text
Stage 1 safety banner visible
Investigation Source visible
Linked objects visible
Evidence timeline visible
Evidence items visible
Relevant knowledge visible
Known errors visible if matched
Orchestration runs visible
Action proposals visible and disabled/not executed
Drafts visible
Generate/Refresh Drafts works
Copy Draft works if implemented
Chat link or chat panel visible
```

Open Operations UI:

```text
http://localhost:4012/agent-investigations
```

Validate:

```text
same workspace works for service engineer
```

Open an AMS ticket detail page:

```text
http://localhost:4012/ams/tickets
```

Validate:

```text
Investigate with Agent opens or links to investigation workspace
```

Confirm Business UI does not expose the workspace:

```text
http://localhost:4011/agent-investigations
```

Expected:

```text
experience boundary or not available
```

---

# Documentation Updates

Update `README.md` with:

```text
Agent Investigation Workspace overview
workspace URLs
manual validation commands
draft generation behavior
Stage 1 safety posture
no remediation execution
```

Update `ARCHITECTURE.md` with:

```text
investigation workspace architecture
evidence timeline architecture
deterministic draft generation
relationship between handoff, case, session, evidence, knowledge, and workspace
future Stage 2 approval workflow placement
future ServiceNow work-note integration point
```

Document clearly:

```text
Prompt 22 creates read-only investigation workspace only.
It does not execute remediation.
It does not post work notes externally.
It does not send customer communications.
It does not enable real model calls by default.
```

---

# Definition of Done

Prompt 22 is complete only when:

- investigation workspace service exists
- investigation summary endpoint exists
- investigation case list endpoint exists
- investigation case detail endpoint exists
- timeline endpoint exists
- evidence endpoint exists
- knowledge endpoint exists
- orchestration runs endpoint exists
- action proposals endpoint exists
- draft generation endpoint exists
- deterministic work-note draft exists
- deterministic customer-update draft exists
- deterministic investigation summary exists
- deterministic next-steps checklist exists
- drafts clearly say human review required
- actions_executed remains 0
- no remediation execution is introduced
- no external model call occurs by default
- Operations BFF exposes investigation workspace
- Agentic BFF exposes investigation workspace
- Business BFF does not expose investigation workspace
- frontend investigation list page exists
- frontend investigation detail workspace exists
- agent chat pages link to workspace
- contextual handoff can open workspace or link to it
- demo control includes workspace readiness
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
- Prompt 22 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. Investigation workspace service behavior
5. Evidence timeline behavior
6. Draft generation behavior
7. Backend APIs added
8. BFF exposure summary
9. Frontend routes/pages added
10. Agent chat integration summary
11. Contextual handoff navigation behavior
12. Demo control integration summary
13. Backend test results
14. Frontend build results
15. Demo stack validation results
16. Manual API validation results
17. Manual UI validation results
18. Confirmation deterministic/mock remains default
19. Confirmation no real model call occurs by default
20. Confirmation no remediation execution was introduced
21. Confirmation no ServiceNow/authentication/autonomous remediation was introduced
22. TODOs or limitations
23. Recommended Git commit message

Recommended commit message:

```text
feat: add agent investigation workspace
```

Do not proceed beyond this prompt.