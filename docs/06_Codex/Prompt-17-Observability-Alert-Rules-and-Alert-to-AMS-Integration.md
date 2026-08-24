# Prompt 17 – Observability Alert Rules and Alert-to-AMS Integration

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 13 added the local observability stack.

Prompt 14 added frontend experience segregation.

Prompt 15 added backend/BFF segregation.

Prompt 16 added demo stack orchestration and a read-only demo control panel.

Your task now is to implement:

```text
Observability Alert Rules and Alert-to-AMS Integration
```

---

## Business Goal

The platform should now demonstrate the full observability-to-operations flow:

```text
Runtime telemetry
      ->
Metrics/logs/traces
      ->
Alert rule evaluation
      ->
Alert event
      ->
AMS ticket
      ->
Support triage
      ->
Future agentic investigation
```

This prompt should create a governed local alerting foundation that can later feed the agentic support system.

The goal is not to create a production alerting system yet.

The goal is to create a demo-ready alert-to-ticket pipeline with clear boundaries, auditability, and future extensibility.

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

Prompt 16 added:

```text
./scripts/start-demo-stack.sh
./scripts/status-demo-stack.sh
./scripts/validate-demo-stack.sh
./scripts/stop-demo-stack.sh
http://localhost:4001/demo-control
```

The current system already has:

```text
Monitoring alerts
Monitoring triage
AMS tickets
Operations exceptions
Runtime observability
Observability stack APIs
Batch failures
Synthetic user journeys
Copilot mock AI foundation
```

Do not break any of these.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve all existing frontend and backend/BFF URLs.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

You must not introduce ServiceNow integration.

You must not introduce external LLM calls.

You must not introduce autonomous remediation.

You must not introduce authentication or authorization.

You must not create real Grafana alert rules unless explicitly necessary.

You must not rely on live Prometheus/Grafana being available during tests.

You must not create an uncontrolled background scheduler.

If background-style evaluation is needed, implement it as manually triggered API endpoints for now.

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

unless justified.

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

Implement a local alert rule and alert evaluation layer that can evaluate EOS runtime metrics and known operational signals, then create AMS tickets.

The alerting layer should support:

```text
alert rule catalog
manual rule evaluation
alert evaluation run history
alert events
alert-to-AMS ticket creation
duplicate suppression
severity mapping
evidence capture
operations console visibility
observability control visibility
simulation lab trigger support
future agentic handoff
```

---

# Data Model

Add a migration only if needed.

Create tables similar to the following if current monitoring tables are insufficient.

Suggested tables:

```text
obs_alert_rules
obs_alert_evaluation_runs
obs_alert_events
obs_alert_event_evidence
obs_alert_ticket_links
```

If existing monitoring tables can be reused cleanly, do so.

However, keep the new observability alerting concept clear and distinct from older synthetic monitoring alert noise.

---

## obs_alert_rules

Fields:

```text
id
rule_code
name
description
signal_type
source_system
metric_name
query_text
condition_operator
threshold_value
severity
enabled
deduplication_key_template
cooldown_minutes
evaluation_window_minutes
target_experience
recommended_owner
create_ticket_by_default
created_at
updated_at
```

Example rules:

```text
EOS_API_ERROR_RATE_HIGH
EOS_API_LATENCY_HIGH
EOS_BACKEND_UNAVAILABLE
EOS_BUSINESS_BFF_UNAVAILABLE
EOS_OPERATIONS_BFF_UNAVAILABLE
EOS_SIMULATION_BFF_UNAVAILABLE
EOS_OBSERVABILITY_BFF_UNAVAILABLE
EOS_AGENTIC_BFF_UNAVAILABLE
EOS_POSTGRES_CONNECTIVITY_DEGRADED
EOS_REDIS_CONNECTIVITY_DEGRADED
EOS_BATCH_FAILURE_SPIKE
EOS_AMS_TICKET_BACKLOG_HIGH
```

---

## obs_alert_evaluation_runs

Fields:

```text
id
run_id
trigger_source
status
started_at
completed_at
rules_evaluated
events_created
events_suppressed
tickets_created
error_message
```

Trigger sources:

```text
MANUAL
SIMULATION
DEMO_CONTROL
OBSERVABILITY_CONTROL
FUTURE_SCHEDULER
```

---

## obs_alert_events

Fields:

```text
id
event_id
rule_id
rule_code
title
description
severity
status
deduplication_key
source_signal
source_url
observed_value
threshold_value
condition_summary
first_seen_at
last_seen_at
occurrence_count
suppressed_count
ticket_creation_status
created_ticket_id
created_at
updated_at
```

Statuses:

```text
OPEN
ACKNOWLEDGED
TICKETED
SUPPRESSED
RESOLVED
```

Ticket creation statuses:

```text
NOT_REQUIRED
PENDING
CREATED
SUPPRESSED_DUPLICATE
FAILED
```

---

## obs_alert_event_evidence

Fields:

```text
id
event_id
evidence_type
title
summary
payload_json
source_url
created_at
```

Evidence types:

```text
PROMETHEUS_METRIC
RUNTIME_HEALTH
BFF_HEALTH
LOG_SUMMARY
TRACE_SUMMARY
BATCH_RUN
AMS_BACKLOG
SIMULATION
```

---

## obs_alert_ticket_links

Fields:

```text
id
event_id
ams_ticket_id
link_type
created_at
created_by
```

Link types:

```text
AUTO_CREATED
MANUALLY_LINKED
DUPLICATE_SUPPRESSED
```

---

# Seed Alert Rules

Add an idempotent seed module:

```text
backend/app/db/seed_observability_alerts.py
```

Seed a small set of useful demo rules.

Recommended initial rules:

```text
EOS_BACKEND_UNAVAILABLE
EOS_BUSINESS_BFF_UNAVAILABLE
EOS_OPERATIONS_BFF_UNAVAILABLE
EOS_SIMULATION_BFF_UNAVAILABLE
EOS_OBSERVABILITY_BFF_UNAVAILABLE
EOS_AGENTIC_BFF_UNAVAILABLE
EOS_API_ERROR_RATE_HIGH
EOS_API_LATENCY_HIGH
EOS_BATCH_FAILURE_SPIKE
EOS_AMS_TICKET_BACKLOG_HIGH
```

Do not require Prometheus to be available for the seed.

Update documentation and validation commands to run:

```bash
python -m app.db.seed_observability_alerts
```

---

# Alert Evaluation Logic

Implement a service:

```text
backend/app/services/observability_alert_service.py
```

It should support:

```text
list rules
get rule
enable/disable rule
evaluate one rule
evaluate all enabled rules
list evaluation runs
get evaluation run
list alert events
get alert event
acknowledge alert event
resolve alert event
create AMS ticket from alert event
```

Evaluation should be deterministic and testable.

Use short-timeout HTTP checks where needed.

Where real metric queries are not safe or not available, use current internal runtime data from the database.

Examples:

## Backend/BFF availability rules

Check:

```text
http://localhost:8050/health
http://localhost:8061/health
http://localhost:8062/health
http://localhost:8063/health
http://localhost:8064/health
http://localhost:8065/health
```

If unavailable, create event.

## API error/latency rules

Prefer existing runtime observability metric tables if available.

Fallback to safe mock/demo evaluation with clear evidence.

## Batch failure spike rule

Use existing batch run data.

If recent failed batch runs exceed threshold, create event.

## AMS backlog rule

Use existing AMS ticket data.

If open tickets exceed threshold, create event.

---

# Duplicate Suppression

Implement deduplication.

If an open event exists with the same deduplication key within cooldown window:

```text
do not create a new event
increment occurrence_count or suppressed_count
record suppression in evaluation run
do not create duplicate AMS ticket
```

Deduplication should be tested.

---

# Alert-to-AMS Ticket Creation

Add service method:

```text
create_ticket_from_alert_event(event_id)
```

It should create an AMS ticket using existing AMS services/models.

Ticket fields should clearly indicate observability source.

Suggested title format:

```text
[Observability Alert] <alert title>
```

Suggested description should include:

```text
rule code
severity
condition summary
observed value
threshold
first seen
last seen
evidence summary
source URLs if available
```

Suggested ticket category:

```text
Observability Alert
```

Suggested ticket source/channel:

```text
OBSERVABILITY_ALERT
```

If the AMS model has constrained fields, map to existing valid values.

Do not auto-resolve tickets.

Do not execute remediation.

---

# Backend APIs

Add routes under:

```text
/api/v1/observability-alerts
```

Expose on:

```text
Full backend 8050
Operations BFF 8062
Observability Control BFF 8064
Agentic BFF 8065 optional read-only
```

Do not expose on Business BFF unless needed.

## Required endpoints

```text
GET  /api/v1/observability-alerts/summary
GET  /api/v1/observability-alerts/rules
GET  /api/v1/observability-alerts/rules/{rule_id}
POST /api/v1/observability-alerts/rules/{rule_id}/enable
POST /api/v1/observability-alerts/rules/{rule_id}/disable

POST /api/v1/observability-alerts/evaluate
POST /api/v1/observability-alerts/evaluate/{rule_id}

GET  /api/v1/observability-alerts/evaluation-runs
GET  /api/v1/observability-alerts/evaluation-runs/{run_id}

GET  /api/v1/observability-alerts/events
GET  /api/v1/observability-alerts/events/{event_id}
POST /api/v1/observability-alerts/events/{event_id}/acknowledge
POST /api/v1/observability-alerts/events/{event_id}/resolve
POST /api/v1/observability-alerts/events/{event_id}/create-ticket
```

Optional simulation endpoint:

```text
POST /api/v1/observability-alerts/simulations/backend-unavailable
```

If implemented, it should not actually stop the backend. It should create a simulated alert event with evidence.

---

# Frontend UI

Add pages to Operations and Observability experiences.

Suggested files:

```text
frontend/src/services/observabilityAlertsApi.ts
frontend/src/pages/ObservabilityAlertPages.tsx
```

## Routes

```text
/observability-alerts
/observability-alerts/rules
/observability-alerts/evaluation-runs
/observability-alerts/events
/observability-alerts/events/:eventId
```

Make these visible in:

```text
operations
observability
full
```

Optional read-only visibility in:

```text
agentic
```

Do not show in:

```text
business
```

## UI Capabilities

The UI should support:

```text
view summary
view rule catalog
enable/disable rules
manually evaluate all enabled rules
evaluate a single rule
view evaluation runs
view alert events
view event detail and evidence
acknowledge event
resolve event
create AMS ticket from event
open linked AMS ticket
```

Clearly label:

```text
No remediation is executed by this feature.
Ticket creation is the only operational action.
```

---

# Demo Control Integration

Update demo control readiness or components to include:

```text
Observability Alerting
```

Include the summary endpoint:

```text
http://localhost:8050/api/v1/observability-alerts/summary
```

Do not add start/stop controls.

---

# BFF Route Exposure

Update BFF route exposure:

## Operations BFF

Expose:

```text
/api/v1/observability-alerts/*
```

## Observability Control BFF

Expose:

```text
/api/v1/observability-alerts/*
```

## Agentic BFF

Expose read-only endpoints if simple:

```text
GET /api/v1/observability-alerts/summary
GET /api/v1/observability-alerts/events
GET /api/v1/observability-alerts/events/{event_id}
```

If read-only route filtering is too complex, expose the full route for now but document TODO to restrict mutation routes later.

Do not expose on Business BFF.

---

# Tests

Add backend tests for:

```text
seed observability alert rules
list rules
evaluate enabled rules
evaluation run creation
alert event creation
duplicate suppression
acknowledge event
resolve event
create AMS ticket from event
BFF route exposure
Business BFF does not expose observability-alerts
demo control includes observability alerting
```

Tests must not require live Prometheus, Grafana, Tempo, or Loki.

Use deterministic internal checks or mocks where necessary.

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

## Manual API validation

```bash
curl -sS http://localhost:8050/api/v1/observability-alerts/summary | jq .
curl -sS http://localhost:8050/api/v1/observability-alerts/rules | jq .
curl -sS -X POST http://localhost:8050/api/v1/observability-alerts/evaluate \
  -H "Content-Type: application/json" \
  -d '{"trigger_source":"MANUAL"}' | jq .
curl -sS http://localhost:8050/api/v1/observability-alerts/evaluation-runs | jq .
curl -sS http://localhost:8050/api/v1/observability-alerts/events | jq .
```

## Manual BFF validation

```bash
curl -sS http://localhost:8062/api/v1/observability-alerts/summary | jq .
curl -sS http://localhost:8064/api/v1/observability-alerts/summary | jq .
curl -i -sS http://localhost:8061/api/v1/observability-alerts/summary | head
```

Expected for Business BFF:

```text
HTTP/1.1 404 Not Found
```

## Manual UI validation

Open:

```text
http://localhost:4001/observability-alerts
http://localhost:4012/observability-alerts
http://localhost:4014/observability-alerts
```

Validate:

```text
summary loads
rules load
manual evaluate works
evaluation runs load
events load
event detail loads
acknowledge works
resolve works
create ticket works
linked AMS ticket opens
```

---

# Definition of Done

Prompt 17 is complete only when:

- observability alert rule catalog exists
- seed module exists and is idempotent
- alert evaluation run tracking exists
- alert events are created deterministically
- duplicate suppression works
- alert evidence is captured
- alert-to-AMS ticket creation works
- APIs exist under `/api/v1/observability-alerts`
- Operations BFF exposes alert APIs
- Observability BFF exposes alert APIs
- Business BFF does not expose alert APIs
- frontend pages exist
- operations experience shows observability alerting
- observability experience shows observability alerting
- full experience shows observability alerting
- demo control includes observability alerting status
- backend tests pass
- frontend build passes
- demo stack validation passes
- no live Prometheus/Grafana dependency is required for tests
- no ServiceNow integration introduced
- no external LLM introduced
- no autonomous remediation introduced
- no authentication introduced
- no broad process killing introduced
- Docker Compose unchanged unless justified
- observability infrastructure unchanged unless justified
- README updated
- ARCHITECTURE.md updated
- Prompt 17 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary, if any
4. Alert rules seeded
5. Alert evaluation behavior
6. Duplicate suppression behavior
7. Alert evidence behavior
8. Alert-to-AMS ticket behavior
9. Backend APIs added
10. BFF exposure summary
11. Frontend routes added
12. Demo control integration summary
13. Backend test results
14. Frontend build results
15. Demo stack validation results
16. Manual API validation results
17. Manual UI validation results
18. Confirmation no ServiceNow integration was introduced
19. Confirmation no external LLM was introduced
20. Confirmation no autonomous remediation was introduced
21. TODOs or limitations
22. Recommended Git commit message

Recommended commit message:

```text
feat: add observability alert to ams integration
```

Do not proceed beyond this prompt.