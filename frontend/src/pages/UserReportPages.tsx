import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  CircularProgress,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip,
} from "@mui/material";
import {
  acknowledgeUserReport,
  createTicketFromUserReport,
  createUserReport,
  getUserReport,
  getUserReports,
  resolveUserReport,
  type UserReport,
  type UserReportPayload,
} from "../services/userReportsApi";
import { InvestigateWithAgentButton } from "../components/agent/InvestigateWithAgentButton";

function State({ loading, error }: { loading: boolean; error: Error | null }) {
  if (loading)
    return (
      <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}>
        <CircularProgress size={22} />
        <Typography>Loading user report data…</Typography>
      </Box>
    );
  if (error)
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error.message}
      </Alert>
    );
  return null;
}
function ChipValue({ value }: { value: string }) {
  const color =
    value === "HIGH" || value === "CRITICAL"
      ? "error"
      : value === "SUBMITTED" ||
          value === "TICKET_CREATED" ||
          value === "ACKNOWLEDGED"
        ? "warning"
        : value === "RESOLVED"
          ? "success"
          : "default";
  return (
    <Chip
      size="small"
      label={value.replaceAll("_", " ")}
      color={color}
      variant={color === "default" ? "outlined" : "filled"}
    />
  );
}
function Header({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <>
      <Typography variant="overline" color="primary">
        User-reported issues
      </Typography>
      <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>
        {title}
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>
        {description}
      </Typography>
    </>
  );
}
function refreshReports(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: ["user-reports"] });
  void queryClient.invalidateQueries({ queryKey: ["ams", "tickets"] });
  void queryClient.invalidateQueries({ queryKey: ["ams", "summary"] });
  void queryClient.invalidateQueries({ queryKey: ["synthetic-users", "runs"] });
}

function ReportActions({
  report,
  onChanged,
}: {
  report: UserReport;
  onChanged: () => void;
}) {
  const action = useMutation({
    mutationFn: ({ type, id }: { type: string; id: string }) =>
      type === "ticket"
        ? createTicketFromUserReport(id)
        : type === "ack"
          ? acknowledgeUserReport(id)
          : resolveUserReport(id),
    onSuccess: onChanged,
  });
  return (
    <Stack direction="row" spacing={1}>
      {!report.ticket_id &&
        report.status !== "RESOLVED" &&
        report.status !== "CANCELLED" && (
          <Button
            size="small"
            onClick={() => action.mutate({ type: "ticket", id: report.id })}
          >
            Create ticket
          </Button>
        )}
      {(report.status === "SUBMITTED" ||
        report.status === "TICKET_CREATED") && (
        <Button
          size="small"
          onClick={() => action.mutate({ type: "ack", id: report.id })}
        >
          Acknowledge
        </Button>
      )}
      {(report.status === "SUBMITTED" ||
        report.status === "TICKET_CREATED" ||
        report.status === "ACKNOWLEDGED") && (
        <Button
          size="small"
          onClick={() => action.mutate({ type: "resolve", id: report.id })}
        >
          Resolve
        </Button>
      )}
      {action.error && (
        <Typography variant="caption" color="error">
          {(action.error as Error).message}
        </Typography>
      )}
    </Stack>
  );
}

export function UserReportsPage() {
  const queryClient = useQueryClient();
  const reports = useQuery({
    queryKey: ["user-reports"],
    queryFn: () => getUserReports(),
  });
  const refresh = () => refreshReports(queryClient);
  return (
    <Box>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="flex-start"
        gap={2}
      >
        <Header
          title="User Reports"
          description="Functional issues submitted by business users and synthetic personas, with optional AMS ticket linkage."
        />
        <Button component={Link} to="/ams/user-reports/new" variant="contained">
          Submit User Report
        </Button>
      </Stack>
      <State
        loading={reports.isLoading}
        error={reports.error as Error | null}
      />
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Report</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Reporter</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Source / entity</TableCell>
              <TableCell>Ticket</TableCell>
              <TableCell>Submitted</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(reports.data || []).map((report) => (
              <TableRow key={report.id}>
                <TableCell>
                  <Button
                    component={Link}
                    to={`/ams/user-reports/${report.id}`}
                    size="small"
                  >
                    {report.report_number}
                  </Button>
                </TableCell>
                <TableCell>{report.title}</TableCell>
                <TableCell>
                  {report.reporter_name}
                  <Typography
                    variant="caption"
                    display="block"
                    color="text.secondary"
                  >
                    {report.reporter_persona || "—"}
                  </Typography>
                </TableCell>
                <TableCell>
                  <ChipValue value={report.severity} />
                </TableCell>
                <TableCell>
                  <ChipValue value={report.status} />
                </TableCell>
                <TableCell>
                  {report.report_channel}
                  <Typography
                    variant="caption"
                    display="block"
                    color="text.secondary"
                  >
                    {report.affected_entity_type}
                  </Typography>
                </TableCell>
                <TableCell>
                  {report.ticket ? (
                    <Button
                      component={Link}
                      to={`/ams/tickets/${report.ticket.id}`}
                      size="small"
                    >
                      {report.ticket.ticket_number}
                    </Button>
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell>
                  {new Date(report.submitted_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  <ReportActions report={report} onChanged={refresh} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

const initialForm: UserReportPayload = {
  reporter_name: "Ben Business User",
  reporter_email: "ben.business.user@example.com",
  reporter_persona: "BUSINESS_USER",
  report_channel: "USER_PORTAL",
  source_module: "WAREHOUSE_FULFILLMENT",
  affected_entity_type: "ORDER",
  title: "",
  description: "",
  business_impact: "",
  severity: "MEDIUM",
  create_ticket: true,
};

export function NewUserReportPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<UserReportPayload>(initialForm);
  const update = (key: keyof UserReportPayload, value: string | boolean) =>
    setForm((current) => ({ ...current, [key]: value }));
  const create = useMutation({
    mutationFn: createUserReport,
    onSuccess: (report) => navigate(`/ams/user-reports/${report.id}`),
  });
  return (
    <Box>
      <Header
        title="Submit User Report"
        description="Record a user experience issue that may require AMS support."
      />
      <Card sx={{ maxWidth: 900 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Reporter name"
                value={form.reporter_name}
                onChange={(event) =>
                  update("reporter_name", event.target.value)
                }
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Reporter email"
                value={form.reporter_email}
                onChange={(event) =>
                  update("reporter_email", event.target.value)
                }
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Persona</InputLabel>
                <Select
                  label="Persona"
                  value={form.reporter_persona}
                  onChange={(event) =>
                    update("reporter_persona", event.target.value)
                  }
                >
                  <MenuItem value="BUSINESS_USER">Business User</MenuItem>
                  <MenuItem value="ORDER_MANAGER">Order Manager</MenuItem>
                  <MenuItem value="WAREHOUSE_SUPERVISOR">
                    Warehouse Supervisor
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Report channel</InputLabel>
                <Select
                  label="Report channel"
                  value={form.report_channel}
                  onChange={(event) =>
                    update("report_channel", event.target.value)
                  }
                >
                  <MenuItem value="USER_PORTAL">User Portal</MenuItem>
                  <MenuItem value="MANUAL">Manual</MenuItem>
                  <MenuItem value="PHONE">Phone</MenuItem>
                  <MenuItem value="EMAIL">Email</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Affected entity</InputLabel>
                <Select
                  label="Affected entity"
                  value={form.affected_entity_type}
                  onChange={(event) =>
                    update("affected_entity_type", event.target.value)
                  }
                >
                  <MenuItem value="ORDER">Order</MenuItem>
                  <MenuItem value="TASK">Task</MenuItem>
                  <MenuItem value="SHIPMENT">Shipment</MenuItem>
                  <MenuItem value="INVENTORY">Inventory</MenuItem>
                  <MenuItem value="SCREEN">Screen</MenuItem>
                  <MenuItem value="UNKNOWN">Unknown</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  label="Severity"
                  value={form.severity}
                  onChange={(event) => update("severity", event.target.value)}
                >
                  <MenuItem value="LOW">Low</MenuItem>
                  <MenuItem value="MEDIUM">Medium</MenuItem>
                  <MenuItem value="HIGH">High</MenuItem>
                  <MenuItem value="CRITICAL">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Affected entity ID (optional UUID)"
                value={form.affected_entity_id || ""}
                onChange={(event) =>
                  update("affected_entity_id", event.target.value)
                }
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                required
                label="Title"
                value={form.title}
                onChange={(event) => update("title", event.target.value)}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                required
                multiline
                minRows={4}
                label="Description"
                value={form.description}
                onChange={(event) => update("description", event.target.value)}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                required
                multiline
                minRows={3}
                label="Business impact"
                value={form.business_impact}
                onChange={(event) =>
                  update("business_impact", event.target.value)
                }
              />
            </Grid>
          </Grid>
          <FormControlLabel
            sx={{ mt: 2 }}
            control={
              <Checkbox
                checked={form.create_ticket}
                onChange={(event) =>
                  update("create_ticket", event.target.checked)
                }
              />
            }
            label="Create AMS ticket now"
          />
          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
            <Button
              variant="contained"
              onClick={() =>
                create.mutate({
                  ...form,
                  affected_entity_id: form.affected_entity_id || undefined,
                })
              }
              disabled={
                create.isPending ||
                !form.title ||
                !form.description ||
                !form.business_impact
              }
            >
              Submit report
            </Button>
            <Button component={Link} to="/ams/user-reports">
              Cancel
            </Button>
          </Stack>
          {create.error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {(create.error as Error).message}
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export function UserReportDetailPage() {
  const { reportId = "" } = useParams();
  const queryClient = useQueryClient();
  const report = useQuery({
    queryKey: ["user-reports", reportId],
    queryFn: () => getUserReport(reportId),
    enabled: Boolean(reportId),
  });
  const refresh = () => {
    void queryClient.invalidateQueries({
      queryKey: ["user-reports", reportId],
    });
    refreshReports(queryClient);
  };
  return (
    <Box>
      <Button component={Link} to="/ams/user-reports" sx={{ mb: 2 }}>
        ← Back to user reports
      </Button>
      <State loading={report.isLoading} error={report.error as Error | null} />
      {report.data && <ReportDetail report={report.data} onChanged={refresh} />}
    </Box>
  );
}

function ReportDetail({
  report,
  onChanged,
}: {
  report: UserReport;
  onChanged: () => void;
}) {
  return (
    <Box>
      <Header title={report.report_number} description={report.title} />
      <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
        <ChipValue value={report.status} />
        <ChipValue value={report.severity} />
      </Stack>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6">Issue details</Typography>
              <Typography sx={{ mt: 2, whiteSpace: "pre-wrap" }}>
                {report.description}
              </Typography>
              <Typography variant="subtitle1" sx={{ mt: 3 }}>
                Business impact
              </Typography>
              <Typography>{report.business_impact}</Typography>
              <Typography color="text.secondary" sx={{ mt: 3 }}>
                Affected entity: {report.affected_entity_type}
                {report.affected_entity_id
                  ? ` · ${report.affected_entity_id}`
                  : ""}
              </Typography>
              {report.ticket && (
                <Typography sx={{ mt: 2 }}>
                  Linked ticket:{" "}
                  <Button
                    component={Link}
                    to={`/ams/tickets/${report.ticket.id}`}
                    size="small"
                  >
                    {report.ticket.ticket_number}
                  </Button>
                </Typography>
              )}
              {report.journey_run_id && (
                <Typography sx={{ mt: 1 }}>
                  Journey run:{" "}
                  {report.journey_run_number || report.journey_run_id}
                  {report.journey_code ? ` · ${report.journey_code}` : ""}
                </Typography>
              )}
              <InvestigateWithAgentButton sourceType="USER_ISSUE" sourceId={report.id} />
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Reporter
              </Typography>
              <Typography>{report.reporter_name}</Typography>
              <Typography color="text.secondary">
                {report.reporter_email || "No email"}
              </Typography>
              <Typography color="text.secondary">
                {report.reporter_persona || "—"} · {report.report_channel}
              </Typography>
              <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>
                Lifecycle
              </Typography>
              <Typography>
                Submitted: {new Date(report.submitted_at).toLocaleString()}
              </Typography>
              <Typography>
                Acknowledged:{" "}
                {report.acknowledged_at
                  ? new Date(report.acknowledged_at).toLocaleString()
                  : "—"}
              </Typography>
              <Typography>
                Resolved:{" "}
                {report.resolved_at
                  ? new Date(report.resolved_at).toLocaleString()
                  : "—"}
              </Typography>
              <ReportActions report={report} onChanged={onChanged} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
