// Teste específico para o contrato c1542 no período de 01/08/2025 a 31/08/2025

async function testarContratoC1542() {
    const baseURL = 'http://127.0.0.1:8000/api';
    
    // Período de teste conforme solicitado
    const dataInicial = '2025-08-01';
    const dataFinal = '2025-08-31';
    
    console.log('🔍 TESTE CONTRATO C1542');
    console.log('📅 Período: 01/08/2025 a 31/08/2025');
    console.log('=' .repeat(60));
    
    try {
        // 1. Buscar todos os contratos no período
        const url = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=${dataInicial}&data_final=${dataFinal}`;
        console.log('\n📡 Chamando API:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status} - ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('\n📊 Resposta da API recebida');
        console.log('Total de contratos encontrados:', data.resultados?.length || 0);
        
        // 2. Procurar especificamente o contrato c1542
        let contratoC1542 = null;
        
        if (data.resultados) {
            contratoC1542 = data.resultados.find(item => {
                // Verificar se é o contrato c1542 (pode estar como número do contrato)
                return item.contrato_numero === 'c1542' || 
                       item.contrato_numero === 'C1542' ||
                       item.contrato_numero === '1542';
            });
        }
        
        console.log('\n🎯 RESULTADO BUSCA C1542:');
        if (contratoC1542) {
            console.log('✅ Contrato C1542 ENCONTRADO!');
            console.log('📋 Detalhes do contrato:');
            console.log('   - ID:', contratoC1542.contrato_id);
            console.log('   - Número:', contratoC1542.contrato_numero);
            console.log('   - Cliente:', contratoC1542.cliente?.nome || 'N/A');
            console.log('   - Cliente ID:', contratoC1542.cliente?.id || 'N/A');
            
            if (contratoC1542.suprimentos) {
                console.log('\n💰 Suprimentos no período:');
                console.log('   - Valor total:', contratoC1542.suprimentos.total_valor || 0);
                console.log('   - Quantidade de notas:', contratoC1542.suprimentos.quantidade_notas || 0);
                
                if (contratoC1542.suprimentos.notas && contratoC1542.suprimentos.notas.length > 0) {
                    console.log('\n📝 Notas de suprimento:');
                    contratoC1542.suprimentos.notas.forEach((nota, index) => {
                        console.log(`   ${index + 1}. Nota ${nota.numero_nota}:`);
                        console.log(`      - Data: ${nota.data}`);
                        console.log(`      - Valor: R$ ${nota.valor_total_nota}`);
                        console.log(`      - Operação: ${nota.operacao}`);
                        console.log(`      - CFOP: ${nota.cfop}`);
                        if (nota.obs) console.log(`      - Obs: ${nota.obs}`);
                    });
                }
            }
        } else {
            console.log('❌ Contrato C1542 NÃO ENCONTRADO no período especificado');
            console.log('\n📋 Contratos encontrados no período:');
            if (data.resultados && data.resultados.length > 0) {
                data.resultados.forEach((contrato, index) => {
                    console.log(`   ${index + 1}. ${contrato.contrato_numero} - ${contrato.cliente?.nome || 'N/A'}`);
                });
            } else {
                console.log('   Nenhum contrato encontrado no período');
            }
        }
        
        // 3. Tentar buscar detalhes específicos do contrato se soubermos o ID
        console.log('\n🔍 Tentando buscar contrato por diferentes métodos...');
        
        // Tentar buscar diretamente se temos dados mock ou outros endpoints
        try {
            const mockResponse = await fetch(`${baseURL}/contratos_locacao/`);
            if (mockResponse.ok) {
                const mockData = await mockResponse.json();
                console.log('📊 Endpoint geral de contratos acessível');
                // Procurar c1542 nos dados gerais se disponível
            }
        } catch (err) {
            console.log('ℹ️ Endpoint geral não disponível');
        }
        
        // 4. Teste de cálculo de período para agosto/2025
        console.log('\n🧮 TESTE DE CÁLCULO PARA AGOSTO/2025:');
        const inicioAgosto = new Date('2025-08-01');
        const fimAgosto = new Date('2025-08-31');
        const diasAgosto = Math.ceil((fimAgosto - inicioAgosto) / (1000 * 60 * 60 * 24)) + 1;
        const mesesAgosto = diasAgosto / 30.44;
        
        console.log(`📅 Período de teste: ${inicioAgosto.toLocaleDateString()} a ${fimAgosto.toLocaleDateString()}`);
        console.log(`⏱️ Dias no período: ${diasAgosto} dias`);
        console.log(`📊 Equivalente em meses: ${mesesAgosto.toFixed(3)} meses`);
        
        // Se o contrato tivesse valor mensal de R$ 1000, o cálculo seria:
        const valorExemplo = 1000;
        const faturamentoExemplo = valorExemplo * mesesAgosto;
        console.log(`💡 Exemplo: Se valorpacela = R$ ${valorExemplo.toFixed(2)}`);
        console.log(`   Faturamento proporcional = R$ ${valorExemplo.toFixed(2)} × ${mesesAgosto.toFixed(3)} = R$ ${faturamentoExemplo.toFixed(2)}`);
        
    } catch (error) {
        console.error('❌ Erro durante o teste:', error.message);
        console.log('\n📋 Informações do erro:');
        console.log('   - Tipo:', error.name);
        console.log('   - Mensagem:', error.message);
        if (error.stack) {
            console.log('   - Stack:', error.stack.split('\n')[0]);
        }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('🏁 Teste concluído');
}

// Executar o teste
testarContratoC1542().catch(console.error);
