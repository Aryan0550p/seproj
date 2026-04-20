/**
 * Shared Data Store – localStorage-backed persistence layer
 * Connects Admin, Salesman & Retailer through unified data.
 */
import { reactive } from 'vue'

const KEYS = {
  PRODUCTS: 'yumsie_products',
  ORDERS: 'yumsie_orders',
  INITIALIZED: 'yumsie_store_init'
}

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

function nextId(prefix, list) {
  const nums = list.map(item => {
    const match = item.id.match(/(\d+)$/)
    return match ? parseInt(match[1]) : 0
  })
  const max = nums.length ? Math.max(...nums) : 0
  return `${prefix}${String(max + 1).padStart(4, '0')}`
}

// ─── Initialize ───────────────────────────────────────────
export function initStore() {
  if (!localStorage.getItem(KEYS.INITIALIZED)) {
    save(KEYS.PRODUCTS, SEED_PRODUCTS)
    save(KEYS.ORDERS, SEED_ORDERS)
    localStorage.setItem(KEYS.INITIALIZED, 'true')
  }
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
  return product
}

export function updateProduct(id, updates) {
  const products = getProducts()
  const idx = products.findIndex(p => p.id === id)
  if (idx !== -1) {
    products[idx] = { ...products[idx], ...updates }
    save(KEYS.PRODUCTS, products)
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
  return load(KEYS.ORDERS) || []
}

export function addOrder(order) {
  const orders = getOrders()
  order.id = nextId('ORD-', orders)
  order.date = order.date || new Date().toISOString().split('T')[0]
  orders.unshift(order)
  save(KEYS.ORDERS, orders)
  return order
}

export function updateOrder(id, updates) {
  const orders = getOrders()
  const idx = orders.findIndex(o => o.id === id)
  if (idx !== -1) {
    orders[idx] = { ...orders[idx], ...updates }
    save(KEYS.ORDERS, orders)
    return orders[idx]
  }
  return null
}

// ─── Utility: Reset Store (for dev/testing) ───────────────
export function resetStore() {
  localStorage.removeItem(KEYS.INITIALIZED)
  localStorage.removeItem(KEYS.PRODUCTS)
  localStorage.removeItem(KEYS.ORDERS)
  initStore()
}

export default {
  initStore,
  getProducts, addProduct, updateProduct, deleteProduct,
  getOrders, addOrder, updateOrder,
  resetStore
}
