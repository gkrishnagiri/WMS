"""Idempotent seed for the curated EOS agent knowledge base."""

from __future__ import annotations

import re

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.models.agent_knowledge import AgentKnowledgeArticle, AgentKnowledgeChunk, AgentKnowledgeSource, AgentKnownError


SOURCES = [
    ("EOS-WAREHOUSE-RUNBOOKS", "EOS Warehouse Runbooks", "Curated procedures for warehouse and fulfillment support.", "CURATED_RUNBOOK", "Warehouse Platform Support"),
    ("EOS-BATCH-GUIDE", "EOS Batch Operations Guide", "Operational procedures for scheduled and manually simulated batch jobs.", "BATCH_OPERATIONS_GUIDE", "Batch Operations"),
    ("EOS-OBSERVABILITY-GUIDE", "EOS Observability Investigation Guide", "Guidance for correlating runtime telemetry and alert evidence.", "OBSERVABILITY_GUIDE", "Observability Engineering"),
    ("EOS-AMS-PLAYBOOK", "EOS AMS Support Playbook", "Support operating procedures for intake, triage, and communication.", "AMS_PLAYBOOK", "AMS Operations"),
    ("EOS-KNOWN-ERRORS", "EOS Known Error Records", "Curated known-error references for repeatable EOS symptoms.", "KNOWN_ERROR_DB", "Application Support"),
]


ARTICLES = [
    ("KB-INV-ALLOC-FAIL", "Inventory Allocation Failure Runbook", "Checks for shortages, reservations, and allocation validation failures.", "RUNBOOK", "INVENTORY", "Warehouse & Fulfillment", "HIGH,CRITICAL", ["inventory", "allocation", "shortage", "reservation"], "Initial Checks\nVerify available inventory, reserved quantity, item status, and the fulfillment task state. Confirm the requested quantity does not exceed allocatable stock.\n\nEvidence Review\nReview allocation events, inventory transactions, and any linked user report or AMS ticket. Compare the requested quantity with the latest inventory balance.\n\nEscalation\nIf inventory is available but allocation still fails, capture the item, order, warehouse, and error code before escalating to warehouse platform support."),
    ("KB-ORDER-STUCK", "Order Stuck During Fulfillment SOP", "A business-facing procedure for an order that cannot progress through fulfillment.", "SOP", "ORDER_FULFILLMENT", "Warehouse & Fulfillment", "MEDIUM,HIGH", ["order", "stuck", "fulfillment", "allocation", "task"], "Initial Checks\nVerify order status, allocation status, fulfillment task state, and the latest order event. Confirm the order has not already been shipped or cancelled.\n\nCustomer Impact\nRecord the order number, affected line, requested ship date, and business impact. Avoid changing order data while the issue is under investigation.\n\nSupport Handoff\nLink the supporting evidence to an AMS ticket when fulfillment is blocked and provide the next expected update time."),
    ("KB-SHIP-SYNC-TIMEOUT", "Shipment Sync Timeout Recovery Guide", "Read-only investigation and human-approved recovery guidance for delayed carrier status synchronization.", "RECOVERY_PROCEDURE", "SHIPMENT", "Shipment Status Synchronization", "MEDIUM,HIGH", ["shipment", "sync", "timeout", "carrier", "delayed"], "Initial Checks\nConfirm shipment status, carrier reference, last successful synchronization time, and whether the shipment is still open.\n\nEvidence Review\nReview batch step events, runtime latency, and any monitoring or observability alert related to carrier synchronization.\n\nRecovery Decision\nDo not rerun or alter shipment data automatically. A service engineer should confirm the retry safety and document the decision."),
    ("KB-BATCH-INV-RECON", "Inventory Reconciliation Batch Failure Procedure", "Procedure for investigating a failed inventory reconciliation batch run.", "RECOVERY_PROCEDURE", "BATCH", "Nightly Inventory Reconciliation", "HIGH,CRITICAL", ["batch", "inventory", "reconciliation", "failed", "negative"], "Failed Step Review\nReview the failed step, failure type, records processed, records succeeded, records failed, and lifecycle events.\n\nData Validation\nCheck for negative available quantity, stale inventory transactions, and variance evidence. Link the operational exception, alert, ticket, or diagnostic case when present.\n\nRerun Safety\nA rerun is not automatic. Confirm idempotency, source data freshness, and approval with batch operations before taking action."),
    ("KB-LOW-STOCK-ALERT", "Low Stock Alert Investigation Guide", "Guide for validating low-stock signals and their business impact.", "INVESTIGATION_GUIDE", "INVENTORY", "Inventory Monitoring", "MEDIUM,HIGH", ["low", "stock", "alert", "reorder", "inventory"], "Signal Validation\nConfirm the item, warehouse, available quantity, reorder point, and alert occurrence history.\n\nBusiness Review\nCheck open orders, allocations, and expected replenishment before communicating an impact.\n\nNext Step\nDocument the evidence and route the issue to the inventory owner; do not modify balances from the support chat."),
    ("KB-API-LATENCY", "API Latency Investigation Guide", "A deterministic checklist for slow EOS APIs and elevated runtime latency.", "INVESTIGATION_GUIDE", "OBSERVABILITY", "EOS Backend API", "MEDIUM,HIGH", ["api", "latency", "slow", "runtime", "trace", "span"], "Measure\nConfirm the route, duration, status code, correlation ID, and slow-request threshold.\n\nCorrelate\nReview runtime traces, spans, logs, metrics, database probe spans, and Redis evidence for the same request.\n\nCommunicate\nSummarize observed facts separately from the hypothesis and provide a human-owned next investigation step."),
    ("KB-BFF-UNAVAILABLE", "Backend/BFF Unavailable Investigation Guide", "Checks for unavailable EOS backend and experience-specific BFF health endpoints.", "INVESTIGATION_GUIDE", "OBSERVABILITY", "EOS Backend Boundaries", "HIGH,CRITICAL", ["backend", "bff", "unavailable", "healthcheck", "health", "boundary"], "Availability Check\nCheck the expected health endpoint and record the HTTP result, experience, request ID, and correlation ID.\n\nScope\nDetermine whether the full backend or one experience BFF is affected. Review recent runtime error traces and collector health where available.\n\nEscalation\nOpen or update an AMS ticket with the affected URL and observed time. No process restart is performed by the agent."),
    ("KB-AMS-BACKLOG", "AMS Ticket Backlog Triage Playbook", "A support-operations playbook for prioritizing an expanding AMS queue.", "SOP", "AMS_OPERATIONS", "AMS Support", "MEDIUM,HIGH", ["ams", "ticket", "backlog", "triage", "queue"], "Queue Review\nReview open ticket count, priority, age, source module, and duplicate signals.\n\nPrioritize\nGroup related alerts, batch failures, and user reports before assigning human ownership.\n\nStatus Update\nUse a customer-safe summary that acknowledges impact without exposing internal credentials or unverified root cause."),
    ("KB-CUSTOMER-FULFILLMENT-UPDATE", "User Communication Template for Fulfillment Issues", "Customer-safe language for acknowledging a fulfillment investigation.", "CUSTOMER_COMMUNICATION_GUIDE", "AMS_OPERATIONS", "Customer Support", "MEDIUM,HIGH", ["customer", "communication", "fulfillment", "update", "impact"], "Acknowledgement\nAcknowledge the reported fulfillment impact and identify the affected order or shipment without exposing internal implementation details.\n\nInvestigation Status\nState that the support team is reviewing order, inventory, shipment, and operational evidence. Do not state an unconfirmed root cause as fact.\n\nNext Update\nProvide the next expected update time and the support channel for follow-up."),
    ("KB-STAGE1-AGENT", "Stage 1 Agentic Support Operating Procedure", "Operating boundaries for deterministic read-only agent guidance.", "INVESTIGATION_GUIDE", "AGENTIC_SUPPORT", "Agentic Support", "ALL", ["stage", "agent", "read-only", "guidance", "approval", "remediation"], "Allowed Behavior\nThe Stage 1 agent may classify an issue, retrieve curated knowledge and live read-only evidence, and provide transparent next steps.\n\nProhibited Behavior\nThe agent does not call an external model, execute shell commands, change business data, close tickets, resolve alerts, send messages, or rerun batches.\n\nHuman Handoff\nA support engineer reviews all guidance and performs any operational action through the existing governed workflow."),
]


KNOWN_ERRORS = [
    ("KERR-INV-ALLOC-SHORTAGE", "INV_ALLOC_SHORTAGE", "Inventory allocation shortage", "Allocation fails or an order remains stuck when requested quantity exceeds allocatable inventory.", "Available stock is below the requested quantity or reservations leave insufficient allocatable balance.", "Verify inventory balance, reservations, and order quantity; follow the Inventory Allocation Failure Runbook.", "Correct source inventory or order data through the approved business workflow after human review.", "INVENTORY", "HIGH", "KB-INV-ALLOC-FAIL"),
    ("KERR-SHIP-SYNC-TIMEOUT", "SHIP_SYNC_TIMEOUT", "Shipment synchronization timeout", "Shipment status remains delayed and a carrier synchronization step reports timeout.", "Carrier endpoint latency or a transient synchronization dependency delay.", "Review carrier reference, last successful sync, runtime latency, and batch events before a human-approved retry.", "Address the integration dependency and validate a safe retry path.", "SHIPMENT", "HIGH", "KB-SHIP-SYNC-TIMEOUT"),
    ("KERR-BATCH-INV-RECON", "BATCH_INV_RECON_FAIL", "Inventory reconciliation batch failure", "Inventory reconciliation fails validation or reports negative available quantity.", "A source transaction or balance variance makes reconciliation validation fail.", "Review the failed step, record counts, variance, exception, and diagnostic evidence; confirm rerun safety.", "Correct source data and rerun through batch operations after approval.", "BATCH", "CRITICAL", "KB-BATCH-INV-RECON"),
    ("KERR-API-LATENCY-SPIKE", "API_LATENCY_SPIKE", "API latency spike", "EOS API requests exceed the configured slow-request threshold.", "Database, Redis, application, or downstream dependency latency.", "Use correlation ID to inspect trace spans, logs, metrics, and dependency probes.", "Resolve the responsible dependency after evidence confirms the cause.", "OBSERVABILITY", "HIGH", "KB-API-LATENCY"),
    ("KERR-BFF-HEALTHCHECK", "BFF_HEALTHCHECK_FAIL", "BFF health check failure", "An experience-specific BFF health endpoint is unavailable or unhealthy.", "The BFF process or one of its shared database/Redis dependencies is unavailable.", "Compare the affected BFF with the full backend and other BFF health endpoints; preserve the response evidence.", "Restore service through the approved runtime operations process.", "OBSERVABILITY", "CRITICAL", "KB-BFF-UNAVAILABLE"),
    ("KERR-AMS-BACKLOG", "AMS_BACKLOG_HIGH", "AMS ticket backlog high", "Open support tickets exceed the operating queue threshold.", "A cluster of unresolved alerts, batch failures, or user reports is creating queue pressure.", "Group duplicates, prioritize by severity and impact, and assign human owners.", "Complete triage and capacity planning through AMS operations.", "AMS_OPERATIONS", "MEDIUM", "KB-AMS-BACKLOG"),
]


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def _chunks(body: str) -> list[tuple[str, str]]:
    chunks = []
    for index, paragraph in enumerate(part.strip() for part in body.split("\n\n") if part.strip()):
        lines = paragraph.splitlines()
        heading = lines[0].strip() if len(lines) > 1 else f"Guidance {index + 1}"
        text = " ".join(line.strip() for line in (lines[1:] if len(lines) > 1 else lines))
        chunks.append((heading, text))
    return chunks


def seed_knowledge(db) -> None:
    sources: dict[str, AgentKnowledgeSource] = {}
    for code, name, description, source_type, owner in SOURCES:
        source = db.scalar(select(AgentKnowledgeSource).where(AgentKnowledgeSource.source_code == code))
        if source is None:
            source = AgentKnowledgeSource(source_id=f"KSRC-{code}", source_code=code, name=name, description=description, source_type=source_type, owner=owner, status="ACTIVE")
            db.add(source)
        else:
            source.name, source.description, source.source_type, source.owner, source.status = name, description, source_type, owner, "ACTIVE"
        sources[code] = source
    db.flush()

    articles: dict[str, AgentKnowledgeArticle] = {}
    source_by_domain = {"INVENTORY": sources["EOS-WAREHOUSE-RUNBOOKS"], "ORDER_FULFILLMENT": sources["EOS-WAREHOUSE-RUNBOOKS"], "SHIPMENT": sources["EOS-BATCH-GUIDE"], "BATCH": sources["EOS-BATCH-GUIDE"], "OBSERVABILITY": sources["EOS-OBSERVABILITY-GUIDE"], "AMS_OPERATIONS": sources["EOS-AMS-PLAYBOOK"], "AGENTIC_SUPPORT": sources["EOS-AMS-PLAYBOOK"]}
    for code, title, summary, article_type, domain, area, severity, tags, body in ARTICLES:
        article = db.scalar(select(AgentKnowledgeArticle).where(AgentKnowledgeArticle.article_code == code))
        source = source_by_domain[domain]
        values = dict(article_id=f"KBA-{code}", source_id=source.id, title=title, summary=summary, body=body, article_type=article_type, domain=domain, application_area=area, severity_applicability=severity, status="ACTIVE", version=1, tags=tags)
        if article is None:
            article = AgentKnowledgeArticle(article_code=code, **values)
            db.add(article)
            db.flush()
        else:
            for key, value in values.items(): setattr(article, key, value)
        articles[code] = article
        for index, (heading, text) in enumerate(_chunks(body)):
            normalized = _normalize(f"{title} {heading} {' '.join(tags)} {text}")
            values = dict(heading=heading, chunk_text=text, normalized_text=normalized, token_count_estimate=len(text.split()), keywords=sorted(set(_normalize(' '.join(tags) + ' ' + text).split())))
            # Update by the stable article/chunk position so retrieval audit
            # rows keep pointing at the same chunk UUID. Extra historical
            # chunks are intentionally left in place rather than deleted.
            chunk = db.scalar(select(AgentKnowledgeChunk).where(AgentKnowledgeChunk.article_id == article.id, AgentKnowledgeChunk.chunk_index == index))
            if chunk is None:
                db.add(AgentKnowledgeChunk(chunk_id=f"KCH-{code}-{index + 1:02d}", article_id=article.id, chunk_index=index, **values))
            else:
                for key, value in values.items():
                    setattr(chunk, key, value)
    db.flush()

    for known_id, error_code, title, symptoms, cause, workaround, permanent_fix, area, severity, article_code in KNOWN_ERRORS:
        known = db.scalar(select(AgentKnownError).where(AgentKnownError.error_code == error_code))
        values = dict(known_error_id=known_id, title=title, symptoms=symptoms, likely_cause=cause, workaround=workaround, permanent_fix=permanent_fix, affected_area=area, severity=severity, status="ACTIVE", related_article_id=articles[article_code].id)
        if known is None:
            db.add(AgentKnownError(error_code=error_code, **values))
        else:
            for key, value in values.items(): setattr(known, key, value)


def seed() -> None:
    manager = DatabaseManager(get_settings())
    manager.initialize()
    assert manager.session_factory is not None
    with manager.session_factory() as db:
        seed_knowledge(db)
        db.commit()
    manager.dispose()
    print(f"Agent knowledge seed complete: sources={len(SOURCES)}, articles={len(ARTICLES)}, known_errors={len(KNOWN_ERRORS)}")


if __name__ == "__main__":
    seed()
