<template>
  <div class="performance-page">
    <div class="page-header">
      <h1>Performance</h1>
      <div class="header-actions">
        <div class="date-filter">
          <select v-model="selectedPeriod" @change="updatePeriod" class="period-select">
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
        </div>
        <button @click="exportReport" class="btn-primary">
          <span class="btn-icon">📊</span>
          Export Report
        </button>
      </div>
    </div>

    <!-- Key Performance Metrics -->
    <div class="metrics-grid">
      <div class="metric-card primary">
        <div class="metric-icon">💰</div>
        <div class="metric-content">
          <h3>Total Sales</h3>
          <div class="metric-value">₹{{ totalSales.toLocaleString() }}</div>
          <div class="metric-change positive">+{{ salesGrowth }}% vs last period</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-content">
          <h3>Conversion Rate</h3>
          <div class="metric-value">{{ conversionRate }}%</div>
          <div class="metric-change positive">+{{ conversionGrowth }}% vs last period</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">🎯</div>
        <div class="metric-content">
          <h3>Target Achievement</h3>
          <div class="metric-value">{{ targetAchievement }}%</div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: targetAchievement + '%' }"></div>
          </div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <h3>New Customers</h3>
          <div class="metric-value">{{ newCustomers }}</div>
          <div class="metric-change positive">+{{ customerGrowth }}% vs last period</div>
        </div>
      </div>
    </div>

    <!-- Performance Charts -->
    <div class="charts-section">
      <div class="chart-row">
        <!-- Sales Trend Chart -->
        <div class="chart-container">
          <h3>Sales Trend</h3>
          <div class="chart-wrapper">
            <svg width="100%" height="250" viewBox="0 0 400 250">
              <!-- Grid lines -->
              <g stroke="rgba(255,255,255,0.1)" stroke-width="1">
                <line x1="50" y1="30" x2="50" y2="200" />
                <line x1="50" y1="200" x2="380" y2="200" />
                <line x1="50" y1="60" x2="380" y2="60" stroke-dasharray="2,2" />
                <line x1="50" y1="100" x2="380" y2="100" stroke-dasharray="2,2" />
                <line x1="50" y1="140" x2="380" y2="140" stroke-dasharray="2,2" />
                <line x1="50" y1="180" x2="380" y2="180" stroke-dasharray="2,2" />
              </g>
              
              <!-- Y-axis labels -->
              <g fill="rgba(255,255,255,0.6)" font-size="10">
                <text x="40" y="35" text-anchor="end">100k</text>
                <text x="40" y="65" text-anchor="end">75k</text>
                <text x="40" y="105" text-anchor="end">50k</text>
                <text x="40" y="145" text-anchor="end">25k</text>
                <text x="40" y="185" text-anchor="end">0</text>
              </g>
              
              <!-- Sales line -->
              <polyline 
                fill="none" 
                stroke="#b48c28" 
                stroke-width="3"
                points="50,160 100,140 150,120 200,110 250,80 300,60 350,40 380,30"
              />
              
              <!-- Data points -->
              <g fill="#b48c28">
                <circle cx="50" cy="160" r="4" />
                <circle cx="100" cy="140" r="4" />
                <circle cx="150" cy="120" r="4" />
                <circle cx="200" cy="110" r="4" />
                <circle cx="250" cy="80" r="4" />
                <circle cx="300" cy="60" r="4" />
                <circle cx="350" cy="40" r="4" />
                <circle cx="380" cy="30" r="4" />
              </g>
              
              <!-- X-axis labels -->
              <g fill="rgba(255,255,255,0.6)" font-size="10">
                <text x="50" y="220" text-anchor="middle">Mon</text>
                <text x="100" y="220" text-anchor="middle">Tue</text>
                <text x="150" y="220" text-anchor="middle">Wed</text>
                <text x="200" y="220" text-anchor="middle">Thu</text>
                <text x="250" y="220" text-anchor="middle">Fri</text>
                <text x="300" y="220" text-anchor="middle">Sat</text>
                <text x="350" y="220" text-anchor="middle">Sun</text>
              </g>
            </svg>
          </div>
        </div>

        <!-- Product Performance -->
        <div class="chart-container">
          <h3>Product Performance</h3>
          <div class="product-list">
            <div v-for="product in productPerformance" :key="product.name" class="product-item">
              <div class="product-info">
                <span class="product-name">{{ product.name }}</span>
                <span class="product-sales">₹{{ product.sales.toLocaleString() }}</span>
              </div>
              <div class="product-bar">
                <div class="product-fill" :style="{ width: product.percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <!-- Customer Segments -->
        <div class="chart-container">
          <h3>Customer Segments</h3>
          <div class="segment-chart">
            <svg width="100%" height="200" viewBox="0 0 300 200">
              <!-- Pie chart -->
              <circle cx="100" cy="100" r="70" fill="none" stroke="#b48c28" stroke-width="40" 
                      stroke-dasharray="219.9" stroke-dashoffset="0" />
              <circle cx="100" cy="100" r="70" fill="none" stroke="#6e9f3a" stroke-width="40" 
                      stroke-dasharray="131.9" stroke-dashoffset="-219.9" />
              <circle cx="100" cy="100" r="70" fill="none" stroke="#d4a937" stroke-width="40" 
                      stroke-dasharray="87.9" stroke-dashoffset="-351.8" />
            </svg>
            <div class="segment-legend">
              <div v-for="segment in customerSegments" :key="segment.name" class="legend-item">
                <span class="legend-color" :style="{ backgroundColor: segment.color }"></span>
                <span class="legend-label">{{ segment.name }} ({{ segment.percentage }}%)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Timeline -->
        <div class="chart-container">
          <h3>Recent Activity</h3>
          <div class="activity-timeline">
            <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="activity.type">{{ activity.icon }}</div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-desc">{{ activity.description }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Performance Table -->
    <div class="table-section">
      <h3>Performance Details</h3>
      <div class="table-container">
        <table class="performance-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Current Period</th>
              <th>Previous Period</th>
              <th>Change</th>
              <th>Target</th>
              <th>Achievement</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="metric in performanceMetrics" :key="metric.name">
              <td>{{ metric.name }}</td>
              <td class="metric-current">{{ metric.current }}</td>
              <td class="metric-previous">{{ metric.previous }}</td>
              <td :class="['metric-change', metric.changeClass]">{{ metric.change }}</td>
              <td>{{ metric.target }}</td>
              <td>
                <div class="achievement-bar">
                  <div class="achievement-fill" :style="{ width: metric.achievement + '%' }"></div>
                  <span class="achievement-text">{{ metric.achievement }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'Performance',
  setup() {
    const selectedPeriod = ref('month')
    
    // Performance data
    const totalSales = ref(2850000)
    const salesGrowth = ref(18)
    const conversionRate = ref(24)
    const conversionGrowth = ref(12)
    const targetAchievement = ref(78)
    const newCustomers = ref(15)
    const customerGrowth = ref(25)

    const productPerformance = ref([
      { name: 'Product A', sales: 850000, percentage: 30 },
      { name: 'Product B', sales: 710000, percentage: 25 },
      { name: 'Product C', sales: 570000, percentage: 20 },
      { name: 'Product D', sales: 420000, percentage: 15 },
      { name: 'Product E', sales: 300000, percentage: 10 }
    ])

    const customerSegments = ref([
      { name: 'Enterprise', percentage: 45, color: '#b48c28' },
      { name: 'Medium Business', percentage: 27, color: '#6e9f3a' },
      { name: 'Small Business', percentage: 18, color: '#d4a937' },
      { name: 'Individual', percentage: 10, color: '#7a9f2f' }
    ])

    const recentActivity = ref([
      { id: 1, type: 'sale', icon: '💰', title: 'New Sale', description: 'Sold Product A to Retail Corp A', time: '2 hours ago' },
      { id: 3, type: 'customer', icon: '👥', title: 'New Customer', description: 'Mart C onboarded as new customer', time: '6 hours ago' },
      { id: 4, type: 'target', icon: '🎯', title: 'Target Achieved', description: 'Monthly sales target 78% completed', time: '1 day ago' },
      { id: 5, type: 'meeting', icon: '🤝', title: 'Meeting Completed', description: 'Product demo with Store D', time: '2 days ago' }
    ])

    const performanceMetrics = ref([
      { 
        name: 'Revenue', 
        current: '₹2.85M', 
        previous: '₹2.42M', 
        change: '+18%', 
        changeClass: 'positive',
        target: '₹3.0M',
        achievement: 95
      },
      { 
        name: 'Orders', 
        current: '142', 
        previous: '125', 
        change: '+14%', 
        changeClass: 'positive',
        target: '150',
        achievement: 95
      },
      { 
        name: 'Average Order Value', 
        current: '₹20,070', 
        previous: '₹19,360', 
        change: '+4%', 
        changeClass: 'positive',
        target: '₹22,000',
        achievement: 91
      },
      { 
        name: 'Conversion Rate', 
        current: '24%', 
        previous: '22%', 
        change: '+2%', 
        changeClass: 'positive',
        target: '25%',
        achievement: 96
      },
      { 
        name: 'Customer Acquisition', 
        current: '15', 
        previous: '12', 
        change: '+25%', 
        changeClass: 'positive',
        target: '18',
        achievement: 83
      },
      { 
        name: 'Customer Retention', 
        current: '89%', 
        previous: '85%', 
        change: '+4%', 
        changeClass: 'positive',
        target: '90%',
        achievement: 99
      }
    ])

    const updatePeriod = () => {
      // In a real app, this would fetch data for the selected period
      showToast(`Data updated for ${selectedPeriod.value}`, 'info')
    }

    const exportReport = () => {
      showToast('Performance report exported successfully!', 'success')
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
      selectedPeriod,
      totalSales,
      salesGrowth,
      conversionRate,
      conversionGrowth,
      targetAchievement,
      newCustomers,
      customerGrowth,
      productPerformance,
      customerSegments,
      recentActivity,
      performanceMetrics,
      updatePeriod,
      exportReport
    }
  }
}
</script>

<style scoped>
.performance-page {
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

.date-filter {
  position: relative;
}

.period-select {
  padding: 10px 15px;
  border: 1px solid rgba(170, 140, 60, 0.3);
  border-radius: 8px;
  background: rgba(20, 24, 20, 0.5);
  color: #f5f5f5;
  outline: none;
  font-weight: 600;
  cursor: pointer;
}

.period-select:focus {
  border-color: #b48c28;
  box-shadow: 0 0 0 2px rgba(180, 140, 40, 0.2);
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

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.metric-card {
  background: linear-gradient(145deg, rgba(25, 30, 25, 0.85), rgba(18, 22, 18, 0.95));
  border: 1px solid rgba(170, 140, 60, 0.2);
  border-radius: 12px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
}

.metric-card.primary {
  border-color: rgba(180, 140, 40, 0.4);
  background: linear-gradient(145deg, rgba(35, 40, 35, 0.9), rgba(25, 30, 25, 0.98));
}

.metric-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.metric-content {
  flex: 1;
}

.metric-content h3 {
  margin: 0 0 8px 0;
  font-size: 1rem;
  color: #b5b5b5;
  font-weight: 600;
  text-transform: uppercase;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 5px;
}

.metric-change {
  font-size: 0.85rem;
  font-weight: 600;
}

.metric-change.positive {
  color: #6ecf8d;
}

.metric-change.negative {
  color: #ff6b6b;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  transition: width 0.3s ease;
}

.charts-section {
  margin-bottom: 40px;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.chart-container {
  background: linear-gradient(145deg, rgba(22, 26, 22, 0.9), rgba(15, 18, 15, 0.95));
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(170, 140, 60, 0.2);
}

.chart-container h3 {
  margin: 0 0 20px 0;
  color: #ffffff;
  font-size: 1.2rem;
}

.chart-wrapper {
  width: 100%;
  height: 250px;
}

.product-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.product-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.product-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-name {
  font-weight: 600;
  color: #ffffff;
}

.product-sales {
  color: #6e9f3a;
  font-weight: 700;
}

.product-bar {
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.product-fill {
  height: 100%;
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  transition: width 0.3s ease;
}

.segment-chart {
  display: flex;
  align-items: center;
  gap: 30px;
}

.segment-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  color: rgba(245, 245, 245, 0.9);
  font-size: 0.9rem;
}

.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 200px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.activity-icon.sale {
  background: rgba(40, 167, 69, 0.2);
}

.activity-icon.customer {
  background: rgba(0, 123, 255, 0.2);
}

.activity-icon.target {
  background: rgba(220, 53, 69, 0.2);
}

.activity-icon.meeting {
  background: rgba(23, 162, 184, 0.2);
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 2px;
}

.activity-desc {
  font-size: 0.9rem;
  color: rgba(245, 245, 245, 0.8);
  margin-bottom: 2px;
}

.activity-time {
  font-size: 0.8rem;
  color: rgba(245, 245, 245, 0.6);
}

.table-section {
  background: linear-gradient(145deg, rgba(22, 26, 22, 0.9), rgba(15, 18, 15, 0.95));
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(170, 140, 60, 0.2);
}

.table-section h3 {
  margin: 0 0 20px 0;
  color: #ffffff;
  font-size: 1.2rem;
}

.performance-table {
  width: 100%;
  border-collapse: collapse;
  color: #f5f5f5;
}

.performance-table th {
  background: rgba(180, 140, 40, 0.1);
  padding: 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.performance-table td {
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.metric-current {
  font-weight: 700;
  color: #ffffff;
}

.metric-previous {
  color: rgba(245, 245, 245, 0.7);
}

.metric-change.positive {
  color: #6ecf8d;
  font-weight: 600;
}

.metric-change.negative {
  color: #ff6b6b;
  font-weight: 600;
}

.achievement-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100px;
}

.achievement-fill {
  height: 8px;
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  border-radius: 4px;
  min-width: 10px;
}

.achievement-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(245, 245, 245, 0.9);
}

@media (max-width: 1024px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .performance-page {
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

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .metric-card {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }

  .segment-chart {
    flex-direction: column;
    text-align: center;
  }

  .table-container {
    overflow-x: auto;
  }
}
</style>
