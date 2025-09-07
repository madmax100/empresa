// Teste rápido para verificar se a API está acessível
const axios = require('axios');

async function testeAPI() {
    console.log('🔍 Testando conexão com a API...');
    
    try {
        // Teste básico de conectividade
        const response = await axios.get('http://localhost:8000/contas/clientes/', {
            timeout: 5000
        });
        
        console.log('✅ API está respondendo!');
        console.log('📊 Status:', response.status);
        console.log('📦 Dados recebidos:', response.data.count || 'N/A', 'registros');
        
        // Teste específico do endpoint que estava falhando
        console.log('\n🔍 Testando endpoint operacional...');
        const opResponse = await axios.get('http://localhost:8000/contas/fluxo-caixa/operacional/', {
            params: {
                data_inicio: '2025-01-01',
                data_fim: '2025-12-31',
                fonte: 'todas',
                filtrar_por_data_pagamento: 'true',
                apenas_contas_pagas: 'true'
            },
            timeout: 10000
        });
        
        console.log('✅ Endpoint operacional funcionando!');
        console.log('📊 Status:', opResponse.status);
        
    } catch (error) {
        console.error('❌ Erro na API:', error.message);
        
        if (error.response) {
            console.error('📊 Status:', error.response.status);
            console.error('📄 Dados:', error.response.data);
        } else if (error.request) {
            console.error('🌐 Erro de conexão - verifique se o backend está rodando');
        }
    }
}

testeAPI();
