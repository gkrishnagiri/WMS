const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export interface HealthResponse {
  status: "healthy" | "unhealthy";
  application: string;
  version: string;
  environment: string;
  checks: {
    api: string;
    database: string;
    redis: string;
  };
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/health`);
  const body = (await response.json()) as HealthResponse;
  if (!response.ok) {
    throw new Error(`Backend health check returned ${response.status}: ${body.status}`);
  }
  return body;
}
