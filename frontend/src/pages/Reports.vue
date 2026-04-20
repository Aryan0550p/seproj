<template>
  <div class="reports">
    <div class="page-header">
      <h1>Reports & Analytics</h1>
    </div>
    <div class="report-controls">
      <select class="report-type">
        <option>Sales Report</option>
        <option>Inventory Report</option>
        <option>Customer Report</option>
        <option>Financial Report</option>
        <option>Delivery Report</option>
      </select>
      <div class="date-group">
        <label>Start Date</label>
        <input type="date" class="date-start">
      </div>
      <div class="date-group">
        <label>End Date</label>
        <input type="date" class="date-end">
      </div>
      <button class="btn btn-primary">Generate Report</button>
      <button class="btn btn-secondary">Export PDF</button>
    </div>
    
    <div class="report-summary">
      <div class="summary-grid">
        <div class="summary-item">
          <h3>Total Sales</h3>
          <p class="summary-value">₹392,350.52</p>
          <span class="trend positive">+15.3% from last period</span>
        </div>
        <div class="summary-item">
          <h3>Total Orders</h3>
          <p class="summary-value">1,456</p>
          <span class="trend positive">+8.7% from last period</span>
        </div>
        <div class="summary-item">
          <h3>Average Order Value</h3>
          <p class="summary-value">₹78,4701.04</p>
          <span class="trend negative">-2.1% from last period</span>
        </div>
        <div class="summary-item">
          <h3>Top Product</h3>
          <p class="summary-value">Premium Rice 5kg</p>
          <span class="trend neutral">234 units sold</span>
        </div>
      </div>
    </div>

    <div class="report-content">
      <div class="chart-section">
        <h2>Sales Trend</h2>
        <div class="chart-placeholder">
          <p>📊 Chart visualization will be displayed here</p>
          <p>Integration with Chart.js or similar library needed</p>
        </div>
      </div>
      
      <div class="table-section">
        <h2>Top Products by Revenue</h2>
        <table class="report-table">
          <thead>
            <tr>
              <th>Product Name</th>
              <th>Units Sold</th>
              <th>Revenue</th>
              <th>Growth %</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Premium Rice 5kg</td>
              <td>234</td>
              <td>₹91,305.00</td>
              <td class="positive">+12.5%</td>
            </tr>
            <tr>
              <td>Organic Sugar 2kg</td>
              <td>189</td>
              <td>₹82,362.50</td>
              <td class="positive">+8.3%</td>
            </tr>
            <tr>
              <td>Refined Oil 1L</td>
              <td>156</td>
              <td>₹81,365.00</td>
              <td class="negative">-3.2%</td>
            </tr>
            <tr>
              <td>Wheat Flour 10kg</td>
              <td>145</td>
              <td>₹76,083.46</td>
              <td class="positive">+5.7%</td>
            </tr>
            <tr>
              <td>Pulses Mix 2kg</td>
              <td>123</td>
              <td>₹61,234.56</td>
              <td class="positive">+10.2%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Reports'
}
</script>

<style scoped>
.reports {
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

.report-controls {
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

.report-type, .date-start, .date-end {
  padding: 10px 16px;
  border: 1px solid rgba(180, 140, 40, 0.4);
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.05);
  color: #f5f5f5;
  backdrop-filter: blur(6px);
  transition: all 0.3s ease;
}

.date-group {
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: center;
}

.date-group label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.6;
  color: #b88a2a;
  font-weight: 500;
  white-space: nowrap;
}

.report-type:focus, .date-start:focus, .date-end:focus {
  outline: none;
  border-color: #b88a2a;
  box-shadow: 0 0 10px rgba(180, 140, 40, 0.3);
}

.report-type option {
  background-color: #1b1f1b;
  color: #f5f5f5;
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
  background: rgba(255, 255, 255, 0.08);
  color: #f5f5f5;
  border: 1.5px solid rgba(180, 140, 40, 0.4);
}

.btn-secondary:hover {
  background: rgba(180, 140, 40, 0.25);
  border-color: rgba(180, 140, 40, 0.7);
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(180, 140, 40, 0.3);
}

.btn-secondary:active {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(180, 140, 40, 0.25);
}

.report-summary {
  margin-bottom: 40px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.summary-item {
  text-align: center;
  padding: 20px;
}

.summary-item h3 {
  font-size: 0.85rem;
  letter-spacing: 1px;
  opacity: 0.7;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.summary-value {
  background: linear-gradient(90deg, #d4a937, #9acd32);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0 0 5px 0;
}

.trend {
  font-size: 0.8rem;
  font-weight: 500;
}

.trend.positive {
  color: #9acd32;
}

.trend.negative {
  color: #d98060;
}

.trend.neutral {
  color: #999;
}

.report-content {
  display: grid;
  gap: 30px;
}

.chart-section, .table-section {
  padding: 20px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(180, 140, 40, 0.2);
}

.chart-section h2, .table-section h2 {
  margin-bottom: 20px;
  color: #f5f5f5;
  font-weight: 600;
}

.chart-placeholder {
  background: rgba(255, 255, 255, 0.02);
  border: 2px dashed rgba(180, 140, 40, 0.3);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  color: #999;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  color: #f5f5f5;
}

.report-table th, .report-table td {
  padding: 0.9rem;
  text-align: left;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.report-table th {
  background: rgba(180, 140, 40, 0.1);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.report-table .positive {
  color: #9acd32;
  font-weight: 500;
}

.report-table .negative {
  color: #d98060;
  font-weight: 500;
}
@media (max-width: 768px) {
  .report-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
