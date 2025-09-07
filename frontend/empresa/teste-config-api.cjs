// Teste de configuração da API
console.log('🔍 Testando configuração da API...');

// Simular as variáveis de ambiente do Vite
const testEnvs = [
  { MODE: 'development', VITE_API_URL: 'http://localhost:8000/contas/' },
  { MODE: 'development', VITE_API_URL: '/contas' },
  { MODE: 'development', VITE_API_URL: undefined },
  { MODE: 'production', VITE_API_URL: 'http://localhost:8000/contas/' }
];

testEnvs.forEach((env, index) => {
  console.log(`\n📋 Teste ${index + 1}:`);
  console.log('MODE:', env.MODE);
  console.log('VITE_API_URL:', env.VITE_API_URL);
  
  const isDevelopment = env.MODE === 'development';
  const baseURL = env.VITE_API_URL || (isDevelopment ? 'http://localhost:8000/contas/' : 'http://127.0.0.1:8000/contas/');
  
  console.log('🎯 URL final:', baseURL);
  console.log('✅ Válida:', baseURL.startsWith('http'));
});

console.log('\n🔧 Para corrigir definitivamente:');
console.log('1. Certifique-se que .env.development tem: VITE_API_URL=http://localhost:8000/contas/');
console.log('2. Reinicie o servidor Vite (npm run dev)');
console.log('3. Verifique se o backend está rodando na porta 8000');
