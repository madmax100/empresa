// Script de debug para verificar dados do backend

console.log('🔍 Testando endpoints...');

// Função para testar endpoints
async function testarEndpoints() {
    try {
        const response = await fetch('http://127.0.0.1:8000/contas/contas_receber/dashboard/');
        const data = await response.json();
        
        console.log('📊 Dados de contas a receber:', {
            resumo: data.resumo,
            titulos_pagos: data.titulos_pagos_periodo?.slice(0, 2),
            titulos_abertos: data.titulos_abertos_periodo?.slice(0, 2)
        });
        
        // Verificar campos de data nos títulos pagos
        if (data.titulos_pagos_periodo?.length > 0) {
            const primeiro = data.titulos_pagos_periodo[0];
            console.log('🗓️ Campos de data no primeiro título pago:', {
                vencimento: primeiro.vencimento,
                data_vencimento: primeiro.data_vencimento,
                dt_vencimento: primeiro.dt_vencimento,
                data_pagamento: primeiro.data_pagamento,
                dt_pagamento: primeiro.dt_pagamento,
                data_quitacao: primeiro.data_quitacao,
                dt_quitacao: primeiro.dt_quitacao,
                allKeys: Object.keys(primeiro)
            });
        }
        
    } catch (error) {
        console.error('❌ Erro ao testar endpoints:', error);
    }
}

testarEndpoints();
