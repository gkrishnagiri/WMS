const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface KnowledgeSource { id: string; source_id: string; source_code: string; name: string; description: string; source_type: string; owner: string; status: string; created_at: string; updated_at: string; }
export interface KnowledgeChunk { id: string; chunk_id: string; chunk_index: number; heading: string; chunk_text: string; token_count_estimate: number; keywords: string[] | null; }
export interface KnowledgeArticle { id: string; article_id: string; source_id: string; article_code: string; title: string; summary: string; body: string; article_type: string; domain: string; application_area: string; severity_applicability: string | null; status: string; version: number; tags: string[] | null; chunks: KnowledgeChunk[]; created_at: string; updated_at: string; }
export interface KnownError { id: string; known_error_id: string; error_code: string; title: string; symptoms: string; likely_cause: string; workaround: string; permanent_fix: string | null; affected_area: string; severity: string; status: string; related_article_id: string | null; created_at: string; updated_at: string; }
export interface RetrievalResult { id: string | null; result_id: string; rank: number; score: number; match_reason: string; snippet: string; article_id: string | null; article_title: string | null; article_type: string | null; domain: string | null; chunk_id: string | null; heading: string | null; known_error_id: string | null; known_error_code: string | null; }
export interface RetrievalQuery { id: string; query_id: string; case_id: string | null; session_id: string | null; message_id: string | null; query_text: string; normalized_query: string; retrieval_mode: string; top_k: number; created_at: string; results: RetrievalResult[]; }
export interface KnowledgeSummary { sources: number; active_sources: number; articles: number; active_articles: number; chunks: number; known_errors: number; retrieval_queries: number; retrieval_results: number; }

async function request<T>(path: string, options: RequestInit = {}): Promise<T> { const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } }); const body = await response.json().catch(() => ({})); if (!response.ok) throw new Error(`Agent knowledge API returned ${response.status}: ${body?.detail || "request failed"}`); return body as T; }
export const getKnowledgeSummary = () => request<KnowledgeSummary>("/api/v1/agent-knowledge/summary");
export const getKnowledgeSources = () => request<KnowledgeSource[]>("/api/v1/agent-knowledge/sources");
export const getKnowledgeArticles = () => request<KnowledgeArticle[]>("/api/v1/agent-knowledge/articles");
export const getKnowledgeArticle = (id: string) => request<KnowledgeArticle>(`/api/v1/agent-knowledge/articles/${id}`);
export const getKnownErrors = () => request<KnownError[]>("/api/v1/agent-knowledge/known-errors");
export const getKnownError = (id: string) => request<KnownError>(`/api/v1/agent-knowledge/known-errors/${id}`);
export const searchKnowledge = (query: string, top_k = 5) => request<{ query_id: string; query: string; retrieval_mode: string; results: RetrievalResult[]; notes: string[] }>("/api/v1/agent-knowledge/search", { method: "POST", body: JSON.stringify({ query, top_k, include_known_errors: true }) });
export const getRetrievalQueries = () => request<RetrievalQuery[]>("/api/v1/agent-knowledge/retrieval-queries");
export const getRetrievalQuery = (id: string) => request<RetrievalQuery>(`/api/v1/agent-knowledge/retrieval-queries/${id}`);
