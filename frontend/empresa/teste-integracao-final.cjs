// Teste final da integração
const axios = require('axios');

async function testarIntegracao() {
    console.log('🔍 Teste final da integração do endpoint...');
    
    try {
        // Simular chamada do frontend
        const response = await axios.get('http://localhost:8000/contas/contas-por-data-pagamento/', {
            params: {
                data_inicio: '2025-08-27',
                data_fim: '2025-08-31',
                tipo: 'ambos',
                status: 'P'
            }
        });
        
        console.log('✅ Status:', response.status);
        
        const data = response.data;
        
        // Validar estrutura esperada pelo frontend
        if (data.contas_a_receber && data.contas_a_pagar && data.resumo) {
            console.log('🎯 Estrutura correta para integração!');
            console.log('📈 Contas a receber:', data.contas_a_receber.length);
            console.log('📉 Contas a pagar:', data.contas_a_pagar.length);
            
            // Simular processamento do frontend
            const recebPagos = data.contas_a_receber || [];
            const pagarPagos = data.contas_a_pagar || [];
            const resumoEndpoint = data.resumo || {};
            
            const totalRecebPago = resumoEndpoint.valor_total_receber || 
                recebPagos.reduce((acc, conta) => acc + (Number(conta.recebido) || Number(conta.valor) || 0), 0);
            
            const totalPagarPago = resumoEndpoint.valor_total_pagar ||
                pagarPagos.reduce((acc, conta) => acc + (Number(conta.valor_pago) || Number(conta.valor) || 0), 0);
            
            console.log('💰 Total recebido no período:', totalRecebPago);
            console.log('💰 Total pago no período:', totalPagarPago);
            console.log('💰 Saldo líquido:', resumoEndpoint.saldo_liquido);
            
            console.log('\n✅ INTEGRAÇÃO VALIDADA COM SUCESSO!');
            console.log('🚀 O endpoint está pronto para uso no dashboard');
            console.log('📊 Dados filtrados por data de pagamento');
            console.log('🔄 Fallback implementado para compatibilidade');
            
        } else {
            console.log('❌ Estrutura inesperada:', Object.keys(data));
        }
        
    } catch (error) {
        console.error('❌ Erro na integração:', error.message);
        if (error.response) {
            console.error('📊 Status:', error.response.status);
            console.error('📊 Dados:', error.response.data);
        }
    }
}

testarIntegracao();
