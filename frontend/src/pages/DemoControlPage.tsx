import { useQuery } from "@tanstack/react-query";
import { Alert, Box, Button, Card, CardContent, Chip, CircularProgress, Grid, Link as MuiLink, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material";
import { getDemoReadiness, getDemoSummary, type DemoReadinessItem } from "../services/demoControlApi";

function State({ loading, error }: { loading: boolean; error: Error | null }) {
  if (loading) return <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 3 }}><CircularProgress size={22} /><Typography>Checking demo stack readiness…</Typography></Box>;
  if (error) return <Alert severity="error" sx={{ mb: 3 }}>{error.message}</Alert>;
  return null;
}

function StatusChip({ healthy, value }: { healthy: boolean; value: string }) {
  return <Chip size="small" label={value} color={healthy ? "success" : "error"} variant="outlined" />;
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return <Card><CardContent><Typography color="text.secondary">{label}</Typography><Typography variant="h4" sx={{ mt: 1, fontWeight: 700 }}>{value}</Typography></CardContent></Card>;
}

const infrastructureLinks = [
  ["Grafana", "http://localhost:3001"],
  ["Prometheus", "http://localhost:9090"],
  ["Tempo", "http://localhost:3200/ready"],
  ["Loki", "http://localhost:3100/ready"],
  ["OTel Collector", "http://localhost:13133/"],
];

export function DemoControlPage() {
  const summary = useQuery({ queryKey: ["demo-control", "summary"], queryFn: getDemoSummary });
  const readiness = useQuery({ queryKey: ["demo-control", "readiness"], queryFn: getDemoReadiness });
  const refresh = () => { void summary.refetch(); void readiness.refetch(); };
  return <Box>
    <Typography variant="overline" color="primary">Local Demo Operations</Typography>
    <Typography variant="h3" sx={{ mt: .5, mb: 1, fontWeight: 700 }}>Demo Control Panel</Typography>
    <Typography color="text.secondary" sx={{ mb: 3 }}>Read-only topology and readiness for the EOS customer demonstration stack.</Typography>
    <Alert severity="info" sx={{ mb: 3 }}>This UI is a read-only demo control panel. It does not start or stop local processes. Use scripts from the terminal for startup and shutdown.</Alert>
    <State loading={summary.isLoading || readiness.isLoading} error={(summary.error || readiness.error) as Error | null} />
    {summary.data && <>
      <Alert severity={summary.data.overall_status === "HEALTHY" ? "success" : "warning"} sx={{ mb: 3 }}>Overall demo status: <strong>{summary.data.overall_status}</strong></Alert>
      <Grid container spacing={2} sx={{ mb: 4 }}>{[["Frontends", summary.data.summary.frontends], ["Backends/BFFs", summary.data.summary.backends], ["Infrastructure", summary.data.summary.infrastructure_components]].map(([label, value]) => <Grid size={{ xs: 12, sm: 4 }} key={String(label)}><Stat label={String(label)} value={value as number} /></Grid>)}</Grid>
      <Typography variant="h5" sx={{ mb: 2 }}>Experience topology</Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>{summary.data.experiences.map((experience) => <Grid size={{ xs: 12, md: 6 }} key={experience.code}><Card><CardContent><Typography variant="h6">{experience.name}</Typography><Typography color="text.secondary" sx={{ mb: 1 }}>{experience.purpose}</Typography><Typography>Frontend: <MuiLink href={experience.frontend_url} target="_blank" rel="noreferrer">{experience.frontend_url}</MuiLink></Typography><Typography>Backend/BFF: <MuiLink href={experience.backend_url} target="_blank" rel="noreferrer">{experience.backend_url}</MuiLink></Typography></CardContent></Card></Grid>)}</Grid>
      <Typography variant="h5" sx={{ mb: 2 }}>Observability links</Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>{infrastructureLinks.map(([label, url]) => <Grid size={{ xs: 12, sm: 6, md: 4 }} key={label}><Card><CardContent><Typography variant="h6">{label}</Typography><MuiLink href={url} target="_blank" rel="noreferrer">{url}</MuiLink></CardContent></Card></Grid>)}</Grid>
      <Typography variant="h5" sx={{ mb: 2 }}>Agent action capabilities</Typography>
      <Alert severity="warning" sx={{ mb: 4 }}>Stage 2 approval-gated mode: {summary.data.capabilities.join(" · ")}. Actions are local, predefined, and require explicit human approval.</Alert>
    </>}
    {readiness.data && <>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}><Typography variant="h5">Readiness</Typography><Button variant="outlined" onClick={refresh} disabled={summary.isFetching || readiness.isFetching}>Refresh readiness</Button></Box>
      <TableContainer component={Paper} sx={{ mb: 4 }}><Table size="small"><TableHead><TableRow>{["Name", "Kind", "URL", "Expected", "Actual", "Status", "Message"].map((header) => <TableCell key={header}>{header}</TableCell>)}</TableRow></TableHead><TableBody>{readiness.data.items.map((item: DemoReadinessItem) => <TableRow key={`${item.kind}-${item.name}`}><TableCell>{item.name}</TableCell><TableCell>{item.kind}</TableCell><TableCell>{item.url}</TableCell><TableCell>{item.expected_status}</TableCell><TableCell>{item.actual_status ?? "—"}</TableCell><TableCell><StatusChip healthy={item.healthy} value={item.healthy ? "PASS" : "FAIL"} /></TableCell><TableCell>{item.message}</TableCell></TableRow>)}</TableBody></Table></TableContainer>
    </>}
    <Typography variant="h5" sx={{ mb: 2 }}>Terminal commands</Typography>
    <Paper sx={{ p: 2, mb: 2, overflow: "auto" }}><pre style={{ margin: 0 }}>{`./scripts/start-demo-stack.sh
./scripts/status-demo-stack.sh
./scripts/validate-demo-stack.sh
./scripts/stop-demo-stack.sh`}</pre></Paper>
    <Typography variant="h5" sx={{ mb: 2 }}>Validation hint</Typography>
    <Paper sx={{ p: 2, overflow: "auto" }}><pre style={{ margin: 0 }}>{`curl -sS http://localhost:8050/api/v1/demo-control/readiness | jq .`}</pre></Paper>
  </Box>;
}
