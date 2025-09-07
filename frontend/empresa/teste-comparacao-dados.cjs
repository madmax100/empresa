// Teste para comparar dados dos cartões vs análise mensal
const axios = require('axios');

async function compararDados() {
    console.log('🔍 Comparando dados dos cartões vs análise mensal...');
    
    try {
        // Simular dados do cartão (período específico com filtro de data de pagamento)
        console.log('\n📊 DADOS DOS CARTÕES (período específico):');
        const dadosCartoes = await axios.get('http://localhost:8000/contas/contas-por-data-pagamento/', {
            params: {
                data_inicio: '2025-08-01',
                data_fim: '2025-08-31',
                tipo: 'ambos',
                status: 'P'
            }
        });
        
        console.log('✅ Status cartões:', dadosCartoes.status);
        console.log('📈 Contas a receber (agosto):', dadosCartoes.data.resumo.total_contas_receber);
        console.log('💰 Valor recebido (agosto):', dadosCartoes.data.resumo.valor_total_receber);
        console.log('📉 Contas a pagar (agosto):', dadosCartoes.data.resumo.total_contas_pagar);
        console.log('💰 Valor pago (agosto):', dadosCartoes.data.resumo.valor_total_pagar);
        
        // Simular dados da análise mensal (ano completo - endpoint tradicional)
        console.log('\n📊 DADOS DA ANÁLISE MENSAL (ano completo):');
        const dadosAnalise = await axios.get('http://localhost:8000/contas/fluxo-caixa/operacional/', {
            params: {
                data_inicio: '2025-01-01',
                data_fim: '2025-12-31',
                tipo: 'todos',
                fonte: 'todas'
            }
        });
        
        console.log('✅ Status análise:', dadosAnalise.status);
        
        // Filtrar movimentos de agosto na análise mensal
        const movimentosAgosto = (dadosAnalise.data.movimentos || []).filter(m => {
            const data = new Date(m.data);
            return data.getFullYear() === 2025 && data.getMonth() === 7; // Agosto (0-based)
        });
        
        const entradasAgosto = movimentosAgosto
            .filter(m => m.tipo === 'entrada')
            .reduce((sum, m) => sum + m.valor, 0);
            
        const saidasAgosto = movimentosAgosto
            .filter(m => m.tipo === 'saida')
            .reduce((sum, m) => sum + m.valor, 0);
        
        console.log('📈 Movimentos entrada (agosto):', movimentosAgosto.filter(m => m.tipo === 'entrada').length);
        console.log('💰 Valor entradas (agosto):', entradasAgosto);
        console.log('📉 Movimentos saída (agosto):', movimentosAgosto.filter(m => m.tipo === 'saida').length);
        console.log('💰 Valor saídas (agosto):', saidasAgosto);
        
        // Comparar diferenças
        console.log('\n🔍 COMPARAÇÃO:');
        console.log('📈 Diferença entradas:', dadosCartoes.data.resumo.valor_total_receber - entradasAgosto);
        console.log('📉 Diferença saídas:', dadosCartoes.data.resumo.valor_total_pagar - saidasAgosto);
        
        if (Math.abs(dadosCartoes.data.resumo.valor_total_receber - entradasAgosto) > 0.01) {
            console.log('❌ PROBLEMA ENCONTRADO: Valores de entrada diferentes!');
            console.log('   - Cartões usam: endpoint de data de pagamento');
            console.log('   - Análise usa: endpoint tradicional de movimentos');
        }
        
        if (Math.abs(dadosCartoes.data.resumo.valor_total_pagar - saidasAgosto) > 0.01) {
            console.log('❌ PROBLEMA ENCONTRADO: Valores de saída diferentes!');
            console.log('   - Cartões usam: endpoint de data de pagamento');
            console.log('   - Análise usa: endpoint tradicional de movimentos');
        }
        
        console.log('\n🎯 SOLUÇÃO:');
        console.log('A análise mensal deveria usar o mesmo critério dos cartões (filtro por data de pagamento)');
        
    } catch (error) {
        console.error('❌ Erro na comparação:', error.message);
        if (error.response) {
            console.error('📊 Status:', error.response.status);
            console.error('📊 Dados:', error.response.data);
        }
    }
}

compararDados();
