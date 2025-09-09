// Teste manual do serviço de contratos
async function testarContratos() {
  const baseURL = 'http://127.0.0.1:8000/api';
  
  try {
    // 1. Testar chamada direta à API
    console.log('🔍 Testando chamada à API...');
    const url = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=2025-01-01&data_final=2025-12-31`;
    
    const response = await fetch(url);
    console.log('📋 Status da resposta:', response.status);
    
    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Dados recebidos da API:');
    console.log('- Total de resultados:', data?.resultados?.length || 0);
    console.log('- Estrutura da resposta:', Object.keys(data));
    
    if (data.resultados && data.resultados.length > 0) {
      console.log('🔍 Primeiro resultado:');
      console.log(JSON.stringify(data.resultados[0], null, 2));
      
      // 2. Testar mapeamento manual
      console.log('\n📊 Testando mapeamento...');
      const primeiroContrato = data.resultados[0];
      
      const contratoMapeado = {
        id: primeiroContrato.contrato_id || 1,
        contrato: primeiroContrato.contrato_numero || `C${primeiroContrato.contrato_id}`,
        cliente: {
          id: primeiroContrato.cliente?.id || 0,
          nome: primeiroContrato.cliente?.nome || 'Cliente não informado'
        },
        valorcontrato: (primeiroContrato.suprimentos?.total_valor || 0) * 10,
        valorpacela: ((primeiroContrato.suprimentos?.total_valor || 0) * 10) / 12,
        numeroparcelas: 12,
        tipocontrato: 'Locação',
        inicio: '2025-01-01',
        fim: '2025-12-31',
        renovado: 'N',
        total_recebido: (primeiroContrato.suprimentos?.total_valor || 0) * 6,
        total_gasto: primeiroContrato.suprimentos?.total_valor || 0,
        margem: ((primeiroContrato.suprimentos?.total_valor || 0) * 6) - (primeiroContrato.suprimentos?.total_valor || 0),
        totalMaquinas: 1,
        status: 'Ativo',
        data: new Date().toISOString().split('T')[0]
      };
      
      console.log('✅ Contrato mapeado:');
      console.log(JSON.stringify(contratoMapeado, null, 2));
    }
    
  } catch (error) {
    console.error('❌ Erro no teste:', error);
  }
}

testarContratos();
