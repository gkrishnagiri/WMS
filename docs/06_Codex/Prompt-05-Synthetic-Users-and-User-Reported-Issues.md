# Prompt 05 – Synthetic Users and User-Reported Functional Issues

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 01 created the enterprise application foundation.

Prompt 02 created the read-focused **Warehouse & Fulfillment Operations** domain foundation.

Prompt 03 created warehouse transaction workflows.

Prompt 04 created the supportability foundation:

```text
Operational Exceptions
AMS Tickets
Ticket Events
Simulation APIs
Ticket lifecycle
```

Your task now is to implement the first **user-driven failure scenario foundation**:

```text
Synthetic Users
Synthetic User Journeys
User-Reported Functional Issues
Ticket Creation from User Reports
```

This prompt represents scenarios where **users experience failures and raise tickets**, especially where there is no monitoring system or no automated detection.

Do not implement monitoring alert noise, observability-based diagnosis, batch jobs, GenAI, agents, LLMs, or ServiceNow integration yet.

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
- Frontend warehouse pages
- Frontend operations pages
- Frontend AMS ticket pages
- Backend running on port `8050`
- Frontend running on port `4001`

Recent committed capabilities include:

```text
feat: add EOS enterprise foundation
feat: add warehouse fulfillment domain foundation
feat: add warehouse transaction workflows
feat: add operational exceptions and AMS ticket foundation
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

- browser automation frameworks
- Playwright
- Selenium
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

Synthetic users in this prompt are deterministic backend-driven personas and journeys, not real browser automation.

---

# Objective

Implement deterministic synthetic users and user-reported issue flows.

This prompt should allow EOS to demonstrate this scenario:

```text
Synthetic user performs a warehouse workflow
        ↓
Workflow succeeds or fails
        ↓
If the user experiences a functional failure, a user issue report is submitted
        ↓
An AMS ticket is created from the user report
        ↓
Support lifecycle continues through the existing AMS ticket module
```

This prompt specifically addresses the following demo scenarios:

```text
A. Synthetic users try to use the application and face failures
E. Functional issue is raised by a user
```

It does **not** address:

```text
B. Monitoring alert noise without observability
C. Monitoring plus observability-enabled diagnosis
D. Batch issue
```

Those will come in later prompts.

---

# Architectural Intent

Prompt 04 created the place where issues and tickets land.

Prompt 05 creates one source of those tickets:

```text
Synthetic User / Business User
        ↓
User-Reported Issue
        ↓
AMS Ticket
```

For this prompt, user-reported issues should not require monitoring or observability.

A user-reported issue may or may not have an operational exception.

Default behavior:

```text
Synthetic journey failure
        ↓
User issue report
        ↓
AMS ticket
```

Do not automatically create operational exceptions for every user report unless the current code structure makes it simple and clearly useful.

The key distinction:

```text
Operational Exception = system/business symptom
User Issue Report     = human-reported experience
AMS Ticket            = support work item
```

---

# Scope

Implement:

1. Synthetic user model
2. Synthetic journey catalog
3. Synthetic journey run history
4. User-reported issue model
5. Ticket creation from user reports
6. Deterministic warehouse journey simulations
7. Frontend synthetic user journey page
8. Frontend user issue report page
9. AMS ticket integration
10. Tests and documentation

Do not implement:

- monitoring alerts
- observability traces
- log analysis
- batch jobs
- AI classification
- LLM summaries
- autonomous remediation
- external ITSM integration
- email/slack integration
- real browser automation
- production identity management

---

# Database Additions

Create a new Alembic migration.

Add the following tables:

```text
synthetic_users
synthetic_journeys
synthetic_journey_runs
ams_user_reports
```

Use UUID primary keys consistent with the existing project style.

Use timestamp conventions consistent with the existing project.

---

## Table: `synthetic_users`

Purpose:

Represent deterministic demo users/personas who interact with EOS.

Fields:

```text
id
user_code
display_name
persona
department
role
email
active
created_at
updated_at
```

Rules:

- `user_code` must be unique
- `email` should be unique if provided
- `active` defaults to true

Suggested personas:

```text
ORDER_MANAGER
WAREHOUSE_SUPERVISOR
PICKER
PACKER
SHIPPING_COORDINATOR
BUSINESS_USER
```

Seed examples:

```text
USR-ORDER-MGR-01    Olivia Order Manager
USR-WH-SUP-01       Sam Warehouse Supervisor
USR-PICKER-01       Priya Picker
USR-PACKER-01       Peter Packer
USR-SHIP-01         Sofia Shipping Coordinator
USR-BIZ-USER-01     Ben Business User
```

---

## Table: `synthetic_journeys`

Purpose:

Represent deterministic business/user journeys that can be run repeatedly for demo scenarios.

Fields:

```text
id
journey_code
name
description
persona
journey_type
expected_outcome
creates_user_report_on_failure
creates_ticket_on_failure
enabled
default_payload
created_at
updated_at
```

Rules:

- `journey_code` must be unique
- `default_payload` should be JSON/JSONB if supported
- `enabled` defaults to true

Suggested journey types:

```text
SUCCESS_PATH
FUNCTIONAL_FAILURE
VALIDATION_FAILURE
USER_REPORTED_ISSUE
```

Seed journeys:

```text
JRN-ORDER-FULFILL-SUCCESS
JRN-ALLOCATE-INSUFFICIENT-STOCK
JRN-PACK-BEFORE-PICK
JRN-SHIP-BEFORE-PACK
JRN-MANUAL-FUNCTIONAL-ISSUE
```

---

## Table: `synthetic_journey_runs`

Purpose:

Maintain auditable history of synthetic journey executions.

Fields:

```text
id
run_number
journey_id
synthetic_user_id
status
started_at
completed_at
duration_ms
input_payload
result_payload
failure_type
failure_message
order_id
task_id
shipment_id
user_report_id
ticket_id
created_at
updated_at
```

Rules:

- `run_number` must be unique
- `journey_id` references `synthetic_journeys.id`
- `synthetic_user_id` references `synthetic_users.id`
- `input_payload` and `result_payload` should be JSON/JSONB if supported
- `order_id`, `task_id`, `shipment_id`, `user_report_id`, and `ticket_id` may be nullable
- failed journeys should store clear `failure_type` and `failure_message`

Suggested statuses:

```text
SUCCESS
FAILED
PARTIAL
SKIPPED
```

Run number format:

```text
SYN-RUN-YYYYMMDD-0001
```

---

## Table: `ams_user_reports`

Purpose:

Represent issues reported by users or synthetic users.

Fields:

```text
id
report_number
reporter_user_id
reporter_name
reporter_email
reporter_persona
report_channel
source_module
affected_entity_type
affected_entity_id
title
description
business_impact
severity
status
journey_run_id
ticket_id
submitted_at
acknowledged_at
resolved_at
created_at
updated_at
```

Rules:

- `report_number` must be unique
- `reporter_user_id` nullable, references `synthetic_users.id`
- `journey_run_id` nullable, references `synthetic_journey_runs.id`
- `ticket_id` nullable, references `ams_tickets.id`
- `source_module` should usually be `WAREHOUSE_FULFILLMENT`
- `report_channel` should indicate how the issue was submitted
- `affected_entity_type` examples:
  - ORDER
  - TASK
  - SHIPMENT
  - INVENTORY
  - SCREEN
  - UNKNOWN
- `affected_entity_id` may be nullable
- report should be able to exist before a ticket is created

Suggested report channels:

```text
SYNTHETIC_USER
USER_PORTAL
MANUAL
PHONE
EMAIL
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
SUBMITTED
TICKET_CREATED
ACKNOWLEDGED
RESOLVED
CANCELLED
```

Report number format:

```text
USR-RPT-YYYYMMDD-0001
```

---

# AMS Ticket Integration

Extend existing AMS ticket creation logic safely.

Do not break Prompt 04 ticket APIs.

When creating a ticket from a user report:

- ticket type should be `INCIDENT`
- ticket source should be `USER_REPORTED` or `SYNTHETIC_USER`
- source module should be `WAREHOUSE_FULFILLMENT`
- business service should be `Warehouse & Fulfillment Operations`
- application name should be `Enterprise Operations Suite`
- affected entity should come from the user report
- short description should come from the user report title
- description should include user report details
- assignment group should default to `AMS-WAREHOUSE-SUPPORT`

Map severity to priority:

```text
CRITICAL -> P1
HIGH     -> P2
MEDIUM   -> P3
LOW      -> P4
```

Ticket creation from a user report must be idempotent:

```text
If the user report already has an active ticket, return the existing ticket.
```

Update the user report:

```text
status = TICKET_CREATED
ticket_id = created ticket id
```

Create standard AMS ticket events using the existing ticket event model.

---

# Seed Data

Create an idempotent seed module:

```text
backend/app/db/seed_synthetic_users.py
```

Runnable as:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_synthetic_users
```

It should seed:

```text
6 synthetic users
5 synthetic journeys
```

Running it multiple times must not create duplicates.

Update README validation commands to include this seed command.

Do not modify existing warehouse seed behavior.

---

# Synthetic Journey Definitions

Implement deterministic backend-driven synthetic journeys.

Create a service such as:

```text
backend/app/services/synthetic_user_service.py
```

or similar.

Journeys should call existing service-layer logic where practical.

Do not call the backend over HTTP from inside the backend.

Do not use browser automation.

---

## Journey 1: Successful Fulfillment

Code:

```text
JRN-ORDER-FULFILL-SUCCESS
```

Purpose:

Demonstrate a successful synthetic user path.

Flow:

```text
Create order
Allocate order
Release tasks
Complete pick task
Complete pack task
Ship order
```

Expected result:

```text
SUCCESS
```

Rules:

- create a small order with available inventory
- do not create user report
- do not create AMS ticket
- write journey run with status `SUCCESS`
- store created order id and shipment id if available

---

## Journey 2: Insufficient Stock Allocation Failure

Code:

```text
JRN-ALLOCATE-INSUFFICIENT-STOCK
```

Purpose:

Represent a user trying to fulfill an order but allocation fails due to insufficient stock.

Flow:

```text
Create order with excessive quantity
Attempt allocation
Allocation fails with business conflict
Create user issue report
Create AMS ticket if requested
```

Expected result:

```text
FAILED
```

Rules:

- do not corrupt inventory
- do not create partial allocation
- create user report with severity `HIGH`
- if `create_ticket = true`, create linked AMS ticket
- store failure message clearly

Example user report title:

```text
User unable to allocate customer order due to insufficient stock
```

---

## Journey 3: Pack Before Pick Functional Failure

Code:

```text
JRN-PACK-BEFORE-PICK
```

Purpose:

Represent a user attempting an invalid workflow step.

Flow:

```text
Create order
Allocate
Release tasks
Attempt to complete PACK task before PICK task completion
System rejects action
Create user issue report
Create AMS ticket if requested
```

Expected result:

```text
FAILED
```

Rules:

- use existing workflow validation
- failure should be deterministic
- create user report with severity `MEDIUM`
- ticket creation is controlled by request flag

Example user report title:

```text
User attempted pack step before picking was completed
```

---

## Journey 4: Ship Before Pack Functional Failure

Code:

```text
JRN-SHIP-BEFORE-PACK
```

Purpose:

Represent a user attempting to ship an order before warehouse work is complete.

Flow:

```text
Create order
Allocate
Release tasks
Optionally complete pick
Do not complete pack
Attempt ship
System rejects action
Create user issue report
Create AMS ticket if requested
```

Expected result:

```text
FAILED
```

Rules:

- do not reduce inventory
- create user report with severity `HIGH`
- ticket creation is controlled by request flag

Example user report title:

```text
User unable to ship order because pack step is incomplete
```

---

## Journey 5: Manual Functional Issue

Code:

```text
JRN-MANUAL-FUNCTIONAL-ISSUE
```

Purpose:

Represent a user-reported functional issue that is not automatically detected.

Flow:

```text
Synthetic business user submits issue report
AMS ticket may be created
```

Expected result:

```text
SUCCESS
```

Rules:

- do not force a warehouse system failure
- create a user report
- create ticket if requested

Example report:

```text
Order dashboard shows confusing fulfillment status for business user
```

This scenario is important because many real AMS tickets are not generated by monitoring; they are reported by users.

---

# Backend APIs

Create synthetic user APIs and user report APIs.

Suggested files:

```text
backend/app/models/synthetic_users.py
backend/app/models/user_reports.py
backend/app/schemas/synthetic_users.py
backend/app/schemas/user_reports.py
backend/app/services/synthetic_user_service.py
backend/app/services/user_report_service.py
backend/app/api/routes/synthetic_users.py
backend/app/api/routes/user_reports.py
```

You may organize differently if consistent with existing project style.

---

## Synthetic User APIs

Use prefix:

```text
/api/v1/synthetic-users
```

Add:

```text
GET  /api/v1/synthetic-users/users
GET  /api/v1/synthetic-users/journeys
GET  /api/v1/synthetic-users/journeys/{journey_code}
POST /api/v1/synthetic-users/journeys/{journey_code}/run
POST /api/v1/synthetic-users/run-suite
GET  /api/v1/synthetic-users/runs
GET  /api/v1/synthetic-users/runs/{run_id}
```

---

### Run Journey Request

Endpoint:

```text
POST /api/v1/synthetic-users/journeys/{journey_code}/run
```

Request:

```json
{
  "synthetic_user_id": "optional-user-uuid",
  "create_ticket": true,
  "input_payload": {}
}
```

Rules:

- if `synthetic_user_id` is omitted, select deterministic active user matching journey persona
- `create_ticket` controls whether failed user reports also create tickets
- create one `synthetic_journey_runs` row per execution
- return run result including:
  - run number
  - status
  - journey code
  - failure message if any
  - order id if any
  - user report id if any
  - ticket id if any

---

### Run Suite

Endpoint:

```text
POST /api/v1/synthetic-users/run-suite
```

Request:

```json
{
  "create_ticket": true
}
```

Behavior:

- run all enabled journeys in deterministic order
- return summary and individual run results
- do not stop the entire suite if one journey fails
- record each run

This is useful for demos.

---

### Journey Run List

Endpoint:

```text
GET /api/v1/synthetic-users/runs
```

Support optional filters:

```text
journey_code
status
synthetic_user_id
```

Return newest first.

Default limit:

```text
100
```

---

## User Report APIs

Use prefix:

```text
/api/v1/ams/user-reports
```

Add:

```text
GET  /api/v1/ams/user-reports
POST /api/v1/ams/user-reports
GET  /api/v1/ams/user-reports/{report_id}
POST /api/v1/ams/user-reports/{report_id}/create-ticket
POST /api/v1/ams/user-reports/{report_id}/acknowledge
POST /api/v1/ams/user-reports/{report_id}/resolve
```

---

### Create User Report

Endpoint:

```text
POST /api/v1/ams/user-reports
```

Request:

```json
{
  "reporter_name": "Ben Business User",
  "reporter_email": "ben.business.user@example.com",
  "reporter_persona": "BUSINESS_USER",
  "report_channel": "USER_PORTAL",
  "source_module": "WAREHOUSE_FULFILLMENT",
  "affected_entity_type": "ORDER",
  "affected_entity_id": "optional-uuid",
  "title": "Unable to ship order",
  "description": "The user tried to ship an order but the system rejected the action.",
  "business_impact": "Customer shipment is delayed.",
  "severity": "HIGH",
  "create_ticket": true
}
```

Rules:

- create user report
- if `create_ticket = true`, create linked AMS ticket
- return report and ticket summary if created

---

### Create Ticket from User Report

Endpoint:

```text
POST /api/v1/ams/user-reports/{report_id}/create-ticket
```

Rules:

- if ticket already exists for report, return existing ticket
- otherwise create AMS incident
- update user report status to `TICKET_CREATED`

---

### Acknowledge User Report

Endpoint:

```text
POST /api/v1/ams/user-reports/{report_id}/acknowledge
```

Allowed from:

```text
SUBMITTED
TICKET_CREATED
```

Result:

```text
ACKNOWLEDGED
```

Set `acknowledged_at`.

---

### Resolve User Report

Endpoint:

```text
POST /api/v1/ams/user-reports/{report_id}/resolve
```

Allowed from:

```text
SUBMITTED
TICKET_CREATED
ACKNOWLEDGED
```

Result:

```text
RESOLVED
```

Set `resolved_at`.

If linked ticket exists, do not automatically resolve the ticket unless the current AMS service already supports a clean and safe reuse of resolve logic. Avoid creating inconsistent ticket lifecycle state.

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

for invalid lifecycle transitions or unsupported journey execution states.

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
Synthetic Journeys
Journey Runs
User Reports
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
Health
About
```

---

## Required Frontend Routes

Add:

```text
/synthetic-users/journeys
/synthetic-users/runs
/ams/user-reports
/ams/user-reports/new
/ams/user-reports/:reportId
```

Existing routes must continue working.

---

## Synthetic Journeys Page

Route:

```text
/synthetic-users/journeys
```

Display:

- journey cards or table
- journey code
- name
- persona
- journey type
- expected outcome
- enabled status
- action button: `Run`
- checkbox/toggle: `Create ticket on failure`

After run:

- show run number
- status
- failure message if any
- user report link if created
- ticket link if created

Also include button:

```text
Run Full Synthetic Suite
```

---

## Journey Runs Page

Route:

```text
/synthetic-users/runs
```

Display table:

- run number
- journey
- synthetic user
- status
- failure type
- failure message
- order id/reference if available
- user report
- ticket
- started at
- completed at
- duration

Use chips for status.

---

## User Reports Page

Route:

```text
/ams/user-reports
```

Display table:

- report number
- title
- reporter
- severity
- status
- source module
- affected entity
- ticket number if linked
- submitted at

Actions:

- create ticket
- acknowledge
- resolve

Add button:

```text
Submit User Report
```

---

## New User Report Page

Route:

```text
/ams/user-reports/new
```

Simple form:

```text
reporter_name
reporter_email
reporter_persona
report_channel
affected_entity_type
affected_entity_id
title
description
business_impact
severity
create_ticket
```

On submit:

- create user report
- navigate to report detail page or user reports list

---

## User Report Detail Page

Route:

```text
/ams/user-reports/:reportId
```

Display:

- report header
- reporter details
- description
- business impact
- affected entity
- linked journey run if any
- linked ticket if any
- lifecycle timestamps

Actions:

- create ticket if no ticket exists
- acknowledge
- resolve

If a ticket exists, provide link to:

```text
/ams/tickets/:ticketId
```

---

# Frontend API Client

Create or extend typed API clients.

Suggested files:

```text
frontend/src/services/syntheticUsersApi.ts
frontend/src/services/userReportsApi.ts
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
4. Existing operations/AMS tests still pass
5. Synthetic users seed is idempotent
6. List synthetic users
7. List synthetic journeys
8. Run successful fulfillment journey
9. Run insufficient stock journey and create user report
10. Run insufficient stock journey with ticket creation
11. Run pack-before-pick journey
12. Run ship-before-pack journey
13. Run manual functional issue journey
14. Run full synthetic suite
15. Create manual user report
16. Create ticket from user report
17. Prevent duplicate ticket creation from same report
18. Acknowledge user report
19. Resolve user report
20. List journey runs
21. List user reports

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

- Prompt 05 user-driven failure scenario summary
- synthetic users
- synthetic journeys
- user-reported issues
- ticket creation from user reports
- new APIs
- new frontend routes
- seed commands
- validation commands
- backend port `8050`
- frontend port `4001`
- deferred future scenarios:
  - monitoring noise
  - observability-enabled diagnosis
  - batch failures
  - AI-native support agents

Update `ARCHITECTURE.md` with:

- synthetic user module
- synthetic journey execution flow
- user issue report module
- user report to AMS ticket flow
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
pytest
```

Then validate live backend:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/synthetic-users/users | jq .
curl -sS http://localhost:8050/api/v1/synthetic-users/journeys | jq .
curl -sS -X POST http://localhost:8050/api/v1/synthetic-users/journeys/JRN-ALLOCATE-INSUFFICIENT-STOCK/run \
  -H "Content-Type: application/json" \
  -d '{"create_ticket": true}' | jq .
curl -sS http://localhost:8050/api/v1/ams/user-reports | jq .
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
http://localhost:4001/synthetic-users/journeys
http://localhost:4001/synthetic-users/runs
http://localhost:4001/ams/user-reports
http://localhost:4001/ams/user-reports/new
```

Manual UI validation:

```text
Open Synthetic Journeys
Run Successful Fulfillment journey
Confirm run succeeds and no ticket is created
Run Insufficient Stock journey with ticket creation enabled
Confirm user report is created
Confirm AMS ticket is created
Open User Reports
Open linked report detail
Open linked AMS ticket
Acknowledge ticket
Start work
Resolve ticket
Close ticket
```

---

# Definition of Done

Prompt 05 is complete only when:

- migration exists
- `synthetic_users` exists
- `synthetic_journeys` exists
- `synthetic_journey_runs` exists
- `ams_user_reports` exists
- synthetic user seed exists and is idempotent
- synthetic users API works
- synthetic journeys API works
- run journey API works
- run suite API works
- journey run list API works
- user report create API works
- user report list/detail APIs work
- ticket creation from user report works
- duplicate tickets from the same user report are prevented
- successful fulfillment synthetic journey works
- insufficient stock synthetic journey creates user report
- pack-before-pick synthetic journey creates user report
- ship-before-pack synthetic journey creates user report
- manual functional issue journey creates user report
- linked AMS ticket lifecycle still works
- frontend synthetic journeys page works
- frontend journey runs page works
- frontend user reports page works
- frontend new user report page works
- frontend user report detail page works
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
4. Backend synthetic user APIs added
5. Backend user report APIs added
6. Frontend routes added
7. Seed command and result
8. Backend validation results
9. Frontend validation results
10. Manual synthetic journey and user-report validation result
11. Confirmation that infrastructure files were not modified
12. Any TODOs
13. Recommended Git commit message

Recommended commit message:

```text
feat: add synthetic users and user-reported issues
```

Do not proceed beyond this prompt.