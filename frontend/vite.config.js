import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  publicDir: false,
  server: {
    port: 3000,
    open: true,
    middlewareMode: false
  }
})
