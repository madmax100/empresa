// Buscar data de fim do contrato C1542

async function buscarDataFimC1542() {
    const baseURL = 'http://127.0.0.1:8000/api';
    
    console.log('🔍 BUSCAR DATA DE FIM DO CONTRATO C1542');
    console.log('=' .repeat(60));
    
    try {
        // 1. Tentar buscar dados específicos do contrato
        console.log('\n📡 Tentando buscar detalhes específicos do contrato...');
        
        try {
            const urlDetalhes = `${baseURL}/contratos_locacao/1542/`;
            console.log(`🌐 URL: ${urlDetalhes}`);
            
            const responseDetalhes = await fetch(urlDetalhes);
            console.log(`📊 Status: ${responseDetalhes.status} - ${responseDetalhes.statusText}`);
            
            if (responseDetalhes.ok) {
                const detalhes = await responseDetalhes.json();
                
                console.log('\n✅ DADOS ENCONTRADOS:');
                console.log('📋 ID:', detalhes.id);
                console.log('📄 Número:', detalhes.contrato);
                console.log('👤 Cliente:', detalhes.cliente?.nome);
                console.log('📅 Data de início:', detalhes.inicio);
                console.log('📅 Data de fim:', detalhes.fim);
                console.log('📋 Status:', detalhes.status);
                console.log('🔄 Renovado:', detalhes.renovado);
                
                // Analisar a vigência
                if (detalhes.inicio && detalhes.fim) {
                    const dataInicio = new Date(detalhes.inicio);
                    const dataFim = new Date(detalhes.fim);
                    const hoje = new Date();
                    
                    console.log('\n📊 ANÁLISE DE VIGÊNCIA:');
                    console.log(`📅 Início: ${dataInicio.toLocaleDateString()}`);
                    console.log(`📅 Fim: ${dataFim.toLocaleDateString()}`);
                    console.log(`📅 Hoje: ${hoje.toLocaleDateString()}`);
                    console.log(`✅ Contrato ativo: ${dataInicio <= hoje && dataFim >= hoje ? 'SIM' : 'NÃO'}`);
                    
                    // Calcular duração
                    const duracao = Math.ceil((dataFim - dataInicio) / (1000 * 60 * 60 * 24));
                    console.log(`⏱️ Duração total: ${duracao} dias`);
                    
                    // Verificar se agosto/2025 está na vigência
                    const agostoInicio = new Date('2025-08-01');
                    const agostoFim = new Date('2025-08-31');
                    const ativoAgosto = dataInicio <= agostoFim && dataFim >= agostoInicio;
                    console.log(`🎯 Ativo em agosto/2025: ${ativoAgosto ? 'SIM' : 'NÃO'}`);
                }
                
                return detalhes;
            } else {
                console.log('❌ Não foi possível acessar detalhes específicos');
            }
        } catch (error) {
            console.log('❌ Erro ao buscar detalhes específicos:', error.message);
        }
        
        // 2. Buscar através do endpoint de suprimentos com período amplo
        console.log('\n📡 Buscando através do endpoint de suprimentos...');
        
        // Usar período amplo para encontrar o contrato
        const periodos = [
            { inicio: '2024-01-01', fim: '2025-12-31', nome: 'Período amplo 2024-2025' },
            { inicio: '2023-01-01', fim: '2026-12-31', nome: 'Período muito amplo 2023-2026' }
        ];
        
        for (const periodo of periodos) {
            try {
                console.log(`\n🔍 Testando ${periodo.nome}:`);
                const urlSuprimentos = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=${periodo.inicio}&data_final=${periodo.fim}&contrato_id=1542`;
                
                const responseSuprimentos = await fetch(urlSuprimentos);
                if (responseSuprimentos.ok) {
                    const dataSuprimentos = await responseSuprimentos.json();
                    
                    if (dataSuprimentos.resultados && dataSuprimentos.resultados.length > 0) {
                        const contrato = dataSuprimentos.resultados[0];
                        console.log('✅ Contrato encontrado via suprimentos');
                        console.log('📋 ID:', contrato.contrato_id);
                        console.log('📄 Número:', contrato.contrato_numero);
                        
                        // Infelizmente, o endpoint de suprimentos não retorna datas de início/fim do contrato
                        // Vamos analisar as datas das notas para inferir a vigência
                        if (contrato.suprimentos && contrato.suprimentos.notas) {
                            const datas = contrato.suprimentos.notas.map(nota => nota.data).sort();
                            const primeiraData = datas[0];
                            const ultimaData = datas[datas.length - 1];
                            
                            console.log('📊 Análise das notas de suprimento:');
                            console.log(`   📅 Primeira nota: ${primeiraData}`);
                            console.log(`   📅 Última nota: ${ultimaData}`);
                            console.log(`   📝 Total de notas: ${contrato.suprimentos.notas.length}`);
                            console.log(`   💰 Valor total: R$ ${contrato.suprimentos.total_valor}`);
                        }
                        
                        break; // Sair do loop se encontrou
                    }
                }
            } catch (error) {
                console.log(`❌ Erro no período ${periodo.nome}:`, error.message);
            }
        }
        
        // 3. Tentar outros endpoints relacionados
        console.log('\n📡 Tentando outros endpoints...');
        
        const outrosEndpoints = [
            `/contratos_locacao/dashboard/C1542/`,
            `/contratos_locacao/dashboard/1542/`,
            `/contratos_locacao/itens/C1542/`,
            `/contratos_locacao/itens/1542/`
        ];
        
        for (const endpoint of outrosEndpoints) {
            try {
                console.log(`\n🔍 Testando: ${endpoint}`);
                const response = await fetch(`${baseURL}${endpoint}`);
                console.log(`📊 Status: ${response.status}`);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('✅ Dados encontrados');
                    console.log('📋 Estrutura:', Object.keys(data));
                    
                    // Procurar por campos de data
                    if (data.inicio) console.log('📅 Início:', data.inicio);
                    if (data.fim) console.log('📅 Fim:', data.fim);
                    if (data.data) console.log('📅 Data:', data.data);
                }
            } catch (error) {
                console.log(`❌ Erro: ${error.message}`);
            }
        }
        
    } catch (error) {
        console.error('❌ Erro geral:', error.message);
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('🏁 Busca concluída');
}

// Executar busca
buscarDataFimC1542().catch(console.error);
