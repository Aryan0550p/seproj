import { reactive } from 'vue'

const STORAGE_KEY = 'yumsie_auth_user'

const DB_USERS_KEY = 'yumsie_db_users'

// Pre-defined users (cannot be created via UI)
const USERS = [
  { username: 'admin', password: 'admin123', role: 'admin' }
]

const state = reactive({
  user: null
})

export function initAuth() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    try {
      state.user = JSON.parse(saved)
    } catch {
      state.user = null
    }
  }
}

export function isLoggedIn() {
  return !!state.user
}

export function getUser() {
  return state.user
}

export function getUserRole() {
  return state.user?.role || null
}

export function getAllUsers() {
  const saved = localStorage.getItem(DB_USERS_KEY)
  let dynamicUsers = []
  if (saved) {
    try {
      dynamicUsers = JSON.parse(saved)
    } catch {
      dynamicUsers = []
    }
  }
  return [...USERS, ...dynamicUsers]
}

export function createUser({ username, password, role, email }) {
  const allUsers = getAllUsers()
  if (allUsers.find(u => u.username === username)) {
    return { success: false, message: 'Username already exists.' }
  }
  
  const saved = localStorage.getItem(DB_USERS_KEY)
  let dynamicUsers = []
  if (saved) {
    try {
      dynamicUsers = JSON.parse(saved)
    } catch {
      dynamicUsers = []
    }
  }
  dynamicUsers.push({ username, password, role, email })
  localStorage.setItem(DB_USERS_KEY, JSON.stringify(dynamicUsers))
  return { success: true, message: `${role} account created successfully!` }
}

export function login({ username, password }) {
  const allUsers = getAllUsers()
  const found = allUsers.find(u => u.username === username && u.password === password)
  if (!found) {
    return false
  }

  state.user = { username: found.username, role: found.role }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.user))
  return true
}

export function logout() {
  state.user = null
  localStorage.removeItem(STORAGE_KEY)
}

export default {
  state,
  initAuth,
  isLoggedIn,
  getUserRole,
  login,
  logout,
  createUser,
  getAllUsers
}
