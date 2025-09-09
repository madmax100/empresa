// Função limpa para processar contratos válidos
const processarContratosValidos = (contratos, dateRange) => {
  const clientesMap = new Map();
  const periodoInicio = dateRange.from;
  const periodoFim = dateRange.to;
  
  console.log(`📊 Processando ${contratos.length} contratos válidos...`);
  
  contratos.forEach((contrato, index) => {
    const clienteId = contrato.cliente.id;
    const clienteNome = contrato.cliente.nome;
    
    console.log(`🔄 Processando contrato ${index + 1}/${contratos.length}:`, {
      id: contrato.id,
      numero: contrato.contrato,
      cliente: clienteNome,
      clienteId,
      valorContrato: contrato.valorcontrato,
      gastoSuprimentos: contrato.total_gasto
    });
    
    if (!clienteId) return;
    
    // Calcular sobreposição de período para faturamento proporcional
    const dataInicioContrato = new Date(contrato.inicio);
    const dataFimContrato = new Date(contrato.fim);
    const inicioEfetivo = dataInicioContrato > periodoInicio ? dataInicioContrato : periodoInicio;
    const fimEfetivo = dataFimContrato < periodoFim ? dataFimContrato : periodoFim;
    const diasEfetivos = Math.max(1, Math.round((fimEfetivo.getTime() - inicioEfetivo.getTime()) / (1000 * 60 * 60 * 24)));
    const mesesEfetivos = Math.max(0.1, diasEfetivos / 30.44);
    
    // Calcular faturamento proporcional ao período
    const valorMensal = Number(contrato.valorpacela || contrato.valorcontrato || 0);
    const faturamentoPeriodo = valorMensal * mesesEfetivos;
    
    console.log(`✅ CONTRATO VÁLIDO NO PERÍODO:`);
    console.log(`👤 Cliente: ${clienteNome}`);
    console.log(`📋 Contrato: ${contrato.contrato}`);
    console.log(`📅 Período Contrato: ${dataInicioContrato.toLocaleDateString()} até ${dataFimContrato.toLocaleDateString()}`);
    console.log(`📅 Período Efetivo: ${inicioEfetivo.toLocaleDateString()} até ${fimEfetivo.toLocaleDateString()}`);
    console.log(`⏱️ Dias Efetivos: ${diasEfetivos} dias (${mesesEfetivos.toFixed(2)} meses)`);
    console.log(`💵 Valor Mensal: R$ ${valorMensal.toFixed(2)}`);
    console.log(`🧮 Faturamento Proporcional: R$ ${faturamentoPeriodo.toFixed(2)}`);
    console.log(`💰 Gastos Suprimentos: R$ ${contrato.total_gasto.toFixed(2)}`);
    console.log(`--------------------------------------------------`);
    
    const contratoData = {
      id: contrato.id,
      contratoNumero: contrato.contrato,
      equipamento: String(contrato.totalMaquinas || 1),
      valorMensal,
      dataInicio: dataInicioContrato.toISOString(),
      dataFim: dataFimContrato.toISOString(),
      status: contrato.status || 'Ativo',
      faturamento: faturamentoPeriodo,
      suprimentos: contrato.total_gasto || 0
    };
    
    if (clientesMap.has(clienteId)) {
      const clienteExistente = clientesMap.get(clienteId);
      clienteExistente.contratos.push(contratoData);
      clienteExistente.faturamentoTotal += faturamentoPeriodo;
      clienteExistente.despesasSuprimentos += (contrato.total_gasto || 0);
      clienteExistente.quantidadeContratos += 1;
      clienteExistente.margemLiquida = clienteExistente.faturamentoTotal - clienteExistente.despesasSuprimentos;
    } else {
      clientesMap.set(clienteId, {
        clienteId,
        cliente: clienteNome,
        contratos: [contratoData],
        faturamentoTotal: faturamentoPeriodo,
        despesasSuprimentos: contrato.total_gasto || 0,
        quantidadeContratos: 1,
        margemLiquida: faturamentoPeriodo - (contrato.total_gasto || 0)
      });
    }
  });
  
  return Array.from(clientesMap.values());
};
