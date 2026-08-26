const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error((await response.text()) || `Request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export interface AgentModelStatus {
  real_model_enabled: boolean; provider_code: string; model_code: string; default_model: string;
  provider_configured: boolean; model_configured: boolean; api_key_present: boolean;
  provider_enabled: boolean; model_enabled: boolean; safe_to_invoke: boolean; reason: string;
  allowed_task_types: string[]; max_context_items: number; max_input_chars: number;
  daily_usage: { invocations: number; estimated_cost: number; max_invocations: number; max_estimated_cost: number; cost_tracking_status: string };
  stage_mode: string;
}
export interface AgentModelContext { session_id: string; task_type: string; context_package: { context_items: Array<Record<string, unknown>>; [key: string]: unknown }; validation_issues: string[]; model_call_made: boolean; }
export interface AgentModelAsk { session_id: string; answer: string; generation_mode: string; safety_status: string; fallback_used: boolean; invocation_id: string | null; invocation_number: string | null; metadata: Record<string, unknown>; actions_executed: number; }

export const getAgentModelStatus = () => request<AgentModelStatus>("/api/v1/agent-model-chat/status");
export const previewAgentModelContext = (sessionId: string, messageText: string) => request<AgentModelContext>(`/api/v1/agent-model-chat/sessions/${sessionId}/preview-context`, { method: "POST", body: JSON.stringify({ message_text: messageText, task_type: "AGENT_STAGE_1_CHAT" }) });
export const dryRunAgentModel = (sessionId: string, messageText: string, useRealModel = true, modelCode?: string) => request<AgentModelContext>(`/api/v1/agent-model-chat/sessions/${sessionId}/dry-run`, { method: "POST", body: JSON.stringify({ message_text: messageText, use_real_model: useRealModel, provider_code: "OPENAI_RESPONSES", model_code: modelCode, task_type: "AGENT_STAGE_1_CHAT" }) });
export const askAgentModel = (sessionId: string, messageText: string, useRealModel = false, modelCode?: string) => request<AgentModelAsk>(`/api/v1/agent-model-chat/sessions/${sessionId}/ask`, { method: "POST", body: JSON.stringify({ message_text: messageText, use_real_model: useRealModel, provider_code: useRealModel ? "OPENAI_RESPONSES" : undefined, model_code: modelCode, task_type: "AGENT_STAGE_1_CHAT" }) });
export const getAgentModelInvocations = () => request<Record<string, unknown>[]>("/api/v1/agent-model-chat/invocations");
