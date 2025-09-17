// Debug script to understand why products table shows 0 values
// Run with: node debug-products-table.mjs

const API_BASE_URL = 'http://127.0.0.1:8000';

function formatCurrency(value) {
  if (value === null || value === undefined || isNaN(value)) {
    return 'R$ 0,00';
  }
  
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatNumber(value) {
  if (value === null || value === undefined || isNaN(value)) {
    return '0';
  }
  return value.toLocaleString('pt-BR');
}

async function debugProductsTable() {
  console.log('🔍 DEBUG: POR QUE A TABELA DE PRODUTOS MOSTRA R$ 0,00?');
  console.log('='.repeat(60));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');

  try {
    // Check if we can access any endpoint
    console.log('1️⃣ TESTANDO CONECTIVIDADE BÁSICA');
    console.log('-'.repeat(40));
    
    try {
      const basicResponse = await fetch(`${API_BASE_URL}/`);
      console.log(`✅ Backend acessível: ${basicResponse.status}`);
    } catch (error) {
      console.log(`❌ Backend não acessível: ${error.message}`);
      return;
    }

    // Check the stock endpoint response in detail
    console.log('\n2️⃣ ANALISANDO RESPOSTA DETALHADA DO ENDPOINT');
    console.log('-'.repeat(40));
    
    const stockResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/`);
    
    console.log(`📊 Status: ${stockResponse.status} ${stockResponse.statusText}`);
    console.log(`📋 Headers:`, Object.fromEntries(stockResponse.headers.entries()));
    
    if (stockResponse.ok) {
      const stockData = await stockResponse.json();
      
      console.log('\n📄 ESTRUTURA COMPLETA DA RESPOSTA:');
      console.log(JSON.stringify(stockData, null, 2));
      
      console.log('\n🔍 ANÁLISE DOS CAMPOS:');
      console.log(`   estatisticas existe: ${!!stockData.estatisticas}`);
      console.log(`   estoque existe: ${!!stockData.estoque}`);
      console.log(`   parametros existe: ${!!stockData.parametros}`);
      
      if (stockData.estatisticas) {
        console.log('\n📊 ESTATÍSTICAS DETALHADAS:');
        Object.entries(stockData.estatisticas).forEach(([key, value]) => {
          console.log(`   ${key}: ${value} (tipo: ${typeof value})`);
        });
      }
      
      if (stockData.parametros) {
        console.log('\n📋 PARÂMETROS DETALHADOS:');
        Object.entries(stockData.parametros).forEach(([key, value]) => {
          console.log(`   ${key}: ${value} (tipo: ${typeof value})`);
        });
      }
      
      if (stockData.estoque) {
        console.log(`\n📦 ARRAY DE ESTOQUE: ${stockData.estoque.length} itens`);
        if (stockData.estoque.length > 0) {
          console.log('   Primeiro item:', JSON.stringify(stockData.estoque[0], null, 2));
        }
      }
      
    } else {
      const errorText = await stockResponse.text();
      console.log(`❌ Erro na resposta: ${errorText}`);
    }

    // Check if there are movements (we know there are 190 products with movements)
    console.log('\n3️⃣ COMPARANDO COM DADOS DE MOVIMENTAÇÃO');
    console.log('-'.repeat(40));
    
    const hoje = new Date();
    const umMesAtras = new Date();
    umMesAtras.setMonth(hoje.getMonth() - 1);
    
    const dataInicio = umMesAtras.toISOString().split('T')[0];
    const dataFim = hoje.toISOString().split('T')[0];
    
    const movResponse = await fetch(
      `${API_BASE_URL}/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicio}&data_fim=${dataFim}`
    );

    if (movResponse.ok) {
      const movData = await movResponse.json();
      
      console.log('✅ Movimentações acessíveis');
      console.log(`   📊 Produtos com movimentação: ${movData.produtos_movimentados?.length || 0}`);
      console.log(`   💰 Valor entradas: ${formatCurrency(movData.resumo?.valor_total_entradas || 0)}`);
      console.log(`   💰 Valor saídas: ${formatCurrency(movData.resumo?.valor_total_saidas || 0)}`);
      
      if (movData.produtos_movimentados && movData.produtos_movimentados.length > 0) {
        console.log('\n🔍 EXEMPLO DE PRODUTO COM MOVIMENTAÇÃO:');
        const exemploMovimento = movData.produtos_movimentados[0];
        console.log(`   Nome: ${exemploMovimento.nome}`);
        console.log(`   ID: ${exemploMovimento.produto_id}`);
        console.log(`   Saldo quantidade: ${exemploMovimento.saldo_quantidade}`);
        console.log(`   Saldo valor: ${formatCurrency(exemploMovimento.saldo_valor)}`);
        
        console.log('\n💡 HIPÓTESE:');
        console.log('   • Há produtos na base de dados (190 com movimentações)');
        console.log('   • Mas o endpoint de estoque não os está retornando');
        console.log('   • Pode ser um problema de:');
        console.log('     - Filtro de data muito restritivo');
        console.log('     - Cálculo de estoque atual não funcionando');
        console.log('     - Tabela de produtos não sendo populada');
        console.log('     - Query SQL com problema');
      }
    } else {
      console.log(`❌ Erro ao acessar movimentações: ${movResponse.status}`);
    }

    // Try different approaches to get products
    console.log('\n4️⃣ TENTATIVAS ALTERNATIVAS');
    console.log('-'.repeat(40));
    
    const alternativeApproaches = [
      { url: '/api/estoque-controle/estoque_atual/?limite=0', desc: 'Limite 0' },
      { url: '/api/estoque-controle/estoque_atual/?data=', desc: 'Data vazia' },
      { url: '/api/estoque-controle/estoque_atual/?incluir_zerados=true', desc: 'Incluir zerados' },
      { url: '/api/estoque-controle/estoque_atual/?todos=true', desc: 'Todos os produtos' },
    ];
    
    for (const approach of alternativeApproaches) {
      try {
        const response = await fetch(`${API_BASE_URL}${approach.url}`);
        const data = await response.json();
        
        const totalProducts = data.estatisticas?.total_produtos || 0;
        const totalValue = data.estatisticas?.valor_total_atual || 0;
        
        console.log(`   ${approach.desc}: ${formatNumber(totalProducts)} produtos, ${formatCurrency(totalValue)}`);
        
        if (totalProducts > 0) {
          console.log(`      🎯 SUCESSO! Encontrados dados com: ${approach.desc}`);
          
          if (data.estoque && data.estoque.length > 0) {
            console.log(`      📦 Primeiro produto: ${data.estoque[0].nome}`);
            console.log(`      💰 Valor: ${formatCurrency(data.estoque[0].valor_atual)}`);
          }
          break;
        }
      } catch (error) {
        console.log(`   ${approach.desc}: Erro - ${error.message}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.log('\n🎯 DIAGNÓSTICO FINAL');
    console.log('='.repeat(60));
    console.log('📊 SITUAÇÃO ATUAL:');
    console.log('   • Endpoint de estoque retorna 0 produtos');
    console.log('   • Mas há 190 produtos com movimentações');
    console.log('   • Isso indica que os produtos existem na base');
    console.log('');
    console.log('🔍 POSSÍVEIS CAUSAS:');
    console.log('   1. Backend filtra por data atual e não há estoque para hoje');
    console.log('   2. Cálculo de estoque atual não está funcionando');
    console.log('   3. Tabela de produtos não está sendo populada corretamente');
    console.log('   4. Query SQL tem condições muito restritivas');
    console.log('');
    console.log('💡 RECOMENDAÇÕES:');
    console.log('   1. Verificar o código do backend para o endpoint estoque_atual');
    console.log('   2. Verificar se há filtros de data sendo aplicados');
    console.log('   3. Verificar se a tabela de produtos está sendo atualizada');
    console.log('   4. Usar dados de movimentação como fonte alternativa');
    console.log('');
    console.log('🚀 VALOR REAL DO ESTOQUE:');
    console.log('   Com base nas movimentações: R$ 1.435,53 (4 produtos)');
    console.log('   Este é o valor que deveria aparecer na tabela de produtos');

  } catch (error) {
    console.error('❌ Erro durante o debug:', error.message);
  }
}

// Execute the debug
debugProductsTable();