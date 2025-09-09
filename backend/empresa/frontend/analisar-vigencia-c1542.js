// Análise detalhada das notas do contrato C1542 para inferir data de fim

async function analisarVigenciaC1542() {
    const baseURL = 'http://127.0.0.1:8000/api';
    
    console.log('🔍 ANÁLISE DA VIGÊNCIA DO CONTRATO C1542');
    console.log('=' .repeat(70));
    
    try {
        // Buscar com período muito amplo para pegar todas as notas
        const periodos = [
            { inicio: '2023-01-01', fim: '2026-12-31', nome: 'Período 2023-2026' },
            { inicio: '2024-01-01', fim: '2025-12-31', nome: 'Período 2024-2025' },
            { inicio: '2025-01-01', fim: '2025-12-31', nome: 'Apenas 2025' }
        ];
        
        for (const periodo of periodos) {
            console.log(`\n📅 ANALISANDO ${periodo.nome.toUpperCase()}:`);
            console.log('-'.repeat(50));
            
            try {
                const url = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=${periodo.inicio}&data_final=${periodo.fim}&contrato_id=1542`;
                const response = await fetch(url);
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.resultados && data.resultados.length > 0) {
                        const contrato = data.resultados[0];
                        
                        console.log(`✅ Contrato encontrado no período`);
                        console.log(`💰 Valor total suprimentos: R$ ${contrato.suprimentos.total_valor}`);
                        console.log(`📝 Total de notas: ${contrato.suprimentos.quantidade_notas}`);
                        
                        if (contrato.suprimentos.notas) {
                            // Analisar todas as datas
                            const datas = contrato.suprimentos.notas.map(nota => nota.data).sort();
                            const primeiraData = datas[0];
                            const ultimaData = datas[datas.length - 1];
                            
                            console.log(`📅 Primeira nota: ${primeiraData}`);
                            console.log(`📅 Última nota: ${ultimaData}`);
                            
                            // Agrupar por ano e mês
                            const porAnoMes = {};
                            contrato.suprimentos.notas.forEach(nota => {
                                const data = new Date(nota.data);
                                const anoMes = `${data.getFullYear()}-${String(data.getMonth() + 1).padStart(2, '0')}`;
                                
                                if (!porAnoMes[anoMes]) {
                                    porAnoMes[anoMes] = { count: 0, valor: 0 };
                                }
                                porAnoMes[anoMes].count++;
                                porAnoMes[anoMes].valor += nota.valor_total_nota;
                            });
                            
                            console.log('\n📊 DISTRIBUIÇÃO POR MÊS:');
                            Object.keys(porAnoMes).sort().forEach(anoMes => {
                                const dados = porAnoMes[anoMes];
                                console.log(`   ${anoMes}: ${dados.count} notas, R$ ${dados.valor.toFixed(2)}`);
                            });
                            
                            // Verificar atividade recente para inferir se ainda está ativo
                            const ultimaDataObj = new Date(ultimaData);
                            const hoje = new Date();
                            const diasSemNota = Math.ceil((hoje - ultimaDataObj) / (1000 * 60 * 60 * 24));
                            
                            console.log('\n🔍 ANÁLISE DE ATIVIDADE:');
                            console.log(`📅 Última atividade: ${ultimaData} (${ultimaDataObj.toLocaleDateString()})`);
                            console.log(`⏱️ Dias sem atividade: ${diasSemNota} dias`);
                            
                            if (diasSemNota <= 30) {
                                console.log('✅ Contrato provavelmente ATIVO (atividade recente)');
                            } else if (diasSemNota <= 90) {
                                console.log('⚠️ Contrato possivelmente ativo (atividade moderada)');
                            } else {
                                console.log('❌ Contrato possivelmente INATIVO (sem atividade recente)');
                            }
                            
                            // Analisar padrão de atividade para inferir término
                            console.log('\n📈 PADRÃO DE ATIVIDADE MENSAL:');
                            const mesesOrdenados = Object.keys(porAnoMes).sort();
                            const ultimosTresMeses = mesesOrdenados.slice(-3);
                            
                            ultimosTresMeses.forEach(mes => {
                                const dados = porAnoMes[mes];
                                console.log(`   ${mes}: ${dados.count} notas, R$ ${dados.valor.toFixed(2)}`);
                            });
                            
                            // Verificar se há atividade em setembro/2025 ou depois
                            const atividadeSetembro = porAnoMes['2025-09'];
                            const atividadeOutubro = porAnoMes['2025-10'];
                            
                            console.log('\n🎯 INFERÊNCIA DA DATA DE FIM:');
                            if (atividadeSetembro) {
                                console.log(`✅ Atividade em setembro/2025: ${atividadeSetembro.count} notas`);
                                console.log('📅 Data de fim estimada: Posterior a setembro/2025');
                            } else {
                                console.log('❌ Sem atividade em setembro/2025');
                                console.log('📅 Data de fim estimada: Entre agosto e setembro/2025');
                            }
                            
                            if (atividadeOutubro) {
                                console.log(`✅ Atividade em outubro/2025: ${atividadeOutubro.count} notas`);
                                console.log('📅 Data de fim estimada: Posterior a outubro/2025');
                            }
                        }
                    } else {
                        console.log('❌ Contrato não encontrado no período');
                    }
                } else {
                    console.log(`❌ Erro na API: ${response.status}`);
                }
                
            } catch (error) {
                console.log(`❌ Erro: ${error.message}`);
            }
        }
        
        // Buscar especificamente dados de setembro e outubro 2025
        console.log('\n🔍 VERIFICAÇÃO ESPECÍFICA - SETEMBRO E OUTUBRO 2025:');
        console.log('-'.repeat(60));
        
        const mesesVerificar = [
            { inicio: '2025-09-01', fim: '2025-09-30', nome: 'Setembro 2025' },
            { inicio: '2025-10-01', fim: '2025-10-31', nome: 'Outubro 2025' },
            { inicio: '2025-11-01', fim: '2025-11-30', nome: 'Novembro 2025' }
        ];
        
        for (const mes of mesesVerificar) {
            try {
                const url = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=${mes.inicio}&data_final=${mes.fim}&contrato_id=1542`;
                const response = await fetch(url);
                
                if (response.ok) {
                    const data = await response.json();
                    const temAtividade = data.resultados && data.resultados.length > 0 && 
                                       data.resultados[0].suprimentos.quantidade_notas > 0;
                    
                    console.log(`📅 ${mes.nome}: ${temAtividade ? '✅ ATIVO' : '❌ SEM ATIVIDADE'}`);
                    
                    if (temAtividade) {
                        const notas = data.resultados[0].suprimentos.quantidade_notas;
                        const valor = data.resultados[0].suprimentos.total_valor;
                        console.log(`   📝 ${notas} notas, R$ ${valor.toFixed(2)}`);
                    }
                } else {
                    console.log(`📅 ${mes.nome}: ❌ Erro na consulta`);
                }
            } catch (error) {
                console.log(`📅 ${mes.nome}: ❌ Erro: ${error.message}`);
            }
        }
        
    } catch (error) {
        console.error('❌ Erro geral:', error.message);
    }
    
    console.log('\n' + '='.repeat(70));
    console.log('🏁 Análise concluída');
}

// Executar análise
analisarVigenciaC1542().catch(console.error);
