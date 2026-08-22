import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Alert, Box, Button, Card, CardContent, Checkbox, CircularProgress, FormControlLabel, Grid, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography, Chip } from "@mui/material";
import { getJourneyRuns, getSyntheticJourneys, runJourney, runSyntheticSuite, type JourneyRun, type RunSuiteResult } from "../services/syntheticUsersApi";

function PageState({ loading, error }: { loading: boolean; error: Error | null }) {
  if (loading) return <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}><CircularProgress size={22} /><Typography>Loading synthetic user data…</Typography></Box>;
  if (error) return <Alert severity="error" sx={{ mb: 2 }}>{error.message}</Alert>;
  return null;
}

function StatusChip({ value }: { value: string }) {
  const color = value === "SUCCESS" ? "success" : value === "FAILED" ? "error" : value === "PARTIAL" ? "warning" : "default";
  return <Chip size="small" label={value.replaceAll("_", " ")} color={color} variant={color === "default" ? "outlined" : "filled"} />;
}

function Header({ title, description }: { title: string; description: string }) {
  return <><Typography variant="overline" color="primary">Synthetic users</Typography><Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>{title}</Typography><Typography color="text.secondary" sx={{ mb: 4 }}>{description}</Typography></>;
}

function RunResult({ run }: { run: JourneyRun }) {
  return <Card sx={{ mt: 3 }}><CardContent><Typography variant="h6">Latest journey result</Typography><Typography sx={{ mt: 1 }}><strong>{run.run_number}</strong> · <StatusChip value={run.status} /></Typography><Typography sx={{ mt: 1 }}>{run.journey_name} · {run.synthetic_user_name}</Typography>{run.failure_message && <Alert severity="warning" sx={{ mt: 2 }}>{run.failure_message}</Alert>}{run.user_report_id && <Typography sx={{ mt: 1 }}>User report: <Button component={Link} to={`/ams/user-reports/${run.user_report_id}`} size="small">{run.user_report_number || run.user_report_id}</Button></Typography>}{run.ticket_id && <Typography>Ticket: <Button component={Link} to={`/ams/tickets/${run.ticket_id}`} size="small">{run.ticket_number || run.ticket_id}</Button></Typography>}</CardContent></Card>;
}

export function SyntheticJourneysPage() {
  const queryClient = useQueryClient();
  const [createTicket, setCreateTicket] = useState(true);
  const [lastRun, setLastRun] = useState<JourneyRun | null>(null);
  const [suite, setSuite] = useState<RunSuiteResult | null>(null);
  const journeys = useQuery({ queryKey: ["synthetic-users", "journeys"], queryFn: getSyntheticJourneys });
  const refresh = () => { void queryClient.invalidateQueries({ queryKey: ["synthetic-users", "runs"] }); void queryClient.invalidateQueries({ queryKey: ["user-reports"] }); void queryClient.invalidateQueries({ queryKey: ["ams", "tickets"] }); void queryClient.invalidateQueries({ queryKey: ["ams", "summary"] }); };
  const run = useMutation({ mutationFn: ({ code }: { code: string }) => runJourney(code, createTicket), onSuccess: (data) => { setLastRun(data); setSuite(null); refresh(); } });
  const runSuite = useMutation({ mutationFn: () => runSyntheticSuite(createTicket), onSuccess: (data) => { setSuite(data); setLastRun(null); refresh(); } });
  return <Box><Header title="Synthetic User Journeys" description="Deterministic backend-driven personas exercising successful and failed warehouse experiences." /><Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3, flexWrap: "wrap" }}><FormControlLabel control={<Checkbox checked={createTicket} onChange={(event) => setCreateTicket(event.target.checked)} />} label="Create ticket on failure" /><Button variant="contained" onClick={() => runSuite.mutate()} disabled={run.isPending || runSuite.isPending}>Run Full Synthetic Suite</Button></Stack><PageState loading={journeys.isLoading} error={journeys.error as Error | null} />{(run.error || runSuite.error) && <Alert severity="error" sx={{ mb: 2 }}>{((run.error || runSuite.error) as Error).message}</Alert>}<Grid container spacing={2}>{(journeys.data || []).map((journey) => <Grid key={journey.id} size={{ xs: 12, md: 6 }}><Card><CardContent><Stack direction="row" justifyContent="space-between" gap={2}><Typography variant="h6">{journey.name}</Typography><StatusChip value={journey.enabled ? "ENABLED" : "DISABLED"} /></Stack><Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>{journey.journey_code}</Typography><Typography sx={{ mt: 2 }}>{journey.description}</Typography><Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>Persona: {journey.persona} · Type: {journey.journey_type} · Expected: {journey.expected_outcome}</Typography><Button variant="outlined" sx={{ mt: 2 }} onClick={() => run.mutate({ code: journey.journey_code })} disabled={run.isPending || !journey.enabled}>Run</Button></CardContent></Card></Grid>)}</Grid>{lastRun && <RunResult run={lastRun} />}{suite && <Card sx={{ mt: 3 }}><CardContent><Typography variant="h6">Suite result</Typography><Typography sx={{ mt: 1 }}>Runs: {suite.total} · Succeeded: {suite.succeeded} · Failed: {suite.failed}</Typography><Stack spacing={1} sx={{ mt: 2 }}>{suite.runs.map((item) => <Typography key={item.id} variant="body2"><strong>{item.run_number}</strong> · {item.journey_code} · <StatusChip value={item.status} /></Typography>)}</Stack></CardContent></Card>}</Box>;
}

export function JourneyRunsPage() {
  const runs = useQuery({ queryKey: ["synthetic-users", "runs"], queryFn: () => getJourneyRuns() });
  return <Box><Header title="Journey Runs" description="Auditable execution history for synthetic personas and their functional experiences." /><PageState loading={runs.isLoading} error={runs.error as Error | null} /><TableContainer component={Paper}><Table size="small"><TableHead><TableRow><TableCell>Run</TableCell><TableCell>Journey</TableCell><TableCell>User</TableCell><TableCell>Status</TableCell><TableCell>Failure</TableCell><TableCell>Order / report / ticket</TableCell><TableCell>Started</TableCell><TableCell>Duration</TableCell></TableRow></TableHead><TableBody>{(runs.data || []).map((run) => <TableRow key={run.id}><TableCell><strong>{run.run_number}</strong></TableCell><TableCell>{run.journey_code}</TableCell><TableCell>{run.synthetic_user_name}</TableCell><TableCell><StatusChip value={run.status} /></TableCell><TableCell>{run.failure_type || "—"}<Typography variant="caption" display="block" color="text.secondary">{run.failure_message || ""}</Typography></TableCell><TableCell>{run.order_id ? <Typography variant="caption" display="block">Order {run.order_id.slice(0, 8)}</Typography> : null}{run.user_report_id ? <Button component={Link} to={`/ams/user-reports/${run.user_report_id}`} size="small">{run.user_report_number || "Report"}</Button> : null}{run.ticket_id ? <Button component={Link} to={`/ams/tickets/${run.ticket_id}`} size="small">{run.ticket_number || "Ticket"}</Button> : null}{!run.order_id && !run.user_report_id && !run.ticket_id ? "—" : null}</TableCell><TableCell>{new Date(run.started_at).toLocaleString()}</TableCell><TableCell>{run.duration_ms == null ? "—" : `${run.duration_ms} ms`}</TableCell></TableRow>)}</TableBody></Table></TableContainer></Box>;
}

