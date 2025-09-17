// Script to analyze the stock data issue and find the correct approach
// Run with: node analyze-stock-issue.mjs

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

async function analyzeStockIssue() {
  console.log('🔍 ANÁLISE DO PROBLEMA DE ESTOQUE');
  console.log('='.repeat(60));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');
  console.log('🚨 PROBLEMA IDENTIFICADO:');
  console.log('   - Endpoint de estoque retorna 0 produtos para hoje');
  console.log('   - Mas há 73 produtos com movimentações');
  console.log('   - Regra: documento_referencia = "000000" deve ser ignorado');
  console.log('');

  try {
    // Test 1: Stock without date filter
    console.log('1️⃣ TESTANDO ESTOQUE SEM FILTRO DE DATA');
    console.log('-'.repeat(50));
    
    const stockNoDateResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/`);
    
    if (stockNoDateResponse.ok) {
      const stockNoDateData = await stockNoDateResponse.json();
      console.log('✅ Resposta recebida sem filtro de data');
      console.log(`   📦 Total produtos: ${formatNumber(stockNoDateData.estatisticas?.total_produtos || 0)}`);
      console.log(`   💰 Valor total: ${formatCurrency(stockNoDateData.estatisticas?.valor_total_atual || 0)}`);
      console.log(`   📅 Data cálculo: ${stockNoDateData.estatisticas?.data_calculo || 'N/A'}`);
      
      if (stockNoDateData.estoque && stockNoDateData.estoque.length > 0) {
        console.log('   ✅ Produtos encontrados!');
        
        // Show first few products
        console.log('\n   🔍 Primeiros 5 produtos:');
        stockNoDateData.estoque.slice(0, 5).forEach((produto, index) => {
          console.log(`   ${index + 1}. ${produto.nome}`);
          console.log(`      Qtd: ${formatNumber(produto.quantidade_atual)} | Valor: ${formatCurrency(produto.valor_atual)}`);
        });
      } else {
        console.log('   ❌ Nenhum produto encontrado mesmo sem filtro de data');
      }
    } else {
      console.log(`❌ Erro sem filtro de data: ${stockNoDateResponse.status}`);
    }

    console.log('');

    // Test 2: Check movements data in detail
    console.log('2️⃣ ANALISANDO MOVIMENTAÇÕES DETALHADAS');
    console.log('-'.repeat(50));
    
    const hoje = new Date();
    const umMesAtras = new Date();
    umMesAtras.setMonth(hoje.getMonth() - 1);
    
    const dataInicio = umMesAtras.toISOString().split('T')[0];
    const dataFim = hoje.toISOString().split('T')[0];
    
    const movResponse = await fetch(
      `${API_BASE_URL}/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicio}&data_fim=${dataFim}&incluir_detalhes=true`
    );

    if (movResponse.ok) {
      const movData = await movResponse.json();
      console.log('✅ Movimentações carregadas com detalhes');
      console.log(`   📊 Produtos com movimentação: ${movData.produtos_movimentados?.length || 0}`);
      
      if (movData.produtos_movimentados && movData.produtos_movimentados.length > 0) {
        // Analyze movements with documento_referencia = "000000"
        let totalMovements = 0;
        let stockAdjustments = 0;
        let regularMovements = 0;
        
        const productsWithStock = [];
        
        movData.produtos_movimentados.forEach(produto => {
          if (produto.movimentacoes_detalhadas) {
            let productStockAdjustments = 0;
            let productRegularMovements = 0;
            let latestStockQuantity = null;
            
            produto.movimentacoes_detalhadas.forEach(movimento => {
              totalMovements++;
              
              // Check for stock adjustment (documento_referencia = "000000")
              if (movimento.documento === "000000") {
                stockAdjustments++;
                productStockAdjustments++;
                latestStockQuantity = movimento.quantidade; // This is the real stock
              } else {
                regularMovements++;
                productRegularMovements++;
              }
            });
            
            if (latestStockQuantity !== null) {
              productsWithStock.push({
                nome: produto.nome,
                referencia: produto.referencia,
                stockQuantity: latestStockQuantity,
                stockAdjustments: productStockAdjustments,
                regularMovements: productRegularMovements,
                saldoValor: produto.saldo_valor
              });
            }
          }
        });
        
        console.log(`   📈 Total movimentos: ${formatNumber(totalMovements)}`);
        console.log(`   🔄 Movimentos regulares: ${formatNumber(regularMovements)}`);
        console.log(`   📦 Ajustes de estoque (000000): ${formatNumber(stockAdjustments)}`);
        console.log(`   📋 Produtos com estoque real: ${formatNumber(productsWithStock.length)}`);
        
        if (productsWithStock.length > 0) {
          console.log('\n   🎯 PRODUTOS COM ESTOQUE REAL (Top 10):');
          console.log('   ' + '-'.repeat(80));
          console.log('   Produto'.padEnd(35) + 'Qtd Real'.padStart(12) + 'Valor'.padStart(15) + 'Ajustes'.padStart(10));
          console.log('   ' + '-'.repeat(80));
          
          productsWithStock
            .sort((a, b) => b.stockQuantity - a.stockQuantity)
            .slice(0, 10)
            .forEach(produto => {
              const nome = produto.nome.length > 33 ? produto.nome.substring(0, 30) + '...' : produto.nome;
              console.log(`   ${nome.padEnd(35)}${formatNumber(produto.stockQuantity).padStart(10)}${formatCurrency(produto.saldoValor).padStart(13)}${produto.stockAdjustments.toString().padStart(8)}`);
            });
          
          // Calculate total stock value from movements
          const totalStockValue = productsWithStock.reduce((total, produto) => {
            return total + (produto.saldoValor || 0);
          }, 0);
          
          console.log('   ' + '-'.repeat(80));
          console.log(`   💰 VALOR TOTAL CALCULADO: ${formatCurrency(totalStockValue)}`);
        }
      }
    } else {
      console.log(`❌ Erro ao carregar movimentações: ${movResponse.status}`);
    }

    console.log('');

    // Test 3: Try different date ranges
    console.log('3️⃣ TESTANDO DIFERENTES PERÍODOS');
    console.log('-'.repeat(50));
    
    const testDates = [
      '2024-12-31',
      '2024-11-30',
      '2024-10-31',
      '2024-09-30',
      '2024-08-31'
    ];
    
    for (const testDate of testDates) {
      const testResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?data=${testDate}`);
      
      if (testResponse.ok) {
        const testData = await testResponse.json();
        const totalProducts = testData.estatisticas?.total_produtos || 0;
        const totalValue = testData.estatisticas?.valor_total_atual || 0;
        
        if (totalProducts > 0) {
          console.log(`   ✅ ${testDate}: ${formatNumber(totalProducts)} produtos, ${formatCurrency(totalValue)}`);
        } else {
          console.log(`   ❌ ${testDate}: Sem dados`);
        }
      } else {
        console.log(`   ❌ ${testDate}: Erro ${testResponse.status}`);
      }
      
      // Small delay to avoid overwhelming the server
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.log('');
    console.log('🎯 CONCLUSÕES E RECOMENDAÇÕES:');
    console.log('='.repeat(60));
    console.log('');
    console.log('📊 PROBLEMA IDENTIFICADO:');
    console.log('   - Endpoint de estoque está filtrado por data');
    console.log('   - Não há dados de estoque para datas recentes');
    console.log('   - Mas há movimentações com estoque real (documento_referencia = "000000")');
    console.log('');
    console.log('💡 SOLUÇÕES PROPOSTAS:');
    console.log('   1. ✅ Usar movimentações para calcular estoque atual');
    console.log('   2. ✅ Filtrar movimentos com documento_referencia = "000000"');
    console.log('   3. ✅ Quantidade desses movimentos = estoque real');
    console.log('   4. ✅ Criar dashboard baseado em movimentações');
    console.log('');
    console.log('🚀 PRÓXIMO PASSO:');
    console.log('   Criar EstoqueDashboardFromMovements.tsx');
    console.log('   - Buscar movimentações do período');
    console.log('   - Filtrar documento_referencia = "000000"');
    console.log('   - Usar quantidade como estoque real');
    console.log('   - Calcular estatísticas corretas');

  } catch (error) {
    console.error('❌ Erro durante a análise:', error.message);
    console.log('\n🔧 Verifique se o backend está rodando:');
    console.log('   python manage.py runserver 127.0.0.1:8000');
  }
}

// Execute the analysis
analyzeStockIssue();