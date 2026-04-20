<template>
  <div class="customers-page">
    <div class="page-header">
      <h1>Customers</h1>
      <div class="header-actions">
        <button @click="openModal('add')" class="btn-primary">
          <span class="btn-icon">➕</span>
          Add Customer
        </button>
        <div class="search-container">
          <input v-model="searchQuery" @input="filterCustomers" type="text" placeholder="Search customers..." class="search-input" />
          <span class="search-icon">🔍</span>
        </div>
      </div>
    </div>

    <!-- Customer Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <h3>Total Customers</h3>
          <div class="stat-value">{{ customers.length }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-content">
          <h3>Active Customers</h3>
          <div class="stat-value">{{ activeCustomers }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <h3>Total Revenue</h3>
          <div class="stat-value">₹{{ totalRevenue.toLocaleString() }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <h3>Avg Order Value</h3>
          <div class="stat-value">₹{{ avgOrderValue.toLocaleString() }}</div>
        </div>
      </div>
    </div>

    <!-- Customers Table -->
    <div class="table-container">
      <table class="customers-table">
        <thead>
          <tr>
            <th @click="sortBy('name')">Customer Name ▼</th>
            <th @click="sortBy('email')">Email</th>
            <th @click="sortBy('phone')">Phone</th>
            <th @click="sortBy('totalOrders')">Orders</th>
            <th @click="sortBy('totalSpent')">Total Spent</th>
            <th @click="sortBy('status')">Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in paginatedCustomers" :key="customer.id">
            <td>
              <div class="customer-info">
                <div class="customer-avatar">{{ customer.name.charAt(0) }}</div>
                <div>
                  <div class="customer-name">{{ customer.name }}</div>
                  <div class="customer-company">{{ customer.company }}</div>
                </div>
              </div>
            </td>
            <td>{{ customer.email }}</td>
            <td>{{ customer.phone }}</td>
            <td>{{ customer.totalOrders }}</td>
            <td>₹{{ customer.totalSpent.toLocaleString() }}</td>
            <td>
              <span class="status" :class="customer.status.toLowerCase()">{{ customer.status }}</span>
            </td>
            <td class="actions">
              <button @click="editCustomer(customer)" class="btn-sm edit">Edit</button>
              <button @click="viewOrders(customer)" class="btn-sm view">Orders</button>
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

    <!-- Add/Edit Customer Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h3>{{ modalType === 'edit' ? 'Edit Customer' : 'Add New Customer' }}</h3>
        <form @submit.prevent="submitModal">
          <div class="form-row">
            <div class="form-group">
              <label>Name *</label>
              <input v-model="modalData.name" type="text" required />
            </div>
            <div class="form-group">
              <label>Company</label>
              <input v-model="modalData.company" type="text" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Email *</label>
              <input v-model="modalData.email" type="email" required />
            </div>
            <div class="form-group">
              <label>Phone *</label>
              <input v-model="modalData.phone" type="tel" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Status</label>
              <select v-model="modalData.status">
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
                <option value="Prospect">Prospect</option>
              </select>
            </div>
            <div class="form-group">
              <label>Address</label>
              <input v-model="modalData.address" type="text" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">{{ modalType === 'edit' ? 'Update' : 'Add' }} Customer</button>
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'Customers',
  setup() {
    const customers = ref([
      { id: 1, name: 'Retail Corp A', company: 'Retail Corp', email: 'contact@retailcorp.com', phone: '+91 9876543210', totalOrders: 15, totalSpent: 250000, status: 'Active', address: '123 Main St, Mumbai' },
      { id: 2, name: 'Shop B', company: 'Shop B Inc', email: 'info@shopb.com', phone: '+91 9876543211', totalOrders: 8, totalSpent: 180000, status: 'Active', address: '456 Market St, Delhi' },
      { id: 3, name: 'Mart C', company: 'Mart C Ltd', email: 'hello@martc.com', phone: '+91 9876543212', totalOrders: 12, totalSpent: 320000, status: 'Active', address: '789 Commerce St, Bangalore' },
      { id: 4, name: 'Store D', company: 'Store D Co', email: 'contact@stored.com', phone: '+91 9876543213', totalOrders: 5, totalSpent: 150000, status: 'Inactive', address: '321 Retail Ave, Chennai' },
      { id: 5, name: 'Retail E', company: 'Retail E Group', email: 'sales@retaile.com', phone: '+91 9876543214', totalOrders: 20, totalSpent: 280000, status: 'Active', address: '654 Business Park, Hyderabad' }
    ])

    const searchQuery = ref('')
    const sortKey = ref('name')
    const sortOrder = ref(1)
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const showModal = ref(false)
    const modalType = ref('')
    const modalData = ref({ name: '', company: '', email: '', phone: '', status: 'Active', address: '' })

    const activeCustomers = computed(() => customers.value.filter(c => c.status === 'Active').length)
    
    const totalRevenue = computed(() => 
      customers.value.reduce((sum, customer) => sum + customer.totalSpent, 0)
    )

    const avgOrderValue = computed(() => {
      const totalOrders = customers.value.reduce((sum, customer) => sum + customer.totalOrders, 0)
      return totalOrders > 0 ? Math.round(totalRevenue.value / totalOrders) : 0
    })

    const filteredCustomers = computed(() => {
      return customers.value.filter(customer =>
        customer.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        customer.email.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        customer.company.toLowerCase().includes(searchQuery.value.toLowerCase())
      ).sort((a, b) => {
        const aVal = a[sortKey.value]
        const bVal = b[sortKey.value]
        return (aVal > bVal ? 1 : -1) * sortOrder.value
      })
    })

    const totalPages = computed(() => Math.ceil(filteredCustomers.value.length / itemsPerPage.value))

    const paginatedCustomers = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredCustomers.value.slice(start, end)
    })

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortOrder.value = -sortOrder.value
      } else {
        sortKey.value = key
        sortOrder.value = 1
      }
    }

    const filterCustomers = () => {
      currentPage.value = 1
    }

    const prevPage = () => {
      if (currentPage.value > 1) currentPage.value--
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) currentPage.value++
    }

    const openModal = (type, customer = null) => {
      modalType.value = type
      if (type === 'edit' && customer) {
        modalData.value = { ...customer }
      } else {
        modalData.value = { name: '', company: '', email: '', phone: '', status: 'Active', address: '' }
      }
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      modalData.value = { name: '', company: '', email: '', phone: '', status: 'Active', address: '' }
    }

    const editCustomer = (customer) => {
      openModal('edit', customer)
    }

    const submitModal = () => {
      if (modalType.value === 'edit') {
        const index = customers.value.findIndex(c => c.id === modalData.value.id)
        if (index !== -1) {
          customers.value[index] = { ...modalData.value }
        }
        showToast('Customer updated successfully!', 'success')
      } else {
        const newCustomer = {
          id: customers.value.length + 1,
          ...modalData.value,
          totalOrders: 0,
          totalSpent: 0
        }
        customers.value.unshift(newCustomer)
        showToast('Customer added successfully!', 'success')
      }
      closeModal()
    }

    const viewOrders = (customer) => {
      showToast(`Viewing orders for ${customer.name}`, 'info')
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
      customers,
      searchQuery,
      filteredCustomers,
      paginatedCustomers,
      currentPage,
      totalPages,
      activeCustomers,
      totalRevenue,
      avgOrderValue,
      showModal,
      modalType,
      modalData,
      sortBy,
      filterCustomers,
      prevPage,
      nextPage,
      openModal,
      closeModal,
      editCustomer,
      submitModal,
      viewOrders
    }
  }
}
</script>

<style scoped>
.customers-page {
  padding: 30px;
  color: #f5f5f5;
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
  border: 1px solid rgba(170, 140, 60, 0.3);
  border-radius: 8px;
  background: rgba(20, 24, 20, 0.5);
  color: #f5f5f5;
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
  background: linear-gradient(145deg, rgba(25, 30, 25, 0.85), rgba(18, 22, 18, 0.95));
  border: 1px solid rgba(170, 140, 60, 0.2);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.stat-content h3 {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  color: #b5b5b5;
  font-weight: 600;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
}

.table-container {
  background: linear-gradient(145deg, rgba(22, 26, 22, 0.9), rgba(15, 18, 15, 0.95));
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(170, 140, 60, 0.2);
  margin-bottom: 20px;
}

.customers-table {
  width: 100%;
  border-collapse: collapse;
  color: #f5f5f5;
}

.customers-table th {
  background: rgba(180, 140, 40, 0.1);
  padding: 15px;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.customers-table td {
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.customer-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.customer-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #111;
}

.customer-name {
  font-weight: 600;
  color: #ffffff;
}

.customer-company {
  font-size: 0.85rem;
  color: rgba(245, 245, 245, 0.7);
}

.status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status.active {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.status.inactive {
  background: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.status.prospect {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
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
  background: rgba(0, 123, 255, 0.2);
  color: #007bff;
}

.btn-sm.edit:hover {
  background: rgba(0, 123, 255, 0.4);
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
  border: 1px solid rgba(170, 140, 60, 0.3);
  border-radius: 6px;
  background: rgba(20, 24, 20, 0.5);
  color: #f5f5f5;
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
  color: rgba(245, 245, 245, 0.8);
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
  background: rgba(108, 117, 125, 0.2);
  color: #f5f5f5;
  border: 1px solid rgba(170, 140, 60, 0.3);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(108, 117, 125, 0.3);
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

.form-group input,
.form-group select {
  padding: 10px;
  border: 1px solid rgba(170, 140, 60, 0.3);
  border-radius: 6px;
  background: rgba(20, 24, 20, 0.5);
  color: #f5f5f5;
  outline: none;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #b48c28;
  box-shadow: 0 0 0 2px rgba(180, 140, 40, 0.2);
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .customers-page {
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

  .form-row {
    grid-template-columns: 1fr;
  }

  .table-container {
    overflow-x: auto;
  }
}
</style>
