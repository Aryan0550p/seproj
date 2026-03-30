<template>
  <div class="dashboard">
    <div class="page-header dashboard-header">
      <h1>Dashboard</h1>
      <button @click="isUserModalOpen = true" class="btn-user-mgmt">👥 User Management</button>
    </div>

    <div class="dashboard-grid">
      <div class="card">
        <div class="card-icon">📦</div>
        <h3>Total Orders</h3>
        <p class="metric">{{ totalOrders }}</p>
        <span class="trend positive">Live data</span>
      </div>
      <div class="card">
        <div class="card-icon">💰</div>
        <h3>Revenue</h3>
        <p class="metric">₹{{ totalRevenue.toLocaleString() }}</p>
        <span class="trend positive">From all orders</span>
      </div>
      <div class="card">
        <div class="card-icon">👥</div>
        <h3>Active Users</h3>
        <p class="metric">{{ activeUsers }}</p>
        <span class="trend neutral">System accounts</span>
      </div>
      <div class="card">
        <div class="card-icon">🚚</div>
        <h3>Pending Deliveries</h3>
        <p class="metric">{{ pendingDeliveries }}</p>
        <span class="trend neutral">Awaiting shipment</span>
      </div>
    </div>

    <div class="recent-activity">
      <h2>Recent Orders</h2>
      <ul>
        <li v-for="order in recentOrders" :key="order.id">
          <span class="activity-icon">🛒</span>
          <strong>{{ order.id }}</strong> – {{ order.customer }} – ₹{{ order.total.toLocaleString() }}
          <span class="status-badge" :class="order.status.toLowerCase()">{{ order.status }}</span>
        </li>
        <li v-if="recentOrders.length === 0">No orders yet.</li>
      </ul>
    </div>

    <!-- User Management Modal -->
    <div v-if="isUserModalOpen" class="modal-overlay" @click.self="isUserModalOpen = false">
      <div class="user-management-modal">
        <div class="modal-header">
          <h2>User Management</h2>
          <button class="close-btn" @click="isUserModalOpen = false">&times;</button>
        </div>
        <div class="create-user-card">
          <h3>Create New User</h3>
          <form @submit.prevent="handleCreateUser" class="create-user-form">
            <div class="form-group">
              <label>Username</label>
              <input v-model="newUser.username" type="text" required placeholder="Enter username" />
            </div>
            <div class="form-group">
              <label>Password</label>
              <input v-model="newUser.password" type="password" required placeholder="Enter password" />
            </div>
            <div class="form-group">
              <label>Role</label>
              <select v-model="newUser.role" required>
                <option value="" disabled>Select Role</option>
                <option value="salesman">Salesman</option>
                <option value="retailer">Retailer (Wholeseller)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Email</label>
              <input v-model="newUser.email" type="email" required placeholder="Enter email" />
            </div>
            <button type="submit" class="btn-primary">Create User</button>
          </form>
          <p v-if="message" :class="['message', messageType]">{{ message }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { createUser, getAllUsers } from '../auth'
import { getOrders } from '../store'

export default {
  name: 'Dashboard',
  setup() {
    const newUser = ref({ username: '', password: '', role: '', email: '' })
    const isUserModalOpen = ref(false)
    const message = ref('')
    const messageType = ref('')
    const orders = ref([])
    const users = ref([])

    onMounted(() => {
      orders.value = getOrders()
      users.value = getAllUsers()
    })

    const totalOrders = computed(() => orders.value.length)
    const totalRevenue = computed(() => orders.value.reduce((sum, o) => sum + (o.total || 0), 0))
    const activeUsers = computed(() => users.value.length)
    const pendingDeliveries = computed(() => orders.value.filter(o => o.status === 'Pending' || o.status === 'Shipped').length)
    const recentOrders = computed(() => orders.value.slice(0, 5))

    const handleCreateUser = () => {
      const result = createUser({ ...newUser.value })
      message.value = result.message
      messageType.value = result.success ? 'success' : 'error'
      if (result.success) {
        newUser.value = { username: '', password: '', role: '', email: '' }
        users.value = getAllUsers()
        setTimeout(() => { 
          isUserModalOpen.value = false
          message.value = ''
        }, 1500)
      } else {
        setTimeout(() => { message.value = '' }, 4000)
      }
    }

    return { newUser, isUserModalOpen, message, messageType, handleCreateUser, totalOrders, totalRevenue, activeUsers, pendingDeliveries, recentOrders }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 30px;
  color: var(--text-primary);
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  margin-bottom: 0;
}

.btn-user-mgmt {
  background: rgba(180, 140, 40, 0.15);
  border: 1.5px solid var(--accent-gold);
  color: var(--accent-gold);
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-user-mgmt:hover {
  background: var(--accent-gold);
  color: #111;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(180, 140, 40, 0.3);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.card {
  position: relative;
  padding: 24px;
  border-radius: 18px;
  background: var(--bg-card);
  border: 1px solid var(--border-accent);
  box-shadow: var(--shadow-main);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), 0 0 25px rgba(200, 160, 70, 0.15);
}

.card::before {
  content: "";
  position: absolute;
  top: 0; left: 0;
  height: 4px; width: 100%;
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  opacity: 0.8;
}

.card-icon { font-size: 2.2rem; position: absolute; top: 20px; right: 20px; opacity: 0.15; color: var(--text-primary); }
.card h3 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary); margin-bottom: 12px; }
.metric { font-size: 2.4rem; font-weight: 700; margin-bottom: 8px; color: var(--text-primary); }
.trend { font-size: 0.85rem; font-weight: 500; }
.trend.positive { color: var(--status-delivered-text); }
.trend.negative { color: var(--status-rejected-text); }
.trend.neutral { color: var(--text-dim); }

.recent-activity {
  padding: 28px; border-radius: 18px;
  background: var(--bg-card);
  border: 1px solid var(--border-accent);
  box-shadow: var(--shadow-main);
}

.recent-activity h2 { margin-bottom: 20px; font-weight: 600; letter-spacing: 1px; font-size: 1.3rem; }
.recent-activity ul { list-style: none; padding: 0; }
.recent-activity li { display: flex; align-items: center; gap: 10px; padding: 12px 0; border-bottom: 1px solid var(--border-subtle); transition: all 0.2s ease; }
.recent-activity li:hover { padding-left: 8px; color: var(--text-primary); }
.activity-icon { margin-right: 8px; font-size: 1.1rem; opacity: 0.7; }
.recent-activity li:last-child { border-bottom: none; }
.status-badge { padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-left: auto; }
.status-badge.pending { background: var(--status-pending-bg); color: var(--status-pending-text); }
.status-badge.shipped { background: var(--status-shipped-bg); color: var(--status-shipped-text); }
.status-badge.delivered { background: var(--status-delivered-bg); color: var(--status-delivered-text); }

/* Modal Styles */
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.3s ease; }
.user-management-modal { background: var(--bg-modal); border: 1px solid var(--border-accent); border-radius: 20px; width: 90%; max-width: 900px; padding: 30px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: scaleIn 0.3s ease; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.modal-header h2 { font-size: 1.5rem; margin: 0; color: var(--text-primary); letter-spacing: 1px; }
.close-btn { background: none; border: none; color: var(--text-secondary); font-size: 2rem; cursor: pointer; transition: color 0.2s; }
.close-btn:hover { color: var(--accent-gold); }

.create-user-card { background: var(--bg-secondary); border-radius: 12px; padding: 24px; }
.create-user-card h3 { margin-top: 0; margin-bottom: 16px; font-size: 1.1rem; color: var(--text-secondary); }
.create-user-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; align-items: end; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 0.9rem; color: var(--text-secondary); }
.form-group input, .form-group select { padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border-input); background: var(--bg-input); color: var(--text-primary); font-size: 1rem; outline: none; }
.form-group input:focus, .form-group select:focus { border-color: var(--accent-gold); }
.btn-primary { grid-column: 1 / -1; padding: 12px 24px; border-radius: 10px; border: none; font-weight: 600; font-size: 1rem; cursor: pointer; background: linear-gradient(90deg, #b48c28, #6e9f3a); color: #111; transition: transform 0.2s ease, box-shadow 0.2s ease; height: 44px; margin-top: 10px; }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(180, 140, 40, 0.3); }
.message { margin-top: 16px; padding: 12px; border-radius: 8px; font-weight: 500; text-align: center; }
.message.success { background: rgba(110, 159, 58, 0.2); color: #6ecf8d; border: 1px solid rgba(110, 159, 58, 0.4); }
.message.error { background: rgba(255, 107, 107, 0.2); color: #ff6b6b; border: 1px solid rgba(255, 107, 107, 0.4); }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>