# Prompt 18 – Agent Chat and Case Intake Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 13 added local observability stack expansion.

Prompt 14 added frontend experience segregation.

Prompt 15 added backend/BFF segregation.

Prompt 16 added demo stack orchestration and demo control panel.

Prompt 17 added observability alert rules and alert-to-AMS integration.

Your task now is to implement:

```text
Agent Chat and Case Intake Foundation
```

---

## Business Goal

The platform should now introduce the first visible agentic support experience:

```text
User or service engineer chats about an issue
        ->
Case intake is created
        ->
Orchestrator gathers relevant context
        ->
Agent produces deterministic Stage 1 guidance
        ->
Ticket/report/alert context can be linked
        ->
Future RAG and real LLM execution can plug in later
```

This prompt should create the foundation for the eventual agentic system.

It should not yet call a real LLM.

It should not yet use GPT-5.4-mini or any external model.

It should not yet implement vector RAG.

It should not yet execute remediation actions.

---

## Agentic Roadmap Context

The intended staged model is:

## Stage 1 – Read-only guidance

```text
Agent gathers relevant context.
Agent summarizes likely issue.
Agent provides instructions.
Human performs all actions.
No system-changing action is executed by the agent.
```

## Stage 2 – Approval-gated execution

```text
Agent proposes each resolution action.
User or service engineer approves each step.
Agent executes only approved safe actions.
Every action is audited.
```

## Stage 3 – Autonomous remediation

```text
Agent runs diagnosis and remediation automatically for approved issue classes.
Strong policy controls, rollback plans, audit logs, and kill switch required.
Initially only in simulation/demo sandbox.
```

Prompt 18 implements only:

```text
Stage 1 read-only deterministic guidance foundation
```

It should prepare the system for Stage 2 and Stage 3, but not enable them.

---

## Future Real Model and RAG Direction

Document this direction but do not implement it yet.

Future prompts should add:

```text
real model provider integration
model selection through governed AI config
RAG over runbooks, SOPs, KB articles, known errors, historical tickets
tool-based retrieval from live system state
approval-gated action execution
agent policy controls
```

The future agent should use a hybrid pattern:

```text
RAG for static knowledge
+
live tools for current system state
+
governed action tools for approved remediation
+
case-scoped conversation memory
```

Prompt 18 should create a clean place for this future orchestration to plug in.

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

Prompt 17 added:

```text
observability alert rule catalog
manual alert evaluation
alert events
alert evidence
alert-to-AMS ticket creation
```

Existing governed AI config and copilot functionality use deterministic mock AI only.

Do not break any existing capability.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve all frontend and backend/BFF URLs.

You must not introduce external LLM calls.

You must not call OpenAI, Azure OpenAI, Anthropic, local model servers, or any external AI provider.

You must not implement real RAG or vector databases in this prompt.

You must not introduce autonomous remediation.

You must not execute shell commands from the agent.

You must not execute database-changing remediation actions from the agent.

You must not introduce ServiceNow integration.

You must not introduce authentication or authorization.

You must not create an uncontrolled scheduler or background worker.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

The agent response logic must be deterministic and testable.

The chat experience should clearly state:

```text
Current phase: deterministic Stage 1 guidance only.
No external LLM call is made.
No remediation action is executed.
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

Implement a chat and case-intake foundation for two audiences:

## 1. User-facing issue assistant

Purpose:

```text
Business user asks about an issue.
Assistant collects issue details.
Assistant creates or links a user report and optional AMS ticket.
Assistant gives read-only guidance and next steps.
```

Example user messages:

```text
My order is stuck.
I cannot allocate inventory.
Shipment is delayed.
I see an error while processing fulfillment.
The system is slow.
```

## 2. Service engineer agent chat

Purpose:

```text
Support engineer chats with the agent about an issue, ticket, alert, batch run, diagnostic case, or user report.
Agent gathers relevant evidence and gives Stage 1 resolution guidance.
```

Example engineer messages:

```text
Investigate this AMS ticket.
Why did this batch fail?
Summarize evidence for this observability alert.
What should I check next?
Prepare a work note.
What is the likely root cause?
```

---

# Data Model

Add a migration if needed.

Suggested migration:

```text
0013_agent_chat_case_intake
```

Create tables similar to the following.

---

## agent_cases

Represents an issue/case known to the agentic system.

Fields:

```text
id
case_id
case_type
title
description
status
priority
source
stage_mode
created_by_role
linked_ams_ticket_id
linked_user_report_id
linked_alert_event_id
linked_batch_run_id
linked_diagnostic_case_id
linked_order_id
linked_shipment_id
linked_inventory_item_id
created_at
updated_at
closed_at
```

Suggested case types:

```text
USER_ISSUE
SERVICE_ENGINEER_INVESTIGATION
OBSERVABILITY_ALERT
BATCH_FAILURE
MONITORING_TRIAGE
AMS_TICKET
DIAGNOSTIC_CASE
```

Statuses:

```text
OPEN
IN_PROGRESS
WAITING_FOR_USER
GUIDANCE_PROVIDED
TICKET_CREATED
CLOSED
```

Stage modes:

```text
STAGE_1_READ_ONLY
STAGE_2_APPROVAL_GATED_DISABLED
STAGE_3_AUTONOMOUS_DISABLED
```

For Prompt 18, every case must use:

```text
STAGE_1_READ_ONLY
```

---

## agent_chat_sessions

Represents a chat thread.

Fields:

```text
id
session_id
case_id
audience
title
status
started_by_role
experience
created_at
updated_at
closed_at
```

Audiences:

```text
USER
SERVICE_ENGINEER
```

Statuses:

```text
ACTIVE
CLOSED
```

Experiences:

```text
business
operations
agentic
full
```

---

## agent_chat_messages

Represents chat messages.

Fields:

```text
id
message_id
session_id
sender_type
sender_role
message_text
message_format
generation_mode
safety_status
created_at
metadata_json
```

Sender types:

```text
USER
SERVICE_ENGINEER
AGENT
SYSTEM
```

Generation modes:

```text
HUMAN_ENTERED
DETERMINISTIC_AGENT
SYSTEM_EVENT
```

Safety statuses:

```text
NOT_APPLICABLE
SAFE
BLOCKED
```

---

## agent_orchestration_runs

Represents one agent reasoning/orchestration cycle.

Fields:

```text
id
run_id
case_id
session_id
trigger_message_id
status
stage_mode
orchestrator_mode
started_at
completed_at
summary
error_message
tools_planned
tools_used
actions_proposed
actions_executed
```

Statuses:

```text
STARTED
COMPLETED
FAILED
BLOCKED
```

For Prompt 18:

```text
orchestrator_mode = DETERMINISTIC_STAGE_1
actions_executed = 0
```

---

## agent_evidence_items

Represents context gathered by the orchestrator.

Fields:

```text
id
evidence_id
case_id
run_id
evidence_type
source_type
source_id
title
summary
payload_json
source_url
relevance_score
created_at
```

Evidence types:

```text
AMS_TICKET
USER_REPORT
OBSERVABILITY_ALERT
ALERT_EVIDENCE
BATCH_RUN
BATCH_EVENT
MONITORING_ALERT
DIAGNOSTIC_CASE
RUNTIME_TRACE
RUNTIME_LOG
RUNTIME_METRIC
WAREHOUSE_ORDER
SHIPMENT
INVENTORY
COPILOT_SESSION
GENERAL_GUIDANCE
```

---

## agent_action_proposals

Represents future approval-gated action proposals.

Create the table now, but do not execute actions in Prompt 18.

Fields:

```text
id
proposal_id
case_id
run_id
title
description
action_type
risk_level
status
requires_approval
approval_status
execution_status
created_at
updated_at
```

Statuses:

```text
PROPOSED
APPROVED
REJECTED
EXPIRED
```

Execution statuses:

```text
NOT_EXECUTED
DISABLED_IN_STAGE_1
EXECUTION_DEFERRED
```

For Prompt 18, all proposed actions, if any, must have:

```text
requires_approval = true
execution_status = DISABLED_IN_STAGE_1
```

---

# Deterministic Orchestrator

Create service:

```text
backend/app/services/agent_orchestrator_service.py
```

The orchestrator should be deterministic.

It should:

```text
accept a chat message
create or update an agent case
identify likely issue type using simple rules
retrieve relevant context from existing internal tables
create evidence items
create an orchestration run
generate a Stage 1 response
optionally create non-executable action proposals
append agent response to the chat session
```

Do not call any LLM provider.

Do not use embeddings.

Do not use vector search.

Do not execute remediation.

---

## Suggested deterministic issue classification

Use keyword and linked context rules.

Examples:

```text
order stuck
allocation
inventory
shipment
batch failed
alert
slow
latency
error
ticket
diagnostic
```

Map to likely case types:

```text
order stuck -> USER_ISSUE
allocation/inventory -> USER_ISSUE
shipment delayed -> USER_ISSUE
batch failed -> BATCH_FAILURE
observability alert -> OBSERVABILITY_ALERT
AMS ticket -> AMS_TICKET
diagnostic -> DIAGNOSTIC_CASE
slow/error -> SERVICE_ENGINEER_INVESTIGATION
```

Keep simple and transparent.

---

## Evidence Retrieval

The orchestrator should retrieve relevant evidence from existing data sources when available.

Possible sources:

```text
AMS tickets
AMS user reports
observability alert events and evidence
batch runs and events
monitoring alerts and triage
observability diagnostics
runtime observability traces/logs/metrics
warehouse orders
shipments
inventory balances
copilot sessions
```

Do not over-engineer.

Implement a small useful subset first, but structure the code so future tools can be added.

At minimum, retrieve evidence from:

```text
AMS ticket if linked
user report if linked
observability alert if linked
batch run if linked
recent open observability alerts
recent failed batch runs
recent open AMS tickets
```

---

## Stage 1 Response Format

Agent response should include sections:

```text
Understanding
Relevant Evidence
Likely Cause
Recommended Next Steps
What I Cannot Do Yet
```

Example:

```text
Understanding:
You are reporting an order fulfillment issue.

Relevant Evidence:
- Found 1 recent failed batch run related to inventory reconciliation.
- Found 2 open AMS tickets in the operations queue.

Likely Cause:
The issue may be related to inventory allocation or a recent batch failure.

Recommended Next Steps:
1. Verify the order status.
2. Check available inventory.
3. Review failed batch run details.
4. Create or update an AMS ticket if the issue is blocking fulfillment.

What I Cannot Do Yet:
This agent is currently Stage 1 read-only. It cannot execute remediation actions.
```

Do not claim certainty unless evidence supports it.

---

# Backend APIs

Add route prefix:

```text
/api/v1/agent-chat
```

Expose on:

```text
Full backend 8050
Business BFF 8061 for user-facing chat only
Operations BFF 8062 for service-engineer chat
Agentic BFF 8065 for all agent-chat APIs
```

Do not expose on Simulation BFF unless needed.

Do not expose on Observability BFF unless needed.

---

## Required endpoints

```text
GET  /api/v1/agent-chat/summary

POST /api/v1/agent-chat/cases
GET  /api/v1/agent-chat/cases
GET  /api/v1/agent-chat/cases/{case_id}
POST /api/v1/agent-chat/cases/{case_id}/close

POST /api/v1/agent-chat/sessions
GET  /api/v1/agent-chat/sessions
GET  /api/v1/agent-chat/sessions/{session_id}
POST /api/v1/agent-chat/sessions/{session_id}/messages
POST /api/v1/agent-chat/sessions/{session_id}/close

GET  /api/v1/agent-chat/sessions/{session_id}/messages
GET  /api/v1/agent-chat/cases/{case_id}/evidence
GET  /api/v1/agent-chat/cases/{case_id}/orchestration-runs
GET  /api/v1/agent-chat/cases/{case_id}/action-proposals
```

---

## Convenience endpoints

Add if simple:

```text
POST /api/v1/agent-chat/intake/user-issue
POST /api/v1/agent-chat/intake/engineer-investigation
POST /api/v1/agent-chat/intake/from-ams-ticket/{ticket_id}
POST /api/v1/agent-chat/intake/from-observability-alert/{event_id}
POST /api/v1/agent-chat/intake/from-batch-run/{run_id}
```

These should create a case and session, add an initial message, run deterministic orchestration, and return the session detail.

---

# BFF Route Exposure

## Business BFF

Expose:

```text
/api/v1/agent-chat/summary
/api/v1/agent-chat/intake/user-issue
/api/v1/agent-chat/sessions/*
```

Business BFF should be user-facing.

It should not expose service-engineer investigation convenience endpoints.

If route-level filtering is difficult, expose full agent-chat route for now but document a TODO.

## Operations BFF

Expose:

```text
/api/v1/agent-chat/*
```

This supports service engineer chat.

## Agentic BFF

Expose:

```text
/api/v1/agent-chat/*
```

This is the main agentic support console.

## Full backend

Expose:

```text
/api/v1/agent-chat/*
```

## Business BFF exclusion

Business BFF should not expose advanced case management if simple to restrict.

Do not block Prompt 18 if route-level filtering is too complex; document TODO.

---

# Frontend UI

Add chat UI in the Agentic experience and selected other experiences.

Suggested files:

```text
frontend/src/services/agentChatApi.ts
frontend/src/pages/AgentChatPages.tsx
```

## Routes

```text
/agent-chat
/agent-chat/user
/agent-chat/engineer
/agent-chat/cases
/agent-chat/cases/:caseId
/agent-chat/sessions
/agent-chat/sessions/:sessionId
```

---

## Agentic UI

Visible in:

```text
http://localhost:4015
```

Show:

```text
Agent Chat Home
User Issue Intake
Service Engineer Chat
Cases
Sessions
Evidence
Orchestration Runs
Action Proposals
```

Add clear status banner:

```text
Stage 1 read-only deterministic agent.
No external LLM call.
No autonomous remediation.
```

---

## Business UI

Visible in:

```text
http://localhost:4011
```

Add a limited page:

```text
/agent-chat/user
```

Label:

```text
Get Help With an Issue
```

This should let a business user describe an issue and get guidance.

It should not show orchestration internals unless useful.

---

## Operations UI

Visible in:

```text
http://localhost:4012
```

Add:

```text
/agent-chat/engineer
/agent-chat/cases
/agent-chat/sessions
```

This supports support engineer investigation.

---

## Full UI

Visible in:

```text
http://localhost:4001
```

Show all agent chat pages.

---

## Chat UI behavior

Implement simple chat behavior:

```text
message list
text input
send button
loading state
agent response appended after send
case/session metadata panel
evidence panel
stage mode banner
```

Do not implement streaming.

Do not implement markdown-heavy rendering unless already available.

Do not add WebSocket.

Use normal REST calls.

---

# Link Agent Chat From Existing Contexts

Add links/buttons where simple:

## AMS ticket detail

```text
Investigate with Agent
```

This should call:

```text
POST /api/v1/agent-chat/intake/from-ams-ticket/{ticket_id}
```

or navigate to agent chat with context.

## Observability alert event detail

```text
Investigate with Agent
```

This should call:

```text
POST /api/v1/agent-chat/intake/from-observability-alert/{event_id}
```

## Batch run detail

```text
Investigate with Agent
```

This should call:

```text
POST /api/v1/agent-chat/intake/from-batch-run/{run_id}
```

If full integration is too much for this prompt, add route/page support and document TODO for contextual buttons.

---

# Demo Control Integration

Update demo control components/readiness to include:

```text
Agent Chat
Agentic Case Intake
Stage 1 Orchestrator
```

Add readiness endpoint check:

```text
http://localhost:8050/api/v1/agent-chat/summary
```

---

# Tests

Add backend tests for:

```text
create user issue intake
create engineer investigation intake
create chat session
send message
agent deterministic response appended
case created with STAGE_1_READ_ONLY
orchestration run created
evidence items created
action proposals are not executed
intake from AMS ticket
intake from observability alert
intake from batch run if implemented
BFF exposure
Business BFF user chat availability
Agentic BFF full agent-chat availability
Simulation BFF does not expose agent-chat
demo control includes agent chat
```

Tests must not require external LLMs.

Tests must not require Prometheus/Grafana/Tempo/Loki to be live.

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

## Summary

```bash
curl -sS http://localhost:8050/api/v1/agent-chat/summary | jq .
curl -sS http://localhost:8065/api/v1/agent-chat/summary | jq .
```

## User issue intake

```bash
curl -sS -X POST http://localhost:8050/api/v1/agent-chat/intake/user-issue \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Order is stuck",
    "description": "My order is stuck during fulfillment and I need help.",
    "initial_message": "My order is stuck. What should I check?"
  }' | jq .
```

## Engineer investigation intake

```bash
curl -sS -X POST http://localhost:8065/api/v1/agent-chat/intake/engineer-investigation \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Investigate failed batch and alert",
    "description": "Service engineer wants the agent to review the latest failed batch and observability alerts.",
    "initial_message": "Investigate recent failed batch runs and tell me likely next steps."
  }' | jq .
```

## Send message to session

Use the returned `session_id`:

```bash
curl -sS -X POST http://localhost:8065/api/v1/agent-chat/sessions/<SESSION_ID>/messages \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "What evidence did you find and what should I do next?"
  }' | jq .
```

## Evidence and orchestration

```bash
curl -sS http://localhost:8065/api/v1/agent-chat/cases/<CASE_ID>/evidence | jq .
curl -sS http://localhost:8065/api/v1/agent-chat/cases/<CASE_ID>/orchestration-runs | jq .
curl -sS http://localhost:8065/api/v1/agent-chat/cases/<CASE_ID>/action-proposals | jq .
```

## BFF exposure

```bash
curl -sS http://localhost:8061/api/v1/agent-chat/summary | jq .
curl -sS http://localhost:8062/api/v1/agent-chat/summary | jq .
curl -sS http://localhost:8065/api/v1/agent-chat/summary | jq .
curl -i -sS http://localhost:8063/api/v1/agent-chat/summary | head
```

Expected:

```text
Business BFF: user-facing summary works
Operations BFF: works
Agentic BFF: works
Simulation BFF: 404 Not Found
```

---

# Manual UI Validation

Open:

```text
http://localhost:4015/agent-chat
http://localhost:4015/agent-chat/user
http://localhost:4015/agent-chat/engineer
http://localhost:4015/agent-chat/cases
http://localhost:4015/agent-chat/sessions
```

Validate:

```text
agentic banner says Stage 1 read-only
no external LLM statement visible
no autonomous remediation statement visible
user issue intake works
engineer investigation intake works
chat message send works
agent response appears
evidence appears
orchestration run appears
action proposals, if any, show disabled/not executed
```

Open Business UI:

```text
http://localhost:4011/agent-chat/user
```

Validate:

```text
business user can submit issue and receive guidance
advanced orchestration internals are hidden or minimized
```

Open Operations UI:

```text
http://localhost:4012/agent-chat/engineer
```

Validate:

```text
service engineer can start investigation chat
case/session list pages are available
```

---

# Documentation Updates

Update `README.md` with:

```text
Agent Chat routes
Stage 1 behavior
manual validation commands
frontend locations
BFF exposure
no external LLM
no autonomous remediation
future RAG and real model direction
```

Update `ARCHITECTURE.md` with:

```text
Agent chat architecture
case intake model
deterministic Stage 1 orchestrator
future RAG/model/tool/action layers
three-stage remediation maturity model
```

Document clearly:

```text
Prompt 18 implements chat and case-intake foundation only.
It does not call real LLMs.
It does not implement vector RAG.
It does not execute remediation.
```

---

# Definition of Done

Prompt 18 is complete only when:

- agent case model exists
- agent chat session model exists
- chat messages are persisted
- orchestration run model exists
- evidence items are persisted
- action proposal model exists but no action is executed
- deterministic Stage 1 orchestrator exists
- user issue intake endpoint works
- engineer investigation intake endpoint works
- message send endpoint works
- agent deterministic response is appended
- evidence retrieval works for at least a useful subset
- orchestration runs are recorded
- APIs exist under `/api/v1/agent-chat`
- Business BFF exposes user-facing chat
- Operations BFF exposes service-engineer chat
- Agentic BFF exposes full agent-chat APIs
- Simulation BFF does not expose agent-chat
- frontend chat pages exist
- Agentic UI has full agent chat console
- Business UI has user issue assistant
- Operations UI has engineer chat
- demo control includes agent chat readiness
- backend tests pass
- frontend build passes
- demo stack validation passes
- no external LLM call is introduced
- no RAG/vector DB is introduced
- no ServiceNow integration is introduced
- no autonomous remediation is introduced
- no authentication is introduced
- Docker Compose unchanged unless justified
- observability infrastructure unchanged unless justified
- README updated
- ARCHITECTURE.md updated
- Prompt 18 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary
4. Agent data model summary
5. Deterministic orchestrator behavior
6. Evidence retrieval behavior
7. Stage 1 response behavior
8. Action proposal behavior
9. Backend APIs added
10. BFF exposure summary
11. Frontend routes added
12. Demo control integration summary
13. Backend test results
14. Frontend build results
15. Demo stack validation results
16. Manual API validation results
17. Manual UI validation results
18. Confirmation no real LLM call was introduced
19. Confirmation no RAG/vector DB was introduced
20. Confirmation no remediation execution was introduced
21. Confirmation no ServiceNow/authentication/autonomous remediation was introduced
22. TODOs or limitations
23. Recommended Git commit message

Recommended commit message:

```text
feat: add agent chat case intake foundation
```

Do not proceed beyond this prompt.