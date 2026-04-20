<template>
  <div class="quotes-page">
    <div class="page-header">
      <h1>Quotes</h1>
      <div class="header-actions">
        <button @click="openModal('add')" class="btn-primary">
          <span class="btn-icon">📝</span>
          Create Quote
        </button>
        <div class="search-container">
          <input v-model="searchQuery" @input="filterQuotes" type="text" placeholder="Search quotes..." class="search-input" />
          <span class="search-icon">🔍</span>
        </div>
      </div>
    </div>

    <!-- Quote Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📋</div>
        <div class="stat-content">
          <h3>Total Quotes</h3>
          <div class="stat-value">{{ quotes.length }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <div class="stat-content">
          <h3>Pending</h3>
          <div class="stat-value">{{ pendingQuotes }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <h3>Accepted</h3>
          <div class="stat-value">{{ acceptedQuotes }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <h3>Pipeline Value</h3>
          <div class="stat-value">₹{{ pipelineValue.toLocaleString() }}</div>
        </div>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button @click="filterStatus = 'all'" :class="{ active: filterStatus === 'all' }" class="tab-btn">All Quotes</button>
      <button @click="filterStatus = 'pending'" :class="{ active: filterStatus === 'pending' }" class="tab-btn">Pending</button>
      <button @click="filterStatus = 'accepted'" :class="{ active: filterStatus === 'accepted' }" class="tab-btn">Accepted</button>
      <button @click="filterStatus = 'rejected'" :class="{ active: filterStatus === 'rejected' }" class="tab-btn">Rejected</button>
      <button @click="filterStatus = 'expired'" :class="{ active: filterStatus === 'expired' }" class="tab-btn">Expired</button>
    </div>

    <!-- Quotes Table -->
    <div class="table-container">
      <table class="quotes-table">
        <thead>
          <tr>
            <th @click="sortBy('quoteNumber')">Quote # ▼</th>
            <th @click="sortBy('customer')">Customer</th>
            <th @click="sortBy('product')">Product</th>
            <th @click="sortBy('quantity')">Quantity</th>
            <th @click="sortBy('totalValue')">Value</th>
            <th @click="sortBy('status')">Status</th>
            <th @click="sortBy('validUntil')">Valid Until</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quote in paginatedQuotes" :key="quote.id">
            <td>
              <div class="quote-number">{{ quote.quoteNumber }}</div>
            </td>
            <td>{{ quote.customer }}</td>
            <td>{{ quote.product }}</td>
            <td>{{ quote.quantity }}</td>
            <td class="value">₹{{ quote.totalValue.toLocaleString() }}</td>
            <td>
              <span class="status" :class="quote.status.toLowerCase()">{{ quote.status }}</span>
            </td>
            <td>
              <div class="date-info">
                <div>{{ formatDate(quote.validUntil) }}</div>
                <div class="days-left" :class="{ 'expired': isExpired(quote.validUntil), 'urgent': isUrgent(quote.validUntil) }">
                  {{ getDaysLeft(quote.validUntil) }}
                </div>
              </div>
            </td>
            <td class="actions">
              <button @click="editQuote(quote)" class="btn-sm edit">Edit</button>
              <button @click="convertToOrder(quote)" class="btn-sm convert" :disabled="quote.status !== 'Accepted'">Convert</button>
              <button @click="sendEmail(quote)" class="btn-sm email">Email</button>
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

    <!-- Add/Edit Quote Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h3>{{ modalType === 'edit' ? 'Edit Quote' : 'Create New Quote' }}</h3>
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
              <label>Valid Until *</label>
              <input v-model="modalData.validUntil" type="date" required />
            </div>
            <div class="form-group">
              <label>Discount (%)</label>
              <input v-model.number="modalData.discount" type="number" min="0" max="100" step="0.1" />
            </div>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="modalData.notes" rows="3" placeholder="Additional terms or notes..."></textarea>
          </div>
          <div class="quote-preview">
            <h4>Quote Preview</h4>
            <div class="preview-line">
              <span>Subtotal:</span>
              <span>₹{{ calculateSubtotal().toLocaleString() }}</span>
            </div>
            <div class="preview-line">
              <span>Discount:</span>
              <span>₹{{ calculateDiscount().toLocaleString() }}</span>
            </div>
            <div class="preview-line total">
              <span>Total:</span>
              <span>₹{{ calculateTotal().toLocaleString() }}</span>
            </div>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">{{ modalType === 'edit' ? 'Update' : 'Create' }} Quote</button>
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
  name: 'Quotes',
  setup() {
    const quotes = ref([
      { id: 1, quoteNumber: 'Q001', customer: 'Retail Corp A', product: 'Product A', quantity: 50, unitPrice: 500, discount: 10, totalValue: 22500, status: 'Pending', validUntil: '2024-03-25', notes: 'Bulk pricing applied' },
      { id: 2, quoteNumber: 'Q002', customer: 'Shop B', product: 'Product B', quantity: 30, unitPrice: 600, discount: 5, totalValue: 17100, status: 'Accepted', validUntil: '2024-03-20', notes: 'Priority delivery' },
      { id: 3, quoteNumber: 'Q003', customer: 'Mart C', product: 'Product C', quantity: 40, unitPrice: 800, discount: 15, totalValue: 27200, status: 'Pending', validUntil: '2024-03-30', notes: '' },
      { id: 4, quoteNumber: 'Q004', customer: 'Store D', product: 'Product A', quantity: 25, unitPrice: 500, discount: 0, totalValue: 12500, status: 'Rejected', validUntil: '2024-03-15', notes: 'Competitor pricing issue' },
      { id: 5, quoteNumber: 'Q005', customer: 'Retail E', product: 'Product B', quantity: 35, unitPrice: 600, discount: 8, totalValue: 19320, status: 'Expired', validUntil: '2024-03-10', notes: 'Follow up required' }
    ])

    const customers = ref(['Retail Corp A', 'Shop B', 'Mart C', 'Store D', 'Retail E'])
    const products = ref(['Product A', 'Product B', 'Product C', 'Product D'])
    
    const searchQuery = ref('')
    const filterStatus = ref('all')
    const sortKey = ref('quoteNumber')
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
      discount: 0, 
      validUntil: '',
      notes: ''
    })

    const pendingQuotes = computed(() => quotes.value.filter(q => q.status === 'Pending').length)
    const acceptedQuotes = computed(() => quotes.value.filter(q => q.status === 'Accepted').length)
    
    const pipelineValue = computed(() => 
      quotes.value
        .filter(q => q.status === 'Pending' || q.status === 'Accepted')
        .reduce((sum, quote) => sum + quote.totalValue, 0)
    )

    const filteredQuotes = computed(() => {
      let filtered = quotes.value

      // Apply status filter
      if (filterStatus.value !== 'all') {
        filtered = filtered.filter(quote => quote.status.toLowerCase() === filterStatus.value.toLowerCase())
      }

      // Apply search filter
      if (searchQuery.value) {
        filtered = filtered.filter(quote =>
          quote.quoteNumber.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          quote.customer.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          quote.product.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }

      // Apply sorting
      return filtered.sort((a, b) => {
        const aVal = a[sortKey.value]
        const bVal = b[sortKey.value]
        return (aVal > bVal ? 1 : -1) * sortOrder.value
      })
    })

    const totalPages = computed(() => Math.ceil(filteredQuotes.value.length / itemsPerPage.value))

    const paginatedQuotes = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredQuotes.value.slice(start, end)
    })

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortOrder.value = -sortOrder.value
      } else {
        sortKey.value = key
        sortOrder.value = 1
      }
    }

    const filterQuotes = () => {
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

    const getDaysLeft = (validUntil) => {
      const today = new Date()
      const validDate = new Date(validUntil)
      const diffTime = validDate - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) return 'Expired'
      if (diffDays === 0) return 'Expires today'
      if (diffDays === 1) return '1 day left'
      return `${diffDays} days left`
    }

    const isExpired = (validUntil) => {
      return new Date(validUntil) < new Date()
    }

    const isUrgent = (validUntil) => {
      const diffTime = new Date(validUntil) - new Date()
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays >= 0 && diffDays <= 3
    }

    const calculateSubtotal = () => {
      return (modalData.value.quantity || 0) * (modalData.value.unitPrice || 0)
    }

    const calculateDiscount = () => {
      return calculateSubtotal() * ((modalData.value.discount || 0) / 100)
    }

    const calculateTotal = () => {
      return calculateSubtotal() - calculateDiscount()
    }

    const openModal = (type, quote = null) => {
      modalType.value = type
      if (type === 'edit' && quote) {
        modalData.value = { ...quote }
      } else {
        const today = new Date()
        const validUntil = new Date(today.setDate(today.getDate() + 30))
        modalData.value = { 
          customer: '', 
          product: '', 
          quantity: 1, 
          unitPrice: 0, 
          discount: 0, 
          validUntil: validUntil.toISOString().split('T')[0],
          notes: ''
        }
      }
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
    }

    const editQuote = (quote) => {
      openModal('edit', quote)
    }

    const submitModal = () => {
      const totalValue = calculateTotal()
      
      if (modalType.value === 'edit') {
        const index = quotes.value.findIndex(q => q.id === modalData.value.id)
        if (index !== -1) {
          quotes.value[index] = { 
            ...modalData.value, 
            totalValue,
            status: 'Pending' // Reset to pending when edited
          }
        }
        showToast('Quote updated successfully!', 'success')
      } else {
        const newQuote = {
          id: quotes.value.length + 1,
          quoteNumber: `Q${String(quotes.value.length + 1).padStart(3, '0')}`,
          ...modalData.value,
          totalValue,
          status: 'Pending'
        }
        quotes.value.unshift(newQuote)
        showToast('Quote created successfully!', 'success')
      }
      closeModal()
    }

    const convertToOrder = (quote) => {
      showToast(`Quote ${quote.quoteNumber} converted to order!`, 'success')
      quote.status = 'Converted'
    }

    const sendEmail = (quote) => {
      showToast(`Quote ${quote.quoteNumber} sent to ${quote.customer}!`, 'success')
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
      quotes,
      customers,
      products,
      searchQuery,
      filterStatus,
      filteredQuotes,
      paginatedQuotes,
      currentPage,
      totalPages,
      pendingQuotes,
      acceptedQuotes,
      pipelineValue,
      showModal,
      modalType,
      modalData,
      sortBy,
      filterQuotes,
      prevPage,
      nextPage,
      formatDate,
      getDaysLeft,
      isExpired,
      isUrgent,
      calculateSubtotal,
      calculateDiscount,
      calculateTotal,
      openModal,
      closeModal,
      editQuote,
      submitModal,
      convertToOrder,
      sendEmail
    }
  }
}
</script>

<style scoped>
.quotes-page {
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

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(90deg, #ffffff, #b48c28);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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

.filter-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid rgba(170, 140, 60, 0.3);
  border-radius: 8px;
  background: rgba(20, 24, 20, 0.5);
  color: #f5f5f5;
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
  background: linear-gradient(145deg, rgba(22, 26, 22, 0.9), rgba(15, 18, 15, 0.95));
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(170, 140, 60, 0.2);
  margin-bottom: 20px;
}

.quotes-table {
  width: 100%;
  border-collapse: collapse;
  color: #f5f5f5;
}

.quotes-table th {
  background: rgba(180, 140, 40, 0.1);
  padding: 15px;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.quotes-table td {
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.quote-number {
  font-weight: 700;
  color: #b48c28;
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
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.status.accepted {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.status.rejected {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.status.expired {
  background: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.date-info {
  font-size: 0.9rem;
}

.days-left {
  font-size: 0.8rem;
  font-weight: 600;
}

.days-left.expired {
  color: #dc3545;
}

.days-left.urgent {
  color: #ffc107;
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

.btn-sm.convert {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.btn-sm.convert:hover:not(:disabled) {
  background: rgba(40, 167, 69, 0.4);
}

.btn-sm.convert:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm.email {
  background: rgba(23, 162, 184, 0.2);
  color: #17a2b8;
}

.btn-sm.email:hover {
  background: rgba(23, 162, 184, 0.4);
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
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid rgba(170, 140, 60, 0.3);
  border-radius: 6px;
  background: rgba(20, 24, 20, 0.5);
  color: #f5f5f5;
  outline: none;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #b48c28;
  box-shadow: 0 0 0 2px rgba(180, 140, 40, 0.2);
}

.quote-preview {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
}

.quote-preview h4 {
  margin: 0 0 10px 0;
  color: #ffffff;
  font-size: 1rem;
}

.preview-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  color: rgba(245, 245, 245, 0.8);
}

.preview-line.total {
  font-weight: 700;
  color: #ffffff;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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
  .quotes-page {
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
