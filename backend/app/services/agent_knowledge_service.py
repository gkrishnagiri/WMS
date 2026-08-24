"""Deterministic keyword retrieval over curated agent support knowledge."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_chat import AgentCase, AgentChatMessage, AgentChatSession
from app.models.agent_knowledge import AgentKnowledgeArticle, AgentKnowledgeChunk, AgentKnowledgeSource, AgentKnownError, AgentRetrievalQuery, AgentRetrievalResult
from app.schemas.agent_knowledge import KnowledgeArticleResponse, KnowledgeChunkResponse, KnowledgeSearchRequest, KnowledgeSearchResponse, KnowledgeSummary, KnownErrorResponse, RetrievalQueryResponse, RetrievalResultResponse, KnowledgeSourceResponse

RETRIEVAL_MODE = "KEYWORD_DETERMINISTIC"
STOP_WORDS = {"a", "an", "and", "are", "can", "did", "for", "has", "i", "in", "is", "it", "my", "of", "on", "or", "the", "to", "what", "why", "with"}


class AgentKnowledgeError(Exception):
    def __init__(self, message: str, status_code: int = 404) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class KnowledgeMatch:
    article: AgentKnowledgeArticle | None
    chunk: AgentKnowledgeChunk | None
    known_error: AgentKnownError | None
    score: float
    reason: str
    snippet: str


@dataclass
class RetrievalBundle:
    query: AgentRetrievalQuery
    matches: list[KnowledgeMatch]


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9_]+", " ", value.lower())).strip()


def _terms(value: str) -> set[str]:
    return {term for term in _normalize(value).replace("_", " ").split() if len(term) > 1 and term not in STOP_WORDS}


def _next(db: Session, field, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            pass
    return f"{prefix}{sequence:04d}"


def _article_response(article: AgentKnowledgeArticle) -> KnowledgeArticleResponse:
    return KnowledgeArticleResponse.model_validate(article, from_attributes=True)


def _result_response(db: Session, result: AgentRetrievalResult) -> RetrievalResultResponse:
    article = db.get(AgentKnowledgeArticle, result.article_id) if result.article_id else None
    chunk = db.get(AgentKnowledgeChunk, result.chunk_id) if result.chunk_id else None
    known = db.get(AgentKnownError, result.known_error_id) if result.known_error_id else None
    return RetrievalResultResponse(id=result.id, result_id=result.result_id, rank=result.rank, score=result.score, match_reason=result.match_reason, snippet=result.snippet, article_id=article.article_id if article else None, article_title=article.title if article else None, article_type=article.article_type if article else None, domain=article.domain if article else None, chunk_id=chunk.chunk_id if chunk else None, heading=chunk.heading if chunk else None, known_error_id=known.known_error_id if known else None, known_error_code=known.error_code if known else None)


def _query_response(db: Session, query: AgentRetrievalQuery) -> RetrievalQueryResponse:
    results = db.scalars(select(AgentRetrievalResult).where(AgentRetrievalResult.query_id == query.id).order_by(AgentRetrievalResult.rank)).all()
    return RetrievalQueryResponse.model_validate(query, from_attributes=True).model_copy(update={"results": [_result_response(db, result) for result in results]})


def list_sources(db: Session) -> list[KnowledgeSourceResponse]:
    return [KnowledgeSourceResponse.model_validate(item, from_attributes=True) for item in db.scalars(select(AgentKnowledgeSource).order_by(AgentKnowledgeSource.name)).all()]


def list_articles(db: Session, domain: str | None = None) -> list[KnowledgeArticleResponse]:
    statement = select(AgentKnowledgeArticle).where(AgentKnowledgeArticle.status == "ACTIVE").order_by(AgentKnowledgeArticle.title)
    if domain:
        statement = statement.where(AgentKnowledgeArticle.domain == domain.upper())
    return [_article_response(item) for item in db.scalars(statement).all()]


def get_article(db: Session, article_id: UUID) -> KnowledgeArticleResponse:
    article = db.get(AgentKnowledgeArticle, article_id)
    if article is None:
        raise AgentKnowledgeError("Knowledge article not found.")
    return _article_response(article)


def list_chunks(db: Session, article_id: UUID | None = None) -> list[KnowledgeChunkResponse]:
    statement = select(AgentKnowledgeChunk).order_by(AgentKnowledgeChunk.article_id, AgentKnowledgeChunk.chunk_index)
    if article_id:
        statement = statement.where(AgentKnowledgeChunk.article_id == article_id)
    return [KnowledgeChunkResponse.model_validate(item, from_attributes=True) for item in db.scalars(statement).all()]


def list_known_errors(db: Session) -> list[KnownErrorResponse]:
    return [KnownErrorResponse.model_validate(item, from_attributes=True) for item in db.scalars(select(AgentKnownError).where(AgentKnownError.status == "ACTIVE").order_by(AgentKnownError.error_code)).all()]


def get_known_error(db: Session, known_error_id: UUID) -> KnownErrorResponse:
    error = db.get(AgentKnownError, known_error_id)
    if error is None:
        raise AgentKnowledgeError("Known error not found.")
    return KnownErrorResponse.model_validate(error, from_attributes=True)


def _article_matches(article: AgentKnowledgeArticle, query_terms: set[str], phrase: str, domains: set[str]) -> list[KnowledgeMatch]:
    if article.domain not in domains and domains:
        return []
    title_terms = _terms(article.title)
    tag_terms = _terms(" ".join(article.tags or []))
    domain_terms = _terms(article.domain)
    summary_terms = _terms(article.summary)
    matches: list[KnowledgeMatch] = []
    for chunk in article.chunks:
        chunk_terms = _terms(chunk.chunk_text)
        score = float(len(query_terms & chunk_terms))
        reasons = []
        if query_terms & title_terms:
            score += len(query_terms & title_terms) * 2.0
            reasons.append("title terms")
        if query_terms & tag_terms:
            score += len(query_terms & tag_terms) * 1.5
            reasons.append("tag terms")
        if query_terms & domain_terms:
            score += len(query_terms & domain_terms) * 1.0
            reasons.append("domain terms")
        if query_terms & summary_terms:
            score += len(query_terms & summary_terms) * 0.75
            reasons.append("summary terms")
        if query_terms & chunk_terms:
            reasons.append("chunk terms")
        if phrase and phrase in _normalize(f"{article.title} {chunk.chunk_text}"):
            score += 3.0
            reasons.append("phrase match")
        if score > 0:
            matches.append(KnowledgeMatch(article=article, chunk=chunk, known_error=None, score=score, reason="Matched " + ", ".join(reasons), snippet=chunk.chunk_text[:1100]))
    return matches


def _known_error_match(error: AgentKnownError, query_terms: set[str], phrase: str) -> KnowledgeMatch | None:
    searchable = f"{error.error_code} {error.title} {error.symptoms} {error.likely_cause} {error.workaround} {error.affected_area}"
    terms = _terms(searchable) | _terms(error.error_code)
    overlap = query_terms & terms
    score = float(len(overlap) * 2.0)
    reasons = []
    if overlap:
        reasons.append("known-error terms")
    if {"allocation", "shortage"}.issubset(query_terms & terms):
        score += 4.0
        reasons.append("symptom pair match")
    if phrase and phrase in _normalize(searchable):
        score += 3
        reasons.append("phrase match")
    if score <= 0:
        return None
    return KnowledgeMatch(article=None, chunk=None, known_error=error, score=score, reason="Matched " + ", ".join(reasons), snippet=f"{error.error_code}: {error.symptoms} Workaround: {error.workaround}")


def _find_matches(db: Session, query_text: str, top_k: int, domains: Iterable[str] | None, include_known_errors: bool) -> list[KnowledgeMatch]:
    normalized = _normalize(query_text)
    query_terms = _terms(query_text)
    phrase = normalized if len(normalized.split()) > 1 else ""
    domain_filter = {domain.upper() for domain in (domains or [])}
    matches: list[KnowledgeMatch] = []
    articles = db.scalars(select(AgentKnowledgeArticle).where(AgentKnowledgeArticle.status == "ACTIVE")).all()
    for article in articles:
        matches.extend(_article_matches(article, query_terms, phrase, domain_filter))
    if include_known_errors:
        for error in db.scalars(select(AgentKnownError).where(AgentKnownError.status == "ACTIVE")).all():
            match = _known_error_match(error, query_terms, phrase)
            if match:
                matches.append(match)
    matches.sort(key=lambda item: (-item.score, item.article.title if item.article else item.known_error.error_code if item.known_error else ""))
    selected = matches[:top_k]
    # A matching known error is a first-class support citation. Keep the best
    # one visible in a bounded result set even when many article chunks score
    # slightly higher.
    known_matches = [item for item in matches if item.known_error]
    if include_known_errors and known_matches and not any(item.known_error for item in selected) and selected:
        selected[-1] = known_matches[0]
        selected.sort(key=lambda item: (-item.score, item.article.title if item.article else item.known_error.error_code if item.known_error else ""))
    return selected


def _record_retrieval(db: Session, request: KnowledgeSearchRequest, matches: list[KnowledgeMatch], commit: bool) -> RetrievalBundle:
    query = AgentRetrievalQuery(query_id=_next(db, AgentRetrievalQuery.query_id, "RETQ-"), case_id=request.case_id, session_id=request.session_id, message_id=request.message_id, query_text=request.query, normalized_query=_normalize(request.query), retrieval_mode=RETRIEVAL_MODE, top_k=request.top_k)
    db.add(query)
    db.flush()
    for rank, match in enumerate(matches, 1):
        db.add(AgentRetrievalResult(result_id=_next(db, AgentRetrievalResult.result_id, "RETR-"), query_id=query.id, article_id=match.article.id if match.article else None, chunk_id=match.chunk.id if match.chunk else None, known_error_id=match.known_error.id if match.known_error else None, rank=rank, score=round(match.score, 2), match_reason=match.reason, snippet=match.snippet))
        db.flush()
    if commit:
        db.commit()
    return RetrievalBundle(query=query, matches=matches)


def search(db: Session, request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    matches = _find_matches(db, request.query, request.top_k, request.domains, request.include_known_errors)
    bundle = _record_retrieval(db, request, matches, commit=True)
    persisted = db.get(AgentRetrievalQuery, bundle.query.id)
    return KnowledgeSearchResponse(query_id=bundle.query.query_id, query=request.query, retrieval_mode=RETRIEVAL_MODE, results=[_result_response(db, result) for result in db.scalars(select(AgentRetrievalResult).where(AgentRetrievalResult.query_id == persisted.id).order_by(AgentRetrievalResult.rank)).all()], notes=["Deterministic keyword retrieval only. No embedding model was used."])


def retrieve_for_agent(db: Session, case: AgentCase, session: AgentChatSession, message: AgentChatMessage, top_k: int = 5) -> RetrievalBundle:
    request = KnowledgeSearchRequest(query=f"{message.message_text} {case.title} {case.description} {case.case_type}", case_id=case.id, session_id=session.id, message_id=message.id, top_k=top_k, include_known_errors=True)
    return _record_retrieval(db, request, _find_matches(db, request.query, top_k, None, True), commit=False)


def list_queries(db: Session) -> list[RetrievalQueryResponse]:
    return [_query_response(db, item) for item in db.scalars(select(AgentRetrievalQuery).order_by(AgentRetrievalQuery.created_at.desc())).all()]


def get_query(db: Session, query_id: str) -> RetrievalQueryResponse:
    query = db.scalar(select(AgentRetrievalQuery).where(AgentRetrievalQuery.query_id == query_id))
    if query is None:
        raise AgentKnowledgeError("Retrieval query not found.")
    return _query_response(db, query)


def summary(db: Session) -> KnowledgeSummary:
    active_sources = db.scalar(select(func.count(AgentKnowledgeSource.id)).where(AgentKnowledgeSource.status == "ACTIVE")) or 0
    active_articles = db.scalar(select(func.count(AgentKnowledgeArticle.id)).where(AgentKnowledgeArticle.status == "ACTIVE")) or 0
    return KnowledgeSummary(sources=int(db.scalar(select(func.count(AgentKnowledgeSource.id))) or 0), active_sources=int(active_sources), articles=int(db.scalar(select(func.count(AgentKnowledgeArticle.id))) or 0), active_articles=int(active_articles), chunks=int(db.scalar(select(func.count(AgentKnowledgeChunk.id))) or 0), known_errors=int(db.scalar(select(func.count(AgentKnownError.id))) or 0), retrieval_queries=int(db.scalar(select(func.count(AgentRetrievalQuery.id))) or 0), retrieval_results=int(db.scalar(select(func.count(AgentRetrievalResult.id))) or 0))
