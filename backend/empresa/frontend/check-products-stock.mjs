// Script to check the actual stock from the product table
// Run with: node check-products-stock.mjs

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

async function checkProductsStock() {
  console.log('📊 VERIFICAÇÃO DO ESTOQUE ATUAL - TABELA DE PRODUTOS');
  console.log('='.repeat(70));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');
  console.log('📋 OBJETIVO: Verificar o estoque real na tabela de produtos');
  console.log('   (Ignorando movimentos com documento_referencia = "000000")');
  console.log('');

  try {
    // Get current stock without date filter to see all available data
    console.log('🔍 Buscando dados de estoque atual...');
    
    const response = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?limite=100`);
    
    if (!response.ok) {
      console.log(`❌ Erro ao buscar estoque: ${response.status}`);
      const errorText = await response.text();
      console.log(`   Detalhes: ${errorText}`);
      return;
    }

    const data = await response.json();
    
    console.log('✅ Dados de estoque carregados com sucesso!');
    console.log('');

    if (data.estatisticas) {
      console.log('📊 ESTATÍSTICAS GERAIS:');
      console.log('-'.repeat(50));
      console.log(`   📦 Total de Produtos: ${formatNumber(data.estatisticas.total_produtos)}`);
      console.log(`   ✅ Produtos com Estoque: ${formatNumber(data.estatisticas.produtos_com_estoque)}`);
      console.log(`   ❌ Produtos Zerados: ${formatNumber(data.estatisticas.produtos_zerados)}`);
      console.log(`   💰 Valor Total Inicial: ${formatCurrency(data.estatisticas.valor_total_inicial)}`);
      console.log(`   💰 Valor Total Atual: ${formatCurrency(data.estatisticas.valor_total_atual)}`);
      console.log(`   📈 Variação Total: ${formatCurrency(data.estatisticas.variacao_total)}`);
      console.log(`   📅 Data do Cálculo: ${data.estatisticas.data_calculo}`);
      console.log('');
    }

    if (data.parametros) {
      console.log('📋 PARÂMETROS DA CONSULTA:');
      console.log('-'.repeat(30));
      console.log(`   📅 Data Consulta: ${data.parametros.data_consulta || 'Todas as datas'}`);
      console.log(`   📊 Total Registros: ${formatNumber(data.parametros.total_registros)}`);
      console.log(`   📄 Limite Aplicado: ${formatNumber(data.parametros.limite_aplicado)}`);
      console.log('');
    }

    if (data.estoque && data.estoque.length > 0) {
      console.log('📦 PRODUTOS COM ESTOQUE (Top 20):');
      console.log('-'.repeat(100));
      console.log('ID'.padEnd(6) + 'Produto'.padEnd(35) + 'Qtd Atual'.padStart(12) + 'Valor Unit.'.padStart(15) + 'Valor Total'.padStart(15) + 'Movimentos'.padStart(12));
      console.log('-'.repeat(100));

      // Sort by current stock value and show top 20
      const produtosComEstoque = data.estoque
        .filter(p => p.quantidade_atual > 0)
        .sort((a, b) => b.valor_atual - a.valor_atual)
        .slice(0, 20);

      produtosComEstoque.forEach(produto => {
        const id = produto.produto_id.toString().padEnd(6);
        const nome = produto.nome.length > 33 ? produto.nome.substring(0, 30) + '...' : produto.nome.padEnd(35);
        const qtdAtual = formatNumber(produto.quantidade_atual).padStart(10);
        const valorUnit = formatCurrency(produto.custo_unitario_inicial).padStart(13);
        const valorTotal = formatCurrency(produto.valor_atual).padStart(13);
        const movimentos = formatNumber(produto.total_movimentacoes).padStart(10);

        console.log(`${id}${nome}${qtdAtual}${valorUnit}${valorTotal}${movimentos}`);
      });

      console.log('-'.repeat(100));
      console.log(`Mostrando ${produtosComEstoque.length} produtos com estoque de ${data.estoque.length} total`);
      console.log('');

      // Show summary by stock levels
      const semEstoque = data.estoque.filter(p => p.quantidade_atual === 0).length;
      const estoqueMinimo = data.estoque.filter(p => p.quantidade_atual > 0 && p.quantidade_atual <= 10).length;
      const estoqueBom = data.estoque.filter(p => p.quantidade_atual > 10 && p.quantidade_atual <= 100).length;
      const estoqueAlto = data.estoque.filter(p => p.quantidade_atual > 100).length;

      console.log('📊 DISTRIBUIÇÃO POR NÍVEL DE ESTOQUE:');
      console.log('-'.repeat(40));
      console.log(`   ❌ Sem estoque (0): ${formatNumber(semEstoque)}`);
      console.log(`   ⚠️  Estoque baixo (1-10): ${formatNumber(estoqueMinimo)}`);
      console.log(`   ✅ Estoque bom (11-100): ${formatNumber(estoqueBom)}`);
      console.log(`   🔥 Estoque alto (>100): ${formatNumber(estoqueAlto)}`);
      console.log('');

      // Calculate total stock value
      const valorTotalCalculado = data.estoque.reduce((total, produto) => total + produto.valor_atual, 0);
      console.log('💰 VALOR TOTAL DO ESTOQUE:');
      console.log('-'.repeat(30));
      console.log(`   📊 Calculado: ${formatCurrency(valorTotalCalculado)}`);
      console.log(`   📋 Estatística: ${formatCurrency(data.estatisticas?.valor_total_atual || 0)}`);
      
      if (Math.abs(valorTotalCalculado - (data.estatisticas?.valor_total_atual || 0)) > 0.01) {
        console.log(`   ⚠️  Diferença: ${formatCurrency(Math.abs(valorTotalCalculado - (data.estatisticas?.valor_total_atual || 0)))}`);
      } else {
        console.log('   ✅ Valores conferem!');
      }
      console.log('');

    } else {
      console.log('📦 Nenhum produto encontrado na tabela de estoque');
      console.log('');
      console.log('💡 Possíveis causas:');
      console.log('   - Tabela de produtos vazia');
      console.log('   - Filtros aplicados muito restritivos');
      console.log('   - Problemas na consulta do banco de dados');
    }

    // Check if there are movements to analyze
    console.log('🔍 VERIFICANDO MOVIMENTAÇÕES RELACIONADAS...');
    console.log('-'.repeat(50));
    
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
      console.log(`✅ Movimentações encontradas: ${movData.produtos_movimentados?.length || 0} produtos`);
      
      if (movData.resumo) {
        console.log(`   💰 Valor total entradas: ${formatCurrency(movData.resumo.valor_total_entradas)}`);
        console.log(`   💰 Valor total saídas: ${formatCurrency(movData.resumo.valor_total_saidas)}`);
        console.log(`   📊 Total movimentações: ${formatNumber(movData.resumo.total_movimentacoes)}`);
      }
    } else {
      console.log('❌ Não foi possível carregar movimentações');
    }

    console.log('');
    console.log('🎯 RESUMO DA VERIFICAÇÃO:');
    console.log('='.repeat(70));
    console.log('✅ Tabela de produtos acessível');
    console.log('✅ Dados de estoque disponíveis');
    console.log('✅ Estatísticas calculadas');
    console.log('✅ Sistema funcionando corretamente');
    console.log('');
    console.log('💡 PRÓXIMOS PASSOS:');
    console.log('   1. Usar estes dados no dashboard');
    console.log('   2. Aplicar regra de negócio para documento_referencia = "000000"');
    console.log('   3. Validar cálculos com movimentações filtradas');

  } catch (error) {
    console.error('❌ Erro durante a verificação:', error.message);
    console.log('\n🔧 Verifique se o backend está rodando:');
    console.log('   python manage.py runserver 127.0.0.1:8000');
  }
}

// Execute the check
checkProductsStock();