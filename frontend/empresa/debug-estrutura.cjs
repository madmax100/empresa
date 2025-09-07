// Teste detalhado da estrutura do endpoint
const axios = require('axios');

async function testarEstrutura() {
    console.log('🔍 Analisando estrutura do endpoint...');
    
    try {
        const response = await axios.get('http://localhost:8000/contas/contas-por-data-pagamento/', {
            params: {
                data_inicio: '2025-08-01',
                data_fim: '2025-08-31',
                tipo: 'ambos',
                status: 'P'
            }
        });
        
        console.log('✅ Status:', response.status);
        console.log('📊 Chaves do objeto:', Object.keys(response.data));
        console.log('📊 Estrutura completa:', JSON.stringify(response.data, null, 2));
        
    } catch (error) {
        console.error('❌ Erro:', error.response?.status, error.response?.data || error.message);
    }
}

testarEstrutura();
