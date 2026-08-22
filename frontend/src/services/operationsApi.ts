const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface OperationalException {
  id: string;
  exception_number: string;
  exception_type: string;
  severity: string;
  status: string;
  source_module: string;
  source_entity_type: string;
  source_entity_id: string | null;
  source_reference: string | null;
  title: string;
  description: string;
  detection_method: string;
  business_impact: string;
  technical_context: Record<string, unknown> | null;
  first_detected_at: string;
  last_detected_at: string;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
  linked_ticket_id: string | null;
  linked_ticket_number: string | null;
}

export interface SimulationResult {
  simulation_type: string;
  exception: OperationalException;
  ticket: { id: string; ticket_number: string; status: string; priority: string } | null;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = (await response.json().catch(() => ({}))) as T | { detail?: unknown };
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body ? String(body.detail) : "request failed";
    throw new Error(`Operations API returned ${response.status}: ${detail}`);
  }
  return body as T;
}

export function getExceptions(params: { status?: string; severity?: string; exception_type?: string } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value) search.set(key, value); });
  return request<OperationalException[]>("/api/v1/operations/exceptions" + (search.size ? `?${search.toString()}` : ""));
}

export function acknowledgeException(id: string) {
  return request<OperationalException>(`/api/v1/operations/exceptions/${id}/acknowledge`, { method: "POST" });
}

export function resolveException(id: string) {
  return request<OperationalException>(`/api/v1/operations/exceptions/${id}/resolve`, { method: "POST" });
}

export function createTicketFromException(id: string) {
  return request<{ id: string; ticket_number: string }>(`/api/v1/ams/tickets/from-exception/${id}`, { method: "POST" });
}

export function simulateLowStock(create_ticket: boolean) {
  return request<SimulationResult>("/api/v1/operations/simulations/low-stock", { method: "POST", body: JSON.stringify({ create_ticket }) });
}

export function simulateTaskBlocked(create_ticket: boolean) {
  return request<SimulationResult>("/api/v1/operations/simulations/task-blocked", { method: "POST", body: JSON.stringify({ create_ticket, reason: "Picker device unavailable" }) });
}

export function simulateShipmentException(create_ticket: boolean) {
  return request<SimulationResult>("/api/v1/operations/simulations/shipment-exception", { method: "POST", body: JSON.stringify({ create_ticket, reason: "Carrier label generation failed" }) });
}

export function simulateOrderStuck(create_ticket: boolean) {
  return request<SimulationResult>("/api/v1/operations/simulations/order-stuck", { method: "POST", body: JSON.stringify({ create_ticket, status: "PICKING" }) });
}

