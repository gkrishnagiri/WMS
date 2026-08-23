# Prompt 14 – Experience Segregation Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 13 added the local observability stack with OpenTelemetry Collector, Tempo, Loki, Prometheus, Grafana, dashboards, and backend OpenTelemetry export.

Your task now is to implement:

```text
Experience Segregation Foundation
```

The goal is to split the current single EOS frontend into distinct demo experiences running at separate URLs.

This is the first step toward the eventual architecture where business application, operations console, simulation/fault-injection lab, observability platform control plane, and agentic support system each have their own UI and backend boundary.

---

## Business Goal

The demo should clearly show customers that EOS is not one monolithic screen.

The demo should show separate experiences:

```text
1. Business Application
2. Operations Console
3. Simulation and Fault Injection Lab
4. Observability Control Plane
5. Agentic Support Console
```

This supports the target story:

```text
Existing enterprise application
        +
Operations/AMS console
        +
Synthetic users and controlled failure testing
        +
Observability platform
        +
Agentic support system
```

The split should make it easy to show multiple browser windows side by side.

---

## Important Architectural Clarification

Prompt 14 should split the **frontend experience and URL model first**.

Do not physically split the backend into independent services yet.

The current backend on port `8050` should remain the shared platform API for now.

Prompt 15 will introduce backend boundary/BFF separation.

Reason:

```text
Prompt 14: separate screens and demo experiences
Prompt 15: separate backend/BFF boundaries
```

This reduces risk and avoids breaking the already working backend and tests.

---

## Current Confirmed Baseline

The repository currently has:

- FastAPI backend on port `8050`
- React/Vite frontend on port `4001`
- PostgreSQL on host port `15432`
- Redis on host port `6379`
- Prometheus on port `9090`
- Grafana on port `3001`
- Tempo on port `3200`
- Loki on port `3100`
- OpenTelemetry Collector on ports `4317`, `4318`, `8889`, `13133`
- Runtime observability middleware
- OpenTelemetry export
- Warehouse business app functionality
- AMS operations functionality
- Synthetic user journeys
- Batch simulations
- Monitoring simulations
- Observability pages
- Copilot and governed AI mock provider pages

Recent committed capabilities include:

```text
feat: add runtime observability instrumentation foundation
feat: add local observability stack expansion
```

Use the current repository structure and coding patterns.

Do not redesign prior prompt output.

---

## Critical Instructions

You must not redesign the project.

You must not rename the application.

You must preserve backend port `8050`.

You must preserve frontend port `4001`.

You must preserve observability ports:

```text
Grafana 3001
Prometheus 9090
Tempo 3200
Loki 3100
OpenTelemetry Collector 4317/4318/8889/13133
```

You must preserve existing APIs and routes.

You must preserve the current full EOS frontend behavior on port `4001` unless explicitly stated.

You must not introduce new frameworks.

You must not introduce new backend services in this prompt.

You must not introduce ServiceNow integration.

You must not introduce external LLM integration.

You must not break Prompt 13 observability stack.

If something is unclear, leave a TODO comment instead of inventing architecture.

---

## Files You May Modify

You may modify:

```text
frontend/
backend/
README.md
ARCHITECTURE.md
docs/06_Codex/
scripts/
```

You may modify package scripts if needed.

You may add frontend environment examples.

You may add startup scripts.

Do not modify local runtime files:

```text
backend/.env
backend/.venv/
frontend/.env
frontend/node_modules/
frontend/dist/
```

Avoid modifying Docker Compose in this prompt unless absolutely necessary.

---

# Target Experience URLs

Implement support for the following frontend experience modes.

## Existing Full Demo UI

Keep the existing frontend available:

```text
http://localhost:4001
```

Purpose:

```text
Full integrated EOS demo UI
```

This should remain available for regression and fallback.

---

## Business Application UI

Add a business-only frontend experience:

```text
http://localhost:4011
```

Purpose:

```text
Warehouse & Fulfillment business application
```

Should show only:

```text
Dashboard / Business Home
Warehouse
Inventory
Orders
Fulfillment Tasks
Shipments
Inventory Transactions
Health
About
```

Should not show:

```text
AMS Tickets
Operations Exceptions
Synthetic Journeys
Monitoring
Observability
Batch Simulations
Copilot
AI Config
```

This represents the normal enterprise application user experience.

---

## Operations Console UI

Add operations console experience:

```text
http://localhost:4012
```

Purpose:

```text
AMS / support operations console
```

Should show:

```text
Operations Exceptions
AMS Tickets
User Reports
Monitoring Alerts
Monitoring Triage
Batch Runs
Observability Diagnostics
Copilot Sessions, if useful for support engineer workflow
Health
About
```

Should not show normal business application workflow pages unless linked as context.

This represents the AMS/support engineer console.

---

## Simulation and Fault Injection Lab UI

Add simulation lab experience:

```text
http://localhost:4013
```

Purpose:

```text
Synthetic users, batch simulations, monitoring simulations, and controlled failure tests
```

Should show:

```text
Synthetic Journeys
Journey Runs
Batch Simulations
Batch Jobs
Batch Runs
Monitoring Simulations
Observability Simulations, if currently available
Runtime test/probe actions, if useful
Health
About
```

Should clearly label that this is a lab/test console.

This represents the controlled demo environment where failures are induced.

---

## Observability Control Plane UI

Add observability control plane experience:

```text
http://localhost:4014
```

Purpose:

```text
EOS observability control plane and links to Grafana/Prometheus/Tempo/Loki
```

Should show:

```text
Runtime Observability
Runtime Traces
Observability Stack
Observability Stack Health
Observability Stack Test
Dashboards
Traces
Logs
Metrics
Diagnostics
Health
About
```

Should prominently link to:

```text
Grafana      http://localhost:3001
Prometheus  http://localhost:9090
Tempo       http://localhost:3200
Loki        http://localhost:3100
```

Important:

Grafana is the primary observability UI.

The EOS observability control plane is only for:

```text
stack health
test telemetry
correlation helper views
runtime trace helper views
demo navigation
```

It should not try to replace Grafana.

---

## Agentic Support Console UI

Add agentic support console experience:

```text
http://localhost:4015
```

Purpose:

```text
Copilot, governed AI, and future agentic support workflows
```

Should show:

```text
Copilot
Copilot Sessions
Copilot Analyze
AI Config
AI Invocations
AI Safety
AI Usage
AI Test
Future Agents placeholder
Health
About
```

Should clearly label current status:

```text
Current phase uses governed deterministic mock AI only.
No autonomous remediation is enabled yet.
No external LLM call is made yet.
```

This represents the future agentic AMS system.

---

# Implementation Strategy

Do not duplicate the entire frontend application.

Use the existing React/Vite frontend and add an **experience mode** mechanism.

The same frontend codebase should be launchable in different modes using environment variables.

Suggested environment variable:

```text
VITE_EOS_EXPERIENCE
```

Allowed values:

```text
full
business
operations
simulation
observability
agentic
```

Suggested display names:

```text
full          Enterprise Operations Suite
business      EOS Business Application
operations    EOS Operations Console
simulation    EOS Simulation Lab
observability EOS Observability Control Plane
agentic       EOS Agentic Support Console
```

The frontend should:

1. Detect `VITE_EOS_EXPERIENCE`
2. Filter navigation items by experience
3. Restrict default landing page by experience
4. Show experience-specific home/landing content
5. Avoid showing irrelevant routes in navigation
6. Preserve existing routes for the full demo UI
7. Avoid breaking deep links where possible

---

# Frontend Experience Configuration

Create a centralized frontend config file, for example:

```text
frontend/src/config/experience.ts
```

It should define:

```text
experience code
display name
description
default route
navigation groups
enabled route prefixes
external links
warning/helper text
```

Suggested route ownership:

## Business

```text
/
/warehouse
/warehouse/inventory
/warehouse/orders
/warehouse/tasks
/warehouse/shipments
/warehouse/inventory-transactions
/health
/about
```

## Operations

```text
/operations
/operations/exceptions
/ams/tickets
/ams/user-reports
/monitoring/alerts
/monitoring/triage
/observability/diagnostics
/batch/runs
/copilot/sessions
/health
/about
```

## Simulation

```text
/synthetic-users/journeys
/synthetic-users/runs
/batch/simulations
/batch/jobs
/batch/runs
/monitoring/simulations
/observability/simulations
/observability/stack/test
/health
/about
```

## Observability

```text
/observability
/observability/runtime
/observability/runtime/traces
/observability/traces
/observability/logs
/observability/metrics
/observability/diagnostics
/observability/stack
/observability/stack/health
/observability/stack/test
/observability/dashboards
/health
/about
```

## Agentic

```text
/copilot
/copilot/sessions
/copilot/analyze
/ai-config
/ai-config/providers
/ai-config/prompts
/ai-config/safety
/ai-config/invocations
/ai-config/usage
/ai-config/test
/agentic
/health
/about
```

---

# Experience Landing Pages

Add experience-aware landing behavior.

When an experience starts, `/` should show a landing page appropriate to that experience.

Suggested component:

```text
frontend/src/pages/ExperienceHomePage.tsx
```

Content should vary by mode.

## Business home

Explain:

```text
This is the business-facing Warehouse & Fulfillment application.
Support, simulation, observability, and agentic controls are intentionally hidden.
```

Cards:

```text
Warehouse
Inventory
Orders
Fulfillment Tasks
Shipments
```

## Operations home

Explain:

```text
This is the AMS operations console for support engineers.
It consolidates tickets, exceptions, monitoring alerts, triage, diagnostics, and batch failures.
```

Cards:

```text
AMS Tickets
Operations Exceptions
Monitoring Alerts
Monitoring Triage
Batch Runs
Diagnostics
```

## Simulation home

Explain:

```text
This lab generates controlled user journeys, batch failures, monitoring alert storms, and observability evidence for demos and testing.
```

Cards:

```text
Synthetic Journeys
Batch Simulations
Monitoring Simulations
Observability Simulations
Runtime Stack Test
```

## Observability home

Explain:

```text
This is the EOS observability control plane. Grafana remains the primary observability UI.
```

Cards/links:

```text
Runtime Observability
Runtime Traces
Stack Health
Stack Test
Grafana
Prometheus
Tempo
Loki
```

## Agentic home

Explain:

```text
This is the governed AI and future agentic support console.
Current phase uses deterministic mock AI and human-approved recommendations only.
```

Cards:

```text
Copilot
Copilot Analyze
AI Config
AI Invocations
AI Safety
Future Agents
```

---

# Navigation Filtering

Update the existing app shell navigation.

Navigation must be generated from a single registry that supports experience filtering.

Suggested file:

```text
frontend/src/config/navigation.ts
```

Each navigation item should include:

```text
label
path
icon if applicable
experience list
group
external flag if applicable
```

The `full` experience should show all existing navigation.

Each specialized experience should only show its relevant items.

---

# Route Access Behavior

Implement light route access handling.

If the user opens a route that is not part of the current experience:

- Do not crash.
- Show a friendly page:

```text
This page belongs to another EOS experience.
```

- Provide links to the correct experience if configured.

Suggested component:

```text
frontend/src/pages/ExperienceBoundaryPage.tsx
```

Do not implement authentication or authorization in this prompt.

This is demo experience segregation, not security.

---

# Startup Scripts

Add scripts to start the frontend in each experience mode.

Do not remove existing frontend start behavior.

Suggested scripts:

```text
frontend/start_full_frontend.sh
frontend/start_business_frontend.sh
frontend/start_operations_frontend.sh
frontend/start_simulation_frontend.sh
frontend/start_observability_frontend.sh
frontend/start_agentic_frontend.sh
```

Ports:

```text
full          4001
business      4011
operations    4012
simulation    4013
observability 4014
agentic       4015
```

Each script should:

```text
set VITE_EOS_EXPERIENCE
set VITE_API_BASE_URL=http://localhost:8050
start Vite on the appropriate host/port
```

Use project style consistent with existing `start_frontend.sh`.

Also update `frontend/package.json` scripts if useful:

```text
dev:full
dev:business
dev:operations
dev:simulation
dev:observability
dev:agentic
```

Do not require all frontends to run during tests.

---

# Optional Root Scripts

If root scripts exist, update or create:

```text
scripts/start-experiences.sh
scripts/stop-experiences.sh
```

These may start/stop multiple frontend experience processes using PID files under `/tmp`.

This is optional.

If implemented, keep it simple and safe.

Do not make normal validation depend on running all frontend modes simultaneously.

---

# Backend Changes

Backend changes should be minimal.

Do not split backend services in this prompt.

Add an experience metadata endpoint if useful:

```text
GET /api/v1/platform/experiences
```

Return:

```json
[
  {
    "code": "business",
    "name": "EOS Business Application",
    "frontend_url": "http://localhost:4011",
    "backend_url": "http://localhost:8050",
    "description": "Business-facing warehouse and fulfillment application."
  }
]
```

Optional route:

```text
GET /api/v1/platform/summary
```

This can describe current platform topology.

If backend route addition is not needed, skip it and keep Prompt 14 frontend-only.

---

# Future Backend Boundary Documentation

Update architecture documentation to show the intended future split.

Target future architecture:

```text
Business Application
  Frontend: business app UI
  Backend: business app API

Operations Console
  Frontend: support operations UI
  Backend/BFF: operations API
  Future: ServiceNow integration

Simulation Lab
  Frontend: simulation/fault-injection UI
  Backend/BFF: simulation API

Observability Control Plane
  Frontend: observability control UI
  Backend/BFF: observability API
  External UI: Grafana
  Possible future: Azure Monitor adapter

Agentic Support Console
  Frontend: agentic support UI
  Backend/BFF: agent orchestration API
```

Important note:

```text
Prompt 14 implements frontend experience segregation only.
Prompt 15 should introduce backend boundary/BFF segregation.
```

---

# Azure and Observability Notes

Add documentation, not implementation.

Document that future Azure deployment can follow one of two paths:

## Option A – Azure-native observability

```text
Azure Monitor
Application Insights
Log Analytics
Managed Grafana if desired
```

## Option B – Open-source observability stack on Azure

```text
Grafana
Prometheus
Tempo
Loki
OpenTelemetry Collector
```

Do not make a final production choice in this prompt.

Do not include pricing claims beyond:

```text
Open-source components may not have license fees, but Azure compute, storage, networking, and managed services still have infrastructure costs.
```

---

# Frontend Tests / Build

Do not add heavy frontend tests.

Ensure:

```bash
cd frontend
npm run build
```

passes.

If possible, validate each experience mode build/start script minimally.

---

# Backend Tests

If adding backend platform endpoints, add tests for:

```text
GET /api/v1/platform/experiences
GET /api/v1/platform/summary
```

Existing tests must continue to pass.

Run:

```bash
cd backend
source .venv/bin/activate
pytest
```

---

# Validation Commands

Run backend validation:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
python -m app.db.seed_batch
python -m app.db.seed_copilot
python -m app.db.seed_ai_config
pytest
```

Run frontend validation:

```bash
cd frontend
npm install
npm run build
```

Validate each frontend mode can start.

Example:

```bash
cd frontend

VITE_EOS_EXPERIENCE=business VITE_API_BASE_URL=http://localhost:8050 npm run dev -- --host 0.0.0.0 --port 4011
```

Then open:

```text
http://localhost:4011
```

Repeat for:

```text
http://localhost:4012
http://localhost:4013
http://localhost:4014
http://localhost:4015
```

Or use the provided start scripts.

---

# Manual UI Validation

Validate:

## Full UI

```text
http://localhost:4001
```

Expected:

```text
All existing demo navigation remains available.
```

## Business UI

```text
http://localhost:4011
```

Expected:

```text
Only business/warehouse functionality is visible.
No AMS, observability, simulation, copilot, or AI config navigation.
```

## Operations UI

```text
http://localhost:4012
```

Expected:

```text
Support operations navigation is visible.
Business workflow and simulation lab navigation are hidden.
```

## Simulation Lab UI

```text
http://localhost:4013
```

Expected:

```text
Synthetic journeys, batch simulations, monitoring simulations, and related lab controls are visible.
```

## Observability Control Plane UI

```text
http://localhost:4014
```

Expected:

```text
Runtime observability, stack health, stack tests, dashboards, traces/logs/metrics links are visible.
Grafana/Prometheus/Tempo/Loki links are available.
```

## Agentic Support Console UI

```text
http://localhost:4015
```

Expected:

```text
Copilot, governed AI, AI config, AI invocation, AI safety, and future agents placeholder are visible.
Clear note says mock AI only and no autonomous remediation yet.
```

---

# Definition of Done

Prompt 14 is complete only when:

- `VITE_EOS_EXPERIENCE` is supported
- full mode continues to work
- business mode works
- operations mode works
- simulation mode works
- observability mode works
- agentic mode works
- navigation is filtered by experience
- experience-specific landing page works
- route boundary page exists or unsupported routes are handled gracefully
- frontend start scripts exist for each mode
- frontend build passes
- backend tests pass
- existing backend API remains on port `8050`
- existing full frontend remains on port `4001`
- business frontend can run on `4011`
- operations frontend can run on `4012`
- simulation frontend can run on `4013`
- observability frontend can run on `4014`
- agentic frontend can run on `4015`
- README updated
- ARCHITECTURE.md updated
- Prompt 14 document saved
- Docker Compose is not unnecessarily modified
- no external LLM integration introduced
- no ServiceNow integration introduced
- Prompt 13 observability stack remains intact

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Experience modes implemented
4. Frontend routes/URLs by experience
5. Startup scripts added
6. Backend changes, if any
7. Backend validation results
8. Frontend validation results
9. Manual UI validation results for all experience URLs
10. Confirmation existing full UI still works on `4001`
11. Confirmation backend remains on `8050`
12. Confirmation Prompt 13 observability stack remains intact
13. Confirmation no external LLM or ServiceNow integration was introduced
14. Any TODOs or limitations
15. Recommended Git commit message

Recommended commit message:

```text
feat: add experience segregation foundation
```

Do not proceed beyond this prompt.