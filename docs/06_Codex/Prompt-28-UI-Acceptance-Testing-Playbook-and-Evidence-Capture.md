# Prompt 28 – UI Acceptance Testing Playbook and Evidence Capture

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

Prompt 22 added Agent Investigation Workspace and Evidence Timeline.

Prompt 23 added Stage 2 approval-gated local safe actions.

Prompt 24 added governed real-model Stage 1 chat activation, disabled by default.

Prompt 25 added guided demo scenario orchestration.

Prompt 26 added Executive Demo Dashboard and Value Storyboard.

Prompt 27 added demo readiness hardening, showcase preparation, reset profiles, smoke reports, URL launcher, and UI test guide.

Your task now is to implement:

```text
UI Acceptance Testing Playbook and Evidence Capture
```

---

## Business Goal

The platform now has a strong demo stack, but the user needs to test and validate the system primarily through the browser.

Prompt 28 should create a structured UI acceptance testing capability so a tester or presenter can:

```text
open the application
follow click-by-click UI flows
track pass/fail status
capture evidence notes
record screenshot references
validate each demo scenario
validate agent-assisted mode
validate human-approval mode
validate real-model disabled/fallback behavior
validate governance boundaries
export a test evidence report
repeat testing after reset/showcase preparation
```

The goal is to reduce dependence on backend curl commands and make the platform testable from the UI.

---

## Critical Scope

Prompt 28 implements:

```text
UI acceptance test catalog
UI test run tracking
manual step-by-step test execution
browser-first evidence capture
pass/fail tracking
screenshot/reference notes
test coverage dashboard
test evidence report export
guided UI test flows
deep links into tested screens
```

Prompt 28 must not implement:

```text
browser automation framework unless already present
external testing SaaS
real model calls by default
autonomous remediation
shell command execution from APIs
arbitrary SQL execution from APIs
ServiceNow integration
customer communications
authentication / authorization
```

This prompt is about **manual browser-driven testing**, not automated end-to-end browser execution.

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

Do not break existing Prompt 13–27 behavior.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve deterministic/mock behavior as the default.

You must not enable real model calls by default.

You must not require an OpenAI API key.

You must not call an external LLM in tests.

You must not execute shell commands from backend APIs.

You must not execute arbitrary SQL from backend APIs.

You must not execute arbitrary user-provided code.

You must not introduce autonomous remediation.

You must not integrate with ServiceNow.

You must not send customer communications externally.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

UI acceptance tests must be local-demo scoped.

No test flow should silently mutate data unless the step clearly says it will start a demo scenario, reset demo data, approve a safe local action, or execute an approval-gated safe local action.

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

Implement a UI acceptance testing module.

The platform should support:

```text
UI test catalog
UI test suites
UI test cases
UI test steps
UI test runs
per-step pass/fail
evidence notes
screenshot reference fields
observed result fields
tester role fields
test report export
coverage dashboard
guided deep links
reset/showcase integration
```

---

# Test Suites

Create a deterministic UI test catalog with these suites:

## 1. Executive Demo Validation

Purpose:

```text
Validate executive dashboard, value storyboard, governance view, and commercial model narrative.
```

Experience:

```text
Business UI
Full UI
```

Core pages:

```text
/executive-demo
/executive-demo/storyboard
/executive-demo/value
/executive-demo/governance
```

---

## 2. Demo Readiness and Showcase Validation

Purpose:

```text
Validate readiness score, smoke report, URL launcher, reset profiles, and showcase preparation.
```

Experience:

```text
Full UI
Operations UI
Simulation UI
Agentic UI
Business UI read-only
```

Core pages:

```text
/demo-readiness
/demo-readiness/showcase
/demo-readiness/ui-test-guide
/demo-readiness/smoke-report
```

---

## 3. Guided Scenario Validation

Purpose:

```text
Validate the four guided demo scenarios and their presenter flows.
```

Experience:

```text
Full UI
Operations UI
Simulation UI
Agentic UI
```

Core pages:

```text
/demo-scenarios
/demo-scenarios/runs
/demo-scenarios/runs/:runId
```

Test all scenarios:

```text
STUCK_FULFILLMENT_ORDER
BATCH_FAILURE_RECOVERY
USER_REPORTED_SHIPMENT_DELAY
OBSERVABILITY_ALERT_NOISE_ROOT_CAUSE
```

---

## 4. Operations-to-Agent Handoff Validation

Purpose:

```text
Validate Investigate with Agent from operational objects.
```

Experience:

```text
Operations UI
Agentic UI
Full UI
```

Source objects:

```text
AMS ticket
Observability alert
Batch run
User report
Diagnostic case
Monitoring triage case
Operations exception
```

---

## 5. Agent Investigation Workspace Validation

Purpose:

```text
Validate source context, evidence timeline, knowledge, known errors, drafts, chat, action proposals, and scenario linkage.
```

Experience:

```text
Agentic UI
Operations UI
Full UI
```

Core pages:

```text
/agent-investigations
/agent-investigations/:caseId
```

---

## 6. Model-Assisted Stage 1 Chat Fallback Validation

Purpose:

```text
Validate model status, preview context, dry run, deterministic ask, and safe fallback when real model is disabled.
```

Experience:

```text
Agentic UI
Operations UI
Full UI
```

Important:

```text
Do not require real model call.
Do not require OpenAI API key.
Validate disabled/fallback behavior only.
```

---

## 7. Stage 2 Approval-Gated Action Validation

Purpose:

```text
Validate safe action proposals, dry run, approval, rejection, execution audit, duplicate prevention, and timeline updates.
```

Experience:

```text
Agentic UI
Operations UI
Full UI
```

Important:

```text
Only predefined local safe actions may execute.
No autonomous remediation.
```

---

## 8. Governance Boundary Validation

Purpose:

```text
Validate experience boundaries, Business read-only behavior, real model default off, autonomous remediation disabled, ServiceNow absent, and API key not exposed.
```

Experience:

```text
Business UI
Operations UI
Simulation UI
Observability UI
Agentic UI
Full UI
```

---

# Data Model

Add migration if needed:

```text
0018_ui_acceptance_testing
```

Suggested tables:

```text
ui_test_suites
ui_test_cases
ui_test_steps
ui_test_runs
ui_test_step_results
ui_test_run_events
```

## ui_test_suites

Suggested fields:

```text
id
suite_code
title
description
experience
sort_order
is_enabled
created_at
updated_at
```

## ui_test_cases

Suggested fields:

```text
id
case_code
suite_code
title
description
preconditions
expected_outcome
primary_url
sort_order
is_enabled
created_at
updated_at
```

## ui_test_steps

Suggested fields:

```text
id
step_code
case_code
step_order
instruction
target_url
what_to_click
expected_result
evidence_to_capture
is_mutating_step
safety_note
created_at
updated_at
```

## ui_test_runs

Suggested fields:

```text
id
run_id
run_title
status
tester_role
started_at
completed_at
summary
created_at
updated_at
```

Statuses:

```text
NOT_STARTED
IN_PROGRESS
PASSED
PASSED_WITH_WARNINGS
FAILED
ABORTED
```

## ui_test_step_results

Suggested fields:

```text
id
run_id
suite_code
case_code
step_code
status
observed_result
evidence_note
screenshot_reference
defect_note
tested_by_role
tested_at
created_at
updated_at
```

Statuses:

```text
NOT_TESTED
PASSED
FAILED
BLOCKED
WARNING
SKIPPED
```

## ui_test_run_events

Suggested fields:

```text
id
run_id
event_type
event_title
event_description
created_at
```

---

# Seed Data

Create seed:

```text
backend/app/db/seed_ui_acceptance_tests.py
```

Seed deterministic suites, cases, and steps.

The seed must be idempotent.

The seed must not create test runs by default.

The seed must not call external services.

Add this seed to validation docs and scripts where appropriate.

---

# Backend Service

Create service:

```text
backend/app/services/ui_acceptance_service.py
```

Responsibilities:

```text
list test suites
list test cases
list test steps
start test run
record step result
update run status
calculate test coverage
build evidence report
export markdown report
link test steps to frontend URLs
integrate with demo readiness summary
```

Create route:

```text
backend/app/api/routes/ui_acceptance.py
```

Create schemas:

```text
backend/app/schemas/ui_acceptance.py
```

---

# Backend APIs

Add route prefix:

```text
/api/v1/ui-acceptance
```

Expose on:

```text
Full backend 8050
Business BFF 8061 read-only catalog/report only
Operations BFF 8062
Simulation BFF 8063
Agentic BFF 8065
```

Do not expose on:

```text
Observability BFF 8064
```

unless there is a clear reason.

---

## Required endpoints

Read-only:

```text
GET  /api/v1/ui-acceptance/summary
GET  /api/v1/ui-acceptance/suites
GET  /api/v1/ui-acceptance/cases
GET  /api/v1/ui-acceptance/cases/{case_code}
GET  /api/v1/ui-acceptance/runs
GET  /api/v1/ui-acceptance/runs/{run_id}
GET  /api/v1/ui-acceptance/runs/{run_id}/report
GET  /api/v1/ui-acceptance/runs/{run_id}/report.md
GET  /api/v1/ui-acceptance/coverage
```

Mutation:

```text
POST /api/v1/ui-acceptance/runs/start
POST /api/v1/ui-acceptance/runs/{run_id}/step-results
POST /api/v1/ui-acceptance/runs/{run_id}/complete
POST /api/v1/ui-acceptance/runs/{run_id}/abort
```

Business BFF must not expose mutation endpoints.

---

## Start run request

```json
{
  "run_title": "Prompt 28 UI Acceptance Test Run",
  "tester_role": "DEMO_TESTER",
  "suite_codes": [
    "EXECUTIVE_DEMO_VALIDATION",
    "DEMO_READINESS_SHOWCASE_VALIDATION",
    "GUIDED_SCENARIO_VALIDATION"
  ]
}
```

If `suite_codes` is empty or missing, include all enabled suites.

---

## Step result request

```json
{
  "suite_code": "GUIDED_SCENARIO_VALIDATION",
  "case_code": "STUCK_FULFILLMENT_ORDER_FLOW",
  "step_code": "OPEN_SCENARIO_CATALOG",
  "status": "PASSED",
  "observed_result": "Scenario catalog opened and four cards were visible.",
  "evidence_note": "Validated on Operations UI at port 4012.",
  "screenshot_reference": "screenshots/prompt28/stuck-order-step-01.png",
  "defect_note": "",
  "tested_by_role": "DEMO_TESTER"
}
```

---

## Report behavior

The report should include:

```text
run id
tester role
start/completion timestamps
overall status
suite summary
case summary
step results
evidence notes
screenshot references
defect notes
coverage metrics
safety confirmations
known limitations
```

Markdown report endpoint should return `text/markdown`.

No PDF generation is required.

No screenshot binary upload is required.

---

# Frontend UI

Create service:

```text
frontend/src/services/uiAcceptanceApi.ts
```

Create page:

```text
frontend/src/pages/UIAcceptancePages.tsx
```

Routes:

```text
/ui-acceptance
/ui-acceptance/suites
/ui-acceptance/runs
/ui-acceptance/runs/:runId
/ui-acceptance/runs/:runId/report
```

Visible in:

```text
Full UI
Business UI read-only
Operations UI
Simulation UI
Agentic UI
```

Not required in:

```text
Observability UI
```

---

## UI Acceptance Dashboard

Show:

```text
overall test coverage
enabled suites
total cases
total steps
latest run
latest run status
pass/fail counts
warnings/blockers
start new test run button
```

Business UI:

```text
read-only catalog/report visibility
no start/record/complete controls
```

---

## Test Suite Page

Show:

```text
suite title
description
experience
test cases
step count
primary URLs
safety notes
```

---

## Test Run Page

This is the most important page.

Show:

```text
run title
tester role
status
progress
suite/case/step tree
current step instruction
target URL
Open Target button
what to click
expected result
evidence to capture
safety note
status selector
observed result text box
evidence note text box
screenshot reference text box
defect note text box
Save Step Result button
Complete Run button
Abort Run button
```

Status selector options:

```text
PASSED
FAILED
BLOCKED
WARNING
SKIPPED
```

Add helper text:

```text
Screenshots are not uploaded in this version. Enter a local screenshot filename or note where the evidence is stored.
```

---

## Report Page

Show:

```text
overall run status
suite summary
case summary
step-by-step results
evidence notes
screenshot references
defects
copy markdown report button
download markdown report link if feasible
```

Do not require binary file generation.

---

# Integration with Demo Readiness

Update demo readiness to include UI acceptance checks:

```text
UI Acceptance Catalog
UI Acceptance Run Tracker
Evidence Report
Latest UI Test Run
```

Readiness should check:

```text
http://localhost:8050/api/v1/ui-acceptance/summary
```

Do not start a test run during readiness checks.

---

# Scripts

Add scripts:

```text
scripts/ui-acceptance-summary.sh
scripts/ui-acceptance-start-run.sh
scripts/ui-acceptance-report.sh
```

Rules:

```text
scripts call local backend APIs only
scripts do not run browser automation
scripts do not mutate demo data except starting/completing test run records
scripts do not call real model
```

Example:

```bash
./scripts/ui-acceptance-summary.sh
./scripts/ui-acceptance-start-run.sh
./scripts/ui-acceptance-report.sh <RUN_ID>
```

---

# Manual Test Flow Content

Seed test steps should include click-by-click guidance for these flows.

## Executive Demo Flow

Steps:

```text
Open Business UI executive demo page
Verify KPI cards
Verify storyboard sections
Verify governance summary
Verify commercial model view
Verify assumption disclaimer
Verify no mutation controls
```

## Demo Readiness Flow

Steps:

```text
Open demo readiness
Verify readiness score
Open smoke report
Open UI test guide
Open URL launcher
Prepare showcase in allowed experience
Verify Business UI is read-only
```

## Stuck Fulfillment Order Flow

Steps:

```text
Open guided scenarios
Start Stuck Fulfillment Order
Advance to issue induction
Open generated AMS ticket or exception
Click Investigate with Agent
Open investigation workspace
Verify evidence timeline
Verify knowledge section
Verify model chat panel is off/default fallback
Verify action proposals
Dry-run a proposal
Approve a safe proposal
Execute approved local safe action
Verify audit and timeline
```

## Batch Failure Recovery Flow

Steps:

```text
Start Batch Failure Recovery scenario
Open batch run
Open alert if generated
Investigate with Agent
Verify batch evidence and runbook knowledge
Generate drafts
Approve next-steps checklist action
Verify audit
```

## User-Reported Shipment Delay Flow

Steps:

```text
Start User-Reported Shipment Delay scenario
Open user report
Open linked AMS ticket
Investigate with Agent
Verify customer-update draft
Verify Business-facing boundaries
```

## Observability Alert Noise Flow

Steps:

```text
Start Observability Alert Noise scenario
Open alert/triage artifacts
Investigate with Agent
Verify grouped evidence
Verify governance and safe acknowledgment proposal
```

## Model Chat Fallback Flow

Steps:

```text
Open investigation workspace
Verify real-model toggle off
Preview context
Dry run
Ask deterministic question
Toggle real-model request while disabled
Verify fallback response
Verify no actions executed
```

## Governance Boundary Flow

Steps:

```text
Open Business UI
Verify admin/mutation routes hidden or blocked
Open Observability UI
Verify unrelated agent/demo readiness routes unavailable if designed that way
Open AI config real model page
Verify API key is not displayed
Verify real model default off
Verify autonomous remediation disabled
```

---

# Tests

Add backend tests for:

```text
UI acceptance seed idempotency
summary endpoint
suite list endpoint
case detail endpoint
start run
record step result
complete run
abort run
report endpoint
markdown report endpoint
coverage endpoint
Business BFF read-only exposure
Business BFF mutation blocked
Observability BFF not exposed
demo readiness includes UI acceptance readiness
scripts exist and are executable
no OpenAI API key required
no external model call required
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

## UI acceptance summary

```bash
curl -sS http://localhost:8050/api/v1/ui-acceptance/summary | jq .
curl -sS http://localhost:8050/api/v1/ui-acceptance/suites | jq .
curl -sS http://localhost:8050/api/v1/ui-acceptance/coverage | jq .
```

## Start UI test run

```bash
UI_RUN=$(
  curl -sS -X POST http://localhost:8050/api/v1/ui-acceptance/runs/start \
    -H "Content-Type: application/json" \
    -d '{
      "run_title": "Prompt 28 Manual UI Acceptance Run",
      "tester_role": "DEMO_TESTER"
    }'
)

echo "$UI_RUN" | jq .

RUN_ID=$(echo "$UI_RUN" | jq -r '.run_id')
echo "$RUN_ID"
```

## Record a step result

Use a valid suite/case/step from the returned catalog.

```bash
curl -sS -X POST "http://localhost:8050/api/v1/ui-acceptance/runs/${RUN_ID}/step-results" \
  -H "Content-Type: application/json" \
  -d '{
    "suite_code": "EXECUTIVE_DEMO_VALIDATION",
    "case_code": "EXECUTIVE_DASHBOARD_READ_ONLY",
    "step_code": "OPEN_EXECUTIVE_DEMO",
    "status": "PASSED",
    "observed_result": "Executive dashboard opened successfully.",
    "evidence_note": "KPI cards and storyboard sections were visible.",
    "screenshot_reference": "screenshots/prompt28/executive-demo-01.png",
    "defect_note": "",
    "tested_by_role": "DEMO_TESTER"
  }' | jq .
```

## Complete run

```bash
curl -sS -X POST "http://localhost:8050/api/v1/ui-acceptance/runs/${RUN_ID}/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Initial UI acceptance smoke completed."
  }' | jq .
```

## Report

```bash
curl -sS "http://localhost:8050/api/v1/ui-acceptance/runs/${RUN_ID}/report" | jq .
curl -sS "http://localhost:8050/api/v1/ui-acceptance/runs/${RUN_ID}/report.md"
```

---

# BFF Validation

```bash
curl -sS http://localhost:8061/api/v1/ui-acceptance/summary | jq .
curl -sS http://localhost:8062/api/v1/ui-acceptance/summary | jq .
curl -sS http://localhost:8063/api/v1/ui-acceptance/summary | jq .
curl -sS http://localhost:8065/api/v1/ui-acceptance/summary | jq .

curl -i -sS -X POST http://localhost:8061/api/v1/ui-acceptance/runs/start \
  -H "Content-Type: application/json" \
  -d '{}' | head

curl -i -sS http://localhost:8064/api/v1/ui-acceptance/summary | head
```

Expected:

```text
Business BFF read-only summary: 200
Operations BFF: 200
Simulation BFF: 200
Agentic BFF: 200
Business mutation: 404 or blocked
Observability BFF: 404
```

---

# Script Validation

```bash
cd ~/giri/AIProjects/WMS

./scripts/ui-acceptance-summary.sh
./scripts/ui-acceptance-start-run.sh
./scripts/ui-acceptance-report.sh <RUN_ID>
```

Expected:

```text
scripts call local EOS APIs only
no browser automation
no real model call
no external service call
```

---

# Manual UI Validation

Open:

```text
http://localhost:4001/ui-acceptance
http://localhost:4001/ui-acceptance/suites
http://localhost:4001/ui-acceptance/runs
```

Also open:

```text
http://localhost:4011/ui-acceptance
http://localhost:4012/ui-acceptance
http://localhost:4013/ui-acceptance
http://localhost:4015/ui-acceptance
```

Validate:

```text
test dashboard loads
test suites visible
test cases visible
start run works in allowed experiences
Business UI is read-only
test run page shows step tree
current step instructions visible
Open Target button works
observed result can be entered
evidence note can be entered
screenshot reference can be entered
step result can be saved
run can be completed
report page loads
markdown report can be copied or viewed
```

Then run at least one browser-only flow:

```text
Executive Demo Validation
Demo Readiness Validation
Stuck Fulfillment Order Flow
Model Chat Fallback Flow
Approval-Gated Action Flow
Governance Boundary Flow
```

Record step results in the UI.

---

# Documentation Updates

Update `README.md` with:

```text
UI acceptance testing overview
how to start a UI test run
how to record evidence
how to use screenshot references
how to export/read markdown report
browser-first testing workflow
```

Update `ARCHITECTURE.md` with:

```text
UI acceptance testing architecture
test catalog and run tracking
evidence capture model
relationship to demo readiness, guided scenarios, investigation workspace, and action audit
```

Document clearly:

```text
Prompt 28 adds manual UI acceptance testing support.
It does not add browser automation.
It does not enable real model calls by default.
It does not execute autonomous remediation.
It does not integrate with ServiceNow.
```

---

# Definition of Done

Prompt 28 is complete only when:

- UI acceptance service exists
- UI acceptance API exists
- UI acceptance seed exists
- deterministic test suites exist
- deterministic test cases exist
- deterministic test steps exist
- start test run works
- record step result works
- complete run works
- abort run works
- report endpoint works
- markdown report endpoint works
- coverage endpoint works
- frontend UI acceptance dashboard exists
- frontend test run page exists
- evidence capture fields exist
- screenshot reference field exists
- report page exists
- Business UI is read-only
- demo readiness includes UI acceptance status
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
- Prompt 28 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. UI acceptance catalog summary
5. UI test run behavior
6. Evidence capture behavior
7. Report/export behavior
8. Coverage behavior
9. Backend APIs added
10. BFF exposure summary
11. Frontend routes/pages added
12. Demo readiness integration summary
13. Scripts added
14. Backend test results
15. Frontend build results
16. Demo stack validation results
17. Manual API validation results
18. Script validation results
19. Manual UI validation results
20. Confirmation deterministic/mock remains default
21. Confirmation no real model call occurs by default
22. Confirmation no autonomous remediation was introduced
23. Confirmation no shell command/arbitrary SQL/external system execution was introduced
24. Confirmation no ServiceNow/authentication was introduced
25. TODOs or limitations
26. Recommended Git commit message

Recommended commit message:

```text
feat: add ui acceptance testing playbook
```

Do not proceed beyond this prompt.

## Implementation record

Implemented in the EOS workspace. Added migration `0018_ui_acceptance_testing`,
manual UI acceptance models/service/routes, idempotent eight-suite catalog seed,
JSON and Markdown evidence reports, coverage tracking, experience-aware BFF
boundaries, frontend dashboard/suite/run/report pages, and local acceptance
scripts. The catalog covers executive, readiness, guided scenarios, handoffs,
workspace, model fallback, approval-gated action, and governance flows.
Business is read-only; Observability has no acceptance routes. Screenshot
references are text-only and no browser automation was added. Deterministic
behavior remains the default, and no real model, shell, SQL, external system,
ServiceNow, customer communication, authentication, or autonomous remediation
capability was introduced.
