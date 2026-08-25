const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Investigation API returned ${response.status}: ${body?.detail || "request failed"}`);
  return body as T;
}

export interface InvestigationWorkspace { case: { id: string; case_id: string; case_type: string; title: string; description: string; status: string; priority: string; stage_mode: string; source_object_type: string | null; source_object_id: string | null; source_object_display: string | null; source_object_url: string | null; }; source: { type: string | null; display: string | null; id: string | null; url: string | null; summary: string; }; linked_objects: Record<string, Record<string, unknown> | null>; sessions: { id: string; session_id: string; title: string; status: string }[]; messages: { id: string; sender_type: string; generation_mode: string; message_text: string; created_at: string }[]; evidence: { id: string; evidence_type: string; title: string; summary: string; created_at: string }[]; knowledge: { id: string; title: string; article_type?: string; domain?: string; summary: string }[]; known_errors: { id: string; error_code: string; title: string; summary: string }[]; orchestration_runs: { id: string; run_id: string; status: string; summary: string; started_at: string; actions_executed: number }[]; action_proposals: { id: string; title: string; status: string; execution_status: string; requires_approval: boolean }[]; latest_guidance: string | null; counts: { evidence_items: number; knowledge_items: number; known_errors: number; orchestration_runs: number; action_proposals: number; actions_executed: number }; stage_safety: { mode: string; real_model_default: boolean; remediation_execution_enabled: boolean; message: string }; }
export interface InvestigationSummary { investigations: number; open_investigations: number; stage_1_investigations: number; evidence_items: number; actions_executed: number; }
export interface TimelineItem { timestamp: string; item_type: string; title: string; description: string; source_type: string; source_id: string | null; severity: string | null; status: string | null; link_url: string | null; metadata: Record<string, unknown>; }
export interface InvestigationDrafts { generation_mode: string; human_review_required: boolean; investigation_summary: { title: string; content: string }; work_note_draft: { title: string; content: string }; customer_update_draft: { title: string; content: string }; next_steps_checklist: { title: string; content: string }; }
export const getInvestigationSummary = () => request<InvestigationSummary>("/api/v1/agent-investigations/summary");
export const getInvestigations = () => request<InvestigationWorkspace[]>("/api/v1/agent-investigations/cases");
export const getInvestigation = (id: string) => request<InvestigationWorkspace>(`/api/v1/agent-investigations/cases/${id}`);
export const getInvestigationTimeline = (id: string) => request<TimelineItem[]>(`/api/v1/agent-investigations/cases/${id}/timeline`);
export const getInvestigationDrafts = (id: string) => request<InvestigationDrafts>(`/api/v1/agent-investigations/cases/${id}/drafts`);
export const generateInvestigationDrafts = (id: string) => request<InvestigationDrafts>(`/api/v1/agent-investigations/cases/${id}/generate-drafts`, { method: "POST", body: "{}" });
