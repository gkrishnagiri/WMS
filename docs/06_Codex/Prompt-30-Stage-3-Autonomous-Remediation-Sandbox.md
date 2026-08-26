# Prompt 30 – Stage 3 Autonomous Remediation Sandbox

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 18 added agent chat and case intake.

Prompt 19 added deterministic knowledge and RAG foundation.

Prompt 20 added governed real model provider foundation, disabled by default.

Prompt 21 added contextual investigation handoff.

Prompt 22 added Agent Investigation Workspace and Evidence Timeline.

Prompt 23 added Stage 2 approval-gated local safe actions.

Prompt 24 added governed real-model Stage 1 chat activation, disabled by default.

Prompt 25 added guided demo scenario orchestration.

Prompt 26 added executive demo dashboard and value storyboard.

Prompt 27 added demo readiness and showcase mode.

Prompt 28 added UI acceptance testing and evidence capture.

Prompt 29 added OpenAI model costing, model selection, pricing assumptions, usage metering, and smoke-test controls.

An additional completed change added the ability to add and delete governed AI model configurations from the AI model configuration UI.

Your task now is to implement:

```text
Stage 3 Autonomous Remediation Sandbox
```

---

## Business Goal

The platform currently supports:

```text
Stage 1: read-only investigation and guidance
Stage 2: human approval-gated local safe actions
```

Prompt 30 should introduce a **Stage 3 autonomous sandbox** for demo purposes only.

The sandbox should show how an AI-native AMS platform could move from:

```text
detect issue
investigate issue
propose action
request approval
```

to:

```text
detect issue
investigate issue
select safe local action
execute within sandbox constraints
audit every step
stop when guardrails require human review
```

The goal is to demonstrate autonomous operations potential while keeping all execution strictly local, safe, bounded, reversible where possible, and auditable.

---

## Critical Scope Clarification

Prompt 30 implements:

```text
local sandbox autonomy only
autonomous run profiles
autonomous decision loop with max steps
safe local action execution only
policy checks before every step
kill switch
dry-run-first mode
budget/token guardrails
audit timeline
human handback when blocked
UI sandbox console
demo scenario integration
```

Prompt 30 must **not** implement:

```text
production autonomy
shell command execution
arbitrary SQL execution
external ServiceNow integration
external system remediation
customer communication sends
email sending
real warehouse destructive operations
unbounded loops
background autonomous polling
unreviewed model use by default
authentication or authorization
```

All Stage 3 behavior is local EOS demo sandbox behavior only.

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

Do not break existing Prompt 13–29 behavior.

---

## Critical Safety Instructions

You must preserve all existing ports.

You must preserve deterministic/mock behavior as the default.

You must not enable real model calls by default.

You must not require an OpenAI API key for tests, seed, build, startup, or demo validation.

You must not call an external LLM in tests.

You must not call an external model unless explicitly requested and all Prompt 20, 24, and 29 governance checks pass.

You must not execute shell commands from backend APIs.

You must not execute arbitrary SQL from backend APIs.

You must not execute arbitrary user-provided code.

You must not integrate with ServiceNow.

You must not send customer communications externally.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

You must not run autonomous remediation in the background.

You must not create an unbounded autonomous loop.

You must not execute actions outside the predefined safe local action catalog.

Stage 3 must require an explicit sandbox run request.

Stage 3 must have a global kill switch.

Stage 3 must have per-run max steps.

Stage 3 must have per-run max estimated cost.

Stage 3 must have per-run max duration.

Stage 3 must have audit records for every decision, guardrail check, and execution.

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

Implement Stage 3 local autonomous remediation sandbox.

The platform should support:

```text
autonomous sandbox run profiles
sandbox run creation
dry-run autonomous plan
autonomous step execution
safe action selection
guardrail checks
kill switch
pause / stop
human handback
cost/token tracking
run timeline
run audit
sandbox UI console
scenario integration
readiness checks
UI acceptance coverage
```

---

# Stage Modes

Use these stage modes consistently:

```text
STAGE_1_READ_ONLY
STAGE_2_APPROVAL_GATED
STAGE_3_AUTONOMOUS_SANDBOX
```

Important:

```text
STAGE_3_AUTONOMOUS_SANDBOX is not production autonomous remediation.
```

Every API/UI surface must label it clearly as:

```text
Local sandbox only
Demo-safe
No external systems
No shell commands
No arbitrary SQL
No ServiceNow
No customer communication
```

---

# Global Feature Flags

Add or reuse settings:

```text
AUTONOMOUS_SANDBOX_ENABLED=false
AUTONOMOUS_SANDBOX_ALLOW_REAL_MODEL=false
AUTONOMOUS_SANDBOX_MAX_STEPS=5
AUTONOMOUS_SANDBOX_MAX_DURATION_SECONDS=120
AUTONOMOUS_SANDBOX_MAX_ESTIMATED_COST=1.00
AUTONOMOUS_SANDBOX_REQUIRE_DRY_RUN_FIRST=true
AUTONOMOUS_SANDBOX_KILL_SWITCH=false
```

Defaults:

```text
AUTONOMOUS_SANDBOX_ENABLED=false
AUTONOMOUS_SANDBOX_ALLOW_REAL_MODEL=false
AUTONOMOUS_SANDBOX_REQUIRE_DRY_RUN_FIRST=true
AUTONOMOUS_SANDBOX_KILL_SWITCH=false
```

If either condition is true:

```text
AUTONOMOUS_SANDBOX_ENABLED=false
AUTONOMOUS_SANDBOX_KILL_SWITCH=true
```

then no autonomous execution may occur.

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

# Sandbox Action Policy

Stage 3 may execute only these local sandbox-safe actions:

```text
CREATE_AMS_WORK_NOTE_DRAFT
CREATE_CUSTOMER_UPDATE_DRAFT
CREATE_NEXT_STEPS_CHECKLIST
ADD_INTERNAL_CASE_NOTE
UPDATE_AGENT_CASE_STATUS
MARK_AGENT_PROPOSAL_REVIEWED
LINK_EVIDENCE_TO_CASE
ACKNOWLEDGE_OBSERVABILITY_ALERT
ACKNOWLEDGE_MONITORING_ALERT
ACKNOWLEDGE_OPERATIONS_EXCEPTION
CREATE_FOLLOW_UP_TASK_DRAFT
```

Still prohibited:

```text
shell commands
arbitrary SQL
delete data
ship order
cancel order
modify inventory quantity
close real AMS ticket
post to ServiceNow
send customer email
send Teams/Slack message
call external APIs
restart service
change infrastructure
change Docker
change observability stack
```

If the agent wants to do a prohibited action:

```text
stop autonomous execution
create human handback reason
record guardrail event
return status NEEDS_HUMAN_REVIEW
```

---

# Data Model

Add migration:

```text
0020_stage3_autonomous_sandbox
```

Create tables as needed.

## stage3_autonomous_runs

Suggested fields:

```text
id
run_id
case_id
scenario_run_id
session_id
source_object_type
source_object_id
status
mode
profile_code
dry_run_required
dry_run_completed
real_model_requested
real_model_used
provider_code
model_code
max_steps
steps_completed
max_duration_seconds
started_at
completed_at
stopped_at
stop_reason
estimated_total_cost
total_input_tokens
total_completion_tokens
total_tokens
created_by_role
created_at
updated_at
```

Statuses:

```text
CREATED
DRY_RUN_READY
DRY_RUN_COMPLETED
RUNNING
PAUSED
COMPLETED
STOPPED
FAILED
NEEDS_HUMAN_REVIEW
KILLED_BY_SWITCH
BLOCKED_BY_POLICY
BLOCKED_BY_BUDGET
```

## stage3_autonomous_steps

Suggested fields:

```text
id
step_id
run_id
step_number
status
decision_type
decision_summary
selected_action_code
proposal_id
execution_id
guardrail_status
guardrail_reason
input_tokens
completion_tokens
total_tokens
estimated_cost
started_at
completed_at
error_message
created_at
updated_at
```

Step statuses:

```text
PLANNED
SKIPPED_DRY_RUN
RUNNING
SUCCEEDED
FAILED
BLOCKED
NEEDS_HUMAN_REVIEW
```

## stage3_autonomous_events

Suggested fields:

```text
id
event_id
run_id
step_id
event_type
event_title
event_description
severity
metadata_json
created_at
```

Event types:

```text
RUN_CREATED
DRY_RUN_STARTED
DRY_RUN_COMPLETED
AUTONOMY_STARTED
ACTION_SELECTED
GUARDRAIL_PASSED
GUARDRAIL_BLOCKED
ACTION_EXECUTION_STARTED
ACTION_EXECUTION_SUCCEEDED
ACTION_EXECUTION_FAILED
HUMAN_HANDOFF
RUN_COMPLETED
RUN_STOPPED
KILL_SWITCH_TRIGGERED
BUDGET_BLOCKED
```

---

# Autonomous Profiles

Seed deterministic profiles.

Create seed:

```text
backend/app/db/seed_stage3_profiles.py
```

or keep as code-defined catalog if simpler.

Required profiles:

## 1. DRY_RUN_ONLY

```text
No actions executed.
Builds autonomous plan only.
```

## 2. LOCAL_DRAFT_AUTONOMY

Allowed actions:

```text
drafts
internal notes
checklists
case status updates
```

## 3. LOCAL_ACKNOWLEDGEMENT_AUTONOMY

Allowed actions:

```text
local alert/exception acknowledgements
evidence linking
internal notes
```

## 4. HUMAN_HANDOFF_ON_UNCERTAINTY

Behavior:

```text
stop and request human review whenever confidence is low or policy is ambiguous.
```

All profiles must be disabled for execution unless:

```text
AUTONOMOUS_SANDBOX_ENABLED=true
kill switch is not active
explicit run request
dry-run completed if required
```

---

# Backend Service

Create service:

```text
backend/app/services/stage3_autonomous_service.py
```

Responsibilities:

```text
list profiles
create autonomous sandbox run
build dry-run plan
start execution
execute bounded loop
select safe local action
validate action against profile
validate action against policy
validate budget/cost/token limits
call Stage 2 action service for execution
record run/step/event audit
pause/stop run
kill switch enforcement
human handback
summarize run
```

Reuse:

```text
agent_investigation_service
agent_action_service
agent_model_chat_service
ai_model_cost_service
demo_scenario_service
ui_acceptance_service where relevant
```

Do not duplicate action execution logic.

All action execution must go through:

```text
agent_action_service
```

---

# Decision Logic

Default decision logic must be deterministic.

A real model may only be used if:

```text
AUTONOMOUS_SANDBOX_ALLOW_REAL_MODEL=true
REAL_MODEL_ENABLED=true
OPENAI_API_KEY present
provider enabled
model enabled
pricing configured
cost guardrails pass
run request explicitly sets use_real_model=true
acknowledge_cost=true
```

If any condition fails:

```text
use deterministic decision logic
or block if profile requires real model
```

Deterministic action selection examples:

## AMS ticket case

Priority:

```text
CREATE_NEXT_STEPS_CHECKLIST
CREATE_AMS_WORK_NOTE_DRAFT
ADD_INTERNAL_CASE_NOTE
UPDATE_AGENT_CASE_STATUS
```

## User report case

Priority:

```text
CREATE_CUSTOMER_UPDATE_DRAFT
CREATE_AMS_WORK_NOTE_DRAFT
ADD_INTERNAL_CASE_NOTE
```

## Alert case

Priority:

```text
LINK_EVIDENCE_TO_CASE
ACKNOWLEDGE_OBSERVABILITY_ALERT
ADD_INTERNAL_CASE_NOTE
```

## Batch failure case

Priority:

```text
CREATE_NEXT_STEPS_CHECKLIST
CREATE_AMS_WORK_NOTE_DRAFT
ADD_INTERNAL_CASE_NOTE
```

Each step must check for duplicate execution and stop when no safe next action remains.

---

# Dry Run

Dry run must:

```text
inspect case context
identify possible safe local actions
estimate max steps
estimate cost if real model requested
show policy checks
show what would execute
show what will not execute
show human handback conditions
```

Dry run must not mutate operational objects except creating the autonomous run and dry-run audit records.

If `AUTONOMOUS_SANDBOX_REQUIRE_DRY_RUN_FIRST=true`, execution must be blocked until dry run is completed.

---

# Execution

Execution must:

```text
run only after explicit start request
run only if sandbox enabled
run only if kill switch is off
run only if dry run completed when required
run max_steps or fewer
execute only safe local actions
record every step
stop on guardrail block
stop on budget block
stop on duplicate/no-op
stop on uncertainty if profile requires
```

Execution must not:

```text
start background jobs
keep running after HTTP response unless clearly and safely implemented
poll continuously
call external systems
```

Preferred implementation:

```text
synchronous bounded execution within one request
max steps small
clear returned result
```

---

# Backend APIs

Add route prefix:

```text
/api/v1/stage3-autonomy
```

Expose on:

```text
Full backend 8050
Agentic BFF 8065
Operations BFF 8062 read-only plus dry-run
Simulation BFF 8063 optional for sandbox demo
```

Do not expose mutation endpoints on:

```text
Business BFF 8061
Observability BFF 8064
```

Business may expose read-only summary only if useful.

## Required endpoints

Read-only:

```text
GET  /api/v1/stage3-autonomy/status
GET  /api/v1/stage3-autonomy/profiles
GET  /api/v1/stage3-autonomy/runs
GET  /api/v1/stage3-autonomy/runs/{run_id}
GET  /api/v1/stage3-autonomy/runs/{run_id}/steps
GET  /api/v1/stage3-autonomy/runs/{run_id}/events
GET  /api/v1/stage3-autonomy/summary
```

Mutation:

```text
POST /api/v1/stage3-autonomy/runs
POST /api/v1/stage3-autonomy/runs/{run_id}/dry-run
POST /api/v1/stage3-autonomy/runs/{run_id}/start
POST /api/v1/stage3-autonomy/runs/{run_id}/pause
POST /api/v1/stage3-autonomy/runs/{run_id}/stop
POST /api/v1/stage3-autonomy/kill-switch
```

---

## Create run request

```json
{
  "case_id": "case UUID or display case ID if supported",
  "scenario_run_id": null,
  "profile_code": "LOCAL_DRAFT_AUTONOMY",
  "created_by_role": "DEMO_PRESENTER",
  "use_real_model": false,
  "provider_code": "OPENAI_RESPONSES",
  "model_code": "OPENAI_GPT_5_4_MINI",
  "max_steps": 3,
  "max_estimated_cost": 0.25,
  "acknowledge_sandbox_only": true
}
```

Rules:

```text
acknowledge_sandbox_only must be true
max_steps cannot exceed configured maximum
use_real_model=false by default
```

---

## Dry-run request

```json
{
  "requested_by_role": "DEMO_PRESENTER"
}
```

---

## Start execution request

```json
{
  "requested_by_role": "DEMO_PRESENTER",
  "acknowledge_autonomous_sandbox": true,
  "acknowledge_no_external_systems": true,
  "acknowledge_cost": true
}
```

Must reject if acknowledgements are missing.

---

## Kill switch request

```json
{
  "enabled": true,
  "requested_by_role": "DEMO_PRESENTER",
  "reason": "Stop all autonomous sandbox execution."
}
```

Kill switch behavior:

```text
when enabled, no new execution can start
running bounded request should stop at next check if applicable
new runs may be created but cannot execute
status must show kill switch active
```

Since persistent environment variables cannot be updated through the API safely, store a runtime database-backed kill switch state for the app-level sandbox.

Do not modify `.env`.

---

# UI

Create service:

```text
frontend/src/services/stage3AutonomyApi.ts
```

Create pages:

```text
frontend/src/pages/Stage3AutonomyPages.tsx
```

Routes:

```text
/stage3-autonomy
/stage3-autonomy/runs
/stage3-autonomy/runs/:runId
/stage3-autonomy/profiles
```

Visible in:

```text
Full UI
Agentic UI
Operations UI read-only/dry-run
Simulation UI optional
```

Not visible in:

```text
Business UI
Observability UI
```

---

## Stage 3 Dashboard

Show:

```text
sandbox enabled status
kill switch status
real model allowed status
real model default off
max steps
max duration
max cost
runs count
completed runs
blocked runs
needs human review count
total estimated cost
total tokens
latest runs
```

Prominent warnings:

```text
Stage 3 is local sandbox only.
No external systems.
No shell commands.
No arbitrary SQL.
No ServiceNow.
No customer communication.
```

---

## Create Run UI

Allow selecting:

```text
agent case
scenario run
profile
max steps
model usage: deterministic only / governed real model if enabled
OpenAI model from governed catalog
cost limit
```

Require checkboxes:

```text
I understand this is local sandbox only.
I understand no external systems will be called.
I understand only predefined safe local actions can execute.
```

Default:

```text
deterministic only
max steps = 3
```

---

## Dry Run UI

Show:

```text
planned steps
selected actions
policy checks
guardrail status
estimated cost
human handback conditions
what will not be done
```

---

## Execution UI

Show:

```text
Start Autonomous Sandbox Run
Pause
Stop
Kill Switch
step timeline
events
action executions
cost/tokens
final status
human handback reason
```

Execution button must be disabled unless:

```text
sandbox enabled
kill switch off
dry run completed
required acknowledgements checked
```

---

# Investigation Workspace Integration

Update `/agent-investigations/:caseId` to include a Stage 3 panel.

Panel should show:

```text
Stage 3 sandbox status
Create autonomous sandbox run
Dry run
Latest autonomous runs for this case
Open Stage 3 console
```

Do not show the execution start button directly in the investigation workspace unless all warnings and acknowledgements are present.

---

# Guided Scenario Integration

Update guided demo scenarios to include optional Stage 3 step.

For at least:

```text
STUCK_FULFILLMENT_ORDER
BATCH_FAILURE_RECOVERY
```

Add optional presenter step:

```text
Demonstrate Stage 3 autonomous sandbox
```

This step should deep-link to Stage 3 console.

It must not start autonomous execution automatically.

---

# Demo Readiness Integration

Update demo readiness to include:

```text
Stage 3 Sandbox Status
Stage 3 Kill Switch
Stage 3 Profiles
Stage 3 Readiness
Stage 3 Cost Guardrails
```

Readiness must not start autonomous runs.

---

# Executive Dashboard Integration

Update executive demo governance/value dashboard to show:

```text
Stage 3 sandbox available
sandbox disabled by default
kill switch status
autonomous production remediation disabled
local sandbox runs count
human handbacks count
```

Do not imply production autonomous remediation.

---

# UI Acceptance Integration

Add UI acceptance suite or extend governance suite:

```text
STAGE3_AUTONOMOUS_SANDBOX_VALIDATION
```

Steps:

```text
Open Stage 3 dashboard
Verify sandbox disabled by default
Verify kill switch state
Create dry-run-only sandbox run
Run dry-run
Verify planned safe local actions
Verify no external execution
Verify execution is blocked when sandbox disabled
Enable only through documented local configuration if manually desired
Verify Business UI does not expose Stage 3
Verify audit events are visible
```

Do not require real model call.

Do not require actual execution if sandbox disabled by default.

---

# AI Costing Integration

If a Stage 3 run uses a real model:

```text
record usage metering
show input/completion/total tokens
show estimated cost
apply per-run cost guardrail
apply daily cost guardrail
store invocation and pricing snapshots
```

If deterministic:

```text
tokens = 0 or null
estimated cost = 0
```

---

# Scripts

Add scripts:

```text
scripts/stage3-autonomy-status.sh
scripts/stage3-autonomy-dry-run.sh
```

Optional execution script:

```text
scripts/stage3-autonomy-start.sh
```

If added, it must refuse unless explicit confirmation is supplied:

```bash
./scripts/stage3-autonomy-start.sh <RUN_ID> --confirm-autonomous-sandbox
```

Without confirmation, refuse.

Scripts must not call external systems.

---

# Tests

Add backend tests for:

```text
Stage 3 status default disabled
profiles endpoint
create run requires sandbox acknowledgement
create run with deterministic profile works
dry run creates planned steps but no executions
start blocked when sandbox disabled
start blocked when kill switch active
start blocked without dry-run when required
start blocked without acknowledgements
bounded deterministic execution with sandbox enabled through test settings
execution only calls agent_action_service
execution creates run steps/events
execution stops at max_steps
execution stops on prohibited action
execution prevents duplicate executions
human handback recorded on uncertainty/block
cost guardrail blocks run
real model not called by default
mocked real model path records usage if explicitly enabled in test
BFF exposure rules
Business BFF does not expose mutation
Observability BFF not exposed
demo readiness includes Stage 3 checks
executive dashboard includes Stage 3 governance
UI acceptance includes Stage 3 suite
no OpenAI API key required
no external LLM/API call required
no shell/SQL/external system execution from APIs
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
python -m app.db.seed_stage3_profiles

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

## Status and profiles

```bash
curl -sS http://localhost:8050/api/v1/stage3-autonomy/status | jq .
curl -sS http://localhost:8050/api/v1/stage3-autonomy/profiles | jq .
curl -sS http://localhost:8050/api/v1/stage3-autonomy/summary | jq .
```

Expected by default:

```text
sandbox disabled
real model not allowed
kill switch status visible
no autonomous execution active
```

## Create investigation case if needed

Use existing agent investigation from scenarios, or create via AMS ticket handoff.

```bash
TICKET_ID=$(
  curl -sS http://localhost:8050/api/v1/ams/tickets \
  | jq -r 'if type=="array" then (.[0].ticket_id // .[0].id) elif has("items") then (.items[0].ticket_id // .items[0].id) elif has("tickets") then (.tickets[0].ticket_id // .tickets[0].id) else empty end'
)

HANDOFF=$(
  curl -sS -X POST "http://localhost:8050/api/v1/agent-chat/intake/from-ams-ticket/${TICKET_ID}" \
    -H "Content-Type: application/json" \
    -d '{
      "initial_message": "Investigate this AMS ticket for Stage 3 sandbox validation.",
      "reuse_existing": true,
      "use_real_model": false
    }'
)

echo "$HANDOFF" | jq .
CASE_ID=$(echo "$HANDOFF" | jq -r '.case_uuid // .case_id')
echo "$CASE_ID"
```

## Create Stage 3 run

```bash
STAGE3_RUN=$(
  curl -sS -X POST http://localhost:8050/api/v1/stage3-autonomy/runs \
    -H "Content-Type: application/json" \
    -d "{
      \"case_id\": \"${CASE_ID}\",
      \"profile_code\": \"LOCAL_DRAFT_AUTONOMY\",
      \"created_by_role\": \"DEMO_PRESENTER\",
      \"use_real_model\": false,
      \"max_steps\": 3,
      \"max_estimated_cost\": 0.25,
      \"acknowledge_sandbox_only\": true
    }"
)

echo "$STAGE3_RUN" | jq .
RUN_ID=$(echo "$STAGE3_RUN" | jq -r '.run_id')
echo "$RUN_ID"
```

## Dry run

```bash
curl -sS -X POST "http://localhost:8050/api/v1/stage3-autonomy/runs/${RUN_ID}/dry-run" \
  -H "Content-Type: application/json" \
  -d '{"requested_by_role":"DEMO_PRESENTER"}' | jq .
```

Expected:

```text
planned steps returned
safe local actions only
no execution performed
```

## Start should be blocked by default

```bash
curl -sS -X POST "http://localhost:8050/api/v1/stage3-autonomy/runs/${RUN_ID}/start" \
  -H "Content-Type: application/json" \
  -d '{
    "requested_by_role": "DEMO_PRESENTER",
    "acknowledge_autonomous_sandbox": true,
    "acknowledge_no_external_systems": true,
    "acknowledge_cost": true
  }' | jq .
```

Expected by default:

```text
blocked because AUTONOMOUS_SANDBOX_ENABLED=false
no actions executed
audit event recorded
```

## Kill switch

```bash
curl -sS -X POST http://localhost:8050/api/v1/stage3-autonomy/kill-switch \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "requested_by_role": "DEMO_PRESENTER",
    "reason": "Manual validation of kill switch."
  }' | jq .

curl -sS http://localhost:8050/api/v1/stage3-autonomy/status | jq .
```

Then turn it off again for normal demo state:

```bash
curl -sS -X POST http://localhost:8050/api/v1/stage3-autonomy/kill-switch \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "requested_by_role": "DEMO_PRESENTER",
    "reason": "Manual validation complete."
  }' | jq .
```

---

# BFF Validation

```bash
curl -sS http://localhost:8065/api/v1/stage3-autonomy/status | jq .
curl -sS http://localhost:8062/api/v1/stage3-autonomy/status | jq .

curl -i -sS http://localhost:8061/api/v1/stage3-autonomy/status | head
curl -i -sS http://localhost:8064/api/v1/stage3-autonomy/status | head
```

Expected:

```text
Agentic BFF: 200
Operations BFF: 200 read-only/dry-run if exposed
Business BFF: 404 or read-only only if intentionally exposed
Observability BFF: 404
```

---

# Script Validation

```bash
cd ~/giri/AIProjects/WMS

./scripts/stage3-autonomy-status.sh
./scripts/stage3-autonomy-dry-run.sh
```

Expected:

```text
scripts call local EOS APIs only
no real model call
no external service call
no autonomous execution unless explicitly confirmed
```

---

# Manual UI Validation

Open:

```text
http://localhost:4015/stage3-autonomy
http://localhost:4015/stage3-autonomy/profiles
http://localhost:4015/stage3-autonomy/runs
```

Also open Full UI:

```text
http://localhost:4001/stage3-autonomy
```

Validate:

```text
Stage 3 dashboard loads
sandbox disabled by default
kill switch visible
real model allowed status visible
warnings visible
profiles visible
create run UI visible
dry run works
planned safe local actions visible
execution start blocked by default
no API key field exists
no shell/SQL/external system controls exist
```

Open an investigation workspace:

```text
http://localhost:4015/agent-investigations
```

Validate:

```text
Stage 3 sandbox panel visible
create sandbox run link/control visible
dry-run link/control visible
latest Stage 3 runs visible
execution controls are gated
```

---

# Documentation Updates

Update `README.md` with:

```text
Stage 3 autonomous sandbox overview
sandbox safety boundaries
kill switch
dry-run-first behavior
how to create a dry-run
why execution is blocked by default
how cost/token tracking applies
how to optionally enable sandbox locally
```

Update `ARCHITECTURE.md` with:

```text
Stage 3 architecture
run/step/event model
bounded decision loop
safe action policy
relationship to Stage 2 action service
kill switch design
cost guardrails
real-model optional path
production boundary
```

Document clearly:

```text
Prompt 30 adds local autonomous sandbox only.
It does not enable production autonomous remediation.
It does not enable real model calls by default.
It does not execute shell commands.
It does not execute arbitrary SQL.
It does not call ServiceNow.
It does not send customer communications.
```

---

# Definition of Done

Prompt 30 is complete only when:

- Stage 3 autonomous service exists
- Stage 3 APIs exist
- Stage 3 migration exists
- profiles exist
- status endpoint works
- create run works
- dry run works
- dry run does not execute actions
- execution is blocked by default
- kill switch works
- bounded execution works in tests when sandbox enabled via test settings
- only safe local actions can execute
- all execution goes through Stage 2 action service
- duplicate execution is prevented
- human handback is recorded
- cost/token tracking integrates with Prompt 29
- Agentic UI Stage 3 dashboard exists
- Stage 3 panel exists in investigation workspace
- guided scenarios link to Stage 3 optional step
- demo readiness includes Stage 3 checks
- executive dashboard includes Stage 3 governance
- UI acceptance includes Stage 3 suite
- scripts exist and work
- backend tests pass
- frontend build passes
- demo stack validation passes
- no OpenAI API key is required
- no default external model call occurs
- autonomous sandbox execution is disabled by default
- no production autonomous remediation is introduced
- no shell commands are executed from APIs
- no arbitrary SQL execution is introduced
- no ServiceNow integration is introduced
- no authentication is introduced
- no Docker Compose change unless justified
- no observability infrastructure change unless justified
- README updated
- ARCHITECTURE.md updated
- Prompt 30 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary
4. Stage 3 profile summary
5. Sandbox status behavior
6. Kill switch behavior
7. Dry-run behavior
8. Execution behavior
9. Safe action policy behavior
10. Human handback behavior
11. Cost/token integration summary
12. Real-model optional path summary
13. Backend APIs added
14. BFF exposure summary
15. Frontend routes/pages added
16. Investigation workspace integration summary
17. Guided scenario integration summary
18. Demo readiness integration summary
19. Executive dashboard integration summary
20. UI acceptance integration summary
21. Scripts added
22. Backend test results
23. Frontend build results
24. Demo stack validation results
25. Manual API validation results
26. Script validation results
27. Manual UI validation results
28. Confirmation deterministic/mock remains default
29. Confirmation no real model call occurs by default
30. Confirmation autonomous sandbox execution is disabled by default
31. Confirmation no production autonomous remediation was introduced
32. Confirmation no shell command/arbitrary SQL/external system execution was introduced
33. Confirmation no ServiceNow/authentication was introduced
34. TODOs or limitations
35. Recommended Git commit message

Recommended commit message:

```text
feat: add stage3 autonomous sandbox
```

Do not proceed beyond this prompt.