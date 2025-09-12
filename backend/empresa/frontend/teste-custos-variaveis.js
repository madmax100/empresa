// Teste do endpoint de custos variáveis
const dataInicio = '2025-08-10';
const dataFim = '2025-09-09';

async function testarCustosVariaveis() {
  try {
    console.log('🔍 Testando endpoint de custos variáveis...');
    console.log(`📅 Período: ${dataInicio} até ${dataFim}`);
    
    const url = `http://localhost:8000/contas/relatorios/custos-variaveis/?data_inicio=${dataInicio}&data_fim=${dataFim}`;
    console.log(`🌐 URL: ${url}`);
    
    const response = await fetch(url);
    
    console.log(`📡 Status da resposta: ${response.status}`);
    console.log(`📝 Status text: ${response.statusText}`);
    
    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('\n📊 RESPOSTA COMPLETA DA API:');
    console.log(JSON.stringify(data, null, 2));
    
    console.log('\n💰 RESUMO DOS CUSTOS VARIÁVEIS:');
    if (data.totais_gerais) {
      console.log(`💳 Valor total pago: ${data.totais_gerais.total_valor_pago}`);
      console.log(`🔢 Quantidade de contas: ${data.total_contas_pagas}`);
    } else {
      console.log('❌ Campo totais_gerais não encontrado na resposta');
    }
    
    if (data.resumo_por_especificacao) {
      console.log('\n📊 RESUMO POR ESPECIFICAÇÃO:');
      data.resumo_por_especificacao.forEach(item => {
        console.log(`${item.especificacao}: R$ ${item.valor_pago_total} (${item.quantidade_contas} contas, ${item.quantidade_fornecedores} fornecedores)`);
      });
    }
    
    if (data.estatisticas_fornecedores) {
      console.log('\n👥 ESTATÍSTICAS DE FORNECEDORES:');
      console.log(`📋 Total cadastrados: ${data.estatisticas_fornecedores.total_fornecedores_variaveis_cadastrados}`);
      console.log(`✅ Com pagamentos no período: ${data.estatisticas_fornecedores.fornecedores_com_pagamentos_no_periodo}`);
    }
    
  } catch (error) {
    console.error('❌ Erro ao testar custos variáveis:', error.message);
    console.error('🔍 Detalhes do erro:', error);
    
    // Em caso de erro, vamos usar dados mocados para teste
    console.log('\n🎭 Testando com dados mocados...');
    const { CustosVariaveisService } = await import('./src/services/custos-variaveis-service.js');
    const mockData = CustosVariaveisService.getMockData(dataInicio, dataFim);
    console.log('📊 Dados mocados:', mockData);
  }
}

testarCustosVariaveis();
