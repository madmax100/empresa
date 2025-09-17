// Script to check the products table directly for actual stock value
// Run with: node check-products-table.mjs

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

async function checkProductsTable() {
  console.log('📊 VERIFICANDO A TABELA DE PRODUTOS DIRETAMENTE');
  console.log('='.repeat(60));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');
  console.log('📋 OBJETIVO: Ver o estoque atual na tabela de produtos');
  console.log('   (Conforme regra: tabela de produtos = estoque atual)');
  console.log('');

  try {
    // Method 1: Try without any filters to get all products
    console.log('1️⃣ BUSCANDO TODOS OS PRODUTOS (SEM FILTROS)');
    console.log('-'.repeat(50));
    
    const allProductsResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/`);
    
    if (allProductsResponse.ok) {
      const allProductsData = await allProductsResponse.json();
      
      console.log('✅ Resposta recebida da tabela de produtos');
      console.log(`   📦 Total produtos: ${formatNumber(allProductsData.estatisticas?.total_produtos || 0)}`);
      console.log(`   💰 Valor total: ${formatCurrency(allProductsData.estatisticas?.valor_total_atual || 0)}`);
      console.log(`   ✅ Produtos com estoque: ${formatNumber(allProductsData.estatisticas?.produtos_com_estoque || 0)}`);
      console.log(`   ❌ Produtos zerados: ${formatNumber(allProductsData.estatisticas?.produtos_zerados || 0)}`);
      console.log(`   📅 Data cálculo: ${allProductsData.estatisticas?.data_calculo || 'N/A'}`);
      console.log(`   📊 Total registros: ${formatNumber(allProductsData.parametros?.total_registros || 0)}`);
      
      if (allProductsData.estoque && allProductsData.estoque.length > 0) {
        console.log('\n🎯 PRODUTOS ENCONTRADOS NA TABELA!');
        console.log(`   📋 Produtos retornados: ${allProductsData.estoque.length}`);
        
        // Show all products with their stock
        console.log('\n📦 LISTA COMPLETA DE PRODUTOS:');
        console.log('-'.repeat(100));
        console.log('ID'.padEnd(6) + 'Nome'.padEnd(40) + 'Qtd Atual'.padStart(12) + 'Valor Unit.'.padStart(15) + 'Valor Total'.padStart(15));
        console.log('-'.repeat(100));
        
        let totalValueCalculated = 0;
        let productsWithStockCount = 0;
        
        allProductsData.estoque.forEach(produto => {
          const id = produto.produto_id.toString().padEnd(6);
          const nome = produto.nome.length > 38 ? produto.nome.substring(0, 35) + '...' : produto.nome.padEnd(40);
          const qtdAtual = formatNumber(produto.quantidade_atual).padStart(10);
          const valorUnit = formatCurrency(produto.custo_unitario_inicial || produto.valor_inicial / produto.quantidade_inicial || 0).padStart(13);
          const valorTotal = formatCurrency(produto.valor_atual).padStart(13);
          
          console.log(`${id}${nome}${qtdAtual}${valorUnit}${valorTotal}`);
          
          totalValueCalculated += produto.valor_atual || 0;
          if (produto.quantidade_atual > 0) {
            productsWithStockCount++;
          }
        });
        
        console.log('-'.repeat(100));
        console.log(`TOTAL CALCULADO: ${formatCurrency(totalValueCalculated)}`);
        console.log(`PRODUTOS COM ESTOQUE: ${productsWithStockCount}`);
        
        // Show top products by value
        console.log('\n🏆 TOP 10 PRODUTOS POR VALOR:');
        console.log('-'.repeat(80));
        
        const topProducts = allProductsData.estoque
          .filter(p => p.valor_atual > 0)
          .sort((a, b) => b.valor_atual - a.valor_atual)
          .slice(0, 10);
        
        topProducts.forEach((produto, index) => {
          console.log(`${index + 1}. ${produto.nome}`);
          console.log(`   Qtd: ${formatNumber(produto.quantidade_atual)} | Valor Unit: ${formatCurrency(produto.custo_unitario_inicial)}`);
          console.log(`   Valor Total: ${formatCurrency(produto.valor_atual)} | Ref: ${produto.referencia}`);
          console.log('');
        });
        
      } else {
        console.log('❌ Nenhum produto encontrado na resposta');
        console.log('   Isso pode indicar que:');
        console.log('   • A tabela de produtos está vazia');
        console.log('   • Há filtros sendo aplicados no backend');
        console.log('   • Os produtos não têm estoque atual');
      }
    } else {
      const errorText = await allProductsResponse.text();
      console.log(`❌ Erro ao acessar tabela de produtos: ${allProductsResponse.status}`);
      console.log(`   Detalhes: ${errorText}`);
    }

    console.log('');

    // Method 2: Try with different limits to see if there's pagination
    console.log('2️⃣ TESTANDO DIFERENTES LIMITES DE PAGINAÇÃO');
    console.log('-'.repeat(50));
    
    const limits = [10, 50, 100, 500, 1000];
    
    for (const limit of limits) {
      const limitResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?limite=${limit}`);
      
      if (limitResponse.ok) {
        const limitData = await limitResponse.json();
        const totalProducts = limitData.estatisticas?.total_produtos || 0;
        const totalValue = limitData.estatisticas?.valor_total_atual || 0;
        const returnedProducts = limitData.estoque?.length || 0;
        
        console.log(`   Limite ${limit}: ${formatNumber(totalProducts)} produtos total, ${returnedProducts} retornados, ${formatCurrency(totalValue)}`);
        
        if (totalProducts > 0) {
          console.log(`      🎯 DADOS ENCONTRADOS COM LIMITE ${limit}!`);
          break;
        }
      } else {
        console.log(`   Limite ${limit}: Erro ${limitResponse.status}`);
      }
      
      // Small delay
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.log('');

    // Method 3: Try without date filter but with large limit
    console.log('3️⃣ BUSCANDO COM LIMITE MÁXIMO');
    console.log('-'.repeat(50));
    
    const maxLimitResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?limite=10000`);
    
    if (maxLimitResponse.ok) {
      const maxLimitData = await maxLimitResponse.json();
      
      console.log('✅ Resposta com limite máximo recebida');
      console.log(`   📦 Total produtos: ${formatNumber(maxLimitData.estatisticas?.total_produtos || 0)}`);
      console.log(`   💰 Valor total: ${formatCurrency(maxLimitData.estatisticas?.valor_total_atual || 0)}`);
      console.log(`   📋 Produtos retornados: ${maxLimitData.estoque?.length || 0}`);
      console.log(`   📊 Total registros: ${formatNumber(maxLimitData.parametros?.total_registros || 0)}`);
      
      if (maxLimitData.estatisticas?.total_produtos > 0) {
        console.log('\n🎯 VALOR REAL DO ESTOQUE NA TABELA DE PRODUTOS:');
        console.log(`💰 VALOR TOTAL: ${formatCurrency(maxLimitData.estatisticas.valor_total_atual)}`);
        console.log(`📦 TOTAL PRODUTOS: ${formatNumber(maxLimitData.estatisticas.total_produtos)}`);
        console.log(`✅ PRODUTOS COM ESTOQUE: ${formatNumber(maxLimitData.estatisticas.produtos_com_estoque)}`);
        console.log(`❌ PRODUTOS ZERADOS: ${formatNumber(maxLimitData.estatisticas.produtos_zerados)}`);
      }
    } else {
      console.log(`❌ Erro com limite máximo: ${maxLimitResponse.status}`);
    }

    console.log('');
    console.log('🎯 CONCLUSÃO SOBRE A TABELA DE PRODUTOS');
    console.log('='.repeat(60));
    console.log('📋 A tabela de produtos deveria mostrar o estoque atual');
    console.log('📊 Se não há dados, pode ser que:');
    console.log('   • A tabela está realmente vazia');
    console.log('   • Há filtros de data sendo aplicados');
    console.log('   • O backend não está retornando os dados corretos');
    console.log('   • Os produtos não têm quantidade atual definida');

  } catch (error) {
    console.error('❌ Erro durante a verificação:', error.message);
    console.log('\n🔧 Verifique se o backend está rodando:');
    console.log('   python manage.py runserver 127.0.0.1:8000');
  }
}

// Execute the check
checkProductsTable();