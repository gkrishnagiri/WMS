import type { ExperienceCode } from "./experience";

export interface NavigationItem {
  label: string;
  path: string;
  experiences: ExperienceCode[];
}

const allExperiences: ExperienceCode[] = ["full", "business", "operations", "simulation", "observability", "agentic"];

export const navigation: NavigationItem[] = [
  { label: "Dashboard", path: "/", experiences: allExperiences },
  { label: "Demo Control", path: "/demo-control", experiences: ["full"] },
  { label: "Warehouse", path: "/warehouse", experiences: ["full", "business"] },
  { label: "Inventory", path: "/warehouse/inventory", experiences: ["full", "business"] },
  { label: "Orders", path: "/warehouse/orders", experiences: ["full", "business"] },
  { label: "Fulfillment Tasks", path: "/warehouse/tasks", experiences: ["full", "business"] },
  { label: "Shipments", path: "/warehouse/shipments", experiences: ["full", "business"] },
  { label: "Inventory Transactions", path: "/warehouse/inventory-transactions", experiences: ["full", "business"] },
  { label: "Operations Exceptions", path: "/operations/exceptions", experiences: ["full", "operations"] },
  { label: "AMS Tickets", path: "/ams/tickets", experiences: ["full", "operations"] },
  { label: "Synthetic Journeys", path: "/synthetic-users/journeys", experiences: ["full", "simulation"] },
  { label: "Journey Runs", path: "/synthetic-users/runs", experiences: ["full", "simulation"] },
  { label: "User Reports", path: "/ams/user-reports", experiences: ["full", "operations"] },
  { label: "Monitoring Alerts", path: "/monitoring/alerts", experiences: ["full", "operations"] },
  { label: "Monitoring Simulations", path: "/monitoring/simulations", experiences: ["full", "simulation"] },
  { label: "Monitoring Triage", path: "/monitoring/triage", experiences: ["full", "operations"] },
  { label: "Observability", path: "/observability", experiences: ["full", "observability"] },
  { label: "Traces", path: "/observability/traces", experiences: ["full", "observability"] },
  { label: "Logs", path: "/observability/logs", experiences: ["full", "observability"] },
  { label: "Metrics", path: "/observability/metrics", experiences: ["full", "observability"] },
  { label: "Diagnostics", path: "/observability/diagnostics", experiences: ["full", "operations", "observability"] },
  { label: "Observability Simulations", path: "/observability/simulations", experiences: ["full", "simulation"] },
  { label: "Batch Jobs", path: "/batch/jobs", experiences: ["full", "simulation"] },
  { label: "Batch Runs", path: "/batch/runs", experiences: ["full", "operations", "simulation"] },
  { label: "Batch Simulations", path: "/batch/simulations", experiences: ["full", "simulation"] },
  { label: "Copilot", path: "/copilot", experiences: ["full", "agentic"] },
  { label: "Copilot Sessions", path: "/copilot/sessions", experiences: ["full", "operations", "agentic"] },
  { label: "AI Config", path: "/ai-config", experiences: ["full", "agentic"] },
  { label: "AI Providers", path: "/ai-config/providers", experiences: ["full", "agentic"] },
  { label: "AI Prompts", path: "/ai-config/prompts", experiences: ["full", "agentic"] },
  { label: "AI Invocations", path: "/ai-config/invocations", experiences: ["full", "agentic"] },
  { label: "AI Safety", path: "/ai-config/safety", experiences: ["full", "agentic"] },
  { label: "AI Usage", path: "/ai-config/usage", experiences: ["full", "agentic"] },
  { label: "AI Test", path: "/ai-config/test", experiences: ["full", "agentic"] },
  { label: "Runtime Observability", path: "/observability/runtime", experiences: ["full", "observability"] },
  { label: "Runtime Traces", path: "/observability/runtime/traces", experiences: ["full", "observability"] },
  { label: "Observability Stack", path: "/observability/stack", experiences: ["full", "observability"] },
  { label: "Stack Health", path: "/observability/stack/health", experiences: ["full", "observability"] },
  { label: "Stack Test", path: "/observability/stack/test", experiences: ["full", "observability", "simulation"] },
  { label: "Grafana Dashboards", path: "/observability/dashboards", experiences: ["full", "observability"] },
  { label: "Health", path: "/health", experiences: allExperiences },
  { label: "About", path: "/about", experiences: allExperiences },
];

export function navigationForExperience(code: ExperienceCode): NavigationItem[] {
  return navigation.filter((item) => item.experiences.includes(code));
}
