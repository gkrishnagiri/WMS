"""Curated support knowledge and deterministic retrieval audit models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class AgentKnowledgeSource(TimestampMixin, Base):
    __tablename__ = "agent_knowledge_sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    owner: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")

    articles: Mapped[list["AgentKnowledgeArticle"]] = relationship(back_populates="source")


class AgentKnowledgeArticle(TimestampMixin, Base):
    __tablename__ = "agent_knowledge_articles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_knowledge_sources.id"), nullable=False)
    article_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    body: Mapped[str] = mapped_column(String(12000), nullable=False)
    article_type: Mapped[str] = mapped_column(String(50), nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    application_area: Mapped[str] = mapped_column(String(100), nullable=False)
    severity_applicability: Mapped[Optional[str]] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    tags: Mapped[Optional[list]] = mapped_column(JSON)

    source: Mapped[AgentKnowledgeSource] = relationship(back_populates="articles")
    chunks: Mapped[list["AgentKnowledgeChunk"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    known_errors: Mapped[list["AgentKnownError"]] = relationship(back_populates="related_article")


class AgentKnowledgeChunk(TimestampMixin, Base):
    __tablename__ = "agent_knowledge_chunks"
    __table_args__ = (UniqueConstraint("article_id", "chunk_index", name="uq_agent_knowledge_chunk_index"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    article_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_knowledge_articles.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    heading: Mapped[str] = mapped_column(String(200), nullable=False)
    chunk_text: Mapped[str] = mapped_column(String(4000), nullable=False)
    normalized_text: Mapped[str] = mapped_column(String(4000), nullable=False)
    token_count_estimate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    keywords: Mapped[Optional[list]] = mapped_column(JSON)

    article: Mapped[AgentKnowledgeArticle] = relationship(back_populates="chunks")


class AgentKnownError(TimestampMixin, Base):
    __tablename__ = "agent_known_errors"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    known_error_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    error_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    symptoms: Mapped[str] = mapped_column(String(1500), nullable=False)
    likely_cause: Mapped[str] = mapped_column(String(1500), nullable=False)
    workaround: Mapped[str] = mapped_column(String(1500), nullable=False)
    permanent_fix: Mapped[Optional[str]] = mapped_column(String(1500))
    affected_area: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    related_article_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_knowledge_articles.id"))

    related_article: Mapped[Optional[AgentKnowledgeArticle]] = relationship(back_populates="known_errors")


class AgentRetrievalQuery(Base):
    __tablename__ = "agent_retrieval_queries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    case_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_cases.id"))
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_chat_sessions.id"))
    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_chat_messages.id"))
    query_text: Mapped[str] = mapped_column(String(3000), nullable=False)
    normalized_query: Mapped[str] = mapped_column(String(3000), nullable=False)
    retrieval_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="KEYWORD_DETERMINISTIC")
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AgentRetrievalResult(Base):
    __tablename__ = "agent_retrieval_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    query_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_retrieval_queries.id"), nullable=False)
    article_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_knowledge_articles.id"))
    chunk_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_knowledge_chunks.id"))
    known_error_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_known_errors.id"))
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    match_reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    snippet: Mapped[str] = mapped_column(String(1200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
