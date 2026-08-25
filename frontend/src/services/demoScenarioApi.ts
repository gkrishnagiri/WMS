const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Demo scenario API returned ${response.status}: ${body?.detail || "request failed"}`);
  return body as T;
}

export interface DemoScenario { id: string; scenario_code: string; title: string; description: string; business_value: string; default_experience: string; is_enabled: boolean; sort_order: number; step_count: number; }
export interface DemoScenarioStep { id: string; step_code: string; step_title: string; step_description: string; presenter_instruction: string; expected_result: string; action_type: string; step_order: number; status: string; started_at: string | null; completed_at: string | null; target_url: string | null; target_object_type: string | null; target_object_id: string | null; instructions: string | null; }
export interface DemoScenarioArtifact { id: string; artifact_type: string; artifact_id: string; artifact_display: string; artifact_url: string | null; metadata_json: Record<string, unknown> | null; created_at: string; }
export interface DemoScenarioEvent { id: string; event_type: string; event_title: string; event_description: string; event_timestamp: string; source_type: string | null; source_id: string | null; metadata_json: Record<string, unknown> | null; created_at: string; }
export interface DemoScenarioNextAction { step_code: string; title: string; action_type: string; presenter_instruction: string; expected_result: string; target_url: string | null; safe_boundary: string; }
export interface DemoScenarioRun { id: string; run_id: string; scenario_code: string; scenario_title: string; status: string; current_step_code: string | null; started_at: string; completed_at: string | null; reset_at: string | null; created_by_role: string; summary: string; outcome_summary: string | null; steps: DemoScenarioStep[]; artifacts: DemoScenarioArtifact[]; timeline: DemoScenarioEvent[]; next_action: DemoScenarioNextAction | null; }
export interface DemoScenarioSummary { scenario_count: number; enabled_scenarios: string[]; run_counts: Record<string, number>; active_runs: number; safe_local_only: boolean; real_model_called_by_readiness: boolean; autonomous_remediation_enabled: boolean; }

export const getDemoScenarioSummary = () => request<DemoScenarioSummary>("/api/v1/demo-scenarios/summary");
export const getDemoScenarioCatalog = () => request<DemoScenario[]>("/api/v1/demo-scenarios/catalog");
export const getDemoScenarioRuns = () => request<DemoScenarioRun[]>("/api/v1/demo-scenarios/runs");
export const getDemoScenarioRun = (runId: string) => request<DemoScenarioRun>(`/api/v1/demo-scenarios/runs/${encodeURIComponent(runId)}`);
export const startDemoScenario = (scenarioCode: string) => request<DemoScenarioRun>(`/api/v1/demo-scenarios/${encodeURIComponent(scenarioCode)}/start`, { method: "POST", body: JSON.stringify({ created_by_role: "DEMO_PRESENTER" }) });
export const advanceDemoScenario = (runId: string) => request<DemoScenarioRun>(`/api/v1/demo-scenarios/runs/${encodeURIComponent(runId)}/advance`, { method: "POST", body: "{}" });
export const completeDemoScenarioStep = (runId: string, stepCode: string) => request<DemoScenarioRun>(`/api/v1/demo-scenarios/runs/${encodeURIComponent(runId)}/steps/${encodeURIComponent(stepCode)}/complete`, { method: "POST", body: "{}" });
export const resetDemoScenario = (runId: string) => request<DemoScenarioRun>(`/api/v1/demo-scenarios/runs/${encodeURIComponent(runId)}/reset`, { method: "POST", body: JSON.stringify({ reset_reason: "Presenter reset the guided demo." }) });
export const getDemoScenarioTimeline = (runId: string) => request<DemoScenarioEvent[]>(`/api/v1/demo-scenarios/runs/${encodeURIComponent(runId)}/timeline`);
export const getDemoScenarioArtifacts = (runId: string) => request<DemoScenarioArtifact[]>(`/api/v1/demo-scenarios/runs/${encodeURIComponent(runId)}/artifacts`);
export const getDemoScenarioNextAction = (runId: string) => request<DemoScenarioNextAction | null>(`/api/v1/demo-scenarios/runs/${encodeURIComponent(runId)}/next-action`);
