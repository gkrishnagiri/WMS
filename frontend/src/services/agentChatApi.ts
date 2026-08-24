const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface AgentCase { id: string; case_id: string; case_type: string; title: string; description: string; status: string; priority: string; source: string; stage_mode: string; created_by_role: string; linked_ams_ticket_id: string | null; linked_user_report_id: string | null; linked_alert_event_id: string | null; linked_batch_run_id: string | null; linked_diagnostic_case_id: string | null; created_at: string; updated_at: string; closed_at: string | null; }
export interface AgentMessage { id: string; message_id: string; session_id: string; sender_type: string; sender_role: string; message_text: string; generation_mode: string; safety_status: string; created_at: string; metadata_json: Record<string, unknown> | null; }
export interface AgentEvidence { id: string; evidence_id: string; case_id: string; run_id: string; evidence_type: string; source_type: string; source_id: string | null; title: string; summary: string; relevance_score: number; created_at: string; }
export interface AgentRun { id: string; run_id: string; case_id: string; session_id: string; trigger_message_id: string; status: string; stage_mode: string; orchestrator_mode: string; started_at: string; completed_at: string | null; summary: string; actions_proposed: number; actions_executed: number; }
export interface AgentProposal { id: string; proposal_id: string; case_id: string; run_id: string; title: string; description: string; action_type: string; risk_level: string; status: string; requires_approval: boolean; approval_status: string; execution_status: string; }
export interface AgentSession { id: string; session_id: string; case_id: string; audience: string; title: string; status: string; started_by_role: string; experience: string; created_at: string; updated_at: string; closed_at: string | null; case: AgentCase; messages: AgentMessage[]; evidence: AgentEvidence[]; orchestration_runs: AgentRun[]; action_proposals: AgentProposal[]; }
export interface AgentSummary { open_cases: number; active_sessions: number; orchestration_runs: number; evidence_items: number; action_proposals: number; actions_executed: number; stage_mode: string; }

async function request<T>(path: string, options: RequestInit = {}): Promise<T> { const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } }); const body = await response.json().catch(() => ({})); if (!response.ok) throw new Error(`Agent chat API returned ${response.status}: ${body?.detail || "request failed"}`); return body as T; }
export const getAgentSummary = () => request<AgentSummary>("/api/v1/agent-chat/summary");
export const getAgentCases = () => request<AgentCase[]>("/api/v1/agent-chat/cases");
export const getAgentSessions = () => request<AgentSession[]>("/api/v1/agent-chat/sessions");
export const getAgentSession = (id: string) => request<AgentSession>(`/api/v1/agent-chat/sessions/${id}`);
export const getAgentCase = (id: string) => request<AgentCase>(`/api/v1/agent-chat/cases/${id}`);
export const getAgentEvidence = (id: string) => request<AgentEvidence[]>(`/api/v1/agent-chat/cases/${id}/evidence`);
export const getAgentRuns = (id: string) => request<AgentRun[]>(`/api/v1/agent-chat/cases/${id}/orchestration-runs`);
export const getAgentProposals = (id: string) => request<AgentProposal[]>(`/api/v1/agent-chat/cases/${id}/action-proposals`);
export const intakeUserIssue = (payload: { title: string; description: string; initial_message: string }) => request<AgentSession>("/api/v1/agent-chat/intake/user-issue", { method: "POST", body: JSON.stringify(payload) });
export const intakeEngineerIssue = (payload: { title: string; description: string; initial_message: string }) => request<AgentSession>("/api/v1/agent-chat/intake/engineer-investigation", { method: "POST", body: JSON.stringify(payload) });
export const sendAgentMessage = (id: string, message_text: string, options: { use_real_model?: boolean; provider_code?: string; model_code?: string; dry_run?: boolean } = {}) => request<AgentSession>(`/api/v1/agent-chat/sessions/${id}/messages`, { method: "POST", body: JSON.stringify({ message_text, ...options }) });
export const closeAgentSession = (id: string) => request<AgentSession>(`/api/v1/agent-chat/sessions/${id}/close`, { method: "POST" });
