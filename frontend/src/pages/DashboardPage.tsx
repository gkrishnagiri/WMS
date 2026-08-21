import { Box, Card, CardContent, Chip, Grid, Typography } from "@mui/material";

export function DashboardPage() {
  return (
    <Box>
      <Typography variant="overline" color="primary">Enterprise Foundation</Typography>
      <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>Operations at a glance</Typography>
      <Typography color="text.secondary" sx={{ maxWidth: 700, mb: 4 }}>
        EOS is the foundation for an AI-Native AMS Research Platform. Platform services are online and ready for future operations modules.
      </Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card><CardContent><Chip label="Phase 1" color="primary" size="small" /><Typography variant="h6" sx={{ mt: 2 }}>Enterprise Foundation</Typography><Typography color="text.secondary">Core application shell, service health, and platform configuration.</Typography></CardContent></Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card><CardContent><Chip label="Planned" variant="outlined" size="small" /><Typography variant="h6" sx={{ mt: 2 }}>Warehouse & Fulfillment</Typography><Typography color="text.secondary">The first business module will arrive in a later phase.</Typography></CardContent></Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card><CardContent><Chip label="Connected" color="success" size="small" /><Typography variant="h6" sx={{ mt: 2 }}>Platform Services</Typography><Typography color="text.secondary">PostgreSQL and Redis are available through the local infrastructure baseline.</Typography></CardContent></Card>
        </Grid>
      </Grid>
    </Box>
  );
}
