"""API schemas for curated knowledge and deterministic retrieval."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeSourceResponse(BaseModel):
    id: UUID
    source_id: str
    source_code: str
    name: str
    description: str
    source_type: str
    owner: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeChunkResponse(BaseModel):
    id: UUID
    chunk_id: str
    chunk_index: int
    heading: str
    chunk_text: str
    token_count_estimate: int
    keywords: list | None

    model_config = {"from_attributes": True}


class KnowledgeArticleResponse(BaseModel):
    id: UUID
    article_id: str
    source_id: UUID
    article_code: str
    title: str
    summary: str
    body: str
    article_type: str
    domain: str
    application_area: str
    severity_applicability: str | None
    status: str
    version: int
    tags: list | None
    chunks: list[KnowledgeChunkResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnownErrorResponse(BaseModel):
    id: UUID
    known_error_id: str
    error_code: str
    title: str
    symptoms: str
    likely_cause: str
    workaround: str
    permanent_fix: str | None
    affected_area: str
    severity: str
    status: str
    related_article_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RetrievalResultResponse(BaseModel):
    id: UUID | None = None
    result_id: str
    rank: int
    score: float
    match_reason: str
    snippet: str
    article_id: str | None = None
    article_title: str | None = None
    article_type: str | None = None
    domain: str | None = None
    chunk_id: str | None = None
    heading: str | None = None
    known_error_id: str | None = None
    known_error_code: str | None = None


class RetrievalQueryResponse(BaseModel):
    id: UUID
    query_id: str
    case_id: UUID | None
    session_id: UUID | None
    message_id: UUID | None
    query_text: str
    normalized_query: str
    retrieval_mode: str
    top_k: int
    created_at: datetime
    results: list[RetrievalResultResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=3000)
    case_id: UUID | None = None
    session_id: UUID | None = None
    message_id: UUID | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    domains: list[str] | None = None
    include_known_errors: bool = True


class KnowledgeSearchResponse(BaseModel):
    query_id: str
    query: str
    retrieval_mode: str
    results: list[RetrievalResultResponse]
    notes: list[str]


class KnowledgeSummary(BaseModel):
    sources: int
    active_sources: int
    articles: int
    active_articles: int
    chunks: int
    known_errors: int
    retrieval_queries: int
    retrieval_results: int
