import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./layouts/AppShell";
import { AboutPage } from "./pages/AboutPage";
import { DashboardPage } from "./pages/DashboardPage";
import { HealthPage } from "./pages/HealthPage";
import { InventoryPage, OrdersPage, ShipmentsPage, TasksPage, WarehousePage } from "./pages/WarehousePages";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/health" element={<HealthPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/warehouse" element={<WarehousePage />} />
        <Route path="/warehouse/inventory" element={<InventoryPage />} />
        <Route path="/warehouse/orders" element={<OrdersPage />} />
        <Route path="/warehouse/tasks" element={<TasksPage />} />
        <Route path="/warehouse/shipments" element={<ShipmentsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
