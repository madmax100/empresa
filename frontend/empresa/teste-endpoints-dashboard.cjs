// Teste dos endpoints do dashboard
const axios = require('axios');

async function testarEndpointsDashboard() {
    console.log('🔍 Testando endpoints do dashboard...');
    
    const baseURL = 'http://localhost:8000';
    const params = {
        data_inicio: '2024-09-01',
        data_fim: '2025-09-03',
        tipo: 'todos',
        fonte: 'todos'
    };
    
    const endpoints = [
        '/fluxo-caixa/operacional/',
        '/contas/fluxo-caixa/operacional/',
        '/dashboard/operacional/',
        '/operacional/',
        '/contas-por-data-pagamento/',
        '/contas/contas-por-data-pagamento/'
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`\n🚀 Testando: ${baseURL}${endpoint}`);
            const response = await axios.get(`${baseURL}${endpoint}`, {
                params,
                timeout: 5000
            });
            
            console.log(`✅ ${endpoint} - Status: ${response.status}`);
            console.log(`📊 Tipo de dados:`, typeof response.data);
            
            if (response.data && typeof response.data === 'object') {
                const keys = Object.keys(response.data);
                console.log(`🔑 Chaves disponíveis:`, keys.slice(0, 5));
            }
            
        } catch (error) {
            if (error.response) {
                console.log(`❌ ${endpoint} - Status: ${error.response.status}`);
                if (error.response.status === 404) {
                    console.log(`   Endpoint não encontrado`);
                }
            } else if (error.code === 'ECONNREFUSED') {
                console.log(`❌ ${endpoint} - Conexão recusada`);
            } else {
                console.log(`❌ ${endpoint} - Erro: ${error.message}`);
            }
        }
    }
    
    console.log('\n🎯 RESUMO:');
    console.log('Se nenhum endpoint funcionou para dashboard operacional,');
    console.log('precisamos ajustar o frontend para usar apenas contas vencidas');
    console.log('ou simular dados mock para o dashboard.');
}

testarEndpointsDashboard();
