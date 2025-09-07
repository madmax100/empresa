// Teste específico das contas vencidas com dados reais
const axios = require('axios');

async function testeContasVencidasDetalhado() {
    console.log('🔍 Teste detalhado das contas vencidas...');
    
    try {
        // Usar os mesmos parâmetros que o frontend está usando
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
            console.log('📊 Estrutura completa da resposta:');
            console.log('  - periodo:', data.periodo);
            console.log('  - filtros:', data.filtros);
            console.log('  - resumo:', data.resumo);
            
            // Verificar arrays de contas
            const receber = data.contas_a_receber || [];
            const pagar = data.contas_a_pagar || [];
            
            console.log(`📈 Contas a receber no array: ${receber.length}`);
            console.log(`📉 Contas a pagar no array: ${pagar.length}`);
            
            // Filtrar contas realmente vencidas antes de 2024-09-01
            const dataLimite = new Date('2024-09-01');
            
            const receberVencidas = receber.filter(conta => {
                const vencimento = new Date(conta.vencimento);
                return vencimento < dataLimite;
            });
            
            const pagarVencidas = pagar.filter(conta => {
                const vencimento = new Date(conta.vencimento);
                return vencimento < dataLimite;
            });
            
            console.log('\n🔍 ANÁLISE APÓS FILTRO NO FRONTEND:');
            console.log(`📈 Contas a receber realmente vencidas: ${receberVencidas.length}`);
            console.log(`📉 Contas a pagar realmente vencidas: ${pagarVencidas.length}`);
            
            if (receberVencidas.length > 0) {
                const valor = receberVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0);
                console.log(`💰 Valor a receber vencido: R$ ${valor.toFixed(2)}`);
                
                console.log('📋 Primeira conta a receber vencida:');
                console.log(`   Cliente: ${receberVencidas[0].cliente_nome}`);
                console.log(`   Valor: R$ ${receberVencidas[0].valor}`);
                console.log(`   Vencimento: ${receberVencidas[0].vencimento?.split('T')[0]}`);
            }
            
            if (pagarVencidas.length > 0) {
                const valor = pagarVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0);
                console.log(`💰 Valor a pagar vencido: R$ ${valor.toFixed(2)}`);
                
                console.log('📋 Primeira conta a pagar vencida:');
                console.log(`   Fornecedor: ${pagarVencidas[0].fornecedor_nome}`);
                console.log(`   Valor: R$ ${pagarVencidas[0].valor}`);
                console.log(`   Vencimento: ${pagarVencidas[0].vencimento?.split('T')[0]}`);
            }
            
            console.log('\n🎯 RESUMO PARA O FRONTEND:');
            console.log('📊 Dados que devem aparecer nos cartões:');
            console.log(`   Entradas Vencidas: R$ ${receberVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0).toFixed(2)}`);
            console.log(`   Saídas Vencidas: R$ ${pagarVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0).toFixed(2)}`);
            console.log(`   Quantidade Receber: ${receberVencidas.length}`);
            console.log(`   Quantidade Pagar: ${pagarVencidas.length}`);
            console.log(`   Total Vencido: ${receberVencidas.length + pagarVencidas.length}`);
            
            const saldoVencido = receberVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0) - 
                                pagarVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0);
            console.log(`   Saldo Vencido: R$ ${saldoVencido.toFixed(2)}`);
            
        } else {
            console.log('❌ Resposta vazia do endpoint');
        }
        
    } catch (error) {
        console.error('❌ Erro:', error.message);
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Dados:', error.response.data);
        }
    }
}

testeContasVencidasDetalhado();
