const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Stage 3 API returned ${response.status}: ${body?.detail || "request failed"}`);
  return body as T;
}

export interface SandboxStatus { mode: string; sandbox_enabled: boolean; kill_switch_enabled: boolean; real_model_allowed: boolean; real_model_default_enabled: boolean; require_dry_run_first: boolean; max_steps: number; max_duration_seconds: number; max_estimated_cost: number; safe_to_execute: boolean; production_autonomous_remediation: boolean; safety_notes: string; reason: string; }
export interface SandboxProfile { profile_code: string; title: string; description: string; allowed_actions: string[]; execution_enabled: boolean; enabled_for_execution: boolean; safety_notes: string; }
export interface SandboxRun { run_id: string; status: string; profile_code: string; case_id?: string; scenario_run_id?: string; dry_run_required: boolean; dry_run_completed: boolean; max_steps: number; steps_completed: number; max_duration_seconds: number; max_estimated_cost: number; estimated_total_cost: number; total_tokens: number; stop_reason?: string; steps: Array<{ step_id: string; step_number: number; status: string; selected_action_code?: string; proposal_id?: string; execution_id?: string; guardrail_status?: string; guardrail_reason?: string; decision_summary?: string; error_message?: string }>; events: Array<{ event_id: string; event_type: string; event_title: string; event_description: string; severity: string }>; }
export interface SandboxSummary { mode: string; sandbox_enabled: boolean; kill_switch_enabled: boolean; run_count: number; completed_runs: number; blocked_runs: number; needs_human_review: number; total_estimated_cost: number; total_tokens: number; status_counts: Record<string, number>; production_autonomous_remediation: boolean; real_model_default_enabled: boolean; safety_notes: string; }

export const getStage3Status = () => request<SandboxStatus>("/api/v1/stage3-autonomy/status");
export const getStage3Profiles = () => request<SandboxProfile[]>("/api/v1/stage3-autonomy/profiles");
export const getStage3Summary = () => request<SandboxSummary>("/api/v1/stage3-autonomy/summary");
export const getStage3Runs = (caseId?: string) => request<SandboxRun[]>(`/api/v1/stage3-autonomy/runs${caseId ? `?case_id=${encodeURIComponent(caseId)}` : ""}`);
export const getStage3Run = (runId: string) => request<SandboxRun>(`/api/v1/stage3-autonomy/runs/${runId}`);
export const createStage3Run = (body: Record<string, unknown>) => request<SandboxRun>("/api/v1/stage3-autonomy/runs", { method: "POST", body: JSON.stringify(body) });
export const dryRunStage3 = (runId: string) => request<{ run: SandboxRun; planned_actions: Array<Record<string, unknown>>; guardrails: Record<string, unknown>; human_handback_conditions: string[]; what_will_not_be_done: string }>(`/api/v1/stage3-autonomy/runs/${runId}/dry-run`, { method: "POST", body: JSON.stringify({ requested_by_role: "DEMO_PRESENTER" }) });
export const startStage3 = (runId: string) => request<SandboxRun>(`/api/v1/stage3-autonomy/runs/${runId}/start`, { method: "POST", body: JSON.stringify({ requested_by_role: "DEMO_PRESENTER", acknowledge_autonomous_sandbox: true, acknowledge_no_external_systems: true, acknowledge_cost: true }) });
export const pauseStage3 = (runId: string) => request<SandboxRun>(`/api/v1/stage3-autonomy/runs/${runId}/pause`, { method: "POST", body: JSON.stringify({ requested_by_role: "DEMO_PRESENTER", reason: "Paused from the sandbox console." }) });
export const stopStage3 = (runId: string) => request<SandboxRun>(`/api/v1/stage3-autonomy/runs/${runId}/stop`, { method: "POST", body: JSON.stringify({ requested_by_role: "DEMO_PRESENTER", reason: "Stopped from the sandbox console." }) });
export const setStage3KillSwitch = (enabled: boolean) => request<Record<string, unknown>>("/api/v1/stage3-autonomy/kill-switch", { method: "POST", body: JSON.stringify({ enabled, requested_by_role: "DEMO_PRESENTER", reason: "Stage 3 console control." }) });
