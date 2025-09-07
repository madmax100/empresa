// Teste direto da API no browser
console.log('🚀 Testando API diretamente do browser...');

async function testarAPIBrowser() {
    try {
        const url = 'http://localhost:8000/contas/contas-por-data-vencimento/?data_inicio=2020-01-01&data_fim=2024-09-01&tipo=ambos&status=A';
        
        console.log('📡 Fazendo fetch para:', url);
        
        const response = await fetch(url);
        
        console.log('✅ Status:', response.status);
        console.log('📊 Headers:', response.headers);
        
        if (response.ok) {
            const data = await response.json();
            console.log('📋 Dados recebidos:', data);
            
            if (data && data.contas_a_receber && data.contas_a_pagar) {
                const receber = data.contas_a_receber.length;
                const pagar = data.contas_a_pagar.length;
                const valorReceber = data.resumo?.valor_total_receber || 0;
                const valorPagar = data.resumo?.valor_total_pagar || 0;
                
                console.log('🎯 RESUMO:');
                console.log(`📈 Contas a receber: ${receber} (R$ ${valorReceber})`);
                console.log(`📉 Contas a pagar: ${pagar} (R$ ${valorPagar})`);
                console.log(`💰 Saldo: R$ ${valorReceber - valorPagar}`);
                
                return {
                    success: true,
                    receber,
                    pagar,
                    valorReceber,
                    valorPagar
                };
            } else {
                console.warn('⚠️ Estrutura de dados inesperada');
                return { success: false, error: 'Estrutura inválida' };
            }
        } else {
            console.error('❌ Erro HTTP:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('📄 Corpo do erro:', errorText);
            return { success: false, error: `HTTP ${response.status}` };
        }
        
    } catch (error) {
        console.error('❌ Erro de fetch:', error);
        return { success: false, error: error.message };
    }
}

// Executar o teste
testarAPIBrowser().then(result => {
    console.log('🏁 Resultado final:', result);
});

console.log('⏳ Teste iniciado... aguarde os resultados no console.');
