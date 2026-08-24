from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.seed_agent_knowledge import seed_knowledge
from app.db.session import get_db
from app.main import app
from app.models.agent_knowledge import AgentKnowledgeArticle, AgentKnowledgeChunk, AgentKnowledgeSource, AgentKnownError, AgentRetrievalQuery, AgentRetrievalResult


@pytest.fixture
async def knowledge_client() -> AsyncIterator[tuple[AsyncClient, object]]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    seed_knowledge(session)
    session.commit()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client, session
    app.dependency_overrides.pop(get_db, None)
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_knowledge_seed_is_idempotent():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    seed_knowledge(session)
    session.commit()
    first = [session.scalar(select(func.count(model.id))) for model in (AgentKnowledgeSource, AgentKnowledgeArticle, AgentKnowledgeChunk, AgentKnownError)]
    seed_knowledge(session)
    session.commit()
    second = [session.scalar(select(func.count(model.id))) for model in (AgentKnowledgeSource, AgentKnowledgeArticle, AgentKnowledgeChunk, AgentKnownError)]
    assert first == second == [5, 10, 30, 6]
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.anyio
async def test_knowledge_catalog_and_search_are_available(knowledge_client):
    knowledge_client, session = knowledge_client
    sources = await knowledge_client.get("/api/v1/agent-knowledge/sources")
    articles = await knowledge_client.get("/api/v1/agent-knowledge/articles")
    errors = await knowledge_client.get("/api/v1/agent-knowledge/known-errors")
    assert sources.status_code == articles.status_code == errors.status_code == 200
    assert len(sources.json()) == 5
    assert len(articles.json()) == 10
    assert len(errors.json()) == 6

    article = await knowledge_client.get(f"/api/v1/agent-knowledge/articles/{articles.json()[0]['id']}")
    assert article.status_code == 200
    assert article.json()["chunks"]

    search = await knowledge_client.post("/api/v1/agent-knowledge/search", json={"query": "order is stuck during fulfillment and inventory allocation failed", "top_k": 5, "include_known_errors": True})
    assert search.status_code == 200
    body = search.json()
    assert any(result["article_title"] == "Order Stuck During Fulfillment SOP" for result in body["results"])
    assert any(result["known_error_code"] == "INV_ALLOC_SHORTAGE" for result in body["results"])
    assert body["retrieval_mode"] == "KEYWORD_DETERMINISTIC"

    queries = await knowledge_client.get("/api/v1/agent-knowledge/retrieval-queries")
    assert queries.status_code == 200
    assert len(queries.json()) == 1
    assert queries.json()[0]["results"]
    assert (await knowledge_client.get(f"/api/v1/agent-knowledge/retrieval-queries/{body['query_id']}")).status_code == 200

    # Reseeding after retrieval has created foreign-key references must update
    # chunks in place and preserve every audit reference.
    seed_knowledge(session)
    session.commit()
    audit_rows = session.scalars(select(AgentRetrievalResult)).all()
    assert audit_rows
    assert all(session.get(AgentKnowledgeChunk, row.chunk_id) is not None for row in audit_rows if row.chunk_id)


@pytest.mark.anyio
async def test_agent_orchestrator_includes_knowledge_evidence(knowledge_client):
    knowledge_client, _ = knowledge_client
    response = await knowledge_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Investigate stuck order", "description": "Inventory allocation failed during fulfillment.", "initial_message": "The order is stuck during fulfillment and inventory allocation failed. What should I check next?"})
    assert response.status_code == 201
    body = response.json()
    assert "Relevant Knowledge:" in body["messages"][-1]["message_text"]
    assert any(item["evidence_type"] in ("KNOWLEDGE_CHUNK", "KNOWN_ERROR") for item in body["evidence"])
    assert body["orchestration_runs"][0]["tools_used"]["knowledge_results"] > 0
