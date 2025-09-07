import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Proxy de desenvolvimento para evitar CORS e facilitar chamadas relativas
  server: {
    proxy: {
      // Use VITE_API_URL=/contas em .env.development (já configurado)
      '/contas': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // Opcional: caso use VITE_API_URL=/api
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  // Otimizações de build
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separar React e bibliotecas principais
          'react-vendor': ['react', 'react-dom'],
          // Separar Recharts (biblioteca de gráficos)
          'charts': ['recharts'],
          // Separar componentes UI (Radix UI)
          'ui-vendor': [
            '@radix-ui/react-alert-dialog',
            '@radix-ui/react-checkbox',
            '@radix-ui/react-dialog',
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-label',
            '@radix-ui/react-popover',
            '@radix-ui/react-select',
            '@radix-ui/react-slot',
            '@radix-ui/react-tabs',
            '@radix-ui/react-toast'
          ],
          // Separar utilitários
          'utils': ['axios', 'date-fns', 'clsx', 'class-variance-authority']
        }
      }
    },
    // Aumentar limite de aviso para chunks maiores
    chunkSizeWarningLimit: 600
  }
})