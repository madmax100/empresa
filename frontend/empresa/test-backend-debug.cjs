#!/usr/bin/env node
/**
 * Script para testar endpoints do backend e verificar estrutura dos dados
 * Uso: node test-backend-debug.cjs
 */

const http = require('http');

// Configuração do backend
const BACKEND_HOST = '127.0.0.1';
const BACKEND_PORT = 8000;

/**
 * Faz requisição HTTP e retorna a resposta
 */
function makeRequest(path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: BACKEND_HOST,
      port: BACKEND_PORT,
      path: path,
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({ status: res.statusCode, data: jsonData });
        } catch (e) {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });
    
    req.on('error', (e) => {
      reject(e);
    });
    
    req.end();
  });
}

/**
 * Analisa a estrutura de um objeto e mostra os campos relacionados a pagamento
 */
function analyzePaymentFields(obj, prefix = '') {
  const paymentFields = [];
  const dateFields = [];
  
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    
    // Campos relacionados a pagamento
    if (key.toLowerCase().includes('pagamento') || 
        key.toLowerCase().includes('quitacao') ||
        key.toLowerCase().includes('payment')) {
      paymentFields.push({ key: fullKey, value: value, type: typeof value });
    }
    
    // Campos de data
    if (key.toLowerCase().includes('data') || 
        key.toLowerCase().includes('dt_') ||
        key.toLowerCase().includes('date')) {
      dateFields.push({ key: fullKey, value: value, type: typeof value });
    }
    
    // Se for um objeto, analisa recursivamente (mas só 1 nível para evitar loops)
    if (typeof value === 'object' && value !== null && !prefix) {
      const nested = analyzePaymentFields(value, fullKey);
      paymentFields.push(...nested.paymentFields);
      dateFields.push(...nested.dateFields);
    }
  }
  
  return { paymentFields, dateFields };
}

/**
 * Testa os endpoints principais
 */
async function testEndpoints() {
  console.log('🔍 TESTANDO ENDPOINTS DO BACKEND');
  console.log('=' .repeat(50));
  
  const endpoints = [
    '/contas/contas_receber/dashboard/',
    '/contas/contas_pagar/dashboard/',
    '/contas/movimentacoes_estoque/?limit=5'
  ];
  
  for (const endpoint of endpoints) {
    console.log(`\n📡 Testando: ${endpoint}`);
    console.log('-'.repeat(40));
    
    try {
      const response = await makeRequest(endpoint);
      
      if (response.status === 200) {
        console.log(`✅ Status: ${response.status}`);
        
        if (typeof response.data === 'object') {
          // Verificar se tem results (paginação Django)
          const dataToAnalyze = response.data.results || response.data;
          
          if (Array.isArray(dataToAnalyze) && dataToAnalyze.length > 0) {
            console.log(`📊 Encontrados ${dataToAnalyze.length} registros`);
            
            // Analisar primeiro registro
            const firstRecord = dataToAnalyze[0];
            console.log(`\n🔍 Estrutura do primeiro registro:`);
            console.log('Campos principais:', Object.keys(firstRecord).join(', '));
            
            // Analisar campos de pagamento
            const analysis = analyzePaymentFields(firstRecord);
            
            if (analysis.paymentFields.length > 0) {
              console.log(`\n💰 Campos de Pagamento encontrados:`);
              analysis.paymentFields.forEach(field => {
                console.log(`  - ${field.key}: ${field.value} (${field.type})`);
              });
            } else {
              console.log(`\n❌ Nenhum campo de pagamento encontrado`);
            }
            
            if (analysis.dateFields.length > 0) {
              console.log(`\n📅 Campos de Data encontrados:`);
              analysis.dateFields.forEach(field => {
                console.log(`  - ${field.key}: ${field.value} (${field.type})`);
              });
            }
            
            // Mostrar objeto completo do primeiro registro para debug
            console.log(`\n🔬 OBJETO COMPLETO (primeiro registro):`);
            console.log(JSON.stringify(firstRecord, null, 2));
            
          } else {
            console.log(`📊 Resposta vazia ou não é array`);
            console.log('Dados recebidos:', JSON.stringify(response.data, null, 2));
          }
        } else {
          console.log(`📊 Resposta não é JSON válido:`, response.data);
        }
      } else {
        console.log(`❌ Status: ${response.status}`);
        console.log('Erro:', response.data);
      }
      
    } catch (error) {
      console.log(`❌ Erro na requisição: ${error.message}`);
    }
  }
}

/**
 * Função principal
 */
async function main() {
  try {
    console.log(`🚀 Iniciando teste dos endpoints`);
    console.log(`🎯 Backend: http://${BACKEND_HOST}:${BACKEND_PORT}`);
    
    await testEndpoints();
    
    console.log('\n✅ Teste concluído!');
    console.log('\n💡 Dicas:');
    console.log('- Verifique os campos de pagamento encontrados');
    console.log('- Compare com os campos que estamos tentando mapear no frontend');
    console.log('- Ajuste o financialService.ts conforme necessário');
    
  } catch (error) {
    console.error('❌ Erro geral:', error);
  }
}

// Executar se chamado diretamente
if (require.main === module) {
  main();
}
