const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`UI acceptance API returned ${response.status}: ${body?.detail || "request failed"}`);
  return body as T;
}

export interface UiStepResult { id: string; suite_code: string; case_code: string; step_code: string; status: string; observed_result?: string | null; evidence_note?: string | null; screenshot_reference?: string | null; defect_note?: string | null; tested_by_role: string; tested_at: string; }
export interface UiTestStep { id: string; step_code: string; case_code: string; step_order: number; instruction: string; target_url: string; what_to_click: string; expected_result: string; evidence_to_capture: string; is_mutating_step: boolean; safety_note: string; result: UiStepResult | null; }
export interface UiTestCase { id: string; case_code: string; suite_code: string; title: string; description: string; preconditions: string; expected_outcome: string; primary_url: string; steps: UiTestStep[]; }
export interface UiTestSuite { id: string; suite_code: string; title: string; description: string; experience: string; sort_order: number; is_enabled: boolean; case_count: number; step_count: number; }
export interface UiTestRun { id: string; run_id: string; run_title: string; status: string; tester_role: string; suite_codes: string[]; started_at: string; completed_at: string | null; summary: string | null; progress: { total_steps: number; tested_steps: number; coverage_percent: number }; cases: UiTestCase[]; events: { id: string; event_type: string; event_title: string; event_description: string; created_at: string }[]; }
export interface UiAcceptanceSummary { read_only_catalog: boolean; enabled_suites: number; total_suites: number; total_cases: number; total_steps: number; total_runs: number; latest_run_id: string | null; latest_run_status: string | null; latest_run: UiTestRun | null; coverage: UiCoverage; safe_local_only: boolean; browser_automation_enabled: boolean; real_model_called_by_readiness: boolean; external_services_required: boolean; safety_note: string; }
export interface UiCoverage { total_enabled_steps: number; recorded_results: number; tested_steps: number; passed_steps: number; failed_steps: number; warning_steps: number; coverage_percent: number; classification: string; screenshot_upload_supported: boolean; }
export interface UiReport { run_id: string; run_title: string; tester_role: string; status: string; started_at: string; completed_at: string | null; summary: string | null; suite_summary: { suite_code: string; case_count: number; tested_steps: number; passed_steps: number; failed_steps: number }[]; status_counts: Record<string, number>; step_results: UiStepResult[]; coverage: UiCoverage; safety_confirmations: string[]; known_limitations: string[]; }

export const getUiAcceptanceSummary = () => request<UiAcceptanceSummary>("/api/v1/ui-acceptance/summary");
export const getUiAcceptanceSuites = () => request<UiTestSuite[]>("/api/v1/ui-acceptance/suites");
export const getUiAcceptanceCases = (suiteCode?: string) => request<UiTestCase[]>(`/api/v1/ui-acceptance/cases${suiteCode ? `?suite_code=${encodeURIComponent(suiteCode)}` : ""}`);
export const getUiAcceptanceCase = (caseCode: string) => request<UiTestCase>(`/api/v1/ui-acceptance/cases/${encodeURIComponent(caseCode)}`);
export const getUiAcceptanceRuns = () => request<UiTestRun[]>("/api/v1/ui-acceptance/runs");
export const getUiAcceptanceRun = (runId: string) => request<UiTestRun>(`/api/v1/ui-acceptance/runs/${encodeURIComponent(runId)}`);
export const getUiAcceptanceReport = (runId: string) => request<UiReport>(`/api/v1/ui-acceptance/runs/${encodeURIComponent(runId)}/report`);
export const getUiAcceptanceMarkdownUrl = (runId: string) => `${apiBaseUrl}/api/v1/ui-acceptance/runs/${encodeURIComponent(runId)}/report.md`;
export const getUiAcceptanceCoverage = () => request<UiCoverage>("/api/v1/ui-acceptance/coverage");
export const startUiAcceptanceRun = (run_title: string, tester_role: string, suite_codes: string[]) => request<UiTestRun>("/api/v1/ui-acceptance/runs/start", { method: "POST", body: JSON.stringify({ run_title, tester_role, suite_codes }) });
export const saveUiStepResult = (runId: string, payload: { suite_code: string; case_code: string; step_code: string; status: string; observed_result: string; evidence_note: string; screenshot_reference: string; defect_note: string; tested_by_role: string }) => request<UiTestRun>(`/api/v1/ui-acceptance/runs/${encodeURIComponent(runId)}/step-results`, { method: "POST", body: JSON.stringify(payload) });
export const completeUiAcceptanceRun = (runId: string, summary: string) => request<UiTestRun>(`/api/v1/ui-acceptance/runs/${encodeURIComponent(runId)}/complete`, { method: "POST", body: JSON.stringify({ summary }) });
export const abortUiAcceptanceRun = (runId: string, summary: string) => request<UiTestRun>(`/api/v1/ui-acceptance/runs/${encodeURIComponent(runId)}/abort`, { method: "POST", body: JSON.stringify({ summary }) });
