export type ExperienceCode = "full" | "business" | "operations" | "simulation" | "observability" | "agentic";

export interface ExternalLink {
  label: string;
  url: string;
}

export interface ExperienceDefinition {
  code: ExperienceCode;
  displayName: string;
  description: string;
  defaultRoute: string;
  enabledRoutePrefixes: string[];
  externalLinks: ExternalLink[];
  helperText?: string;
}

const allRoutes = ["/"];

export const EXPERIENCE_CONFIG: Record<ExperienceCode, ExperienceDefinition> = {
  full: {
    code: "full",
    displayName: "Enterprise Operations Suite",
    description: "Full integrated EOS demo experience.",
    defaultRoute: "/",
    enabledRoutePrefixes: allRoutes,
    externalLinks: [],
  },
  business: {
    code: "business",
    displayName: "EOS Business Application",
    description: "Business-facing Warehouse & Fulfillment application.",
    defaultRoute: "/",
    enabledRoutePrefixes: [
      "/",
      "/warehouse",
      "/agent-chat/user",
      "/agent-knowledge/search",
      "/executive-demo",
      "/health",
      "/about",
    ],
    externalLinks: [],
    helperText: "Support, simulation, observability, and agentic controls are intentionally hidden from this business experience.",
  },
  operations: {
    code: "operations",
    displayName: "EOS Operations Console",
    description: "AMS and support operations console for support engineers.",
    defaultRoute: "/",
    enabledRoutePrefixes: [
      "/",
      "/operations/exceptions",
      "/ams/tickets",
      "/ams/user-reports",
      "/monitoring/alerts",
      "/monitoring/triage",
      "/observability/diagnostics",
      "/batch/runs",
      "/copilot/sessions",
      "/observability-alerts",
      "/agent-chat/engineer",
      "/agent-chat/cases",
      "/agent-chat/sessions",
      "/agent-investigations",
      "/demo-scenarios",
      "/executive-demo",
      "/agent-knowledge",
      "/agent-investigations",
      "/health",
      "/about",
    ],
    externalLinks: [],
    helperText: "Business workflows and simulation controls belong to the other EOS experiences.",
  },
  simulation: {
    code: "simulation",
    displayName: "EOS Simulation Lab",
    description: "Controlled synthetic-user, batch, monitoring, and fault-injection lab.",
    defaultRoute: "/",
    enabledRoutePrefixes: [
      "/",
      "/synthetic-users/journeys",
      "/synthetic-users/runs",
      "/batch/simulations",
      "/batch/jobs",
      "/batch/runs",
      "/monitoring/simulations",
      "/observability/simulations",
      "/observability/stack/test",
      "/demo-scenarios",
      "/executive-demo",
      "/health",
      "/about",
    ],
    externalLinks: [],
    helperText: "This lab generates deterministic failures and support evidence for demos and testing.",
  },
  observability: {
    code: "observability",
    displayName: "EOS Observability Control Plane",
    description: "Runtime telemetry, evidence views, and local observability stack controls.",
    defaultRoute: "/",
    enabledRoutePrefixes: [
      "/",
      "/observability",
      "/observability-alerts",
      "/health",
      "/about",
    ],
    externalLinks: [
      { label: "Grafana", url: "http://localhost:3001" },
      { label: "Prometheus", url: "http://localhost:9090" },
      { label: "Tempo", url: "http://localhost:3200" },
      { label: "Loki", url: "http://localhost:3100" },
    ],
    helperText: "Grafana remains the primary observability UI; EOS provides control-plane and correlation helpers.",
  },
  agentic: {
    code: "agentic",
    displayName: "EOS Agentic Support Console",
    description: "Governed copilot and future agentic support workflows.",
    defaultRoute: "/",
    enabledRoutePrefixes: [
      "/",
      "/copilot",
      "/ai-config",
      "/agent-chat",
      "/agent-investigations",
      "/demo-scenarios",
      "/agent-knowledge",
      "/executive-demo",
      "/agentic",
      "/health",
      "/about",
    ],
    externalLinks: [],
    helperText: "Current phase uses governed deterministic mock AI only. No autonomous remediation or external LLM call is enabled.",
  },
};

export function getExperienceCode(): ExperienceCode {
  const configured = import.meta.env.VITE_EOS_EXPERIENCE as string | undefined;
  return configured && configured in EXPERIENCE_CONFIG ? configured as ExperienceCode : "full";
}

export function getExperienceDefinition(code = getExperienceCode()): ExperienceDefinition {
  return EXPERIENCE_CONFIG[code];
}

export function isRouteAllowed(pathname: string, code = getExperienceCode()): boolean {
  if (code === "full") return true;
  const normalizedPath = pathname === "/" ? "/" : pathname.replace(/\/$/, "");
  return getExperienceDefinition(code).enabledRoutePrefixes.some((prefix) => {
    if (prefix === "/") return normalizedPath === "/";
    return normalizedPath === prefix || normalizedPath.startsWith(`${prefix}/`);
  });
}

export function findExperienceForPath(pathname: string): ExperienceDefinition | undefined {
  return (Object.values(EXPERIENCE_CONFIG) as ExperienceDefinition[]).find((experience) =>
    experience.code !== "full" && isRouteAllowed(pathname, experience.code),
  );
}
