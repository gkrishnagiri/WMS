# Prompt 09 – AI-Native Support Engineer Copilot Foundation

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

Your task now is to implement the next support scenario:

```text
AI-Native Support Engineer Copilot Foundation
```

This prompt introduces the first AI-native support layer, but it must remain deterministic and governed.

Do not integrate external LLMs yet.

Do not add LangGraph, LiteLLM, OpenAI SDKs, local models, vector databases, RAG frameworks, autonomous agents, or ServiceNow integration yet.

This prompt creates the **copilot foundation** that later prompts can connect to LLMs and agentic workflows.

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

The copilot in this prompt is deterministic and rules-based.

---

# Objective

Implement a governed support engineer copilot foundation.

The copilot should help a support engineer by aggregating context across existing EOS support modules:

```text
AMS ticket
Operational exception
User report
Monitoring alert
Monitoring triage case
Observability diagnostic case
Batch run
Warehouse business entity
```

The copilot should provide deterministic assistance such as:

```text
support context summary
impact summary
evidence timeline
probable support category
recommended next actions
suggested investigation checklist
draft ticket work note
draft customer update
safe action eligibility
```

This is not an autonomous agent yet.

This is not an LLM chatbot yet.

The goal is to create the governed substrate for later AI/agentic prompts.

---

# Architectural Intent

Prior prompts created separate support artifacts.

Prompt 09 should connect them into one support workbench.

The intended flow:

```text
Support engineer opens Copilot Workbench
        ↓
Selects or creates a copilot session
        ↓
Attaches a ticket, exception, alert, triage case, diagnostic case, batch run, or user report
        ↓
Copilot builds a deterministic context snapshot
        ↓
Copilot generates recommendations and safe next actions
        ↓
Engineer reviews recommendations
        ↓
Engineer may create a ticket work note draft, customer update draft, or investigation checklist
        ↓
Engineer manually acts through existing modules
```

The copilot must not perform destructive actions automatically.

It can recommend.

It can draft.

It can link existing artifacts.

It can call safe existing read APIs/service logic.

It can create a copilot record of recommended actions.

It should not silently resolve tickets, close alerts, or remediate workflows.

---

# Scope

Implement:

1. Copilot session model
2. Copilot context snapshot model
3. Copilot recommendation model
4. Copilot action plan model
5. Copilot message/note model
6. Deterministic context builder
7. Deterministic recommendation engine
8. Ticket/exception/alert/batch/diagnostic context aggregation
9. Draft work note generation
10. Draft customer update generation
11. Investigation checklist generation
12. Safe action registry
13. Copilot frontend workbench
14. Backend tests
15. Documentation updates

Do not implement:

- external LLM calls
- real natural language conversation with a model
- RAG
- embeddings
- vector search
- autonomous remediation
- automatic ticket closure
- automatic production changes
- ServiceNow integration
- real notification sending

---

# Database Additions

Create a new Alembic migration.

Add the following tables:

```text
copilot_sessions
copilot_context_snapshots
copilot_recommendations
copilot_action_plans
copilot_messages
copilot_safe_actions
copilot_action_events
```

Use UUID primary keys consistent with existing project style.

Use timestamp conventions consistent with existing project.

---

## Table: `copilot_sessions`

Purpose:

Represent a support engineer copilot session.

Fields:

```text
id
session_number
title
description
status
primary_entity_type
primary_entity_id
primary_ticket_id
severity
confidence_level
created_by
created_at
updated_at
closed_at
```

Rules:

- `session_number` must be unique
- `primary_ticket_id` nullable, references `ams_tickets.id`
- `primary_entity_type` examples:
  - AMS_TICKET
  - OPERATIONAL_EXCEPTION
  - USER_REPORT
  - MONITORING_ALERT
  - MONITORING_TRIAGE_CASE
  - OBSERVABILITY_DIAGNOSTIC
  - BATCH_RUN
  - MANUAL
- `primary_entity_id` nullable
- one session may exist without a ticket

Suggested statuses:

```text
OPEN
ANALYZING
RECOMMENDATIONS_READY
ACTION_PLAN_READY
CLOSED
```

Suggested confidence levels:

```text
LOW
MEDIUM
HIGH
UNKNOWN
```

Session number format:

```text
COPILOT-YYYYMMDD-0001
```

---

## Table: `copilot_context_snapshots`

Purpose:

Persist the context assembled by the copilot at a point in time.

Fields:

```text
id
session_id
snapshot_number
source_entity_type
source_entity_id
summary
impact_summary
technical_summary
business_summary
timeline_summary
evidence_summary
related_entities
raw_context
created_by
created_at
```

Rules:

- `session_id` references `copilot_sessions.id`
- `snapshot_number` must be unique
- `related_entities` should be JSON/JSONB if supported
- `raw_context` should be JSON/JSONB if supported
- raw context must not include secrets
- context should include only data already available inside EOS

Snapshot number format:

```text
CTX-YYYYMMDD-0001
```

---

## Table: `copilot_recommendations`

Purpose:

Represent deterministic copilot recommendations.

Fields:

```text
id
session_id
snapshot_id
recommendation_type
title
details
priority
confidence_level
rationale
source_evidence
status
created_at
updated_at
accepted_at
dismissed_at
```

Rules:

- `session_id` references `copilot_sessions.id`
- `snapshot_id` nullable, references `copilot_context_snapshots.id`
- `source_evidence` should be JSON/JSONB if supported

Suggested recommendation types:

```text
INVESTIGATE
CHECK_OBSERVABILITY
CHECK_BATCH_RUN
CHECK_MONITORING_ALERTS
CHECK_USER_IMPACT
CREATE_TICKET
UPDATE_TICKET
ACKNOWLEDGE_ALERT
CREATE_DIAGNOSTIC
ESCALATE
COMMUNICATE_STATUS
```

Suggested priorities:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Suggested statuses:

```text
PROPOSED
ACCEPTED
DISMISSED
COMPLETED
```

---

## Table: `copilot_action_plans`

Purpose:

Represent a deterministic support action plan.

Fields:

```text
id
session_id
snapshot_id
plan_number
title
summary
status
steps
risk_level
requires_human_approval
created_at
updated_at
approved_at
completed_at
```

Rules:

- `session_id` references `copilot_sessions.id`
- `snapshot_id` nullable, references `copilot_context_snapshots.id`
- `plan_number` must be unique
- `steps` should be JSON/JSONB if supported
- `requires_human_approval` must default to true

Suggested statuses:

```text
DRAFT
READY_FOR_REVIEW
APPROVED
COMPLETED
CANCELLED
```

Suggested risk levels:

```text
LOW
MEDIUM
HIGH
```

Action plan number format:

```text
PLAN-YYYYMMDD-0001
```

---

## Table: `copilot_messages`

Purpose:

Store deterministic copilot-generated messages, notes, drafts, and user-visible text artifacts.

Fields:

```text
id
session_id
message_type
title
content
status
target_entity_type
target_entity_id
created_by
created_at
updated_at
```

Rules:

- `session_id` references `copilot_sessions.id`
- content is deterministic text generated from context
- no external LLM should be used

Suggested message types:

```text
CONTEXT_SUMMARY
WORK_NOTE_DRAFT
CUSTOMER_UPDATE_DRAFT
INVESTIGATION_CHECKLIST
HANDOFF_NOTE
RESOLUTION_DRAFT
```

Suggested statuses:

```text
DRAFT
REVIEWED
APPLIED
DISCARDED
```

---

## Table: `copilot_safe_actions`

Purpose:

Catalog actions the copilot is allowed to recommend.

This is not an execution engine yet.

Fields:

```text
id
action_code
name
description
target_module
action_type
risk_level
requires_human_approval
enabled
created_at
updated_at
```

Rules:

- `action_code` must be unique
- `requires_human_approval` defaults to true

Suggested actions:

```text
ACKNOWLEDGE_TICKET
START_TICKET_WORK
CREATE_TICKET_WORK_NOTE_DRAFT
ACKNOWLEDGE_ALERT
CREATE_DIAGNOSTIC_FROM_ALERT
CREATE_DIAGNOSTIC_FROM_BATCH_RUN
CREATE_TICKET_FROM_EXCEPTION
CREATE_TICKET_FROM_BATCH_RUN
CREATE_TICKET_FROM_DIAGNOSTIC
GENERATE_CUSTOMER_UPDATE
GENERATE_INVESTIGATION_CHECKLIST
```

---

## Table: `copilot_action_events`

Purpose:

Audit copilot action recommendations, approvals, and manual execution references.

Fields:

```text
id
session_id
action_code
event_type
target_entity_type
target_entity_id
from_status
to_status
message
event_payload
created_by
created_at
```

Rules:

- `session_id` references `copilot_sessions.id`
- `event_payload` should be JSON/JSONB if supported
- this table should not imply autonomous execution unless explicitly recorded in later prompts

Suggested event types:

```text
ACTION_RECOMMENDED
ACTION_ACCEPTED
ACTION_DISMISSED
ACTION_PLAN_CREATED
DRAFT_CREATED
MANUAL_ACTION_RECORDED
```

---

# Seed Data

Create an idempotent seed module:

```text
backend/app/db/seed_copilot.py
```

Runnable as:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_copilot
```

It should seed the safe action catalog.

Running it multiple times must not create duplicates.

Update README validation commands to include this seed command.

Do not modify existing seed behavior for warehouse, synthetic users, monitoring, batch, operations, AMS, or observability.

---

# Copilot Context Builder

Create service modules such as:

```text
backend/app/services/copilot_service.py
backend/app/services/copilot_context_service.py
backend/app/services/copilot_recommendation_service.py
```

You may organize differently if consistent with existing project style.

The context builder should accept:

```text
entity_type
entity_id
```

Supported entity types:

```text
AMS_TICKET
OPERATIONAL_EXCEPTION
USER_REPORT
MONITORING_ALERT
MONITORING_TRIAGE_CASE
OBSERVABILITY_DIAGNOSTIC
BATCH_RUN
MANUAL
```

It should aggregate related context where available.

---

## Context for AMS Ticket

For an AMS ticket, collect:

```text
ticket header
ticket status
ticket priority
ticket source
ticket source module
ticket events
linked operational exception if any
linked user report if any
linked monitoring alert if any
linked monitoring triage case if any
linked observability diagnostic if any
linked batch run if any
related logs/metrics/traces if any
```

If direct reverse links are not easy for some entities, include TODO notes and implement the relationships that are currently practical.

---

## Context for Operational Exception

Collect:

```text
exception header
exception severity/status
source entity
linked ticket
related monitoring alerts if linked
related diagnostic cases if linked
```

---

## Context for User Report

Collect:

```text
report details
reporter
business impact
linked ticket
linked synthetic journey run if any
```

---

## Context for Monitoring Alert

Collect:

```text
alert details
component
metric
observed value
threshold
events
linked ticket
linked diagnostic cases if any
```

---

## Context for Monitoring Triage Case

Collect:

```text
triage case details
linked alerts
linked ticket
suspected impact
suspected root cause
confidence level
```

---

## Context for Observability Diagnostic

Collect:

```text
diagnostic case details
probable cause
confidence
recommended next steps
primary trace
evidence records
linked ticket
linked alert
linked triage case
```

---

## Context for Batch Run

Collect:

```text
batch run details
job details
step runs
events
failure type
failure message
linked exception
linked ticket
linked diagnostic case
```

---

# Deterministic Recommendation Engine

Create deterministic recommendations based on context.

Do not use AI/LLM.

Examples:

## Ticket has no diagnostic but has monitoring alert

Recommend:

```text
Create diagnostic case from monitoring alert
```

## Ticket has batch source and failed batch run has no diagnostic

Recommend:

```text
Create diagnostic case from batch run
```

## Alert is open and unacknowledged

Recommend:

```text
Acknowledge alert and group into triage case
```

## Diagnostic case has high confidence and no ticket

Recommend:

```text
Create AMS ticket from diagnostic case
```

## User report has business impact and no ticket

Recommend:

```text
Create AMS ticket from user report
```

## Ticket is open with no work note draft

Recommend:

```text
Generate ticket work note draft
```

## Diagnostic case has probable cause and evidence

Recommend:

```text
Generate customer update draft
```

## Batch run failed

Recommend:

```text
Review failed step and create exception/ticket if not already linked
```

Each recommendation must include:

```text
title
details
priority
confidence_level
rationale
source_evidence
```

---

# Draft Generation

Generate deterministic text artifacts from context.

No LLM.

## Work Note Draft

Should include:

```text
Current status
Impacted module
Observed symptoms
Evidence reviewed
Current hypothesis
Next action
```

Example:

```text
Support investigation update:
The issue is linked to Warehouse & Fulfillment Operations. Evidence reviewed includes monitoring alerts, diagnostic case details, and batch run events. Current hypothesis: database latency affected inventory allocation. Next action: validate database response time and review failed workflow step evidence.
```

## Customer Update Draft

Should include:

```text
acknowledgement
business impact
current investigation status
next update expectation
```

Avoid internal technical jargon where possible.

## Investigation Checklist

Generate checklist items based on source context.

Examples:

For monitoring alert:

```text
- Confirm alert occurrence count and last seen time.
- Check linked diagnostic case.
- Review trace spans for slow or failed operation.
- Review related AMS ticket status.
```

For batch run:

```text
- Review failed batch step.
- Confirm records processed, succeeded, and failed.
- Check whether exception was created.
- Check whether diagnostic case exists.
- Confirm whether rerun is safe.
```

---

# Safe Action Rules

The copilot may recommend actions but must not automatically execute destructive actions.

Allowed in Prompt 09:

```text
create copilot session
create context snapshot
create recommendations
create action plan
create message/draft/checklist
mark recommendation accepted/dismissed
record manual action event
```

Optional if simple and safe:

```text
create diagnostic case from existing alert/batch/ticket by calling existing services
create AMS ticket from diagnostic case only if explicitly requested through API
```

Not allowed in Prompt 09:

```text
automatically resolve ticket
automatically close ticket
automatically suppress alert
automatically resolve alert
automatically resolve diagnostic case
automatically rerun batch job
automatically change inventory/order/shipment data
```

---

# Backend APIs

Create copilot APIs.

Suggested files:

```text
backend/app/models/copilot.py
backend/app/schemas/copilot.py
backend/app/services/copilot_service.py
backend/app/services/copilot_context_service.py
backend/app/services/copilot_recommendation_service.py
backend/app/api/routes/copilot.py
backend/app/db/seed_copilot.py
```

Use prefix:

```text
/api/v1/copilot
```

Add:

```text
GET  /api/v1/copilot/summary
GET  /api/v1/copilot/safe-actions
GET  /api/v1/copilot/sessions
POST /api/v1/copilot/sessions
GET  /api/v1/copilot/sessions/{session_id}
POST /api/v1/copilot/sessions/{session_id}/build-context
POST /api/v1/copilot/sessions/{session_id}/generate-recommendations
POST /api/v1/copilot/sessions/{session_id}/generate-action-plan
POST /api/v1/copilot/sessions/{session_id}/generate-work-note
POST /api/v1/copilot/sessions/{session_id}/generate-customer-update
POST /api/v1/copilot/sessions/{session_id}/generate-investigation-checklist
POST /api/v1/copilot/recommendations/{recommendation_id}/accept
POST /api/v1/copilot/recommendations/{recommendation_id}/dismiss
POST /api/v1/copilot/sessions/{session_id}/close
POST /api/v1/copilot/analyze
```

Optional if safe:

```text
POST /api/v1/copilot/sessions/{session_id}/create-diagnostic
POST /api/v1/copilot/sessions/{session_id}/create-ticket
```

Do not implement optional endpoints if they cause unsafe coupling.

---

## Copilot Summary

Endpoint:

```text
GET /api/v1/copilot/summary
```

Return:

```json
{
  "open_sessions": 4,
  "recommendations_proposed": 12,
  "recommendations_accepted": 3,
  "action_plans_ready": 2,
  "draft_messages": 5,
  "safe_actions_enabled": 10
}
```

Use actual database queries.

---

## Create Copilot Session

Endpoint:

```text
POST /api/v1/copilot/sessions
```

Request:

```json
{
  "title": "Investigate batch inventory reconciliation failure",
  "description": "Support engineer wants a consolidated view of batch failure evidence.",
  "primary_entity_type": "BATCH_RUN",
  "primary_entity_id": "batch-run-id",
  "primary_ticket_id": null,
  "severity": "HIGH"
}
```

Behavior:

- create session
- status `OPEN`
- do not automatically generate context unless request includes `build_context = true`

Optional request flag:

```json
{
  "build_context": true,
  "generate_recommendations": true
}
```

If flags are true, build context and recommendations after session creation.

---

## Analyze Endpoint

Endpoint:

```text
POST /api/v1/copilot/analyze
```

Purpose:

Convenience endpoint for demos.

Request:

```json
{
  "entity_type": "BATCH_RUN",
  "entity_id": "batch-run-id",
  "title": "Analyze failed batch run"
}
```

Behavior:

- create copilot session
- build context snapshot
- generate recommendations
- generate action plan
- generate investigation checklist
- return consolidated response

This endpoint should still be deterministic.

---

## Session Detail

Endpoint:

```text
GET /api/v1/copilot/sessions/{session_id}
```

Return:

```text
session header
latest context snapshot
all recommendations
latest action plan
messages/drafts
action events
primary linked entity summary
```

---

## Build Context

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/build-context
```

Behavior:

- use session primary entity
- collect related context
- create `copilot_context_snapshots`
- update session status to `ANALYZING` or `RECOMMENDATIONS_READY` if recommendations already exist

---

## Generate Recommendations

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-recommendations
```

Behavior:

- require at least one context snapshot
- apply deterministic rules
- create recommendation records
- avoid duplicate active recommendations with same type/title for same session
- update session status to `RECOMMENDATIONS_READY`

---

## Generate Action Plan

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-action-plan
```

Behavior:

- require context snapshot
- use recommendations if available
- create action plan with ordered steps
- all steps require human approval
- update session status to `ACTION_PLAN_READY`

---

## Generate Work Note

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-work-note
```

Behavior:

- create deterministic work note draft
- store in `copilot_messages`
- do not apply to AMS ticket automatically

---

## Generate Customer Update

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-customer-update
```

Behavior:

- create deterministic customer update draft
- store in `copilot_messages`
- do not send externally

---

## Generate Investigation Checklist

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/generate-investigation-checklist
```

Behavior:

- create deterministic checklist
- store in `copilot_messages`

---

## Accept Recommendation

Endpoint:

```text
POST /api/v1/copilot/recommendations/{recommendation_id}/accept
```

Behavior:

- update status to `ACCEPTED`
- set `accepted_at`
- create action event

Do not execute the recommendation automatically.

---

## Dismiss Recommendation

Endpoint:

```text
POST /api/v1/copilot/recommendations/{recommendation_id}/dismiss
```

Behavior:

- update status to `DISMISSED`
- set `dismissed_at`
- create action event

---

## Close Session

Endpoint:

```text
POST /api/v1/copilot/sessions/{session_id}/close
```

Behavior:

- allowed from any non-closed state
- set status `CLOSED`
- set `closed_at`

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
Copilot
Copilot Sessions
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
Health
About
```

---

## Required Frontend Routes

Add:

```text
/copilot
/copilot/sessions
/copilot/sessions/:sessionId
/copilot/analyze
```

Existing routes must continue working.

---

## Copilot Overview Page

Route:

```text
/copilot
```

Display:

- summary cards from `/api/v1/copilot/summary`
- explanation:

```text
The copilot currently uses deterministic governed rules. No external LLM or autonomous remediation is enabled.
```

- quick action buttons:
  - New Copilot Session
  - Analyze Existing Artifact
  - View Sessions

---

## Copilot Sessions Page

Route:

```text
/copilot/sessions
```

Display session table:

```text
session number
title
primary entity type
severity
confidence
status
created by
created at
```

Session number should link to detail page.

Add button:

```text
New Session
```

Simple create form/dialog:

```text
title
description
primary_entity_type
primary_entity_id
severity
build_context
generate_recommendations
```

---

## Copilot Analyze Page

Route:

```text
/copilot/analyze
```

Purpose:

Demo-friendly entry point.

Form:

```text
entity_type
entity_id
title
```

Entity type options:

```text
AMS_TICKET
OPERATIONAL_EXCEPTION
USER_REPORT
MONITORING_ALERT
MONITORING_TRIAGE_CASE
OBSERVABILITY_DIAGNOSTIC
BATCH_RUN
MANUAL
```

On submit:

- call `/api/v1/copilot/analyze`
- navigate to created session detail

Include helper text:

```text
Use an existing ticket, alert, diagnostic case, batch run, exception, or user report ID to build a governed copilot context.
```

---

## Copilot Session Detail Page

Route:

```text
/copilot/sessions/:sessionId
```

Display:

1. Session header
2. Primary entity details
3. Latest context snapshot
4. Recommendations
5. Action plan
6. Generated drafts/messages
7. Action events

Actions:

```text
Build Context
Generate Recommendations
Generate Action Plan
Generate Work Note
Generate Customer Update
Generate Investigation Checklist
Close Session
```

Recommendation actions:

```text
Accept
Dismiss
```

Do not execute accepted recommendation automatically.

---

# Frontend API Client

Create or extend typed API client.

Suggested file:

```text
frontend/src/services/copilotApi.ts
```

Use `VITE_API_BASE_URL`.

Use TanStack Query for data loading.

Use mutations for copilot actions.

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
9. Copilot seed is idempotent
10. Safe actions list works
11. Copilot summary endpoint works
12. Create copilot session
13. Create session with build context
14. Analyze endpoint creates session/context/recommendations/action plan/checklist
15. Build context for AMS ticket
16. Build context for monitoring alert
17. Build context for observability diagnostic case
18. Build context for batch run
19. Generate recommendations from context
20. Recommendation deduplication works
21. Generate action plan
22. Generate work note draft
23. Generate customer update draft
24. Generate investigation checklist
25. Accept recommendation
26. Dismiss recommendation
27. Close session
28. Session detail returns snapshots, recommendations, plans, messages, and events
29. Copilot does not automatically close tickets or resolve alerts

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

- Prompt 09 copilot foundation summary
- deterministic support copilot behavior
- supported entity types
- context snapshot generation
- recommendation generation
- action plan generation
- work note draft generation
- customer update draft generation
- investigation checklist generation
- safe action catalog
- new APIs
- new frontend routes
- seed commands
- validation commands
- backend port `8050`
- frontend port `4001`
- explicit deferred items:
  - external LLM integration
  - LangGraph
  - LiteLLM
  - RAG
  - embeddings/vector store
  - autonomous remediation
  - ServiceNow integration

Update `ARCHITECTURE.md` with:

- copilot module
- governed deterministic context builder
- deterministic recommendation engine
- safe action registry
- copilot session lifecycle
- integration with existing support artifacts
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
pytest
```

Then validate live backend:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/copilot/summary | jq .
curl -sS http://localhost:8050/api/v1/copilot/safe-actions | jq .
curl -sS http://localhost:8050/api/v1/copilot/sessions | jq .
```

To test the analyze flow, first create or reuse a batch failure:

```bash
BATCH_RUN_ID=$(
  curl -sS -X POST http://localhost:8050/api/v1/batch/simulations/inventory-reconciliation-failure \
    -H "Content-Type: application/json" \
    -d '{"create_exception": true, "create_ticket": true, "create_observability": true}' \
  | jq -r '.id // .batch_run_id // .run.id'
)

echo "$BATCH_RUN_ID"
```

Then run copilot analysis:

```bash
curl -sS -X POST http://localhost:8050/api/v1/copilot/analyze \
  -H "Content-Type: application/json" \
  -d "{
    \"entity_type\": \"BATCH_RUN\",
    \"entity_id\": \"${BATCH_RUN_ID}\",
    \"title\": \"Analyze failed inventory reconciliation batch\"
  }" | jq .
```

Then validate sessions:

```bash
curl -sS http://localhost:8050/api/v1/copilot/sessions | jq .
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
```

Manual UI validation:

```text
Open Batch Simulations
Run Inventory Reconciliation Failure with exception/ticket/observability enabled
Copy the generated batch run ID
Open Copilot Analyze
Select BATCH_RUN
Paste the batch run ID
Run Analyze
Open created Copilot Session
Confirm context snapshot is visible
Confirm recommendations are visible
Generate action plan
Generate work note
Generate customer update
Generate investigation checklist
Accept one recommendation
Dismiss one recommendation
Confirm no ticket or alert was automatically resolved
Close session
```

---

# Definition of Done

Prompt 09 is complete only when:

- migration exists
- `copilot_sessions` exists
- `copilot_context_snapshots` exists
- `copilot_recommendations` exists
- `copilot_action_plans` exists
- `copilot_messages` exists
- `copilot_safe_actions` exists
- `copilot_action_events` exists
- copilot seed exists and is idempotent
- safe action API works
- copilot summary API works
- session create/list/detail APIs work
- context build works
- analyze endpoint works
- recommendations are generated deterministically
- recommendation deduplication works
- action plan generation works
- work note draft generation works
- customer update draft generation works
- investigation checklist generation works
- recommendation accept/dismiss works
- close session works
- copilot does not automatically close tickets or resolve alerts
- frontend copilot overview works
- frontend sessions page works
- frontend analyze page works
- frontend session detail page works
- existing warehouse APIs still work
- existing operations/AMS APIs still work
- existing synthetic user APIs still work
- existing monitoring APIs still work
- existing observability APIs still work
- existing batch APIs still work
- backend tests pass
- frontend build passes
- backend remains on port `8050`
- frontend remains on port `4001`
- README updated
- ARCHITECTURE.md updated
- no infrastructure files modified

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Alembic migration name
4. Backend copilot APIs added
5. Frontend routes added
6. Seed command and result
7. Backend validation results
8. Frontend validation results
9. Manual copilot validation result
10. Confirmation that infrastructure files were not modified
11. Confirmation that no external LLM/agent framework was introduced
12. Any TODOs
13. Recommended Git commit message

Recommended commit message:

```text
feat: add ai-native support copilot foundation
```

Do not proceed beyond this prompt.