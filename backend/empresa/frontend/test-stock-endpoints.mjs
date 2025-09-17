// Test script to verify stock endpoints work correctly
// Run with: node test-stock-endpoints.mjs

console.log('🧪 Testing Stock Endpoints...');
console.log('🎯 Backend: http://127.0.0.1:8000');
console.log('📋 Endpoints to test:');
console.log('  - /api/estoque-controle/estoque_atual/');
console.log('  - /api/estoque-controle/estoque_critico/');
console.log('  - /api/estoque-controle/movimentacoes_periodo/');
console.log('  - /api/estoque-controle/produtos_mais_movimentados/');

const API_BASE_URL = 'http://127.0.0.1:8000';

async function testEndpoint(endpoint, description) {
  try {
    console.log(`\n🔍 Testing ${description}...`);
    console.log(`   URL: ${API_BASE_URL}${endpoint}`);
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log(`✅ ${description}: SUCCESS`);
      
      // Show some basic info about the response
      if (data.estoque) {
        console.log(`   📦 Products: ${data.estoque.length}`);
      }
      if (data.produtos) {
        console.log(`   📦 Products: ${data.produtos.length}`);
      }
      if (data.produtos_mais_movimentados) {
        console.log(`   📦 Products: ${data.produtos_mais_movimentados.length}`);
      }
      if (data.produtos_movimentados) {
        console.log(`   📦 Products: ${data.produtos_movimentados.length}`);
      }
      if (data.estatisticas) {
        console.log(`   💰 Total Value: R$ ${data.estatisticas.valor_total_atual?.toLocaleString('pt-BR') || '0'}`);
      }
      if (data.resumo) {
        console.log(`   💰 Total Entries: R$ ${data.resumo.valor_total_entradas?.toLocaleString('pt-BR') || '0'}`);
      }
      
      return true;
    } else {
      const errorText = await response.text();
      console.log(`❌ ${description}: FAILED`);
      console.log(`   Status: ${response.status}`);
      console.log(`   Error: ${errorText}`);
      return false;
    }
  } catch (error) {
    console.log(`❌ ${description}: EXCEPTION`);
    console.log(`   Error: ${error.message}`);
    return false;
  }
}

async function testBackendConnection() {
  try {
    console.log('\n🌐 Testing backend connectivity...');
    // Test with a known endpoint instead of root
    const response = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?limite=1`);
    
    if (response.ok || response.status === 404) {
      console.log('✅ Backend is reachable');
      return true;
    } else {
      console.log(`❌ Backend returned status ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log('❌ Cannot reach backend:', error.message);
    console.log('\n🔧 Make sure the Django backend is running:');
    console.log('   python manage.py runserver 127.0.0.1:8000');
    return false;
  }
}

async function runTests() {
  // Test backend connectivity first
  const backendOk = await testBackendConnection();
  
  console.log('\n📊 Testing stock endpoints...');

  const tests = [
    {
      endpoint: '/api/estoque-controle/estoque_atual/?limite=5',
      description: 'Current Stock (estoque_atual)'
    },
    {
      endpoint: '/api/estoque-controle/estoque_critico/?limite=5',
      description: 'Critical Stock (estoque_critico)'
    },
    {
      endpoint: '/api/estoque-controle/produtos_mais_movimentados/?limite=5',
      description: 'Most Moved Products (produtos_mais_movimentados)'
    },
    {
      endpoint: '/api/estoque-controle/movimentacoes_periodo/?data_inicio=2024-01-01&data_fim=2024-12-31',
      description: 'Period Movements (movimentacoes_periodo)'
    }
  ];

  let successCount = 0;
  
  for (const test of tests) {
    const success = await testEndpoint(test.endpoint, test.description);
    if (success) successCount++;
  }

  console.log('\n🎯 SUMMARY:');
  console.log(`✅ ${successCount}/${tests.length} endpoints working correctly`);
  
  if (successCount === tests.length) {
    console.log('🎉 All stock endpoints are working!');
    console.log('\n🚀 Ready to use in EstoqueDashboard component!');
    console.log('\n📋 Next steps:');
    console.log('1. Run: npm run dev');
    console.log('2. Navigate to the stock dashboard');
    console.log('3. Verify data loads correctly');
  } else {
    console.log('⚠️  Some endpoints failed. Check the backend configuration.');
  }
}

// Run the tests
runTests().catch(error => {
  console.error('❌ Test execution failed:', error);
});