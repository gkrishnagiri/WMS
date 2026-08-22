import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./layouts/AppShell";
import { AboutPage } from "./pages/AboutPage";
import { DashboardPage } from "./pages/DashboardPage";
import { HealthPage } from "./pages/HealthPage";
import { InventoryPage, OrdersPage, ShipmentsPage, TasksPage, WarehousePage } from "./pages/WarehousePages";
import { CreateOrderPage, InventoryTransactionsPage, OrderDetailPage, WorkflowTasksPage } from "./pages/WarehouseWorkflowPages";
import { AmsTicketDetailPage, AmsTicketsPage, OperationsExceptionsPage, OperationsSimulationsPage } from "./pages/SupportabilityPages";
import { JourneyRunsPage, SyntheticJourneysPage } from "./pages/SyntheticUserPages";
import { NewUserReportPage, UserReportDetailPage, UserReportsPage } from "./pages/UserReportPages";
import { MonitoringAlertsPage, MonitoringSimulationsPage, MonitoringTriageDetailPage, MonitoringTriagePage } from "./pages/MonitoringPages";

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
        <Route path="/operations/exceptions" element={<OperationsExceptionsPage />} />
        <Route path="/operations/simulations" element={<OperationsSimulationsPage />} />
        <Route path="/ams/tickets" element={<AmsTicketsPage />} />
        <Route path="/ams/tickets/:ticketId" element={<AmsTicketDetailPage />} />
        <Route path="/synthetic-users/journeys" element={<SyntheticJourneysPage />} />
        <Route path="/synthetic-users/runs" element={<JourneyRunsPage />} />
        <Route path="/ams/user-reports" element={<UserReportsPage />} />
        <Route path="/ams/user-reports/new" element={<NewUserReportPage />} />
        <Route path="/ams/user-reports/:reportId" element={<UserReportDetailPage />} />
        <Route path="/monitoring/alerts" element={<MonitoringAlertsPage />} />
        <Route path="/monitoring/simulations" element={<MonitoringSimulationsPage />} />
        <Route path="/monitoring/triage" element={<MonitoringTriagePage />} />
        <Route path="/monitoring/triage/:caseId" element={<MonitoringTriageDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
