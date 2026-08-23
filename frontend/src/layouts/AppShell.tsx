import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { getExperienceDefinition, getExperienceCode, isRouteAllowed } from "../config/experience";
import { navigationForExperience } from "../config/navigation";
import { ExperienceBoundaryPage } from "../pages/ExperienceBoundaryPage";

const drawerWidth = 252;
const theme = createTheme({
  palette: {
    primary: { main: "#1565c0", dark: "#0d2f52" },
    background: { default: "#f4f7fb", paper: "#ffffff" },
  },
  typography: { fontFamily: "Inter, Roboto, Arial, sans-serif" },
  shape: { borderRadius: 10 },
});

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation();
  const experience = getExperienceDefinition();
  const navigation = navigationForExperience(getExperienceCode());

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="fixed" elevation={0}>
        <Toolbar sx={{ minHeight: 72 }}>
          <Box sx={{ width: drawerWidth, display: { xs: "none", sm: "block" } }}>
            <Typography variant="h6" fontWeight={700}>EOS</Typography>
          </Box>
          <Box>
            <Typography variant="h6" fontWeight={700}>{experience.displayName}</Typography>
            <Typography variant="caption" sx={{ opacity: 0.78 }}>AI-Native AMS Research Platform</Typography>
          </Box>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: "none", sm: "block" },
          "& .MuiDrawer-paper": { width: drawerWidth, boxSizing: "border-box", pt: 9 },
        }}
      >
        <Box sx={{ px: 2.5, py: 2 }}>
          <Typography variant="overline" color="text.secondary">Workspace</Typography>
          <Typography variant="body2" color="text.secondary">{experience.description}</Typography>
        </Box>
        <Divider />
        <List sx={{ px: 1.5, py: 1 }}>
          {navigation.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton component={Link} to={item.path} sx={{ borderRadius: 2, mb: 0.5 }}>
                <ListItemText primary={item.label} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>
      <Box component="main" sx={{ ml: { xs: 0, sm: `${drawerWidth}px` }, pt: 11, px: { xs: 2, sm: 4 }, pb: 5 }}>
        {isRouteAllowed(location.pathname) ? children : <ExperienceBoundaryPage />}
      </Box>
    </ThemeProvider>
  );
}
