// Script to find the actual stock value from all available sources
// Run with: node find-actual-stock-value.mjs

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

async function findActualStockValue() {
  console.log('🔍 BUSCANDO O VALOR REAL DO ESTOQUE');
  console.log('='.repeat(60));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');

  let actualStockValue = 0;
  let actualProductCount = 0;
  let dataSource = 'unknown';

  try {
    // Method 1: Check stock endpoint without date filter
    console.log('1️⃣ MÉTODO 1: ENDPOINT DE ESTOQUE SEM FILTRO DE DATA');
    console.log('-'.repeat(50));
    
    const stockResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/`);
    
    if (stockResponse.ok) {
      const stockData = await stockResponse.json();
      
      console.log('✅ Resposta recebida do endpoint de estoque');
      console.log(`   📦 Total produtos: ${formatNumber(stockData.estatisticas?.total_produtos || 0)}`);
      console.log(`   💰 Valor total: ${formatCurrency(stockData.estatisticas?.valor_total_atual || 0)}`);
      console.log(`   📅 Data cálculo: ${stockData.estatisticas?.data_calculo || 'N/A'}`);
      
      if (stockData.estatisticas?.total_produtos > 0) {
        actualStockValue = stockData.estatisticas.valor_total_atual || 0;
        actualProductCount = stockData.estatisticas.total_produtos || 0;
        dataSource = 'stock_endpoint';
        
        console.log('🎯 DADOS ENCONTRADOS NO ENDPOINT DE ESTOQUE!');
        
        if (stockData.estoque && stockData.estoque.length > 0) {
          console.log('\n   🏆 TOP 5 PRODUTOS POR VALOR:');
          stockData.estoque
            .sort((a, b) => b.valor_atual - a.valor_atual)
            .slice(0, 5)
            .forEach((produto, index) => {
              console.log(`   ${index + 1}. ${produto.nome}`);
              console.log(`      Qtd: ${formatNumber(produto.quantidade_atual)} | Valor: ${formatCurrency(produto.valor_atual)}`);
            });
        }
      } else {
        console.log('❌ Nenhum produto encontrado no endpoint de estoque');
      }
    } else {
      console.log(`❌ Erro no endpoint de estoque: ${stockResponse.status}`);
    }

    console.log('');

    // Method 2: Check movements and calculate from documento_referencia = "000000"
    console.log('2️⃣ MÉTODO 2: CÁLCULO A PARTIR DE MOVIMENTAÇÕES');
    console.log('-'.repeat(50));
    
    const hoje = new Date();
    const seiseMesesAtras = new Date();
    seiseMesesAtras.setMonth(hoje.getMonth() - 6);
    
    const dataInicio = seiseMesesAtras.toISOString().split('T')[0];
    const dataFim = hoje.toISOString().split('T')[0];
    
    const movResponse = await fetch(
      `${API_BASE_URL}/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicio}&data_fim=${dataFim}&incluir_detalhes=true`
    );

    if (movResponse.ok) {
      const movData = await movResponse.json();
      
      console.log('✅ Movimentações carregadas com detalhes');
      console.log(`   📊 Produtos com movimentação: ${movData.produtos_movimentados?.length || 0}`);
      console.log(`   💰 Valor total entradas: ${formatCurrency(movData.resumo?.valor_total_entradas || 0)}`);
      console.log(`   💰 Valor total saídas: ${formatCurrency(movData.resumo?.valor_total_saidas || 0)}`);
      
      if (movData.produtos_movimentados && movData.produtos_movimentados.length > 0) {
        let stockFromMovements = 0;
        let productsWithStock = 0;
        const stockAdjustments = [];
        
        movData.produtos_movimentados.forEach(produto => {
          if (produto.movimentacoes_detalhadas) {
            // Find stock adjustments (documento = "000000")
            const adjustments = produto.movimentacoes_detalhadas
              .filter(mov => mov.documento === "000000")
              .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());
            
            if (adjustments.length > 0) {
              const latestAdjustment = adjustments[0];
              const stockValue = latestAdjustment.quantidade * latestAdjustment.valor_unitario;
              
              if (latestAdjustment.quantidade > 0 || stockValue > 0) {
                stockFromMovements += stockValue;
                productsWithStock++;
                
                stockAdjustments.push({
                  nome: produto.nome,
                  quantidade: latestAdjustment.quantidade,
                  valorUnitario: latestAdjustment.valor_unitario,
                  valorTotal: stockValue,
                  data: latestAdjustment.data
                });
              }
            }
          }
        });
        
        console.log(`\n   📦 Produtos com ajustes de estoque: ${productsWithStock}`);
        console.log(`   💰 Valor calculado das movimentações: ${formatCurrency(stockFromMovements)}`);
        
        if (stockFromMovements > actualStockValue) {
          actualStockValue = stockFromMovements;
          actualProductCount = productsWithStock;
          dataSource = 'movements_calculation';
          
          console.log('🎯 VALOR MAIOR ENCONTRADO NAS MOVIMENTAÇÕES!');
        }
        
        if (stockAdjustments.length > 0) {
          console.log('\n   🔍 AJUSTES DE ESTOQUE ENCONTRADOS:');
          stockAdjustments
            .sort((a, b) => b.valorTotal - a.valorTotal)
            .slice(0, 5)
            .forEach((adj, index) => {
              console.log(`   ${index + 1}. ${adj.nome}`);
              console.log(`      Qtd: ${formatNumber(adj.quantidade)} | Valor Unit: ${formatCurrency(adj.valorUnitario)}`);
              console.log(`      Valor Total: ${formatCurrency(adj.valorTotal)} | Data: ${adj.data}`);
            });
        }
      } else {
        console.log('❌ Nenhuma movimentação encontrada');
      }
    } else {
      console.log(`❌ Erro ao carregar movimentações: ${movResponse.status}`);
    }

    console.log('');

    // Method 3: Check different date ranges
    console.log('3️⃣ MÉTODO 3: TESTANDO DIFERENTES PERÍODOS');
    console.log('-'.repeat(50));
    
    const testDates = [
      '2024-12-31',
      '2024-11-30',
      '2024-10-31',
      '2024-09-30',
      '2024-08-31',
      '2024-07-31',
      '2024-06-30'
    ];
    
    for (const testDate of testDates) {
      const testResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?data=${testDate}`);
      
      if (testResponse.ok) {
        const testData = await testResponse.json();
        const testValue = testData.estatisticas?.valor_total_atual || 0;
        const testProducts = testData.estatisticas?.total_produtos || 0;
        
        if (testProducts > 0) {
          console.log(`   ✅ ${testDate}: ${formatNumber(testProducts)} produtos, ${formatCurrency(testValue)}`);
          
          if (testValue > actualStockValue) {
            actualStockValue = testValue;
            actualProductCount = testProducts;
            dataSource = `historical_${testDate}`;
            
            console.log(`      🎯 NOVO VALOR MÁXIMO ENCONTRADO!`);
          }
        } else {
          console.log(`   ❌ ${testDate}: Sem dados`);
        }
      }
      
      // Small delay
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.log('');
    console.log('🎯 RESULTADO FINAL - VALOR REAL DO ESTOQUE');
    console.log('='.repeat(60));
    
    if (actualStockValue > 0) {
      console.log('✅ VALOR REAL DO ESTOQUE ENCONTRADO!');
      console.log('');
      console.log(`💰 VALOR TOTAL: ${formatCurrency(actualStockValue)}`);
      console.log(`📦 TOTAL DE PRODUTOS: ${formatNumber(actualProductCount)}`);
      console.log(`📊 FONTE DOS DADOS: ${dataSource}`);
      console.log('');
      
      switch (dataSource) {
        case 'stock_endpoint':
          console.log('📋 FONTE: Endpoint de estoque (tabela de produtos)');
          console.log('✅ Dados obtidos diretamente da tabela de produtos');
          break;
        case 'movements_calculation':
          console.log('📋 FONTE: Cálculo a partir de movimentações');
          console.log('✅ Dados calculados usando documento_referencia = "000000"');
          break;
        default:
          if (dataSource.startsWith('historical_')) {
            const date = dataSource.replace('historical_', '');
            console.log(`📋 FONTE: Dados históricos para ${date}`);
            console.log('✅ Dados obtidos do endpoint com filtro de data');
          }
          break;
      }
      
      console.log('');
      console.log('🚀 RECOMENDAÇÕES PARA O FRONTEND:');
      console.log('1. ✅ Use este valor como referência para testes');
      console.log('2. ✅ Configure o dashboard para mostrar estes dados');
      console.log('3. ✅ Verifique se o cálculo está correto');
      
    } else {
      console.log('❌ NENHUM VALOR DE ESTOQUE ENCONTRADO');
      console.log('');
      console.log('🔍 POSSÍVEIS CAUSAS:');
      console.log('• Base de dados vazia');
      console.log('• Produtos sem estoque');
      console.log('• Regras de negócio filtrando todos os dados');
      console.log('• Problemas na configuração do backend');
      console.log('');
      console.log('💡 PRÓXIMOS PASSOS:');
      console.log('1. Verificar se há produtos cadastrados');
      console.log('2. Verificar se há movimentações registradas');
      console.log('3. Revisar regras de documento_referencia');
    }

  } catch (error) {
    console.error('❌ Erro durante a busca:', error.message);
    console.log('\n🔧 Verifique se o backend está rodando:');
    console.log('   python manage.py runserver 127.0.0.1:8000');
  }
}

// Execute the search
findActualStockValue();