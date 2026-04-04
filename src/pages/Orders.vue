<template>
  <div class="orders-page">
    <div class="page-header">
      <h1>Order Management</h1>
      <div class="header-actions">
        <div class="search-container">
          <input v-model="searchQuery" @input="filterOrders" type="text" placeholder="Search orders..." class="search-input" />
          <span class="search-icon">🔍</span>
        </div>
      </div>
    </div>

    <!-- Order Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-content">
          <h3>Total Orders</h3>
          <div class="stat-value">{{ orders.length }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <div class="stat-content">
          <h3>Pending</h3>
          <div class="stat-value">{{ pendingOrders }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🚚</div>
        <div class="stat-content">
          <h3>Shipped</h3>
          <div class="stat-value">{{ shippedOrders }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <h3>Delivered</h3>
          <div class="stat-value">{{ deliveredOrders }}</div>
        </div>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button @click="filterStatus = 'all'" :class="{ active: filterStatus === 'all' }" class="tab-btn">All Orders</button>
      <button @click="filterStatus = 'pending'" :class="{ active: filterStatus === 'pending' }" class="tab-btn">Pending</button>
      <button @click="filterStatus = 'shipped'" :class="{ active: filterStatus === 'shipped' }" class="tab-btn">Shipped</button>
      <button @click="filterStatus = 'delivered'" :class="{ active: filterStatus === 'delivered' }" class="tab-btn">Delivered</button>
    </div>

    <!-- Orders Table -->
    <div class="table-container">
      <table class="orders-table">
        <thead>
          <tr>
            <th @click="sortBy('id')">Order # ▼</th>
            <th @click="sortBy('customer')">Customer</th>
            <th @click="sortBy('total')">Value</th>
            <th @click="sortBy('status')">Status</th>
            <th @click="sortBy('payment')">Payment</th>
            <th @click="sortBy('date')">Order Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in paginatedOrders" :key="order.id">
            <td>
              <div class="order-number">{{ order.id }}</div>
            </td>
            <td>{{ order.customer }}</td>
            <td class="value">₹{{ order.total.toLocaleString() }}</td>
            <td>
              <span class="status" :class="order.status.toLowerCase()">{{ order.status }}</span>
            </td>
            <td>
              <span class="status-payment" :class="order.payment.toLowerCase()">{{ order.payment }}</span>
            </td>
            <td>{{ formatDate(order.date) }}</td>
            <td class="actions">
              <button @click="openStatusModal(order)" class="btn-sm status">Update</button>
              <button v-if="order.payment === 'Unpaid'" @click="markPaid(order)" class="btn-sm paid">Mark Paid</button>
              <button v-else @click="markUnpaid(order)" class="btn-sm unpaid">Mark Unpaid</button>
              <button v-if="order.status === 'Pending'" @click="handleDispatch(order)" class="btn-sm dispatch">Dispatch</button>
              <button v-if="order.status !== 'Delivered'" @click="handleCancel(order)" class="btn-sm cancel">Cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredOrders.length === 0" class="empty-table">No orders found matching your criteria.</div>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button @click="prevPage" :disabled="currentPage === 1" class="btn-pagination">Previous</button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-pagination">Next</button>
    </div>

    <!-- Status Update Modal -->
    <div v-if="showStatusModal" class="modal-overlay" @click="closeStatusModal">
      <div class="modal" @click.stop>
        <h3>Update Order Status</h3>
        <p>Order: {{ selectedOrder.id }} - {{ selectedOrder.customer }}</p>
        <form @submit.prevent="submitStatusUpdate">
          <div class="form-group">
            <label>New Status *</label>
            <select v-model="newStatus" required>
              <option value="Pending">Pending</option>
              <option value="Shipped">Shipped</option>
              <option value="Delivered">Delivered</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">Update Status</button>
            <button type="button" @click="closeStatusModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getOrders, updateOrder, dispatchOrder, cancelOrder } from '../store'

export default {
  name: 'Orders',
  setup() {
    const orders = ref([])
    const searchQuery = ref('')
    const filterStatus = ref('all')
    const sortKey = ref('id')
    const sortOrder = ref(-1) // Default to descending for newest orders first
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    
    // Status Modal
    const showStatusModal = ref(false)
    const selectedOrder = ref({})
    const newStatus = ref('')

    const reload = async () => {
      orders.value = await getOrders()
    }
    onMounted(() => { reload() })

    const pendingOrders = computed(() => orders.value.filter(o => o.status === 'Pending').length)
    const shippedOrders = computed(() => orders.value.filter(o => o.status === 'Shipped').length)
    const deliveredOrders = computed(() => orders.value.filter(o => o.status === 'Delivered').length)

    const filteredOrders = computed(() => {
      let result = [...orders.value]
      
      if (filterStatus.value !== 'all') {
        result = result.filter(o => o.status.toLowerCase() === filterStatus.value.toLowerCase())
      }
      
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        result = result.filter(o => 
          o.id.toLowerCase().includes(q) || 
          o.customer.toLowerCase().includes(q)
        )
      }

      return result.sort((a, b) => {
        const aVal = a[sortKey.value]
        const bVal = b[sortKey.value]
        if (typeof aVal === 'string') {
          return aVal.localeCompare(bVal) * sortOrder.value
        }
        return (aVal - bVal) * sortOrder.value
      })
    })

    const totalPages = computed(() => Math.max(1, Math.ceil(filteredOrders.value.length / itemsPerPage.value)))
    const paginatedOrders = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      return filteredOrders.value.slice(start, start + itemsPerPage.value)
    })

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortOrder.value = -sortOrder.value
      } else {
        sortKey.value = key
        sortOrder.value = 1
      }
    }

    const filterOrders = () => { currentPage.value = 1 }
    const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
    const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    }

    const openStatusModal = (order) => {
      selectedOrder.value = order
      newStatus.value = order.status
      showStatusModal.value = true
    }

    const closeStatusModal = () => {
      showStatusModal.value = false
    }

    const submitStatusUpdate = async () => {
      try {
        const updated = await updateOrder(selectedOrder.value.id, { status: newStatus.value })
        await reload()
        closeStatusModal()
        if (updated?.isFinalized) {
          showToast('Status updated. Order finalized: payment and delivery are both completed.')
        } else {
          showToast('Status updated successfully!')
        }
      } catch (error) {
        showToast(error.message || 'Failed to update status')
      }
    }

    const markPaid = async (order) => {
      try {
        const updated = await updateOrder(order.id, { payment: 'Paid' })
        await reload()
        if (updated?.isFinalized) {
          showToast('Payment marked as Paid. Order finalized successfully!')
        } else {
          showToast('Payment marked as Paid!')
        }
      } catch (error) {
        showToast(error.message || 'Failed to mark payment as paid')
      }
    }

    const markUnpaid = async (order) => {
      try {
        await updateOrder(order.id, { payment: 'Unpaid' })
        await reload()
        showToast('Payment changed to Unpaid!')
      } catch (error) {
        showToast(error.message || 'Failed to mark payment as unpaid')
      }
    }

    const handleDispatch = async (order) => {
      try {
        await dispatchOrder(order.id)
        await reload()
        showToast('Order dispatched! Inventory reduced.')
      } catch (error) {
        showToast(error.message || 'Failed to dispatch order')
      }
    }

    const handleCancel = async (order) => {
      if (confirm(`Are you sure you want to cancel order ${order.id}? Inventory will be restored.`)) {
        try {
          await cancelOrder(order.id)
          await reload()
          showToast('Order cancelled. Inventory restored.')
        } catch (error) {
          showToast(error.message || 'Failed to cancel order')
        }
      }
    }

    const showToast = (message) => {
      const toast = document.createElement('div');
      toast.textContent = message;
      toast.style.cssText = `
        position: fixed; top: 20px; right: 20px; background: #6e9f3a; color: white;
        padding: 12px 20px; border-radius: 8px; z-index: 1000; font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      `;
      document.body.appendChild(toast);
      setTimeout(() => document.body.removeChild(toast), 3000);
    };

    return {
      orders, searchQuery, filterStatus, currentPage, totalPages,
      pendingOrders, shippedOrders, deliveredOrders,
      filteredOrders, paginatedOrders,
      showStatusModal, selectedOrder, newStatus,
      sortBy, filterOrders, prevPage, nextPage, formatDate,
      openStatusModal, closeStatusModal, submitStatusUpdate, markPaid, markUnpaid,
      handleDispatch, handleCancel
    }
  }
}
</script>

<style scoped>
.orders-page { 
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

.page-header h1 { 
  margin: 0; 
}

.search-container { position: relative; }
.search-input { 
  padding: 12px 45px 12px 20px; 
  border: 1px solid rgba(170, 140, 60, 0.2); 
  border-radius: 30px; 
  background: rgba(255, 255, 255, 0.03); 
  backdrop-filter: blur(10px);
  color: var(--text-primary); 
  width: 280px; 
  outline: none; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
}
.search-input:focus { 
  border-color: var(--accent-gold); 
  box-shadow: 0 0 20px rgba(180, 140, 40, 0.15);
  width: 320px;
}
.search-icon { 
  position: absolute; 
  right: 18px; 
  top: 50%; 
  transform: translateY(-50%); 
  opacity: 0.6; 
  font-size: 1.1rem;
}

.stats-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
  gap: 25px; 
  margin-bottom: 35px; 
}
.stat-card { 
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02)); 
  backdrop-filter: blur(15px);
  border: 1px solid rgba(170, 140, 60, 0.15); 
  border-radius: 16px; 
  padding: 24px; 
  display: flex; 
  align-items: center; 
  gap: 20px; 
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, border-color 0.3s ease;
}
.stat-card:hover { 
  transform: translateY(-5px); 
  border-color: rgba(180, 140, 40, 0.4);
}
.stat-icon { 
  font-size: 2.2rem; 
  filter: drop-shadow(0 0 8px rgba(180, 140, 40, 0.3));
}
.stat-content h3 { 
  margin: 0 0 4px 0; 
  font-size: 0.85rem; 
  color: var(--text-secondary); 
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.stat-value { 
  font-size: 1.8rem; 
  font-weight: 800; 
  color: #fff;
}

.filter-tabs { 
  display: flex; 
  gap: 12px; 
  margin-bottom: 25px; 
  overflow-x: auto; 
  padding: 5px; 
}
.tab-btn { 
  padding: 10px 22px; 
  border: 1px solid rgba(255, 255, 255, 0.1); 
  border-radius: 30px; 
  background: rgba(255, 255, 255, 0.03); 
  color: var(--text-secondary); 
  cursor: pointer; 
  transition: all 0.3s ease; 
  white-space: nowrap; 
  font-weight: 600; 
  font-size: 0.9rem;
}
.tab-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}
.tab-btn.active { 
  background: linear-gradient(135deg, var(--accent-gold), #7a9f2f); 
  color: #000; 
  border-color: transparent;
  box-shadow: 0 4px 15px rgba(180, 140, 40, 0.3);
}

.table-container { 
  background: rgba(20, 24, 20, 0.6); 
  backdrop-filter: blur(20px);
  border-radius: 20px; 
  padding: 25px; 
  border: 1px solid rgba(170, 140, 60, 0.1); 
  box-shadow: var(--shadow-main); 
  margin-bottom: 25px; 
}
.orders-table { width: 100%; border-collapse: collapse; }
.orders-table th { 
  text-align: left; 
  padding: 18px 15px; 
  border-bottom: 1px solid rgba(255, 255, 255, 0.08); 
  color: var(--text-dim); 
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer; 
}
.orders-table th:hover { color: var(--accent-gold); }
.orders-table td { 
  padding: 20px 15px; 
  border-bottom: 1px solid rgba(255, 255, 255, 0.04); 
  color: var(--text-primary);
}
.order-number { font-weight: 700; color: var(--accent-gold); font-family: monospace; font-size: 1rem; }
.value { font-weight: 800; color: #6e9f3a; }

.status { 
  padding: 5px 12px; 
  border-radius: 30px; 
  font-size: 0.7rem; 
  font-weight: 800; 
  letter-spacing: 0.5px;
  text-transform: uppercase; 
  display: inline-block;
}
.status.pending { background: rgba(180, 140, 40, 0.15); color: var(--accent-gold); border: 1px solid rgba(180, 140, 40, 0.3); }
.status.shipped { background: rgba(0, 123, 255, 0.15); color: #007bff; border: 1px solid rgba(0, 123, 255, 0.3); }
.status.delivered { background: rgba(110, 159, 58, 0.15); color: #6e9f3a; border: 1px solid rgba(110, 159, 58, 0.3); }

.status-payment { font-size: 0.8rem; font-weight: 700; }
.status-payment.paid { color: #6e9f3a; }
.status-payment.unpaid { color: #ff6b6b; }

.actions { display: flex; gap: 10px; }
.btn-sm { 
  padding: 8px 16px; 
  border-radius: 8px; 
  border: none; 
  font-weight: 700; 
  cursor: pointer; 
  font-size: 0.8rem; 
  transition: all 0.2s ease;
}
.btn-sm.status { 
  background: rgba(255, 255, 255, 0.05); 
  color: var(--text-primary); 
  border: 1px solid rgba(255, 255, 255, 0.1); 
}
.btn-sm.status:hover { background: rgba(255, 255, 255, 0.1); }
.btn-sm.paid { 
  background: rgba(110, 159, 58, 0.15); 
  color: #6e9f3a; 
  border: 1px solid rgba(110, 159, 58, 0.3); 
}
.btn-sm.paid:hover { background: rgba(110, 159, 58, 0.25); }
.btn-sm.unpaid {
  background: rgba(255, 152, 0, 0.15);
  color: #ff9800;
  border: 1px solid rgba(255, 152, 0, 0.3);
}
.btn-sm.unpaid:hover { background: rgba(255, 152, 0, 0.25); }
.btn-sm.dispatch {
  background: rgba(0, 123, 255, 0.15);
  color: #007bff;
  border: 1px solid rgba(0, 123, 255, 0.3);
}
.btn-sm.dispatch:hover { background: rgba(0, 123, 255, 0.25); }
.btn-sm.cancel {
  background: rgba(220, 53, 69, 0.15);
  color: #dc3545;
  border: 1px solid rgba(220, 53, 69, 0.3);
}
.btn-sm.cancel:hover { background: rgba(220, 53, 69, 0.25); }

.empty-table { text-align: center; padding: 60px; color: var(--text-dim); font-size: 1.1rem; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 24px; margin-top: 20px; }
.btn-pagination { 
  padding: 10px 20px; 
  border: 1px solid rgba(255, 255, 255, 0.1); 
  border-radius: 12px; 
  background: rgba(255, 255, 255, 0.05); 
  color: #fff; 
  cursor: pointer; 
  font-weight: 600;
  transition: all 0.2s;
}
.btn-pagination:hover:not(:disabled) { background: rgba(255, 255, 255, 0.1); }
.btn-pagination:disabled { opacity: 0.3; cursor: not-allowed; }

/* Modal */
.modal-overlay { 
  position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
  background: rgba(0, 0, 0, 0.85); 
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; z-index: 1000; 
}
.modal { 
  background: linear-gradient(165deg, #1a1e1a, #0f120f); 
  border: 1px solid rgba(170, 140, 60, 0.3); 
  padding: 35px; 
  border-radius: 24px; 
  width: 440px; 
  box-shadow: 0 25px 50px rgba(0,0,0,0.6); 
}
.modal h3 { margin: 0 0 10px 0; color: var(--accent-gold); font-size: 1.5rem; font-weight: 800; }
.modal p { color: var(--text-secondary); margin-bottom: 25px; font-size: 0.95rem; }
.form-group { margin-bottom: 25px; }
.form-group label { display: block; margin-bottom: 10px; font-size: 0.85rem; font-weight: 700; color: var(--text-dim); text-transform: uppercase; }
.form-group select { 
  width: 100%; padding: 14px; border-radius: 12px; 
  background: rgba(255, 255, 255, 0.05); 
  color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); 
  outline: none; font-size: 1rem;
}
.form-group select:focus { border-color: var(--accent-gold); }
.modal-actions { display: flex; gap: 15px; margin-top: 35px; }
.btn-primary { 
  flex: 1; padding: 14px; border-radius: 12px; border: none; 
  background: linear-gradient(135deg, var(--accent-gold), #7a9f2f); 
  color: #000; font-weight: 800; cursor: pointer; 
  box-shadow: 0 4px 15px rgba(180, 140, 40, 0.3);
  transition: transform 0.2s;
}
.btn-primary:hover { transform: scale(1.02); }
.btn-secondary { 
  flex: 1; padding: 14px; border-radius: 12px; 
  border: 1px solid rgba(255, 255, 255, 0.1); 
  background: rgba(255, 255, 255, 0.05); 
  color: #fff; cursor: pointer; font-weight: 600;
}
.btn-secondary:hover { background: rgba(255, 255, 255, 0.1); }
</style>