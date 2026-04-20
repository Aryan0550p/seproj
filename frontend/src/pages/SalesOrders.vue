<template>
  <div class="orders-page">
    <div class="page-header">
      <h1>Orders</h1>
      <div class="header-actions">
        <button @click="openModal('add')" class="btn-primary">
          <span class="btn-icon">➕</span>
          Create Order
        </button>
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
      <button @click="filterStatus = 'processing'" :class="{ active: filterStatus === 'processing' }" class="tab-btn">Processing</button>
      <button @click="filterStatus = 'shipped'" :class="{ active: filterStatus === 'shipped' }" class="tab-btn">Shipped</button>
      <button @click="filterStatus = 'delivered'" :class="{ active: filterStatus === 'delivered' }" class="tab-btn">Delivered</button>
    </div>

    <!-- Orders Table -->
    <div class="table-container">
      <table class="orders-table">
        <thead>
          <tr>
            <th @click="sortBy('orderNumber')">Order # ▼</th>
            <th @click="sortBy('customer')">Customer</th>
            <th @click="sortBy('product')">Product</th>
            <th @click="sortBy('quantity')">Quantity</th>
            <th @click="sortBy('totalValue')">Value</th>
            <th @click="sortBy('status')">Status</th>
            <th @click="sortBy('orderDate')">Order Date</th>
            <th @click="sortBy('deliveryDate')">Delivery Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in paginatedOrders" :key="order.id">
            <td>
              <div class="order-number">{{ order.orderNumber }}</div>
            </td>
            <td>{{ order.customer }}</td>
            <td>{{ order.product }}</td>
            <td>{{ order.quantity }}</td>
            <td class="value">₹{{ order.totalValue.toLocaleString() }}</td>
            <td>
              <span class="status" :class="order.status.toLowerCase()">{{ order.status }}</span>
            </td>
            <td>
              <div class="date-info">
                <div>{{ formatDate(order.orderDate) }}</div>
              </div>
            </td>
            <td>
              <div class="date-info">
                <div>{{ formatDate(order.deliveryDate) }}</div>
                <div class="days-left" :class="{ 'overdue': isOverdue(order.deliveryDate), 'urgent': isUrgent(order.deliveryDate) }">
                  {{ getDeliveryStatus(order.deliveryDate, order.status) }}
                </div>
              </div>
            </td>
            <td class="actions">
              <button @click="editOrder(order)" class="btn-sm edit">Edit</button>
              <button @click="updateStatus(order)" class="btn-sm status" :disabled="order.status === 'Delivered'">Update</button>
              <button @click="viewDetails(order)" class="btn-sm view">Details</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button @click="prevPage" :disabled="currentPage === 1" class="btn-pagination">Previous</button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-pagination">Next</button>
    </div>

    <!-- Add/Edit Order Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h3>{{ modalType === 'edit' ? 'Edit Order' : 'Create New Order' }}</h3>
        <form @submit.prevent="submitModal">
          <div class="form-row">
            <div class="form-group">
              <label>Customer *</label>
              <select v-model="modalData.customer" required>
                <option value="">Select Customer</option>
                <option v-for="customer in customers" :key="customer" :value="customer">{{ customer }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Product *</label>
              <select v-model="modalData.product" required>
                <option value="">Select Product</option>
                <option v-for="product in products" :key="product" :value="product">{{ product }}</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Quantity *</label>
              <input v-model.number="modalData.quantity" type="number" min="1" required />
            </div>
            <div class="form-group">
              <label>Unit Price (₹) *</label>
              <input v-model.number="modalData.unitPrice" type="number" min="0" step="0.01" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Order Date *</label>
              <input v-model="modalData.orderDate" type="date" required />
            </div>
            <div class="form-group">
              <label>Expected Delivery Date *</label>
              <input v-model="modalData.deliveryDate" type="date" required />
            </div>
          </div>
          <div class="form-group">
            <label>Delivery Address</label>
            <textarea v-model="modalData.deliveryAddress" rows="3" placeholder="Enter delivery address..."></textarea>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="modalData.notes" rows="2" placeholder="Order notes or special instructions..."></textarea>
          </div>
          <div class="order-preview">
            <h4>Order Summary</h4>
            <div class="preview-line">
              <span>Subtotal:</span>
              <span>₹{{ calculateSubtotal().toLocaleString() }}</span>
            </div>
            <div class="preview-line">
              <span>Tax (18%):</span>
              <span>₹{{ calculateTax().toLocaleString() }}</span>
            </div>
            <div class="preview-line total">
              <span>Total:</span>
              <span>₹{{ calculateTotal().toLocaleString() }}</span>
            </div>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">{{ modalType === 'edit' ? 'Update' : 'Create' }} Order</button>
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Status Update Modal -->
    <div v-if="showStatusModal" class="modal-overlay" @click="closeStatusModal">
      <div class="modal" @click.stop>
        <h3>Update Order Status</h3>
        <p>Order: {{ selectedOrder.orderNumber }} - {{ selectedOrder.customer }}</p>
        <form @submit.prevent="submitStatusUpdate">
          <div class="form-group">
            <label>New Status *</label>
            <select v-model="newStatus" required>
              <option value="">Select Status</option>
              <option value="Pending">Pending</option>
              <option value="Processing">Processing</option>
              <option value="Shipped">Shipped</option>
              <option value="Delivered">Delivered</option>
            </select>
          </div>
          <div class="form-group">
            <label>Status Notes</label>
            <textarea v-model="statusNotes" rows="3" placeholder="Add notes about this status update..."></textarea>
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
import { getOrders, addOrder, updateOrder, getProducts } from '../store'

export default {
  name: 'SalesOrders',
  setup() {
    const storeOrders = ref([])
    const storeProducts = ref([])

    const reload = () => {
      const raw = getOrders()
      storeOrders.value = raw.map(o => ({
        id: o.id,
        orderNumber: o.id,
        customer: o.customer,
        product: o.items && o.items[0] ? o.items[0].name : 'N/A',
        quantity: o.items && o.items[0] ? o.items[0].qty : 0,
        unitPrice: o.items && o.items[0] ? o.items[0].price : 0,
        totalValue: o.total || 0,
        status: o.status,
        orderDate: o.date,
        deliveryDate: o.deliveryDate || 'TBD',
        deliveryAddress: o.deliveryAddress || '',
        notes: o.notes || ''
      }))
      storeProducts.value = getProducts()
    }

    onMounted(reload)

    const orders = computed(() => storeOrders.value)
    const customers = computed(() => [...new Set(storeOrders.value.map(o => o.customer))])
    const products = computed(() => storeProducts.value.map(p => p.name))
    
    const searchQuery = ref('')
    const filterStatus = ref('all')
    const sortKey = ref('orderNumber')
    const sortOrder = ref(1)
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const showModal = ref(false)
    const modalType = ref('')
    const modalData = ref({ 
      customer: '', 
      product: '', 
      quantity: 1, 
      unitPrice: 0, 
      orderDate: '',
      deliveryDate: '',
      deliveryAddress: '',
      notes: ''
    })

    // Status update modal
    const showStatusModal = ref(false)
    const selectedOrder = ref({})
    const newStatus = ref('')
    const statusNotes = ref('')

    const pendingOrders = computed(() => orders.value.filter(o => o.status === 'Pending').length)
    const shippedOrders = computed(() => orders.value.filter(o => o.status === 'Shipped').length)
    const deliveredOrders = computed(() => orders.value.filter(o => o.status === 'Delivered').length)

    const filteredOrders = computed(() => {
      let filtered = orders.value

      // Apply status filter
      if (filterStatus.value !== 'all') {
        filtered = filtered.filter(order => order.status.toLowerCase() === filterStatus.value.toLowerCase())
      }

      // Apply search filter
      if (searchQuery.value) {
        filtered = filtered.filter(order =>
          order.orderNumber.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          order.customer.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          order.product.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }

      // Apply sorting
      return filtered.sort((a, b) => {
        const aVal = a[sortKey.value]
        const bVal = b[sortKey.value]
        return (aVal > bVal ? 1 : -1) * sortOrder.value
      })
    })

    const totalPages = computed(() => Math.ceil(filteredOrders.value.length / itemsPerPage.value))

    const paginatedOrders = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredOrders.value.slice(start, end)
    })

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortOrder.value = -sortOrder.value
      } else {
        sortKey.value = key
        sortOrder.value = 1
      }
    }

    const filterOrders = () => {
      currentPage.value = 1
    }

    const prevPage = () => {
      if (currentPage.value > 1) currentPage.value--
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) currentPage.value++
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }

    const getDeliveryStatus = (deliveryDate, status) => {
      if (status === 'Delivered') return 'Delivered'
      
      const today = new Date()
      const deliveryDateObj = new Date(deliveryDate)
      const diffTime = deliveryDateObj - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) return 'Overdue'
      if (diffDays === 0) return 'Due today'
      if (diffDays === 1) return 'Tomorrow'
      return `${diffDays} days`
    }

    const isOverdue = (deliveryDate) => {
      return new Date(deliveryDate) < new Date()
    }

    const isUrgent = (deliveryDate) => {
      const diffTime = new Date(deliveryDate) - new Date()
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays >= 0 && diffDays <= 2
    }

    const calculateSubtotal = () => {
      return (modalData.value.quantity || 0) * (modalData.value.unitPrice || 0)
    }

    const calculateTax = () => {
      return calculateSubtotal() * 0.18 // 18% tax
    }

    const calculateTotal = () => {
      return calculateSubtotal() + calculateTax()
    }

    const openModal = (type, order = null) => {
      modalType.value = type
      if (type === 'edit' && order) {
        modalData.value = { ...order }
      } else {
        const today = new Date()
        const deliveryDate = new Date(today.setDate(today.getDate() + 7))
        modalData.value = { 
          customer: '', 
          product: '', 
          quantity: 1, 
          unitPrice: 0, 
          orderDate: today.toISOString().split('T')[0],
          deliveryDate: deliveryDate.toISOString().split('T')[0],
          deliveryAddress: '',
          notes: ''
        }
      }
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
    }

    const editOrder = (order) => {
      openModal('edit', order)
    }

    const submitModal = () => {
      const totalValue = calculateTotal()
      
      if (modalType.value === 'edit') {
        updateOrder(modalData.value.id, {
          customer: modalData.value.customer,
          items: [{ productId: '', name: modalData.value.product, qty: modalData.value.quantity, price: modalData.value.unitPrice }],
          total: totalValue,
          deliveryDate: modalData.value.deliveryDate,
          deliveryAddress: modalData.value.deliveryAddress,
          notes: modalData.value.notes
        })
        showToast('Order updated successfully!', 'success')
      } else {
        const prod = storeProducts.value.find(p => p.name === modalData.value.product)
        addOrder({
          customer: modalData.value.customer,
          createdBy: 'salesman',
          items: [{ productId: prod?.id || '', name: modalData.value.product, qty: modalData.value.quantity, price: modalData.value.unitPrice }],
          total: totalValue,
          status: 'Pending',
          payment: 'Unpaid',
          deliveryDate: modalData.value.deliveryDate,
          deliveryAddress: modalData.value.deliveryAddress,
          notes: modalData.value.notes
        })
        showToast('Order created successfully!', 'success')
      }
      reload()
      closeModal()
    }

    const updateStatus = (order) => {
      selectedOrder.value = order
      newStatus.value = order.status
      statusNotes.value = ''
      showStatusModal.value = true
    }

    const closeStatusModal = () => {
      showStatusModal.value = false
      selectedOrder.value = {}
      newStatus.value = ''
      statusNotes.value = ''
    }

    const submitStatusUpdate = () => {
      updateOrder(selectedOrder.value.id, { status: newStatus.value })
      reload()
      showToast(`Order ${selectedOrder.value.orderNumber} status updated to ${newStatus.value}!`, 'success')
      closeStatusModal()
    }

    const viewDetails = (order) => {
      showToast(`Viewing details for order ${order.orderNumber}`, 'info')
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

    return {
      orders,
      customers,
      products,
      searchQuery,
      filterStatus,
      filteredOrders,
      paginatedOrders,
      currentPage,
      totalPages,
      pendingOrders,
      shippedOrders,
      deliveredOrders,
      showModal,
      modalType,
      modalData,
      showStatusModal,
      selectedOrder,
      newStatus,
      statusNotes,
      sortBy,
      filterOrders,
      prevPage,
      nextPage,
      formatDate,
      getDeliveryStatus,
      isOverdue,
      isUrgent,
      calculateSubtotal,
      calculateTax,
      calculateTotal,
      openModal,
      closeModal,
      editOrder,
      submitModal,
      updateStatus,
      closeStatusModal,
      submitStatusUpdate,
      viewDetails
    }
  }
}
</script>

<style scoped>
.orders-page {
  padding: 30px;
  color: var(--text-primary);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.page-header h1 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.search-container {
  position: relative;
}

.search-input {
  padding: 10px 40px 10px 15px;
  border: 1px solid var(--border-input);
  border-radius: 8px;
  background: var(--bg-input);
  color: var(--text-primary);
  outline: none;
  width: 250px;
}

.search-input::placeholder {
  color: rgba(245, 245, 245, 0.6);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-accent);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: var(--shadow-main);
}

.stat-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.stat-content h3 {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.filter-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-input);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: rgba(170, 140, 60, 0.2);
}

.tab-btn.active {
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  color: #111;
  border-color: transparent;
}

.table-container {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-accent);
  box-shadow: var(--shadow-main);
  margin-bottom: 20px;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
  color: var(--text-primary);
}

.orders-table th {
  background: var(--bg-secondary);
  padding: 15px;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.orders-table td {
  padding: 15px;
  border-bottom: 1px solid var(--border-subtle);
}

.order-number {
  font-weight: 700;
  color: var(--accent-gold);
}

.value {
  font-weight: 700;
  color: #6e9f3a;
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

.status.processing {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-accent);
}

.status.shipped {
  background: var(--status-shipped-bg);
  color: var(--status-shipped-text);
}

.status.delivered {
  background: var(--status-delivered-bg);
  color: var(--status-delivered-text);
}

.date-info {
  font-size: 0.9rem;
}

.days-left {
  font-size: 0.8rem;
  font-weight: 600;
}

.days-left.overdue {
  color: var(--status-rejected-text);
}

.days-left.urgent {
  color: var(--status-pending-text);
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
  background: rgba(0, 123, 255, 0.2);
  color: #007bff;
}

.btn-sm.edit:hover {
  background: rgba(0, 123, 255, 0.4);
}

.btn-sm.status {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.btn-sm.status:hover:not(:disabled) {
  background: rgba(255, 193, 7, 0.4);
}

.btn-sm.status:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm.view {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.btn-sm.view:hover {
  background: rgba(40, 167, 69, 0.4);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.btn-pagination {
  padding: 8px 16px;
  border: 1px solid var(--border-input);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-pagination:hover:not(:disabled) {
  background: rgba(170, 140, 60, 0.2);
}

.btn-pagination:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary);
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  color: #111;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(180, 140, 40, 0.3);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-accent);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--bg-card-hover);
}

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
  background: var(--bg-modal);
  border-radius: 12px;
  padding: 30px;
  width: 90%;
  max-width: 600px;
  border: 1px solid var(--border-accent);
  box-shadow: var(--shadow-main);
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.modal p {
  color: var(--text-secondary);
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
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid var(--border-input);
  border-radius: 6px;
  background: var(--bg-input);
  color: var(--text-primary);
  outline: none;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #b48c28;
  box-shadow: 0 0 0 2px rgba(180, 140, 40, 0.2);
}

.order-preview {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
}

.order-preview h4 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
  font-size: 1rem;
}

.preview-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  color: var(--text-secondary);
}

.preview-line.total {
  font-weight: 700;
  color: var(--text-primary);
  border-top: 1px solid var(--border-subtle);
  padding-top: 5px;
  margin-top: 10px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .orders-page {
    padding: 20px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filter-tabs {
    justify-content: center;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .table-container {
    overflow-x: auto;
  }
}
</style>
