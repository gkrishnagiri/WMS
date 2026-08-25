# Prompt 27 – Demo Readiness Hardening and One-Command Showcase Mode

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

Your task now is to implement:

```text
Demo Readiness Hardening and One-Command Showcase Mode
```

---

## Business Goal

The platform now has the core AI-native AMS demo capabilities, but the presenter needs a reliable way to:

```text
reset demo data
prepare a clean demo state
verify all services are ready
open the right URLs
run UI-driven demo flows
avoid manual backend/curl work
repeat the same scenarios consistently
```

Prompt 27 should make EOS easier to use as a repeatable customer demo environment.

The user should be able to run one script or open one page and know:

```text
Is the demo stack healthy?
Are all required seed datasets present?
Are the guided scenarios ready?
Can I reset and replay the use cases?
Which UI pages should I open?
Which demo steps should I click through?
Are model calls disabled by default?
Are autonomous actions disabled?
Are approval-gated actions working?
```

---

## Critical Scope

Prompt 27 implements:

```text
demo readiness hardening
safe reset profiles
showcase mode preparation
UI demo guide
readiness report
smoke test report
presenter URL launcher list
scenario replay support
demo checklist
```

Prompt 27 must not implement:

```text
autonomous remediation
real model calls by default
shell command execution from the app
arbitrary SQL execution from the app
external ServiceNow integration
customer communications
authentication / authorization
production reset tooling
```

All reset behavior must be clearly scoped to **local EOS demo data**.

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

Do not break existing Prompt 13–26 behavior.

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

Reset functionality must be safe, explicit, and local-demo scoped.

No reset endpoint should delete database schema.

No reset endpoint should drop the database.

No reset endpoint should wipe audit history unless protected by an explicit local-dev-only confirmation string.

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

Implement demo readiness and showcase support.

The platform should support:

```text
demo readiness dashboard
safe reset profiles
showcase preparation
seed verification
scenario readiness
UI test guide
presenter checklist
URL launcher list
smoke report
repeatable scenario replay
readiness scoring
```

---

# Reset Profiles

Implement reset profiles with clear behavior.

## 1. SOFT_RESET

Purpose:

```text
Prepare the demo for another run without deleting history.
```

Behavior:

```text
mark active demo scenario runs as RESET
mark incomplete guided steps as reset/skipped if needed
preserve scenario events
preserve action audit
preserve model invocation audit
preserve agent investigations
preserve AMS tickets
preserve operational data
```

Use case:

```text
Presenter wants to restart guided scenarios while keeping audit history.
```

---

## 2. SHOWCASE_RESET

Purpose:

```text
Prepare a clean, deterministic demo-ready state.
```

Behavior:

```text
run idempotent seed verification
ensure four guided scenarios exist
ensure warehouse seed data exists
ensure monitoring/batch/knowledge/AI config seeds exist
ensure no real model is enabled by default
reset active scenario runs
create no external calls
optionally create one prepared showcase run per required scenario only if explicitly requested
```

Use case:

```text
Presenter wants a predictable demo setup before a customer walkthrough.
```

---

## 3. LOCAL_DEV_GENERATED_DATA_RESET

Purpose:

```text
Local developer cleanup of generated demo runs and generated local artifacts.
```

This profile must be guarded.

Required confirmation body:

```json
{
  "confirmation": "RESET_LOCAL_DEMO_GENERATED_DATA"
}
```

Behavior:

```text
archive or mark generated demo runs as reset
archive generated scenario artifacts where safe
do not delete seed data
do not drop tables
do not delete audit logs by default
do not reset database schema
```

If hard deletion is implemented at all, it must be restricted to generated local demo artifacts and must not touch seed/reference data.

Preferred:

```text
archive/mark reset instead of delete
```

---

# Backend Service

Create service:

```text
backend/app/services/demo_readiness_service.py
```

Responsibilities:

```text
compute readiness summary
verify core services from database perspective
verify seeded data presence
verify scenario catalog
verify guided scenario readiness
verify agent investigation readiness
verify action approval readiness
verify model default disabled
build URL launcher list
build UI test guide
build showcase checklist
run safe reset profiles
prepare showcase mode
return smoke report
```

Create route:

```text
backend/app/api/routes/demo_readiness.py
```

Create schemas if useful:

```text
backend/app/schemas/demo_readiness.py
```

---

# Backend APIs

Add route prefix:

```text
/api/v1/demo-readiness
```

Expose on:

```text
Full backend 8050
Business BFF 8061 read-only only
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
GET  /api/v1/demo-readiness/summary
GET  /api/v1/demo-readiness/checks
GET  /api/v1/demo-readiness/showcase
GET  /api/v1/demo-readiness/urls
GET  /api/v1/demo-readiness/ui-test-guide
GET  /api/v1/demo-readiness/smoke-report
GET  /api/v1/demo-readiness/reset-profiles
```

Mutation endpoints:

```text
POST /api/v1/demo-readiness/reset
POST /api/v1/demo-readiness/prepare-showcase
```

Mutation endpoints must not be exposed on Business BFF.

---

## Summary response

Return:

```json
{
  "status": "READY",
  "readiness_score": 96,
  "demo_mode": "SHOWCASE_READY",
  "critical_checks_passed": 20,
  "critical_checks_failed": 0,
  "warnings": [],
  "real_model_default_enabled": false,
  "autonomous_remediation_enabled": false,
  "service_now_enabled": false,
  "recommended_next_action": "Open the guided demo scenarios page."
}
```

Statuses:

```text
READY
READY_WITH_WARNINGS
NOT_READY
UNKNOWN
```

---

## Checks

Include checks for:

```text
database reachable
warehouse seed data
synthetic users seed data
monitoring seed data
batch seed data
AI config seed data
agent knowledge seed data
demo scenario seed data
executive dashboard available
agent investigation workspace available
agent actions available
model chat available
real model disabled by default
autonomous remediation disabled
ServiceNow not configured
frontend URL list available
BFF route boundaries expected
```

---

## URL launcher list

Return grouped URLs:

```text
Executive Demo
Guided Scenarios
Demo Readiness
Demo Control
Operations Console
Simulation Lab
Agentic Workspace
Agent Investigations
Agent Actions
AI Config Real Model
Observability Alerts
Batch Runs
AMS Tickets
Business View
```

Each URL item should include:

```text
label
experience
url
description
recommended_order
```

---

## UI Test Guide

Return a structured UI test guide.

Sections:

```text
Executive storyboard test
Guided scenario test
Operations issue test
Agent investigation test
Model-assisted chat fallback test
Approval-gated action test
Governance/readiness test
Business read-only test
```

Each test step should include:

```text
step_number
page_url
what_to_click
expected_result
what_to_capture
pass_fail_hint
```

This should allow a human tester to validate the platform from the browser.

---

## Smoke Report

Return a compact report:

```text
stack URLs
critical API readiness
seed counts
scenario counts
investigation counts
action counts
model default status
BFF exposure status
known warnings
```

Do not execute model calls.

Do not approve or execute actions.

Do not start scenarios unless explicitly requested by prepare-showcase.

---

# Showcase Preparation

Implement:

```text
POST /api/v1/demo-readiness/prepare-showcase
```

Request body:

```json
{
  "profile": "SHOWCASE_RESET",
  "create_prepared_runs": true,
  "created_by_role": "DEMO_PRESENTER"
}
```

Behavior:

```text
perform SHOWCASE_RESET
verify seeds
ensure scenarios are ready
optionally create prepared scenario runs
return suggested demo flow
return URLs to open
return readiness score
```

Must not:

```text
call real model
approve actions automatically
execute approved actions automatically
enable autonomous remediation
send customer communications
call external systems
```

---

# Scripts

Add scripts:

```text
scripts/prepare-showcase.sh
scripts/reset-demo-readiness.sh
scripts/demo-smoke-report.sh
scripts/open-demo-urls.sh
```

Rules:

```text
scripts may call local backend APIs
scripts must not drop database
scripts must not require external tools beyond curl/jq where already used
scripts must not call real model
scripts must not expose API keys
```

`open-demo-urls.sh` may simply print the URLs if browser opening is unreliable on the VM.

---

# Frontend UI

Create service:

```text
frontend/src/services/demoReadinessApi.ts
```

Create page:

```text
frontend/src/pages/DemoReadinessPages.tsx
```

Routes:

```text
/demo-readiness
/demo-readiness/showcase
/demo-readiness/ui-test-guide
/demo-readiness/smoke-report
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

## Demo Readiness Page

Show:

```text
readiness score
status
critical checks
warnings
real model default status
autonomous remediation status
ServiceNow status
recommended next action
```

---

## Showcase Page

Show:

```text
prepare showcase button
reset profile selector
safe reset explanation
prepared scenario runs
recommended URL launcher list
suggested presenter flow
```

On Business UI:

```text
show read-only status
hide mutation buttons
```

---

## UI Test Guide Page

Show browser-driven test cases:

```text
test section
page to open
what to click
expected result
capture note
pass/fail marker if simple local state only
```

No browser automation is required.

---

## Smoke Report Page

Show:

```text
stack URLs
seed readiness
scenario readiness
agent readiness
actions readiness
model readiness
BFF exposure summary
known warnings
```

---

# Demo Control Integration

Update demo control readiness/components to include:

```text
Demo Readiness
Showcase Mode
Reset Profiles
UI Test Guide
Smoke Report
```

Readiness should check:

```text
http://localhost:8050/api/v1/demo-readiness/summary
```

Do not call reset or prepare-showcase during readiness checks.

---

# Tests

Add backend tests for:

```text
demo readiness summary endpoint
checks endpoint
URL launcher endpoint
UI test guide endpoint
smoke report endpoint
reset profiles endpoint
soft reset preserves audit history
showcase reset verifies seeds and keeps real model disabled
prepare-showcase creates prepared runs only when requested
prepare-showcase does not call model
prepare-showcase does not approve or execute actions
local dev reset requires confirmation
Business BFF exposes read-only readiness endpoints
Business BFF blocks reset and prepare-showcase
Observability BFF does not expose readiness routes
demo control includes readiness components
no OpenAI API key required
no external LLM call required
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

## Readiness summary

```bash
curl -sS http://localhost:8050/api/v1/demo-readiness/summary | jq .
curl -sS http://localhost:8050/api/v1/demo-readiness/checks | jq .
curl -sS http://localhost:8050/api/v1/demo-readiness/urls | jq .
curl -sS http://localhost:8050/api/v1/demo-readiness/ui-test-guide | jq .
curl -sS http://localhost:8050/api/v1/demo-readiness/smoke-report | jq .
curl -sS http://localhost:8050/api/v1/demo-readiness/reset-profiles | jq .
```

Expected:

```text
readiness status returned
checks returned
URL launcher returned
UI test guide returned
smoke report returned
reset profiles returned
real model default off
autonomous remediation disabled
```

---

## Showcase preparation

```bash
curl -sS -X POST http://localhost:8050/api/v1/demo-readiness/prepare-showcase \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "SHOWCASE_RESET",
    "create_prepared_runs": true,
    "created_by_role": "DEMO_PRESENTER"
  }' | jq .
```

Expected:

```text
showcase prepared
prepared runs returned if requested
real model remains disabled
no action approvals executed
no external calls
```

---

## Soft reset

```bash
curl -sS -X POST http://localhost:8050/api/v1/demo-readiness/reset \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "SOFT_RESET",
    "reset_reason": "Manual validation reset"
  }' | jq .
```

Expected:

```text
active demo runs reset
audit retained
seed data retained
```

---

## Local dev reset confirmation guard

```bash
curl -i -sS -X POST http://localhost:8050/api/v1/demo-readiness/reset \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "LOCAL_DEV_GENERATED_DATA_RESET",
    "reset_reason": "Should be blocked without confirmation"
  }' | head
```

Expected:

```text
blocked because confirmation is missing
```

Then:

```bash
curl -sS -X POST http://localhost:8050/api/v1/demo-readiness/reset \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "LOCAL_DEV_GENERATED_DATA_RESET",
    "confirmation": "RESET_LOCAL_DEMO_GENERATED_DATA",
    "reset_reason": "Manual local demo cleanup validation"
  }' | jq .
```

Expected:

```text
generated local demo data archived/reset safely
no seed data deleted
no schema dropped
```

---

# BFF Validation

```bash
curl -sS http://localhost:8061/api/v1/demo-readiness/summary | jq .
curl -sS http://localhost:8062/api/v1/demo-readiness/summary | jq .
curl -sS http://localhost:8063/api/v1/demo-readiness/summary | jq .
curl -sS http://localhost:8065/api/v1/demo-readiness/summary | jq .

curl -i -sS -X POST http://localhost:8061/api/v1/demo-readiness/prepare-showcase \
  -H "Content-Type: application/json" \
  -d '{}' | head

curl -i -sS http://localhost:8064/api/v1/demo-readiness/summary | head
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

./scripts/demo-smoke-report.sh
./scripts/prepare-showcase.sh
./scripts/reset-demo-readiness.sh --profile SOFT_RESET
./scripts/open-demo-urls.sh
```

Expected:

```text
scripts call local backend APIs only
no real model call
no database drop
no external service call
URL script prints or opens demo URLs
```

---

# Manual UI Validation

Open:

```text
http://localhost:4001/demo-readiness
http://localhost:4001/demo-readiness/showcase
http://localhost:4001/demo-readiness/ui-test-guide
http://localhost:4001/demo-readiness/smoke-report
```

Also open:

```text
http://localhost:4011/demo-readiness
http://localhost:4012/demo-readiness
http://localhost:4013/demo-readiness
http://localhost:4015/demo-readiness
```

Validate:

```text
readiness score visible
critical checks visible
real model default off visible
autonomous remediation disabled visible
ServiceNow disabled visible
URL launcher visible
UI test guide visible
smoke report visible
showcase preparation works in allowed experiences
Business UI is read-only
reset buttons hidden or disabled in Business UI
```

Run a browser-only demo path using the UI guide:

```text
Executive Demo
Guided Scenario
Operations Ticket/Exception
Investigate with Agent
Investigation Workspace
Model Chat Fallback
Approval-Gated Safe Action
Audit/Timeline
Demo Readiness Smoke Report
```

---

# Documentation Updates

Update `README.md` with:

```text
demo readiness overview
reset profile explanations
showcase mode instructions
UI test guide usage
script commands
safe reset boundaries
```

Update `ARCHITECTURE.md` with:

```text
demo readiness architecture
safe reset design
showcase preparation design
UI testing guide design
relationship to scenario orchestration and demo control
```

Document clearly:

```text
Prompt 27 adds demo readiness and showcase hardening only.
It does not enable real model calls by default.
It does not add autonomous remediation.
It does not execute shell commands from APIs.
It does not drop the database.
It does not integrate with ServiceNow.
```

---

# Definition of Done

Prompt 27 is complete only when:

- demo readiness service exists
- demo readiness API exists
- readiness summary works
- checks endpoint works
- URL launcher endpoint works
- UI test guide endpoint works
- smoke report endpoint works
- reset profiles endpoint works
- SOFT_RESET works
- SHOWCASE_RESET works
- LOCAL_DEV_GENERATED_DATA_RESET requires confirmation
- prepare-showcase works
- prepare-showcase does not call model
- prepare-showcase does not approve or execute actions
- scripts exist and work
- frontend readiness pages exist
- Business UI is read-only
- allowed experiences can prepare showcase
- demo control includes readiness components
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
- Prompt 27 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. Demo readiness behavior
5. Reset profile behavior
6. Showcase preparation behavior
7. UI test guide behavior
8. Smoke report behavior
9. URL launcher behavior
10. Scripts added
11. Backend APIs added
12. BFF exposure summary
13. Frontend routes/pages added
14. Demo control integration summary
15. Backend test results
16. Frontend build results
17. Demo stack validation results
18. Manual API validation results
19. Script validation results
20. Manual UI validation results
21. Confirmation deterministic/mock remains default
22. Confirmation no real model call occurs by default
23. Confirmation no autonomous remediation was introduced
24. Confirmation no shell command/arbitrary SQL/external system execution was introduced
25. Confirmation no ServiceNow/authentication was introduced
26. TODOs or limitations
27. Recommended Git commit message

Recommended commit message:

```text
feat: add demo readiness showcase mode
```

Do not proceed beyond this prompt.

## Implementation record

Implemented in the EOS workspace. The implementation adds the local demo
readiness service and API, guarded reset profiles, showcase preparation, URL
launcher, browser UI test guide, smoke report, four local presenter scripts,
experience-aware BFF exposure, and readiness pages at `/demo-readiness`,
`/demo-readiness/showcase`, `/demo-readiness/ui-test-guide`, and
`/demo-readiness/smoke-report`. No migration was required because reset state
uses the existing demo scenario run/event model. Verification covers readiness
reporting, seed/catalog preparation, reset confirmation, prepared-run safety,
BFF boundaries, and demo-control capabilities. Real model calls remain disabled
by default; no autonomous remediation, shell/SQL execution, external system,
ServiceNow, authentication, or schema reset was added.
