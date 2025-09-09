// Teste com período onde há dados - março 2025
async function testarMarco2025() {
  const baseURL = 'http://127.0.0.1:8000/api';
  
  try {
    // Testar período específico - março 2025 (sabemos que há dados)
    console.log('🔍 Testando período específico: março 2025...');
    const url = `${baseURL}/contratos_locacao/suprimentos/?data_inicial=2025-03-01&data_final=2025-03-31`;
    
    const response = await fetch(url);
    console.log('📋 Status da resposta:', response.status);
    
    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Dados para março 2025:');
    console.log('- Total de resultados:', data?.resultados?.length || 0);
    console.log('- Resumo:', data?.resumo);
    
    if (data.resultados && data.resultados.length > 0) {
      console.log('\n📋 Primeiros 3 contratos em março:');
      data.resultados.slice(0, 3).forEach((contrato, index) => {
        console.log(`\n${index + 1}. Contrato ${contrato.contrato_numero}:`);
        console.log(`   Cliente: ${contrato.cliente?.nome}`);
        console.log(`   Valor suprimentos: R$ ${contrato.suprimentos?.total_valor || 0}`);
        console.log(`   Quantidade notas: ${contrato.suprimentos?.quantidade_notas || 0}`);
        
        if (contrato.suprimentos?.notas?.length > 0) {
          const datas = contrato.suprimentos.notas.map(n => n.data).sort();
          console.log(`   Datas das notas: ${datas.join(', ')}`);
        }
      });
      
      // Simular lógica de vigência para março
      console.log('\n🔍 Simulando lógica de vigência para março:');
      const periodoInicio = new Date('2025-03-01');
      const periodoFim = new Date('2025-03-31');
      
      let contratosVigentes = 0;
      
      data.resultados.forEach(contrato => {
        if (contrato.suprimentos?.notas && contrato.suprimentos.notas.length > 0) {
          const datas = contrato.suprimentos.notas.map(n => new Date(n.data)).sort((a, b) => a - b);
          const primeiraNotaData = datas[0];
          const ultimaNotaData = datas[datas.length - 1];
          
          // Expandir período do contrato
          const inicioContrato = new Date(primeiraNotaData);
          inicioContrato.setMonth(inicioContrato.getMonth() - 6);
          
          const fimContrato = new Date(ultimaNotaData);
          fimContrato.setMonth(fimContrato.getMonth() + 6);
          
          // Verificar vigência
          const vigente = inicioContrato <= periodoFim && fimContrato >= periodoInicio;
          
          if (vigente) {
            contratosVigentes++;
            console.log(`✅ ${contrato.contrato_numero}: ${inicioContrato.toLocaleDateString()} até ${fimContrato.toLocaleDateString()}`);
          } else {
            console.log(`❌ ${contrato.contrato_numero}: ${inicioContrato.toLocaleDateString()} até ${fimContrato.toLocaleDateString()}`);
          }
        }
      });
      
      console.log(`\n✅ Contratos vigentes em março: ${contratosVigentes} de ${data.resultados.length}`);
    }
    
  } catch (error) {
    console.error('❌ Erro no teste:', error);
  }
}

testarMarco2025();
