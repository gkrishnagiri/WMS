import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./layouts/AppShell";
import { AboutPage } from "./pages/AboutPage";
import { HealthPage } from "./pages/HealthPage";
import { InventoryPage, OrdersPage, ShipmentsPage, TasksPage, WarehousePage } from "./pages/WarehousePages";
import { CreateOrderPage, InventoryTransactionsPage, OrderDetailPage, WorkflowTasksPage } from "./pages/WarehouseWorkflowPages";
import { AmsTicketDetailPage, AmsTicketsPage, OperationsExceptionsPage, OperationsSimulationsPage } from "./pages/SupportabilityPages";
import { JourneyRunsPage, SyntheticJourneysPage } from "./pages/SyntheticUserPages";
import { NewUserReportPage, UserReportDetailPage, UserReportsPage } from "./pages/UserReportPages";
import { DiagnosticDetailPage, DiagnosticsPage, LogsPage, MetricsPage, ObservabilityOverviewPage, ObservabilitySimulationsPage, TraceDetailPage, TracesPage } from "./pages/ObservabilityPages";
import { BatchJobDetailPage, BatchJobsPage, BatchRunDetailPage, BatchRunsPage, BatchSimulationsPage } from "./pages/BatchPages";
import { MonitoringAlertsPage, MonitoringSimulationsPage, MonitoringTriageDetailPage, MonitoringTriagePage } from "./pages/MonitoringPages";
import { CopilotAnalyzePage, CopilotOverviewPage, CopilotSessionDetailPage, CopilotSessionsPage } from "./pages/CopilotPages";
import { AiConfigOverviewPage, AiInvocationsPage, AiPromptsPage, AiProvidersPage, AiSafetyPage, AiTestPage, AiUsagePage } from "./pages/AIConfigPages";
import { RuntimeObservabilityOverviewPage, RuntimeTraceDetailPage, RuntimeTracesPage } from "./pages/RuntimeObservabilityPages";
import { ObservabilityDashboardsPage, ObservabilityStackHealthPage, ObservabilityStackOverviewPage, ObservabilityStackTestPage } from "./pages/ObservabilityStackPages";
import { ExperienceRootPage } from "./pages/ExperienceHomePage";
import { DemoControlPage } from "./pages/DemoControlPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<ExperienceRootPage />} />
        <Route path="/demo-control" element={<DemoControlPage />} />
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
        <Route path="/observability" element={<ObservabilityOverviewPage />} />
        <Route path="/observability/simulations" element={<ObservabilitySimulationsPage />} />
        <Route path="/observability/traces" element={<TracesPage />} />
        <Route path="/observability/traces/:traceId" element={<TraceDetailPage />} />
        <Route path="/observability/logs" element={<LogsPage />} />
        <Route path="/observability/metrics" element={<MetricsPage />} />
        <Route path="/observability/diagnostics" element={<DiagnosticsPage />} />
        <Route path="/observability/diagnostics/:caseId" element={<DiagnosticDetailPage />} />
        <Route path="/batch/jobs" element={<BatchJobsPage />} />
        <Route path="/batch/jobs/:jobId" element={<BatchJobDetailPage />} />
        <Route path="/batch/runs" element={<BatchRunsPage />} />
        <Route path="/batch/runs/:runId" element={<BatchRunDetailPage />} />
        <Route path="/batch/simulations" element={<BatchSimulationsPage />} />
        <Route path="/copilot" element={<CopilotOverviewPage />} />
        <Route path="/copilot/sessions" element={<CopilotSessionsPage />} />
        <Route path="/copilot/sessions/:sessionId" element={<CopilotSessionDetailPage />} />
        <Route path="/copilot/analyze" element={<CopilotAnalyzePage />} />
        <Route path="/ai-config" element={<AiConfigOverviewPage />} />
        <Route path="/ai-config/providers" element={<AiProvidersPage />} />
        <Route path="/ai-config/prompts" element={<AiPromptsPage />} />
        <Route path="/ai-config/safety" element={<AiSafetyPage />} />
        <Route path="/ai-config/invocations" element={<AiInvocationsPage />} />
        <Route path="/ai-config/usage" element={<AiUsagePage />} />
        <Route path="/ai-config/test" element={<AiTestPage />} />
        <Route path="/observability/runtime" element={<RuntimeObservabilityOverviewPage />} />
        <Route path="/observability/runtime/traces" element={<RuntimeTracesPage />} />
        <Route path="/observability/runtime/traces/:traceId" element={<RuntimeTraceDetailPage />} />
        <Route path="/observability/stack" element={<ObservabilityStackOverviewPage />} />
        <Route path="/observability/stack/health" element={<ObservabilityStackHealthPage />} />
        <Route path="/observability/stack/test" element={<ObservabilityStackTestPage />} />
        <Route path="/observability/dashboards" element={<ObservabilityDashboardsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
