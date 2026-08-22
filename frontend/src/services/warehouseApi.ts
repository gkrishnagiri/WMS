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

export interface Item {
  id: string;
  sku: string;
  name: string;
  category: string;
  unit_of_measure: string;
  reorder_point: number;
  safety_stock: number;
  active: boolean;
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

export interface OrderLineDetail {
  id: string;
  line_number: number;
  item_id: string;
  sku: string;
  item_name: string;
  quantity_ordered: number;
  quantity_allocated: number;
  quantity_shipped: number;
}

export interface Allocation {
  id: string;
  order_id: string;
  order_line_id: string;
  warehouse_id: string;
  warehouse_code: string;
  location_id: string;
  location_code: string;
  item_id: string;
  sku: string;
  quantity_allocated: number;
  quantity_picked: number;
  quantity_packed: number;
  quantity_shipped: number;
  status: string;
}

export interface OrderEvent {
  id: string;
  order_id: string;
  event_type: string;
  from_status: string | null;
  to_status: string | null;
  message: string;
  event_payload: Record<string, unknown> | null;
  created_by: string;
  created_at: string;
}

export interface OrderDetail {
  id: string;
  order_number: string;
  customer_name: string;
  order_type: string;
  priority: string;
  status: string;
  requested_ship_date: string | null;
  warehouse_id: string | null;
  lines: OrderLineDetail[];
  allocations: Allocation[];
  tasks: FulfillmentTask[];
  shipments: Shipment[];
  events: OrderEvent[];
}

export interface InventoryTransaction {
  id: string;
  transaction_number: string;
  transaction_type: string;
  warehouse_id: string;
  warehouse_code: string;
  location_id: string;
  location_code: string;
  item_id: string;
  sku: string;
  order_id: string | null;
  order_line_id: string | null;
  allocation_id: string | null;
  task_id: string | null;
  shipment_id: string | null;
  quantity_on_hand_delta: number;
  quantity_allocated_delta: number;
  quantity_on_hand_after: number;
  quantity_allocated_after: number;
  quantity_available_after: number;
  reference_type: string | null;
  reference_number: string | null;
  reason_code: string | null;
  notes: string | null;
  created_by: string;
  created_at: string;
}

export interface CreateOrderPayload {
  customer_name: string;
  order_type: string;
  priority: string;
  requested_ship_date: string | null;
  warehouse_id?: string;
  lines: { item_id: string; quantity_ordered: number }[];
}

export interface ShipOrderPayload {
  carrier: string;
  tracking_number?: string;
  shipped_by?: string;
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
  shipped_by?: string | null;
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

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiBaseUrl + path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
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

export function getItems() {
  return get<Item[]>("/api/v1/warehouse/items?active=true");
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

export function createOrder(payload: CreateOrderPayload) {
  return request<OrderDetail>("/api/v1/warehouse/orders", { method: "POST", body: JSON.stringify(payload) });
}

export function getOrderDetail(orderId: string) {
  return get<OrderDetail>(`/api/v1/warehouse/orders/${orderId}`);
}

export function allocateOrder(orderId: string) {
  return request<OrderDetail>(`/api/v1/warehouse/orders/${orderId}/allocate`, { method: "POST" });
}

export function releaseTasks(orderId: string) {
  return request<OrderDetail>(`/api/v1/warehouse/orders/${orderId}/release-tasks`, { method: "POST" });
}

export function startTask(taskId: string) {
  return request<FulfillmentTask>(`/api/v1/warehouse/tasks/${taskId}/start`, { method: "POST" });
}

export function completeTask(taskId: string) {
  return request<FulfillmentTask>(`/api/v1/warehouse/tasks/${taskId}/complete`, { method: "POST" });
}

export function shipOrder(orderId: string, payload: ShipOrderPayload) {
  return request<OrderDetail>(`/api/v1/warehouse/orders/${orderId}/ship`, { method: "POST", body: JSON.stringify(payload) });
}

export function getOrderEvents(orderId: string) {
  return get<OrderEvent[]>(`/api/v1/warehouse/orders/${orderId}/events`);
}

export function getInventoryTransactions(params: { item_id?: string; warehouse_id?: string; order_id?: string; transaction_type?: string } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value) search.set(key, value); });
  return get<InventoryTransaction[]>("/api/v1/warehouse/inventory-transactions" + (search.size ? "?" + search.toString() : ""));
}
