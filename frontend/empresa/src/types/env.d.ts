// src/types/env.d.ts

declare global {
    namespace NodeJS {
      interface ProcessEnv {
        REACT_APP_API_URL: string;
        VITE_API_URL: string;
        NODE_ENV: 'development' | 'production';
        // Adicione outras variáveis de ambiente conforme necessário
      }
    }
  }