import path from "path";
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
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
});
