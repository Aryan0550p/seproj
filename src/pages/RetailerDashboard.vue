<template>
  <div class="retailer-dashboard">
    <!-- Header -->
    <div class="page-header header-section">
      <div class="welcome">
        <h1>Welcome, {{ profile.name }}</h1>
        <p>Your B2B portal for catalog and orders.</p>
      </div>
      <div class="account-status">
        <div class="status-item">
          <span class="label">Credit Limit</span>
          <span class="value">{{ formatCurrency(profile.creditLimit) }}</span>
        </div>
        <div class="status-item">
          <span class="label">Available Balance</span>
          <span class="value highlight">{{ formatCurrency(profile.availableCredit) }}</span>
        </div>
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon">📦</div>
        <div class="kpi-content">
          <h3>Recent Orders</h3>
          <p class="kpi-value">{{ recentOrdersCount }}</p>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon">🚚</div>
        <div class="kpi-content">
          <h3>Pending Deliveries</h3>
          <p class="kpi-value">{{ pendingDeliveriesCount }}</p>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-content">
          <h3>Pending Outstanding</h3>
          <p class="kpi-value warning">{{ formatCurrency(outstandingBalance) }}</p>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon">⭐</div>
        <div class="kpi-content">
          <h3>Favorites</h3>
          <p class="kpi-value">{{ favorites.length }} Items</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="dashboard-tabs">
      <button @click="currentTab = 'overview'" :class="{ active: currentTab === 'overview' }">Overview</button>
      <button @click="currentTab = 'catalog'" :class="{ active: currentTab === 'catalog' }">Catalog & Ordering</button>
      <button @click="currentTab = 'orders'" :class="{ active: currentTab === 'orders' }">Orders & Invoices</button>
      <button @click="currentTab = 'profile'" :class="{ active: currentTab === 'profile' }">Account</button>
      <div class="cart-trigger" @click="currentTab = 'cart'" :class="{ active: currentTab === 'cart' }">
        🛒 Cart <span class="badge" v-if="cart.length">{{ cart.length }}</span>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="tab-content main-panel">
      
      <!-- OVERVIEW TAB -->
      <div v-if="currentTab === 'overview'" class="overview-grid">
        <div class="left-col">
          <!-- Notifications -->
          <div class="card section-card">
            <h3>Notifications & Alerts</h3>
            <div class="notification-list">
              <div v-for="note in notifications" :key="note.id" class="notification-item" :class="note.type">
                <span class="icon">{{ note.icon }}</span>
                <div class="note-text">
                  <p>{{ note.message }}</p>
                  <span class="time">{{ note.time }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Quick Favorites Reorder -->
          <div class="card section-card">
            <h3>Quick Reorder (Favorites)</h3>
            <div class="product-grid mini">
              <div v-for="item in favoriteProducts" :key="item.id" class="product-card">
                <h4>{{ item.name }}</h4>
                <p class="price">{{ formatCurrency(item.price) }} / {{ item.unit }}</p>
                <button class="btn-primary sm" @click="addToCart(item, 1)">Add to Cart</button>
              </div>
            </div>
          </div>
        </div>

        <div class="right-col">
          <!-- Active Orders Widget -->
          <div class="card section-card">
            <h3>Active Orders <button class="btn-link" @click="currentTab = 'orders'">View All</button></h3>
            <div class="mini-order-list">
              <div v-for="order in activeOrders" :key="order.id" class="mini-order">
                <div class="order-head">
                  <span class="order-id">{{ order.id }}</span>
                  <span class="status" :class="order.status.toLowerCase()">{{ order.status }}</span>
                </div>
                <div class="order-desc">
                  <span>{{ order.date }}</span>
                  <span>{{ formatCurrency(order.total) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CATALOG TAB -->
      <div v-else-if="currentTab === 'catalog'" class="catalog-view">
        <div class="catalog-header">
          <div class="search-box">
            <input v-model="searchQuery" type="text" placeholder="Search products..." />
            <span>🔍</span>
          </div>
          <div class="filters">
            <select v-model="selectedCategory">
              <option value="">All Categories</option>
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
            <label class="stock-filter">
              <input type="checkbox" v-model="inStockOnly" /> In Stock Only
            </label>
          </div>
        </div>

        <div class="product-grid layout-grid">
          <div v-for="product in filteredProducts" :key="product.id" class="product-card full">
            <div class="card-head">
              <h4>{{ product.name }}</h4>
              <button class="btn-icon" @click="toggleFavorite(product.id)">
                {{ favorites.includes(product.id) ? '⭐' : '☆' }}
              </button>
            </div>
            <p class="category">{{ product.category }}</p>
            <div class="stock-info" :class="{ 'in-stock': product.stock > 0, 'out-stock': product.stock === 0 }">
               {{ product.stock > 0 ? `${product.stock} in stock` : 'Out of Stock' }}
            </div>
            <p class="price">{{ formatCurrency(product.price) }} <span>/ {{ product.unit }}</span></p>
            
            <div class="add-action" v-if="product.stock > 0">
              <input type="number" v-model.number="product.qty" min="1" :max="product.stock" class="qty-input" />
              <button class="btn-primary" @click="addToCart(product, product.qty)">Add</button>
            </div>
            <div v-else class="add-action out">
              <button class="btn-secondary disabled" disabled>Unavailable</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ORDERS & INVOICES TAB -->
      <div v-else-if="currentTab === 'orders'" class="orders-view">
        <div class="tabs-sub">
          <button @click="subTabOrders = 'orders'" :class="{ active: subTabOrders === 'orders' }">My Orders</button>
          <button @click="subTabOrders = 'invoices'" :class="{ active: subTabOrders === 'invoices' }">Invoices & Payments</button>
        </div>

        <div v-if="subTabOrders === 'orders'" class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Date</th>
                <th>Total</th>
                <th>Estimated Delivery</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in ordersList" :key="order.id">
                <td>{{ order.id }}</td>
                <td>{{ order.date }}</td>
                <td>{{ formatCurrency(order.total) }}</td>
                <td>{{ order.delivery }}</td>
                <td><span class="status" :class="order.status.toLowerCase()">{{ order.status }}</span></td>
                <td>
                  <button class="btn-link sm" @click="trackOrder(order)">Track</button>
                  <button class="btn-link sm" @click="reorder(order)">Reorder</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Order Ref</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inv in invoices" :key="inv.id">
                <td>{{ inv.id }}</td>
                <td>{{ inv.orderId }}</td>
                <td>{{ inv.date }}</td>
                <td>{{ formatCurrency(inv.amount) }}</td>
                <td><span class="status" :class="inv.status.toLowerCase()">{{ inv.status }}</span></td>
                <td>
                  <button class="btn-link sm" @click="downloadInvoice(inv)">Download PDF</button>
                  <button v-if="inv.status === 'Unpaid'" class="btn-primary sm" @click="payInvoice(inv)">Pay Now</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- CART TAB -->
      <div v-else-if="currentTab === 'cart'" class="cart-view">
        <div class="grid-cart">
          <div class="card section-card cart-items">
            <h3>Shopping Cart</h3>
            <div v-if="cart.length === 0" class="empty-state">
              <p>Your cart is empty.</p>
              <button class="btn-secondary" @click="currentTab = 'catalog'">Browse Catalog</button>
            </div>
            <div v-else class="cart-list">
              <div v-for="(item, index) in cart" :key="index" class="cart-item">
                <div class="ci-info">
                  <h4>{{ item.product.name }}</h4>
                  <p>{{ formatCurrency(item.product.price) }} / {{ item.product.unit }}</p>
                </div>
                <div class="ci-actions">
                  <input type="number" v-model.number="item.qty" min="1" @change="updateCartQty(index, item.qty)" />
                  <span class="ci-total">{{ formatCurrency(item.product.price * item.qty) }}</span>
                  <button class="btn-icon danger" @click="removeFromCart(index)">🗑️</button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card section-card cart-summary" v-if="cart.length > 0">
            <h3>Order Summary</h3>
            <div class="summary-line">
              <span>Subtotal</span>
              <span>{{ formatCurrency(cartSubtotal) }}</span>
            </div>
            <div class="summary-line">
              <span>Tax (5%)</span>
              <span>{{ formatCurrency(cartTax) }}</span>
            </div>
            <div class="summary-line total">
              <span>Total</span>
              <span>{{ formatCurrency(cartTotal) }}</span>
            </div>
            <button class="btn-primary w-full checkout-btn" @click="checkout">Proceed to Checkout</button>
          </div>
        </div>
      </div>

      <!-- PROFILE TAB -->
      <div v-else-if="currentTab === 'profile'" class="profile-view">
        <div class="grid-2">
          <div class="card section-card">
            <h3>Business Profile</h3>
            <div class="profile-details">
              <div class="p-row"><strong>Business Name:</strong> {{ profile.name }}</div>
              <div class="p-row"><strong>Contact Person:</strong> {{ profile.contact }}</div>
              <div class="p-row"><strong>Email:</strong> {{ profile.email }}</div>
              <div class="p-row"><strong>Phone:</strong> {{ profile.phone }}</div>
              <div class="p-row"><strong>GSTIN:</strong> {{ profile.gstin }}</div>
              <div class="p-row"><strong>Shipping Address:</strong><br>{{ profile.address }}</div>
            </div>
            <button class="btn-secondary mt-15">Request Profile Update</button>
          </div>
          
          <div class="card section-card">
            <h3>Support & Documents</h3>
            <div class="support-links">
              <button class="btn-outline w-full text-left">📄 Download NDA / Contracts</button>
              <button class="btn-outline w-full text-left">📄 Compliance Certificates</button>
              <button class="btn-outline w-full text-left">🎫 Open Support Ticket</button>
              <button class="btn-outline w-full text-left">📞 Contact Account Manager</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { getProducts, getOrders, addOrder } from '../store';
import { getUser } from '../auth';

export default {
  name: 'RetailerDashboard',
  setup() {
    const currentTab = ref('overview');
    const subTabOrders = ref('orders');
    const currentUser = getUser();

    const storeProducts = ref([]);
    const storeOrders = ref([]);
    const favorites = ref(['P001', 'P005']);
    const cart = ref([]);

    const reload = async () => {
      storeProducts.value = await getProducts();
      const allOrders = await getOrders();
      // Filter orders for the current retailer
      storeOrders.value = allOrders.filter(o => o.customer === currentUser?.username || o.createdBy === currentUser?.username);
    };

    onMounted(() => { reload(); });

    const profile = ref({
      name: currentUser?.username || 'Retailer',
      contact: 'Business Contact',
      email: `${currentUser?.username}@example.com`,
      phone: '+91 9876543210',
      gstin: '27AAAAA0000A1Z5',
      address: 'Business Address, India',
      creditLimit: 500000,
      availableCredit: 325000
    });

    const products = computed(() => storeProducts.value.map(p => ({ ...p, qty: 1 })));
    const categories = computed(() => [...new Set(storeProducts.value.map(p => p.category))]);
    
    const ordersList = computed(() => storeOrders.value.map(o => ({
      id: o.id,
      date: o.date,
      total: o.total,
      delivery: o.deliveryDate || 'TBD',
      status: o.status
    })));

    const invoices = ref([
      { id: 'INV-105', orderId: 'ORD-1009', date: '2026-03-15', amount: 12500, status: 'Unpaid' },
    ]);

    const notifications = ref([
      { id: 1, type: 'info', icon: '📦', message: 'Welcome to your new B2B portal.', time: 'Just now' }
    ]);

    // FILTERS & FORMS
    const searchQuery = ref('');
    const selectedCategory = ref('');
    const inStockOnly = ref(false);

    // COMPUTED
    const outstandingBalance = computed(() => invoices.value.filter(i => i.status === 'Unpaid').reduce((sum, i) => sum + i.amount, 0));
    const recentOrdersCount = computed(() => ordersList.value.length);
    const pendingDeliveriesCount = computed(() => ordersList.value.filter(o => o.status === 'Pending' || o.status === 'Shipped').length);
    const activeOrders = computed(() => ordersList.value.filter(o => o.status !== 'Delivered'));
    const favoriteProducts = computed(() => products.value.filter(p => favorites.value.includes(p.id)));

    const filteredProducts = computed(() => {
      let result = products.value;
      if (searchQuery.value) {
        result = result.filter(p => p.name.toLowerCase().includes(searchQuery.value.toLowerCase()));
      }
      if (selectedCategory.value) {
        result = result.filter(p => p.category === selectedCategory.value);
      }
      if (inStockOnly.value) {
        result = result.filter(p => p.stock > 0);
      }
      return result;
    });

    const cartSubtotal = computed(() => cart.value.reduce((sum, item) => sum + (item.product.price * item.qty), 0));
    const cartTax = computed(() => cartSubtotal.value * 0.05);
    const cartTotal = computed(() => cartSubtotal.value + cartTax.value);

    // METHODS
    const formatCurrency = (val) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(val);

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

    const toggleFavorite = (id) => {
      if (favorites.value.includes(id)) {
        favorites.value = favorites.value.filter(f => f !== id);
      } else {
        favorites.value.push(id);
      }
    };

    const addToCart = (product, qty) => {
      if (qty <= 0) return;
      const existing = cart.value.find(c => c.product.id === product.id);
      if (existing) {
        existing.qty += qty;
      } else {
        cart.value.push({ product, qty });
      }
      showToast(`Added ${qty} of ${product.name} to cart.`);
    };

    const updateCartQty = (index, qty) => {
      if (qty < 1) cart.value[index].qty = 1;
    };

    const removeFromCart = (index) => {
      cart.value.splice(index, 1);
    };

    const checkout = async () => {
      if(cartTotal.value > profile.value.availableCredit) {
        alert("Transaction exceeds available credit balance.");
        return;
      }
      profile.value.availableCredit -= cartTotal.value;
      await addOrder({
        customer: currentUser?.username || 'Retailer',
        createdBy: currentUser?.username || 'retailer',
        items: cart.value.map(item => ({
          productId: item.product.id,
          name: item.product.name,
          qty: item.qty,
          price: item.product.price
        })),
        total: cartTotal.value,
        status: 'Pending',
        payment: 'Unpaid',
        deliveryDate: 'TBD'
      });
      cart.value = [];
      showToast('Order placed successfully!');
      await reload();
      currentTab.value = 'orders';
    };

    const trackOrder = (order) => alert(`Tracking info for ${order.id}...`);
    const reorder = (order) => {
      showToast(`Mock reordering functionality for ${order.id} executed.`);
    };
    const downloadInvoice = (inv) => showToast(`Downloading PDF for ${inv.id}...`);
    const payInvoice = (inv) => {
       inv.status = 'Paid';
       showToast(`Payment processed for ${inv.id} via Mock Gateway.`);
    }

    return {
      currentTab, subTabOrders, profile, products, categories, favorites, ordersList, invoices, notifications, cart,
      searchQuery, selectedCategory, inStockOnly,
      outstandingBalance, recentOrdersCount, pendingDeliveriesCount, activeOrders, favoriteProducts, filteredProducts,
      cartSubtotal, cartTax, cartTotal,
      formatCurrency, toggleFavorite, addToCart, updateCartQty, removeFromCart, checkout,
      trackOrder, reorder, downloadInvoice, payInvoice
    };
  }
};
</script>

<style scoped>
.retailer-dashboard {
  color: var(--text-primary);
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: var(--bg-card);
  padding: 24px;
  border-radius: 12px;
  border: 1px solid var(--border-accent);
  box-shadow: var(--shadow-main);
}
.welcome h1 { margin: 0 0 5px; font-size: 1.8rem; }
.welcome p { margin: 0; color: var(--text-secondary); }
.account-status { display: flex; gap: 30px; }
.status-item { display: flex; flex-direction: column; align-items: flex-end; }
.status-item .label { font-size: 0.85rem; color: var(--text-dim); text-transform: uppercase; }
.status-item .value { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); }
.status-item .value.highlight { color: var(--accent-gold); font-size: 1.4rem; }

/* KPI Grid */
.kpi-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px;
}
.kpi-card {
  display: flex; align-items: center; gap: 15px;
  background: var(--bg-card); padding: 20px; border-radius: 12px;
  border: 1px solid var(--border-accent);
  box-shadow: var(--shadow-main);
}
.kpi-icon { font-size: 2.2rem; }
.kpi-content h3 { margin: 0 0 5px; font-size: 0.9rem; color: var(--text-secondary); }
.kpi-value { margin: 0; font-size: 1.6rem; font-weight: 700; color: var(--text-primary); }
.kpi-value.warning { color: var(--status-rejected-text); }

/* Tabs */
.dashboard-tabs {
  display: flex; gap: 10px; border-bottom: 1px solid var(--border-subtle); margin-bottom: 20px; overflow-x: auto; padding-bottom: 5px;
}
.dashboard-tabs button, .cart-trigger {
  background: none; border: none; color: var(--text-secondary); padding: 12px 20px; font-size: 1rem; font-weight: 600;
  cursor: pointer; border-bottom: 3px solid transparent; transition: all 0.2s; white-space: nowrap;
}
.dashboard-tabs button:hover, .cart-trigger:hover { color: var(--text-primary); }
.dashboard-tabs button.active, .cart-trigger.active { color: var(--accent-gold); border-bottom-color: var(--accent-gold); }
.cart-trigger { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.badge { background: #ff4757; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; }

/* General Layouts */
.card { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-accent); padding: 20px; box-shadow: var(--shadow-main); }
.card h3 { margin-top: 0; border-bottom: 1px solid var(--border-subtle); padding-bottom: 10px; margin-bottom: 15px; color: var(--text-primary); }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

/* Overview */
.overview-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
.left-col, .right-col { display: flex; flex-direction: column; gap: 20px; }

/* Notifications */
.notification-item { display: flex; gap: 12px; align-items: flex-start; padding: 12px; border-radius: 8px; background: var(--bg-secondary); margin-bottom: 10px; }
.notification-item.info { border-left: 3px solid var(--status-shipped-text); }
.notification-item.warning { border-left: 3px solid var(--status-pending-text); }
.notification-item.success { border-left: 3px solid var(--status-delivered-text); }
.note-text p { margin: 0 0 4px; font-size: 0.95rem; color: var(--text-primary); }
.note-text .time { font-size: 0.75rem; color: var(--text-dim); }

/* Catalog */
.catalog-header { display: flex; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }
.search-box { position: relative; width: 300px; }
.search-box input { width: 100%; padding: 10px 35px 10px 15px; border-radius: 8px; border: 1px solid var(--border-input); background: var(--bg-input); color: var(--text-primary); }
.search-box span { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); }
.filters { display: flex; gap: 15px; align-items: center; }
.filters select { padding: 10px; border-radius: 8px; background: var(--bg-input); color: var(--text-primary); border: 1px solid var(--border-input); }
.layout-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }
.product-card { background: var(--bg-secondary); padding: 15px; border-radius: 12px; border: 1px solid var(--border-subtle); }
.card-head { display: flex; justify-content: space-between; align-items: flex-start; }
.card-head h4 { margin: 0; font-size: 1.1rem; color: var(--text-primary); }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 1.2rem; color: var(--accent-gold); }
.category { font-size: 0.8rem; color: var(--text-dim); margin: 5px 0 10px; }
.stock-info { font-size: 0.85rem; margin-bottom: 10px; }
.stock-info.in-stock { color: var(--status-delivered-text); }
.stock-info.out-stock { color: var(--status-rejected-text); }
.price { font-size: 1.2rem; font-weight: 700; color: var(--accent-gold); margin-bottom: 15px; }
.price span { font-size: 0.85rem; color: var(--text-dim); font-weight: normal; }
.add-action { display: flex; gap: 10px; }
.qty-input { width: 60px; padding: 8px; border-radius: 6px; border: 1px solid var(--border-input); background: var(--bg-input); color: var(--text-primary); text-align: center; }

/* Tables */
.tabs-sub { display: flex; gap: 15px; margin-bottom: 20px; }
.tabs-sub button { background: none; border: 1px solid var(--border-accent); color: var(--text-secondary); padding: 6px 15px; border-radius: 6px; cursor: pointer; }
.tabs-sub button.active { background: var(--accent-gold); color: #111; border-color: var(--accent-gold); font-weight: 600; }
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--border-subtle); color: var(--text-primary); }
.data-table th { background: var(--bg-secondary); color: var(--text-secondary); font-weight: 600; }

.status { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
.status.pending, .status.unpaid { background: var(--status-pending-bg); color: var(--status-pending-text); }
.status.shipped { background: var(--status-shipped-bg); color: var(--status-shipped-text); }
.status.delivered, .status.paid { background: var(--status-delivered-bg); color: var(--status-delivered-text); }

/* Cart */
.grid-cart { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
.cart-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid var(--border-subtle); color: var(--text-primary); }
.ci-info h4 { margin: 0 0 5px; }
.ci-info p { margin: 0; color: var(--text-secondary); font-size: 0.9rem; }
.ci-actions { display: flex; align-items: center; gap: 15px; }
.ci-actions input { width: 60px; padding: 6px; text-align: center; border-radius: 4px; border: 1px solid var(--border-input); background: var(--bg-input); color: var(--text-primary); }
.ci-total { font-weight: 700; width: 100px; text-align: right; }
.summary-line { display: flex; justify-content: space-between; margin-bottom: 15px; color: var(--text-secondary); }
.summary-line.total { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); border-top: 1px solid var(--border-subtle); padding-top: 15px; }
.checkout-btn { padding: 15px; font-size: 1.1rem; margin-top: 20px; }

/* Profile */
.profile-details { margin-bottom: 20px; color: var(--text-primary); }
.p-row { margin-bottom: 12px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px; }
.support-links button { margin-bottom: 10px; padding: 12px 15px; border-color: var(--border-accent); }

/* Buttons */
.btn-primary { background: linear-gradient(90deg, var(--accent-gold), var(--accent-green)); border: none; color: #111; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; }
.btn-secondary { background: var(--bg-secondary); border: 1px solid var(--border-accent); color: var(--text-primary); padding: 8px 16px; border-radius: 6px; cursor: pointer; }
.btn-link { background: none; border: none; color: var(--accent-gold); cursor: pointer; }
.btn-link:hover { text-decoration: underline; }
.btn-outline { background: transparent; border: 1px solid var(--border-accent); color: var(--text-secondary); border-radius: 6px; cursor: pointer; }
.btn-outline:hover { background: var(--bg-secondary); color: var(--text-primary); }
.sm { padding: 4px 10px; font-size: 0.85rem; }
.w-full { width: 100%; }
.text-left { text-align: left; }
.btn-icon.danger { color: #ff4757; }
.mt-15 { margin-top: 15px; }

@media (max-width: 900px) {
  .overview-grid, .grid-2, .grid-cart { grid-template-columns: 1fr; }
  .dashboard-tabs { overflow-x: auto; }
}
</style>

