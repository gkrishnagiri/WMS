import { Box, Card, CardContent, Chip, Grid, Typography } from "@mui/material";

const futureModules = ["Warehouse & Fulfillment Operations", "Inventory", "Orders", "Shipping", "Batch Processing", "Incident Simulation", "Agentic AMS Platform"];

export function AboutPage() {
  return (
    <Box>
      <Typography variant="overline" color="primary">Platform profile</Typography>
      <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>About EOS</Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>A foundation for realistic enterprise operations research and agentic support experiments.</Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}><Card><CardContent><Typography variant="h6">Enterprise Operations Suite</Typography><Typography color="text.secondary" sx={{ mt: 1 }}>AI-Native AMS Research Platform</Typography><Typography sx={{ mt: 2 }}>Version 0.1.0</Typography><Chip label="Enterprise Foundation" color="primary" size="small" sx={{ mt: 2 }} /></CardContent></Card></Grid>
        <Grid size={{ xs: 12, md: 6 }}><Card><CardContent><Typography variant="h6">Technology stack</Typography><Typography color="text.secondary" sx={{ mt: 1 }}>React · TypeScript · Vite · React Router · TanStack Query · Material UI</Typography><Typography color="text.secondary" sx={{ mt: 1 }}>FastAPI · Python · SQLAlchemy · PostgreSQL · Redis</Typography></CardContent></Card></Grid>
      </Grid>
      <Card sx={{ mt: 2 }}><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Future module placeholders</Typography><Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>{futureModules.map((module) => <Chip key={module} label={module} variant="outlined" />)}</Box></CardContent></Card>
    </Box>
  );
}
