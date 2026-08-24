const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface DemoExperience {
  code: string;
  name: string;
  frontend_url: string;
  backend_url: string;
  purpose: string;
}

export interface DemoSummary {
  application: string;
  mode: string;
  summary: { frontends: number; backends: number; infrastructure_components: number };
  overall_status: string;
  experiences: DemoExperience[];
  observability: Record<string, string>;
}

export interface DemoReadinessItem {
  name: string;
  kind: string;
  url: string;
  expected_status: number | string;
  actual_status: number | string | null;
  healthy: boolean;
  message: string;
}

export interface DemoReadiness {
  overall_status: string;
  checked_at: string;
  items: DemoReadinessItem[];
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Demo control API returned ${response.status}`);
  return body as T;
}

export const getDemoSummary = () => request<DemoSummary>("/api/v1/demo-control/summary");
export const getDemoComponents = () => request<Record<string, unknown>>("/api/v1/demo-control/components");
export const getDemoUrls = () => request<Record<string, unknown>>("/api/v1/demo-control/urls");
export const getDemoReadiness = () => request<DemoReadiness>("/api/v1/demo-control/readiness");
