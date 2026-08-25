const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Demo readiness API returned ${response.status}: ${body?.detail || "request failed"}`);
  return body as T;
}

export interface ReadinessCheck { name: string; check_code: string; status: string; healthy: boolean; critical: boolean; message: string; value?: number | string | boolean | null; }
export interface ReadinessSummary { status: string; readiness_score: number; demo_mode: string; critical_checks_passed: number; critical_checks_failed: number; warnings: string[]; real_model_default_enabled: boolean; autonomous_remediation_enabled: boolean; service_now_enabled: boolean; recommended_next_action: string; checked_at: string; }
export interface LauncherUrl { label: string; experience: string; url: string; description: string; recommended_order: number; }
export interface UrlResponse { urls: LauncherUrl[]; }
export interface GuideStep { step_number: number; page_url: string; what_to_click: string; expected_result: string; what_to_capture: string; pass_fail_hint: string; }
export interface GuideSection { title: string; steps: GuideStep[]; }
export interface TestGuide { title: string; description: string; sections: GuideSection[]; }
export interface ResetProfile { profile: string; purpose: string; confirmation_required: boolean; confirmation?: string; preserves: string[]; }
export interface ResetProfiles { profiles: ResetProfile[]; hard_delete_enabled: boolean; schema_drop_enabled: boolean; }
export interface ShowcaseResponse { mode: string; readiness: ReadinessSummary; reset_profiles: ResetProfiles; suggested_flow: string[]; urls: LauncherUrl[]; }
export interface SmokeReport { generated_at: string; stack_urls: Record<string, string>; readiness: ReadinessSummary; seed_counts: Record<string, number>; scenario_counts: Record<string, number>; investigation_counts: Record<string, number>; action_counts: Record<string, number>; model_default: Record<string, unknown>; bff_exposure: Record<string, boolean>; known_warnings: string[]; }

export const getDemoReadinessSummary = () => request<ReadinessSummary>("/api/v1/demo-readiness/summary");
export const getDemoReadinessChecks = () => request<{ checks: ReadinessCheck[]; summary: ReadinessSummary }>("/api/v1/demo-readiness/checks");
export const getDemoReadinessShowcase = () => request<ShowcaseResponse>("/api/v1/demo-readiness/showcase");
export const getDemoReadinessUrls = () => request<UrlResponse>("/api/v1/demo-readiness/urls");
export const getDemoReadinessGuide = () => request<TestGuide>("/api/v1/demo-readiness/ui-test-guide");
export const getDemoSmokeReport = () => request<SmokeReport>("/api/v1/demo-readiness/smoke-report");
export const getDemoResetProfiles = () => request<ResetProfiles>("/api/v1/demo-readiness/reset-profiles");
export const resetDemoReadiness = (profile: string, reset_reason: string, confirmation?: string) => request<Record<string, unknown>>("/api/v1/demo-readiness/reset", { method: "POST", body: JSON.stringify({ profile, reset_reason, confirmation }) });
export const prepareDemoShowcase = (create_prepared_runs: boolean) => request<Record<string, unknown>>("/api/v1/demo-readiness/prepare-showcase", { method: "POST", body: JSON.stringify({ profile: "SHOWCASE_RESET", create_prepared_runs, created_by_role: "DEMO_PRESENTER" }) });
