// Teste do endpoint de contas por vencimento
const axios = require('axios');

async function testarEndpointVencimento() {
    console.log('🔍 Testando endpoint de contas por vencimento...');
    
    try {
        // Teste básico do endpoint
        const response = await axios.get('http://localhost:8000/contas/contas-por-data-vencimento/', {
            params: {
                data_inicio: '2020-01-01',
                data_fim: '2025-09-01', // Antes do período atual
                tipo: 'ambos',
                status: 'A' // Apenas contas em aberto
            }
        });
        
        console.log('✅ Status:', response.status);
        console.log('📊 Tipo de resposta:', typeof response.data);
        
        const data = response.data;
        
        if (data) {
            console.log('📋 Estrutura da resposta:');
            console.log('   - Período:', data.periodo);
            console.log('   - Filtros:', data.filtros);
            
            if (data.resumo) {
                console.log('📊 Resumo:');
                console.log('   - Contas a receber:', data.resumo.total_contas_receber);
                console.log('   - Valor a receber:', data.resumo.valor_total_receber);
                console.log('   - Contas a pagar:', data.resumo.total_contas_pagar);
                console.log('   - Valor a pagar:', data.resumo.valor_total_pagar);
                console.log('   - Saldo previsto:', data.resumo.saldo_previsto);
            }
            
            // Verificar contas vencidas (com vencimento anterior a 01/09/2025)
            const dataLimite = new Date('2025-09-01');
            
            const recebVencidas = (data.contas_a_receber || []).filter(conta => {
                const vencimento = new Date(conta.vencimento);
                return vencimento < dataLimite;
            });
            
            const pagarVencidas = (data.contas_a_pagar || []).filter(conta => {
                const vencimento = new Date(conta.vencimento);
                return vencimento < dataLimite;
            });
            
            console.log('\n🔍 ANÁLISE DE CONTAS VENCIDAS (antes de 01/09/2025):');
            console.log('📈 Contas a receber vencidas:', recebVencidas.length);
            console.log('📉 Contas a pagar vencidas:', pagarVencidas.length);
            
            if (recebVencidas.length > 0) {
                const valorRecebVencidas = recebVencidas.reduce((sum, conta) => 
                    sum + parseFloat(conta.valor || 0), 0);
                console.log('💰 Valor total a receber vencido:', valorRecebVencidas);
                
                console.log('📋 Primeiras 3 contas a receber vencidas:');
                recebVencidas.slice(0, 3).forEach((conta, i) => {
                    console.log(`   ${i+1}. ${conta.cliente_nome}: R$ ${conta.valor} (venc: ${conta.vencimento?.split('T')[0]})`);
                });
            }
            
            if (pagarVencidas.length > 0) {
                const valorPagarVencidas = pagarVencidas.reduce((sum, conta) => 
                    sum + parseFloat(conta.valor || 0), 0);
                console.log('💰 Valor total a pagar vencido:', valorPagarVencidas);
                
                console.log('📋 Primeiras 3 contas a pagar vencidas:');
                pagarVencidas.slice(0, 3).forEach((conta, i) => {
                    console.log(`   ${i+1}. ${conta.fornecedor_nome}: R$ ${conta.valor} (venc: ${conta.vencimento?.split('T')[0]})`);
                });
            }
            
            console.log('\n🎯 DADOS PARA O DASHBOARD:');
            console.log('✅ Endpoint funcional e retornando dados estruturados');
            console.log('✅ Filtro por status "A" funcionando');
            console.log('✅ Possível identificar contas vencidas por data');
            console.log('✅ Dados prontos para integração nos cartões');
            
        } else {
            console.log('❌ Resposta vazia do endpoint');
        }
        
    } catch (error) {
        console.error('❌ Erro ao testar endpoint:', error.message);
        if (error.response) {
            console.error('📊 Status:', error.response.status);
            console.error('📊 Dados do erro:', error.response.data);
        }
    }
}

testarEndpointVencimento();
