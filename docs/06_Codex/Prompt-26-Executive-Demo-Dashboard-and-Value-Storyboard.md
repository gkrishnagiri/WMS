# Prompt 26 – Executive Demo Dashboard and Value Storyboard

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

Your task now is to implement:

```text
Executive Demo Dashboard and Value Storyboard
```

---

## Business Goal

The platform now has a strong technical demo flow, but executives and senior stakeholders need a business-facing view that explains:

```text
What problem are we solving?
How does AI-native AMS change the operating model?
What value is demonstrated?
How do guided scenarios map to measurable outcomes?
How does governance reduce risk?
How does this support future commercial models?
```

Prompt 26 should create an executive dashboard that summarizes the platform value across:

```text
scenario outcomes
issue-to-investigation flow
evidence gathered
knowledge reused
model-assisted capability
approval-gated actions
auditability
human effort reduction potential
operating model maturity
AI-native AMS commercial narrative
```

This is not a production ROI calculator. It is a **demo value storyboard** using local EOS demo data and clearly labeled assumptions.

---

## Executive Demo Story

The executive dashboard should support a storyline like:

```text
Traditional AMS support is reactive and manual
        ->
Issues are detected across tickets, alerts, batches, and user reports
        ->
EOS creates contextual investigations
        ->
Agent gathers evidence and knowledge
        ->
Model-assisted chat can be enabled under governance
        ->
Safe actions require human approval
        ->
Audit trail is retained
        ->
The operating model shifts from ticket handling to outcome-oriented AI-native operations
```

The dashboard should help a presenter explain:

```text
speed
quality
reuse
governance
auditability
commercial impact
```

---

## Critical Scope

Prompt 26 implements:

```text
executive dashboard
value storyboard
scenario outcome summary
demo KPI cards
AI-native operating model narrative
commercial value view
governance and risk-control view
guided demo deep links
read-only aggregate APIs
```

Prompt 26 must not implement:

```text
real financial billing
actual commercial contract engine
autonomous remediation
real model calls by default
shell command execution
arbitrary SQL execution
external ServiceNow integration
customer communications
production analytics claims without labeling as demo/estimated
authentication / authorization
```

All metrics must be based on local EOS demo data or clearly labeled demo assumptions.

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

Do not break existing Prompt 13–25 behavior.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve deterministic/mock behavior as the default.

You must not enable real model calls by default.

You must not require an OpenAI API key.

You must not call an external LLM in tests.

You must not execute shell commands.

You must not execute arbitrary SQL.

You must not execute arbitrary user-provided code.

You must not introduce autonomous remediation.

You must not integrate with ServiceNow.

You must not send customer communications externally.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

The dashboard must be read-only.

The dashboard must label all non-production assumptions clearly as:

```text
Demo estimate
Illustrative assumption
Scenario-derived metric
```

Do not imply these are real customer production savings.

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

Implement an executive value dashboard and storyboard.

The platform should support:

```text
executive summary cards
scenario outcome dashboard
AI-native AMS value chain
traditional vs AI-native comparison
governance and safety controls summary
commercial model implications
demo KPI trend/summary
storyboard sections
deep links to guided scenarios and investigations
read-only APIs
presenter-friendly UI
```

---

# Executive Dashboard Routes

Create frontend routes:

```text
/executive-demo
/executive-demo/storyboard
/executive-demo/value
/executive-demo/governance
```

At minimum, `/executive-demo` may contain all sections if separate routes are too much.

Visible in:

```text
Full UI                    4001
Business UI                4011
Operations UI              4012
Agentic UI                 4015
```

Optional in:

```text
Simulation UI              4013
```

Not required in:

```text
Observability UI           4014
```

Business UI should be read-only and leadership-oriented.

---

# Backend API

Add route prefix:

```text
/api/v1/executive-demo
```

Expose on:

```text
Full backend 8050
Business BFF 8061
Operations BFF 8062
Agentic BFF 8065
```

Optional read-only exposure on:

```text
Simulation BFF 8063
```

Do not expose on:

```text
Observability BFF 8064
```

unless there is a clear reason.

---

## Required Endpoints

```text
GET /api/v1/executive-demo/summary
GET /api/v1/executive-demo/value-metrics
GET /api/v1/executive-demo/storyboard
GET /api/v1/executive-demo/scenario-outcomes
GET /api/v1/executive-demo/governance
GET /api/v1/executive-demo/operating-model
GET /api/v1/executive-demo/commercial-model
GET /api/v1/executive-demo/deep-links
```

All endpoints must be read-only.

No endpoint should trigger scenario runs, model calls, approvals, execution, or data mutation.

---

# Backend Service

Create service:

```text
backend/app/services/executive_demo_service.py
```

Responsibilities:

```text
aggregate demo scenario data
aggregate agent investigation data
aggregate action approval/audit data
aggregate model readiness/usage metadata
derive demo value metrics
build storyboard sections
build governance narrative
build operating model narrative
build commercial model narrative
return deep links
```

Create route:

```text
backend/app/api/routes/executive_demo.py
```

Create schemas if useful:

```text
backend/app/schemas/executive_demo.py
```

---

# Data Model

Prefer dynamic computation from existing tables.

Add migration only if needed.

Optional migration:

```text
0018_executive_demo_value_storyboard
```

Optional tables:

```text
executive_value_assumptions
executive_storyboard_cards
```

Only add these if useful for configurable assumptions.

If added, seed deterministic values.

Suggested assumption fields:

```text
assumption_code
title
description
value_type
numeric_value
unit
label
is_demo_assumption
sort_order
```

Example assumptions:

```text
manual_triage_minutes_baseline = 30
manual_evidence_collection_minutes_baseline = 45
manual_work_note_draft_minutes_baseline = 15
manual_customer_update_minutes_baseline = 10
```

Important:

These are illustrative assumptions only.

They must be labeled clearly in API and UI.

---

# Value Metrics

Compute value metrics from existing demo data.

Suggested metric groups:

## 1. Scenario execution

```text
total_scenarios
enabled_scenarios
scenario_runs
completed_runs
active_runs
reset_runs
scenario_artifacts_created
```

## 2. Issue-to-investigation

```text
issues_induced
ams_tickets_linked
alerts_linked
batch_runs_linked
user_reports_linked
agent_investigations_created
investigation_handoffs
```

## 3. Evidence and knowledge

```text
evidence_items_collected
knowledge_items_retrieved
known_errors_matched
timeline_events_created
retrieval_queries_recorded
```

## 4. Model-assisted readiness

```text
real_model_feature_enabled
api_key_present
provider_enabled
model_enabled
real_model_calls_default_enabled=false
model_invocations_recorded
fallback_responses_recorded
```

Do not call the model to compute these.

## 5. Approval-gated actions

```text
action_proposals_created
actions_approved
actions_rejected
actions_executed
actions_succeeded
duplicate_executions_prevented
```

## 6. Governance and audit

```text
invocation_audit_records
guardrail_events
action_audit_events
scenario_timeline_events
cases_with_actions_executed_zero
```

## 7. Demo-estimated effort impact

Based on assumptions, calculate illustrative values:

```text
estimated_manual_effort_baseline_minutes
estimated_agent_assisted_effort_minutes
estimated_effort_avoided_minutes
estimated_effort_avoided_percent
```

Label:

```text
Demo estimate based on configurable assumptions, not production measurement.
```

---

# Suggested Demo Effort Formula

Use simple transparent formulas.

Example:

```text
manual_baseline_minutes =
  investigation_count * manual_triage_minutes_baseline
  + investigation_count * manual_evidence_collection_minutes_baseline
  + work_note_draft_count * manual_work_note_draft_minutes_baseline
  + customer_update_draft_count * manual_customer_update_minutes_baseline
```

```text
agent_assisted_minutes =
  investigation_count * assisted_triage_minutes_assumption
  + investigation_count * assisted_review_minutes_assumption
  + approval_count * approval_review_minutes_assumption
```

```text
effort_avoided_minutes =
  max(manual_baseline_minutes - agent_assisted_minutes, 0)
```

Keep the assumptions visible.

Do not present the estimate as actual measured productivity unless measured timestamps are available.

---

# Storyboard Sections

Build a deterministic executive storyboard.

Required sections:

## 1. The Traditional AMS Challenge

Explain:

```text
ticket-centric operations
manual triage
manual evidence gathering
knowledge fragmentation
slow handoffs
limited auditability of AI assistance
```

## 2. The AI-Native AMS Operating Model

Explain:

```text
signal-to-investigation flow
contextual agent handoff
evidence timeline
knowledge retrieval
model-assisted Stage 1 chat
approval-gated Stage 2 actions
audit trail
```

## 3. Scenario-Based Proof Points

For each Prompt 25 scenario, summarize:

```text
scenario name
business problem
source signals
agent capabilities demonstrated
generated artifacts
current run status
deep link
```

## 4. Governance by Design

Explain:

```text
mock/deterministic default
real model disabled by default
Stage 1 read-only model chat
approval-gated actions
safe local action catalog
no autonomous remediation
no ServiceNow/customer-send integration
audit records
guardrails
```

## 5. Commercial Model Implications

Explain how this supports enterprise AMS commercial model shifts:

```text
from ticket-volume pricing to outcome/value pricing
from capacity-only pricing to platform-plus-services pricing
from manual effort billing to automation governance and agent operations
from SLA-only metrics to AI-assisted resolution and auditability metrics
```

This should be narrative only. Do not implement billing.

## 6. Roadmap to Production

Explain future phases:

```text
production integrations
ServiceNow connector
enterprise identity and authorization
real observability integrations
real model activation
approval workflow hardening
controlled autonomous remediation sandbox
commercial governance metrics
```

---

# Governance Dashboard

Create a governance summary showing:

```text
real model default off
OpenAI key not required
provider/model readiness
guardrail events
safety policy status
Stage 1 read-only mode
Stage 2 approval-gated mode
actions executed only after approval
no autonomous remediation
no shell/SQL/external execution
audit coverage
```

This should be visible and reassuring to risk/compliance stakeholders.

---

# Commercial Model View

Create a business/commercial view that maps:

```text
Traditional AMS model
AI-native alternative
Value lever
Metric used in demo
Risk allocation impact
```

Suggested rows:

```text
Ticket-volume pricing -> Outcome-based incident avoidance / faster restoration
Fixed capacity -> Platform + governed agent operations
Application-based pricing -> Digital operations pod / product-aligned support
SLA penalty model -> SLA + experience + automation assurance
Minor enhancement bucket -> Agent-maintained backlog triage and safe-change workflow
Manual L1/L2 support -> Human-supervised agentic operations
```

Do not produce legal contract clauses here unless already documented elsewhere.

Keep this as a concise executive view.

---

# Deep Links

The executive dashboard should link to:

```text
/demo-scenarios
/demo-scenarios/runs
/agent-investigations
/agent-actions/proposals if available
/agent-chat/sessions
/ai-config/real-model
/demo-control
```

Link availability should respect experience routing.

---

# Frontend UI

Create service:

```text
frontend/src/services/executiveDemoApi.ts
```

Create pages:

```text
frontend/src/pages/ExecutiveDemoPages.tsx
```

Update navigation:

```text
Full UI
Business UI
Operations UI
Agentic UI
```

Suggested page layout:

```text
Hero executive summary
Demo KPI cards
Value chain graphic or stepper
Scenario outcomes
Governance summary
Approval-gated actions summary
Model readiness summary
Commercial model implications
Storyboard sections
Deep links
Assumption disclaimer
```

Do not use a heavy charting dependency unless already present.

Use existing UI libraries/components.

---

## KPI Card Examples

Cards should include:

```text
Guided Scenarios
Investigations Created
Evidence Items Collected
Knowledge Items Reused
Safe Actions Proposed
Approved Local Actions
Audit Records
Estimated Effort Avoided
Real Model Default
Autonomous Remediation
```

Example display values:

```text
Real Model Default: Off
Autonomous Remediation: Disabled
Actions Executed: Approval-gated only
```

---

## Visual Value Chain

Add a simple visual stepper:

```text
Signal
    ->
Contextual Handoff
    ->
Evidence + Knowledge
    ->
Stage 1 Guidance
    ->
Approval-Gated Action
    ->
Audit + Learning
```

Each step should link to relevant modules where possible.

---

## Assumption Disclaimer

Display prominently:

```text
Value estimates are demo estimates based on local EOS scenario data and configurable assumptions. They are not production measurements.
```

---

# Demo Control Integration

Update demo control readiness/components to include:

```text
Executive Demo Dashboard
Value Metrics
Executive Storyboard
Governance Dashboard
Commercial Model View
```

Readiness should check:

```text
http://localhost:8050/api/v1/executive-demo/summary
```

Do not trigger scenario runs or model calls.

---

# Tests

Add backend tests for:

```text
executive summary endpoint
value metrics endpoint
storyboard endpoint
scenario outcomes endpoint
governance endpoint
operating model endpoint
commercial model endpoint
deep links endpoint
metrics are read-only
metrics do not trigger scenario runs
metrics do not trigger model calls
demo assumptions are labeled
governance response confirms real model default off
commercial model response includes traditional-to-AI-native mapping
BFF exposure rules
Business BFF exposes read-only executive demo
Observability BFF does not expose executive demo unless intentionally exposed
demo control includes executive demo readiness
no OpenAI API key required
no external LLM call required
no shell/SQL/external system execution
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

## Executive summary

```bash
curl -sS http://localhost:8050/api/v1/executive-demo/summary | jq .
```

## Value metrics

```bash
curl -sS http://localhost:8050/api/v1/executive-demo/value-metrics | jq .
```

Expected:

```text
scenario metrics
investigation metrics
evidence/knowledge metrics
action metrics
governance metrics
demo-estimated effort impact
assumption disclaimer
```

## Storyboard

```bash
curl -sS http://localhost:8050/api/v1/executive-demo/storyboard | jq .
```

Expected sections:

```text
Traditional AMS Challenge
AI-Native AMS Operating Model
Scenario-Based Proof Points
Governance by Design
Commercial Model Implications
Roadmap to Production
```

## Governance

```bash
curl -sS http://localhost:8050/api/v1/executive-demo/governance | jq .
```

Expected:

```text
real model default off
Stage 1 read-only
Stage 2 approval-gated
no autonomous remediation
no shell/SQL/external execution
audit coverage
```

## Commercial model

```bash
curl -sS http://localhost:8050/api/v1/executive-demo/commercial-model | jq .
```

Expected:

```text
traditional model
AI-native alternative
value lever
demo metric
risk allocation impact
```

## Deep links

```bash
curl -sS http://localhost:8050/api/v1/executive-demo/deep-links | jq .
```

---

# BFF Validation

```bash
curl -sS http://localhost:8061/api/v1/executive-demo/summary | jq .
curl -sS http://localhost:8062/api/v1/executive-demo/summary | jq .
curl -sS http://localhost:8065/api/v1/executive-demo/summary | jq .

curl -i -sS http://localhost:8064/api/v1/executive-demo/summary | head
```

Expected:

```text
Business BFF: 200 read-only
Operations BFF: 200
Agentic BFF: 200
Observability BFF: 404 unless intentionally exposed
```

If Simulation BFF is exposed:

```bash
curl -sS http://localhost:8063/api/v1/executive-demo/summary | jq .
```

Expected:

```text
Simulation BFF: 200 read-only if implemented
```

---

# Manual UI Validation

Open:

```text
http://localhost:4001/executive-demo
http://localhost:4011/executive-demo
http://localhost:4012/executive-demo
http://localhost:4015/executive-demo
```

Validate:

```text
executive summary loads
KPI cards visible
scenario outcomes visible
value chain visible
governance summary visible
commercial model view visible
storyboard sections visible
deep links work
assumption disclaimer visible
```

Confirm:

```text
Business UI is read-only
No mutation controls are present
No real-model test button is triggered from this page
No action approval/execution happens from this page unless only deep-linked to existing module
No API key input exists
No remediation controls exist
```

---

# Documentation Updates

Update `README.md` with:

```text
Executive Demo Dashboard overview
dashboard URLs
business value metrics
demo-estimate disclaimer
manual validation commands
safe boundaries
```

Update `ARCHITECTURE.md` with:

```text
executive demo architecture
value metric aggregation
scenario-to-value chain
governance dashboard design
commercial model view
relationship to guided scenarios, agent investigations, model chat, and approval-gated actions
```

Document clearly:

```text
Prompt 26 adds a read-only executive value storyboard.
It does not enable real model calls by default.
It does not execute actions.
It does not introduce autonomous remediation.
It does not integrate with ServiceNow.
It does not implement billing or production ROI.
```

---

# Definition of Done

Prompt 26 is complete only when:

- executive demo service exists
- executive demo API routes exist
- summary endpoint works
- value metrics endpoint works
- storyboard endpoint works
- scenario outcomes endpoint works
- governance endpoint works
- operating model endpoint works
- commercial model endpoint works
- deep links endpoint works
- dashboard is read-only
- value assumptions are clearly labeled
- business value estimate is clearly labeled as demo/illustrative
- dashboard does not trigger scenario runs
- dashboard does not trigger model calls
- dashboard does not trigger actions
- Business UI exposes read-only executive dashboard
- Operations UI exposes dashboard
- Agentic UI exposes dashboard
- Full UI exposes dashboard
- frontend executive page exists
- demo control includes executive demo readiness
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
- Prompt 26 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. Executive dashboard behavior
5. Value metrics behavior
6. Demo-estimate assumptions
7. Storyboard sections
8. Governance dashboard behavior
9. Commercial model view behavior
10. Deep links summary
11. Backend APIs added
12. BFF exposure summary
13. Frontend routes/pages added
14. Demo control integration summary
15. Backend test results
16. Frontend build results
17. Demo stack validation results
18. Manual API validation results
19. Manual UI validation results
20. Confirmation dashboard is read-only
21. Confirmation deterministic/mock remains default
22. Confirmation no real model call occurs by default
23. Confirmation no autonomous remediation was introduced
24. Confirmation no shell command/arbitrary SQL/external system execution was introduced
25. Confirmation no ServiceNow/authentication was introduced
26. TODOs or limitations
27. Recommended Git commit message

Recommended commit message:

```text
feat: add executive demo value storyboard
```

Do not proceed beyond this prompt.

## Implementation record

Implemented the read-only executive demo aggregation and storyboard layer.
It provides summary, value metrics, scenario outcomes, governance, operating
model, commercial model, storyboard, and deep-link APIs over local EOS data.
The UI is available at `/executive-demo` and the three focused routes under
that path in Full, Business, Operations, and Agentic experiences.

Effort numbers are explicitly labeled demo estimates with visible illustrative
assumptions. No endpoint mutates data, starts a scenario, calls a model,
approves/executes an action, sends communications, posts to ServiceNow, or
performs autonomous remediation.
