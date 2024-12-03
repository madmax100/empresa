/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_APP_TITLE: string
    // adicione outras variáveis de ambiente se necessário
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
