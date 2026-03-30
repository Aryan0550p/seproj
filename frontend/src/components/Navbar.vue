<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <h1>YUMSIE</h1>
    </div>
    
    <!-- Mobile menu toggle -->
    <button class="mobile-menu-toggle" @click="toggleMobileMenu" v-if="$route.name !== 'Login'">
      ☰
    </button>
    
    <div class="navbar-links" :class="{ 'mobile-open': isMobileMenuOpen }" v-if="$route.name !== 'Login'">
      <!-- ADMIN NAVBAR -->
      <template v-if="userRole === 'admin'">
        <router-link to="/dashboard" class="nav-link" @click="closeMobileMenu">Dashboard</router-link>
        <router-link to="/inventory" class="nav-link" @click="closeMobileMenu">Inventory</router-link>
        <router-link to="/orders" class="nav-link" @click="closeMobileMenu">Orders</router-link>
        <router-link to="/payments" class="nav-link" @click="closeMobileMenu">Payments</router-link>
        <router-link to="/delivery" class="nav-link" @click="closeMobileMenu">Delivery</router-link>
        <router-link to="/reports" class="nav-link" @click="closeMobileMenu">Reports</router-link>
      </template>

      <!-- SALESMAN NAVBAR -->
      <template v-else-if="userRole === 'salesman'">
        <router-link to="/sales-dashboard" class="nav-link" @click="closeMobileMenu">My Dashboard</router-link>
        <router-link to="/customers" class="nav-link" @click="closeMobileMenu">Customers</router-link>
        <router-link to="/sales-orders" class="nav-link" @click="closeMobileMenu">Orders</router-link>
        <router-link to="/performance" class="nav-link" @click="closeMobileMenu">Performance</router-link>
      </template>

      <!-- RETAILER NAVBAR -->
      <template v-else-if="userRole === 'retailer'">
        <router-link to="/retailer-dashboard" class="nav-link" @click="closeMobileMenu">My Dashboard</router-link>
      </template>

      <!-- Action buttons -->
      <div class="nav-actions">
        <button class="theme-toggle" @click="toggleTheme" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
          {{ isDark ? '🌞' : '🌙' }}
        </button>
        <button class="logout" @click="handleLogout" title="Logout">Logout</button>
      </div>
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
      isDark: true,
      userRole: null,
      isMobileMenuOpen: false
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
    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen;
    },
    closeMobileMenu() {
      this.isMobileMenuOpen = false;
    },
    handleLogout() {
      auth.logout()
      this.$router.push({ name: 'Login' })
    },
    updateUserRole() {
      this.userRole = getUserRole()
    }
  },
  mounted() {
    this.updateUserRole()
    const saved = localStorage.getItem('theme');
    if (saved === 'light') {
      this.isDark = false;
      document.body.classList.add('light');
    }
    
    // Listen for route changes to update user role
    this.$router.afterEach(() => {
      this.updateUserRole()
    })
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (this.isMobileMenuOpen && !e.target.closest('.navbar')) {
        this.closeMobileMenu()
      }
    })
  },
  watch: {
    // Watch for auth state changes
    '$store.state.user': {
      handler() {
        this.updateUserRole()
      },
      deep: true
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
.navbar-brand h1 {
  margin: 0;
  font-size: 1.8rem;
  background: linear-gradient(90deg, #ffffff, #b48c28);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}

/* Mobile menu toggle */
.mobile-menu-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #cfcfcf;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.mobile-menu-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

/* Links Container */
.navbar-links {
  display: flex;
  align-items: center;
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

/* Nav Actions */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 20px;
}

/* Theme toggle button */
.theme-toggle {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #cfcfcf;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
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

/* Mobile */
@media (max-width: 900px) {
  .navbar {
    padding: 12px 20px;
  }

  .mobile-menu-toggle {
    display: block;
  }

  .navbar-links {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--bg-navbar);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-accent);
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    padding: 20px;
    box-shadow: var(--shadow-main);
  }

  .navbar-links.mobile-open {
    display: flex;
  }

  .nav-link {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .nav-link:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .nav-actions {
    margin-left: 0;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    justify-content: center;
  }

  .theme-toggle, .logout {
    flex: 1;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .navbar-brand h1 {
    font-size: 1.5rem;
  }
  
  .navbar {
    padding: 10px 16px;
  }
}
</style>