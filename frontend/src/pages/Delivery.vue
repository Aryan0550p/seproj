<template>
  <div class="delivery">
    <div class="page-header">
      <h1>Delivery & Logistics</h1>
    </div>
    <div class="delivery-stats">
      <div class="stat-card">
        <h3>Pending Deliveries</h3>
        <p class="stat-number">23</p>
      </div>
      <div class="stat-card">
        <h3>In Transit</h3>
        <p class="stat-number">15</p>
      </div>
      <div class="stat-card">
        <h3>Delivered Today</h3>
        <p class="stat-number">8</p>
      </div>
      <div class="stat-card">
        <h3>Delayed</h3>
        <p class="stat-number">3</p>
      </div>
    </div>
    <div class="delivery-actions">
      <button class="btn btn-primary">Schedule Delivery</button>
      <button class="btn btn-secondary">Assign Driver</button>
      <select class="filter-select">
        <option>All Deliveries</option>
        <option>Pending</option>
        <option>In Transit</option>
        <option>Delivered</option>
        <option>Delayed</option>
      </select>
    </div>
    <div class="delivery-list">
      <div class="delivery-card">
        <div class="delivery-header">
          <h3>Delivery #D001</h3>
          <span class="delivery-status pending">Pending</span>
        </div>
        <div class="delivery-details">
          <p><strong>Order:</strong> #1234</p>
          <p><strong>Customer:</strong> ABC Retail Store</p>
          <p><strong>Address:</strong> 123 Main St, City</p>
          <p><strong>Scheduled:</strong> 2026-03-05 10:00 AM</p>
          <p><strong>Driver:</strong> Not Assigned</p>
        </div>
        <div class="delivery-actions">
          <button class="btn btn-sm">Assign Driver</button>
          <button class="btn btn-sm">View Details</button>
        </div>
      </div>
      <div class="delivery-card">
        <div class="delivery-header">
          <h3>Delivery #D002</h3>
          <span class="delivery-status transit">In Transit</span>
        </div>
        <div class="delivery-details">
          <p><strong>Order:</strong> #1235</p>
          <p><strong>Customer:</strong> XYZ Wholesale</p>
          <p><strong>Address:</strong> 456 Oak Ave, City</p>
          <p><strong>Scheduled:</strong> 2026-03-04 2:00 PM</p>
          <p><strong>Driver:</strong> John Smith</p>
        </div>
        <div class="delivery-actions">
          <button class="btn btn-sm">Track</button>
          <button class="btn btn-sm">Contact Driver</button>
        </div>
      </div>
      <div class="delivery-card">
        <div class="delivery-header">
          <h3>Delivery #D003</h3>
          <span class="delivery-status delayed">Delayed</span>
        </div>
        <div class="delivery-details">
          <p><strong>Order:</strong> #1236</p>
          <p><strong>Customer:</strong> Local Market</p>
          <p><strong>Address:</strong> 789 Pine Rd, City</p>
          <p><strong>Scheduled:</strong> 2026-03-03 11:00 AM</p>
          <p><strong>Driver:</strong> Mike Johnson</p>
        </div>
        <div class="delivery-actions">
          <button class="btn btn-sm">Update Status</button>
          <button class="btn btn-sm">Notify Customer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Delivery'
}
</script>

<style scoped>
.delivery {
  padding: 40px;
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

.delivery-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2.5rem;
  margin-bottom: 40px;
}

.stat-card {
  padding: 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  border-radius: 18px;
  border: 1px solid rgba(180, 140, 40, 0.2);
}

.stat-card h3 {
  font-size: 0.85rem;
  letter-spacing: 1px;
  opacity: 0.7;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.stat-number {
  font-size: 2.2rem;
  font-weight: 700;
  background: linear-gradient(90deg, #d4a937, #9acd32);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.delivery-actions {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
  padding: 20px;
  align-items: center;
  flex-wrap: wrap;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  border-radius: 18px;
  border: 1px solid rgba(180, 140, 40, 0.2);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.btn-primary {
  background: linear-gradient(135deg, #b88a2a, #7a9f2f);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(180, 140, 40, 0.5), 0 0 20px rgba(200, 160, 50, 0.3);
  background: linear-gradient(135deg, #d4a937, #9acd32);
}

.btn-primary:active {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(180, 140, 40, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #f5f5f5;
  border: 1px solid rgba(180, 140, 40, 0.3);
}

.btn-secondary:hover {
  background: rgba(180, 140, 40, 0.15);
}

.btn-sm {
  padding: 6px 14px;
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.08);
  color: #f5f5f5;
  border: 1px solid rgba(180, 140, 40, 0.4);
}

.btn-sm:hover {
  background: rgba(180, 140, 40, 0.35);
  border-color: rgba(180, 140, 40, 0.7);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(180, 140, 40, 0.3);
}

.btn-sm:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(180, 140, 40, 0.25);
}

.filter-select {
  padding: 10px 16px;
  border: 1px solid rgba(180, 140, 40, 0.4);
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.05);
  color: #f5f5f5;
  backdrop-filter: blur(6px);
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.filter-select option {
  background-color: #1b1f1b;
  color: #f5f5f5;
  padding: 10px;
}

.filter-select:focus {
  outline: none;
  border-color: #b88a2a;
  box-shadow: 0 0 10px rgba(180, 140, 40, 0.3);
}

.delivery-list {
  display: grid;
  gap: 3rem;
}

.delivery-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  border-radius: 18px;
  padding: 25px;
  border: 1px solid rgba(180, 140, 40, 0.2);
  border-top: 2px solid rgba(180, 140, 40, 0.3);
}

.delivery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(180, 140, 40, 0.1);
}

.delivery-header h3 {
  margin: 0;
  color: #f5f5f5;
  font-weight: 600;
}

.delivery-status {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.pending {
  background: rgba(213, 130, 24, 0.15);
  color: #d4a937;
  border: 1px solid rgba(180, 140, 40, 0.4);
}

.transit {
  background: rgba(180, 140, 40, 0.15);
  color: #d4a937;
  border: 1px solid rgba(180, 140, 40, 0.4);
}

.delivered {
  background: rgba(122, 159, 47, 0.15);
  color: #9acd32;
  border: 1px solid rgba(122, 159, 47, 0.4);
}

.delayed {
  background: rgba(180, 100, 60, 0.15);
  color: #d98060;
  border: 1px solid rgba(180, 100, 60, 0.4);
}

.delivery-details {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(180, 140, 40, 0.1);
}

.delivery-details p {
  margin: 8px 0;
  opacity: 0.85;
  font-size: 0.95rem;
  line-height: 1.6;
}
</style>
