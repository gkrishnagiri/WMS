const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface MonitoringSummary { open_alerts: number; critical_alerts: number; high_alerts: number; acknowledged_alerts: number; suppressed_alerts: number; open_triage_cases: number; alerts_linked_to_tickets: number; noisiest_component: string | null; }
export interface MonitoringComponent { id: string; component_code: string; name: string; component_type: string; layer: string; status: string; owner_team: string; description: string; }
export interface AlertRule { id: string; rule_code: string; name: string; component_id: string; component_code: string; metric_name: string; condition_operator: string; threshold_value: number; severity: string; enabled: boolean; dedupe_window_minutes: number; description: string; }
export interface MonitoringAlert { id: string; alert_number: string; rule_id: string; rule_code: string; component_id: string; component_code: string; component_name: string; severity: string; status: string; signal_type: string; metric_name: string; observed_value: number; threshold_value: number; title: string; description: string; first_seen_at: string; last_seen_at: string; occurrence_count: number; acknowledged_at: string | null; suppressed_at: string | null; resolved_at: string | null; linked_ticket_id: string | null; linked_ticket_number: string | null; }
export interface SimulationResult { simulation_code: string; alerts_created: number; alerts_repeated: number; alerts_open: number; highest_severity: string | null; simulation_summary: string; alerts: MonitoringAlert[]; }
export interface TriageAlert { id: string; alert_number: string; component_code: string; severity: string; status: string; metric_name: string; title: string; }
export interface TriageCase { id: string; case_number: string; title: string; description: string; status: string; severity: string; suspected_impact: string; suspected_root_cause: string | null; confidence_level: string; analysis_notes: string | null; linked_ticket_id: string | null; linked_ticket_number: string | null; created_by: string; created_at: string; updated_at: string; acknowledged_at: string | null; resolved_at: string | null; closed_at: string | null; alert_count: number; alerts: TriageAlert[]; }

async function request<T>(path: string, options: RequestInit = {}): Promise<T> { const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } }); const body = await response.json().catch(() => ({})); if (!response.ok) throw new Error(`Monitoring API returned ${response.status}: ${typeof body === "object" && body?.detail ? body.detail : "request failed"}`); return body as T; }
export const getMonitoringSummary = () => request<MonitoringSummary>("/api/v1/monitoring/summary");
export const getMonitoringComponents = () => request<MonitoringComponent[]>("/api/v1/monitoring/components");
export const getAlertRules = () => request<AlertRule[]>("/api/v1/monitoring/rules");
export function getMonitoringAlerts(params: { status?: string } = {}) { const query = params.status ? `?status=${encodeURIComponent(params.status)}` : ""; return request<MonitoringAlert[]>(`/api/v1/monitoring/alerts${query}`); }
export const acknowledgeAlert = (id: string) => request<MonitoringAlert>(`/api/v1/monitoring/alerts/${id}/acknowledge`, { method: "POST" });
export const suppressAlert = (id: string) => request<MonitoringAlert>(`/api/v1/monitoring/alerts/${id}/suppress`, { method: "POST" });
export const resolveAlert = (id: string) => request<MonitoringAlert>(`/api/v1/monitoring/alerts/${id}/resolve`, { method: "POST" });
export const createTicketFromAlert = (id: string) => request<{ id: string; ticket_number: string }>(`/api/v1/monitoring/alerts/${id}/create-ticket`, { method: "POST" });
export const runMonitoringSimulation = (code: string) => request<SimulationResult>(`/api/v1/monitoring/simulations/${code}`, { method: "POST", body: "{}" });
export const getTriageCases = () => request<TriageCase[]>("/api/v1/monitoring/triage-cases");
export const getTriageCase = (id: string) => request<TriageCase>(`/api/v1/monitoring/triage-cases/${id}`);
export const createTriageCase = (payload: { title: string; description: string; severity: string; suspected_impact: string; suspected_root_cause?: string; confidence_level: string; alert_ids: string[] }) => request<TriageCase>("/api/v1/monitoring/triage-cases", { method: "POST", body: JSON.stringify(payload) });
export const addAlertsToTriageCase = (id: string, alert_ids: string[]) => request<TriageCase>(`/api/v1/monitoring/triage-cases/${id}/add-alerts`, { method: "POST", body: JSON.stringify({ alert_ids }) });
export const startTriageInvestigation = (id: string) => request<TriageCase>(`/api/v1/monitoring/triage-cases/${id}/start-investigation`, { method: "POST" });
export const resolveTriageCase = (id: string, analysis_notes: string) => request<TriageCase>(`/api/v1/monitoring/triage-cases/${id}/resolve`, { method: "POST", body: JSON.stringify({ analysis_notes }) });
export const createTicketFromTriageCase = (id: string) => request<{ id: string; ticket_number: string }>(`/api/v1/monitoring/triage-cases/${id}/create-ticket`, { method: "POST" });
