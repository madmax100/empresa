// src/config/api-force.ts
// Configuração forçada para desenvolvimento - usar temporariamente

const config = {
  api: {
    baseURL: 'http://localhost:8000/contas/',
    timeout: 30000,
    longTimeout: 120000,
  }
};

export default config;
