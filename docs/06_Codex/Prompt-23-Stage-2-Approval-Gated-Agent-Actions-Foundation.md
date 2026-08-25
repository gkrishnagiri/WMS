# Prompt 23 – Stage 2 Approval-Gated Agent Actions Foundation

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

Your task now is to implement:

```text
Stage 2 Approval-Gated Agent Actions Foundation
```

---

## Business Goal

The platform currently supports Stage 1 read-only agent guidance:

```text
Agent gathers evidence
Agent retrieves knowledge
Agent explains likely cause
Agent recommends next steps
Human performs all actions
```

Prompt 23 should introduce the foundation for Stage 2:

```text
Agent proposes safe actions
Human reviews each proposed action
Human approves or rejects each action
System executes only approved, narrowly scoped safe/demo actions
Every step is audited
No autonomous remediation is enabled
```

This is the demo story:

```text
Engineer investigates an issue
        ->
Agent proposes resolution steps
        ->
Engineer approves one safe step
        ->
System executes only that approved step
        ->
Audit trail records who approved, what executed, and result
        ->
Agent updates the investigation workspace
```

---

## Critical Scope Clarification

Prompt 23 implements:

```text
approval-gated action proposals
approval workflow
safe action catalog
narrow demo-safe execution handlers
audit trail
workspace integration
```

Prompt 23 must **not** implement:

```text
autonomous remediation
unapproved action execution
shell command execution
arbitrary SQL execution
external ServiceNow updates
real customer communication sends
real LLM-required execution
```

Real model usage remains optional and disabled by default.

The action proposal logic can remain deterministic.

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

Do not break existing Prompt 13–22 behavior.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve deterministic/mock behavior as the default.

You must not enable real model calls by default.

You must not require an OpenAI API key.

You must not call an external LLM in tests.

You must not introduce autonomous remediation.

You must not execute shell commands.

You must not execute arbitrary SQL.

You must not execute arbitrary user-provided code.

You must not integrate with ServiceNow.

You must not send customer communications externally.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

All actions must be from a predefined safe catalog.

Every executable action must require explicit approval first.

Actions must be idempotent or safely guarded against duplicate execution.

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

Implement Stage 2 approval-gated action foundation.

The platform should support:

```text
safe action catalog
action proposal generation
action approval
action rejection
approved action execution
execution audit
workspace action panel
timeline updates
draft-only actions
ticket/work-note local actions
case status actions
simulation-safe operational actions
```

---

# Safe Action Catalog

Create or extend a safe action catalog.

Suggested action types:

```text
CREATE_AMS_WORK_NOTE_DRAFT
ADD_INTERNAL_CASE_NOTE
UPDATE_AGENT_CASE_STATUS
MARK_AGENT_PROPOSAL_REVIEWED
CREATE_NEXT_STEPS_CHECKLIST
LINK_EVIDENCE_TO_CASE
CREATE_FOLLOW_UP_TASK_DRAFT
CREATE_CUSTOMER_UPDATE_DRAFT
ACKNOWLEDGE_OBSERVABILITY_ALERT
ACKNOWLEDGE_MONITORING_ALERT
ACKNOWLEDGE_OPERATIONS_EXCEPTION
```

Careful distinction:

## Allowed in Prompt 23

```text
create local draft
create internal note
update agent case status
acknowledge local EOS demo alert/exception
link local evidence
mark proposal reviewed
```

## Not allowed in Prompt 23

```text
execute shell command
restart service
change inventory
modify warehouse order
ship order
delete data
send email
post to ServiceNow
call external API
auto-resolve AMS ticket
auto-resolve production alert
```

---

# Data Model

Add migration if needed:

```text
0016_stage2_approval_gated_actions
```

Extend or create tables as needed.

Existing table:

```text
agent_action_proposals
```

may already exist from Prompt 18.

Add fields if missing:

```text
approved_by_role
approved_at
rejected_by_role
rejected_at
approval_comment
execution_started_at
execution_completed_at
execution_error
execution_result_json
execution_mode
safe_action_code
idempotency_key
```

Create action execution table if useful:

```text
agent_action_executions
```

Suggested fields:

```text
id
execution_id
proposal_id
case_id
run_id
safe_action_code
status
requested_by_role
approved_by_role
started_at
completed_at
result_summary
result_json
error_message
idempotency_key
created_at
updated_at
```

Statuses:

```text
PENDING_APPROVAL
APPROVED
REJECTED
EXECUTION_PENDING
EXECUTING
SUCCEEDED
FAILED
SKIPPED_DUPLICATE
DISABLED
```

Execution modes:

```text
STAGE_2_APPROVAL_GATED
STAGE_1_DISABLED
DRY_RUN
```

---

# Action Proposal Behavior

Update deterministic orchestrator and/or investigation service to propose safe actions based on case context.

Examples:

## AMS ticket case

Propose:

```text
CREATE_AMS_WORK_NOTE_DRAFT
ADD_INTERNAL_CASE_NOTE
CREATE_NEXT_STEPS_CHECKLIST
```

## Observability alert case

Propose:

```text
ACKNOWLEDGE_OBSERVABILITY_ALERT
CREATE_AMS_WORK_NOTE_DRAFT
LINK_EVIDENCE_TO_CASE
```

## Batch failure case

Propose:

```text
CREATE_NEXT_STEPS_CHECKLIST
CREATE_AMS_WORK_NOTE_DRAFT
ADD_INTERNAL_CASE_NOTE
```

## User report case

Propose:

```text
CREATE_CUSTOMER_UPDATE_DRAFT
CREATE_AMS_WORK_NOTE_DRAFT
ADD_INTERNAL_CASE_NOTE
```

Important:

Proposals are safe suggestions.

No proposal should execute automatically.

---

# Approval Workflow

Add service:

```text
backend/app/services/agent_action_service.py
```

Responsibilities:

```text
list safe actions
list proposals
get proposal
approve proposal
reject proposal
execute approved proposal
dry-run proposal
record execution result
prevent duplicate execution
update timeline/evidence where appropriate
```

Rules:

```text
Only APPROVED proposals can execute.
Rejected proposals cannot execute.
Already executed proposals cannot execute again unless explicitly idempotent and safe.
Execution requires explicit endpoint call.
Approval endpoint must not execute by default unless request says execute_after_approval=true.
```

---

# Backend APIs

Add route prefix:

```text
/api/v1/agent-actions
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

unless specifically justified.

## Required endpoints

```text
GET  /api/v1/agent-actions/summary
GET  /api/v1/agent-actions/catalog
GET  /api/v1/agent-actions/proposals
GET  /api/v1/agent-actions/proposals/{proposal_id}
POST /api/v1/agent-actions/proposals/{proposal_id}/approve
POST /api/v1/agent-actions/proposals/{proposal_id}/reject
POST /api/v1/agent-actions/proposals/{proposal_id}/dry-run
POST /api/v1/agent-actions/proposals/{proposal_id}/execute
GET  /api/v1/agent-actions/executions
GET  /api/v1/agent-actions/executions/{execution_id}
```

Request body for approval:

```json
{
  "approved_by_role": "SERVICE_ENGINEER",
  "approval_comment": "Approved after reviewing evidence.",
  "execute_after_approval": false
}
```

Request body for reject:

```json
{
  "rejected_by_role": "SERVICE_ENGINEER",
  "rejection_comment": "Not appropriate for this case."
}
```

Execution request:

```json
{
  "requested_by_role": "SERVICE_ENGINEER",
  "execution_comment": "Execute approved draft generation step."
}
```

---

# Execution Handlers

Implement only safe handlers.

## CREATE_AMS_WORK_NOTE_DRAFT

Creates or returns deterministic work-note draft for the case.

It should not post externally.

## CREATE_CUSTOMER_UPDATE_DRAFT

Creates or returns deterministic customer-update draft.

It should not send externally.

## CREATE_NEXT_STEPS_CHECKLIST

Creates or returns checklist.

## ADD_INTERNAL_CASE_NOTE

Adds an agent/system note to the local case/chat/session.

## UPDATE_AGENT_CASE_STATUS

Updates local agent case status only.

Allowed target statuses:

```text
IN_PROGRESS
WAITING_FOR_USER
GUIDANCE_PROVIDED
CLOSED
```

## ACKNOWLEDGE_OBSERVABILITY_ALERT

May acknowledge a local EOS observability alert event if linked.

Do not resolve it.

## ACKNOWLEDGE_MONITORING_ALERT

May acknowledge a local EOS monitoring alert if linked.

Do not resolve it.

## ACKNOWLEDGE_OPERATIONS_EXCEPTION

May acknowledge a local EOS operations exception if linked.

Do not resolve it.

If a handler cannot safely perform the action, return FAILED with a clear message.

---

# Dry Run

Dry run should return:

```text
what would happen
whether proposal is executable
required approval state
target object
expected local changes
safety notes
```

Dry run must not mutate data.

---

# Investigation Workspace Integration

Update Prompt 22 workspace to show:

```text
safe action catalog
action proposals
approval status
execution status
execution history
approve button
reject button
dry-run button
execute approved button
```

Buttons must be clearly labeled:

```text
Approve
Reject
Dry Run
Execute Approved Action
```

Add safety warning:

```text
Stage 2 approval-gated mode. Only predefined safe local actions can execute. No shell commands, external sends, ServiceNow updates, or autonomous remediation are enabled.
```

---

# Agent Chat Integration

When an action is approved/rejected/executed, append a system message to the related agent chat session if available:

```text
Action proposal approved: ...
Action proposal rejected: ...
Approved action executed: ...
```

Do not let chat text execute actions directly.

---

# Timeline Integration

Update investigation timeline to include:

```text
ACTION_PROPOSED
ACTION_APPROVED
ACTION_REJECTED
ACTION_DRY_RUN
ACTION_EXECUTION_STARTED
ACTION_EXECUTION_SUCCEEDED
ACTION_EXECUTION_FAILED
```

---

# Demo Control Integration

Update demo control components/readiness to include:

```text
Stage 2 Action Catalog
Approval-Gated Actions
Action Execution Audit
```

Readiness should check:

```text
http://localhost:8050/api/v1/agent-actions/summary
```

Do not approve or execute actions during readiness.

---

# Frontend UI

Add service:

```text
frontend/src/services/agentActionsApi.ts
```

Update:

```text
frontend/src/pages/AgentInvestigationPages.tsx
frontend/src/pages/AgentChatPages.tsx
```

Optional dedicated route:

```text
/agent-actions
/agent-actions/proposals
/agent-actions/executions
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

## UI requirements

The UI should show:

```text
safe action catalog
proposals table
proposal detail
approval/rejection controls
dry-run output
execution result
execution history
case-linked proposals in investigation workspace
```

For every execute button, show confirmation text:

```text
This will execute a predefined local safe action only. It will not run shell commands, call external systems, send messages, or perform autonomous remediation.
```

---

# Tests

Add backend tests for:

```text
safe action catalog
proposal generation for AMS ticket case
proposal generation for alert case
approve proposal
reject proposal
cannot execute unapproved proposal
cannot execute rejected proposal
dry run does not mutate data
execute approved CREATE_AMS_WORK_NOTE_DRAFT
execute approved CREATE_CUSTOMER_UPDATE_DRAFT
execute approved CREATE_NEXT_STEPS_CHECKLIST
execute approved ADD_INTERNAL_CASE_NOTE
duplicate execution prevented
execution audit created
timeline includes approval/execution events
agent chat system message appended
BFF exposure rules
Business BFF does not expose agent-actions
Simulation BFF does not expose agent-actions
demo control includes agent-actions readiness
no external LLM/API/shell required
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
      "initial_message": "Investigate this AMS ticket and propose safe next actions.",
      "reuse_existing": true,
      "use_real_model": false
    }'
)

echo "$HANDOFF" | jq .

CASE_ID=$(echo "$HANDOFF" | jq -r '.case_id')
echo "$CASE_ID"
```

List proposals:

```bash
curl -sS "http://localhost:8050/api/v1/agent-actions/proposals?case_id=${CASE_ID}" | jq .
```

Capture one proposal:

```bash
PROPOSAL_ID=$(
  curl -sS "http://localhost:8050/api/v1/agent-actions/proposals?case_id=${CASE_ID}" \
  | jq -r 'if type=="array" then .[0].proposal_id elif has("items") then .items[0].proposal_id else empty end'
)

echo "$PROPOSAL_ID"
```

Dry run:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-actions/proposals/${PROPOSAL_ID}/dry-run" \
  -H "Content-Type: application/json" \
  -d '{"requested_by_role":"SERVICE_ENGINEER"}' | jq .
```

Approve:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-actions/proposals/${PROPOSAL_ID}/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by_role": "SERVICE_ENGINEER",
    "approval_comment": "Approved after reviewing evidence.",
    "execute_after_approval": false
  }' | jq .
```

Execute:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-actions/proposals/${PROPOSAL_ID}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "requested_by_role": "SERVICE_ENGINEER",
    "execution_comment": "Execute approved safe local action."
  }' | jq .
```

Expected:

```text
approved proposal executes
execution audit created
no shell command
no external API call
no ServiceNow
no customer send
```

Duplicate execute:

```bash
curl -sS -X POST "http://localhost:8050/api/v1/agent-actions/proposals/${PROPOSAL_ID}/execute" \
  -H "Content-Type: application/json" \
  -d '{"requested_by_role":"SERVICE_ENGINEER"}' | jq .
```

Expected:

```text
duplicate prevented or skipped safely
```

BFF exposure:

```bash
curl -sS http://localhost:8062/api/v1/agent-actions/summary | jq .
curl -sS http://localhost:8065/api/v1/agent-actions/summary | jq .
curl -i -sS http://localhost:8061/api/v1/agent-actions/summary | head
curl -i -sS http://localhost:8063/api/v1/agent-actions/summary | head
curl -i -sS http://localhost:8064/api/v1/agent-actions/summary | head
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
safe action warning visible
action proposals visible
dry run works
approve works
reject works on another proposal
execute approved action works
execution audit visible
duplicate execution is prevented
timeline shows approval/execution events
chat system message appears
no autonomous action controls exist
```

If dedicated routes were added:

```text
http://localhost:4015/agent-actions
http://localhost:4015/agent-actions/proposals
http://localhost:4015/agent-actions/executions
```

Validate they load.

---

# Documentation Updates

Update `README.md` with:

```text
Stage 2 approval-gated action overview
safe action catalog
manual validation commands
what is allowed
what is prohibited
no autonomous remediation
```

Update `ARCHITECTURE.md` with:

```text
Stage 2 action architecture
proposal -> approval -> execution -> audit flow
safe action handler pattern
timeline integration
future Stage 3 autonomous remediation boundary
```

Document clearly:

```text
Prompt 23 introduces approval-gated local safe actions only.
It does not introduce autonomous remediation.
It does not execute shell commands.
It does not call external systems.
It does not post to ServiceNow.
It does not send customer communications.
```

---

# Definition of Done

Prompt 23 is complete only when:

- safe action catalog exists
- action service exists
- proposal approval works
- proposal rejection works
- dry run works and does not mutate data
- unapproved proposal cannot execute
- rejected proposal cannot execute
- approved safe proposal can execute
- execution audit exists
- duplicate execution is prevented
- workspace shows action controls
- timeline includes approval/execution events
- chat system messages are appended
- Operations BFF exposes agent-actions
- Agentic BFF exposes agent-actions
- Business BFF does not expose agent-actions
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
- Prompt 23 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. Safe action catalog summary
5. Approval workflow behavior
6. Dry-run behavior
7. Execution handler behavior
8. Duplicate prevention behavior
9. Backend APIs added
10. BFF exposure summary
11. Frontend routes/pages added
12. Investigation workspace integration summary
13. Timeline/chat integration summary
14. Demo control integration summary
15. Backend test results
16. Frontend build results
17. Demo stack validation results
18. Manual API validation results
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
feat: add approval gated agent actions
```

Do not proceed beyond this prompt.