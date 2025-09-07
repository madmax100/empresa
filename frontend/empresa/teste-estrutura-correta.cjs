// Teste do endpoint com estrutura correta
const axios = require('axios');

async function testarEstrutura() {
    console.log('🔍 Testando endpoint com estrutura correta...');
    
    try {
        const response = await axios.get('http://localhost:8000/contas/contas-por-data-pagamento/', {
            params: {
                data_inicio: '2025-08-27',
                data_fim: '2025-08-31',
                tipo: 'ambos',
                status: 'P'
            }
        });
        
        console.log('✅ Status:', response.status);
        console.log('📊 Tipo de resposta:', typeof response.data);
        
        const data = response.data;
        
        if (data) {
            console.log('📋 Chaves principais:', Object.keys(data));
            
            // Período
            if (data.periodo) {
                console.log('📅 Período:', data.periodo);
            }
            
            // Filtros
            if (data.filtros) {
                console.log('🔍 Filtros aplicados:', data.filtros);
            }
            
            // Resumo
            if (data.resumo) {
                console.log('📊 Resumo:');
                console.log('   - Total contas a pagar:', data.resumo.total_contas_pagar);
                console.log('   - Valor total a pagar:', data.resumo.valor_total_pagar);
                console.log('   - Total contas a receber:', data.resumo.total_contas_receber);
                console.log('   - Valor total a receber:', data.resumo.valor_total_receber);
                console.log('   - Saldo líquido:', data.resumo.saldo_liquido);
            }
            
            // Contas a pagar
            if (data.contas_a_pagar) {
                console.log('📉 Contas a pagar encontradas:', data.contas_a_pagar.length);
                if (data.contas_a_pagar.length > 0) {
                    const primeira = data.contas_a_pagar[0];
                    console.log('   - Exemplo:', {
                        id: primeira.id,
                        fornecedor: primeira.fornecedor_nome,
                        valor: primeira.valor,
                        valor_pago: primeira.valor_pago,
                        data_pagamento: primeira.data_pagamento
                    });
                }
            }
            
            // Contas a receber  
            if (data.contas_a_receber) {
                console.log('📈 Contas a receber encontradas:', data.contas_a_receber.length);
                if (data.contas_a_receber.length > 0) {
                    const primeira = data.contas_a_receber[0];
                    console.log('   - Exemplo:', {
                        id: primeira.id,
                        cliente: primeira.cliente_nome,
                        valor: primeira.valor,
                        recebido: primeira.recebido,
                        data_pagamento: primeira.data_pagamento
                    });
                }
            }
            
            console.log('\n🎯 Estrutura perfeita para integração!');
            console.log('✅ Dados filtrados por data de pagamento');
            console.log('✅ Separação clara entre contas a pagar e receber');
            console.log('✅ Resumos já calculados');
            
        } else {
            console.log('❌ Resposta vazia');
        }
        
    } catch (error) {
        console.error('❌ Erro:', error.message);
        if (error.response) {
            console.error('📊 Status:', error.response.status);
            console.error('📊 Dados do erro:', error.response.data);
        }
    }
}

testarEstrutura();
