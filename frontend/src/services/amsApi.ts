const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface TicketEvent {
  id: string;
  ticket_id: string;
  event_type: string;
  from_status: string | null;
  to_status: string | null;
  message: string;
  event_payload: Record<string, unknown> | null;
  created_by: string;
  created_at: string;
}

export interface TicketException {
  id: string;
  exception_number: string;
  exception_type: string;
  severity: string;
  status: string;
  title: string;
  description: string;
  source_reference: string | null;
}

export interface AmsTicket {
  id: string;
  ticket_number: string;
  ticket_type: string;
  severity: string;
  priority: string;
  status: string;
  source: string;
  source_module: string;
  exception_id: string | null;
  affected_entity_type: string | null;
  affected_entity_id: string | null;
  short_description: string;
  description: string;
  assignment_group: string;
  assigned_to: string | null;
  business_service: string;
  application_name: string;
  environment: string;
  opened_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  closed_at: string | null;
  resolution_code: string | null;
  resolution_notes: string | null;
  created_at: string;
  updated_at: string;
  exception: TicketException | null;
  events: TicketEvent[];
}

export interface AmsSummary {
  open_exceptions: number;
  critical_exceptions: number;
  open_tickets: number;
  p1_tickets: number;
  p2_tickets: number;
  tickets_in_progress: number;
  resolved_today: number;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = (await response.json().catch(() => ({}))) as T | { detail?: unknown };
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body ? String(body.detail) : "request failed";
    throw new Error(`AMS API returned ${response.status}: ${detail}`);
  }
  return body as T;
}

export function getAmsSummary() { return request<AmsSummary>("/api/v1/ams/summary"); }
export function getTickets() { return request<AmsTicket[]>("/api/v1/ams/tickets"); }
export function getTicket(id: string) { return request<AmsTicket>(`/api/v1/ams/tickets/${id}`); }
export function acknowledgeTicket(id: string) { return request<AmsTicket>(`/api/v1/ams/tickets/${id}/acknowledge`, { method: "POST" }); }
export function startTicketWork(id: string) { return request<AmsTicket>(`/api/v1/ams/tickets/${id}/start-work`, { method: "POST" }); }
export function resolveTicket(id: string, resolution_code: string, resolution_notes: string) { return request<AmsTicket>(`/api/v1/ams/tickets/${id}/resolve`, { method: "POST", body: JSON.stringify({ resolution_code, resolution_notes }) }); }
export function closeTicket(id: string) { return request<AmsTicket>(`/api/v1/ams/tickets/${id}/close`, { method: "POST" }); }

