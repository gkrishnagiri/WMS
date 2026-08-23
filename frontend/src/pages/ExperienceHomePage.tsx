import { Box, Button, Card, CardContent, Chip, Grid, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import { getExperienceDefinition, type ExperienceCode } from "../config/experience";
import { DashboardPage } from "./DashboardPage";

const cards: Record<Exclude<ExperienceCode, "full">, { label: string; path: string; description: string }[]> = {
  business: [
    { label: "Warehouse", path: "/warehouse", description: "Warehouses, zones, locations, and operating context." },
    { label: "Inventory", path: "/warehouse/inventory", description: "Availability and inventory balance views." },
    { label: "Orders", path: "/warehouse/orders", description: "Customer orders and fulfillment progress." },
    { label: "Fulfillment Tasks", path: "/warehouse/tasks", description: "Pick and pack task execution." },
    { label: "Shipments", path: "/warehouse/shipments", description: "Shipment readiness and confirmation." },
  ],
  operations: [
    { label: "AMS Tickets", path: "/ams/tickets", description: "Support work items and lifecycle management." },
    { label: "Operations Exceptions", path: "/operations/exceptions", description: "Business and operational symptoms." },
    { label: "Monitoring Alerts", path: "/monitoring/alerts", description: "Noisy monitoring signals and alert state." },
    { label: "Monitoring Triage", path: "/monitoring/triage", description: "Manual support grouping of related alerts." },
    { label: "Batch Runs", path: "/batch/runs", description: "Batch failures and operational history." },
    { label: "Diagnostics", path: "/observability/diagnostics", description: "Evidence-backed support diagnosis." },
  ],
  simulation: [
    { label: "Synthetic Journeys", path: "/synthetic-users/journeys", description: "Run deterministic user workflows." },
    { label: "Batch Simulations", path: "/batch/simulations", description: "Induce controlled batch outcomes." },
    { label: "Monitoring Simulations", path: "/monitoring/simulations", description: "Generate deterministic alert noise." },
    { label: "Observability Simulations", path: "/observability/simulations", description: "Generate traces, logs, metrics, and diagnoses." },
    { label: "Runtime Stack Test", path: "/observability/stack/test", description: "Emit local test telemetry signals." },
  ],
  observability: [
    { label: "Runtime Observability", path: "/observability/runtime", description: "Inspect live EOS request telemetry." },
    { label: "Runtime Traces", path: "/observability/runtime/traces", description: "Explore request traces and runtime evidence." },
    { label: "Stack Health", path: "/observability/stack/health", description: "Check local collector and backend availability." },
    { label: "Stack Test", path: "/observability/stack/test", description: "Generate span, log, and metric signals." },
    { label: "Grafana", path: "http://localhost:3001", description: "Open the primary observability UI." },
    { label: "Prometheus", path: "http://localhost:9090", description: "Open the local metrics backend." },
    { label: "Tempo", path: "http://localhost:3200", description: "Open the local trace backend." },
    { label: "Loki", path: "http://localhost:3100", description: "Open the local log backend." },
  ],
  agentic: [
    { label: "Copilot", path: "/copilot", description: "Governed support context and recommendations." },
    { label: "Copilot Analyze", path: "/copilot/analyze", description: "Analyze an existing support artifact." },
    { label: "AI Config", path: "/ai-config", description: "Provider, prompt, and safety configuration." },
    { label: "AI Invocations", path: "/ai-config/invocations", description: "Review governed mock invocations." },
    { label: "AI Safety", path: "/ai-config/safety", description: "Inspect and test deterministic guardrails." },
    { label: "Future Agents", path: "/about", description: "Placeholder for future human-governed agent workflows." },
  ],
};

function isExternal(path: string): boolean {
  return path.startsWith("http://") || path.startsWith("https://");
}

export function ExperienceRootPage() {
  const experience = getExperienceDefinition();
  if (experience.code === "full") return <DashboardPage />;
  return <ExperienceHomePage />;
}

export function ExperienceHomePage() {
  const experience = getExperienceDefinition();
  const experienceCards = cards[experience.code as Exclude<ExperienceCode, "full">];

  return (
    <Box>
      <Typography variant="overline" color="primary">{experience.displayName}</Typography>
      <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>{experience.code === "simulation" ? "Controlled simulation lab" : experience.code === "observability" ? "Observability control plane" : experience.code === "agentic" ? "Governed support intelligence" : "Business operations workspace"}</Typography>
      <Typography color="text.secondary" sx={{ maxWidth: 820, mb: 2 }}>{experience.description}</Typography>
      {experience.helperText && <AlertText>{experience.helperText}</AlertText>}
      <Grid container spacing={2} sx={{ mt: 1 }}>
        {experienceCards.map((card) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={`${card.label}-${card.path}`}>
            <Card sx={{ height: "100%" }}>
              <CardContent sx={{ display: "flex", height: "100%", flexDirection: "column" }}>
                <Chip label={experience.code.toUpperCase()} size="small" color="primary" sx={{ alignSelf: "flex-start" }} />
                <Typography variant="h6" sx={{ mt: 2 }}>{card.label}</Typography>
                <Typography color="text.secondary" sx={{ mt: 1, mb: 2, flexGrow: 1 }}>{card.description}</Typography>
                {isExternal(card.path) ? (
                  <Button component="a" href={card.path} target="_blank" rel="noreferrer" variant="outlined">Open</Button>
                ) : (
                  <Button component={Link} to={card.path} variant="outlined">Open</Button>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

function AlertText({ children }: { children: string }) {
  return <Box sx={{ borderLeft: 4, borderColor: "primary.main", bgcolor: "primary.50", px: 2, py: 1.5, maxWidth: 900 }}><Typography color="text.secondary">{children}</Typography></Box>;
}
