// Verificação de vigência do contrato C1542 em agosto de 2025

async function verificarVigenciaC1542() {
    const baseURL = 'http://127.0.0.1:8000/api';
    
    console.log('🔍 VERIFICAÇÃO DE VIGÊNCIA - CONTRATO C1542');
    console.log('📅 Período: Agosto de 2025 (01/08/2025 a 31/08/2025)');
    console.log('=' .repeat(60));
    
    try {
        // 1. Buscar dados do contrato em agosto de 2025
        const dataInicial = '2025-08-01';
        const dataFinal = '2025-08-31';
        
        const url = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=${dataInicial}&data_final=${dataFinal}`;
        console.log('\n📡 Consultando API para agosto/2025...');
        console.log('🌐 URL:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} - ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Resposta da API recebida');
        
        // 2. Procurar especificamente o contrato C1542
        const contratoC1542 = data.resultados?.find(item => {
            return item.contrato_numero === 'C1542' || 
                   item.contrato_numero === 'c1542' ||
                   item.contrato_numero === '1542' ||
                   item.contrato_id === 1542;
        });
        
        console.log('\n🎯 RESULTADO DA VERIFICAÇÃO:');
        console.log('=' .repeat(40));
        
        if (contratoC1542) {
            console.log('✅ CONTRATO C1542 ESTÁ VIGENTE EM AGOSTO/2025');
            console.log('\n📋 Evidências de vigência:');
            console.log(`   🆔 ID do contrato: ${contratoC1542.contrato_id}`);
            console.log(`   📄 Número: ${contratoC1542.contrato_numero}`);
            console.log(`   👤 Cliente: ${contratoC1542.cliente?.nome || 'N/A'}`);
            console.log(`   🆔 Cliente ID: ${contratoC1542.cliente?.id || 'N/A'}`);
            
            if (contratoC1542.suprimentos) {
                console.log('\n💰 Atividade em agosto/2025:');
                console.log(`   💵 Valor total de suprimentos: R$ ${contratoC1542.suprimentos.total_valor || 0}`);
                console.log(`   📝 Quantidade de notas: ${contratoC1542.suprimentos.quantidade_notas || 0}`);
                
                if (contratoC1542.suprimentos.notas && contratoC1542.suprimentos.notas.length > 0) {
                    console.log('\n📅 Datas das atividades:');
                    
                    const datas = contratoC1542.suprimentos.notas.map(nota => nota.data).sort();
                    const primeiraAtividade = datas[0];
                    const ultimaAtividade = datas[datas.length - 1];
                    
                    console.log(`   🎯 Primeira atividade: ${new Date(primeiraAtividade).toLocaleDateString()}`);
                    console.log(`   🎯 Última atividade: ${new Date(ultimaAtividade).toLocaleDateString()}`);
                    console.log(`   📊 Total de dias com atividade: ${datas.length}`);
                    
                    // Verificar distribuição ao longo do mês
                    const diasUnicos = [...new Set(datas)].length;
                    console.log(`   📈 Dias únicos com atividade: ${diasUnicos}`);
                    
                    if (diasUnicos >= 3) {
                        console.log('   ✅ Atividade distribuída ao longo do mês - FORTE INDICAÇÃO DE VIGÊNCIA');
                    } else if (diasUnicos >= 2) {
                        console.log('   ✅ Múltiplas datas de atividade - INDICAÇÃO DE VIGÊNCIA');
                    } else {
                        console.log('   ⚠️ Atividade concentrada em poucos dias');
                    }
                }
            }
            
            // 3. Análise de continuidade (verificar outros meses próximos)
            console.log('\n🔍 Verificando continuidade em meses adjacentes...');
            
            try {
                // Julho 2025
                const urlJulho = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=2025-07-01&data_final=2025-07-31`;
                const responseJulho = await fetch(urlJulho);
                let ativoJulho = false;
                
                if (responseJulho.ok) {
                    const dataJulho = await responseJulho.json();
                    ativoJulho = dataJulho.resultados?.some(item => 
                        item.contrato_numero === 'C1542' || item.contrato_id === 1542
                    );
                }
                
                // Setembro 2025
                const urlSetembro = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=2025-09-01&data_final=2025-09-30`;
                const responseSetembro = await fetch(urlSetembro);
                let ativoSetembro = false;
                
                if (responseSetembro.ok) {
                    const dataSetembro = await responseSetembro.json();
                    ativoSetembro = dataSetembro.resultados?.some(item => 
                        item.contrato_numero === 'C1542' || item.contrato_id === 1542
                    );
                }
                
                console.log('\n📊 Continuidade do contrato:');
                console.log(`   📅 Julho 2025: ${ativoJulho ? '✅ Ativo' : '❌ Sem atividade'}`);
                console.log(`   📅 Agosto 2025: ✅ Ativo (confirmado)`);
                console.log(`   📅 Setembro 2025: ${ativoSetembro ? '✅ Ativo' : '❌ Sem atividade'}`);
                
                if (ativoJulho && ativoSetembro) {
                    console.log('   🎯 CONTRATO COM CONTINUIDADE CONFIRMADA');
                } else if (ativoJulho || ativoSetembro) {
                    console.log('   📈 Contrato com atividade em meses adjacentes');
                } else {
                    console.log('   ⚠️ Atividade isolada em agosto (pode ser pontual)');
                }
                
            } catch (err) {
                console.log('   ⚠️ Não foi possível verificar meses adjacentes:', err.message);
            }
            
        } else {
            console.log('❌ CONTRATO C1542 NÃO ENCONTRADO EM AGOSTO/2025');
            console.log('\n📋 Possíveis razões:');
            console.log('   • Contrato não estava vigente no período');
            console.log('   • Sem atividade de suprimentos no mês');
            console.log('   • Contrato suspenso temporariamente');
            console.log('   • Dados não disponíveis na API para este período');
            
            console.log(`\n📊 Total de contratos ativos em agosto/2025: ${data.resultados?.length || 0}`);
            
            if (data.resultados && data.resultados.length > 0) {
                console.log('\n📋 Outros contratos ativos no período:');
                data.resultados.slice(0, 5).forEach((contrato, index) => {
                    console.log(`   ${index + 1}. ${contrato.contrato_numero} - ${contrato.cliente?.nome || 'N/A'}`);
                });
                if (data.resultados.length > 5) {
                    console.log(`   ... e mais ${data.resultados.length - 5} contratos`);
                }
            }
        }
        
        // 4. Conclusão final
        console.log('\n🏁 CONCLUSÃO:');
        console.log('=' .repeat(40));
        
        if (contratoC1542) {
            console.log('✅ O contrato C1542 ESTÁ VIGENTE em agosto de 2025');
            console.log('📋 Evidência: Presença de atividades de suprimentos no período');
            console.log('💡 Recomendação: Contrato pode ser incluído em relatórios e cálculos financeiros para agosto/2025');
        } else {
            console.log('❌ O contrato C1542 NÃO ESTÁ VIGENTE em agosto de 2025');
            console.log('📋 Evidência: Ausência de atividades registradas no período');
            console.log('💡 Recomendação: Verificar status do contrato ou período de vigência');
        }
        
    } catch (error) {
        console.error('❌ Erro durante a verificação:', error.message);
        console.log('\n📋 Não foi possível confirmar a vigência devido a erro técnico');
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('🔚 Verificação concluída');
}

// Executar verificação
verificarVigenciaC1542().catch(console.error);
