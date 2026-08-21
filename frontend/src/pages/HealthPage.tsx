import { Alert, Box, Card, CardContent, CircularProgress, Grid, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { getHealth } from "../services/api";

export function HealthPage() {
  const health = useQuery({ queryKey: ["health"], queryFn: getHealth, refetchInterval: 30000 });

  if (health.isLoading) return <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}><CircularProgress size={24} /><Typography>Checking platform health…</Typography></Box>;
  if (health.isError) return <Alert severity="error"><strong>Backend unreachable.</strong> Make sure the EOS API is running at the configured API URL. {health.error.message}</Alert>;
  if (!health.data) return <Alert severity="warning">No health data is currently available.</Alert>;

  const data = health.data;
  return (
    <Box>
      <Typography variant="overline" color="primary">Runtime status</Typography>
      <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>System health</Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>Live connectivity status for the EOS application dependencies.</Typography>
      <Grid container spacing={2}>
        {Object.entries(data.checks).map(([name, status]) => (
          <Grid size={{ xs: 12, sm: 4 }} key={name}><Card><CardContent><Typography color="text.secondary" textTransform="capitalize">{name}</Typography><Typography variant="h5" sx={{ mt: 1 }} color={status === "healthy" ? "success.main" : "error.main"}>{status}</Typography></CardContent></Card></Grid>
        ))}
      </Grid>
      <Card sx={{ mt: 2 }}><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Application details</Typography><Typography>Environment: <strong>{data.environment}</strong></Typography><Typography>Version: <strong>{data.version}</strong></Typography><Typography>Overall status: <strong>{data.status}</strong></Typography></CardContent></Card>
    </Box>
  );
}
