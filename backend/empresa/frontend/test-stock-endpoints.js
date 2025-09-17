// Test script to check stock control endpoints
// Run with: node test-stock-endpoints.js

import fetch from 'node-fetch';

console.log('🧪 Testing Stock Control Endpoints...');

const baseUrl = 'http://127.0.0.1:8000';
const endpoints = [
  '/contas/estoque-controle/estoque_atual/',
  '/contas/estoque-controle/estoque_critico/',
  '/contas/estoque-controle/produtos_mais_movimentados/',
  '/contas/estoque-controle/movimentacoes_periodo/'
];

async function testEndpoint(endpoint) {
  try {
    console.log(`\n🔍 Testing: ${baseUrl}${endpoint}`);
    
    const response = await fetch(`${baseUrl}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log(`📊 Status: ${response.status} ${response.statusText}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log(`✅ Success! Data keys:`, Object.keys(data));
      
      if (data.estoque) {
        console.log(`📦 Products found: ${data.estoque.length}`);
      }
      if (data.produtos) {
        console.log(`📦 Products found: ${data.produtos.length}`);
      }
      if (data.produtos_mais_movimentados) {
        console.log(`🔄 Most moved products: ${data.produtos_mais_movimentados.length}`);
      }
      if (data.produtos_movimentados) {
        console.log(`📅 Period movements: ${data.produtos_movimentados.length}`);
      }
      if (data.estatisticas) {
        console.log(`📊 Statistics:`, data.estatisticas);
      }
      
      return { success: true, data };
    } else {
      const errorText = await response.text();
      console.log(`❌ Error: ${errorText}`);
      return { success: false, error: errorText };
    }
  } catch (error) {
    console.log(`❌ Network Error: ${error.message}`);
    return { success: false, error: error.message };
  }
}

async function testAllEndpoints() {
  console.log('🚀 Starting endpoint tests...\n');
  
  const results = [];
  
  for (const endpoint of endpoints) {
    const result = await testEndpoint(endpoint);
    results.push({ endpoint, ...result });
    
    // Wait a bit between requests
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  console.log('\n📋 SUMMARY:');
  console.log('='.repeat(50));
  
  let successCount = 0;
  for (const result of results) {
    const status = result.success ? '✅ OK' : '❌ FAIL';
    console.log(`${status} ${result.endpoint}`);
    if (result.success) successCount++;
  }
  
  console.log(`\n🎯 Results: ${successCount}/${results.length} endpoints working`);
  
  if (successCount === 0) {
    console.log('\n🚨 NO ENDPOINTS WORKING!');
    console.log('Possible issues:');
    console.log('1. Backend server is not running');
    console.log('2. Backend is running on different port');
    console.log('3. Stock control endpoints are not implemented');
    console.log('4. CORS issues');
    console.log('\n💡 Solutions:');
    console.log('1. Start backend: python manage.py runserver');
    console.log('2. Check if backend has stock control app');
    console.log('3. Verify URLs in backend/urls.py');
  } else if (successCount < results.length) {
    console.log('\n⚠️  SOME ENDPOINTS NOT WORKING!');
    console.log('Check the failed endpoints above');
  } else {
    console.log('\n🎉 ALL ENDPOINTS WORKING!');
    console.log('The issue might be in the frontend component');
  }
}

// Test basic connectivity first
async function testBasicConnectivity() {
  console.log('🌐 Testing basic backend connectivity...');
  
  try {
    const response = await fetch(`${baseUrl}/`, {
      method: 'GET',
    });
    
    console.log(`📡 Backend status: ${response.status} ${response.statusText}`);
    
    if (response.ok) {
      console.log('✅ Backend is reachable');
      return true;
    } else {
      console.log('❌ Backend returned error');
      return false;
    }
  } catch (error) {
    console.log(`❌ Cannot reach backend: ${error.message}`);
    console.log('\n💡 Make sure backend is running:');
    console.log('cd C:\\Users\\Cirilo\\Documents\\kiro\\empresa\\backend');
    console.log('python manage.py runserver');
    return false;
  }
}

async function main() {
  const isBackendReachable = await testBasicConnectivity();
  
  if (isBackendReachable) {
    await testAllEndpoints();
  } else {
    console.log('\n🛑 Cannot proceed with endpoint tests - backend not reachable');
  }
}

main().catch(console.error);