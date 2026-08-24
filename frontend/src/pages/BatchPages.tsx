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
  Typography,
  Chip,
} from "@mui/material";
import {
  createBatchDiagnostic,
  createBatchException,
  createBatchTicket,
  getBatchJob,
  getBatchJobs,
  getBatchRun,
  getBatchRuns,
  getBatchSummary,
  runBatchSimulation,
  runBatchSuite,
  type BatchJob,
  type BatchRun,
  type BatchSimulationResult,
  type BatchSuiteResult,
} from "../services/batchApi";
import { InvestigateWithAgentButton } from "../components/agent/InvestigateWithAgentButton";

const chip = (value: string) => (
  <Chip
    size="small"
    label={value.replaceAll("_", " ")}
    color={
      value === "FAILED" || value === "TIMEOUT" || value === "HIGH"
        ? "error"
        : value === "PARTIAL_SUCCESS" ||
            value === "RUNNING" ||
            value === "MEDIUM"
          ? "warning"
          : value === "SUCCESS"
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
        <Typography>Loading batch data…</Typography>
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
        Batch Operations
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
function SummaryCard({
  label,
  value,
}: {
  label: string;
  value: number | string;
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
function refresh(q: ReturnType<typeof useQueryClient>) {
  void q.invalidateQueries({ queryKey: ["batch"] });
  void q.invalidateQueries({ queryKey: ["ams", "tickets"] });
  void q.invalidateQueries({ queryKey: ["operations", "exceptions"] });
  void q.invalidateQueries({ queryKey: ["observability"] });
}

export function BatchJobsPage() {
  const summary = useQuery({
    queryKey: ["batch", "summary"],
    queryFn: getBatchSummary,
  });
  const jobs = useQuery({ queryKey: ["batch", "jobs"], queryFn: getBatchJobs });
  return (
    <Box>
      <Header
        title="Batch Jobs"
        description="Configured warehouse batch processes and their deterministic execution history."
      />
      <State
        loading={summary.isLoading || jobs.isLoading}
        error={(summary.error || jobs.error) as Error | null}
      />
      {summary.data && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {[
            ["Batch jobs", summary.data.batch_jobs],
            ["Runs total", summary.data.runs_total],
            ["Successful", summary.data.runs_success],
            ["Failed", summary.data.runs_failed],
            ["Partial", summary.data.runs_partial],
            ["Timeout", summary.data.runs_timeout],
          ].map(([label, value]) => (
            <Grid key={String(label)} size={{ xs: 6, md: 2 }}>
              <SummaryCard label={String(label)} value={value as number} />
            </Grid>
          ))}
        </Grid>
      )}
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {[
                "Job",
                "Name",
                "Type",
                "Enabled",
                "SLA",
                "Steps",
                "Recent status",
              ].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(jobs.data || []).map((job: BatchJob) => (
              <TableRow key={job.id}>
                <TableCell>
                  <Button
                    component={Link}
                    to={`/batch/jobs/${job.id}`}
                    size="small"
                  >
                    {job.job_code}
                  </Button>
                </TableCell>
                <TableCell>{job.name}</TableCell>
                <TableCell>{job.job_type}</TableCell>
                <TableCell>{job.enabled ? "Yes" : "No"}</TableCell>
                <TableCell>{job.sla_minutes} min</TableCell>
                <TableCell>{job.step_count}</TableCell>
                <TableCell>
                  {job.recent_runs[0]
                    ? chip(job.recent_runs[0].status)
                    : "No runs"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export function BatchJobDetailPage() {
  const { jobId = "" } = useParams();
  const query = useQuery({
    queryKey: ["batch", "job", jobId],
    queryFn: () => getBatchJob(jobId),
    enabled: Boolean(jobId),
  });
  return (
    <Box>
      <Button component={Link} to="/batch/jobs" sx={{ mb: 2 }}>
        ← Back to batch jobs
      </Button>
      <State loading={query.isLoading} error={query.error as Error | null} />
      {query.data && (
        <>
          <Header title={query.data.job_code} description={query.data.name} />
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography>{query.data.description}</Typography>
              <Typography color="text.secondary" sx={{ mt: 1 }}>
                Type: {query.data.job_type} · Module: {query.data.module} · SLA:{" "}
                {query.data.sla_minutes} minutes
              </Typography>
            </CardContent>
          </Card>
          <Typography variant="h5" sx={{ mb: 1 }}>
            Configured steps
          </Typography>
          <TableContainer component={Paper} sx={{ mb: 3 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Order</TableCell>
                  <TableCell>Code</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Expected duration</TableCell>
                  <TableCell>Enabled</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {query.data.steps.map((step) => (
                  <TableRow key={step.id}>
                    <TableCell>{step.step_order}</TableCell>
                    <TableCell>{step.step_code}</TableCell>
                    <TableCell>{step.step_name}</TableCell>
                    <TableCell>{step.step_type}</TableCell>
                    <TableCell>{step.expected_duration_ms} ms</TableCell>
                    <TableCell>{step.enabled ? "Yes" : "No"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Typography variant="h5" sx={{ mb: 1 }}>
            Recent runs
          </Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Run</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Processed</TableCell>
                  <TableCell>Failed</TableCell>
                  <TableCell>Started</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {query.data.recent_runs.map((run) => (
                  <TableRow key={run.id}>
                    <TableCell>
                      <Button
                        component={Link}
                        to={`/batch/runs/${run.id}`}
                        size="small"
                      >
                        {run.run_number}
                      </Button>
                    </TableCell>
                    <TableCell>{chip(run.status)}</TableCell>
                    <TableCell>{run.duration_ms ?? "—"} ms</TableCell>
                    <TableCell>{run.records_processed}</TableCell>
                    <TableCell>{run.records_failed}</TableCell>
                    <TableCell>
                      {new Date(run.started_at).toLocaleString()}
                    </TableCell>
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

export function BatchRunsPage() {
  const query = useQuery({
    queryKey: ["batch", "runs"],
    queryFn: getBatchRuns,
  });
  return (
    <Box>
      <Header
        title="Batch Runs"
        description="Auditable synchronous batch executions, failures, and linked support artifacts."
      />
      <State loading={query.isLoading} error={query.error as Error | null} />
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {[
                "Run",
                "Job",
                "Status",
                "Scenario",
                "Duration",
                "Processed",
                "Failed",
                "Failure type",
                "Exception",
                "Ticket",
                "Diagnostic",
                "Started",
              ].map((h) => (
                <TableCell key={h}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(query.data || []).map((run: BatchRun) => (
              <TableRow key={run.id}>
                <TableCell>
                  <Button
                    component={Link}
                    to={`/batch/runs/${run.id}`}
                    size="small"
                  >
                    {run.run_number}
                  </Button>
                </TableCell>
                <TableCell>{run.job_code}</TableCell>
                <TableCell>{chip(run.status)}</TableCell>
                <TableCell>{run.scenario_code}</TableCell>
                <TableCell>{run.duration_ms ?? "—"} ms</TableCell>
                <TableCell>{run.records_processed}</TableCell>
                <TableCell>{run.records_failed}</TableCell>
                <TableCell>
                  {run.failure_type ? chip(run.failure_type) : "—"}
                </TableCell>
                <TableCell>{run.linked_exception_number || "—"}</TableCell>
                <TableCell>{run.linked_ticket_number || "—"}</TableCell>
                <TableCell>{run.linked_diagnostic_number || "—"}</TableCell>
                <TableCell>
                  {new Date(run.started_at).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

function RunActions({
  run,
  onChanged,
}: {
  run: BatchRun;
  onChanged: () => void;
}) {
  const mutation = useMutation({
    mutationFn: (kind: string) =>
      kind === "exception"
        ? createBatchException(run.id)
        : kind === "ticket"
          ? createBatchTicket(run.id)
          : createBatchDiagnostic(run.id),
    onSuccess: onChanged,
  });
  if (run.status === "SUCCESS") return null;
  return (
    <Stack direction="row" spacing={1}>
      {!run.linked_exception_id && (
        <Button size="small" onClick={() => mutation.mutate("exception")}>
          Create Exception
        </Button>
      )}
      {!run.linked_ticket_id && (
        <Button size="small" onClick={() => mutation.mutate("ticket")}>
          Create Ticket
        </Button>
      )}
      {!run.linked_diagnostic_case_id && (
        <Button size="small" onClick={() => mutation.mutate("diagnostic")}>
          Create Diagnostic
        </Button>
      )}
      {mutation.error && (
        <Typography color="error" variant="caption">
          {(mutation.error as Error).message}
        </Typography>
      )}
    </Stack>
  );
}
export function BatchRunDetailPage() {
  const { runId = "" } = useParams();
  const q = useQueryClient();
  const query = useQuery({
    queryKey: ["batch", "run", runId],
    queryFn: () => getBatchRun(runId),
    enabled: Boolean(runId),
  });
  return (
    <Box>
      <Button component={Link} to="/batch/runs" sx={{ mb: 2 }}>
        ← Back to batch runs
      </Button>
      <State loading={query.isLoading} error={query.error as Error | null} />
      {query.data && (
        <>
          <Header
            title={query.data.run_number}
            description={`${query.data.job_code} · ${query.data.scenario_code}`}
          />
          <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
            {chip(query.data.status)}
            {query.data.failure_type && chip(query.data.failure_type)}
          </Stack>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography>{query.data.summary}</Typography>
              {query.data.failure_message && (
                <Typography color="error" sx={{ mt: 1 }}>
                  {query.data.failure_message}
                </Typography>
              )}
              <Typography color="text.secondary" sx={{ mt: 1 }}>
                Records processed/succeeded/failed:{" "}
                {query.data.records_processed}/{query.data.records_succeeded}/
                {query.data.records_failed}
              </Typography>
              <Typography sx={{ mt: 2 }}>
                <RunActions run={query.data} onChanged={() => refresh(q)} />
              </Typography>
              <InvestigateWithAgentButton sourceType="BATCH_FAILURE" sourceId={query.data.id} />
            </CardContent>
          </Card>
          <Typography variant="h5" sx={{ mb: 1 }}>
            Step runs
          </Typography>
          <TableContainer component={Paper} sx={{ mb: 3 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {[
                    "Order",
                    "Step",
                    "Status",
                    "Duration",
                    "Processed",
                    "Failed",
                    "Failure",
                  ].map((h) => (
                    <TableCell key={h}>{h}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {query.data.steps.map((step) => (
                  <TableRow key={step.id}>
                    <TableCell>{step.step_order}</TableCell>
                    <TableCell>{step.step_code}</TableCell>
                    <TableCell>{chip(step.status)}</TableCell>
                    <TableCell>{step.duration_ms ?? "—"} ms</TableCell>
                    <TableCell>{step.records_processed}</TableCell>
                    <TableCell>{step.records_failed}</TableCell>
                    <TableCell>{step.failure_message || "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Typography variant="h5" sx={{ mb: 1 }}>
            Event timeline
          </Typography>
          <Stack spacing={1}>
            {query.data.events.map((event) => (
              <Box key={event.id}>
                <Typography fontWeight={700}>
                  {event.event_type.replaceAll("_", " ")}
                </Typography>
                <Typography>{event.message}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(event.created_at).toLocaleString()}
                </Typography>
              </Box>
            ))}
          </Stack>
        </>
      )}
    </Box>
  );
}

const scenarios = [
  {
    code: "inventory-reconciliation-success",
    title: "Inventory Reconciliation Success",
    description: "Run every reconciliation step successfully.",
  },
  {
    code: "inventory-reconciliation-failure",
    title: "Inventory Reconciliation Failure",
    description: "Fail reconciliation after validation succeeds.",
  },
  {
    code: "order-release-validation-failure",
    title: "Order Release Validation Failure",
    description: "Reject orders with incomplete allocation prerequisites.",
  },
  {
    code: "shipment-sync-timeout",
    title: "Shipment Sync Timeout",
    description: "Simulate a carrier status synchronization timeout.",
  },
  {
    code: "low-stock-notification-partial-failure",
    title: "Low Stock Partial Failure",
    description: "Process most notifications while eight records fail.",
  },
];
export function BatchSimulationsPage() {
  const [flags, setFlags] = useState({
    create_exception: true,
    create_ticket: true,
    create_observability: true,
  });
  const [result, setResult] = useState<BatchSimulationResult | null>(null);
  const [suite, setSuite] = useState<BatchSuiteResult | null>(null);
  const mutation = useMutation<
    BatchSimulationResult | BatchSuiteResult,
    Error,
    string
  >({
    mutationFn: (code: string) =>
      code === "batch-failure-suite"
        ? runBatchSuite(flags)
        : runBatchSimulation(code, flags),
    onSuccess: (data) => {
      if ("results" in data) {
        setSuite(data);
        setResult(null);
      } else {
        setResult(data);
        setSuite(null);
      }
    },
  });
  return (
    <Box>
      <Header
        title="Batch Simulations"
        description="Manually trigger deterministic batch success, failure, timeout, and partial-success scenarios."
      />
      <Stack direction="row" spacing={2} sx={{ mb: 3, flexWrap: "wrap" }}>
        {(
          ["create_exception", "create_ticket", "create_observability"] as const
        ).map((key) => (
          <FormControlLabel
            key={key}
            control={
              <Checkbox
                checked={flags[key]}
                onChange={(e) =>
                  setFlags({ ...flags, [key]: e.target.checked })
                }
              />
            }
            label={key.replaceAll("_", " ")}
          />
        ))}
      </Stack>
      <Grid container spacing={2}>
        {[
          ...scenarios,
          {
            code: "batch-failure-suite",
            title: "Batch Failure Suite",
            description:
              "Run one success and four deterministic failure scenarios.",
          },
        ].map((s) => (
          <Grid key={s.code} size={{ xs: 12, sm: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6">{s.title}</Typography>
                <Typography
                  color="text.secondary"
                  sx={{ minHeight: 46, mt: 1 }}
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
            <Typography variant="h6">
              {result.run.run_number} · {chip(result.run.status)}
            </Typography>
            <Typography sx={{ mt: 1 }}>{result.run.summary}</Typography>
            <Stack direction="row" spacing={2} sx={{ mt: 1, flexWrap: "wrap" }}>
              {result.exception_id && (
                <Button
                  component={Link}
                  to="/operations/exceptions"
                  size="small"
                >
                  Exception {result.exception_number}
                </Button>
              )}
              {result.ticket_id && (
                <Button
                  component={Link}
                  to={`/ams/tickets/${result.ticket_id}`}
                  size="small"
                >
                  Ticket {result.ticket_number}
                </Button>
              )}
              {result.diagnostic_case_id && (
                <Button
                  component={Link}
                  to={`/observability/diagnostics/${result.diagnostic_case_id}`}
                  size="small"
                >
                  Diagnostic {result.diagnostic_number}
                </Button>
              )}
              <Button
                component={Link}
                to={`/batch/runs/${result.run.id}`}
                size="small"
              >
                View run
              </Button>
            </Stack>
          </CardContent>
        </Card>
      )}
      {suite && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6">Batch failure suite</Typography>
            <Typography sx={{ mt: 1 }}>{suite.summary}</Typography>
            <Typography sx={{ mt: 1 }}>
              Runs: {suite.runs_created} · Success: {suite.successful_runs} ·
              Failed/timeout: {suite.failed_runs} · Partial:{" "}
              {suite.partial_runs} · Tickets: {suite.tickets_created} ·
              Exceptions: {suite.exceptions_created} · Diagnostics:{" "}
              {suite.diagnostics_created}
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
