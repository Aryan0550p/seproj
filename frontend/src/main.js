import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initAuth } from './auth'

// global stylesheet (utilities, theme rules)
import './assets/styles.css'

function showFatalError(message, error) {
  const overlay = document.createElement('div')
  overlay.style.position = 'fixed'
  overlay.style.inset = '0'
  overlay.style.background = 'rgba(0,0,0,0.8)'
  overlay.style.color = 'white'
  overlay.style.zIndex = '9999'
  overlay.style.padding = '24px'
  overlay.style.fontFamily = 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
  overlay.style.overflow = 'auto'
  overlay.innerHTML = `
    <h1 style="margin-top:0;font-size:24px;">Application Error</h1>
    <pre style="white-space:pre-wrap;">${message}</pre>
    <pre style="white-space:pre-wrap;margin-top:12px;">${error?.stack || ''}</pre>
  `
  document.body.appendChild(overlay)
}

window.addEventListener('error', (event) => {
  console.error('Uncaught error:', event.error)
  showFatalError(event.message, event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled rejection:', event.reason)
  showFatalError('Unhandled Promise Rejection', event.reason)
})

initAuth()

const app = createApp(App)
app.use(router)
app.mount('#app')
