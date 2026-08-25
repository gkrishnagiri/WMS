const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { headers: { "Content-Type": "application/json" } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Executive demo API returned ${response.status}: ${body?.detail || "request failed"}`);
  return body as T;
}

export interface ExecutiveSummary { title: string; headline: string; read_only: boolean; disclaimer: string; kpis: Record<string, number | string>; operating_model: string; scenario_status: Record<string, number>; governance_status: Record<string, string | boolean>; }
export interface ValueMetrics { metric_classification: string; disclaimer: string; scenario_execution: Record<string, number>; issue_to_investigation: Record<string, number>; evidence_and_knowledge: Record<string, number>; model_assisted_readiness: Record<string, unknown>; approval_gated_actions: Record<string, number>; governance_and_audit: Record<string, number>; effort_impact: { estimated_manual_effort_baseline_minutes: number; estimated_agent_assisted_effort_minutes: number; estimated_effort_avoided_minutes: number; estimated_effort_avoided_percent: number; label: string; disclaimer: string; assumptions: { assumption_code: string; title: string; description: string; value: number; unit: string; label: string; is_demo_assumption: boolean }[] }; }
export interface ScenarioOutcome { scenario_code: string; title: string; business_problem: string; business_value: string; source_signals: string[]; agent_capabilities: string[]; generated_artifacts: number; run_count: number; latest_run_status: string; latest_run_id: string | null; deep_link: string; }
export interface StoryboardSection { section_code: string; title: string; message: string; proof_points?: string[]; scenarios?: ScenarioOutcome[]; }
export interface Storyboard { title: string; disclaimer: string; sections: StoryboardSection[]; }
export interface Governance { title: string; real_model_default: string; real_model_enabled: boolean; api_key_required_for_demo: boolean; api_key_present: boolean; provider_model_readiness: Record<string, unknown>; stage_1: string; stage_2: string; autonomous_remediation: boolean; prohibited_execution: string[]; audit: Record<string, number>; safety_controls: string[]; }
export interface OperatingModel { title: string; maturity: string; value_chain: { step: string; description: string; link: string }[]; speed: string; quality: string; reuse: string; governance: string; auditability: string; }
export interface CommercialModel { title: string; disclaimer: string; rows: { traditional_model: string; ai_native_alternative: string; value_lever: string; demo_metric: string; risk_allocation_impact: string }[]; }
export interface DeepLink { label: string; path: string; experiences: string[]; }

export const getExecutiveSummary = () => request<ExecutiveSummary>("/api/v1/executive-demo/summary");
export const getExecutiveValueMetrics = () => request<ValueMetrics>("/api/v1/executive-demo/value-metrics");
export const getExecutiveStoryboard = () => request<Storyboard>("/api/v1/executive-demo/storyboard");
export const getExecutiveScenarioOutcomes = () => request<ScenarioOutcome[]>("/api/v1/executive-demo/scenario-outcomes");
export const getExecutiveGovernance = () => request<Governance>("/api/v1/executive-demo/governance");
export const getExecutiveOperatingModel = () => request<OperatingModel>("/api/v1/executive-demo/operating-model");
export const getExecutiveCommercialModel = () => request<CommercialModel>("/api/v1/executive-demo/commercial-model");
export const getExecutiveDeepLinks = () => request<{ links: DeepLink[] }>("/api/v1/executive-demo/deep-links");
