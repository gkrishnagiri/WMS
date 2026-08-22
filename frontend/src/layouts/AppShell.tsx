import type { ReactNode } from "react";
import { Link } from "react-router-dom";
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

const drawerWidth = 252;
const theme = createTheme({
  palette: {
    primary: { main: "#1565c0", dark: "#0d2f52" },
    background: { default: "#f4f7fb", paper: "#ffffff" },
  },
  typography: { fontFamily: "Inter, Roboto, Arial, sans-serif" },
  shape: { borderRadius: 10 },
});

const navigation = [
  { label: "Dashboard", path: "/" },
  { label: "Warehouse", path: "/warehouse" },
  { label: "Inventory", path: "/warehouse/inventory" },
  { label: "Orders", path: "/warehouse/orders" },
  { label: "Fulfillment Tasks", path: "/warehouse/tasks" },
  { label: "Shipments", path: "/warehouse/shipments" },
  { label: "Inventory Transactions", path: "/warehouse/inventory-transactions" },
  { label: "Operations", path: "/operations/exceptions" },
  { label: "AMS Tickets", path: "/ams/tickets" },
  { label: "Synthetic Journeys", path: "/synthetic-users/journeys" },
  { label: "Journey Runs", path: "/synthetic-users/runs" },
  { label: "User Reports", path: "/ams/user-reports" },
  { label: "Monitoring", path: "/monitoring/alerts" },
  { label: "Monitoring Simulations", path: "/monitoring/simulations" },
  { label: "Monitoring Triage", path: "/monitoring/triage" },
  { label: "Observability", path: "/observability" },
  { label: "Traces", path: "/observability/traces" },
  { label: "Diagnostics", path: "/observability/diagnostics" },
  { label: "Batch Jobs", path: "/batch/jobs" },
  { label: "Batch Runs", path: "/batch/runs" },
  { label: "Batch Simulations", path: "/batch/simulations" },
  { label: "Copilot", path: "/copilot" },
  { label: "Copilot Sessions", path: "/copilot/sessions" },
  { label: "Health", path: "/health" },
  { label: "About", path: "/about" },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="fixed" elevation={0}>
        <Toolbar sx={{ minHeight: 72 }}>
          <Box sx={{ width: drawerWidth, display: { xs: "none", sm: "block" } }}>
            <Typography variant="h6" fontWeight={700}>EOS</Typography>
          </Box>
          <Box>
            <Typography variant="h6" fontWeight={700}>Enterprise Operations Suite</Typography>
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
          <Typography variant="body2" color="text.secondary">Foundation environment</Typography>
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
        {children}
      </Box>
    </ThemeProvider>
  );
}
