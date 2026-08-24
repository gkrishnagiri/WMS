"""Knowledge catalog and deterministic retrieval APIs."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent_knowledge import KnowledgeArticleResponse, KnowledgeChunkResponse, KnowledgeSearchRequest, KnowledgeSearchResponse, KnowledgeSummary, KnownErrorResponse, KnowledgeSourceResponse, RetrievalQueryResponse
from app.services import agent_knowledge_service as service

router = APIRouter(prefix="/api/v1/agent-knowledge", tags=["agent-knowledge"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 404), detail=getattr(error, "message", str(error)))


@router.get("/summary", response_model=KnowledgeSummary)
def summary(db: Session = Depends(get_db)) -> KnowledgeSummary: return service.summary(db)


@router.get("/sources", response_model=list[KnowledgeSourceResponse])
def sources(db: Session = Depends(get_db)) -> list[KnowledgeSourceResponse]: return service.list_sources(db)


@router.get("/articles", response_model=list[KnowledgeArticleResponse])
def articles(domain: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[KnowledgeArticleResponse]: return service.list_articles(db, domain)


@router.get("/articles/{article_id}", response_model=KnowledgeArticleResponse)
def article_detail(article_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_article(db, article_id)
    except service.AgentKnowledgeError as error: raise _error(error) from error


@router.get("/known-errors", response_model=list[KnownErrorResponse])
def known_errors(db: Session = Depends(get_db)) -> list[KnownErrorResponse]: return service.list_known_errors(db)


@router.get("/known-errors/{known_error_id}", response_model=KnownErrorResponse)
def known_error_detail(known_error_id: UUID, db: Session = Depends(get_db)):
    try: return service.get_known_error(db, known_error_id)
    except service.AgentKnowledgeError as error: raise _error(error) from error


@router.post("/search", response_model=KnowledgeSearchResponse)
def search(request: KnowledgeSearchRequest, db: Session = Depends(get_db)) -> KnowledgeSearchResponse: return service.search(db, request)


@router.get("/retrieval-queries", response_model=list[RetrievalQueryResponse])
def retrieval_queries(db: Session = Depends(get_db)) -> list[RetrievalQueryResponse]: return service.list_queries(db)


@router.get("/retrieval-queries/{query_id}", response_model=RetrievalQueryResponse)
def retrieval_query_detail(query_id: str, db: Session = Depends(get_db)):
    try: return service.get_query(db, query_id)
    except service.AgentKnowledgeError as error: raise _error(error) from error


@router.get("/articles/{article_id}/chunks", response_model=list[KnowledgeChunkResponse])
def article_chunks(article_id: UUID, db: Session = Depends(get_db)) -> list[KnowledgeChunkResponse]: return service.list_chunks(db, article_id)
