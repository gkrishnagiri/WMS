const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string): Promise<T> {
  const response = await fetch(apiBaseUrl + path);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Baseline completion API returned ${response.status}: ${body?.detail || "request failed"}`);
  return body as T;
}

export interface BaselineSummary { baseline_name: string; baseline_version: string; completion_status: string; completed_prompt_range: string; capability_count: number; scenario_count: number; stage_modes_supported: string[]; real_model_default_enabled: boolean; stage3_autonomous_execution_default_enabled: boolean; service_now_enabled: boolean; authentication_enabled: boolean; recommended_start_url: string; recommended_demo_flow: string[]; warnings: string[]; read_only: boolean; safety_boundary: string; generated_at: string; }
export interface Requirement { requirement_id: string; category: string; requirement: string; status: string; implemented_by_prompts: string[]; primary_ui_routes: string[]; primary_api_routes: string[]; evidence_source: string; test_coverage: string; notes: string; }
export interface WalkthroughStep { step_number: number; instruction: string; page_url: string; what_to_click: string; expected_result: string; evidence_to_capture: string; }
export interface Walkthrough { walkthrough_id: string; title: string; audience: string; estimated_duration_minutes: number; start_experience: string; start_url: string; preconditions: string[]; steps: WalkthroughStep[]; expected_outcomes: string[]; evidence_to_capture: string[]; reset_instructions: string; }
export interface Limitation { limitation_id: string; area: string; description: string; impact: string; status: string; future_phase_recommendation: string; }
export interface SignoffSection { area: string; items: { item: string; status: string; evidence_url_or_route: string; validation_method: string; notes: string; }[]; }

export const getBaselineSummary = () => request<BaselineSummary>("/api/v1/baseline-completion/summary");
export const getRequirements = () => request<{ requirements: Requirement[]; summary: Record<string, number>; read_only: boolean }>("/api/v1/baseline-completion/requirements");
export const getWalkthroughs = () => request<{ walkthroughs: Walkthrough[]; read_only: boolean }>("/api/v1/baseline-completion/walkthroughs");
export const getDemoJourneys = () => request<{ journeys: Record<string, unknown>[]; read_only: boolean }>("/api/v1/baseline-completion/demo-journeys");
export const getResetGuide = () => request<Record<string, unknown>>("/api/v1/baseline-completion/reset-guide");
export const getTestingGuide = () => request<Record<string, unknown>>("/api/v1/baseline-completion/testing-guide");
export const getModelGuide = () => request<Record<string, unknown>>("/api/v1/baseline-completion/model-guide");
export const getStageModes = () => request<{ stage_modes: Record<string, unknown>[]; read_only: boolean }>("/api/v1/baseline-completion/stage-modes");
export const getLimitations = () => request<{ limitations: Limitation[]; read_only: boolean }>("/api/v1/baseline-completion/known-limitations");
export const getSignoff = () => request<{ sections: SignoffSection[]; overall_status: string; read_only: boolean }>("/api/v1/baseline-completion/signoff-checklist");
export const getHandoverPack = () => request<Record<string, unknown>>("/api/v1/baseline-completion/handover-pack");
export const getHandoverMarkdown = () => requestText("/api/v1/baseline-completion/handover-pack.md");

async function requestText(path: string): Promise<string> {
  const response = await fetch(apiBaseUrl + path);
  if (!response.ok) throw new Error(`Baseline handover API returned ${response.status}`);
  return response.text();
}
