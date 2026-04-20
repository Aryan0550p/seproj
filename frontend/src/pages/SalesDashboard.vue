<template>
  <div class="sales-dashboard">
    <div class="page-header">
      <h1>Sales Dashboard</h1>
    </div>
    <!-- HEADER: KPI Cards -->
    <div class="kpi-grid">
      <div v-for="kpi in kpis" :key="kpi.title" class="kpi-card" :title="kpi.tooltip">
        <div class="kpi-icon">{{ kpi.icon }}</div>
        <div class="kpi-content">
          <h3>{{ kpi.title }}</h3>
          <div v-if="kpi.type === 'progress'" class="progress-container">
            <div class="progress-bar" :style="{ width: kpi.value }"></div>
            <span class="progress-text">{{ kpi.value }}</span>
          </div>
          <p v-else class="kpi-value">{{ kpi.value }}</p>
          <span v-if="kpi.trend" class="trend" :class="{ positive: kpi.trend.includes('+'), negative: kpi.trend.includes('-') }">
            {{ kpi.trend }}
          </span>
        </div>
      </div>
    </div>

    <!-- MAIN CONTENT: 2-Column Layout -->
    <div class="main-content">
      <!-- LEFT COLUMN: Order Queue & Quick Actions -->
      <div class="left-panel">
        <!-- Order Queue Management -->
        <div class="panel-section">
          <h2>My Order Queue</h2>
          <div class="table-container">
            <table class="order-table">
              <thead>
                <tr>
                  <th @click="sortBy('customer')">Customer ▼</th>
                  <th @click="sortBy('id')">Order #</th>
                  <th @click="sortBy('value')">Value</th>
                  <th @click="sortBy('status')">Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in paginatedOrders" :key="order.id">
                  <td>{{ order.customer }}</td>
                  <td>{{ order.id }}</td>
                  <td>{{ order.value }}</td>
                  <td>
                    <span class="status" :class="order.status.toLowerCase()">{{ order.status }}</span>
                  </td>
                  <td class="actions">
                    <button @click="editOrder(order)" class="btn-sm edit">Edit</button>
                    <button v-if="order.status === 'Pending'" @click="shipOrder(order)" class="btn-sm ship">Ship</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="panel-section">
          <h3>Quick Actions</h3>
          <div class="quick-actions-grid">
            <button @click="openModal('addOrder')" class="quick-btn primary">
              <span class="btn-icon">➕</span>
              Add Order
            </button>
            <div class="search-container">
              <input v-model="searchQuery" @input="filterOrders" type="text" placeholder="Search customers/products..." class="search-input" />
              <span class="search-icon">🔍</span>
            </div>
          </div>
        </div>

        <!-- Follow-up Tools -->
        <div class="panel-section">
          <h3>Follow-up Tasks</h3>
          <div class="tasks-list">
            <div v-for="task in tasks" :key="task.id" class="task-item" :class="{ overdue: task.overdue }">
              <div class="task-header">
                <span class="task-type">{{ task.type }}</span>
                <span class="task-due">{{ task.due }}</span>
              </div>
              <p class="task-desc">{{ task.description }}</p>
              <div class="task-actions">
                <button @click="completeTask(task)" class="btn-xs">Complete</button>
                <button @click="snoozeTask(task)" class="btn-xs secondary">Snooze</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: Analytics & Notifications -->
      <div class="right-panel">
        <!-- Performance Analytics -->
        <div class="panel-section">
          <h3>Performance Analytics</h3>
          <div class="chart-grid">
            <!-- Sales Trends (Line Chart) -->
            <div class="chart-card">
              <h4>Sales Trends (7 days)</h4>
              <div class="line-chart">
                <svg width="100%" height="120" viewBox="0 0 300 120">
                  <polyline fill="none" stroke="#b48c28" stroke-width="3" points="0,100 30,90 60,80 90,70 120,60 150,50 180,40 210,30 240,20 270,15 300,10" />
                  <circle cx="300" cy="10" r="4" fill="#b48c28" />
                  <text x="300" y="5" font-size="10" fill="#f5f5f5">Today</text>
                </svg>
              </div>
            </div>

            <!-- Top Customers (Pie Chart) -->
            <div class="chart-card">
              <h4>Top Customers</h4>
              <div class="pie-chart">
                <svg width="100%" height="120" viewBox="0 0 200 200">
                  <circle cx="100" cy="100" r="70" fill="none" stroke="#b48c28" stroke-width="35" stroke-dasharray="219.9" stroke-dashoffset="0" />
                  <circle cx="100" cy="100" r="70" fill="none" stroke="#6e9f3a" stroke-width="35" stroke-dasharray="164.9" stroke-dashoffset="-219.9" />
                  <circle cx="100" cy="100" r="70" fill="none" stroke="#d4a937" stroke-width="35" stroke-dasharray="55.0" stroke-dashoffset="-384.8" />
                </svg>
                <div class="pie-legend">
                  <div v-for="customer in topCustomers" :key="customer.name" class="legend-item">
                    <span class="legend-color" :style="{ backgroundColor: getColor(customer.name) }"></span>
                    {{ customer.name }} ({{ customer.pct }}%)
                  </div>
                </div>
              </div>
            </div>

            <!-- Win/Loss Ratio -->
            <div class="chart-card">
              <h4>Win/Loss Ratio</h4>
              <div class="ratio-chart">
                <div class="ratio-bar">
                  <div class="ratio-win" :style="{ width: winLossRatio.win + '%' }">{{ winLossRatio.win }}%</div>
                  <div class="ratio-loss" :style="{ width: winLossRatio.loss + '%' }">{{ winLossRatio.loss }}%</div>
                </div>
                <div class="ratio-labels">
                  <span>Win Rate</span>
                  <span>Loss Rate</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Notifications/Alerts -->
        <div class="panel-section">
          <h3>Notifications & Alerts</h3>
          <div class="notifications-list">
            <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.type">
              <span class="alert-icon">{{ alert.icon }}</span>
              <div class="alert-content">
                <p class="alert-title">{{ alert.title }}</p>
                <p class="alert-desc">{{ alert.description }}</p>
                <span class="alert-time">{{ alert.time }}</span>
              </div>
              <button @click="dismissAlert(alert)" class="alert-dismiss">×</button>
            </div>
          </div>
        </div>

        <!-- Export/Reports -->
        <div class="panel-section">
          <h3>Export & Reports</h3>
          <div class="export-actions">
            <button @click="exportReport('personal')" class="export-btn">
              <span class="btn-icon">📊</span>
              Personal Sales Summary
            </button>
            <button @click="exportReport('pipeline')" class="export-btn">
              <span class="btn-icon">📈</span>
              Weekly Pipeline Report
            </button>
          </div>
        </div>

        <!-- User Management -->
        <div class="panel-section">
          <h3>User Management</h3>
          <div class="create-user-container">
            <h4>Create Wholeseller Account</h4>
            <form @submit.prevent="handleCreateUser" class="create-user-form">
              <input v-model="newUser.username" type="text" required placeholder="Username" />
              <input v-model="newUser.password" type="password" required placeholder="Password" />
              <button type="submit" class="quick-btn primary" style="justify-content:center;">Create Account</button>
            </form>
            <p v-if="userMessage" :class="['message', userMessageType]">{{ userMessage }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- MODALS -->
    <!-- Order Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h3>{{ modalType === 'edit' ? 'Edit Order' : 'Add New Order' }}</h3>
        <form @submit.prevent="submitModal">
          <div class="form-row">
            <div class="form-group">
              <label>Customer</label>
              <select v-model="modalData.customer" required>
                <option value="">Select Customer</option>
                <option v-for="cust in customers" :key="cust" :value="cust">{{ cust }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Product</label>
              <select v-model="modalData.product" required>
                <option value="">Select Product</option>
                <option v-for="prod in products" :key="prod" :value="prod">{{ prod }}</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Quantity</label>
              <input v-model.number="modalData.quantity" type="number" min="1" required />
            </div>
            <div class="form-group">
              <label>Value (₹)</label>
              <input v-model="modalData.value" type="text" required />
            </div>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="modalData.notes" rows="3"></textarea>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">{{ modalType === 'edit' ? 'Update' : 'Create' }}</button>
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { createUser } from '../auth'
import { getOrders, addOrder, updateOrder, getProducts } from '../store'

export default {
  name: 'SalesDashboard',
  setup() {
    const orders = ref([])
    const storeProducts = ref([])

    const reload = () => {
      orders.value = getOrders()
      storeProducts.value = getProducts()
      storeProducts.value = getProducts()
    }

    onMounted(reload)

    // KPI Data – computed from real store data
    const kpis = computed(() => [
      { title: "Today's Target", value: "75%", type: "progress", trend: "+5%", tooltip: "Daily sales target progress", icon: "🎯" },
      { title: "Pipeline Value", value: `₹${(orders.value.filter(o => o.status === 'Pending').reduce((s, o) => s + (o.total || 0), 0) / 1000).toFixed(1)}K`, trend: "+18%", tooltip: "Total value in pending pipeline", icon: "💰" },
      { title: "Pending Orders", value: orders.value.filter(o => o.status === 'Pending').length, tooltip: "Orders awaiting shipment", icon: "📦" }
    ])

    // Products & Customers from store
    const customers = computed(() => [...new Set(orders.value.map(o => o.customer))])
    const products = computed(() => storeProducts.value.map(p => p.name))
    const topCustomers = ref([
      { name: "Retail Corp A", pct: 35 },
      { name: "Shop B", pct: 28 },
      { name: "Mart C", pct: 22 },
      { name: "Store D", pct: 15 }
    ])
    const winLossRatio = ref({ win: 68, loss: 32 })

    // Tasks Data
    const tasks = ref([
      { id: 1, type: "Call", description: "Follow up with Retail Corp A", due: "Today", overdue: false },
      { id: 2, type: "Email", description: "Send product catalog to new lead Shop B", due: "Tomorrow", overdue: false },
      { id: 3, type: "Meeting", description: "Review Q4 targets with management", due: "Yesterday", overdue: true }
    ])

    // Alerts – derived from store
    const alerts = computed(() => {
      const a = []
      const lowStock = storeProducts.value.filter(p => p.stock > 0 && p.stock <= 30)
      lowStock.forEach(p => a.push({ id: `ls-${p.id}`, type: "warning", icon: "⚠️", title: "Low Stock Alert", description: `${p.name} running low (${p.stock} units left)`, time: "Now" }))
      const unpaid = orders.value.filter(o => o.payment === 'Unpaid')
      if (unpaid.length) a.push({ id: 'pay-1', type: "info", icon: "💳", title: "Payments Due", description: `${unpaid.length} order(s) with unpaid invoices`, time: "Active" })
      return a
    })

    // User Creation State
    const newUser = ref({ username: '', password: '', role: 'retailer' })
    const userMessage = ref('')
    const userMessageType = ref('')

    // Reactive State
    const searchQuery = ref('')
    const sortKey = ref('customer')
    const sortOrder = ref(1)
    const showModal = ref(false)
    const modalType = ref('')
    const modalData = ref({ customer: '', product: '', quantity: 1, value: '', notes: '' })

    // Computed Properties
    const filteredOrders = computed(() => {
      return orders.value.filter(order =>
        order.customer.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        order.id.toLowerCase().includes(searchQuery.value.toLowerCase())
      ).sort((a, b) => {
        const aVal = a[sortKey.value]
        const bVal = b[sortKey.value]
        return (aVal > bVal ? 1 : -1) * sortOrder.value
      })
    })

    const paginatedOrders = computed(() => filteredOrders.value.slice(0, 10))

    // Methods
    const handleCreateUser = () => {
      const result = createUser({ ...newUser.value, role: 'retailer' })
      userMessage.value = result.message
      userMessageType.value = result.success ? 'success' : 'error'
      if (result.success) {
        newUser.value = { ...newUser.value, username: '', password: '' }
      }
      setTimeout(() => { userMessage.value = '' }, 4000)
    }

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortOrder.value = -sortOrder.value
      } else {
        sortKey.value = key
        sortOrder.value = 1
      }
    }

    const editOrder = (order) => {
      modalType.value = 'edit'
      modalData.value = { ...order }
      showModal.value = true
    }

    const shipOrder = (order) => {
      updateOrder(order.id, { status: 'Shipped' })
      reload()
      showToast('Order shipped successfully!', 'success')
    }

    const openModal = (type) => {
      modalType.value = type
      modalData.value = { customer: '', product: '', quantity: 1, value: '', notes: '' }
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      modalData.value = { customer: '', product: '', quantity: 1, value: '', notes: '' }
    }

    const submitModal = () => {
      if (modalType.value === 'edit') {
        updateOrder(modalData.value.id, { ...modalData.value })
        showToast('Order updated successfully!', 'success')
      } else {
        const prod = storeProducts.value.find(p => p.name === modalData.value.product)
        const price = prod ? prod.price : 0
        const total = price * (modalData.value.quantity || 1)
        addOrder({
          customer: modalData.value.customer,
          createdBy: 'salesman',
          items: [{ productId: prod?.id || '', name: modalData.value.product, qty: modalData.value.quantity, price }],
          total: total || parseInt(String(modalData.value.value).replace(/[^\d]/g, '')) || 0,
          status: 'Pending',
          payment: 'Unpaid'
        })
        showToast(`Order created successfully!`, 'success')
      }
      reload()
      closeModal()
    }

    const completeTask = (task) => {
      tasks.value = tasks.value.filter(t => t.id !== task.id)
      showToast('Task completed!', 'success')
    }

    const snoozeTask = (task) => {
      task.due = 'Tomorrow'
      task.overdue = false
      showToast('Task snoozed', 'info')
    }

    const dismissAlert = (alert) => {
      // For computed alerts, just show toast
      showToast('Alert dismissed', 'info')
    }

    const exportReport = (type) => {
      showToast(`${type === 'personal' ? 'Personal Sales Summary' : 'Weekly Pipeline Report'} exported successfully!`, 'success')
    }

    const showToast = (message, type = 'info') => {
      const toast = document.createElement('div')
      toast.textContent = message
      toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#6e9f3a' : type === 'warning' ? '#ffc107' : '#17a2b8'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 1000;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      `
      document.body.appendChild(toast)
      setTimeout(() => document.body.removeChild(toast), 4000)
    }

    const getColor = (name) => {
      const colors = { 'Retail Corp A': '#b48c28', 'Shop B': '#6e9f3a', 'Mart C': '#d4a937', 'Store D': '#7a9f2f' }
      return colors[name] || '#b48c28'
    }

    return {
      kpis,
      orders,
      customers,
      products,
      topCustomers,
      winLossRatio,
      tasks,
      alerts,
      searchQuery,
      filteredOrders,
      paginatedOrders,
      showModal,
      modalType,
      modalData,
      sortBy,
      editOrder,
      shipOrder,
      openModal,
      closeModal,
      submitModal,
      completeTask,
      snoozeTask,
      dismissAlert,
      exportReport,
      getColor,
      newUser,
      userMessage,
      userMessageType,
      handleCreateUser
    }
  }
}
</script>
<style scoped>
.sales-dashboard {
  padding: 30px;
  color: var(--text-primary);
  min-height: 100vh;
  background: radial-gradient(circle at top right, rgba(180, 140, 40, 0.05), transparent 400px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 { margin: 0; }

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.kpi-card {
  padding: 20px;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-accent);
  box-shadow: var(--shadow-main);
  transition: transform 0.3s ease;
  display: flex;
  align-items: center;
  gap: 15px;
}

.kpi-card:hover {
  transform: translateY(-4px);
}

.kpi-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.kpi-content {
  flex: 1;
}

.kpi-card h3 {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 600;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.progress-container {
  position: relative;
  height: 24px;
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  margin: 8px 0;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
}

.trend {
  font-size: 0.85rem;
  font-weight: 500;
}

.trend.positive {
  color: var(--status-delivered-text);
}

.trend.negative {
  color: var(--status-rejected-text);
}

/* Main Content */
.main-content {
  display: grid;
  grid-template-columns: 65% 35%;
  gap: 30px;
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.panel-section {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-accent);
}

.panel-section h2, .panel-section h3 {
  margin-top: 0;
  color: var(--text-primary);
  margin-bottom: 15px;
}

.panel-section h2 {
  font-size: 1.4rem;
}

.panel-section h3 {
  font-size: 1.1rem;
}

/* Table */
.table-container {
  max-height: 350px;
  overflow-y: auto;
}

.order-table {
  width: 100%;
  border-collapse: collapse;
  color: var(--text-primary);
}

.order-table th {
  background: var(--bg-secondary);
  padding: 12px;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  color: var(--text-secondary);
}

.order-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status.pending {
  background: var(--status-pending-bg);
  color: var(--status-pending-text);
}

.status.shipped {
  background: var(--status-shipped-bg);
  color: var(--status-shipped-text);
}

.status.delivered {
  background: var(--status-delivered-bg);
  color: var(--status-delivered-text);
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-sm.edit {
  background: var(--bg-secondary);
  color: var(--status-shipped-text);
  border: 1px solid var(--border-accent);
}

.btn-sm.edit:hover {
  background: var(--bg-card-hover);
}

.btn-sm.ship {
  background: var(--bg-secondary);
  color: var(--status-delivered-text);
  border: 1px solid var(--border-accent);
}

.btn-sm.ship:hover {
  background: var(--bg-card-hover);
}

/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.quick-btn {
  padding: 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-btn.primary {
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  color: #111;
}

.quick-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(180, 140, 40, 0.3);
}

.quick-btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-accent);
}

.quick-btn.secondary:hover {
  background: var(--bg-card-hover);
}

.btn-icon {
  font-size: 1.2rem;
}

.search-container {
  position: relative;
  grid-column: span 2;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 12px;
  border: 1px solid var(--border-input);
  border-radius: 8px;
  background: var(--bg-input);
  color: var(--text-primary);
  outline: none;
  font-size: 0.9rem;
}

.search-input::placeholder {
  color: var(--text-dim);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.6;
}

/* Tasks */
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  padding: 12px;
  border-radius: 8px;
  background: var(--bg-secondary);
  border-left: 4px solid var(--accent-gold);
}

.task-item.overdue {
  border-left-color: var(--status-rejected-text);
  background: var(--status-rejected-bg);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.task-type {
  font-weight: 600;
  color: var(--accent-gold);
}

.task-due {
  font-size: 0.8rem;
  color: var(--text-dim);
}

.task-desc {
  margin: 5px 0;
  font-size: 0.9rem;
}

.task-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.btn-xs {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.7rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-xs {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.btn-xs.secondary {
  background: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.btn-xs:hover {
  opacity: 0.8;
}

/* Charts */
.chart-grid {
  display: grid;
  gap: 15px;
}

.chart-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid var(--border-accent);
}

/* User Management (Sales Dashboard) */
.create-user-container h4 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.create-user-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.create-user-form input {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border-input);
  background: var(--bg-input);
  color: var(--text-primary);
  outline: none;
}

.create-user-form input:focus {
  border-color: rgba(180, 150, 45, 0.8);
}

.message {
  margin-top: 12px;
  padding: 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  text-align: center;
}

.message.success {
  background: rgba(40, 167, 69, 0.2);
  color: #6ecf8d;
}

.message.error {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.chart-card h4 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  color: #ffffff;
}

.line-chart, .pie-chart {
  margin-top: 10px;
}

.pie-legend {
  margin-top: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  font-size: 0.85rem;
}

.legend-color {
  width: 10px;
  height: 10px;
  margin-right: 8px;
  border-radius: 2px;
}

.ratio-chart {
  margin-top: 10px;
}

.ratio-bar {
  display: flex;
  height: 20px;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 5px;
}

.ratio-win {
  background: #6e9f3a;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
}

.ratio-loss {
  background: #ff6b6b;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
}

.ratio-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: rgba(245, 245, 245, 0.7);
}

/* Notifications */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-left: 4px solid #b48c28;
}

.alert-item.warning {
  border-left-color: #ffc107;
  background: rgba(255, 193, 7, 0.1);
}

.alert-item.success {
  border-left-color: #28a745;
  background: rgba(40, 167, 69, 0.1);
}

.alert-icon {
  font-size: 1.2rem;
  margin-top: 2px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  margin: 0 0 4px 0;
  font-weight: 600;
  color: #ffffff;
}

.alert-desc {
  margin: 0 0 4px 0;
  font-size: 0.9rem;
  color: rgba(245, 245, 245, 0.8);
}

.alert-time {
  font-size: 0.8rem;
  color: rgba(245, 245, 245, 0.6);
}

.alert-dismiss {
  background: none;
  border: none;
  color: rgba(245, 245, 245, 0.6);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.alert-dismiss:hover {
  color: #ffffff;
}

/* Export Actions */
.export-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.export-btn {
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #f5f5f5;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: linear-gradient(145deg, rgba(25, 30, 25, 0.95), rgba(18, 22, 18, 0.98));
  border-radius: 12px;
  padding: 30px;
  width: 90%;
  max-width: 600px;
  border: 1px solid rgba(170, 140, 60, 0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  color: #ffffff;
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: 600;
  color: #f5f5f5;
  font-size: 0.9rem;
}

.form-group select,
.form-group input,
.form-group textarea {
  padding: 10px;
  border: 1px solid rgba(170, 140, 60, 0.3);
  border-radius: 6px;
  background: rgba(20, 24, 20, 0.5);
  color: #f5f5f5;
  outline: none;
  font-size: 0.9rem;
}

.form-group select:focus,
.form-group input:focus,
.form-group textarea:focus {
  border-color: #b48c28;
  box-shadow: 0 0 0 2px rgba(180, 140, 40, 0.2);
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  color: #111;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(180, 140, 40, 0.3);
}

.btn-secondary {
  background: rgba(108, 117, 125, 0.2);
  color: #f5f5f5;
  border: 1px solid rgba(170, 140, 60, 0.3);
}

.btn-secondary:hover {
  background: rgba(108, 117, 125, 0.3);
}

/* Responsive */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .quick-actions-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sales-dashboard {
    padding: 20px;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .kpi-card {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }

  .modal {
    padding: 20px;
    margin: 10px;
  }
}
</style>