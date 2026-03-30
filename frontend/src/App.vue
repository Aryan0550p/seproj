<template>
  <div id="app">
    <Navbar v-if="isAuthenticated" />
    <main class="main-content">
      <router-view />
    </main>
    <Footer v-if="isAuthenticated" />

  </div>
</template>

<script>
import { computed } from 'vue'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
import { isLoggedIn } from './auth'
import { initStore } from './store'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  },
  setup() {
    initStore()
    const isAuthenticated = computed(() => isLoggedIn())

    return { isAuthenticated }
  }
}
</script>


<style>
#app {
  font-family: 'Inter', Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  /* Use CSS variables for theme adaptivity */
  background: var(--bg-app);
  color: var(--text-primary);

  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  transition: background 0.3s ease, color 0.3s ease;
}

/* Subtle premium glow layer */
#app::before {
  content: "";
  position: fixed;
  inset: 0;

  background:
    radial-gradient(circle at 15% 20%, rgba(180, 140, 40, 0.08), transparent 40%),
    radial-gradient(circle at 85% 80%, rgba(120, 180, 60, 0.06), transparent 40%);

  pointer-events: none;
  z-index: 0;
}

/* Ensure content appears above glow */
.main-content {
  position: relative;
  z-index: 1;

  padding: 30px 40px;
  min-height: calc(100vh - 140px);

  max-width: 1400px;
  margin: 0 auto;
}

/* Smooth page transitions */
.main-content {
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>