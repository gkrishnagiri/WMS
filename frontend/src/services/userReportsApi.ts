const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface ReportTicketSummary {
  id: string;
  ticket_number: string;
  status: string;
  priority: string;
}

export interface UserReport {
  id: string;
  report_number: string;
  reporter_user_id: string | null;
  reporter_name: string;
  reporter_email: string | null;
  reporter_persona: string | null;
  report_channel: string;
  source_module: string;
  affected_entity_type: string;
  affected_entity_id: string | null;
  title: string;
  description: string;
  business_impact: string;
  severity: string;
  status: string;
  journey_run_id: string | null;
  journey_run_number: string | null;
  journey_code: string | null;
  ticket_id: string | null;
  ticket: ReportTicketSummary | null;
  submitted_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserReportPayload {
  reporter_user_id?: string;
  reporter_name: string;
  reporter_email?: string;
  reporter_persona?: string;
  report_channel: string;
  source_module: string;
  affected_entity_type: string;
  affected_entity_id?: string;
  title: string;
  description: string;
  business_impact: string;
  severity: string;
  journey_run_id?: string;
  create_ticket: boolean;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = (await response.json().catch(() => ({}))) as T | { detail?: unknown };
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body ? String(body.detail) : "request failed";
    throw new Error(`User Reports API returned ${response.status}: ${detail}`);
  }
  return body as T;
}

export function getUserReports(params: { status?: string; severity?: string } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value) search.set(key, value); });
  return request<UserReport[]>("/api/v1/ams/user-reports" + (search.size ? `?${search.toString()}` : ""));
}
export function getUserReport(id: string) { return request<UserReport>(`/api/v1/ams/user-reports/${id}`); }
export function createUserReport(payload: UserReportPayload) { return request<UserReport>("/api/v1/ams/user-reports", { method: "POST", body: JSON.stringify(payload) }); }
export function createTicketFromUserReport(id: string) { return request<UserReport>(`/api/v1/ams/user-reports/${id}/create-ticket`, { method: "POST" }); }
export function acknowledgeUserReport(id: string) { return request<UserReport>(`/api/v1/ams/user-reports/${id}/acknowledge`, { method: "POST" }); }
export function resolveUserReport(id: string) { return request<UserReport>(`/api/v1/ams/user-reports/${id}/resolve`, { method: "POST" }); }

