const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface StackSummary { otel_enabled: boolean; otel_available: boolean; service_name: string; collector_endpoint: string; traces_enabled: boolean; logs_enabled: boolean; metrics_enabled: boolean; tempo_url: string; loki_url: string; prometheus_url: string; grafana_url: string; initialization_error: string | null; }
export interface StackHealthComponent { name: string; url: string; status: string; detail: string | null; }
export interface StackHealth { status: string; components: StackHealthComponent[]; }
export interface TestAction { status: string; message: string; trace_id: string | null; span_id: string | null; metric_name: string | null; }
export interface TestAll { span: TestAction; log: TestAction; metric: TestAction; }

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Observability stack API returned ${response.status}: ${typeof body === "object" && body?.detail ? body.detail : "request failed"}`);
  return body as T;
}
export const getStackSummary = () => request<StackSummary>("/api/v1/observability-stack/summary");
export const getStackHealth = () => request<StackHealth>("/api/v1/observability-stack/health");
export const getStackConfig = () => request<Record<string, unknown>>("/api/v1/observability-stack/config");
export const runStackTestSpan = () => request<TestAction>("/api/v1/observability-stack/test-span", { method: "POST", body: "{}" });
export const runStackTestLog = () => request<TestAction>("/api/v1/observability-stack/test-log", { method: "POST", body: "{}" });
export const runStackTestMetric = () => request<TestAction>("/api/v1/observability-stack/test-metric", { method: "POST", body: "{}" });
export const runStackTestAll = () => request<TestAll>("/api/v1/observability-stack/test-all", { method: "POST", body: "{}" });
