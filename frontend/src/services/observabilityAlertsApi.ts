const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface AlertRule { id: string; rule_code: string; name: string; description: string; signal_type: string; source_system: string; metric_name: string | null; condition_operator: string; threshold_value: number | null; severity: string; enabled: boolean; cooldown_minutes: number; evaluation_window_minutes: number; target_experience: string; create_ticket_by_default: boolean; }
export interface AlertEvidence { id: string; evidence_type: string; title: string; summary: string; payload_json: Record<string, unknown> | null; source_url: string | null; created_at: string; }
export interface AlertEvent { id: string; event_id: string; rule_code: string; title: string; description: string; severity: string; status: string; source_signal: string; source_url: string | null; observed_value: number | null; threshold_value: number | null; condition_summary: string; first_seen_at: string; last_seen_at: string; occurrence_count: number; suppressed_count: number; ticket_creation_status: string; created_ticket_id: string | null; linked_ticket_number: string | null; evidence: AlertEvidence[]; }
export interface EvaluationRun { id: string; run_id: string; trigger_source: string; status: string; started_at: string; completed_at: string | null; rules_evaluated: number; events_created: number; events_suppressed: number; tickets_created: number; event_ids: string[]; }
export interface AlertSummary { rules: number; enabled_rules: number; open_events: number; ticketed_events: number; acknowledged_events: number; resolved_events: number; evaluation_runs: number; tickets_created: number; }

async function request<T>(path: string, options: RequestInit = {}): Promise<T> { const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } }); const body = await response.json().catch(() => ({})); if (!response.ok) throw new Error(`Observability alerts API returned ${response.status}: ${body?.detail || "request failed"}`); return body as T; }
export const getAlertSummary = () => request<AlertSummary>("/api/v1/observability-alerts/summary");
export const getAlertRules = () => request<AlertRule[]>("/api/v1/observability-alerts/rules");
export const setAlertRuleEnabled = (id: string, enabled: boolean) => request<AlertRule>(`/api/v1/observability-alerts/rules/${id}/${enabled ? "enable" : "disable"}`, { method: "POST" });
export const evaluateAlerts = () => request<EvaluationRun>("/api/v1/observability-alerts/evaluate", { method: "POST", body: JSON.stringify({ trigger_source: "MANUAL" }) });
export const evaluateAlertRule = (id: string) => request<EvaluationRun>(`/api/v1/observability-alerts/evaluate/${id}`, { method: "POST", body: JSON.stringify({ trigger_source: "MANUAL" }) });
export const getEvaluationRuns = () => request<EvaluationRun[]>("/api/v1/observability-alerts/evaluation-runs");
export const getAlertEvents = () => request<AlertEvent[]>("/api/v1/observability-alerts/events");
export const getAlertEvent = (id: string) => request<AlertEvent>(`/api/v1/observability-alerts/events/${id}`);
export const acknowledgeAlertEvent = (id: string) => request<AlertEvent>(`/api/v1/observability-alerts/events/${id}/acknowledge`, { method: "POST" });
export const resolveAlertEvent = (id: string) => request<AlertEvent>(`/api/v1/observability-alerts/events/${id}/resolve`, { method: "POST" });
export const createTicketFromAlertEvent = (id: string) => request<{ id: string; ticket_number: string }>(`/api/v1/observability-alerts/events/${id}/create-ticket`, { method: "POST" });
