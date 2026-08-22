import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import {
  allocateOrder,
  completeTask,
  createOrder,
  getInventoryTransactions,
  getItems,
  getOrderDetail,
  getTasks,
  releaseTasks,
  shipOrder,
  startTask,
  type FulfillmentTask,
  type InventoryTransaction,
  type OrderDetail,
} from "../services/warehouseApi";
import { getWarehouses } from "../services/warehouseApi";

function ErrorAlert({ error }: { error: unknown }) {
  return error ? <Alert severity="error">{error instanceof Error ? error.message : "Warehouse workflow request failed."}</Alert> : null;
}

function WorkflowAction({ label, onClick, disabled, loading }: { label: string; onClick: () => void; disabled?: boolean; loading?: boolean }) {
  return <Button variant="contained" onClick={onClick} disabled={disabled || loading}>{loading ? <CircularProgress size={18} color="inherit" /> : label}</Button>;
}

export function CreateOrderPage() {
  const navigate = useNavigate();
  const items = useQuery({ queryKey: ["warehouse", "items", "active"], queryFn: getItems });
  const warehouses = useQuery({ queryKey: ["warehouse", "warehouses"], queryFn: getWarehouses });
  const [customerName, setCustomerName] = useState("");
  const [priority, setPriority] = useState("NORMAL");
  const [orderType, setOrderType] = useState("STANDARD");
  const [requestedShipDate, setRequestedShipDate] = useState("");
  const [warehouseId, setWarehouseId] = useState("");
  const [lines, setLines] = useState([{ item_id: "", quantity_ordered: 1 }]);
  const mutation = useMutation({
    mutationFn: createOrder,
    onSuccess: (order) => navigate(`/warehouse/orders/${order.id}`),
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!customerName.trim() || lines.some((line) => !line.item_id || line.quantity_ordered < 1)) return;
    mutation.mutate({ customer_name: customerName.trim(), order_type: orderType, priority, requested_ship_date: requestedShipDate || null, warehouse_id: warehouseId || undefined, lines });
  };

  return <Box>
    <Typography variant="overline" color="primary">Warehouse workflow</Typography>
    <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>Create Order</Typography>
    <Typography color="text.secondary" sx={{ mb: 3 }}>Create demand first; inventory is reserved in the separate allocation step.</Typography>
    <ErrorAlert error={mutation.error} />
    <Card component="form" onSubmit={submit} sx={{ maxWidth: 900 }}>
      <CardContent>
        <Stack spacing={2}>
          <TextField label="Customer name" value={customerName} onChange={(event) => setCustomerName(event.target.value)} required />
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <TextField select label="Order type" value={orderType} onChange={(event) => setOrderType(event.target.value)} fullWidth><MenuItem value="STANDARD">Standard</MenuItem><MenuItem value="EXPRESS">Express</MenuItem></TextField>
            <TextField select label="Priority" value={priority} onChange={(event) => setPriority(event.target.value)} fullWidth><MenuItem value="LOW">Low</MenuItem><MenuItem value="NORMAL">Normal</MenuItem><MenuItem value="HIGH">High</MenuItem><MenuItem value="URGENT">Urgent</MenuItem></TextField>
            <TextField type="date" label="Requested ship date" value={requestedShipDate} onChange={(event) => setRequestedShipDate(event.target.value)} slotProps={{ inputLabel: { shrink: true } }} fullWidth />
          </Stack>
          <TextField select label="Warehouse (optional)" value={warehouseId} onChange={(event) => setWarehouseId(event.target.value)} helperText="If omitted, allocation selects the first deterministic available location.">
            <MenuItem value="">Any active warehouse</MenuItem>
            {(warehouses.data || []).map((warehouse) => <MenuItem key={warehouse.id} value={warehouse.id}>{warehouse.code} — {warehouse.name}</MenuItem>)}
          </TextField>
          <Typography variant="h6">Order lines</Typography>
          {lines.map((line, index) => <Stack key={index} direction={{ xs: "column", sm: "row" }} spacing={2}>
            <TextField select label={`Item ${index + 1}`} value={line.item_id} onChange={(event) => setLines((current) => current.map((value, i) => i === index ? { ...value, item_id: event.target.value } : value))} fullWidth required>
              {(items.data || []).map((item) => <MenuItem key={item.id} value={item.id}>{item.sku} — {item.name}</MenuItem>)}
            </TextField>
            <TextField type="number" label="Quantity" value={line.quantity_ordered} onChange={(event) => setLines((current) => current.map((value, i) => i === index ? { ...value, quantity_ordered: Number(event.target.value) } : value))} inputProps={{ min: 1 }} sx={{ width: { sm: 160 } }} required />
            <Button type="button" color="error" onClick={() => setLines((current) => current.filter((_, i) => i !== index))} disabled={lines.length === 1}>Remove</Button>
          </Stack>)}
          <Button type="button" variant="outlined" onClick={() => setLines((current) => [...current, { item_id: "", quantity_ordered: 1 }])} sx={{ alignSelf: "flex-start" }}>Add line</Button>
          <Box><Button type="submit" variant="contained" disabled={mutation.isPending || items.isLoading}>Create Order</Button></Box>
        </Stack>
      </CardContent>
    </Card>
  </Box>;
}

function WorkflowSections({ order }: { order: OrderDetail }) {
  return <Stack spacing={3}>
    <Card><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Order lines</Typography><TableContainer><Table size="small"><TableHead><TableRow><TableCell>Line</TableCell><TableCell>Item</TableCell><TableCell align="right">Ordered</TableCell><TableCell align="right">Allocated</TableCell><TableCell align="right">Shipped</TableCell></TableRow></TableHead><TableBody>{order.lines.map((line) => <TableRow key={line.id}><TableCell>{line.line_number}</TableCell><TableCell><strong>{line.sku}</strong><Typography variant="caption" display="block">{line.item_name}</Typography></TableCell><TableCell align="right">{line.quantity_ordered}</TableCell><TableCell align="right">{line.quantity_allocated}</TableCell><TableCell align="right">{line.quantity_shipped}</TableCell></TableRow>)}</TableBody></Table></TableContainer></CardContent></Card>
    <Card><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Allocations</Typography><TableContainer><Table size="small"><TableHead><TableRow><TableCell>Item</TableCell><TableCell>Warehouse</TableCell><TableCell>Location</TableCell><TableCell>Status</TableCell><TableCell align="right">Allocated</TableCell><TableCell align="right">Picked</TableCell><TableCell align="right">Packed</TableCell><TableCell align="right">Shipped</TableCell></TableRow></TableHead><TableBody>{order.allocations.map((allocation) => <TableRow key={allocation.id}><TableCell>{allocation.sku}</TableCell><TableCell>{allocation.warehouse_code}</TableCell><TableCell>{allocation.location_code}</TableCell><TableCell>{allocation.status}</TableCell><TableCell align="right">{allocation.quantity_allocated}</TableCell><TableCell align="right">{allocation.quantity_picked}</TableCell><TableCell align="right">{allocation.quantity_packed}</TableCell><TableCell align="right">{allocation.quantity_shipped}</TableCell></TableRow>)}</TableBody></Table></TableContainer>{!order.allocations.length && <Typography color="text.secondary">No inventory has been allocated.</Typography>}</CardContent></Card>
    <Card><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Fulfillment tasks</Typography><TaskRows tasks={order.tasks} /></CardContent></Card>
    <Card><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Shipments</Typography>{order.shipments.length ? <TableContainer><Table size="small"><TableHead><TableRow><TableCell>Shipment</TableCell><TableCell>Carrier</TableCell><TableCell>Tracking</TableCell><TableCell>Status</TableCell><TableCell>Shipped at</TableCell></TableRow></TableHead><TableBody>{order.shipments.map((shipment) => <TableRow key={shipment.id}><TableCell>{shipment.shipment_number}</TableCell><TableCell>{shipment.carrier}</TableCell><TableCell>{shipment.tracking_number || "—"}</TableCell><TableCell>{shipment.status}</TableCell><TableCell>{shipment.shipped_at ? new Date(shipment.shipped_at).toLocaleString() : "—"}</TableCell></TableRow>)}</TableBody></Table></TableContainer> : <Typography color="text.secondary">No shipment has been confirmed.</Typography>}</CardContent></Card>
    <Card><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Recent order events</Typography>{order.events.map((event) => <Box key={event.id} sx={{ mb: 1.5 }}><Typography variant="body2"><strong>{event.event_type.replaceAll("_", " ")}</strong> — {event.message}</Typography><Typography variant="caption" color="text.secondary">{new Date(event.created_at).toLocaleString()}</Typography></Box>)}</CardContent></Card>
  </Stack>;
}

function TaskRows({ tasks, actions = false }: { tasks: FulfillmentTask[]; actions?: boolean }) {
  const queryClient = useQueryClient();
  const start = useMutation({ mutationFn: startTask, onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ["warehouse", "tasks"] }); void queryClient.invalidateQueries({ queryKey: ["warehouse", "order"] }); } });
  const complete = useMutation({ mutationFn: completeTask, onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ["warehouse", "tasks"] }); void queryClient.invalidateQueries({ queryKey: ["warehouse", "order"] }); } });
  return <><ErrorAlert error={start.error || complete.error} /><TableContainer><Table size="small"><TableHead><TableRow><TableCell>Task</TableCell><TableCell>Type</TableCell><TableCell>Status</TableCell><TableCell>Warehouse</TableCell><TableCell>Actions</TableCell></TableRow></TableHead><TableBody>{tasks.map((task) => <TableRow key={task.id}><TableCell>{task.task_number}</TableCell><TableCell>{task.task_type}</TableCell><TableCell>{task.status}</TableCell><TableCell>{task.warehouse_code}</TableCell><TableCell>{actions && <Stack direction="row" spacing={1}>{task.status === "OPEN" && <Button size="small" onClick={() => start.mutate(task.id)}>Start</Button>}{(task.status === "OPEN" || task.status === "IN_PROGRESS") && <Button size="small" onClick={() => complete.mutate(task.id)}>Complete</Button>}</Stack>}</TableCell></TableRow>)}</TableBody></Table></TableContainer></>;
}

export function OrderDetailPage() {
  const { orderId = "" } = useParams();
  const queryClient = useQueryClient();
  const order = useQuery({ queryKey: ["warehouse", "order", orderId], queryFn: () => getOrderDetail(orderId), enabled: Boolean(orderId) });
  const refresh = () => { void queryClient.invalidateQueries({ queryKey: ["warehouse", "order", orderId] }); void queryClient.invalidateQueries({ queryKey: ["warehouse", "orders"] }); void queryClient.invalidateQueries({ queryKey: ["warehouse", "tasks"] }); void queryClient.invalidateQueries({ queryKey: ["warehouse", "inventory"] }); void queryClient.invalidateQueries({ queryKey: ["warehouse", "transactions"] }); void queryClient.invalidateQueries({ queryKey: ["warehouse", "shipments"] }); };
  const allocate = useMutation({ mutationFn: allocateOrder, onSuccess: refresh });
  const release = useMutation({ mutationFn: releaseTasks, onSuccess: refresh });
  const ship = useMutation({ mutationFn: (id: string) => shipOrder(id, { carrier: "UPS", shipped_by: "system" }), onSuccess: refresh });
  if (order.isLoading) return <CircularProgress />;
  if (order.isError || !order.data) return <ErrorAlert error={order.error} />;
  const current = order.data;
  const readyToShip = current.status === "PACKING" && current.tasks.length > 0 && current.tasks.every((task) => task.status === "COMPLETED");
  return <Box>
    <Typography variant="overline" color="primary">Warehouse workflow</Typography>
    <Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>{current.order_number}</Typography>
    <Typography color="text.secondary" sx={{ mb: 2 }}>{current.customer_name} · {current.order_type} · {current.priority} · {current.status}</Typography>
    <Stack direction="row" spacing={1} sx={{ mb: 3, flexWrap: "wrap" }}>
      {current.status === "NEW" && <WorkflowAction label="Allocate" onClick={() => allocate.mutate(current.id)} loading={allocate.isPending} />}
      {current.status === "ALLOCATED" && <WorkflowAction label="Release Tasks" onClick={() => release.mutate(current.id)} loading={release.isPending} />}
      {readyToShip && <WorkflowAction label="Ship Order" onClick={() => ship.mutate(current.id)} loading={ship.isPending} />}
    </Stack>
    <ErrorAlert error={allocate.error || release.error || ship.error} />
    <WorkflowSections order={current} />
  </Box>;
}

export function InventoryTransactionsPage() {
  const transactions = useQuery({ queryKey: ["warehouse", "transactions"], queryFn: () => getInventoryTransactions() });
  return <Box><Typography variant="overline" color="primary">Warehouse workflow</Typography><Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>Inventory Transactions</Typography><Typography color="text.secondary" sx={{ mb: 3 }}>Auditable reservations, confirmations, and shipment issues. Newest transactions appear first.</Typography><ErrorAlert error={transactions.error} />{transactions.isLoading ? <CircularProgress /> : <TransactionTable rows={transactions.data || []} />}</Box>;
}

function TransactionTable({ rows }: { rows: InventoryTransaction[] }) {
  return <TableContainer component={Paper}><Table size="small"><TableHead><TableRow><TableCell>Transaction</TableCell><TableCell>Type</TableCell><TableCell>Warehouse</TableCell><TableCell>Location</TableCell><TableCell>Item</TableCell><TableCell align="right">On-hand Δ</TableCell><TableCell align="right">Allocated Δ</TableCell><TableCell align="right">On-hand after</TableCell><TableCell align="right">Allocated after</TableCell><TableCell align="right">Available after</TableCell><TableCell>Reference</TableCell><TableCell>Created</TableCell></TableRow></TableHead><TableBody>{rows.map((row) => <TableRow key={row.id}><TableCell><strong>{row.transaction_number}</strong></TableCell><TableCell>{row.transaction_type.replaceAll("_", " ")}</TableCell><TableCell>{row.warehouse_code}</TableCell><TableCell>{row.location_code}</TableCell><TableCell>{row.sku}</TableCell><TableCell align="right">{row.quantity_on_hand_delta}</TableCell><TableCell align="right">{row.quantity_allocated_delta}</TableCell><TableCell align="right">{row.quantity_on_hand_after}</TableCell><TableCell align="right">{row.quantity_allocated_after}</TableCell><TableCell align="right">{row.quantity_available_after}</TableCell><TableCell>{row.reference_number || "—"}</TableCell><TableCell>{new Date(row.created_at).toLocaleString()}</TableCell></TableRow>)}</TableBody></Table></TableContainer>;
}

export function WorkflowTasksPage() {
  const tasks = useQuery({ queryKey: ["warehouse", "tasks"], queryFn: getTasks });
  return <Box><Typography variant="overline" color="primary">Warehouse workflow</Typography><Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>Fulfillment Tasks</Typography><Typography color="text.secondary" sx={{ mb: 3 }}>Start and complete the controlled pick and pack work released from orders.</Typography><ErrorAlert error={tasks.error} />{tasks.isLoading ? <CircularProgress /> : <TaskRows tasks={tasks.data || []} actions />}</Box>;
}
