<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <h1>YUMSIE</h1>
    </div>
    <div class="navbar-links" v-if="$route.name !== 'Login'">
      <!-- ADMIN NAVBAR -->
      <template v-if="userRole === 'admin'">
        <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
        <router-link to="/inventory" class="nav-link">Inventory</router-link>
        <router-link to="/orders" class="nav-link">Orders</router-link>
        <router-link to="/payments" class="nav-link">Payments</router-link>
        <router-link to="/delivery" class="nav-link">Delivery</router-link>
        <router-link to="/reports" class="nav-link">Reports</router-link>
      </template>

      <template v-else-if="userRole === 'salesman'">
        <router-link to="/sales-dashboard" class="nav-link">My Dashboard</router-link>
        <router-link to="/customers" class="nav-link">Customers</router-link>
        <router-link to="/sales-orders" class="nav-link">Orders</router-link>
        <router-link to="/performance" class="nav-link">Performance</router-link>
      </template>

      <!-- RETAILER NAVBAR -->
      <template v-else-if="userRole === 'retailer'">
        <router-link to="/retailer-dashboard" class="nav-link">My Dashboard</router-link>
      </template>

      <!-- theme toggle placed right -->
      <button class="theme-toggle" @click="toggleTheme">
        {{ isDark ? '🌞' : '🌙' }}
      </button>
      <button class="logout" @click="handleLogout">Logout</button>
    </div>
  </nav>
</template>

<script>
import { getUserRole } from '../auth'
import auth from '../auth'

export default {
  name: 'Navbar',
  data() {
    return {
      // true = dark mode, false = light mode
      isDark: true,
      userRole: null
    };
  },
  methods: {
    toggleTheme() {
      this.isDark = !this.isDark;
      if (this.isDark) {
        document.body.classList.remove('light');
        localStorage.setItem('theme', 'dark');
      } else {
        document.body.classList.add('light');
        localStorage.setItem('theme', 'light');
      }
    },
    handleLogout() {
      auth.logout()
      this.$router.push({ name: 'Login' })
    }
  },
  mounted() {
    this.userRole = getUserRole()
    const saved = localStorage.getItem('theme');
    if (saved === 'light') {
      this.isDark = false;
      document.body.classList.add('light');
    }
  }
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;

  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 18px 40px;

  background: var(--bg-navbar);
  backdrop-filter: blur(12px);

  border-bottom: 1px solid var(--border-accent);
  box-shadow: var(--shadow-main);
}

/* Brand */


/* Links Container */
.navbar-links {
  display: flex;
  gap: 28px;
}

/* Link Base */
.nav-link {
  position: relative;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  letter-spacing: 0.5px;

  color: #cfcfcf;
  padding: 6px 4px;

  transition: all 0.3s ease;
  background: linear-gradient(90deg, #ffffff, #b48c28);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Underline Animation */
.nav-link::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 0%;
  height: 2px;

  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  transition: width 0.3s ease;
}

.nav-link:hover {
  background: linear-gradient(90deg, #ffffff, #d4a937);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-link:hover::after {
  width: 100%;
}

/* Active Link */
.nav-link.router-link-active {
  font-weight: 600;
  background: linear-gradient(90deg, #ffffff, #d4a937);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-link.router-link-active::after {
  width: 100%;
}

/* Mobile */
@media (max-width: 900px) {
  .navbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .navbar-links {
    flex-wrap: wrap;
    gap: 16px;
  }
}

/* Theme toggle button */
.theme-toggle {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #cfcfcf;
  margin-left: 20px;
  transition: color 0.3s ease;
}

.theme-toggle:hover {
  color: #ffffff;
}

.logout {
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(170, 140, 60, 0.4);
  border-radius: 999px;
  padding: 8px 14px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.logout:hover {
  background: rgba(255, 255, 255, 0.25);
  color: rgba(255, 255, 255, 1);
  border-color: rgba(180, 150, 45, 0.6);
}
</style>