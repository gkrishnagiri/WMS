const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");
async function request<T>(path: string, options?: RequestInit): Promise<T> { const response = await fetch(apiBaseUrl + path, { headers: { "Content-Type": "application/json" }, ...options }); const body = await response.json().catch(() => ({})); if (!response.ok) throw new Error(body?.detail || `Request failed: ${response.status}`); return body as T; }
export interface CostModel { model_code: string; external_model_name: string; display_name: string; provider_code: string; enabled: boolean; provider_enabled: boolean; supports_real_invocation: boolean; pricing_configured: boolean; pricing_status: string; pricing: Record<string, unknown> | null; }
export interface CostSummary { real_model_enabled: boolean; api_key_present: boolean; provider_enabled: boolean; active_model_count: number; pricing_configured_count: number; total_invocations: number; total_input_tokens: number; total_completion_tokens: number; total_tokens: number; estimated_total_cost: number; cost_today: number; safe_to_invoke: boolean; reason: string; pricing_warning: string; }
export const getAiCostingSummary = () => request<CostSummary>("/api/v1/ai-costing/summary");
export const getAiCostingModels = () => request<CostModel[]>("/api/v1/ai-costing/models");
export const createAiCostingModel = (body: Record<string, unknown>) => request<CostModel>("/api/v1/ai-costing/models", { method: "POST", body: JSON.stringify(body) });
export const deleteAiCostingModel = (code: string) => request<Record<string, unknown>>(`/api/v1/ai-costing/models/${encodeURIComponent(code)}`, { method: "DELETE" });
export const updateAiModelPricing = (code: string, body: Record<string, unknown>) => request<Record<string, unknown>>(`/api/v1/ai-costing/models/${encodeURIComponent(code)}/pricing`, { method: "PUT", body: JSON.stringify(body) });
export const getAiCostingUsage = () => request<Record<string, unknown>[]>("/api/v1/ai-costing/usage");
export const getAiCostingByModel = () => request<Record<string, unknown>[]>("/api/v1/ai-costing/usage/by-model");
export const getAiCostingGuardrails = () => request<Record<string, unknown>>("/api/v1/ai-costing/guardrails");
export const dryRunAiSmoke = (body: Record<string, unknown>) => request<Record<string, unknown>>("/api/v1/ai-costing/smoke-test/dry-run", { method: "POST", body: JSON.stringify(body) });
export const runAiSmoke = (body: Record<string, unknown>) => request<Record<string, unknown>>("/api/v1/ai-costing/smoke-test/run", { method: "POST", body: JSON.stringify(body) });
