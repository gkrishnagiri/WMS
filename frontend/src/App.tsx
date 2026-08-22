import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./layouts/AppShell";
import { AboutPage } from "./pages/AboutPage";
import { DashboardPage } from "./pages/DashboardPage";
import { HealthPage } from "./pages/HealthPage";
import { InventoryPage, OrdersPage, ShipmentsPage, TasksPage, WarehousePage } from "./pages/WarehousePages";
import { CreateOrderPage, InventoryTransactionsPage, OrderDetailPage, WorkflowTasksPage } from "./pages/WarehouseWorkflowPages";

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
        <Route path="/warehouse/orders/new" element={<CreateOrderPage />} />
        <Route path="/warehouse/orders/:orderId" element={<OrderDetailPage />} />
        <Route path="/warehouse/tasks" element={<WorkflowTasksPage />} />
        <Route path="/warehouse/shipments" element={<ShipmentsPage />} />
        <Route path="/warehouse/inventory-transactions" element={<InventoryTransactionsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
