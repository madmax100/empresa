// Análise da vigência do contrato C1542 baseado na resposta da API

function analisarVigenciaC1542() {
    console.log('🔍 ANÁLISE DE VIGÊNCIA DO CONTRATO C1542');
    console.log('📅 Baseado na resposta da API para 01-02/08/2025');
    console.log('=' .repeat(70));
    
    // Dados do endpoint observados
    const dadosAPI = {
        periodo_consultado: {
            inicio: '2025-08-01',
            fim: '2025-08-02'
        },
        total_contratos_vigentes: 28,
        c1542_presente: false,
        cliente_centec: {
            id: 4771,
            nome: 'INSTITUTO CENTRO DE ENSINO TECNOLOGICO - CENTEC',
            contratos_ativos: [
                {
                    id: 1614,
                    numero: 'C1614',
                    vigencia: {
                        inicio: '2025-05-01',
                        fim: '2026-04-30'
                    },
                    valor_mensal: 9843.12,
                    valor_total: 118117.44
                }
            ]
        }
    };
    
    console.log('📊 DADOS OBSERVADOS NA API:');
    console.log(`   Período consultado: ${dadosAPI.periodo_consultado.inicio} a ${dadosAPI.periodo_consultado.fim}`);
    console.log(`   Total de contratos vigentes: ${dadosAPI.total_contratos_vigentes}`);
    console.log(`   C1542 presente na lista: ${dadosAPI.c1542_presente ? 'SIM' : 'NÃO'}`);
    
    console.log('\n👤 CLIENTE CENTEC (ID: 4771):');
    console.log(`   Nome: ${dadosAPI.cliente_centec.nome}`);
    console.log(`   Contratos ativos encontrados: ${dadosAPI.cliente_centec.contratos_ativos.length}`);
    
    dadosAPI.cliente_centec.contratos_ativos.forEach((contrato, index) => {
        console.log(`   ${index + 1}. ${contrato.numero}:`);
        console.log(`      - Vigência: ${contrato.vigencia.inicio} até ${contrato.vigencia.fim}`);
        console.log(`      - Valor mensal: R$ ${contrato.valor_mensal.toFixed(2)}`);
        console.log(`      - Valor total: R$ ${contrato.valor_total.toFixed(2)}`);
    });
    
    console.log('\n🔍 ANÁLISE SOBRE O C1542:');
    console.log('=' .repeat(50));
    
    // Sabemos que C1542 teve atividade em agosto com suprimentos
    const atividade_c1542_agosto = {
        valor_suprimentos: 1358.65,
        quantidade_notas: 7,
        primeira_nota: '2025-08-12',
        ultima_nota: '2025-08-28'
    };
    
    console.log('📦 ATIVIDADE C1542 EM AGOSTO (dados anteriores):');
    console.log(`   Valor suprimentos: R$ ${atividade_c1542_agosto.valor_suprimentos}`);
    console.log(`   Quantidade de notas: ${atividade_c1542_agosto.quantidade_notas}`);
    console.log(`   Período das notas: ${atividade_c1542_agosto.primeira_nota} a ${atividade_c1542_agosto.ultima_nota}`);
    
    console.log('\n🤔 POSSÍVEIS EXPLICAÇÕES:');
    console.log('1. O C1542 pode ter vigência que NÃO inclui os dias 01-02/08/2025');
    console.log('2. O C1542 pode ter encerrado antes de 01/08/2025');
    console.log('3. O C1542 pode ter iniciado após 02/08/2025');
    console.log('4. Pode haver sobreposição/substituição pelo C1614');
    
    // Hipóteses baseadas nos dados
    console.log('\n💡 HIPÓTESES DE VIGÊNCIA DO C1542:');
    console.log('=' .repeat(50));
    
    const hipoteses = [
        {
            nome: 'Hipótese 1: Encerramento anterior',
            vigencia_estimada: {
                inicio: '2024-08-10',
                fim: '2025-07-31' // Encerra antes de agosto
            },
            probabilidade: 'Alta',
            justificativa: 'C1542 não aparece na consulta de 01-02/08, mas C1614 (mesmo cliente) está ativo desde 01/05/2025'
        },
        {
            nome: 'Hipótese 2: Início posterior',
            vigencia_estimada: {
                inicio: '2025-08-03',
                fim: '2026-08-02' // Inicia após 02/08
            },
            probabilidade: 'Baixa',
            justificativa: 'Improvável, pois já existe C1614 do mesmo cliente ativo'
        },
        {
            nome: 'Hipótese 3: Vigência específica',
            vigencia_estimada: {
                inicio: '2025-08-05',
                fim: '2025-08-31' // Vigência curta em agosto
            },
            probabilidade: 'Média',
            justificativa: 'Explicaria a atividade de suprimentos apenas de 12-28/08'
        }
    ];
    
    hipoteses.forEach((hip, index) => {
        console.log(`\n${index + 1}. ${hip.nome}:`);
        console.log(`   📅 Vigência estimada: ${hip.vigencia_estimada.inicio} até ${hip.vigencia_estimada.fim}`);
        console.log(`   📊 Probabilidade: ${hip.probabilidade}`);
        console.log(`   💭 Justificativa: ${hip.justificativa}`);
    });
    
    console.log('\n🎯 CONCLUSÃO MAIS PROVÁVEL:');
    console.log('=' .repeat(50));
    console.log('📅 O contrato C1542 provavelmente teve vigência até 31/07/2025');
    console.log('🔄 Foi substituído pelo C1614 a partir de 01/05/2025 (sobreposição)');
    console.log('📦 As notas de suprimento de agosto podem ser:');
    console.log('   - Suprimentos finais/liquidação do C1542');
    console.log('   - Erro de classificação (deveriam ser do C1614)');
    console.log('   - Período de transição entre contratos');
    
    console.log('\n📋 PARA CONFIRMAR:');
    console.log('1. Consultar API com período que inclui julho/2025');
    console.log('2. Verificar se C1542 aparece em períodos anteriores');
    console.log('3. Analisar sobreposição com C1614');
    console.log('4. Verificar classificação das notas de suprimento');
    
    console.log('\n' + '='.repeat(70));
    console.log('🏁 Análise concluída');
}

// Executar análise
analisarVigenciaC1542();
