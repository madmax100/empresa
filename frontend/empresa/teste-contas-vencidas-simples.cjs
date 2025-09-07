// Teste simples das contas vencidas
const axios = require('axios');

async function testeConasVencidas() {
    console.log('🔍 Testando apenas contas vencidas...');
    
    try {
        const params = {
            data_inicio: '2020-01-01',
            data_fim: '2024-09-01', // Antes de setembro 2024
            tipo: 'ambos',
            status: 'A'
        };
        
        console.log('📅 Parâmetros:', params);
        
        const response = await axios.get('http://localhost:8000/contas/contas-por-data-vencimento/', {
            params
        });
        
        console.log('✅ Status:', response.status);
        const data = response.data;
        
        if (data) {
            console.log('📊 Resumo:', data.resumo);
            
            const dataLimite = new Date('2024-09-01');
            console.log('📅 Data limite:', dataLimite.toISOString().split('T')[0]);
            
            // Filtrar contas realmente vencidas
            const recebVencidas = (data.contas_a_receber || []).filter(conta => {
                const vencimento = new Date(conta.vencimento);
                return vencimento < dataLimite;
            });
            
            const pagarVencidas = (data.contas_a_pagar || []).filter(conta => {
                const vencimento = new Date(conta.vencimento);
                return vencimento < dataLimite;
            });
            
            console.log('📈 Contas a receber vencidas:', recebVencidas.length);
            console.log('📉 Contas a pagar vencidas:', pagarVencidas.length);
            
            if (recebVencidas.length > 0) {
                const valor = recebVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0);
                console.log('💰 Valor a receber vencido:', valor);
            }
            
            if (pagarVencidas.length > 0) {
                const valor = pagarVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0);
                console.log('💰 Valor a pagar vencido:', valor);
            }
            
            console.log('\n🎯 DADOS PARA O FRONTEND:');
            console.log('entradas_vencidas:', recebVencidas.length);
            console.log('saidas_vencidas:', pagarVencidas.length);
            console.log('valor_entradas_vencidas:', recebVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0));
            console.log('valor_saidas_vencidas:', pagarVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0));
        }
        
    } catch (error) {
        console.error('❌ Erro:', error.message);
        if (error.response) {
            console.error('Status:', error.response.status);
        }
    }
}

testeConasVencidas();
