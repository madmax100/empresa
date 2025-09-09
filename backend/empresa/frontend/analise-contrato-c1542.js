// Teste detalhado do contrato C1542 - buscar dados financeiros completos

async function buscarDetalhesContratoC1542() {
    const baseURL = 'http://127.0.0.1:8000/api';
    
    console.log('🔍 ANÁLISE DETALHADA CONTRATO C1542');
    console.log('📅 Período de teste: 01/08/2025 a 31/08/2025');
    console.log('=' .repeat(70));
    
    try {
        // 1. Buscar dados gerais de contratos (sem filtro de período)
        console.log('\n📡 Buscando dados gerais do contrato...');
        
        // Tentar endpoint geral primeiro
        let contratoEncontrado = null;
        
        try {
            const urlGeral = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=2024-01-01&data_final=2025-12-31`;
            console.log('🌐 URL:', urlGeral);
            
            const response = await fetch(urlGeral);
            if (response.ok) {
                const data = await response.json();
                
                // Procurar C1542
                contratoEncontrado = data.resultados?.find(item => {
                    return item.contrato_numero === 'C1542' || 
                           item.contrato_numero === 'c1542' ||
                           item.contrato_numero === '1542' ||
                           item.contrato_id === 1542;
                });
                
                console.log('✅ Dados gerais obtidos');
                console.log('📊 Total de contratos no sistema:', data.resultados?.length || 0);
            }
        } catch (err) {
            console.log('⚠️ Erro ao buscar dados gerais:', err.message);
        }
        
        // 2. Tentar buscar detalhes específicos do contrato por ID
        if (contratoEncontrado || true) { // Sempre tentar, mesmo sem encontrar nos gerais
            console.log('\n🎯 Tentando buscar detalhes específicos do contrato ID 1542...');
            
            try {
                const urlDetalhes = `${baseURL}/contratos_locacao/1542/`;
                console.log('🌐 URL detalhes:', urlDetalhes);
                
                const responseDetalhes = await fetch(urlDetalhes);
                if (responseDetalhes.ok) {
                    const detalhes = await responseDetalhes.json();
                    
                    console.log('✅ DETALHES COMPLETOS DO CONTRATO C1542:');
                    console.log('=' .repeat(50));
                    console.log('📋 ID:', detalhes.id);
                    console.log('📄 Número do contrato:', detalhes.contrato);
                    console.log('👤 Cliente:', detalhes.cliente?.nome);
                    console.log('🆔 Cliente ID:', detalhes.cliente?.id);
                    console.log('💰 Valor do contrato:', detalhes.valorcontrato);
                    console.log('💵 Valor da parcela (MENSAL):', detalhes.valorpacela);
                    console.log('🔢 Número de parcelas:', detalhes.numeroparcelas);
                    console.log('📅 Início:', detalhes.inicio);
                    console.log('📅 Fim:', detalhes.fim);
                    console.log('📋 Tipo:', detalhes.tipocontrato);
                    console.log('🔄 Renovado:', detalhes.renovado);
                    console.log('📊 Status:', detalhes.status);
                    
                    if (detalhes.total_recebido !== undefined) {
                        console.log('💹 Total recebido:', detalhes.total_recebido);
                    }
                    if (detalhes.total_gasto !== undefined) {
                        console.log('💸 Total gasto:', detalhes.total_gasto);
                    }
                    if (detalhes.margem !== undefined) {
                        console.log('📈 Margem:', detalhes.margem);
                    }
                    
                    // 3. Análise do período agosto/2025
                    console.log('\n🧮 ANÁLISE PERÍODO AGOSTO/2025:');
                    console.log('=' .repeat(50));
                    
                    const inicioContrato = new Date(detalhes.inicio);
                    const fimContrato = new Date(detalhes.fim);
                    const inicioFiltro = new Date('2025-08-01');
                    const fimFiltro = new Date('2025-08-31');
                    
                    console.log('📅 Período do contrato:', inicioContrato.toLocaleDateString(), 'até', fimContrato.toLocaleDateString());
                    console.log('🎯 Período de análise:', inicioFiltro.toLocaleDateString(), 'até', fimFiltro.toLocaleDateString());
                    
                    // Verificar sobreposição
                    const contratoAtivoNoPeriodo = inicioContrato <= fimFiltro && fimContrato >= inicioFiltro;
                    console.log('✅ Contrato ativo no período:', contratoAtivoNoPeriodo ? 'SIM' : 'NÃO');
                    
                    if (contratoAtivoNoPeriodo) {
                        // Calcular período efetivo
                        const inicioEfetivo = new Date(Math.max(inicioContrato.getTime(), inicioFiltro.getTime()));
                        const fimEfetivo = new Date(Math.min(fimContrato.getTime(), fimFiltro.getTime()));
                        
                        const diasEfetivos = Math.ceil((fimEfetivo - inicioEfetivo) / (1000 * 60 * 60 * 24)) + 1;
                        const mesesEfetivos = diasEfetivos / 30.44;
                        
                        console.log('📊 Período efetivo:', inicioEfetivo.toLocaleDateString(), 'até', fimEfetivo.toLocaleDateString());
                        console.log('⏱️ Dias efetivos:', diasEfetivos, 'dias');
                        console.log('📈 Meses efetivos:', mesesEfetivos.toFixed(3), 'meses');
                        
                        // Calcular faturamento
                        const valorMensal = detalhes.valorpacela || detalhes.valorcontrato || 0;
                        const origemValor = detalhes.valorpacela ? 'valorpacela (valor mensal)' : 
                                          detalhes.valorcontrato ? 'valorcontrato (fallback)' : 'zero';
                        
                        const faturamentoProporcional = valorMensal * mesesEfetivos;
                        
                        console.log('\n💰 CÁLCULO FINANCEIRO:');
                        console.log('💵 Valor mensal utilizado: R$', valorMensal.toFixed(2), `(${origemValor})`);
                        console.log('🧮 Cálculo: R$', valorMensal.toFixed(2), '×', mesesEfetivos.toFixed(3), 'meses');
                        console.log('💹 Faturamento proporcional: R$', faturamentoProporcional.toFixed(2));
                        
                        // Comparar com dados de suprimentos encontrados anteriormente
                        console.log('\n📦 COMPARAÇÃO COM SUPRIMENTOS:');
                        console.log('💰 Valor suprimentos encontrado: R$ 1.358,65');
                        console.log('💹 Faturamento proporcional calculado: R$', faturamentoProporcional.toFixed(2));
                        
                        if (faturamentoProporcional > 0) {
                            const percentualSuprimentos = (1358.65 / faturamentoProporcional) * 100;
                            console.log('📊 Suprimentos representam:', percentualSuprimentos.toFixed(1), '% do faturamento');
                        }
                    }
                    
                } else {
                    console.log('❌ Não foi possível obter detalhes específicos do contrato');
                    console.log('Status:', responseDetalhes.status, responseDetalhes.statusText);
                }
                
            } catch (err) {
                console.log('⚠️ Erro ao buscar detalhes específicos:', err.message);
            }
        }
        
    } catch (error) {
        console.error('❌ Erro geral:', error.message);
    }
    
    console.log('\n' + '='.repeat(70));
    console.log('🏁 Análise concluída');
}

// Executar análise
buscarDetalhesContratoC1542().catch(console.error);
