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

function getDynamicUsers() {
  const saved = localStorage.getItem(DB_USERS_KEY)
  if (!saved) {
    return []
  }

  try {
    return JSON.parse(saved)
  } catch {
    return []
  }
}

function saveDynamicUsers(users) {
  localStorage.setItem(DB_USERS_KEY, JSON.stringify(users))
}

export function getAllUsers() {
  return [...USERS, ...getDynamicUsers()]
}

export function createUser({ username, password, role, email }) {
  const allUsers = getAllUsers()
  const normalizedUsername = String(username || '').trim()

  if (allUsers.find(u => u.username === normalizedUsername)) {
    return { success: false, message: 'Username already exists.' }
  }

  const dynamicUsers = getDynamicUsers()
  dynamicUsers.push({
    username: normalizedUsername,
    password,
    role,
    email: String(email || '').trim(),
    createdAt: new Date().toISOString()
  })
  saveDynamicUsers(dynamicUsers)
  return { success: true, message: `${role} account created successfully!` }
}

export function deleteUser(username) {
  if (username === 'admin') {
    return { success: false, message: 'The built-in admin account cannot be deleted.' }
  }

  const dynamicUsers = getDynamicUsers()
  const nextUsers = dynamicUsers.filter(user => user.username !== username)

  if (nextUsers.length === dynamicUsers.length) {
    return { success: false, message: 'User not found.' }
  }

  saveDynamicUsers(nextUsers)

  if (state.user?.username === username) {
    logout()
  }

  return { success: true, message: `${username} was deleted successfully.` }
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
  deleteUser,
  getAllUsers
}
