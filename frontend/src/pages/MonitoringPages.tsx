import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip,
} from "@mui/material";
import {
  acknowledgeAlert,
  createTicketFromAlert,
  createTicketFromTriageCase,
  createTriageCase,
  getMonitoringAlerts,
  getMonitoringSummary,
  getTriageCase,
  getTriageCases,
  resolveAlert,
  resolveTriageCase,
  runMonitoringSimulation,
  startTriageInvestigation,
  suppressAlert,
  type MonitoringAlert,
  type TriageCase,
} from "../services/monitoringApi";
import { InvestigateWithAgentButton } from "../components/agent/InvestigateWithAgentButton";

const chip = (value: string) => (
  <Chip
    size="small"
    label={value.replaceAll("_", " ")}
    color={
      value === "CRITICAL" ||
      value === "HIGH" ||
      value === "OPEN" ||
      value === "INVESTIGATING"
        ? "error"
        : value === "MEDIUM" || value === "ACKNOWLEDGED"
          ? "warning"
          : value === "RESOLVED" || value === "CLOSED"
            ? "success"
            : "default"
    }
    variant="outlined"
  />
);
function State({ loading, error }: { loading: boolean; error: Error | null }) {
  if (loading)
    return (
      <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}>
        <CircularProgress size={22} />
        <Typography>Loading monitoring data…</Typography>
      </Box>
    );
  if (error)
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error.message}
      </Alert>
    );
  return null;
}
function Header({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <>
      <Typography variant="overline" color="primary">
        Monitoring
      </Typography>
      <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>
        {title}
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>
        {description}
      </Typography>
    </>
  );
}
function refresh(q: ReturnType<typeof useQueryClient>) {
  void q.invalidateQueries({ queryKey: ["monitoring"] });
  void q.invalidateQueries({ queryKey: ["ams", "tickets"] });
}
function SummaryCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <Card>
      <CardContent>
        <Typography color="text.secondary">{label}</Typography>
        <Typography variant="h4" sx={{ mt: 1, fontWeight: 700 }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
}

export function MonitoringAlertsPage() {
  const q = useQueryClient();
  const summary = useQuery({
    queryKey: ["monitoring", "summary"],
    queryFn: getMonitoringSummary,
  });
  const alerts = useQuery({
    queryKey: ["monitoring", "alerts"],
    queryFn: () => getMonitoringAlerts(),
  });
  const action = useMutation({
    mutationFn: async ({ id, op }: { id: string; op: string }) =>
      op === "ack"
        ? acknowledgeAlert(id)
        : op === "suppress"
          ? suppressAlert(id)
          : op === "resolve"
            ? resolveAlert(id)
            : createTicketFromAlert(id),
    onSuccess: () => refresh(q),
  });
  return (
    <Box>
      <Header
        title="Monitoring Alerts"
        description="Component-level monitoring symptoms. No traces, logs, or automated root-cause diagnosis are attached."
      />
      <State
        loading={summary.isLoading || alerts.isLoading}
        error={(summary.error || alerts.error) as Error | null}
      />
      {summary.data && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {[
            ["Open alerts", summary.data.open_alerts],
            ["Critical", summary.data.critical_alerts],
            ["High", summary.data.high_alerts],
            ["Noisiest component", summary.data.noisiest_component || "—"],
          ].map(([label, value]) => (
            <Grid key={String(label)} size={{ xs: 6, md: 3 }}>
              <SummaryCard
                label={String(label)}
                value={value as string | number}
              />
            </Grid>
          ))}
        </Grid>
      )}
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {[
                "Alert",
                "Severity",
                "Status",
                "Component",
                "Metric",
                "Observed / threshold",
                "Occurrences",
                "Last seen",
                "Ticket",
                "Actions",
              ].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(alerts.data || []).map((a: MonitoringAlert) => (
              <TableRow key={a.id}>
                <TableCell>
                  <strong>{a.alert_number}</strong>
                  <Typography variant="caption" display="block">
                    {a.title}
                  </Typography>
                </TableCell>
                <TableCell>{chip(a.severity)}</TableCell>
                <TableCell>{chip(a.status)}</TableCell>
                <TableCell>{a.component_code}</TableCell>
                <TableCell>{a.metric_name}</TableCell>
                <TableCell>
                  {a.observed_value} / {a.threshold_value}
                </TableCell>
                <TableCell>{a.occurrence_count}</TableCell>
                <TableCell>
                  {new Date(a.last_seen_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {a.linked_ticket_id ? (
                    <Button
                      component={Link}
                      to={`/ams/tickets/${a.linked_ticket_id}`}
                      size="small"
                    >
                      {a.linked_ticket_number || "View"}
                    </Button>
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={0.5}>
                    {a.status === "OPEN" && (
                      <Button
                        size="small"
                        onClick={() => action.mutate({ id: a.id, op: "ack" })}
                      >
                        Ack
                      </Button>
                    )}
                    {(a.status === "OPEN" || a.status === "ACKNOWLEDGED") && (
                      <Button
                        size="small"
                        onClick={() =>
                          action.mutate({ id: a.id, op: "suppress" })
                        }
                      >
                        Suppress
                      </Button>
                    )}
                    {[
                      "OPEN",
                      "ACKNOWLEDGED",
                      "SUPPRESSED",
                      "LINKED_TO_TICKET",
                    ].includes(a.status) && (
                      <Button
                        size="small"
                        onClick={() =>
                          action.mutate({ id: a.id, op: "resolve" })
                        }
                      >
                        Resolve
                      </Button>
                    )}
                    {!a.linked_ticket_id && (
                      <Button
                        size="small"
                        onClick={() =>
                          action.mutate({ id: a.id, op: "ticket" })
                        }
                      >
                        Ticket
                      </Button>
                    )}
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {action.error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {(action.error as Error).message}
        </Alert>
      )}
    </Box>
  );
}

const simulations = [
  {
    code: "api-latency-cascade",
    title: "API Latency Cascade",
    description: "Frontend, API, and workflow symptoms.",
  },
  {
    code: "database-degradation",
    title: "Database Degradation",
    description: "Database and downstream application symptoms.",
  },
  {
    code: "redis-flapping",
    title: "Redis Flapping",
    description: "Intermittent cache connection noise.",
  },
  {
    code: "frontend-error-burst",
    title: "Frontend Error Burst",
    description: "User-facing API failure symptoms.",
  },
  {
    code: "warehouse-workflow-noise",
    title: "Warehouse Workflow Noise",
    description: "Business-process alert noise.",
  },
  {
    code: "noisy-alert-storm",
    title: "Noisy Alert Storm",
    description: "Run all deterministic symptom groups.",
  },
];
export function MonitoringSimulationsPage() {
  const [result, setResult] = useState<Awaited<
    ReturnType<typeof runMonitoringSimulation>
  > | null>(null);
  const mutation = useMutation({
    mutationFn: runMonitoringSimulation,
    onSuccess: setResult,
  });
  return (
    <Box>
      <Header
        title="Monitoring Simulations"
        description="Generate repeatable component-level alert noise without real Prometheus or observability integrations."
      />
      <Grid container spacing={2}>
        {simulations.map((s) => (
          <Grid key={s.code} size={{ xs: 12, sm: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6">{s.title}</Typography>
                <Typography
                  color="text.secondary"
                  sx={{ minHeight: 45, mt: 1 }}
                >
                  {s.description}
                </Typography>
                <Button
                  variant="contained"
                  sx={{ mt: 2 }}
                  disabled={mutation.isPending}
                  onClick={() => mutation.mutate(s.code)}
                >
                  Run simulation
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      {mutation.error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {(mutation.error as Error).message}
        </Alert>
      )}
      {result && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6">{result.simulation_code}</Typography>
            <Typography sx={{ mt: 1 }}>{result.simulation_summary}</Typography>
            <Typography sx={{ mt: 1 }}>
              Created: <strong>{result.alerts_created}</strong> · Repeated:{" "}
              <strong>{result.alerts_repeated}</strong> · Open:{" "}
              <strong>{result.alerts_open}</strong> · Highest severity:{" "}
              {chip(result.highest_severity || "—")}
            </Typography>
            <Button component={Link} to="/monitoring/alerts" sx={{ mt: 2 }}>
              View alerts
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

function TriageActions({
  row,
  onChanged,
}: {
  row: TriageCase;
  onChanged: () => void;
}) {
  const m = useMutation({
    mutationFn: async (op: string) => {
      if (op === "start") await startTriageInvestigation(row.id);
      else if (op === "ticket") await createTicketFromTriageCase(row.id);
      else
        await resolveTriageCase(
          row.id,
          "Support engineer determined the symptom cleared after manual analysis.",
        );
    },
    onSuccess: onChanged,
  });
  return (
    <Stack direction="row" spacing={0.5}>
      {row.status === "OPEN" && (
        <Button size="small" onClick={() => m.mutate("start")}>
          Investigate
        </Button>
      )}
      {["OPEN", "INVESTIGATING", "LINKED_TO_TICKET"].includes(row.status) && (
        <Button size="small" onClick={() => m.mutate("resolve")}>
          Resolve
        </Button>
      )}
      {!row.linked_ticket_id && (
        <Button size="small" onClick={() => m.mutate("ticket")}>
          Ticket
        </Button>
      )}
      {m.error && (
        <Typography variant="caption" color="error">
          {(m.error as Error).message}
        </Typography>
      )}
    </Stack>
  );
}
export function MonitoringTriagePage() {
  const q = useQueryClient();
  const rows = useQuery({
    queryKey: ["monitoring", "triage"],
    queryFn: getTriageCases,
  });
  const openAlerts = useQuery({
    queryKey: ["monitoring", "alerts", "open"],
    queryFn: () => getMonitoringAlerts({ status: "OPEN" }),
  });
  const [selected, setSelected] = useState<string[]>([]);
  const [title, setTitle] = useState("Multiple warehouse monitoring alerts");
  const [impact, setImpact] = useState("Warehouse workflows may be degraded.");
  const [description, setDescription] = useState(
    "Support engineer is grouping noisy alerts for manual investigation.",
  );
  const create = useMutation({
    mutationFn: () =>
      createTriageCase({
        title,
        description,
        severity: "HIGH",
        suspected_impact: impact,
        confidence_level: "LOW",
        alert_ids: selected,
      }),
    onSuccess: () => {
      setSelected([]);
      refresh(q);
    },
  });
  return (
    <Box>
      <Header
        title="Monitoring Triage"
        description="Manually group related alert symptoms into a support working case. Root cause remains human-entered and unconfirmed."
      />
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6">Create triage case</Typography>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField
              label="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <TextField
              label="Suspected impact"
              value={impact}
              onChange={(e) => setImpact(e.target.value)}
            />
            <Typography variant="subtitle2">Open alerts to include</Typography>
            {(openAlerts.data || []).map((a) => (
              <FormControlLabel
                key={a.id}
                control={
                  <Checkbox
                    checked={selected.includes(a.id)}
                    onChange={(e) =>
                      setSelected(
                        e.target.checked
                          ? [...selected, a.id]
                          : selected.filter((id) => id !== a.id),
                      )
                    }
                  />
                }
                label={`${a.alert_number} · ${a.component_code} · ${a.title}`}
              />
            ))}
            <Button
              variant="contained"
              onClick={() => create.mutate()}
              disabled={create.isPending || !title || !selected.length}
            >
              Create case
            </Button>
            {create.error && (
              <Alert severity="error">{(create.error as Error).message}</Alert>
            )}
          </Stack>
        </CardContent>
      </Card>
      <State loading={rows.isLoading} error={rows.error as Error | null} />
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {[
                "Case",
                "Title",
                "Severity",
                "Status",
                "Alerts",
                "Ticket",
                "Created",
                "Actions",
              ].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(rows.data || []).map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.case_number}</TableCell>
                <TableCell>
                  <Button
                    component={Link}
                    to={`/monitoring/triage/${row.id}`}
                    size="small"
                  >
                    {row.title}
                  </Button>
                </TableCell>
                <TableCell>{chip(row.severity)}</TableCell>
                <TableCell>{chip(row.status)}</TableCell>
                <TableCell>{row.alert_count}</TableCell>
                <TableCell>
                  {row.linked_ticket_id ? (
                    <Button
                      component={Link}
                      to={`/ams/tickets/${row.linked_ticket_id}`}
                      size="small"
                    >
                      {row.linked_ticket_number || "View"}
                    </Button>
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell>
                  {new Date(row.created_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  <TriageActions row={row} onChanged={() => refresh(q)} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export function MonitoringTriageDetailPage() {
  const { caseId = "" } = useParams();
  const q = useQueryClient();
  const query = useQuery({
    queryKey: ["monitoring", "triage", caseId],
    queryFn: () => getTriageCase(caseId),
    enabled: Boolean(caseId),
  });
  const [notes, setNotes] = useState(
    "Support engineer determined the symptom cleared after manual analysis.",
  );
  const m = useMutation({
    mutationFn: async (op: string) => {
      if (op === "start") await startTriageInvestigation(caseId);
      else if (op === "ticket") await createTicketFromTriageCase(caseId);
      else await resolveTriageCase(caseId, notes);
    },
    onSuccess: () => {
      void q.invalidateQueries({ queryKey: ["monitoring", "triage", caseId] });
      void q.invalidateQueries({ queryKey: ["monitoring", "triage"] });
      void q.invalidateQueries({ queryKey: ["monitoring", "alerts"] });
    },
  });
  return (
    <Box>
      <Button component={Link} to="/monitoring/triage" sx={{ mb: 2 }}>
        ← Back to monitoring triage
      </Button>
      <State loading={query.isLoading} error={query.error as Error | null} />
      {query.data && (
        <>
          <Header
            title={query.data.case_number}
            description={query.data.title}
          />
          <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
            {chip(query.data.status)}
            {chip(query.data.severity)}
            <Typography color="text.secondary">
              {query.data.alert_count} alert(s)
            </Typography>
          </Stack>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 8 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6">Working case</Typography>
                  <InvestigateWithAgentButton sourceType="MONITORING_TRIAGE" sourceId={query.data.id} />
                  <Typography sx={{ mt: 2 }}>
                    {query.data.description}
                  </Typography>
                  <Typography sx={{ mt: 2 }}>
                    Suspected impact: {query.data.suspected_impact}
                  </Typography>
                  <Typography sx={{ mt: 1 }}>
                    Suspected root cause:{" "}
                    {query.data.suspected_root_cause || "Unknown"}
                  </Typography>
                  <Typography sx={{ mt: 1 }}>
                    Confidence: {query.data.confidence_level}
                  </Typography>
                  <Typography variant="h6" sx={{ mt: 3 }}>
                    Included alerts
                  </Typography>
                  {query.data.alerts.map((a) => (
                    <Typography key={a.id} sx={{ mt: 1 }}>
                      {a.alert_number} · {a.component_code} · {a.title}
                    </Typography>
                  ))}
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Card>
                <CardContent>
                  <Stack spacing={2}>
                    <TextField
                      label="Analysis notes"
                      multiline
                      minRows={3}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                    <Button
                      variant="contained"
                      disabled={
                        m.isPending ||
                        !["OPEN", "INVESTIGATING"].includes(query.data.status)
                      }
                      onClick={() => m.mutate("start")}
                    >
                      Start investigation
                    </Button>
                    <Button onClick={() => m.mutate("resolve")}>Resolve</Button>
                    {query.data.linked_ticket_id ? (
                      <Button
                        component={Link}
                        to={`/ams/tickets/${query.data.linked_ticket_id}`}
                      >
                        View AMS ticket
                      </Button>
                    ) : (
                      <Button onClick={() => m.mutate("ticket")}>
                        Create AMS ticket
                      </Button>
                    )}
                    {m.error && (
                      <Alert severity="error">
                        {(m.error as Error).message}
                      </Alert>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}
