import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { Alert, Box, Button, Card, CardContent, Checkbox, CircularProgress, FormControlLabel, Grid, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Typography, Chip } from "@mui/material";
import { acknowledgeException, createTicketFromException, getExceptions, resolveException, simulateLowStock, simulateOrderStuck, simulateShipmentException, simulateTaskBlocked, type OperationalException, type SimulationResult } from "../services/operationsApi";
import { acknowledgeTicket, closeTicket, getAmsSummary, getTicket, getTickets, resolveTicket, startTicketWork, type AmsTicket } from "../services/amsApi";

function State({ loading, error }: { loading: boolean; error: Error | null }) {
  if (loading) return <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}><CircularProgress size={22} /><Typography>Loading supportability data…</Typography></Box>;
  if (error) return <Alert severity="error" sx={{ mb: 2 }}>{error.message}</Alert>;
  return null;
}

function ValueChip({ value }: { value: string }) {
  const color = value === "CRITICAL" || value === "HIGH" || value === "OPEN" || value === "IN_PROGRESS" ? "error" : value === "MEDIUM" || value === "ACKNOWLEDGED" || value === "NEW" ? "warning" : value === "RESOLVED" || value === "CLOSED" ? "success" : "default";
  return <Chip size="small" label={value.replaceAll("_", " ")} color={color} variant={color === "default" ? "outlined" : "filled"} />;
}

function Header({ title, description }: { title: string; description: string }) {
  return <><Typography variant="overline" color="primary">Supportability</Typography><Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>{title}</Typography><Typography color="text.secondary" sx={{ mb: 4 }}>{description}</Typography></>;
}

function refreshSupport(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: ["operations", "exceptions"] });
  void queryClient.invalidateQueries({ queryKey: ["ams", "tickets"] });
  void queryClient.invalidateQueries({ queryKey: ["ams", "summary"] });
}

export function OperationsExceptionsPage() {
  const queryClient = useQueryClient();
  const exceptions = useQuery({ queryKey: ["operations", "exceptions"], queryFn: () => getExceptions() });
  const action = useMutation({ mutationFn: async ({ id, type }: { id: string; type: "ack" | "resolve" | "ticket" }) => { if (type === "ack") await acknowledgeException(id); else if (type === "resolve") await resolveException(id); else await createTicketFromException(id); }, onSuccess: () => refreshSupport(queryClient) });
  return <Box><Header title="Operational Exceptions" description="Business-process symptoms detected or simulated across warehouse fulfillment." /><State loading={exceptions.isLoading} error={exceptions.error as Error | null} />{action.error && <Alert severity="error" sx={{ mb: 2 }}>{(action.error as Error).message}</Alert>}<TableContainer component={Paper}><Table size="small"><TableHead><TableRow><TableCell>Exception</TableCell><TableCell>Type</TableCell><TableCell>Severity</TableCell><TableCell>Status</TableCell><TableCell>Source</TableCell><TableCell>Title</TableCell><TableCell>Last detected</TableCell><TableCell>Actions</TableCell></TableRow></TableHead><TableBody>{(exceptions.data || []).map((row) => <TableRow key={row.id}><TableCell><strong>{row.exception_number}</strong></TableCell><TableCell>{row.exception_type.replaceAll("_", " ")}</TableCell><TableCell><ValueChip value={row.severity} /></TableCell><TableCell><ValueChip value={row.status} /></TableCell><TableCell>{row.source_entity_type}<Typography variant="caption" display="block" color="text.secondary">{row.source_reference || "—"}</Typography></TableCell><TableCell>{row.title}</TableCell><TableCell>{new Date(row.last_detected_at).toLocaleString()}</TableCell><TableCell><Stack direction="row" spacing={1}>{row.status === "OPEN" && <Button size="small" onClick={() => action.mutate({ id: row.id, type: "ack" })}>Acknowledge</Button>}{row.status !== "RESOLVED" && row.status !== "SUPPRESSED" && <Button size="small" onClick={() => action.mutate({ id: row.id, type: "resolve" })}>Resolve</Button>}{row.linked_ticket_id ? <Button component={Link} to={`/ams/tickets/${row.linked_ticket_id}`} size="small">{row.linked_ticket_number}</Button> : <Button size="small" onClick={() => action.mutate({ id: row.id, type: "ticket" })}>Create ticket</Button>}</Stack></TableCell></TableRow>)}</TableBody></Table></TableContainer></Box>;
}

const simulations = [
  { key: "low-stock", title: "Low Stock", description: "Reduce a deterministic balance below its reorder point.", run: simulateLowStock },
  { key: "task-blocked", title: "Task Blocked", description: "Mark an eligible fulfillment task as blocked.", run: simulateTaskBlocked },
  { key: "shipment-exception", title: "Shipment Exception", description: "Mark an eligible shipment as an outbound exception.", run: simulateShipmentException },
  { key: "order-stuck", title: "Order Stuck", description: "Place an active order in PICKING beyond the detection threshold.", run: simulateOrderStuck },
];

export function OperationsSimulationsPage() {
  const [createTicket, setCreateTicket] = useState(true);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const simulation = useMutation({ mutationFn: ({ run }: { run: (createTicket: boolean) => Promise<SimulationResult> }) => run(createTicket), onSuccess: setResult });
  return <Box><Header title="Failure Simulations" description="Controlled, deterministic demo tools for generating supportability signals." /><FormControlLabel control={<Checkbox checked={createTicket} onChange={(event) => setCreateTicket(event.target.checked)} />} label="Create an AMS ticket from the exception" /><Grid container spacing={2} sx={{ mt: 1 }}>{simulations.map((item) => <Grid key={item.key} size={{ xs: 12, sm: 6 }}><Card><CardContent><Typography variant="h6">{item.title}</Typography><Typography color="text.secondary" sx={{ minHeight: 48, mt: 1 }}>{item.description}</Typography><Button variant="contained" onClick={() => simulation.mutate({ run: item.run })} disabled={simulation.isPending} sx={{ mt: 2 }}>Run simulation</Button></CardContent></Card></Grid>)}</Grid>{simulation.error && <Alert severity="error" sx={{ mt: 3 }}>{(simulation.error as Error).message}</Alert>}{result && <Card sx={{ mt: 3 }}><CardContent><Typography variant="h6">Simulation result</Typography><Typography sx={{ mt: 1 }}>Exception: <strong>{result.exception.exception_number}</strong> · <ValueChip value={result.exception.status} /></Typography><Typography sx={{ mt: 1 }}>{result.exception.title}</Typography>{result.ticket && <Typography sx={{ mt: 1 }}>Ticket: <Button component={Link} to={`/ams/tickets/${result.ticket.id}`} size="small">{result.ticket.ticket_number}</Button></Typography>}</CardContent></Card>}</Box>;
}

function TicketActions({ ticket, onChanged }: { ticket: AmsTicket; onChanged: () => void }) {
  const action = useMutation({ mutationFn: ({ type, id }: { type: string; id: string }) => { if (type === "ack") return acknowledgeTicket(id); if (type === "start") return startTicketWork(id); if (type === "close") return closeTicket(id); return resolveTicket(id, window.prompt("Resolution code", "WORKAROUND_APPLIED") || "WORKAROUND_APPLIED", window.prompt("Resolution notes", "Deterministic support action completed.") || "Deterministic support action completed."); }, onSuccess: onChanged });
  return <Stack direction="row" spacing={1}>{ticket.status === "NEW" && <Button size="small" onClick={() => action.mutate({ type: "ack", id: ticket.id })}>Acknowledge</Button>}{(ticket.status === "NEW" || ticket.status === "ACKNOWLEDGED") && <Button size="small" onClick={() => action.mutate({ type: "start", id: ticket.id })}>Start work</Button>}{(ticket.status === "NEW" || ticket.status === "ACKNOWLEDGED" || ticket.status === "IN_PROGRESS") && <Button size="small" onClick={() => action.mutate({ type: "resolve", id: ticket.id })}>Resolve</Button>}{ticket.status === "RESOLVED" && <Button size="small" onClick={() => action.mutate({ type: "close", id: ticket.id })}>Close</Button>}{action.error && <Typography color="error" variant="caption">{(action.error as Error).message}</Typography>}</Stack>;
}

function SummaryCard({ label, value }: { label: string; value: number }) { return <Card><CardContent><Typography color="text.secondary">{label}</Typography><Typography variant="h4" sx={{ mt: 1, fontWeight: 700 }}>{value.toLocaleString()}</Typography></CardContent></Card>; }

export function AmsTicketsPage() {
  const queryClient = useQueryClient();
  const summary = useQuery({ queryKey: ["ams", "summary"], queryFn: getAmsSummary });
  const tickets = useQuery({ queryKey: ["ams", "tickets"], queryFn: getTickets });
  const refresh = () => refreshSupport(queryClient);
  return <Box><Header title="AMS Tickets" description="Support work created from operational exceptions and manual demo scenarios." /><State loading={summary.isLoading || tickets.isLoading} error={(summary.error || tickets.error) as Error | null} />{summary.data && <Grid container spacing={2} sx={{ mb: 3 }}><Grid size={{ xs: 6, md: 3 }}><SummaryCard label="Open exceptions" value={summary.data.open_exceptions} /></Grid><Grid size={{ xs: 6, md: 3 }}><SummaryCard label="Critical exceptions" value={summary.data.critical_exceptions} /></Grid><Grid size={{ xs: 6, md: 3 }}><SummaryCard label="Open tickets" value={summary.data.open_tickets} /></Grid><Grid size={{ xs: 6, md: 3 }}><SummaryCard label="In progress" value={summary.data.tickets_in_progress} /></Grid></Grid>}<TableContainer component={Paper}><Table size="small"><TableHead><TableRow><TableCell>Ticket</TableCell><TableCell>Type</TableCell><TableCell>Priority</TableCell><TableCell>Severity</TableCell><TableCell>Status</TableCell><TableCell>Description</TableCell><TableCell>Assignment group</TableCell><TableCell>Opened</TableCell><TableCell>Actions</TableCell></TableRow></TableHead><TableBody>{(tickets.data || []).map((ticket) => <TableRow key={ticket.id}><TableCell><Button component={Link} to={`/ams/tickets/${ticket.id}`} size="small">{ticket.ticket_number}</Button></TableCell><TableCell>{ticket.ticket_type}</TableCell><TableCell><ValueChip value={ticket.priority} /></TableCell><TableCell><ValueChip value={ticket.severity} /></TableCell><TableCell><ValueChip value={ticket.status} /></TableCell><TableCell>{ticket.short_description}</TableCell><TableCell>{ticket.assignment_group}</TableCell><TableCell>{new Date(ticket.opened_at).toLocaleString()}</TableCell><TableCell><TicketActions ticket={ticket} onChanged={refresh} /></TableCell></TableRow>)}</TableBody></Table></TableContainer></Box>;
}

export function AmsTicketDetailPage() {
  const { ticketId = "" } = useParams();
  const queryClient = useQueryClient();
  const ticket = useQuery({ queryKey: ["ams", "ticket", ticketId], queryFn: () => getTicket(ticketId), enabled: Boolean(ticketId) });
  const refresh = () => { void queryClient.invalidateQueries({ queryKey: ["ams", "ticket", ticketId] }); refreshSupport(queryClient); };
  return <Box><Button component={Link} to="/ams/tickets" sx={{ mb: 2 }}>← Back to AMS tickets</Button><State loading={ticket.isLoading} error={ticket.error as Error | null} />{ticket.data && <TicketDetail ticket={ticket.data} onChanged={refresh} />}</Box>;
}

function TicketDetail({ ticket, onChanged }: { ticket: AmsTicket; onChanged: () => void }) {
  const [resolutionCode, setResolutionCode] = useState(ticket.resolution_code || "WORKAROUND_APPLIED");
  const [resolutionNotes, setResolutionNotes] = useState(ticket.resolution_notes || "Deterministic support action completed.");
  const resolve = useMutation({ mutationFn: () => resolveTicket(ticket.id, resolutionCode, resolutionNotes), onSuccess: onChanged });
  return <Box><Typography variant="overline" color="primary">AMS ticket detail</Typography><Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>{ticket.ticket_number}</Typography><Stack direction="row" spacing={1} sx={{ mb: 3 }}><ValueChip value={ticket.status} /><ValueChip value={ticket.priority} /><ValueChip value={ticket.severity} /></Stack><Grid container spacing={2}><Grid size={{ xs: 12, md: 8 }}><Card><CardContent><Typography variant="h6">{ticket.short_description}</Typography><Typography sx={{ mt: 2, whiteSpace: "pre-wrap" }}>{ticket.description}</Typography><Typography color="text.secondary" sx={{ mt: 2 }}>Assignment: {ticket.assignment_group} · {ticket.application_name} · {ticket.environment}</Typography>{ticket.exception && <Box sx={{ mt: 3, p: 2, bgcolor: "background.default", borderRadius: 2 }}><Typography variant="subtitle1">Linked exception</Typography><Typography>{ticket.exception.exception_number} · {ticket.exception.title}</Typography><Typography color="text.secondary">{ticket.exception.description}</Typography></Box>}</CardContent></Card>{ticket.status !== "RESOLVED" && ticket.status !== "CLOSED" && <Card sx={{ mt: 2 }}><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Resolution</Typography><Stack spacing={2}><TextField label="Resolution code" value={resolutionCode} onChange={(event) => setResolutionCode(event.target.value)} /><TextField label="Resolution notes" multiline minRows={3} value={resolutionNotes} onChange={(event) => setResolutionNotes(event.target.value)} /><Button variant="contained" onClick={() => resolve.mutate()} disabled={resolve.isPending}>Resolve ticket</Button>{resolve.error && <Alert severity="error">{(resolve.error as Error).message}</Alert>}</Stack></CardContent></Card>}</Grid><Grid size={{ xs: 12, md: 4 }}><Card><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Lifecycle</Typography><Stack spacing={1}><Typography>Opened: {new Date(ticket.opened_at).toLocaleString()}</Typography><Typography>Acknowledged: {ticket.acknowledged_at ? new Date(ticket.acknowledged_at).toLocaleString() : "—"}</Typography><Typography>Resolved: {ticket.resolved_at ? new Date(ticket.resolved_at).toLocaleString() : "—"}</Typography><Typography>Closed: {ticket.closed_at ? new Date(ticket.closed_at).toLocaleString() : "—"}</Typography><TicketActions ticket={ticket} onChanged={onChanged} /></Stack></CardContent></Card><Card sx={{ mt: 2 }}><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Event timeline</Typography><Stack spacing={2}>{ticket.events.map((event) => <Box key={event.id}><Typography variant="body2" fontWeight={700}>{event.event_type.replaceAll("_", " ")}</Typography><Typography variant="body2">{event.message}</Typography><Typography variant="caption" color="text.secondary">{new Date(event.created_at).toLocaleString()}</Typography></Box>)}</Stack></CardContent></Card></Grid></Grid></Box>;
}
