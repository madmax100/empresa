// Script to analyze movement data and understand the "000000" documento_referencia pattern
// Run with: node analyze-movement-data.mjs

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

async function analyzeMovementData() {
  console.log('🔍 ANÁLISE DOS DADOS DE MOVIMENTAÇÃO');
  console.log('='.repeat(60));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');
  console.log('📋 REGRA DE NEGÓCIO:');
  console.log('   - documento_referencia = "000000" → Movimento deve ser ignorado');
  console.log('   - Quantidade = Estoque real do produto naquele dia');
  console.log('');

  try {
    // Get period movements with details
    const hoje = new Date();
    const umMesAtras = new Date();
    umMesAtras.setMonth(hoje.getMonth() - 1);
    
    const dataInicio = umMesAtras.toISOString().split('T')[0];
    const dataFim = hoje.toISOString().split('T')[0];
    
    console.log(`📅 Período analisado: ${dataInicio} até ${dataFim}`);
    console.log('');

    const response = await fetch(
      `${API_BASE_URL}/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicio}&data_fim=${dataFim}&incluir_detalhes=true`
    );

    if (!response.ok) {
      console.log(`❌ Erro ao buscar movimentações: ${response.status}`);
      return;
    }

    const data = await response.json();
    
    if (!data.produtos_movimentados || data.produtos_movimentados.length === 0) {
      console.log('📦 Nenhuma movimentação encontrada no período');
      return;
    }

    console.log('✅ DADOS DE MOVIMENTAÇÃO CARREGADOS');
    console.log(`📊 Total de produtos com movimentação: ${data.produtos_movimentados.length}`);
    console.log('');

    // Analyze movements with documento_referencia = "000000"
    let totalMovements = 0;
    let stockAdjustmentMovements = 0;
    let regularMovements = 0;
    let productsWithStockAdjustments = 0;

    const stockAdjustmentExamples = [];

    data.produtos_movimentados.forEach(produto => {
      if (produto.movimentacoes_detalhadas) {
        let hasStockAdjustment = false;
        
        produto.movimentacoes_detalhadas.forEach(movimento => {
          totalMovements++;
          
          // Check if this is a stock adjustment (documento_referencia = "000000")
          if (movimento.documento === "000000" || 
              (movimento.nota_fiscal && movimento.nota_fiscal.numero === "000000")) {
            stockAdjustmentMovements++;
            hasStockAdjustment = true;
            
            // Collect examples
            if (stockAdjustmentExamples.length < 5) {
              stockAdjustmentExamples.push({
                produto: produto.nome,
                data: movimento.data,
                quantidade: movimento.quantidade,
                tipo: movimento.tipo,
                documento: movimento.documento,
                observacoes: movimento.observacoes
              });
            }
          } else {
            regularMovements++;
          }
        });
        
        if (hasStockAdjustment) {
          productsWithStockAdjustments++;
        }
      }
    });

    console.log('📊 ANÁLISE DOS MOVIMENTOS:');
    console.log('-'.repeat(40));
    console.log(`   📈 Total de movimentos: ${formatNumber(totalMovements)}`);
    console.log(`   🔄 Movimentos regulares: ${formatNumber(regularMovements)}`);
    console.log(`   📦 Ajustes de estoque (000000): ${formatNumber(stockAdjustmentMovements)}`);
    console.log(`   📋 Produtos com ajustes: ${formatNumber(productsWithStockAdjustments)}`);
    console.log('');

    if (stockAdjustmentMovements > 0) {
      const percentage = ((stockAdjustmentMovements / totalMovements) * 100).toFixed(1);
      console.log(`📊 Percentual de ajustes de estoque: ${percentage}%`);
      console.log('');

      console.log('🔍 EXEMPLOS DE AJUSTES DE ESTOQUE (documento_referencia = "000000"):');
      console.log('-'.repeat(80));
      
      stockAdjustmentExamples.forEach((exemplo, index) => {
        console.log(`${index + 1}. Produto: ${exemplo.produto}`);
        console.log(`   📅 Data: ${exemplo.data}`);
        console.log(`   📦 Quantidade: ${formatNumber(exemplo.quantidade)}`);
        console.log(`   🏷️  Tipo: ${exemplo.tipo}`);
        console.log(`   📄 Documento: ${exemplo.documento}`);
        console.log(`   📝 Observações: ${exemplo.observacoes || 'N/A'}`);
        console.log('');
      });
    }

    // Analyze how this affects stock calculation
    console.log('💡 IMPACTO NO CÁLCULO DE ESTOQUE:');
    console.log('-'.repeat(40));
    console.log('');
    console.log('📋 LÓGICA CORRETA PARA CÁLCULO:');
    console.log('   1. Ignorar movimentos com documento_referencia = "000000"');
    console.log('   2. A quantidade desses movimentos = estoque real naquele dia');
    console.log('   3. Usar apenas movimentos regulares para cálculos de entrada/saída');
    console.log('');

    // Show products that would be affected
    const affectedProducts = data.produtos_movimentados.filter(produto => 
      produto.movimentacoes_detalhadas && 
      produto.movimentacoes_detalhadas.some(mov => 
        mov.documento === "000000" || 
        (mov.nota_fiscal && mov.nota_fiscal.numero === "000000")
      )
    );

    if (affectedProducts.length > 0) {
      console.log('🎯 PRODUTOS AFETADOS PELA REGRA:');
      console.log('-'.repeat(50));
      
      affectedProducts.slice(0, 10).forEach((produto, index) => {
        const stockAdjustments = produto.movimentacoes_detalhadas.filter(mov => 
          mov.documento === "000000" || 
          (mov.nota_fiscal && mov.nota_fiscal.numero === "000000")
        );
        
        console.log(`${index + 1}. ${produto.nome}`);
        console.log(`   📦 Ajustes de estoque: ${stockAdjustments.length}`);
        console.log(`   📈 Total movimentos: ${produto.total_movimentacoes}`);
        console.log(`   💰 Saldo atual: ${formatCurrency(produto.saldo_valor)}`);
        console.log('');
      });
      
      if (affectedProducts.length > 10) {
        console.log(`   ... e mais ${affectedProducts.length - 10} produtos`);
        console.log('');
      }
    }

    console.log('🎯 RECOMENDAÇÕES:');
    console.log('='.repeat(60));
    console.log('1. ✅ Implementar filtro para ignorar documento_referencia = "000000"');
    console.log('2. ✅ Tratar quantidade como estoque real do dia');
    console.log('3. ✅ Recalcular estatísticas excluindo esses movimentos');
    console.log('4. ✅ Criar componente que aplica essa regra de negócio');
    console.log('');
    console.log('🚀 Próximos passos:');
    console.log('   - Criar EstoqueDashboardFromMovements.tsx');
    console.log('   - Implementar lógica de filtro de movimentos');
    console.log('   - Recalcular valores corretos do estoque');

  } catch (error) {
    console.error('❌ Erro durante a análise:', error.message);
    console.log('\n🔧 Verifique se o backend está rodando:');
    console.log('   python manage.py runserver 127.0.0.1:8000');
  }
}

// Execute the analysis
analyzeMovementData();