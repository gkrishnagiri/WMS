import { Box, Button, Card, CardContent, Chip, Typography } from "@mui/material";
import { Link, useLocation } from "react-router-dom";
import { findExperienceForPath, getExperienceDefinition } from "../config/experience";

export function ExperienceBoundaryPage() {
  const location = useLocation();
  const current = getExperienceDefinition();
  const owningExperience = findExperienceForPath(location.pathname);

  return (
    <Box sx={{ maxWidth: 760 }}>
      <Typography variant="overline" color="primary">Experience boundary</Typography>
      <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>This page belongs to another EOS experience</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        The current browser is running the <strong>{current.displayName}</strong>. This route is intentionally kept out of that experience&apos;s navigation.
      </Typography>
      <Card>
        <CardContent>
          {owningExperience ? (
            <>
              <Chip label={owningExperience.displayName} color="primary" size="small" />
              <Typography variant="h6" sx={{ mt: 2 }}>{owningExperience.description}</Typography>
              <Typography color="text.secondary" sx={{ mt: 1, mb: 3 }}>
                Open the matching frontend URL to view this page.
              </Typography>
              <Button component="a" href={frontendUrl(owningExperience.code)} variant="contained">Open {owningExperience.displayName}</Button>
            </>
          ) : (
            <Typography color="text.secondary">No specialized EOS experience is registered for this route.</Typography>
          )}
          <Button component={Link} to="/" variant="text" sx={{ ml: 1 }}>Return home</Button>
        </CardContent>
      </Card>
    </Box>
  );
}

function frontendUrl(code: string): string {
  const ports: Record<string, number> = { business: 4011, operations: 4012, simulation: 4013, observability: 4014, agentic: 4015 };
  return `http://localhost:${ports[code] ?? 4001}`;
}
