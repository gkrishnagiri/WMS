# Prompt 19 – Knowledge and RAG Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

```text
Enterprise Operations Suite (EOS)
```

Prompt 18 added:

```text
Agent Chat and Case Intake Foundation
```

It created:

```text
agent cases
chat sessions
messages
orchestration runs
evidence items
action proposals
deterministic Stage 1 guidance
```

Your task now is to implement:

```text
Knowledge and RAG Foundation
```

---

## Business Goal

The agent should no longer rely only on recent tickets, alerts, batch runs, and operational evidence.

It should also be able to retrieve relevant support knowledge such as:

```text
runbooks
SOPs
known-error records
troubleshooting guides
application support notes
batch recovery procedures
inventory allocation guides
shipment integration guides
observability investigation guides
AMS operating procedures
```

This prompt should create the foundation for Retrieval-Augmented Generation, but without calling a real LLM yet.

The goal is:

```text
User / service engineer asks about an issue
        ->
Agent case intake starts
        ->
Orchestrator retrieves live evidence
        ->
Orchestrator retrieves relevant knowledge
        ->
Agent produces deterministic Stage 1 guidance using both
```

---

## Important Scope Clarification

Prompt 19 implements:

```text
knowledge base
knowledge seeding
chunking
deterministic retrieval
retrieval audit
agent integration
UI for knowledge search
```

Prompt 19 must **not** implement:

```text
real GPT model calls
external embeddings
vector database
OpenAI embeddings
Azure OpenAI embeddings
LangChain
LlamaIndex
agent frameworks
autonomous remediation
ServiceNow integration
```

This is a **RAG foundation**, not production RAG yet.

Use deterministic keyword/scored retrieval for now.

Future prompts can add:

```text
real model integration
embedding model integration
hybrid vector + keyword retrieval
reranking
citations in generated model responses
ServiceNow KB ingestion
document upload pipelines
```

---

## Current Baseline

The current system includes:

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

Prompt 18 currently has deterministic agent chat and case intake.

Current backend test baseline:

```text
115 passed
```

Do not break existing functionality.

---

## Critical Instructions

You must preserve all existing ports.

You must preserve all existing frontend and backend/BFF URLs.

You must not call any external LLM.

You must not call OpenAI, Azure OpenAI, Anthropic, local model servers, or any other model provider.

You must not introduce external embeddings.

You must not introduce a vector database.

You must not introduce LangChain, LlamaIndex, or an agent framework.

You must not introduce autonomous remediation.

You must not execute shell commands from the agent.

You must not execute remediation actions from the agent.

You must not introduce ServiceNow integration.

You must not introduce authentication or authorization.

You must not modify Docker Compose unless absolutely necessary.

You must not modify observability infrastructure unless absolutely necessary.

All retrieval must be deterministic and testable.

The UI must clearly state:

```text
Current phase: deterministic knowledge retrieval only.
No external LLM call.
No embedding model.
No autonomous remediation.
```

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

Implement a knowledge foundation that supports:

```text
knowledge source catalog
knowledge article/runbook catalog
known-error records
knowledge chunking
deterministic keyword retrieval
retrieval scoring
retrieval audit trail
agent orchestration integration
knowledge search UI
case-linked knowledge evidence
future RAG readiness
```

---

# Data Model

Add migration:

```text
0014_agent_knowledge_rag_foundation
```

Create tables similar to the following.

---

## agent_knowledge_sources

Represents a knowledge source system or curated source.

Fields:

```text
id
source_id
source_code
name
description
source_type
owner
status
created_at
updated_at
```

Source types:

```text
CURATED_RUNBOOK
SOP
KNOWN_ERROR_DB
APPLICATION_SUPPORT_NOTE
BATCH_OPERATIONS_GUIDE
OBSERVABILITY_GUIDE
AMS_PLAYBOOK
FUTURE_SERVICENOW_KB
```

Statuses:

```text
ACTIVE
INACTIVE
DRAFT
```

---

## agent_knowledge_articles

Represents a runbook, SOP, KB article, or support note.

Fields:

```text
id
article_id
source_id
article_code
title
summary
body
article_type
domain
application_area
severity_applicability
status
version
tags
created_at
updated_at
```

Article types:

```text
RUNBOOK
SOP
TROUBLESHOOTING_GUIDE
KNOWN_ERROR
RECOVERY_PROCEDURE
INVESTIGATION_GUIDE
CUSTOMER_COMMUNICATION_GUIDE
```

Domains:

```text
WAREHOUSE
INVENTORY
ORDER_FULFILLMENT
SHIPMENT
BATCH
OBSERVABILITY
MONITORING
AMS_OPERATIONS
AGENTIC_SUPPORT
```

Statuses:

```text
ACTIVE
DRAFT
RETIRED
```

---

## agent_knowledge_chunks

Represents searchable text chunks.

Fields:

```text
id
chunk_id
article_id
chunk_index
heading
chunk_text
normalized_text
token_count_estimate
keywords
created_at
updated_at
```

Use a simple deterministic chunking approach.

Suggested approach:

```text
split article body by headings or paragraphs
keep chunks small enough for future model context
store normalized lowercase text
extract simple keywords from title, heading, tags, and chunk text
```

Do not use external tokenizers.

A rough word-count estimate is enough.

---

## agent_known_errors

Represents known-error records.

Fields:

```text
id
known_error_id
error_code
title
symptoms
likely_cause
workaround
permanent_fix
affected_area
severity
status
related_article_id
created_at
updated_at
```

Statuses:

```text
ACTIVE
RETIRED
DRAFT
```

---

## agent_retrieval_queries

Represents retrieval query audit records.

Fields:

```text
id
query_id
case_id
session_id
message_id
query_text
normalized_query
retrieval_mode
top_k
created_at
```

Retrieval modes:

```text
KEYWORD_DETERMINISTIC
CASE_CONTEXT_DETERMINISTIC
FUTURE_VECTOR_DISABLED
```

---

## agent_retrieval_results

Represents retrieved knowledge items.

Fields:

```text
id
result_id
query_id
article_id
chunk_id
known_error_id
rank
score
match_reason
snippet
created_at
```

---

# Seed Knowledge Base

Add an idempotent seed module:

```text
backend/app/db/seed_agent_knowledge.py
```

Seed a practical demo knowledge base.

Minimum knowledge sources:

```text
EOS Warehouse Runbooks
EOS Batch Operations Guide
EOS Observability Investigation Guide
EOS AMS Support Playbook
EOS Known Error Records
```

Minimum articles/runbooks:

```text
Inventory Allocation Failure Runbook
Order Stuck During Fulfillment SOP
Shipment Sync Timeout Recovery Guide
Inventory Reconciliation Batch Failure Procedure
Low Stock Alert Investigation Guide
API Latency Investigation Guide
Backend/BFF Unavailable Investigation Guide
AMS Ticket Backlog Triage Playbook
User Communication Template for Fulfillment Issues
Stage 1 Agentic Support Operating Procedure
```

Minimum known errors:

```text
INV_ALLOC_SHORTAGE
SHIP_SYNC_TIMEOUT
BATCH_INV_RECON_FAIL
API_LATENCY_SPIKE
BFF_HEALTHCHECK_FAIL
AMS_BACKLOG_HIGH
```

Seed should create chunks idempotently.

Run twice during validation to confirm idempotency.

Update documentation and validation commands to include:

```bash
python -m app.db.seed_agent_knowledge
```

---

# Deterministic Retrieval Logic

Create service:

```text
backend/app/services/agent_knowledge_service.py
```

It should support:

```text
list sources
list articles
get article
list chunks
list known errors
search knowledge
retrieve for agent case
record retrieval query
record retrieval results
```

---

## Search Behavior

Implement deterministic keyword/scored retrieval.

No embeddings.

No external search service.

Suggested scoring:

```text
+ title exact/partial match
+ tag match
+ domain match
+ known error symptom match
+ keyword overlap
+ phrase match
+ linked case type boost
+ linked evidence type boost
```

Return:

```text
article title
article type
domain
chunk heading
snippet
score
match reason
known error if matched
```

Keep it simple and transparent.

---

## Search API Request

Suggested request:

```json
{
  "query": "order is stuck during fulfillment",
  "case_id": "optional",
  "session_id": "optional",
  "top_k": 5,
  "domains": ["ORDER_FULFILLMENT", "INVENTORY"],
  "include_known_errors": true
}
```

---

## Search API Response

Suggested response:

```json
{
  "query_id": "RETQ-...",
  "query": "order is stuck during fulfillment",
  "retrieval_mode": "KEYWORD_DETERMINISTIC",
  "results": [
    {
      "rank": 1,
      "score": 12.5,
      "article_id": "KB-...",
      "article_title": "Order Stuck During Fulfillment SOP",
      "article_type": "SOP",
      "domain": "ORDER_FULFILLMENT",
      "chunk_id": "KCH-...",
      "heading": "Initial Checks",
      "snippet": "Verify order status, allocation status, and fulfillment task state...",
      "match_reason": "Matched query terms: order, stuck, fulfillment"
    }
  ],
  "notes": [
    "Deterministic keyword retrieval only. No embedding model was used."
  ]
}
```

---

# Agent Orchestrator Integration

Update:

```text
backend/app/services/agent_orchestrator_service.py
```

The deterministic Stage 1 orchestrator should now retrieve knowledge.

When a user or engineer sends a message, the orchestrator should:

```text
classify issue type
retrieve live operational evidence
retrieve relevant knowledge articles/chunks/known errors
persist retrieval query/results
create agent evidence items for top knowledge results
include knowledge in the Stage 1 response
```

Add evidence type:

```text
KNOWLEDGE_ARTICLE
KNOWLEDGE_CHUNK
KNOWN_ERROR
```

If evidence type enums are constrained, add the new values safely.

---

## Stage 1 Response Update

Agent response should include:

```text
Understanding
Relevant Operational Evidence
Relevant Knowledge
Likely Cause
Recommended Next Steps
What I Cannot Do Yet
```

Example:

```text
Understanding:
You are reporting an order fulfillment issue.

Relevant Operational Evidence:
- Found 1 recent failed inventory reconciliation batch run.
- Found 2 open AMS tickets.

Relevant Knowledge:
- Order Stuck During Fulfillment SOP
- Inventory Allocation Failure Runbook
- Known Error INV_ALLOC_SHORTAGE

Likely Cause:
The issue may be related to inventory allocation or a recent reconciliation failure.

Recommended Next Steps:
1. Verify order status and allocation status.
2. Check available inventory for the requested item.
3. Review the latest inventory reconciliation batch run.
4. Follow the Inventory Allocation Failure Runbook.
5. Create or update the AMS ticket if fulfillment is blocked.

What I Cannot Do Yet:
This agent is currently Stage 1 read-only. It cannot execute remediation actions.
No external LLM was used to generate this guidance.
```

---

# Backend APIs

Add route prefix:

```text
/api/v1/agent-knowledge
```

Expose on:

```text
Full backend 8050
Operations BFF 8062
Agentic BFF 8065
```

Optional limited exposure on Business BFF:

```text
search only for user-facing help articles
```

Do not expose on Simulation BFF.

Do not expose on Observability BFF unless needed.

---

## Required endpoints

```text
GET  /api/v1/agent-knowledge/summary

GET  /api/v1/agent-knowledge/sources
GET  /api/v1/agent-knowledge/articles
GET  /api/v1/agent-knowledge/articles/{article_id}
GET  /api/v1/agent-knowledge/known-errors
GET  /api/v1/agent-knowledge/known-errors/{known_error_id}

POST /api/v1/agent-knowledge/search

GET  /api/v1/agent-knowledge/retrieval-queries
GET  /api/v1/agent-knowledge/retrieval-queries/{query_id}
```

Optional:

```text
POST /api/v1/agent-knowledge/cases/{case_id}/retrieve
```

---

# BFF Route Exposure

## Full backend

Expose:

```text
/api/v1/agent-knowledge/*
```

## Agentic BFF

Expose:

```text
/api/v1/agent-knowledge/*
```

## Operations BFF

Expose:

```text
/api/v1/agent-knowledge/*
```

## Business BFF

Expose either:

```text
/api/v1/agent-knowledge/summary
/api/v1/agent-knowledge/search
```

or do not expose.

If Business UI uses knowledge search for user help, expose limited search.

Do not expose article management or retrieval audit internals to Business BFF if route-level filtering is simple.

## Simulation BFF

Should return 404 for:

```text
/api/v1/agent-knowledge/summary
```

## Observability BFF

Should return 404 unless needed.

---

# Frontend UI

Add knowledge UI primarily to the Agentic and Operations experiences.

Suggested files:

```text
frontend/src/services/agentKnowledgeApi.ts
frontend/src/pages/AgentKnowledgePages.tsx
```

## Routes

```text
/agent-knowledge
/agent-knowledge/search
/agent-knowledge/articles
/agent-knowledge/articles/:articleId
/agent-knowledge/known-errors
/agent-knowledge/retrieval-queries
/agent-knowledge/retrieval-queries/:queryId
```

Visible in:

```text
full
operations
agentic
```

Optional limited user help search in:

```text
business
```

Do not show in:

```text
simulation
observability
```

---

## UI Features

The Agentic/Operations knowledge UI should support:

```text
summary cards
search box
search result list
article catalog
article detail
known-error list
retrieval query audit list
retrieval query detail
```

The UI must clearly label:

```text
Deterministic keyword retrieval only.
No external LLM call.
No embedding model.
```

---

# Agent Chat UI Integration

Update the Agent Chat session/case detail pages to show:

```text
Relevant Knowledge
Retrieved Articles
Known Errors
Retrieval Query IDs
```

When a message is sent and the agent responds, the user should be able to see knowledge evidence linked to the case.

Do not implement streaming.

Do not implement model citations yet beyond deterministic retrieved article names/snippets.

---

# Demo Control Integration

Update demo control components/readiness to include:

```text
Agent Knowledge
Deterministic Retrieval
RAG Foundation
```

Add readiness endpoint check:

```text
http://localhost:8050/api/v1/agent-knowledge/summary
```

Do not add start/stop controls.

---

# Tests

Add backend tests for:

```text
knowledge seed idempotency
list knowledge sources
list articles
get article
list known errors
get known error
search returns relevant runbook for order stuck
search returns relevant known error for allocation shortage
retrieval query/result audit records are created
agent orchestrator includes knowledge evidence
agent response includes Relevant Knowledge section
BFF exposure
Simulation BFF does not expose agent knowledge
demo control includes agent knowledge readiness
```

Tests must not require external LLMs.

Tests must not require embeddings.

Tests must not require Prometheus/Grafana/Tempo/Loki to be live.

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
python -m app.db.seed_agent_knowledge
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

## Summary

```bash
curl -sS http://localhost:8050/api/v1/agent-knowledge/summary | jq .
curl -sS http://localhost:8065/api/v1/agent-knowledge/summary | jq .
```

## Sources and articles

```bash
curl -sS http://localhost:8050/api/v1/agent-knowledge/sources | jq .
curl -sS http://localhost:8050/api/v1/agent-knowledge/articles | jq .
curl -sS http://localhost:8050/api/v1/agent-knowledge/known-errors | jq .
```

## Search

```bash
curl -sS -X POST http://localhost:8050/api/v1/agent-knowledge/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "order is stuck during fulfillment and inventory allocation failed",
    "top_k": 5,
    "include_known_errors": true
  }' | jq .
```

Expected:

```text
Order Stuck During Fulfillment SOP
Inventory Allocation Failure Runbook
INV_ALLOC_SHORTAGE or related known error
```

## Agent chat with knowledge retrieval

```bash
curl -sS -X POST http://localhost:8065/api/v1/agent-chat/intake/engineer-investigation \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Investigate stuck order and allocation issue",
    "description": "Service engineer wants the agent to use operational evidence and knowledge.",
    "initial_message": "Order is stuck during fulfillment and inventory allocation appears to have failed. What should I check?"
  }' | jq .
```

Then inspect returned case/session:

```bash
curl -sS http://localhost:8065/api/v1/agent-chat/cases/<CASE_ID>/evidence | jq .
curl -sS http://localhost:8050/api/v1/agent-knowledge/retrieval-queries | jq .
```

Expected:

```text
knowledge evidence items exist
retrieval query audit exists
agent response includes Relevant Knowledge
```

## BFF exposure

```bash
curl -sS http://localhost:8062/api/v1/agent-knowledge/summary | jq .
curl -sS http://localhost:8065/api/v1/agent-knowledge/summary | jq .
curl -i -sS http://localhost:8063/api/v1/agent-knowledge/summary | head
curl -i -sS http://localhost:8064/api/v1/agent-knowledge/summary | head
```

Expected:

```text
Operations BFF: works
Agentic BFF: works
Simulation BFF: 404
Observability BFF: 404 unless intentionally exposed
```

---

# Manual UI Validation

Open:

```text
http://localhost:4015/agent-knowledge
http://localhost:4015/agent-knowledge/search
http://localhost:4015/agent-knowledge/articles
http://localhost:4015/agent-knowledge/known-errors
http://localhost:4015/agent-knowledge/retrieval-queries
```

Validate:

```text
summary loads
search works
articles load
article detail loads
known errors load
retrieval audit loads
no external LLM / no embedding model banner is visible
```

Open Operations UI:

```text
http://localhost:4012/agent-knowledge/search
```

Validate:

```text
service engineer can search runbooks and known errors
```

Open Agent Chat:

```text
http://localhost:4015/agent-chat/engineer
```

Validate:

```text
agent response includes relevant knowledge
case evidence includes knowledge evidence
```

---

# Documentation Updates

Update `README.md` with:

```text
Agent Knowledge routes
seed command
manual validation commands
knowledge UI locations
deterministic retrieval explanation
future RAG direction
no external LLM
no embeddings
no vector DB
```

Update `ARCHITECTURE.md` with:

```text
knowledge/RAG foundation architecture
knowledge source/article/chunk model
known-error model
retrieval query/result audit model
agent orchestrator integration
future hybrid RAG architecture
future real-model integration point
```

Document clearly:

```text
Prompt 19 implements deterministic retrieval and RAG foundation only.
It does not call real LLMs.
It does not create embeddings.
It does not use a vector database.
It does not execute remediation.
```

---

# Definition of Done

Prompt 19 is complete only when:

- knowledge source model exists
- knowledge article model exists
- knowledge chunk model exists
- known-error model exists
- retrieval query/result audit exists
- seed_agent_knowledge is idempotent
- deterministic retrieval works
- search APIs exist
- article/known-error APIs exist
- agent orchestrator retrieves knowledge
- agent case evidence includes knowledge evidence
- agent response includes Relevant Knowledge section
- Agentic UI has knowledge pages
- Operations UI has knowledge pages
- Agent Chat UI shows knowledge evidence
- demo control includes agent knowledge readiness
- backend tests pass
- frontend build passes
- demo stack validation passes
- no real LLM call is introduced
- no embedding model is introduced
- no vector DB is introduced
- no ServiceNow integration is introduced
- no authentication is introduced
- no autonomous remediation is introduced
- Docker Compose unchanged unless justified
- observability infrastructure unchanged unless justified
- README updated
- ARCHITECTURE.md updated
- Prompt 19 document saved

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Migration summary
4. Knowledge data model summary
5. Seeded sources/articles/known errors
6. Deterministic retrieval behavior
7. Retrieval audit behavior
8. Agent orchestrator integration summary
9. Agent response changes
10. Backend APIs added
11. BFF exposure summary
12. Frontend routes added
13. Demo control integration summary
14. Backend test results
15. Frontend build results
16. Demo stack validation results
17. Manual API validation results
18. Manual UI validation results
19. Confirmation no real LLM call was introduced
20. Confirmation no embeddings/vector DB were introduced
21. Confirmation no remediation execution was introduced
22. Confirmation no ServiceNow/authentication/autonomous remediation was introduced
23. TODOs or limitations
24. Recommended Git commit message

Recommended commit message:

```text
feat: add agent knowledge rag foundation
```

Do not proceed beyond this prompt.