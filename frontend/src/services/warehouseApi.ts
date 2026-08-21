const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8050").replace(/\/$/, "");

export interface WarehouseSummary {
  warehouses: number;
  locations: number;
  items: number;
  inventory_units_on_hand: number;
  open_orders: number;
  open_tasks: number;
  shipments_in_progress: number;
  low_stock_items: number;
}

export interface Warehouse {
  id: string;
  code: string;
  name: string;
  region: string;
  city: string;
  country: string;
  status: string;
  zone_count: number;
  location_count: number;
}

export interface InventoryBalance {
  id: string;
  warehouse_id: string;
  warehouse_code: string;
  warehouse_name: string;
  location_id: string;
  location_code: string;
  item_id: string;
  sku: string;
  item_name: string;
  quantity_on_hand: number;
  quantity_allocated: number;
  quantity_available: number;
  low_stock: boolean;
}

export interface Order {
  id: string;
  order_number: string;
  customer_name: string;
  order_type: string;
  priority: string;
  status: string;
  requested_ship_date: string | null;
  line_count: number;
}

export interface FulfillmentTask {
  id: string;
  task_number: string;
  order_id: string;
  order_number: string;
  order_line_id: string | null;
  warehouse_id: string;
  warehouse_code: string;
  task_type: string;
  status: string;
  priority: string;
  assigned_to: string | null;
  due_at: string | null;
}

export interface Shipment {
  id: string;
  shipment_number: string;
  order_id: string;
  order_number: string;
  warehouse_id: string;
  warehouse_code: string;
  carrier: string;
  tracking_number: string | null;
  status: string;
  shipped_at: string | null;
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(apiBaseUrl + path);
  const body = (await response.json().catch(() => ({}))) as T | { detail?: string };
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body && body.detail ? body.detail : "request failed";
    throw new Error("Warehouse API returned " + response.status + ": " + detail);
  }
  return body as T;
}

export function getWarehouseSummary() {
  return get<WarehouseSummary>("/api/v1/warehouse/summary");
}

export function getWarehouses() {
  return get<Warehouse[]>("/api/v1/warehouse/warehouses");
}

export function getInventory(params: { sku?: string; lowStockOnly?: boolean } = {}) {
  const search = new URLSearchParams();
  if (params.sku) search.set("sku", params.sku);
  if (params.lowStockOnly) search.set("low_stock_only", "true");
  return get<InventoryBalance[]>("/api/v1/warehouse/inventory" + (search.size ? "?" + search.toString() : ""));
}

export function getOrders() {
  return get<Order[]>("/api/v1/warehouse/orders");
}

export function getTasks() {
  return get<FulfillmentTask[]>("/api/v1/warehouse/tasks");
}

export function getShipments() {
  return get<Shipment[]>("/api/v1/warehouse/shipments");
}
