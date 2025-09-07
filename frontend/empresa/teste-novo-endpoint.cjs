// Teste do novo endpoint de filtro por data de pagamento
const axios = require('axios');

async function testarNovoEndpoint() {
    console.log('🔍 Testando endpoint de filtro por data de pagamento...');
    
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
        console.log('📊 Tipo de dados retornados:', typeof response.data);
        console.log('📊 É array?', Array.isArray(response.data));
        
        if (Array.isArray(response.data)) {
            console.log('📈 Total de contas retornadas:', response.data.length);
            
            // Separar por tipo baseado nos campos
            const contasReceber = response.data.filter(conta => conta.cliente_nome);
            const contasPagar = response.data.filter(conta => conta.fornecedor_nome);
            
            console.log('📈 Contas a receber (com cliente_nome):', contasReceber.length);
            console.log('📉 Contas a pagar (com fornecedor_nome):', contasPagar.length);
            
            if (contasReceber.length > 0) {
                console.log('📋 Exemplo conta a receber:', {
                    id: contasReceber[0].id,
                    cliente: contasReceber[0].cliente_nome,
                    valor: contasReceber[0].valor,
                    recebido: contasReceber[0].recebido,
                    data_pagamento: contasReceber[0].data_pagamento,
                    status: contasReceber[0].status
                });
            }
            
            if (contasPagar.length > 0) {
                console.log('📋 Exemplo conta a pagar:', {
                    id: contasPagar[0].id,
                    fornecedor: contasPagar[0].fornecedor_nome,
                    valor: contasPagar[0].valor,
                    valor_pago: contasPagar[0].valor_pago,
                    data_pagamento: contasPagar[0].data_pagamento,
                    status: contasPagar[0].status
                });
            }
            
        } else {
            const contasReceber = response.data?.contas_receber || [];
            const contasPagar = response.data?.contas_pagar || [];
            
            console.log('📈 Contas a receber:', contasReceber.length);
            console.log('📉 Contas a pagar:', contasPagar.length);
        }
        
    } catch (error) {
        console.error('❌ Erro ao testar endpoint:', error.response?.status, error.response?.data || error.message);
    }
}

testarNovoEndpoint();
