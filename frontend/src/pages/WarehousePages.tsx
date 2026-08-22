import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Grid,
  Paper,
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
import { Link } from "react-router-dom";
import {
  getInventory,
  getOrders,
  getShipments,
  getTasks,
  getWarehouseSummary,
  getWarehouses,
  type FulfillmentTask,
  type InventoryBalance,
  type Order,
  type Shipment,
} from "../services/warehouseApi";

function PageState({ isLoading, isError, error }: { isLoading: boolean; isError: boolean; error: Error | null }) {
  if (isLoading) {
    return <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}><CircularProgress size={24} /><Typography>Loading warehouse data…</Typography></Box>;
  }
  if (isError) {
    return <Alert severity="error"><strong>Warehouse API unavailable.</strong> Start the EOS backend and ensure the database has been migrated and seeded. {error?.message}</Alert>;
  }
  return null;
}

function StatusChip({ value }: { value: string }) {
  const color = value === "COMPLETED" || value === "SHIPPED" || value === "DELIVERED" ? "success" : value === "BLOCKED" || value === "EXCEPTION" ? "error" : value === "IN_PROGRESS" || value === "READY" ? "warning" : "default";
  return <Chip label={value.replaceAll("_", " ")} color={color} size="small" variant={color === "default" ? "outlined" : "filled"} />;
}

function PageHeader({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <><Typography variant="overline" color="primary">{eyebrow}</Typography><Typography variant="h3" sx={{ mt: 0.5, mb: 1, fontWeight: 700 }}>{title}</Typography><Typography color="text.secondary" sx={{ mb: 4 }}>{description}</Typography></>;
}

function StatCard({ label, value, detail }: { label: string; value: number; detail?: string }) {
  return <Card><CardContent><Typography color="text.secondary">{label}</Typography><Typography variant="h4" sx={{ mt: 1, fontWeight: 700 }}>{value.toLocaleString()}</Typography>{detail && <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>{detail}</Typography>}</CardContent></Card>;
}

export function WarehousePage() {
  const summary = useQuery({ queryKey: ["warehouse", "summary"], queryFn: getWarehouseSummary });
  const warehouses = useQuery({ queryKey: ["warehouse", "warehouses"], queryFn: getWarehouses });
  const error = summary.error || warehouses.error;
  return <Box>
    <PageHeader eyebrow="Warehouse domain" title="Warehouse & Fulfillment Operations" description="A live operational view across fulfillment centers, inventory health, customer demand, and outbound work." />
    <PageState isLoading={summary.isLoading || warehouses.isLoading} isError={summary.isError || warehouses.isError} error={error instanceof Error ? error : null} />
    {summary.data && <Grid container spacing={2} sx={{ mb: 3 }}>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}><StatCard label="Warehouses" value={summary.data.warehouses} /></Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}><StatCard label="Locations" value={summary.data.locations} /></Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}><StatCard label="Units on hand" value={summary.data.inventory_units_on_hand} detail={summary.data.low_stock_items + " low-stock items"} /></Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}><StatCard label="Open orders" value={summary.data.open_orders} detail={summary.data.open_tasks + " open fulfillment tasks"} /></Grid>
    </Grid>}
    {summary.data && <Grid container spacing={2} sx={{ mb: 3 }}>
      <Grid size={{ xs: 12, sm: 4 }}><StatCard label="Open tasks" value={summary.data.open_tasks} /></Grid>
      <Grid size={{ xs: 12, sm: 4 }}><StatCard label="Shipments in progress" value={summary.data.shipments_in_progress} /></Grid>
      <Grid size={{ xs: 12, sm: 4 }}><StatCard label="Active items" value={summary.data.items} /></Grid>
    </Grid>}
    <Card><CardContent><Typography variant="h6" sx={{ mb: 2 }}>Fulfillment centers</Typography><WarehouseTable rows={warehouses.data || []} /></CardContent></Card>
  </Box>;
}

function WarehouseTable({ rows }: { rows: { code: string; name: string; city: string; region: string; status: string; zone_count: number; location_count: number }[] }) {
  return <TableContainer><Table size="small"><TableHead><TableRow><TableCell>Code</TableCell><TableCell>Warehouse</TableCell><TableCell>Region</TableCell><TableCell>Zones</TableCell><TableCell>Locations</TableCell><TableCell>Status</TableCell></TableRow></TableHead><TableBody>{rows.map((row) => <TableRow key={row.code}><TableCell><strong>{row.code}</strong></TableCell><TableCell>{row.name}<Typography variant="caption" display="block" color="text.secondary">{row.city}</Typography></TableCell><TableCell>{row.region}</TableCell><TableCell>{row.zone_count}</TableCell><TableCell>{row.location_count}</TableCell><TableCell><StatusChip value={row.status} /></TableCell></TableRow>)}</TableBody></Table></TableContainer>;
}

export function InventoryPage() {
  const [search, setSearch] = useState("");
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const inventory = useQuery({ queryKey: ["warehouse", "inventory", lowStockOnly], queryFn: () => getInventory({ lowStockOnly }) });
  const visibleRows = inventory.data?.filter((row) => !search || `${row.sku} ${row.item_name}`.toLowerCase().includes(search.toLowerCase()));
  return <Box><PageHeader eyebrow="Warehouse domain" title="Inventory" description="Current item balances by fulfillment center and storage location." /><Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap", mb: 3 }}><TextField size="small" label="Search SKU or item" value={search} onChange={(event) => setSearch(event.target.value)} /><FormControlLabel control={<Checkbox checked={lowStockOnly} onChange={(event) => setLowStockOnly(event.target.checked)} />} label="Low stock only" /></Box><PageState isLoading={inventory.isLoading} isError={inventory.isError} error={inventory.error} />{visibleRows && <InventoryTable rows={visibleRows} />}</Box>;
}

function InventoryTable({ rows }: { rows: InventoryBalance[] }) {
  return <TableContainer component={Paper}><Table size="small"><TableHead><TableRow><TableCell>Warehouse</TableCell><TableCell>Location</TableCell><TableCell>SKU</TableCell><TableCell>Item</TableCell><TableCell align="right">On hand</TableCell><TableCell align="right">Allocated</TableCell><TableCell align="right">Available</TableCell><TableCell>Stock</TableCell></TableRow></TableHead><TableBody>{rows.map((row) => <TableRow key={row.id}><TableCell>{row.warehouse_code}</TableCell><TableCell>{row.location_code}</TableCell><TableCell><strong>{row.sku}</strong></TableCell><TableCell>{row.item_name}</TableCell><TableCell align="right">{row.quantity_on_hand}</TableCell><TableCell align="right">{row.quantity_allocated}</TableCell><TableCell align="right">{row.quantity_available}</TableCell><TableCell>{row.low_stock ? <Chip label="Low stock" color="warning" size="small" /> : <Chip label="Healthy" color="success" size="small" variant="outlined" />}</TableCell></TableRow>)}</TableBody></Table></TableContainer>;
}

export function OrdersPage() {
  const orders = useQuery({ queryKey: ["warehouse", "orders"], queryFn: getOrders });
  return <Box><Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 2 }}><PageHeader eyebrow="Warehouse domain" title="Customer Orders" description="Demand records and their current fulfillment lifecycle status." /><Button component={Link} to="/warehouse/orders/new" variant="contained">Create Order</Button></Box><PageState isLoading={orders.isLoading} isError={orders.isError} error={orders.error} />{orders.data && <OrderTable rows={orders.data} />}</Box>;
}

function OrderTable({ rows }: { rows: Order[] }) {
  return <TableContainer component={Paper}><Table size="small"><TableHead><TableRow><TableCell>Order</TableCell><TableCell>Customer</TableCell><TableCell>Status</TableCell><TableCell>Priority</TableCell><TableCell>Requested ship date</TableCell><TableCell align="right">Lines</TableCell></TableRow></TableHead><TableBody>{rows.map((row) => <TableRow key={row.id}><TableCell><Button component={Link} to={`/warehouse/orders/${row.id}`} size="small">{row.order_number}</Button></TableCell><TableCell>{row.customer_name}</TableCell><TableCell><StatusChip value={row.status} /></TableCell><TableCell><StatusChip value={row.priority} /></TableCell><TableCell>{row.requested_ship_date || "—"}</TableCell><TableCell align="right">{row.line_count}</TableCell></TableRow>)}</TableBody></Table></TableContainer>;
}

export function TasksPage() {
  const tasks = useQuery({ queryKey: ["warehouse", "tasks"], queryFn: getTasks });
  return <Box><PageHeader eyebrow="Warehouse domain" title="Fulfillment Tasks" description="Warehouse work currently open, in progress, blocked, or completed." /><PageState isLoading={tasks.isLoading} isError={tasks.isError} error={tasks.error} />{tasks.data && <TaskTable rows={tasks.data} />}</Box>;
}

function TaskTable({ rows }: { rows: FulfillmentTask[] }) {
  return <TableContainer component={Paper}><Table size="small"><TableHead><TableRow><TableCell>Task</TableCell><TableCell>Type</TableCell><TableCell>Status</TableCell><TableCell>Priority</TableCell><TableCell>Warehouse</TableCell><TableCell>Assigned to</TableCell><TableCell>Due date</TableCell></TableRow></TableHead><TableBody>{rows.map((row) => <TableRow key={row.id}><TableCell><strong>{row.task_number}</strong></TableCell><TableCell>{row.task_type}</TableCell><TableCell><StatusChip value={row.status} /></TableCell><TableCell><StatusChip value={row.priority} /></TableCell><TableCell>{row.warehouse_code}</TableCell><TableCell>{row.assigned_to || "Unassigned"}</TableCell><TableCell>{row.due_at ? new Date(row.due_at).toLocaleDateString() : "—"}</TableCell></TableRow>)}</TableBody></Table></TableContainer>;
}

export function ShipmentsPage() {
  const shipments = useQuery({ queryKey: ["warehouse", "shipments"], queryFn: getShipments });
  return <Box><PageHeader eyebrow="Warehouse domain" title="Shipments" description="Outbound shipment records across the fulfillment network." /><PageState isLoading={shipments.isLoading} isError={shipments.isError} error={shipments.error} />{shipments.data && <ShipmentTable rows={shipments.data} />}</Box>;
}

function ShipmentTable({ rows }: { rows: Shipment[] }) {
  return <TableContainer component={Paper}><Table size="small"><TableHead><TableRow><TableCell>Shipment</TableCell><TableCell>Order</TableCell><TableCell>Warehouse</TableCell><TableCell>Carrier</TableCell><TableCell>Tracking number</TableCell><TableCell>Status</TableCell><TableCell>Shipped date</TableCell></TableRow></TableHead><TableBody>{rows.map((row) => <TableRow key={row.id}><TableCell><strong>{row.shipment_number}</strong></TableCell><TableCell>{row.order_number}</TableCell><TableCell>{row.warehouse_code}</TableCell><TableCell>{row.carrier}</TableCell><TableCell>{row.tracking_number || "—"}</TableCell><TableCell><StatusChip value={row.status} /></TableCell><TableCell>{row.shipped_at ? new Date(row.shipped_at).toLocaleDateString() : "—"}</TableCell></TableRow>)}</TableBody></Table></TableContainer>;
}
