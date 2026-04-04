<template>
  <div class="inventory">
    <div class="page-header">
      <h1>Inventory Management</h1>
    </div>
    <div class="inventory-actions">
      <button class="btn btn-primary" @click="openAddModal">Add New Item</button>
      <button class="btn btn-secondary" @click="openSampleModal">📦 Record Sample</button>
      <button class="btn btn-secondary" @click="openPhysicalCountModal">📋 Physical Count</button>
      <input type="text" v-model="searchQuery" placeholder="Search inventory..." class="search-input">
    </div>
    <div class="inventory-table">
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Product Name</th>
            <th>Category</th>
            <th>Stock Quantity</th>
            <th>Unit Price</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in filteredProducts" :key="product.id">
            <td>{{ product.sku }}</td>
            <td>{{ product.name }}</td>
            <td>{{ product.category }}</td>
            <td>{{ product.stock }}</td>
            <td>₹{{ product.price.toLocaleString() }} / {{ product.unit }}</td>
            <td>
              <span class="status" :class="getStockClass(product.stock)">{{ getStockLabel(product.stock) }}</span>
            </td>
            <td class="action-cell">
              <button class="btn btn-sm" @click="openEditModal(product)">Edit</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h3>{{ editingProduct ? 'Edit Product' : 'Add Product' }}</h3>
        <form @submit.prevent="saveProduct" class="modal-form">
          <div class="form-group">
            <label>Product Name</label>
            <input v-model="formData.name" type="text" required />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Category</label>
              <input v-model="formData.category" type="text" required />
            </div>
            <div class="form-group">
              <label>SKU</label>
              <input v-model="formData.sku" type="text" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Price (₹)</label>
              <input v-model.number="formData.price" type="number" min="0" required />
            </div>
            <div class="form-group">
              <label>Unit</label>
              <input v-model="formData.unit" type="text" required placeholder="kg, L, etc." />
            </div>
          </div>
          <div class="form-group">
            <label>Stock Quantity</label>
            <input v-model.number="formData.stock" type="number" min="0" required />
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary">{{ editingProduct ? 'Update' : 'Add' }}</button>
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Sample Distribution Modal (SCRUM-23) -->
    <div v-if="showSampleModal" class="modal-overlay" @click="closeSampleModal">
      <div class="modal" @click.stop>
        <h3>Record Sample Distribution</h3>
        <form @submit.prevent="submitSampleDistribution" class="modal-form">
          <div class="form-group">
            <label>Product *</label>
            <select v-model="sampleData.productId" required>
              <option value="">Select Product</option>
              <option v-for="product in products" :key="product.id" :value="product.id">{{ product.name }} (Stock: {{ product.stock }})</option>
            </select>
          </div>
          <div class="form-group">
            <label>Quantity *</label>
            <input v-model.number="sampleData.quantity" type="number" min="1" required />
          </div>
          <div class="form-group">
            <label>Recipient Type</label>
            <input v-model="sampleData.recipientType" type="text" placeholder="e.g., customer, distributor, event" />
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary">Record Distribution</button>
            <button type="button" class="btn btn-secondary" @click="closeSampleModal">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Physical Stock Count Modal (SCRUM-26) -->
    <div v-if="showPhysicalCountModal" class="modal-overlay" @click="closePhysicalCountModal">
      <div class="modal" @click.stop>
        <h3>Record Physical Stock Count</h3>
        <form @submit.prevent="submitPhysicalCount" class="modal-form">
          <div class="form-group">
            <label>Product *</label>
            <select v-model="physicalData.productId" required>
              <option value="">Select Product</option>
              <option v-for="product in products" :key="product.id" :value="product.id">{{ product.name }} (System: {{ product.stock }})</option>
            </select>
          </div>
          <div class="form-group">
            <label>Physical Count *</label>
            <input v-model.number="physicalData.physicalCount" type="number" min="0" required />
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary">Record Count</button>
            <button type="button" class="btn btn-secondary" @click="closePhysicalCountModal">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getProducts, addProduct, updateProduct, recordSampleDistribution, recordPhysicalStock, getStockMismatches } from '../store'

export default {
  name: 'Inventory',
  setup() {
    const products = ref([])
    const searchQuery = ref('')
    const showModal = ref(false)
    const editingProduct = ref(null)
    const formData = ref({ name: '', category: '', sku: '', price: 0, unit: 'kg', stock: 0 })
    
    // Sample distribution (SCRUM-23)
    const showSampleModal = ref(false)
    const sampleData = ref({ productId: '', quantity: 1, recipientType: '' })
    
    // Physical stock count (SCRUM-26)
    const showPhysicalCountModal = ref(false)
    const physicalData = ref({ productId: '', physicalCount: 0 })

    const reload = async () => {
      products.value = await getProducts()
    }
    onMounted(() => { reload() })

    const filteredProducts = computed(() => {
      if (!searchQuery.value) return products.value
      const q = searchQuery.value.toLowerCase()
      return products.value.filter(p =>
        p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q) || p.sku.toLowerCase().includes(q)
      )
    })

    const getStockClass = (stock) => stock === 0 ? 'out-stock' : stock <= 30 ? 'low-stock' : 'in-stock'
    const getStockLabel = (stock) => stock === 0 ? 'Out of Stock' : stock <= 30 ? 'Low Stock' : 'In Stock'

    const openAddModal = () => {
      editingProduct.value = null
      formData.value = { name: '', category: '', sku: '', price: 0, unit: 'kg', stock: 0 }
      showModal.value = true
    }

    const openEditModal = (product) => {
      editingProduct.value = product.id
      formData.value = { ...product }
      showModal.value = true
    }

    const closeModal = () => { showModal.value = false }

    const saveProduct = async () => {
      try {
        if (editingProduct.value) {
          await updateProduct(editingProduct.value, { ...formData.value })
        } else {
          await addProduct({ ...formData.value })
        }
        await reload()
        closeModal()
      } catch (error) {
        showToast(error.message || 'Failed to save product', 'warning')
      }
    }

    const openSampleModal = () => {
      sampleData.value = { productId: '', quantity: 1, recipientType: 'sample' }
      showSampleModal.value = true
    }

    const closeSampleModal = () => {
      showSampleModal.value = false
    }

    const submitSampleDistribution = async () => {
      if (!sampleData.value.productId) return
      try {
        await recordSampleDistribution(sampleData.value.productId, sampleData.value.quantity, sampleData.value.recipientType)
        await reload()
        closeSampleModal()
        showToast(`Sample distribution recorded!`)
      } catch (error) {
        showToast(error.message || 'Failed to record sample distribution', 'warning')
      }
    }

    const openPhysicalCountModal = () => {
      physicalData.value = { productId: '', physicalCount: 0 }
      showPhysicalCountModal.value = true
    }

    const closePhysicalCountModal = () => {
      showPhysicalCountModal.value = false
    }

    const submitPhysicalCount = async () => {
      if (!physicalData.value.productId) return
      try {
        const record = await recordPhysicalStock(physicalData.value.productId, physicalData.value.physicalCount)
        await reload()
        closePhysicalCountModal()
        if (record && record.variance !== 0) {
          showToast(`Mismatch detected! Variance: ${record.variance > 0 ? '+' : ''}${record.variance}`, 'warning')
        } else {
          showToast(`Physical count recorded successfully!`)
        }
      } catch (error) {
        showToast(error.message || 'Failed to record physical stock', 'warning')
      }
    }

    const showToast = (message, type = 'success') => {
      const toast = document.createElement('div')
      toast.textContent = message
      toast.style.cssText = `
        position: fixed; top: 20px; right: 20px;
        background: ${type === 'warning' ? '#ffc107' : '#6e9f3a'};
        color: ${type === 'warning' ? '#000' : '#fff'};
        padding: 12px 20px; border-radius: 8px; z-index: 1000; font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      `
      document.body.appendChild(toast)
      setTimeout(() => document.body.removeChild(toast), 3000)
    }

    return { 
      products, searchQuery, filteredProducts, showModal, editingProduct, formData, 
      showSampleModal, sampleData, showPhysicalCountModal, physicalData,
      getStockClass, getStockLabel, openAddModal, openEditModal, closeModal, saveProduct,
      openSampleModal, closeSampleModal, submitSampleDistribution,
      openPhysicalCountModal, closePhysicalCountModal, submitPhysicalCount
    }
  }
}
</script>

<style scoped>
.inventory { padding: 30px; color: var(--text-primary); }
.inventory h1 { margin: 0; }
.inventory-actions { display: flex; gap: 18px; margin-bottom: 30px; align-items: center; flex-wrap: wrap; }
.btn { padding: 10px 22px; border-radius: 30px; border: none; font-weight: 500; letter-spacing: 0.5px; cursor: pointer; transition: all 0.4s ease; position: relative; overflow: hidden; }
.btn-primary { background: linear-gradient(135deg, #b88a2a, #7a9f2f); color: white; box-shadow: 0 4px 15px rgba(180, 140, 40, 0.3); }
.btn-primary:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(180, 140, 40, 0.5); background: linear-gradient(135deg, #d4a937, #9acd32); }
.btn-secondary { background: var(--bg-secondary); color: var(--text-primary); border: 1.5px solid var(--border-accent); }
.btn-secondary:hover { background: var(--bg-card-hover); }
.btn-sm { padding: 6px 14px; font-size: 0.8rem; border-radius: 20px; background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border-accent); }
.btn-sm:hover { background: var(--bg-card-hover); transform: translateY(-2px); box-shadow: var(--shadow-main); }
.search-input { padding: 10px 16px; border-radius: 25px; border: 1px solid var(--border-input); background: var(--bg-input); color: var(--text-primary); flex: 1; max-width: 320px; transition: all 0.3s ease; }
.search-input:focus { outline: none; border-color: var(--accent-gold); box-shadow: var(--shadow-glow); }
.inventory-table { border-radius: 18px; overflow: hidden; background: var(--bg-card); border: 1px solid var(--border-accent); box-shadow: var(--shadow-main); }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 16px; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; background: var(--bg-secondary); color: var(--text-secondary); }
td { padding: 16px; border-bottom: 1px solid var(--border-subtle); font-size: 0.95rem; color: var(--text-primary); }
tbody tr { transition: all 0.2s ease; }
tbody tr:hover { background: var(--bg-secondary); }
.action-cell { white-space: nowrap; }
.status { padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.5px; }
.in-stock { background: var(--status-delivered-bg); color: var(--status-delivered-text); }
.low-stock { background: var(--status-pending-bg); color: var(--status-pending-text); }
.out-stock { background: var(--status-rejected-bg); color: var(--status-rejected-text); }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: var(--bg-modal); border-radius: 12px; padding: 30px; width: 90%; max-width: 500px; border: 1px solid var(--border-accent); box-shadow: var(--shadow-main); }
.modal h3 { margin-top: 0; margin-bottom: 20px; color: var(--text-primary); }
.modal-form { display: flex; flex-direction: column; gap: 15px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 0.9rem; color: var(--text-secondary); }
.form-group input { padding: 10px; border-radius: 8px; border: 1px solid var(--border-input); background: var(--bg-input); color: var(--text-primary); outline: none; }
.form-group input:focus { border-color: rgba(180, 150, 45, 0.8); }
.modal-actions { display: flex; gap: 10px; margin-top: 10px; }
</style>