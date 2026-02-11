import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    hmr: true, // Hot Module Replacement ativado
    watch: {
      usePolling: true, // Usa polling para detectar mudanças (melhor para Windows)
    }
  }
})
