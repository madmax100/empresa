// Script to check what dates have stock data available
// Run with: node check-stock-dates.mjs

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

async function checkStockForDate(date) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?data=${date}`);
    
    if (response.ok) {
      const data = await response.json();
      return {
        date,
        success: true,
        totalProducts: data.estatisticas?.total_produtos || 0,
        totalValue: data.estatisticas?.valor_total_atual || 0,
        productsWithStock: data.estatisticas?.produtos_com_estoque || 0,
        dataCalculation: data.estatisticas?.data_calculo || date
      };
    } else {
      return {
        date,
        success: false,
        error: `HTTP ${response.status}`
      };
    }
  } catch (error) {
    return {
      date,
      success: false,
      error: error.message
    };
  }
}

async function findStockDates() {
  console.log('🔍 BUSCANDO DATAS COM DADOS DE ESTOQUE');
  console.log('='.repeat(60));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');

  // Check various dates
  const today = new Date();
  const datesToCheck = [];
  
  // Add today and previous days
  for (let i = 0; i < 30; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    datesToCheck.push(date.toISOString().split('T')[0]);
  }
  
  // Add some specific dates that might have data
  const specificDates = [
    '2024-12-31',
    '2024-12-01',
    '2024-11-01',
    '2024-10-01',
    '2024-09-01',
    '2024-08-01',
    '2024-07-01',
    '2024-06-01',
    '2024-05-01',
    '2024-04-01',
    '2024-03-01',
    '2024-02-01',
    '2024-01-01'
  ];
  
  datesToCheck.push(...specificDates);
  
  console.log(`📅 Verificando ${datesToCheck.length} datas...`);
  console.log('');

  const results = [];
  let foundData = false;

  for (const date of datesToCheck) {
    const result = await checkStockForDate(date);
    results.push(result);
    
    if (result.success && result.totalProducts > 0) {
      if (!foundData) {
        console.log('✅ DATAS COM DADOS DE ESTOQUE ENCONTRADAS:');
        console.log('-'.repeat(80));
        console.log('Data'.padEnd(12) + 'Produtos'.padStart(10) + 'Valor Total'.padStart(18) + 'Com Estoque'.padStart(12) + 'Data Cálculo'.padStart(15));
        console.log('-'.repeat(80));
        foundData = true;
      }
      
      console.log(
        `${result.date.padEnd(12)} ${formatNumber(result.totalProducts).padStart(8)} ${formatCurrency(result.totalValue).padStart(16)} ${formatNumber(result.productsWithStock).padStart(10)} ${result.dataCalculation.padStart(13)}`
      );
    }
    
    // Add small delay to avoid overwhelming the server
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  if (!foundData) {
    console.log('❌ Nenhuma data com dados de estoque encontrada');
    console.log('');
    console.log('🔍 Verificando se há dados sem filtro de data...');
    
    // Try without date filter
    const noDateResult = await checkStockForDate('');
    if (noDateResult.success && noDateResult.totalProducts > 0) {
      console.log('✅ Dados encontrados sem filtro de data:');
      console.log(`   📦 Total de Produtos: ${formatNumber(noDateResult.totalProducts)}`);
      console.log(`   💰 Valor Total: ${formatCurrency(noDateResult.totalValue)}`);
      console.log(`   ✅ Produtos com Estoque: ${formatNumber(noDateResult.productsWithStock)}`);
    }
  } else {
    console.log('-'.repeat(80));
    
    // Find the most recent date with data
    const datesWithData = results.filter(r => r.success && r.totalProducts > 0);
    if (datesWithData.length > 0) {
      const mostRecent = datesWithData[0];
      console.log('');
      console.log('🎯 DADOS MAIS RECENTES:');
      console.log(`   📅 Data: ${mostRecent.date}`);
      console.log(`   📦 Total de Produtos: ${formatNumber(mostRecent.totalProducts)}`);
      console.log(`   💰 Valor Total do Estoque: ${formatCurrency(mostRecent.totalValue)}`);
      console.log(`   ✅ Produtos com Estoque: ${formatNumber(mostRecent.productsWithStock)}`);
      console.log(`   📊 Data do Cálculo: ${mostRecent.dataCalculation}`);
    }
  }

  console.log('');
  console.log('🎯 RESUMO DA BUSCA');
  console.log('='.repeat(60));
  console.log(`📅 Datas verificadas: ${datesToCheck.length}`);
  console.log(`✅ Datas com dados: ${results.filter(r => r.success && r.totalProducts > 0).length}`);
  console.log(`❌ Datas sem dados: ${results.filter(r => !r.success || r.totalProducts === 0).length}`);
  
  if (foundData) {
    console.log('');
    console.log('💡 DICA: Use uma das datas com dados para testar o dashboard');
    console.log('   Exemplo: http://localhost:3000/dashboard?data=YYYY-MM-DD');
  }
}

// Execute the search
findStockDates();