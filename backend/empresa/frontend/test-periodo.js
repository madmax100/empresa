// Teste com período específico - Setembro 2025
async function testarPeriodoEspecifico() {
  const baseURL = 'http://127.0.0.1:8000/api';
  
  try {
    // Testar período específico - setembro 2025
    console.log('🔍 Testando período específico: setembro 2025...');
    const url = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=2025-09-01&data_final=2025-09-30`;
    
    const response = await fetch(url);
    console.log('📋 Status da resposta:', response.status);
    
    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Dados para setembro 2025:');
    console.log('- Total de resultados:', data?.resultados?.length || 0);
    console.log('- Resumo:', data?.resumo);
    
    if (data.resultados && data.resultados.length > 0) {
      console.log('\n📋 Primeiros 3 contratos em setembro:');
      data.resultados.slice(0, 3).forEach((contrato, index) => {
        console.log(`\n${index + 1}. Contrato ${contrato.contrato_numero}:`);
        console.log(`   Cliente: ${contrato.cliente?.nome}`);
        console.log(`   Valor suprimentos: R$ ${contrato.suprimentos?.total_valor || 0}`);
        console.log(`   Quantidade notas: ${contrato.suprimentos?.quantidade_notas || 0}`);
        
        if (contrato.suprimentos?.notas?.length > 0) {
          console.log(`   Primeira nota: ${contrato.suprimentos.notas[0].data}`);
          console.log(`   Última nota: ${contrato.suprimentos.notas[contrato.suprimentos.notas.length - 1].data}`);
        }
      });
      
      // Simular lógica de vigência
      console.log('\n🔍 Simulando lógica de vigência:');
      const periodoInicio = new Date('2025-09-01');
      const periodoFim = new Date('2025-09-30');
      
      let contratosVigentes = 0;
      
      data.resultados.forEach(contrato => {
        if (contrato.suprimentos?.notas && contrato.suprimentos.notas.length > 0) {
          const primeiraNotaData = new Date(contrato.suprimentos.notas[0].data);
          const ultimaNotaData = new Date(contrato.suprimentos.notas[contrato.suprimentos.notas.length - 1].data);
          
          // Expandir período do contrato
          const inicioContrato = new Date(primeiraNotaData);
          inicioContrato.setMonth(inicioContrato.getMonth() - 6);
          
          const fimContrato = new Date(ultimaNotaData);
          fimContrato.setMonth(fimContrato.getMonth() + 6);
          
          // Verificar vigência
          const vigente = inicioContrato <= periodoFim && fimContrato >= periodoInicio;
          
          if (vigente) {
            contratosVigentes++;
          }
        }
      });
      
      console.log(`\n✅ Contratos vigentes em setembro: ${contratosVigentes} de ${data.resultados.length}`);
    }
    
  } catch (error) {
    console.error('❌ Erro no teste:', error);
  }
}

testarPeriodoEspecifico();
