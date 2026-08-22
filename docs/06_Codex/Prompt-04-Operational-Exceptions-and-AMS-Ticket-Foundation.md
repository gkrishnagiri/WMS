# Prompt 04 – Operational Exceptions and AMS Ticket Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 01 created the enterprise application foundation.

Prompt 02 created the read-focused **Warehouse & Fulfillment Operations** domain foundation.

Prompt 03 created warehouse transaction workflows:

```text
Create Order
Allocate
Release Tasks
Pick
Pack
Ship
Inventory Transaction Ledger
```

Your task now is to implement the first **Application Maintenance Services foundation** around the warehouse module:

```text
Operational Exceptions
Failure Simulation
AMS Ticket Foundation
```

This prompt introduces the supportability layer, but it must remain deterministic.

Do not implement GenAI, LLMs, agents, LangGraph, autonomous resolution, or ticket analytics yet.

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
- Warehouse workflow APIs
- Inventory transaction ledger
- Order event history
- Frontend warehouse pages
- Frontend workflow pages
- Backend running on port `8050`
- Frontend running on port `4001`

Recent commits include:

```text
feat: add EOS enterprise foundation
feat: add warehouse fulfillment domain foundation
feat: add warehouse transaction workflows
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

- charting libraries
- workflow engines
- Celery
- Dramatiq
- Kafka
- Temporal
- LangGraph
- LLM SDKs
- agent frameworks
- ServiceNow connectors

---

# Objective

Implement the deterministic supportability layer for EOS.

Prompt 04 should create:

1. Operational exception model
2. Exception detection rules
3. Failure simulation endpoints
4. AMS ticket model
5. Ticket creation from exceptions
6. Ticket lifecycle APIs
7. Exception and ticket frontend pages
8. Backend tests
9. Documentation updates

This prompt should allow the demo application to show:

```text
A warehouse workflow fails or degrades
        ↓
An operational exception is recorded
        ↓
An AMS ticket is created
        ↓
Support lifecycle begins
```

This is the foundation for future AI-native AMS capabilities.

---

# Scope

Implement:

- Deterministic operational exceptions
- Manual and simulated exception generation
- AMS ticket creation from exceptions
- Ticket lifecycle transitions
- Exception-to-ticket linkage
- Basic support dashboard
- Exception and ticket details
- Tests and documentation

Do not implement:

- AI classification
- LLM summaries
- autonomous remediation
- ServiceNow integration
- email/slack integration
- incident prediction
- root cause inference
- vector search
- embeddings
- agent orchestration
- automated code changes
- production incident management process complexity

Those come later.

---

# Conceptual Model

Prompt 04 introduces two related but separate concepts.

## Operational Exception

An operational exception is something wrong or abnormal inside the EOS business process.

Examples:

```text
Insufficient inventory
Order stuck in PICKING
Task blocked
Shipment exception
Low stock condition
Workflow validation failure
```

Operational exceptions represent business/application symptoms.

## AMS Ticket

An AMS ticket is a support record created to manage investigation and resolution of an exception.

Examples:

```text
AMS-INC-20260822-0001
AMS-SR-20260822-0001
AMS-PROB-20260822-0001
```

AMS tickets represent support work.

---

# Database Additions

Create a new Alembic migration.

Add the following tables:

```text
ops_exceptions
ams_tickets
ams_ticket_events
```

Optional, only if useful and consistent:

```text
ops_simulation_runs
```

Use UUID primary keys consistent with the existing project style.

Use timestamp conventions consistent with the existing project.

---

## Table: `ops_exceptions`

Purpose:

Record operational exceptions detected or simulated in EOS.

Fields:

```text
id
exception_number
exception_type
severity
status
source_module
source_entity_type
source_entity_id
source_reference
title
description
detection_method
business_impact
technical_context
first_detected_at
last_detected_at
resolved_at
created_at
updated_at
```

Rules:

- `exception_number` must be unique
- `source_module` should usually be `WAREHOUSE_FULFILLMENT`
- `source_entity_type` examples:
  - ORDER
  - ORDER_LINE
  - TASK
  - SHIPMENT
  - INVENTORY_BALANCE
  - ITEM
  - SYSTEM
- `source_entity_id` should be nullable UUID text or UUID depending on existing style
- `technical_context` should be JSON/JSONB if supported
- `business_impact` should be short human-readable text

Suggested exception types:

```text
INSUFFICIENT_STOCK
LOW_STOCK
ORDER_STUCK
TASK_BLOCKED
TASK_OVERDUE
SHIPMENT_EXCEPTION
WORKFLOW_VALIDATION_FAILURE
SYSTEM_INTEGRATION_FAILURE
```

Suggested severities:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Suggested statuses:

```text
OPEN
ACKNOWLEDGED
LINKED_TO_TICKET
RESOLVED
SUPPRESSED
```

Suggested detection methods:

```text
SIMULATED
RULE_BASED
USER_REPORTED
SYSTEM
```

---

## Table: `ams_tickets`

Purpose:

Record deterministic AMS support tickets linked to operational exceptions or application symptoms.

Fields:

```text
id
ticket_number
ticket_type
severity
priority
status
source
source_module
exception_id
affected_entity_type
affected_entity_id
short_description
description
assignment_group
assigned_to
business_service
application_name
environment
opened_at
acknowledged_at
resolved_at
closed_at
resolution_code
resolution_notes
created_at
updated_at
```

Rules:

- `ticket_number` must be unique
- `exception_id` nullable, references `ops_exceptions.id`
- `source_module` should usually be `WAREHOUSE_FULFILLMENT`
- `application_name` should default to `Enterprise Operations Suite`
- `environment` should default to current app environment
- `business_service` should default to `Warehouse & Fulfillment Operations`

Suggested ticket types:

```text
INCIDENT
SERVICE_REQUEST
PROBLEM
```

For Prompt 04, implement at minimum:

```text
INCIDENT
```

Suggested severities:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Suggested priorities:

```text
P4
P3
P2
P1
```

Suggested statuses:

```text
NEW
ACKNOWLEDGED
IN_PROGRESS
RESOLVED
CLOSED
CANCELLED
```

Suggested source values:

```text
EXCEPTION
MANUAL
SIMULATION
SYSTEM
```

Suggested assignment group:

```text
AMS-WAREHOUSE-SUPPORT
```

---

## Table: `ams_ticket_events`

Purpose:

Maintain lifecycle and audit history for AMS tickets.

Fields:

```text
id
ticket_id
event_type
from_status
to_status
message
event_payload
created_by
created_at
```

Rules:

- `ticket_id` references `ams_tickets.id`
- `event_payload` should be JSON/JSONB if supported
- `created_by` defaults to `system`

Suggested event types:

```text
TICKET_CREATED
TICKET_ACKNOWLEDGED
TICKET_ASSIGNED
TICKET_STATUS_CHANGED
TICKET_RESOLVED
TICKET_CLOSED
TICKET_CANCELLED
COMMENT_ADDED
```

---

## Optional Table: `ops_simulation_runs`

Only add this if it is straightforward.

Purpose:

Track user-triggered simulations.

Fields:

```text
id
simulation_type
status
input_payload
result_payload
created_by
created_at
```

Suggested statuses:

```text
SUCCESS
FAILED
```

If this table adds too much complexity, skip it and document as deferred.

---

# Exception Detection Rules

Implement deterministic rules.

Do not add a rule engine.

Do not add external dependencies.

Create a service module such as:

```text
backend/app/services/operations_exception_service.py
```

or similar.

Implement these rules.

---

## Rule 1: Low Stock

Detect inventory balances where:

```text
quantity_on_hand - quantity_allocated <= item.reorder_point
```

Create or return an open `LOW_STOCK` exception.

Rules:

- Do not create duplicate open exceptions for the same item/location.
- Severity:
  - `CRITICAL` if available quantity is `0`
  - `HIGH` if available quantity is below safety stock
  - `MEDIUM` otherwise

---

## Rule 2: Order Stuck

Detect orders that have remained in an active workflow status beyond a threshold.

Statuses:

```text
ALLOCATED
PICKING
PACKING
```

Default threshold:

```text
24 hours
```

Create or return an `ORDER_STUCK` exception.

For Prompt 04, it is acceptable to expose this as an endpoint that accepts `threshold_hours`.

---

## Rule 3: Task Blocked

Allow a task to be marked as blocked.

When a task is blocked:

- set task status to `BLOCKED`
- create `TASK_BLOCKED` exception
- optionally create an AMS incident

---

## Rule 4: Shipment Exception

Allow a shipment to be marked as exception.

When a shipment is marked exception:

- set shipment status to `EXCEPTION`
- create `SHIPMENT_EXCEPTION` exception
- optionally create an AMS incident

---

# Failure Simulation

Create deterministic simulation endpoints.

These are demo tools, not production features.

Use the namespace:

```text
/api/v1/operations/simulations
```

Implement:

```text
POST /api/v1/operations/simulations/low-stock
POST /api/v1/operations/simulations/task-blocked
POST /api/v1/operations/simulations/shipment-exception
POST /api/v1/operations/simulations/order-stuck
```

---

## Simulate Low Stock

Endpoint:

```text
POST /api/v1/operations/simulations/low-stock
```

Request:

```json
{
  "item_id": "optional-item-uuid",
  "warehouse_id": "optional-warehouse-uuid",
  "create_ticket": true
}
```

Behavior:

- Find a deterministic inventory balance if none supplied.
- Reduce available inventory to trigger low stock.
- Create inventory transaction if the existing ledger supports it cleanly.
- Create or return a `LOW_STOCK` exception.
- If `create_ticket = true`, create or return linked AMS incident.
- Must be idempotent enough to avoid duplicate open exceptions/tickets for the same item/location.

---

## Simulate Task Blocked

Endpoint:

```text
POST /api/v1/operations/simulations/task-blocked
```

Request:

```json
{
  "task_id": "optional-task-uuid",
  "reason": "Picker device unavailable",
  "create_ticket": true
}
```

Behavior:

- Find a deterministic non-completed task if none supplied.
- Set task status to `BLOCKED`.
- Create or return `TASK_BLOCKED` exception.
- If `create_ticket = true`, create or return linked AMS incident.

---

## Simulate Shipment Exception

Endpoint:

```text
POST /api/v1/operations/simulations/shipment-exception
```

Request:

```json
{
  "shipment_id": "optional-shipment-uuid",
  "reason": "Carrier label generation failed",
  "create_ticket": true
}
```

Behavior:

- Find a deterministic shipment if none supplied.
- Set shipment status to `EXCEPTION`.
- Create or return `SHIPMENT_EXCEPTION` exception.
- If `create_ticket = true`, create or return linked AMS incident.

---

## Simulate Order Stuck

Endpoint:

```text
POST /api/v1/operations/simulations/order-stuck
```

Request:

```json
{
  "order_id": "optional-order-uuid",
  "status": "PICKING",
  "create_ticket": true
}
```

Behavior:

- Find or update a deterministic order into an active workflow status.
- Adjust timestamps only if safe and simple.
- Create or return `ORDER_STUCK` exception.
- If `create_ticket = true`, create or return linked AMS incident.

If modifying timestamps is awkward, create a deterministic exception without timestamp mutation and document the simplification.

---

# Backend API Endpoints

Create operations and AMS APIs.

Suggested files:

```text
backend/app/models/operations.py
backend/app/models/ams.py
backend/app/schemas/operations.py
backend/app/schemas/ams.py
backend/app/services/operations_exception_service.py
backend/app/services/ams_ticket_service.py
backend/app/api/routes/operations.py
backend/app/api/routes/ams.py
```

You may organize differently if consistent with existing project style.

---

## Operations APIs

Use prefix:

```text
/api/v1/operations
```

Add:

```text
GET  /api/v1/operations/exceptions
GET  /api/v1/operations/exceptions/{exception_id}
POST /api/v1/operations/exceptions/{exception_id}/acknowledge
POST /api/v1/operations/exceptions/{exception_id}/resolve
POST /api/v1/operations/detect/low-stock
POST /api/v1/operations/detect/order-stuck
POST /api/v1/operations/simulations/low-stock
POST /api/v1/operations/simulations/task-blocked
POST /api/v1/operations/simulations/shipment-exception
POST /api/v1/operations/simulations/order-stuck
```

### Exception List Filters

Support optional filters:

```text
status
severity
exception_type
source_module
```

Default sort:

```text
open first, newest first
```

---

## AMS Ticket APIs

Use prefix:

```text
/api/v1/ams
```

Add:

```text
GET  /api/v1/ams/summary
GET  /api/v1/ams/tickets
POST /api/v1/ams/tickets
GET  /api/v1/ams/tickets/{ticket_id}
POST /api/v1/ams/tickets/from-exception/{exception_id}
POST /api/v1/ams/tickets/{ticket_id}/acknowledge
POST /api/v1/ams/tickets/{ticket_id}/start-work
POST /api/v1/ams/tickets/{ticket_id}/resolve
POST /api/v1/ams/tickets/{ticket_id}/close
GET  /api/v1/ams/tickets/{ticket_id}/events
```

---

## AMS Summary Response

Endpoint:

```text
GET /api/v1/ams/summary
```

Return:

```json
{
  "open_exceptions": 3,
  "critical_exceptions": 1,
  "open_tickets": 2,
  "p1_tickets": 0,
  "p2_tickets": 1,
  "tickets_in_progress": 1,
  "resolved_today": 0
}
```

Use actual database queries.

---

## Ticket Creation from Exception

Endpoint:

```text
POST /api/v1/ams/tickets/from-exception/{exception_id}
```

Rules:

- If an active ticket already exists for the exception, return it instead of creating duplicate.
- Create ticket type `INCIDENT`.
- Map exception severity to ticket priority:
  - `CRITICAL` → `P1`
  - `HIGH` → `P2`
  - `MEDIUM` → `P3`
  - `LOW` → `P4`
- Ticket status starts as `NEW`.
- Create `TICKET_CREATED` event.
- Update exception status to `LINKED_TO_TICKET`.

---

## Manual Ticket Creation

Endpoint:

```text
POST /api/v1/ams/tickets
```

Request:

```json
{
  "ticket_type": "INCIDENT",
  "severity": "MEDIUM",
  "priority": "P3",
  "short_description": "Warehouse workflow issue",
  "description": "Manual support ticket for demo scenario",
  "affected_entity_type": "ORDER",
  "affected_entity_id": "optional-uuid"
}
```

Rules:

- Generate ticket number if not supplied.
- Ticket number format:

```text
AMS-INC-YYYYMMDD-0001
```

- Create `TICKET_CREATED` event.

---

## Ticket Lifecycle

Implement deterministic status transitions.

### Acknowledge

```text
POST /api/v1/ams/tickets/{ticket_id}/acknowledge
```

Allowed from:

```text
NEW
```

Result:

```text
ACKNOWLEDGED
```

Set `acknowledged_at`.

Create `TICKET_ACKNOWLEDGED` event.

---

### Start Work

```text
POST /api/v1/ams/tickets/{ticket_id}/start-work
```

Allowed from:

```text
NEW
ACKNOWLEDGED
```

Result:

```text
IN_PROGRESS
```

Create `TICKET_STATUS_CHANGED` event.

---

### Resolve

```text
POST /api/v1/ams/tickets/{ticket_id}/resolve
```

Request:

```json
{
  "resolution_code": "WORKAROUND_APPLIED",
  "resolution_notes": "Reset simulated blocked workflow state."
}
```

Allowed from:

```text
NEW
ACKNOWLEDGED
IN_PROGRESS
```

Result:

```text
RESOLVED
```

Set `resolved_at`.

Create `TICKET_RESOLVED` event.

If linked to an exception, mark exception `RESOLVED` and set `resolved_at`.

---

### Close

```text
POST /api/v1/ams/tickets/{ticket_id}/close
```

Allowed from:

```text
RESOLVED
```

Result:

```text
CLOSED
```

Set `closed_at`.

Create `TICKET_CLOSED` event.

---

# Error Handling

Use:

```text
400 Bad Request
```

for invalid inputs.

Use:

```text
404 Not Found
```

for missing records.

Use:

```text
409 Conflict
```

for invalid lifecycle transitions or duplicate active states.

Do not return generic internal errors for business rule violations.

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
Operations
AMS Tickets
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
Health
About
```

---

## Required Frontend Routes

Add:

```text
/operations/exceptions
/operations/simulations
/ams/tickets
/ams/tickets/:ticketId
```

Existing routes must continue working.

---

## Operations Exceptions Page

Route:

```text
/operations/exceptions
```

Display table:

- exception number
- type
- severity
- status
- source module
- source entity
- title
- first detected
- last detected

Actions:

- acknowledge
- resolve
- create ticket

Use chips for severity and status.

---

## Operations Simulations Page

Route:

```text
/operations/simulations
```

Display simulation cards:

```text
Low Stock
Task Blocked
Shipment Exception
Order Stuck
```

Each card should have:

- description
- button to run simulation
- checkbox or toggle for `create_ticket`
- result panel showing exception number and ticket number if created

Keep the UI simple.

---

## AMS Tickets Page

Route:

```text
/ams/tickets
```

Display:

- summary cards from `/api/v1/ams/summary`
- ticket table

Ticket table columns:

- ticket number
- type
- priority
- severity
- status
- short description
- assignment group
- opened at

Actions:

- acknowledge
- start work
- resolve
- close where allowed

Ticket number should link to ticket detail page.

---

## AMS Ticket Detail Page

Route:

```text
/ams/tickets/:ticketId
```

Display:

- ticket header
- description
- linked exception information if present
- lifecycle timestamps
- resolution information
- event timeline

Actions:

- acknowledge
- start work
- resolve
- close where allowed

Use simple forms for resolution code and notes.

---

# Frontend API Client

Create or extend typed API clients.

Suggested files:

```text
frontend/src/services/operationsApi.ts
frontend/src/services/amsApi.ts
```

Use `VITE_API_BASE_URL`.

Use TanStack Query for data loading.

Use mutations for actions.

Show loading and error states.

---

# Backend Tests

Add tests covering:

1. Existing health/version tests still pass
2. Existing warehouse read tests still pass
3. Existing warehouse workflow tests still pass
4. Detect low stock
5. Simulate low stock with ticket creation
6. Simulate task blocked
7. Simulate shipment exception
8. Create ticket from exception
9. Prevent duplicate active ticket for same exception
10. Ticket acknowledge transition
11. Ticket start-work transition
12. Ticket resolve transition
13. Ticket close transition
14. Invalid lifecycle transition returns `409`
15. AMS summary endpoint works
16. Exception list endpoint works

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

- Prompt 04 supportability layer summary
- operational exceptions
- simulations
- AMS tickets
- new APIs
- new frontend routes
- validation commands
- backend port `8050`
- frontend port `4001`
- deferred AI-native capabilities

Update `ARCHITECTURE.md` with:

- operations exception module
- AMS ticket module
- exception-to-ticket flow
- simulation capabilities
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
pytest
```

Then validate live backend:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/operations/exceptions | jq .
curl -sS http://localhost:8050/api/v1/ams/summary | jq .
curl -sS -X POST http://localhost:8050/api/v1/operations/simulations/low-stock \
  -H "Content-Type: application/json" \
  -d '{"create_ticket": true}' | jq .
curl -sS http://localhost:8050/api/v1/ams/tickets | jq .
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
http://localhost:4001/operations/exceptions
http://localhost:4001/operations/simulations
http://localhost:4001/ams/tickets
```

Manual UI validation:

```text
Open Operations Simulations
Run Low Stock simulation with ticket creation enabled
Open Operations Exceptions
Confirm exception exists
Open AMS Tickets
Confirm ticket exists
Open ticket detail
Acknowledge ticket
Start work
Resolve ticket
Close ticket
```

---

# Definition of Done

Prompt 04 is complete only when:

- migration exists
- `ops_exceptions` exists
- `ams_tickets` exists
- `ams_ticket_events` exists
- operational exception service exists
- AMS ticket service exists
- simulation APIs exist
- exception APIs exist
- AMS ticket APIs exist
- low stock detection works
- task blocked simulation works
- shipment exception simulation works
- order stuck simulation works
- ticket creation from exception works
- duplicate active tickets are prevented
- ticket lifecycle works
- invalid transitions return clear `409` errors
- frontend exception page works
- frontend simulation page works
- frontend ticket list works
- frontend ticket detail works
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
4. Backend operations APIs added
5. Backend AMS APIs added
6. Frontend routes added
7. Backend validation results
8. Frontend validation results
9. Manual simulation/ticket lifecycle validation result
10. Confirmation that infrastructure files were not modified
11. Any TODOs
12. Recommended Git commit message

Recommended commit message:

```text
feat: add operational exceptions and AMS ticket foundation
```

Do not proceed beyond this prompt.