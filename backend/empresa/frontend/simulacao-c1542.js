// Simulação específica do contrato C1542 com dados reais encontrados

function simularContratoC1542() {
    console.log('🎯 SIMULAÇÃO CONTRATO C1542 - PERÍODO AGOSTO/2025');
    console.log('=' .repeat(70));
    
    // Dados reais encontrados no teste anterior
    const contratoDados = {
        id: 1542,
        numero: 'C1542',
        cliente: {
            id: 4771,
            nome: 'INSTITUTO CENTRO DE ENSINO TECNOLOGICO - CENTEC'
        },
        suprimentos_agosto_2025: {
            valor_total: 1358.65,
            quantidade_notas: 7,
            primeira_nota: '2025-08-12',
            ultima_nota: '2025-08-28'
        }
    };
    
    console.log('📋 DADOS DO CONTRATO:');
    console.log(`   ID: ${contratoDados.id}`);
    console.log(`   Número: ${contratoDados.numero}`);
    console.log(`   Cliente: ${contratoDados.cliente.nome}`);
    console.log(`   Cliente ID: ${contratoDados.cliente.id}`);
    
    console.log('\n💰 SUPRIMENTOS EM AGOSTO/2025:');
    console.log(`   Valor total: R$ ${contratoDados.suprimentos_agosto_2025.valor_total.toFixed(2)}`);
    console.log(`   Quantidade de notas: ${contratoDados.suprimentos_agosto_2025.quantidade_notas}`);
    console.log(`   Primeira nota: ${contratoDados.suprimentos_agosto_2025.primeira_nota}`);
    console.log(`   Última nota: ${contratoDados.suprimentos_agosto_2025.ultima_nota}`);
    
    // Período de análise: agosto/2025
    const periodoInicio = new Date('2025-08-01');
    const periodoFim = new Date('2025-08-31');
    const diasPeriodo = Math.ceil((periodoFim - periodoInicio) / (1000 * 60 * 60 * 24)) + 1;
    const mesesPeriodo = diasPeriodo / 30.44;
    
    console.log('\n📅 PERÍODO DE ANÁLISE:');
    console.log(`   Início: ${periodoInicio.toLocaleDateString()}`);
    console.log(`   Fim: ${periodoFim.toLocaleDateString()}`);
    console.log(`   Dias: ${diasPeriodo} dias`);
    console.log(`   Meses: ${mesesPeriodo.toFixed(3)} meses`);
    
    // Simulações com diferentes valores mensais
    const simulacoes = [
        { valorMensal: 1000, origem: 'Exemplo básico' },
        { valorMensal: 1335, origem: 'Próximo ao valor dos suprimentos' },
        { valorMensal: 2000, origem: 'Valor médio de contrato' },
        { valorMensal: 3000, origem: 'Valor alto de contrato' },
        { valorMensal: 1358.65 / mesesPeriodo, origem: 'Reverso dos suprimentos (se 100% fosse suprimento)' }
    ];
    
    console.log('\n🧮 SIMULAÇÕES DE FATURAMENTO (baseado em diferentes valores mensais):');
    console.log('=' .repeat(70));
    
    simulacoes.forEach((sim, index) => {
        const faturamentoProporcional = sim.valorMensal * mesesPeriodo;
        const percentualSuprimentos = (contratoDados.suprimentos_agosto_2025.valor_total / faturamentoProporcional) * 100;
        
        console.log(`\n${index + 1}. ${sim.origem}:`);
        console.log(`   💵 Valor mensal (valorpacela): R$ ${sim.valorMensal.toFixed(2)}`);
        console.log(`   🧮 Cálculo: R$ ${sim.valorMensal.toFixed(2)} × ${mesesPeriodo.toFixed(3)} meses`);
        console.log(`   💹 Faturamento agosto/2025: R$ ${faturamentoProporcional.toFixed(2)}`);
        console.log(`   📊 Suprimentos representam: ${percentualSuprimentos.toFixed(1)}% do faturamento`);
        
        if (percentualSuprimentos >= 5 && percentualSuprimentos <= 25) {
            console.log(`   ✅ Percentual razoável para suprimentos`);
        } else if (percentualSuprimentos > 25) {
            console.log(`   ⚠️ Percentual alto - pode indicar valor mensal baixo`);
        } else {
            console.log(`   ⚠️ Percentual baixo - pode indicar valor mensal alto`);
        }
    });
    
    // Análise da distribuição temporal dos suprimentos
    console.log('\n📊 ANÁLISE TEMPORAL DOS SUPRIMENTOS:');
    console.log('=' .repeat(50));
    
    const notasSuprimentos = [
        { data: '2025-08-12', valor: 392.15 + 150.83, descricao: '2 notas no dia 12' },
        { data: '2025-08-19', valor: 167.90, descricao: 'Nota MP 401' },
        { data: '2025-08-21', valor: 129.48, descricao: 'Nota MP 501' },
        { data: '2025-08-26', valor: 116.36 + 185.30, descricao: '2 notas no dia 26' },
        { data: '2025-08-28', valor: 216.63, descricao: 'Nota múltiplos modelos' }
    ];
    
    let totalVerificacao = 0;
    notasSuprimentos.forEach((nota, index) => {
        totalVerificacao += nota.valor;
        console.log(`   ${index + 1}. ${nota.data}: R$ ${nota.valor.toFixed(2)} - ${nota.descricao}`);
    });
    
    console.log(`\n   📋 Total verificação: R$ ${totalVerificacao.toFixed(2)}`);
    console.log(`   📊 Total API: R$ ${contratoDados.suprimentos_agosto_2025.valor_total.toFixed(2)}`);
    console.log(`   ✅ Diferença: R$ ${Math.abs(totalVerificacao - contratoDados.suprimentos_agosto_2025.valor_total).toFixed(2)}`);
    
    // Sugestão de valor mensal mais provável
    console.log('\n💡 ANÁLISE E SUGESTÃO:');
    console.log('=' .repeat(50));
    
    // Assumindo que suprimentos representam entre 10% a 20% do faturamento
    const percentualEstimado = 15; // 15% é uma média razoável
    const faturamentoEstimado = contratoDados.suprimentos_agosto_2025.valor_total / (percentualEstimado / 100);
    const valorMensalEstimado = faturamentoEstimado / mesesPeriodo;
    
    console.log(`   📊 Assumindo suprimentos = ${percentualEstimado}% do faturamento:`);
    console.log(`   💹 Faturamento estimado agosto: R$ ${faturamentoEstimado.toFixed(2)}`);
    console.log(`   💵 Valor mensal estimado: R$ ${valorMensalEstimado.toFixed(2)}`);
    console.log(`   📋 Valor anual estimado: R$ ${(valorMensalEstimado * 12).toFixed(2)}`);
    
    console.log('\n🎯 RESULTADO ESPERADO NO DASHBOARD:');
    console.log(`   Se valorpacela = R$ ${valorMensalEstimado.toFixed(2)}`);
    console.log(`   Faturamento proporcional agosto/2025 = R$ ${faturamentoEstimado.toFixed(2)}`);
    console.log(`   Suprimentos encontrados = R$ ${contratoDados.suprimentos_agosto_2025.valor_total.toFixed(2)}`);
    
    console.log('\n' + '='.repeat(70));
    console.log('🏁 Simulação concluída');
}

// Executar simulação
simularContratoC1542();
