# Prompt 25 — Agentic Demo Scenario Orchestration and Guided Storylines

Implemented the presenter-controlled guided demo foundation for EOS.

- Added four deterministic scenario catalog entries and migration `0017_demo_scenario_orch`.
- Added scenario runs, ordered presenter steps, linked artifacts, and scenario timeline events.
- Added safe local induction for fulfillment, batch, user-report, and alert-noise storylines.
- Added Full/Operations/Simulation/Agentic scenario APIs, with Business catalog/summary read-only exposure.
- Added `/demo-scenarios`, run list, and run detail UI with talking points, deep links, advance, complete, and reset controls.
- Linked agent investigation workspaces back to their scenario run.
- Added scenario readiness checks and backend coverage.

Safety boundary: scenarios use deterministic local EOS data only. Starting or
advancing a run never calls the real model, approves or executes actions, sends
communications, posts to ServiceNow, runs shell/SQL/code, or performs
autonomous remediation. Reset retains shared operational and audit history.
