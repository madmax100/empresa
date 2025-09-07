// Debug do dashboard operacional
const axios = require('axios');

async function debugDashboardOperacional() {
    console.log('🔍 Debug do Dashboard Operacional...');
    
    try {
        // Simular os filtros que estão sendo usados no frontend
        const filtros = {
            dataInicial: '2024-09-01',
            dataFinal: '2025-09-03', // Data atual
            tipo: 'todos',
            fonte: 'todos'
        };
        
        console.log('📊 Filtros sendo usados:', filtros);
        
        // 1. Testar endpoint do dashboard operacional
        console.log('\n1️⃣ Testando endpoint do dashboard operacional...');
        const dashboardResponse = await axios.get('http://localhost:8000/dashboard/operacional/', {
            params: filtros
        });
        
        console.log('✅ Dashboard Status:', dashboardResponse.status);
        const dashboardData = dashboardResponse.data;
        
        if (dashboardData) {
            console.log('📋 Filtros do dashboard:', dashboardData.filtros);
            console.log('📊 Resumo do dashboard:', dashboardData.resumo);
            console.log('📈 Movimentos encontrados:', dashboardData.movimentos?.length || 0);
        }
        
        // 2. Testar endpoint de contas vencidas com os mesmos filtros
        console.log('\n2️⃣ Testando endpoint de contas vencidas...');
        const contasVencidasParams = {
            data_inicio: '2020-01-01',
            data_fim: filtros.dataInicial, // Vencidas antes do período
            tipo: 'ambos',
            status: 'A'
        };
        
        console.log('📅 Parâmetros para contas vencidas:', contasVencidasParams);
        
        const vencidasResponse = await axios.get('http://localhost:8000/contas/contas-por-data-vencimento/', {
            params: contasVencidasParams
        });
        
        console.log('✅ Vencidas Status:', vencidasResponse.status);
        const vencidasData = vencidasResponse.data;
        
        if (vencidasData) {
            console.log('📋 Período vencidas:', vencidasData.periodo);
            console.log('📊 Resumo vencidas:', vencidasData.resumo);
            
            // Analisar contas que realmente venceram antes do período
            const dataLimite = new Date(filtros.dataInicial);
            console.log('📅 Data limite para contas vencidas:', dataLimite.toISOString().split('T')[0]);
            
            const recebVencidas = (vencidasData.contas_a_receber || []).filter(conta => {
                const vencimento = new Date(conta.vencimento);
                return vencimento < dataLimite;
            });
            
            const pagarVencidas = (vencidasData.contas_a_pagar || []).filter(conta => {
                const vencimento = new Date(conta.vencimento);
                return vencimento < dataLimite;
            });
            
            console.log('\n🔍 ANÁLISE DETALHADA:');
            console.log('📈 Total contas a receber do endpoint:', vencidasData.contas_a_receber?.length || 0);
            console.log('📈 Contas a receber realmente vencidas:', recebVencidas.length);
            console.log('📉 Total contas a pagar do endpoint:', vencidasData.contas_a_pagar?.length || 0);
            console.log('📉 Contas a pagar realmente vencidas:', pagarVencidas.length);
            
            if (recebVencidas.length > 0) {
                const valorReceber = recebVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0);
                console.log('💰 Valor a receber vencido:', valorReceber);
                
                console.log('📋 Primeiras 3 contas a receber vencidas:');
                recebVencidas.slice(0, 3).forEach((conta, i) => {
                    console.log(`   ${i+1}. ${conta.cliente_nome}: R$ ${conta.valor} (venc: ${conta.vencimento?.split('T')[0]})`);
                });
            }
            
            if (pagarVencidas.length > 0) {
                const valorPagar = pagarVencidas.reduce((sum, conta) => sum + parseFloat(conta.valor || 0), 0);
                console.log('💰 Valor a pagar vencido:', valorPagar);
                
                console.log('📋 Primeiras 3 contas a pagar vencidas:');
                pagarVencidas.slice(0, 3).forEach((conta, i) => {
                    console.log(`   ${i+1}. ${conta.fornecedor_nome || conta.cliente_nome}: R$ ${conta.valor} (venc: ${conta.vencimento?.split('T')[0]})`);
                });
            }
            
            console.log('\n🎯 RESUMO FINAL:');
            console.log('✅ Dashboard operacional funcional:', !!dashboardData);
            console.log('✅ Endpoint vencidas funcional:', !!vencidasData);
            console.log('📊 Contas vencidas encontradas:', recebVencidas.length + pagarVencidas.length);
            
            if (recebVencidas.length === 0 && pagarVencidas.length === 0) {
                console.log('⚠️ POSSÍVEL PROBLEMA: Não foram encontradas contas vencidas');
                console.log('💡 Verificar se o período selecionado está correto');
                console.log('💡 Verificar se há contas com status "A" no banco');
            }
        }
        
    } catch (error) {
        console.error('❌ Erro no debug:', error.message);
        if (error.response) {
            console.error('📊 Status:', error.response.status);
            console.error('📊 Dados do erro:', error.response.data);
        }
    }
}

debugDashboardOperacional();
