// Teste direto da configuração Axios
import axios from 'axios';

// Simular a configuração exata do projeto
const baseURL = 'http://localhost:8000/contas/';

console.log('🔍 Testando conexão direta com:', baseURL);

const api = axios.create({
    baseURL: baseURL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Teste 1: Endpoint simples
try {
    console.log('📋 Testando endpoint básico...');
    const response = await api.get('clientes/', { timeout: 5000 });
    console.log('✅ Clientes:', response.status, response.data?.count || 'sem count');
} catch (error) {
    console.error('❌ Erro clientes:', error.message);
    if (error.response) {
        console.error('📊 Status:', error.response.status);
        console.error('🌐 URL tentativa:', error.config?.url);
    }
}

// Teste 2: Endpoint do dashboard
try {
    console.log('📊 Testando dashboard comercial...');
    const response = await api.get('fluxo-caixa/dashboard_comercial/', {
        params: {
            data_inicio: '2025-01-01',
            data_fim: '2025-12-31'
        },
        timeout: 10000
    });
    console.log('✅ Dashboard:', response.status);
} catch (error) {
    console.error('❌ Erro dashboard:', error.message);
    if (error.response) {
        console.error('📊 Status:', error.response.status);
        console.error('🌐 URL tentativa:', error.config?.url);
    }
}

console.log('🏁 Teste concluído');
