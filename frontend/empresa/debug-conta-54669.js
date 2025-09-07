// Script para debug da conta #54669
const axios = require('axios');

async function debugConta54669() {
    try {
        console.log('🔍 Buscando dados da conta #54669...');
        
        // Buscar contas a pagar
        const response = await axios.get('http://127.0.0.1:8000/contas/contas_pagar/dashboard/', {
            params: {
                data_inicio: '2025-01-01',
                data_fim: '2025-12-31'
            }
        });
        
        console.log('📊 Status da resposta:', response.status);
        console.log('📊 Total de títulos pagos:', response.data?.titulos_pagos_periodo?.length || 0);
        
        // Buscar especificamente a conta #54669
        const conta54669 = response.data?.titulos_pagos_periodo?.find(conta => conta.id === 54669);
        
        if (conta54669) {
            console.log('✅ Conta #54669 encontrada:');
            console.log('📋 Dados completos:', JSON.stringify(conta54669, null, 2));
            console.log('🏷️ Campos específicos:', {
                id: conta54669.id,
                status: conta54669.status,
                data_pagamento: conta54669.data_pagamento,
                vencimento: conta54669.vencimento,
                data_vencimento: conta54669.data_vencimento,
                historico: conta54669.historico,
                valor: conta54669.valor,
                valor_total_pago: conta54669.valor_total_pago,
                fornecedor: conta54669.fornecedor
            });
        } else {
            console.log('❌ Conta #54669 NÃO encontrada nos títulos pagos');
            
            // Verificar se está nos títulos em aberto
            const contaAberta = response.data?.titulos_abertos_periodo?.find(conta => conta.id === 54669);
            if (contaAberta) {
                console.log('📋 Encontrada nos títulos ABERTOS:', JSON.stringify(contaAberta, null, 2));
            } else {
                console.log('❌ Conta #54669 não encontrada em lugar nenhum');
            }
        }
        
    } catch (error) {
        console.error('❌ Erro ao buscar dados:', error.message);
    }
}

debugConta54669();
