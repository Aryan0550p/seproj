import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../pages/Dashboard.vue'
import SalesDashboard from '../pages/SalesDashboard.vue'
import Inventory from '../pages/Inventory.vue'
import Orders from '../pages/Orders.vue'
import SalesOrders from '../pages/SalesOrders.vue'
import Payments from '../pages/Payments.vue'
import Delivery from '../pages/Delivery.vue'
import Reports from '../pages/Reports.vue'
import Customers from '../pages/Customers.vue'
import Performance from '../pages/Performance.vue'
import Login from '../pages/Login.vue'
import RetailerDashboard from '../pages/RetailerDashboard.vue'
import { isLoggedIn, getUserRole } from '../auth'

const routes = [
  {
    path: '/',
    redirect: { name: 'Login' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/sales-dashboard',
    name: 'SalesDashboard',
    component: SalesDashboard,
    meta: { requiresAuth: true, roles: ['salesman'] }
  },
  {
    path: '/retailer-dashboard',
    name: 'RetailerDashboard',
    component: RetailerDashboard,
    meta: { requiresAuth: true, roles: ['retailer'] }
  },
  {
    path: '/customers',
    name: 'Customers',
    component: Customers,
    meta: { requiresAuth: true, roles: ['salesman'] }
  },
  {
    path: '/sales-orders',
    name: 'SalesOrders',
    component: SalesOrders,
    meta: { requiresAuth: true, roles: ['salesman'] }
  },
  {
    path: '/performance',
    name: 'Performance',
    component: Performance,
    meta: { requiresAuth: true, roles: ['salesman'] }
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: Inventory,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/payments',
    name: 'Payments',
    component: Payments,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/delivery',
    name: 'Delivery',
    component: Delivery,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: {
      template: `<div style="padding: 60px; color: #f5f5f5; font-family: sans-serif;"><h1 style="font-size:2rem; margin-bottom: 18px;">Page not found</h1><p>The route you are trying to access does not exist. Try going back to <a href="/" style="color: #b48c28;">home</a>.</p></div>`
    },
    meta: { guest: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const loggedIn = isLoggedIn()
  const userRole = getUserRole()

  if (to.meta.requiresAuth && !loggedIn) {
    return next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
  }



  // Role-based access control
  if (to.meta.roles && !to.meta.roles.includes(userRole)) {
    // Redirect to appropriate dashboard
    if (userRole === 'admin') {
      return next({ name: 'Dashboard' })
    } else if (userRole === 'salesman') {
      return next({ name: 'SalesDashboard' })
    } else if (userRole === 'retailer') {
      return next({ name: 'RetailerDashboard' })
    }
  }

  next()
})

export default router
