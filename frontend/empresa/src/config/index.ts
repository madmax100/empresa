// src/config/index.ts

const isDevelopment = import.meta.env.MODE === 'development';

const config = {
  env: isDevelopment ? 'development' : 'production',
  api: {
    baseURL: import.meta.env.VITE_API_URL || (isDevelopment ? 'http://localhost:8000/contas/' : 'http://127.0.0.1:8000/contas/'),
    timeout: 30000,
    longTimeout: 120000,
    maxRetries: 3,
    retryDelay: 1000,
    defaultHeaders: {
      'Accept': 'application/json',
      'X-Application-Version': '1.0.0'
    },
    authToken: null as string | null
  },
  app: {
    name: 'Sistema de Gestão Financeira',
    version: '1.0.0'
  },
  features: {
    enableRetry: true,
    enableCache: true,
    debugMode: isDevelopment
  },
  pagination: {
    defaultPageSize: 20,
    maxPageSize: 100
  }
};

export default config;