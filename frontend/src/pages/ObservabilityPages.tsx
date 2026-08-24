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
  getDiagnosticCase,
  getDiagnosticCases,
  getLogs,
  getMetrics,
  getObservabilitySummary,
  getTrace,
  getTraces,
  linkDiagnosticTicket,
  resolveDiagnosticCase,
  runObservabilitySimulation,
  runObservabilitySuite,
  type DiagnosticCase,
  type ObsLog,
  type ObsMetric,
  type ObsTrace,
} from "../services/observabilityApi";
import { InvestigateWithAgentButton } from "../components/agent/InvestigateWithAgentButton";

const chip = (value: string) => (
  <Chip
    size="small"
    label={value.replaceAll("_", " ")}
    color={
      value === "ERROR" ||
      value === "CRITICAL" ||
      value === "HIGH" ||
      value === "TIMEOUT"
        ? "error"
        : value === "DEGRADED" ||
            value === "SLOW" ||
            value === "MEDIUM" ||
            value === "UNDER_REVIEW"
          ? "warning"
          : value === "SUCCESS" ||
              value === "OK" ||
              value === "DIAGNOSED" ||
              value === "RESOLVED"
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
        <Typography>Loading observability data…</Typography>
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
        Observability
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
function SummaryCard({ label, value }: { label: string; value: number }) {
  return (
    <Card>
      <CardContent>
        <Typography color="text.secondary">{label}</Typography>
        <Typography variant="h4" sx={{ mt: 1, fontWeight: 700 }}>
          {value.toLocaleString()}
        </Typography>
      </CardContent>
    </Card>
  );
}
function refresh(q: ReturnType<typeof useQueryClient>) {
  void q.invalidateQueries({ queryKey: ["observability"] });
  void q.invalidateQueries({ queryKey: ["ams", "tickets"] });
}

export function ObservabilityOverviewPage() {
  const summary = useQuery({
    queryKey: ["observability", "summary"],
    queryFn: getObservabilitySummary,
  });
  return (
    <Box>
      <Header
        title="Observability"
        description="Deterministic traces, logs, and metrics provide evidence-backed support diagnosis without AI or external observability tools."
      />
      <Alert severity="info" sx={{ mb: 3 }}>
        This module demonstrates deterministic observability evidence for
        support diagnosis. It does not use AI or real external observability
        tools yet.
      </Alert>
      <State
        loading={summary.isLoading}
        error={summary.error as Error | null}
      />
      {summary.data && (
        <Grid container spacing={2}>
          {[
            ["Traces", summary.data.traces],
            ["Error traces", summary.data.error_traces],
            ["Slow spans", summary.data.slow_spans],
            ["Error logs", summary.data.error_logs],
            ["Metric samples", summary.data.metric_samples],
            ["Open diagnoses", summary.data.open_diagnostic_cases],
            ["High confidence", summary.data.high_confidence_diagnoses],
            ["Linked tickets", summary.data.linked_tickets],
          ].map(([label, value]) => (
            <Grid key={String(label)} size={{ xs: 6, md: 3 }}>
              <SummaryCard label={String(label)} value={value as number} />
            </Grid>
          ))}
        </Grid>
      )}
      <Stack direction="row" spacing={2} sx={{ mt: 4 }}>
        <Button
          component={Link}
          variant="contained"
          to="/observability/simulations"
        >
          Run simulations
        </Button>
        <Button component={Link} to="/observability/traces">
          View traces
        </Button>
        <Button component={Link} to="/observability/diagnostics">
          View diagnostics
        </Button>
      </Stack>
    </Box>
  );
}

const simulations = [
  {
    code: "database-degradation",
    title: "Database Degradation",
    description:
      "Correlate slow database spans with allocation and API symptoms.",
  },
  {
    code: "redis-cache-failure",
    title: "Redis Cache Failure",
    description: "Trace cache failure and a degraded API fallback path.",
  },
  {
    code: "allocation-failure",
    title: "Allocation Failure",
    description:
      "Distinguish insufficient stock business validation from outage.",
  },
  {
    code: "shipment-integration-failure",
    title: "Shipment Integration Failure",
    description: "Trace a simulated carrier label generation timeout.",
  },
];
export function ObservabilitySimulationsPage() {
  const [result, setResult] = useState<
    | Awaited<ReturnType<typeof runObservabilitySimulation>>
    | Awaited<ReturnType<typeof runObservabilitySuite>>
    | null
  >(null);
  const [createTicket, setCreateTicket] = useState(false);
  const mutation = useMutation({
    mutationFn: (code: string) =>
      code === "observability-demo-suite"
        ? runObservabilitySuite(createTicket)
        : runObservabilitySimulation(code, createTicket),
    onSuccess: setResult,
  });
  return (
    <Box>
      <Header
        title="Observability Simulations"
        description="Generate repeatable traces, spans, structured logs, metric samples, and deterministic diagnostic cases."
      />
      <FormControlLabel
        control={
          <Checkbox
            checked={createTicket}
            onChange={(e) => setCreateTicket(e.target.checked)}
          />
        }
        label="Create/link AMS ticket"
      />
      <Grid container spacing={2} sx={{ mt: 1 }}>
        {[
          ...simulations,
          {
            code: "observability-demo-suite",
            title: "Observability Demo Suite",
            description:
              "Run all four evidence scenarios in deterministic order.",
          },
        ].map((s) => (
          <Grid key={s.code} size={{ xs: 12, sm: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6">{s.title}</Typography>
                <Typography
                  color="text.secondary"
                  sx={{ minHeight: 48, mt: 1 }}
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
            {"results" in result ? (
              <Typography sx={{ mt: 1 }}>
                Traces: {result.traces_created} · Diagnostic cases:{" "}
                {result.diagnostic_cases_created} · Alerts:{" "}
                {result.alerts_created_or_reused} · Tickets:{" "}
                {result.tickets_created_or_linked}
              </Typography>
            ) : (
              <>
                <Typography sx={{ mt: 1 }}>{result.summary}</Typography>
                {result.trace_id && (
                  <Typography sx={{ mt: 1 }}>
                    Trace:{" "}
                    <Button
                      component={Link}
                      size="small"
                      to={`/observability/traces/${result.trace_identifier || result.trace_id}`}
                    >
                      {result.trace_identifier}
                    </Button>
                  </Typography>
                )}
                {result.diagnostic_case_id && (
                  <Typography>
                    Diagnosis:{" "}
                    <Button
                      component={Link}
                      size="small"
                      to={`/observability/diagnostics/${result.diagnostic_case_id}`}
                    >
                      {result.diagnostic_number}
                    </Button>
                  </Typography>
                )}
                {result.ticket_id && (
                  <Typography>
                    Ticket:{" "}
                    <Button
                      component={Link}
                      size="small"
                      to={`/ams/tickets/${result.ticket_id}`}
                    >
                      {result.ticket_id}
                    </Button>
                  </Typography>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export function TracesPage() {
  const query = useQuery({
    queryKey: ["observability", "traces"],
    queryFn: getTraces,
  });
  return (
    <Box>
      <Header
        title="Traces"
        description="End-to-end request and workflow timelines correlated with support symptoms."
      />
      <State loading={query.isLoading} error={query.error as Error | null} />
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {[
                "Trace",
                "Name",
                "Type",
                "Status",
                "Module",
                "Root reference",
                "Duration",
                "Alert",
                "Started",
              ].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(query.data || []).map((t: ObsTrace) => (
              <TableRow key={t.id}>
                <TableCell>
                  <Button
                    component={Link}
                    to={`/observability/traces/${t.trace_id}`}
                    size="small"
                  >
                    {t.trace_id}
                  </Button>
                </TableCell>
                <TableCell>{t.trace_name}</TableCell>
                <TableCell>{chip(t.trace_type)}</TableCell>
                <TableCell>{chip(t.status)}</TableCell>
                <TableCell>{t.source_module}</TableCell>
                <TableCell>{t.root_reference || "—"}</TableCell>
                <TableCell>{t.duration_ms ?? "—"} ms</TableCell>
                <TableCell>{t.linked_alert_id ? "Linked" : "—"}</TableCell>
                <TableCell>{new Date(t.started_at).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export function TraceDetailPage() {
  const { traceId = "" } = useParams();
  const query = useQuery({
    queryKey: ["observability", "trace", traceId],
    queryFn: () => getTrace(traceId),
    enabled: Boolean(traceId),
  });
  return (
    <Box>
      <Button component={Link} to="/observability/traces" sx={{ mb: 2 }}>
        ← Back to traces
      </Button>
      <State loading={query.isLoading} error={query.error as Error | null} />
      {query.data && (
        <>
          <Header
            title={query.data.trace_id}
            description={query.data.trace_name}
          />
          <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
            {chip(query.data.status)}
            {chip(query.data.trace_type)}
            <Typography color="text.secondary">
              {query.data.duration_ms ?? "—"} ms
            </Typography>
          </Stack>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography>{query.data.summary}</Typography>
              <Typography color="text.secondary" sx={{ mt: 1 }}>
                Module: {query.data.source_module} · Root:{" "}
                {query.data.root_reference || "—"} · Alert:{" "}
                {query.data.linked_alert_id || "—"} · Ticket:{" "}
                {query.data.linked_ticket_id || "—"}
              </Typography>
            </CardContent>
          </Card>
          <Typography variant="h5" sx={{ mb: 1 }}>
            Span timeline
          </Typography>
          <TableContainer component={Paper} sx={{ mb: 3 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {[
                    "Span",
                    "Service",
                    "Component",
                    "Operation",
                    "Status",
                    "Duration",
                    "Error",
                  ].map((h) => (
                    <TableCell key={h}>{h}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {query.data.spans.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell>{s.span_name}</TableCell>
                    <TableCell>{s.service_name}</TableCell>
                    <TableCell>{s.component_code || "—"}</TableCell>
                    <TableCell>{s.operation_type}</TableCell>
                    <TableCell>{chip(s.status)}</TableCell>
                    <TableCell>{s.duration_ms} ms</TableCell>
                    <TableCell>{s.error_message || "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Typography variant="h5" sx={{ mb: 1 }}>
            Related logs
          </Typography>
          <TableContainer component={Paper} sx={{ mb: 3 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Time</TableCell>
                  <TableCell>Level</TableCell>
                  <TableCell>Event</TableCell>
                  <TableCell>Component</TableCell>
                  <TableCell>Message</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {query.data.logs.map((l: ObsLog) => (
                  <TableRow key={l.id}>
                    <TableCell>
                      {new Date(l.logged_at).toLocaleTimeString()}
                    </TableCell>
                    <TableCell>{chip(l.level)}</TableCell>
                    <TableCell>{l.event_type}</TableCell>
                    <TableCell>{l.component_code || "—"}</TableCell>
                    <TableCell>{l.message}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Typography variant="h5" sx={{ mb: 1 }}>
            Related metrics
          </Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Time</TableCell>
                  <TableCell>Metric</TableCell>
                  <TableCell>Component</TableCell>
                  <TableCell>Value</TableCell>
                  <TableCell>Unit</TableCell>
                  <TableCell>Severity</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {query.data.metrics.map((m: ObsMetric) => (
                  <TableRow key={m.id}>
                    <TableCell>
                      {new Date(m.recorded_at).toLocaleTimeString()}
                    </TableCell>
                    <TableCell>{m.metric_name}</TableCell>
                    <TableCell>{m.component_code || "—"}</TableCell>
                    <TableCell>{m.metric_value}</TableCell>
                    <TableCell>{m.metric_unit}</TableCell>
                    <TableCell>{m.severity ? chip(m.severity) : "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Box>
  );
}

export function LogsPage() {
  const query = useQuery({
    queryKey: ["observability", "logs"],
    queryFn: getLogs,
  });
  return (
    <Box>
      <Header
        title="Structured Logs"
        description="Logs correlated with traces, spans, components, alerts, and tickets."
      />
      <State loading={query.isLoading} error={query.error as Error | null} />
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {[
                "Log",
                "Time",
                "Level",
                "Event",
                "Component",
                "Message",
                "Trace",
              ].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(query.data || []).map((l: ObsLog) => (
              <TableRow key={l.id}>
                <TableCell>{l.log_number}</TableCell>
                <TableCell>{new Date(l.logged_at).toLocaleString()}</TableCell>
                <TableCell>{chip(l.level)}</TableCell>
                <TableCell>{l.event_type}</TableCell>
                <TableCell>{l.component_code || "—"}</TableCell>
                <TableCell>{l.message}</TableCell>
                <TableCell>{l.trace_id || "—"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export function MetricsPage() {
  const query = useQuery({
    queryKey: ["observability", "metrics"],
    queryFn: getMetrics,
  });
  return (
    <Box>
      <Header
        title="Metric Samples"
        description="Point-in-time metric evidence generated by deterministic scenarios."
      />
      <State loading={query.isLoading} error={query.error as Error | null} />
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {[
                "Sample",
                "Time",
                "Metric",
                "Component",
                "Value",
                "Unit",
                "Severity",
                "Trace",
                "Alert",
              ].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(query.data || []).map((m: ObsMetric) => (
              <TableRow key={m.id}>
                <TableCell>{m.sample_number}</TableCell>
                <TableCell>
                  {new Date(m.recorded_at).toLocaleString()}
                </TableCell>
                <TableCell>{m.metric_name}</TableCell>
                <TableCell>{m.component_code || "—"}</TableCell>
                <TableCell>{m.metric_value}</TableCell>
                <TableCell>{m.metric_unit}</TableCell>
                <TableCell>{m.severity ? chip(m.severity) : "—"}</TableCell>
                <TableCell>{m.trace_id || "—"}</TableCell>
                <TableCell>{m.linked_alert_id || "—"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

function DiagnosticActions({
  row,
  onChanged,
}: {
  row: DiagnosticCase;
  onChanged: () => void;
}) {
  const m = useMutation({
    mutationFn: (op: string) =>
      op === "ticket"
        ? linkDiagnosticTicket(row.id)
        : resolveDiagnosticCase(
            row.id,
            "Support engineer validated the correlated evidence and resolved the symptom.",
          ),
    onSuccess: onChanged,
  });
  return (
    <Stack direction="row" spacing={0.5}>
      {!row.linked_ticket_id && (
        <Button size="small" onClick={() => m.mutate("ticket")}>
          Ticket
        </Button>
      )}
      {["OPEN", "UNDER_REVIEW", "DIAGNOSED", "LINKED_TO_TICKET"].includes(
        row.status,
      ) && (
        <Button size="small" onClick={() => m.mutate("resolve")}>
          Resolve
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
export function DiagnosticsPage() {
  const q = useQueryClient();
  const query = useQuery({
    queryKey: ["observability", "diagnostics"],
    queryFn: getDiagnosticCases,
  });
  return (
    <Box>
      <Header
        title="Diagnostic Cases"
        description="Evidence-backed support diagnoses. Probable causes are deterministic and require human validation."
      />
      <State loading={query.isLoading} error={query.error as Error | null} />
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {[
                "Diagnostic",
                "Title",
                "Severity",
                "Status",
                "Confidence",
                "Probable cause",
                "Trace",
                "Ticket",
                "Created",
                "Actions",
              ].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(query.data || []).map((d: DiagnosticCase) => (
              <TableRow key={d.id}>
                <TableCell>
                  <Button
                    component={Link}
                    to={`/observability/diagnostics/${d.id}`}
                    size="small"
                  >
                    {d.diagnostic_number}
                  </Button>
                </TableCell>
                <TableCell>{d.title}</TableCell>
                <TableCell>{chip(d.severity)}</TableCell>
                <TableCell>{chip(d.status)}</TableCell>
                <TableCell>{chip(d.confidence_level)}</TableCell>
                <TableCell>{d.probable_cause}</TableCell>
                <TableCell>{d.primary_trace_identifier || "—"}</TableCell>
                <TableCell>
                  {d.linked_ticket_id ? (
                    <Button
                      component={Link}
                      size="small"
                      to={`/ams/tickets/${d.linked_ticket_id}`}
                    >
                      View
                    </Button>
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell>{new Date(d.created_at).toLocaleString()}</TableCell>
                <TableCell>
                  <DiagnosticActions row={d} onChanged={() => refresh(q)} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export function DiagnosticDetailPage() {
  const { caseId = "" } = useParams();
  const q = useQueryClient();
  const query = useQuery({
    queryKey: ["observability", "diagnostic", caseId],
    queryFn: () => getDiagnosticCase(caseId),
    enabled: Boolean(caseId),
  });
  const [notes, setNotes] = useState(
    "Support engineer validated the correlated evidence and resolved the symptom.",
  );
  const m = useMutation({
    mutationFn: (op: string) =>
      op === "ticket"
        ? linkDiagnosticTicket(caseId)
        : resolveDiagnosticCase(caseId, notes),
    onSuccess: () => {
      void q.invalidateQueries({ queryKey: ["observability"] });
      void q.invalidateQueries({ queryKey: ["ams", "tickets"] });
    },
  });
  return (
    <Box>
      <Button component={Link} to="/observability/diagnostics" sx={{ mb: 2 }}>
        ← Back to diagnostics
      </Button>
      <State loading={query.isLoading} error={query.error as Error | null} />
      {query.data && (
        <>
          <Header
            title={query.data.diagnostic_number}
            description={query.data.title}
          />
          <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
            {chip(query.data.status)}
            {chip(query.data.severity)}
            {chip(query.data.confidence_level)}
          </Stack>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 8 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6">Probable cause</Typography>
                  <InvestigateWithAgentButton sourceType="DIAGNOSTIC_CASE" sourceId={query.data.id} />
                  <Typography sx={{ mt: 1 }}>
                    {query.data.probable_cause}
                  </Typography>
                  <Typography variant="h6" sx={{ mt: 3 }}>
                    Diagnosis summary
                  </Typography>
                  <Typography sx={{ mt: 1, whiteSpace: "pre-wrap" }}>
                    {query.data.diagnosis_summary}
                  </Typography>
                  <Typography variant="h6" sx={{ mt: 3 }}>
                    Recommended next steps
                  </Typography>
                  <Typography sx={{ mt: 1, whiteSpace: "pre-wrap" }}>
                    {query.data.recommended_next_steps}
                  </Typography>
                  <Typography variant="h6" sx={{ mt: 3 }}>
                    Links
                  </Typography>
                  <Typography sx={{ mt: 1 }}>
                    Trace:{" "}
                    {query.data.primary_trace_identifier ? (
                      <Button
                        component={Link}
                        size="small"
                        to={`/observability/traces/${query.data.primary_trace_identifier}`}
                      >
                        {query.data.primary_trace_identifier}
                      </Button>
                    ) : (
                      "—"
                    )}{" "}
                    · Alert: {query.data.linked_alert_id || "—"} · Triage:{" "}
                    {query.data.linked_triage_case_id || "—"}
                  </Typography>
                </CardContent>
              </Card>
              <Typography variant="h5" sx={{ mt: 3, mb: 1 }}>
                Evidence
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Details</TableCell>
                      <TableCell>Weight</TableCell>
                      <TableCell>Source</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {query.data.evidence.map((e) => (
                      <TableRow key={e.id}>
                        <TableCell>{chip(e.evidence_type)}</TableCell>
                        <TableCell>{e.title}</TableCell>
                        <TableCell>{e.details}</TableCell>
                        <TableCell>{e.weight}</TableCell>
                        <TableCell>{e.source_table}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Card>
                <CardContent>
                  <Stack spacing={2}>
                    <Typography>
                      Created:{" "}
                      {new Date(query.data.created_at).toLocaleString()}
                    </Typography>
                    <Typography>
                      Ticket: {query.data.linked_ticket_id || "Not linked"}
                    </Typography>
                    <TextField
                      label="Resolution notes"
                      multiline
                      minRows={3}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                    {!query.data.linked_ticket_id && (
                      <Button
                        variant="contained"
                        onClick={() => m.mutate("ticket")}
                      >
                        Create/link AMS ticket
                      </Button>
                    )}
                    {[
                      "OPEN",
                      "UNDER_REVIEW",
                      "DIAGNOSED",
                      "LINKED_TO_TICKET",
                    ].includes(query.data.status) && (
                      <Button onClick={() => m.mutate("resolve")}>
                        Resolve diagnostic case
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
