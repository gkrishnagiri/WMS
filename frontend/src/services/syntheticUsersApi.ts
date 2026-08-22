const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface SyntheticUser {
  id: string;
  user_code: string;
  display_name: string;
  persona: string;
  department: string;
  role: string;
  email: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SyntheticJourney {
  id: string;
  journey_code: string;
  name: string;
  description: string;
  persona: string;
  journey_type: string;
  expected_outcome: string;
  creates_user_report_on_failure: boolean;
  creates_ticket_on_failure: boolean;
  enabled: boolean;
  default_payload: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface JourneyRun {
  id: string;
  run_number: string;
  journey_id: string;
  journey_code: string;
  journey_name: string;
  synthetic_user_id: string;
  synthetic_user_name: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  input_payload: Record<string, unknown> | null;
  result_payload: Record<string, unknown> | null;
  failure_type: string | null;
  failure_message: string | null;
  order_id: string | null;
  task_id: string | null;
  shipment_id: string | null;
  user_report_id: string | null;
  user_report_number: string | null;
  ticket_id: string | null;
  ticket_number: string | null;
  created_at: string;
  updated_at: string;
}

export interface RunSuiteResult {
  total: number;
  succeeded: number;
  failed: number;
  runs: JourneyRun[];
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = (await response.json().catch(() => ({}))) as T | { detail?: unknown };
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body ? String(body.detail) : "request failed";
    throw new Error(`Synthetic Users API returned ${response.status}: ${detail}`);
  }
  return body as T;
}

export function getSyntheticUsers() { return request<SyntheticUser[]>("/api/v1/synthetic-users/users"); }
export function getSyntheticJourneys() { return request<SyntheticJourney[]>("/api/v1/synthetic-users/journeys"); }
export function runJourney(journeyCode: string, create_ticket: boolean, input_payload: Record<string, unknown> = {}) { return request<JourneyRun>(`/api/v1/synthetic-users/journeys/${journeyCode}/run`, { method: "POST", body: JSON.stringify({ create_ticket, input_payload }) }); }
export function runSyntheticSuite(create_ticket: boolean) { return request<RunSuiteResult>("/api/v1/synthetic-users/run-suite", { method: "POST", body: JSON.stringify({ create_ticket }) }); }
export function getJourneyRuns(params: { journey_code?: string; status?: string } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value) search.set(key, value); });
  return request<JourneyRun[]>("/api/v1/synthetic-users/runs" + (search.size ? `?${search.toString()}` : ""));
}

