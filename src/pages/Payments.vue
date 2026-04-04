<template>
  <div class="payments p-4">
    <div class="page-header">
      <h1>Payment Management</h1>
    </div>

    <!-- Summary -->
    <div class="grid grid-3 mb-4">
      <div class="card text-center">
        <h3 class="summary-title">Total Revenue</h3>
        <p class="metric-value">₹{{ totalRevenue.toLocaleString() }}</p>
      </div>
      <div class="card text-center">
        <h3 class="summary-title">Pending Payments</h3>
        <p class="metric-value">₹{{ pendingAmount.toLocaleString() }}</p>
      </div>
      <div class="card text-center">
        <h3 class="summary-title">Paid Amount</h3>
        <p class="metric-value">₹{{ paidAmount.toLocaleString() }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card payment-toolbar mb-4">
      <select class="filter-input" v-model="paymentFilter">
        <option value="all">All Payments</option>
        <option value="Paid">Paid</option>
        <option value="Unpaid">Unpaid</option>
      </select>
    </div>

    <!-- Payment List -->
    <div class="grid">
      <div class="card payment-item" v-for="order in filteredOrders" :key="order.id">
        <div class="payment-info">
          <h4>{{ order.id }}</h4>
          <p><strong>Customer:</strong> {{ order.customer }}</p>
          <p><strong>Order Date:</strong> {{ order.date }}</p>
          <p><strong>Status:</strong> {{ order.status }}</p>
        </div>
        <div class="payment-amount">
          <p class="metric-value">₹{{ order.total.toLocaleString() }}</p>
          <span class="status" :class="(order.payment || 'unpaid').toLowerCase()">{{ order.payment || 'Unpaid' }}</span>
        </div>
        <div class="payment-actions">
          <button v-if="order.payment !== 'Paid'" @click="markPaid(order)" class="btn-primary btn-sm">Process Payment</button>
          <span v-else style="color: #6ecf8d; font-weight: 600;">✓ Paid</span>
        </div>
      </div>
      <div v-if="filteredOrders.length === 0" class="card" style="text-align: center; padding: 40px; color: #999;">No payment records found.</div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getOrders, updateOrder } from '../store'

export default {
  name: 'Payments',
  setup() {
    const orders = ref([])
    const paymentFilter = ref('all')

    const reload = async () => {
      orders.value = await getOrders()
    }
    onMounted(() => { reload() })

    const totalRevenue = computed(() => orders.value.reduce((s, o) => s + (o.total || 0), 0))
    const paidAmount = computed(() => orders.value.filter(o => o.payment === 'Paid').reduce((s, o) => s + (o.total || 0), 0))
    const pendingAmount = computed(() => totalRevenue.value - paidAmount.value)

    const filteredOrders = computed(() => {
      if (paymentFilter.value === 'all') return orders.value
      return orders.value.filter(o => (o.payment || 'Unpaid') === paymentFilter.value)
    })

    const markPaid = async (order) => {
      try {
        const updated = await updateOrder(order.id, { payment: 'Paid' })
        await reload()
        if (updated?.isFinalized) {
          window.alert(`Order ${order.id} finalized successfully.`)
        }
      } catch (error) {
        window.alert(error.message || 'Failed to process payment')
      }
    }

    return { orders, paymentFilter, totalRevenue, paidAmount, pendingAmount, filteredOrders, markPaid }
  }
}
</script>

<style scoped>
.payments { padding: 40px; color: var(--text-primary); }
h1 { margin: 0; }
.grid.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.5rem; margin-bottom: 30px; }
.grid { display: flex; flex-direction: column; gap: 20px; }
.card { padding: 24px; border-radius: 18px; background: var(--bg-card); border: 1px solid var(--border-accent); box-shadow: var(--shadow-main); }
.text-center { text-align: center; }
.summary-title { font-size: 0.85rem; letter-spacing: 1px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: var(--text-primary); }
.payment-toolbar { display: flex; gap: 20px; align-items: center; padding: 20px; background: var(--bg-card); border-radius: 18px; border: 1px solid var(--border-accent); margin-bottom: 30px; }
.filter-input { padding: 0.6rem 1rem; border-radius: 30px; border: 1px solid var(--border-input); background: var(--bg-input); color: var(--text-primary); font-weight: 500; cursor: pointer; }
.filter-input option { background-color: var(--bg-card); color: var(--text-primary); }
.filter-input:focus { outline: none; box-shadow: var(--shadow-glow); border-color: var(--accent-gold); }
.payment-item { display: flex; justify-content: space-between; align-items: center; gap: 2rem; }
.payment-info h4 { margin-bottom: 0.5rem; color: var(--accent-gold); }
.payment-info p { margin: 4px 0; color: var(--text-secondary); }
.payment-amount { text-align: center; }
.status { display: inline-block; margin-top: 0.4rem; padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.paid { background: var(--status-delivered-bg); border: 1px solid var(--border-accent); color: var(--status-delivered-text); }
.unpaid { background: var(--status-pending-bg); border: 1px solid var(--border-accent); color: var(--status-pending-text); }
.btn-primary { border: none; border-radius: 25px; background: linear-gradient(135deg, #b88a2a, #7a9f2f); color: white; font-weight: 600; cursor: pointer; transition: all 0.4s ease; }
.btn-primary:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(180, 140, 40, 0.5); }
.btn-sm { padding: 8px 16px; font-size: 0.8rem; }
@media (max-width: 768px) { .payment-item { flex-direction: column; text-align: center; } .grid.grid-3 { grid-template-columns: 1fr; } }
</style>