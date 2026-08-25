const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Agent action API returned ${response.status}: ${body?.detail || "request failed"}`);
  return body as T;
}

export interface AgentActionCatalogItem { code: string; name: string; description: string; risk_level: string; enabled: boolean; execution_mode: string; safety_notes: string; handler: null; }
export interface AgentActionProposal { id: string; proposal_id: string; case_id: string; run_id: string; title: string; description: string; action_type: string; safe_action_code: string | null; risk_level: string; status: string; requires_approval: boolean; approval_status: string; approved_by_role: string | null; approved_at: string | null; rejected_by_role: string | null; rejected_at: string | null; approval_comment: string | null; execution_status: string; execution_mode: string; execution_started_at: string | null; execution_completed_at: string | null; execution_error: string | null; execution_result_json: Record<string, unknown> | null; idempotency_key: string | null; action_payload_json: Record<string, unknown> | null; created_at: string; updated_at: string; }
export interface AgentActionExecution { id: string; execution_id: string; proposal_id: string; case_id: string; run_id: string; safe_action_code: string; status: string; requested_by_role: string; approved_by_role: string | null; started_at: string | null; completed_at: string | null; result_summary: string | null; result_json: Record<string, unknown> | null; error_message: string | null; idempotency_key: string; created_at: string; updated_at: string; }
export interface AgentActionSummary { stage_mode: string; execution_mode: string; catalog_actions: number; proposals: number; pending_approval: number; approved: number; rejected: number; executions: number; succeeded: number; failed: number; autonomous_remediation_enabled: boolean; real_model_default: boolean; safety_notes: string; }
export interface AgentActionResult { proposal: AgentActionProposal; execution: AgentActionExecution | null; duplicate_prevented?: boolean; message?: string; }
export interface AgentActionDryRun { proposal: AgentActionProposal; what_would_happen: string; executable: boolean; required_approval_state: string; target_object: Record<string, unknown>; expected_local_changes: string; safety_notes: string; requested_by_role: string; dry_run: boolean; }

export const getAgentActionSummary = () => request<AgentActionSummary>("/api/v1/agent-actions/summary");
export const getAgentActionCatalog = () => request<AgentActionCatalogItem[]>("/api/v1/agent-actions/catalog");
export const getAgentActionProposals = (caseId?: string) => request<AgentActionProposal[]>(`/api/v1/agent-actions/proposals${caseId ? `?case_id=${encodeURIComponent(caseId)}` : ""}`);
export const getAgentActionExecutions = (caseId?: string) => request<AgentActionExecution[]>(`/api/v1/agent-actions/executions${caseId ? `?case_id=${encodeURIComponent(caseId)}` : ""}`);
export const approveAgentAction = (proposalId: string, comment = "") => request<AgentActionResult>(`/api/v1/agent-actions/proposals/${proposalId}/approve`, { method: "POST", body: JSON.stringify({ approved_by_role: "SERVICE_ENGINEER", approval_comment: comment, execute_after_approval: false }) });
export const rejectAgentAction = (proposalId: string, comment = "") => request<AgentActionResult>(`/api/v1/agent-actions/proposals/${proposalId}/reject`, { method: "POST", body: JSON.stringify({ rejected_by_role: "SERVICE_ENGINEER", rejection_comment: comment }) });
export const dryRunAgentAction = (proposalId: string) => request<AgentActionDryRun>(`/api/v1/agent-actions/proposals/${proposalId}/dry-run`, { method: "POST", body: JSON.stringify({ requested_by_role: "SERVICE_ENGINEER" }) });
export const executeAgentAction = (proposalId: string) => request<AgentActionResult>(`/api/v1/agent-actions/proposals/${proposalId}/execute`, { method: "POST", body: JSON.stringify({ requested_by_role: "SERVICE_ENGINEER", execution_comment: "Execute approved safe local action." }) });
