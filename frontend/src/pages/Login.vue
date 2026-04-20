<template>
  <div class="login-container">
    <Navbar />
    <div class="login-page">
      <div class="login-card">
        <div class="login-header">
          <h1>Welcome back</h1>
          <button class="theme-toggle" type="button" @click="toggleTheme">
            {{ isDark ? '🌞' : '🌙' }}
          </button>
        </div>
        <p class="subtitle">Sign in with your credentials to access the dashboard.</p>

        <form @submit.prevent="handleLogin">
          <label>
            <span>Username</span>
            <input v-model="username" type="text" autocomplete="username" placeholder="Enter Username" required />
          </label>

          <label>
            <span>Password</span>
            <input v-model="password" type="password" autocomplete="current-password" placeholder="Enter Password" required />
          </label>

          <button type="submit" class="btn" :disabled="isSubmitting">
            {{ isSubmitting ? 'Signing in…' : 'Sign in' }}
          </button>

          <p v-if="error" class="error">{{ error }}</p>

          
        </form>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login } from '../auth'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

export default {
  name: 'Login',
  components: {
    Navbar,
    Footer
  },
  setup() {
    const router = useRouter()
    const route = useRoute()

    const username = ref('')
    const password = ref('')
    const error = ref('')
    const isSubmitting = ref(false)
    const isDark = ref(true)

    const applyTheme = (dark) => {
      isDark.value = dark
      if (dark) {
        document.body.classList.remove('light')
        localStorage.setItem('theme', 'dark')
      } else {
        document.body.classList.add('light')
        localStorage.setItem('theme', 'light')
      }
    }

    onMounted(() => {
      const saved = localStorage.getItem('theme')
      applyTheme(saved !== 'light')
    })

    const toggleTheme = () => {
      applyTheme(!isDark.value)
    }

    const handleLogin = async () => {
      error.value = ''
      isSubmitting.value = true

      const ok = login({ username: username.value.trim(), password: password.value })

      if (!ok) {
        error.value = 'Invalid credentials. Please try again.'
        isSubmitting.value = false
        return
      }

      const redirectTo = route.query.redirect || { name: 'Dashboard' }
      await router.replace(redirectTo)
    }

    return {
      username,
      password,
      error,
      isSubmitting,
      isDark,
      toggleTheme,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  position: relative;
  display: flex;
  flex-direction: column;
  background: linear-gradient(
      180deg,
      rgba(10, 8, 6, 0.72),
      rgba(10, 8, 6, 0.72)
    ),
    url('../assets/food_bg.jpeg') center/cover no-repeat;
  background-attachment: fixed;
}

.login-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(10, 8, 6, 0.45);
  pointer-events: none;
  z-index: 1;
}

body.light .login-container {
  background: linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.3),
      rgba(255, 255, 255, 0.3)
    ),
    url('../assets/food_bg.jpeg') center/cover no-repeat;
  background-attachment: fixed;
}

body.light .login-container::before {
  background: rgba(255, 255, 255, 0.35);
}

.login-page {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 20px;
  position: relative;
  z-index: 2;
}

body.light .login-page::before {
  background: rgba(255, 255, 255, 0.45);
}

.login-card {
  margin-top: 0;
  position: relative;
  width: min(450px, 100%);
  padding: 32px 30px;
  margin-top: -8vh;
  border-radius: 20px;
  background: rgba(18, 18, 18, 0.92);
  border: 1px solid rgba(170, 140, 60, 0.3);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45), 0 0 28px rgba(170, 140, 60, 0.07);
  backdrop-filter: blur(10px);
  z-index: 2;
}

.login-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.login-card h1 {
  margin: 0;
  font-size: 2rem;
  letter-spacing: 1px;
  color: #ffffff;
}

.subtitle {
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 500;
  font-size: 0.95rem;
}

form {
  margin-top: 26px;
  display: grid;
  gap: 18px;
}

label {
  display: grid;
  gap: 8px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.75);
}

input {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(170, 140, 60, 0.25);
  background: rgba(20, 24, 20, 0.55);
  color: #ffffff;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s ease;
}

input:focus {
  border-color: rgba(180, 150, 45, 0.9);
  box-shadow: 0 0 0 3px rgba(180, 150, 45, 0.15);
}

.btn {
  padding: 12px 14px;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  background: linear-gradient(90deg, #b48c28, #6e9f3a);
  color: #111;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
}

.error {
  color: #ff6b6b;
  font-weight: 600;
  margin-top: 4px;
}

.note {
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  line-height: 1.3;
}

.note strong {
  color: rgba(255, 255, 255, 0.95);
}

/* Ensure login card adapts to light mode */
body.light .login-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.12);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.12), 0 0 28px rgba(0, 0, 0, 0.06);
}

body.light .login-card h1 {
  color: #1a1a1a;
}

body.light .login-card .subtitle,
body.light .login-card label,
body.light .login-card .note {
  color: rgba(26, 26, 26, 0.8);
}

body.light .login-card input {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.15);
  color: #1a1a1a;
}

body.light .login-card input:focus {
  box-shadow: 0 0 0 3px rgba(180, 150, 45, 0.15);
}

body.light .login-card .btn {
  color: #111;
}

/* Theme toggle button (match navbar style) */
.login-card .theme-toggle {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.9);
  padding: 8px;
  border-radius: 12px;
  transition: color 0.2s ease, background 0.2s ease;
}

.login-card .theme-toggle:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
}

body.light .login-card .theme-toggle {
  color: #1a1a1a;
}

body.light .login-card .theme-toggle:hover {
  color: #000;
  background: rgba(0, 0, 0, 0.06);
}
</style>
