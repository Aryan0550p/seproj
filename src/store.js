/**
 * Shared Data Store – localStorage-backed persistence layer
 * Connects Admin, Salesman & Retailer through unified data.
 */
const KEYS = {
  PRODUCTS: 'yumsie_products',
  ORDERS: 'yumsie_orders',
  LOGS: 'yumsie_activity_logs',
  ALERTS: 'yumsie_discrepancy_alerts',
  NOTIFICATIONS: 'yumsie_notifications',
  SAMPLE_DISTRIBUTIONS: 'yumsie_sample_distributions',
  PHYSICAL_STOCKS: 'yumsie_physical_stocks',
  STOCK_ADJUSTMENTS: 'yumsie_stock_adjustments',
  INITIALIZED: 'yumsie_store_init'
}

const MAX_ACTIVITY_LOGS = 1000

// ─── Seed Data ────────────────────────────────────────────
const SEED_PRODUCTS = [
  { id: 'P001', name: 'Premium Coffee Beans', category: 'Beverages', price: 1200, unit: 'kg', stock: 150, sku: 'SKU001' },
  { id: 'P002', name: 'Organic Green Tea', category: 'Beverages', price: 850, unit: 'kg', stock: 80, sku: 'SKU002' },
  { id: 'P003', name: 'Whole Wheat Flour', category: 'Pantry', price: 45, unit: 'kg', stock: 500, sku: 'SKU003' },
  { id: 'P004', name: 'Almond Oil', category: 'Pantry', price: 1500, unit: 'L', stock: 0, sku: 'SKU004' },
  { id: 'P005', name: 'Raw Honey Crate', category: 'Pantry', price: 4500, unit: '10kg', stock: 25, sku: 'SKU005' },
  { id: 'P006', name: 'Premium Rice 5kg', category: 'Grains', price: 260, unit: '5kg', stock: 150, sku: 'SKU006' },
  { id: 'P007', name: 'Organic Sugar 2kg', category: 'Sweeteners', price: 125, unit: '2kg', stock: 25, sku: 'SKU007' },
  { id: 'P008', name: 'Refined Oil 1L', category: 'Oils', price: 88, unit: 'L', stock: 0, sku: 'SKU008' }
]

const SEED_ORDERS = [
  { id: 'ORD-1001', customer: 'Retail Corp A', createdBy: 'retailer1', date: '2026-03-10', items: [{ productId: 'P001', name: 'Premium Coffee Beans', qty: 10, price: 1200 }], total: 12000, status: 'Delivered', payment: 'Paid' },
  { id: 'ORD-1002', customer: 'Shop B', createdBy: 'salesman1', date: '2026-03-12', items: [{ productId: 'P003', name: 'Whole Wheat Flour', qty: 100, price: 45 }], total: 4500, status: 'Shipped', payment: 'Paid' },
  { id: 'ORD-1003', customer: 'Mart C', createdBy: 'retailer1', date: '2026-03-15', items: [{ productId: 'P006', name: 'Premium Rice 5kg', qty: 50, price: 260 }], total: 13000, status: 'Pending', payment: 'Unpaid' },
  { id: 'ORD-1004', customer: 'Store D', createdBy: 'salesman1', date: '2026-03-16', items: [{ productId: 'P002', name: 'Organic Green Tea', qty: 20, price: 850 }], total: 17000, status: 'Pending', payment: 'Unpaid' },
  { id: 'ORD-1005', customer: 'Retail Corp A', createdBy: 'retailer1', date: '2026-03-17', items: [{ productId: 'P005', name: 'Raw Honey Crate', qty: 5, price: 4500 }], total: 22500, status: 'Shipped', payment: 'Unpaid' }
]

// ─── Helpers ──────────────────────────────────────────────
function load(key) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function save(key, data) {
  localStorage.setItem(key, JSON.stringify(data))
}

function ensureArrayKey(key) {
  const value = load(key)
  if (!Array.isArray(value)) save(key, [])
}

function nextId(prefix, list) {
  const nums = list.map(item => {
    const match = item.id.match(/(\d+)$/)
    return match ? parseInt(match[1]) : 0
  })
  const max = nums.length ? Math.max(...nums) : 0
  return `${prefix}${String(max + 1).padStart(4, '0')}`
}

function nextRecordId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`
}

function nowIso() {
  return new Date().toISOString()
}

function calculateOrderExpectedTotal(order) {
  const items = Array.isArray(order.items) ? order.items : []
  return items.reduce((sum, item) => {
    const qty = Number(item.qty || 0)
    const price = Number(item.price || 0)
    return sum + (qty * price)
  }, 0)
}

function evaluateOrderCompletion(order) {
  const deliveryConfirmed = order.status === 'Delivered'
  const paymentCompleted = order.payment === 'Paid'
  return {
    deliveryConfirmed,
    paymentCompleted,
    canFinalize: deliveryConfirmed && paymentCompleted
  }
}

function applyOrderCompletionState(order, previousOrder = null) {
  const completion = evaluateOrderCompletion(order)
  const finalizedAt = completion.canFinalize
    ? (order.finalizedAt || previousOrder?.finalizedAt || nowIso())
    : null

  return {
    ...order,
    deliveryConfirmed: completion.deliveryConfirmed,
    paymentCompleted: completion.paymentCompleted,
    isFinalized: completion.canFinalize,
    finalizedAt
  }
}

function createActivityLog({
  action,
  entityType,
  entityId,
  description,
  metadata = {}
}) {
  const logs = load(KEYS.LOGS) || []
  logs.unshift({
    id: nextRecordId('LOG'),
    timestamp: nowIso(),
    action,
    entityType,
    entityId,
    description,
    metadata
  })
  save(KEYS.LOGS, logs.slice(0, MAX_ACTIVITY_LOGS))
}

function createAlert({
  code,
  severity,
  entityType,
  entityId,
  message,
  recipients,
  metadata = {}
}) {
  const alerts = load(KEYS.ALERTS) || []
  const existingActive = alerts.find(alert =>
    alert.status === 'active' &&
    alert.code === code &&
    alert.entityType === entityType &&
    alert.entityId === entityId
  )

  if (existingActive) return existingActive

  const alert = {
    id: nextRecordId('ALT'),
    createdAt: nowIso(),
    status: 'active',
    code,
    severity,
    entityType,
    entityId,
    message,
    recipients,
    metadata
  }

  alerts.unshift(alert)
  save(KEYS.ALERTS, alerts)

  const notifications = load(KEYS.NOTIFICATIONS) || []
  recipients.forEach(recipient => {
    notifications.unshift({
      id: nextRecordId('NTF'),
      createdAt: nowIso(),
      recipient,
      alertId: alert.id,
      message: `[${severity.toUpperCase()}] ${message}`,
      read: false
    })
  })
  save(KEYS.NOTIFICATIONS, notifications)

  createActivityLog({
    action: 'DISCREPANCY_ALERT_CREATED',
    entityType,
    entityId,
    description: message,
    metadata: { code, severity, recipients }
  })

  return alert
}

function resolveAlertByCode(entityType, entityId, code) {
  const alerts = load(KEYS.ALERTS) || []
  let changed = false

  const next = alerts.map(alert => {
    if (
      alert.status === 'active' &&
      alert.entityType === entityType &&
      alert.entityId === entityId &&
      alert.code === code
    ) {
      changed = true
      return { ...alert, status: 'resolved', resolvedAt: nowIso() }
    }
    return alert
  })

  if (changed) save(KEYS.ALERTS, next)
}

function syncDiscrepancyAlerts(entityType, entityId, issues, recipients) {
  const issueCodes = new Set(issues.map(issue => issue.code))

  issues.forEach(issue => {
    createAlert({
      code: issue.code,
      severity: issue.severity,
      entityType,
      entityId,
      message: issue.message,
      recipients,
      metadata: issue.metadata || {}
    })
  })

  const activeAlerts = (load(KEYS.ALERTS) || []).filter(alert =>
    alert.status === 'active' &&
    alert.entityType === entityType &&
    alert.entityId === entityId
  )

  activeAlerts.forEach(alert => {
    if (!issueCodes.has(alert.code)) {
      resolveAlertByCode(entityType, entityId, alert.code)
    }
  })
}

function getOrderDiscrepancies(order, productsById) {
  const issues = []
  const items = Array.isArray(order.items) ? order.items : []

  if (!items.length) {
    issues.push({
      code: 'ORDER_EMPTY_ITEMS',
      severity: 'high',
      message: `Order ${order.id} has no line items.`
    })
  }

  let hasInvalidItemData = false
  items.forEach((item, idx) => {
    const qty = Number(item.qty || 0)
    const price = Number(item.price || 0)

    if (qty <= 0 || price < 0) hasInvalidItemData = true

    const product = productsById[item.productId]
    if (product && Number(product.stock || 0) < qty) {
      issues.push({
        code: `ORDER_STOCK_MISMATCH_${item.productId}`,
        severity: 'medium',
        message: `Order ${order.id} requests ${qty} units of ${item.name || item.productId}, but stock is ${product.stock}.`,
        metadata: { itemIndex: idx, productId: item.productId, requested: qty, stock: product.stock }
      })
    }
  })

  if (hasInvalidItemData) {
    issues.push({
      code: 'ORDER_INVALID_ITEM_DATA',
      severity: 'high',
      message: `Order ${order.id} contains invalid quantity or price values.`
    })
  }

  const expectedTotal = calculateOrderExpectedTotal(order)
  const total = Number(order.total || 0)
  if (Math.abs(expectedTotal - total) > 0.01) {
    issues.push({
      code: 'ORDER_TOTAL_MISMATCH',
      severity: 'high',
      message: `Order ${order.id} total (${total}) does not match items total (${expectedTotal}).`,
      metadata: { expectedTotal, total }
    })
  }

  if (order.status === 'Delivered' && order.payment !== 'Paid') {
    issues.push({
      code: 'ORDER_DELIVERED_UNPAID',
      severity: 'medium',
      message: `Order ${order.id} is delivered but payment is not completed.`
    })
  }

  return issues
}

function getInventoryDiscrepancies(product) {
  const issues = []
  const stock = Number(product.stock || 0)

  if (stock < 0) {
    issues.push({
      code: 'INVENTORY_NEGATIVE_STOCK',
      severity: 'high',
      message: `Product ${product.name} has negative stock (${stock}).`
    })
  }

  if (product.price != null && Number(product.price) < 0) {
    issues.push({
      code: 'INVENTORY_NEGATIVE_PRICE',
      severity: 'high',
      message: `Product ${product.name} has a negative price.`
    })
  }

  return issues
}

function runDiscrepancyChecksForProduct(product) {
  const issues = getInventoryDiscrepancies(product)
  syncDiscrepancyAlerts('product', product.id, issues, ['warehouse_manager'])
}

function runDiscrepancyChecksForOrder(order) {
  const productsById = getProducts().reduce((acc, product) => {
    acc[product.id] = product
    return acc
  }, {})

  const issues = getOrderDiscrepancies(order, productsById)
  syncDiscrepancyAlerts('order', order.id, issues, ['warehouse_manager', 'order_fulfillment_specialist'])
}

function runGlobalDiscrepancyChecks() {
  getProducts().forEach(runDiscrepancyChecksForProduct)
  getOrders().forEach(runDiscrepancyChecksForOrder)
}

// ─── Initialize ───────────────────────────────────────────
export function initStore() {
  if (!localStorage.getItem(KEYS.INITIALIZED)) {
    save(KEYS.PRODUCTS, SEED_PRODUCTS)
    save(KEYS.ORDERS, SEED_ORDERS.map(order => applyOrderCompletionState(order)))
    save(KEYS.LOGS, [])
    save(KEYS.ALERTS, [])
    save(KEYS.NOTIFICATIONS, [])
    save(KEYS.SAMPLE_DISTRIBUTIONS, [])
    save(KEYS.PHYSICAL_STOCKS, [])
    save(KEYS.STOCK_ADJUSTMENTS, [])
    localStorage.setItem(KEYS.INITIALIZED, 'true')
  } else {
    ensureArrayKey(KEYS.LOGS)
    ensureArrayKey(KEYS.ALERTS)
    ensureArrayKey(KEYS.NOTIFICATIONS)
    ensureArrayKey(KEYS.SAMPLE_DISTRIBUTIONS)
    ensureArrayKey(KEYS.PHYSICAL_STOCKS)
    ensureArrayKey(KEYS.STOCK_ADJUSTMENTS)
  }

  runGlobalDiscrepancyChecks()
}

// ─── Products ─────────────────────────────────────────────
export function getProducts() {
  return load(KEYS.PRODUCTS) || []
}

export function addProduct(product) {
  const products = getProducts()
  product.id = nextId('P', products)
  products.push(product)
  save(KEYS.PRODUCTS, products)
  createActivityLog({
    action: 'STOCK_UPDATED',
    entityType: 'product',
    entityId: product.id,
    description: `Product ${product.name} created with stock ${product.stock}.`,
    metadata: { stock: product.stock, sku: product.sku }
  })
  runDiscrepancyChecksForProduct(product)
  return product
}

export function updateProduct(id, updates) {
  const products = getProducts()
  const idx = products.findIndex(p => p.id === id)
  if (idx !== -1) {
    const previous = products[idx]
    products[idx] = { ...products[idx], ...updates }
    save(KEYS.PRODUCTS, products)

    if (Object.prototype.hasOwnProperty.call(updates, 'stock') && Number(previous.stock) !== Number(products[idx].stock)) {
      createActivityLog({
        action: 'STOCK_UPDATED',
        entityType: 'product',
        entityId: id,
        description: `Stock updated for ${products[idx].name}: ${previous.stock} → ${products[idx].stock}.`,
        metadata: { previousStock: previous.stock, updatedStock: products[idx].stock }
      })
    }

    runDiscrepancyChecksForProduct(products[idx])
    return products[idx]
  }
  return null
}

export function deleteProduct(id) {
  const products = getProducts().filter(p => p.id !== id)
  save(KEYS.PRODUCTS, products)
}

// ─── Orders ───────────────────────────────────────────────
export function getOrders() {
  const orders = load(KEYS.ORDERS) || []
  return orders.map(order => applyOrderCompletionState(order, order))
}

export function addOrder(order) {
  const orders = getOrders()
  order.id = nextId('ORD-', orders)
  order.date = order.date || new Date().toISOString().split('T')[0]
  const finalizedOrder = applyOrderCompletionState(order)
  orders.unshift(finalizedOrder)
  save(KEYS.ORDERS, orders)

  createActivityLog({
    action: 'ORDER_CREATED',
    entityType: 'order',
    entityId: finalizedOrder.id,
    description: `Order ${finalizedOrder.id} created for ${finalizedOrder.customer}.`,
    metadata: { total: finalizedOrder.total, status: finalizedOrder.status, payment: finalizedOrder.payment }
  })

  runDiscrepancyChecksForOrder(finalizedOrder)
  return finalizedOrder
}

export function updateOrder(id, updates) {
  const orders = getOrders()
  const idx = orders.findIndex(o => o.id === id)
  if (idx !== -1) {
    const previous = { ...orders[idx] }
    const merged = { ...orders[idx], ...updates }
    orders[idx] = applyOrderCompletionState(merged, previous)
    save(KEYS.ORDERS, orders)

    if (Object.prototype.hasOwnProperty.call(updates, 'status') && previous.status !== orders[idx].status) {
      createActivityLog({
        action: orders[idx].status === 'Delivered' ? 'DELIVERY_CONFIRMED' : 'ORDER_STATUS_UPDATED',
        entityType: 'order',
        entityId: id,
        description: `Order ${id} status changed: ${previous.status} → ${orders[idx].status}.`,
        metadata: { previousStatus: previous.status, updatedStatus: orders[idx].status }
      })
    }

    if (Object.prototype.hasOwnProperty.call(updates, 'payment') && previous.payment !== orders[idx].payment) {
      createActivityLog({
        action: 'PAYMENT_UPDATED',
        entityType: 'order',
        entityId: id,
        description: `Order ${id} payment changed: ${previous.payment} → ${orders[idx].payment}.`,
        metadata: { previousPayment: previous.payment, updatedPayment: orders[idx].payment }
      })
    }

    if (!previous.isFinalized && orders[idx].isFinalized) {
      createActivityLog({
        action: 'ORDER_FINALIZED',
        entityType: 'order',
        entityId: id,
        description: `Order ${id} finalized after payment and delivery verification.`,
        metadata: { finalizedAt: orders[idx].finalizedAt }
      })
    }

    runDiscrepancyChecksForOrder(orders[idx])
    return orders[idx]
  }
  return null
}

export function verifyOrderCompletion(orderId) {
  const order = getOrders().find(o => o.id === orderId)
  if (!order) return null

  const completion = evaluateOrderCompletion(order)
  return {
    orderId,
    deliveryConfirmed: completion.deliveryConfirmed,
    paymentCompleted: completion.paymentCompleted,
    canFinalize: completion.canFinalize,
    finalizedAt: completion.canFinalize ? (order.finalizedAt || nowIso()) : null
  }
}

export function getActivityLogs() {
  return load(KEYS.LOGS) || []
}

export function getAlerts() {
  return load(KEYS.ALERTS) || []
}

export function getActiveAlerts() {
  return getAlerts().filter(alert => alert.status === 'active')
}

export function resolveAlert(alertId) {
  const alerts = getAlerts()
  const idx = alerts.findIndex(alert => alert.id === alertId)
  if (idx === -1) return null
  if (alerts[idx].status === 'resolved') return alerts[idx]

  alerts[idx] = { ...alerts[idx], status: 'resolved', resolvedAt: nowIso() }
  save(KEYS.ALERTS, alerts)

  createActivityLog({
    action: 'DISCREPANCY_ALERT_RESOLVED',
    entityType: alerts[idx].entityType,
    entityId: alerts[idx].entityId,
    description: `Alert resolved: ${alerts[idx].message}`,
    metadata: { alertId: alerts[idx].id, code: alerts[idx].code }
  })

  return alerts[idx]
}

export function getNotifications() {
  return load(KEYS.NOTIFICATIONS) || []
}

export function getNotificationsForRecipient(recipient) {
  return getNotifications().filter(item => item.recipient === recipient)
}

// ─── SCRUM-25: Stock Validation ────────────────────────────
export function validateOrderStock(items) {
  const products = getProducts()
  const productsById = products.reduce((acc, p) => {
    acc[p.id] = p
    return acc
  }, {})

  const issues = []
  items.forEach((item, idx) => {
    const product = productsById[item.productId]
    const qty = Number(item.qty || 0)

    if (!product) {
      issues.push({
        itemIndex: idx,
        productId: item.productId,
        message: `Product ${item.productId} not found.`
      })
      return
    }

    const availableStock = Number(product.stock || 0)
    if (qty > availableStock) {
      issues.push({
        itemIndex: idx,
        productId: item.productId,
        productName: product.name,
        requestedQty: qty,
        availableStock,
        message: `Insufficient stock for ${product.name}. Requested: ${qty}, Available: ${availableStock}`
      })
    }
  })

  return {
    isValid: issues.length === 0,
    issues
  }
}

// ─── SCRUM-22: Stock Adjustment Logic ──────────────────────
export function adjustStock(productId, adjustmentQty, reason = 'manual') {
  const products = getProducts()
  const idx = products.findIndex(p => p.id === productId)
  if (idx === -1) return null

  const previous = { ...products[idx] }
  const previousStock = Number(previous.stock || 0)
  const newStock = Math.max(0, previousStock + adjustmentQty)

  products[idx] = {
    ...products[idx],
    stock: newStock
  }
  save(KEYS.PRODUCTS, products)

  const adjustments = load(KEYS.STOCK_ADJUSTMENTS) || []
  const adjustment = {
    id: nextRecordId('ADJ'),
    productId,
    productName: products[idx].name,
    previousStock,
    adjustmentQty,
    newStock,
    reason,
    timestamp: nowIso()
  }
  adjustments.unshift(adjustment)
  save(KEYS.STOCK_ADJUSTMENTS, adjustments)

  createActivityLog({
    action: 'STOCK_ADJUSTED',
    entityType: 'product',
    entityId: productId,
    description: `Stock adjusted for ${products[idx].name}: ${previousStock} → ${newStock} (${reason})`,
    metadata: {
      previousStock,
      adjustmentQty,
      newStock,
      reason,
      adjustmentId: adjustment.id
    }
  })

  runDiscrepancyChecksForProduct(products[idx])
  return adjustment
}

// ─── SCRUM-22: Dispatch Order (Auto-deduct inventory) ──────
export function dispatchOrder(orderId) {
  const order = getOrders().find(o => o.id === orderId)
  if (!order) return null

  const items = Array.isArray(order.items) ? order.items : []
  items.forEach(item => {
    adjustStock(item.productId, -Number(item.qty || 0), `order_dispatch_${orderId}`)
  })

  const updated = updateOrder(orderId, { status: 'Shipped' })
  createActivityLog({
    action: 'ORDER_DISPATCHED',
    entityType: 'order',
    entityId: orderId,
    description: `Order ${orderId} dispatched. Inventory reduced for ${items.length} product(s).`,
    metadata: { itemCount: items.length }
  })

  return updated
}

// ─── SCRUM-22: Cancel Order (Restore inventory) ────────────
export function cancelOrder(orderId) {
  const order = getOrders().find(o => o.id === orderId)
  if (!order) return null

  const items = Array.isArray(order.items) ? order.items : []
  items.forEach(item => {
    adjustStock(item.productId, Number(item.qty || 0), `order_cancellation_${orderId}`)
  })

  const updated = updateOrder(orderId, { status: 'Cancelled' })
  createActivityLog({
    action: 'ORDER_CANCELLED',
    entityType: 'order',
    entityId: orderId,
    description: `Order ${orderId} cancelled. Inventory restored for ${items.length} product(s).`,
    metadata: { itemCount: items.length }
  })

  return updated
}

// ─── SCRUM-23: Sample Distribution Recording ───────────────
export function recordSampleDistribution(productId, quantity, recipientType = 'unknown') {
  const product = getProducts().find(p => p.id === productId)
  if (!product) return null

  const distribution = {
    id: nextRecordId('SAMP'),
    productId,
    productName: product.name,
    quantity,
    recipientType,
    recordedAt: nowIso()
  }

  const distributions = load(KEYS.SAMPLE_DISTRIBUTIONS) || []
  distributions.unshift(distribution)
  save(KEYS.SAMPLE_DISTRIBUTIONS, distributions)

  adjustStock(productId, -quantity, `sample_distribution_${recipientType}`)

  createActivityLog({
    action: 'SAMPLE_DISTRIBUTION_RECORDED',
    entityType: 'product',
    entityId: productId,
    description: `Sample distribution recorded: ${quantity} units of ${product.name} given to ${recipientType}.`,
    metadata: { quantity, recipientType, distributionId: distribution.id }
  })

  return distribution
}

export function getSampleDistributions() {
  return load(KEYS.SAMPLE_DISTRIBUTIONS) || []
}

// ─── SCRUM-26: Physical Stock Recording & Mismatch Detection ─
export function recordPhysicalStock(productId, physicalCount) {
  const product = getProducts().find(p => p.id === productId)
  if (!product) return null

  const recordedStock = Number(product.stock || 0)
  const physical = Number(physicalCount || 0)
  const variance = physical - recordedStock

  const record = {
    id: nextRecordId('PSC'),
    productId,
    productName: product.name,
    recordedStock,
    physicalCount: physical,
    variance,
    recordedAt: nowIso()
  }

  const records = load(KEYS.PHYSICAL_STOCKS) || []
  records.unshift(record)
  save(KEYS.PHYSICAL_STOCKS, records)

  createActivityLog({
    action: 'PHYSICAL_STOCK_RECORDED',
    entityType: 'product',
    entityId: productId,
    description: `Physical count for ${product.name}: ${physical} units (system: ${recordedStock}, variance: ${variance > 0 ? '+' : ''}${variance})`,
    metadata: { recordedStock, physicalCount: physical, variance }
  })

  if (variance !== 0) {
    createAlert({
      code: `STOCK_MISMATCH_${productId}`,
      severity: Math.abs(variance) > 10 ? 'high' : 'medium',
      entityType: 'product',
      entityId: productId,
      message: `Stock mismatch for ${product.name}: system shows ${recordedStock}, physical count is ${physical} (${variance > 0 ? '+' : ''}${variance})`,
      recipients: ['warehouse_manager'],
      metadata: { variance, record: record.id }
    })
  }

  return record
}

export function getPhysicalStockRecords() {
  return load(KEYS.PHYSICAL_STOCKS) || []
}

export function getStockMismatches() {
  const records = getPhysicalStockRecords()
  return records.filter(r => r.variance !== 0)
}

export function getStockAdjustments() {
  return load(KEYS.STOCK_ADJUSTMENTS) || []
}

// ─── SCRUM-32: Pending Payments Query ──────────────────────
export function getPendingPaymentOrders() {
  return getOrders().filter(order => order.payment === 'Unpaid')
}

export function getPendingPaymentStats() {
  const pending = getPendingPaymentOrders()
  return {
    count: pending.length,
    totalAmount: pending.reduce((sum, o) => sum + (Number(o.total) || 0), 0),
    orders: pending
  }
}

// ─── Utility: Reset Store (for dev/testing) ───────────────
export function resetStore() {
  localStorage.removeItem(KEYS.INITIALIZED)
  localStorage.removeItem(KEYS.PRODUCTS)
  localStorage.removeItem(KEYS.ORDERS)
  localStorage.removeItem(KEYS.LOGS)
  localStorage.removeItem(KEYS.ALERTS)
  localStorage.removeItem(KEYS.NOTIFICATIONS)
  localStorage.removeItem(KEYS.SAMPLE_DISTRIBUTIONS)
  localStorage.removeItem(KEYS.PHYSICAL_STOCKS)
  localStorage.removeItem(KEYS.STOCK_ADJUSTMENTS)
  initStore()
}

export default {
  initStore,
  getProducts, addProduct, updateProduct, deleteProduct,
  getOrders, addOrder, updateOrder,
  verifyOrderCompletion,
  validateOrderStock,
  adjustStock,
  dispatchOrder,
  cancelOrder,
  recordSampleDistribution,
  getSampleDistributions,
  recordPhysicalStock,
  getPhysicalStockRecords,
  getStockMismatches,
  getStockAdjustments,
  getPendingPaymentOrders,
  getPendingPaymentStats,
  getActivityLogs,
  getAlerts,
  getActiveAlerts,
  resolveAlert,
  getNotifications,
  getNotificationsForRecipient,
  resetStore
}
