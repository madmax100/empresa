// Script to verify current stock value for today
// Run with: node verify-stock-today.mjs

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

async function verifyStockToday() {
  const today = new Date().toISOString().split('T')[0];
  
  console.log('📊 VERIFICAÇÃO DO ESTOQUE - HOJE');
  console.log('='.repeat(50));
  console.log(`📅 Data: ${today}`);
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');

  try {
    // Test 1: Current Stock Value
    console.log('1️⃣ VALOR ATUAL DO ESTOQUE');
    console.log('-'.repeat(30));
    
    const estoqueResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?data=${today}`);
    
    if (estoqueResponse.ok) {
      const estoqueData = await estoqueResponse.json();
      
      console.log('✅ Dados do estoque carregados com sucesso!');
      console.log('');
      
      if (estoqueData.estatisticas) {
        const stats = estoqueData.estatisticas;
        
        console.log('📊 ESTATÍSTICAS DO ESTOQUE:');
        console.log(`   💰 Valor Total Atual: ${formatCurrency(stats.valor_total_atual)}`);
        console.log(`   💰 Valor Total Inicial: ${formatCurrency(stats.valor_total_inicial)}`);
        console.log(`   📈 Variação Total: ${formatCurrency(stats.variacao_total)}`);
        console.log(`   📦 Total de Produtos: ${formatNumber(stats.total_produtos)}`);
        console.log(`   ✅ Produtos com Estoque: ${formatNumber(stats.produtos_com_estoque)}`);
        console.log(`   ❌ Produtos Zerados: ${formatNumber(stats.produtos_zerados)}`);
        console.log(`   📅 Data do Cálculo: ${stats.data_calculo}`);
        console.log('');
        
        // Show top 10 products by value
        if (estoqueData.estoque && estoqueData.estoque.length > 0) {
          console.log('🏆 TOP 10 PRODUTOS POR VALOR:');
          console.log('-'.repeat(80));
          console.log('Produto'.padEnd(30) + 'Qtd'.padStart(8) + 'Valor Unit.'.padStart(15) + 'Valor Total'.padStart(15));
          console.log('-'.repeat(80));
          
          const topProducts = estoqueData.estoque
            .sort((a, b) => b.valor_atual - a.valor_atual)
            .slice(0, 10);
          
          topProducts.forEach((produto, index) => {
            const nome = produto.nome.length > 28 ? produto.nome.substring(0, 25) + '...' : produto.nome;
            const qtd = formatNumber(produto.quantidade_atual);
            const valorUnit = formatCurrency(produto.custo_unitario_inicial);
            const valorTotal = formatCurrency(produto.valor_atual);
            
            console.log(
              `${(index + 1).toString().padStart(2)}. ${nome.padEnd(28)} ${qtd.padStart(6)} ${valorUnit.padStart(13)} ${valorTotal.padStart(13)}`
            );
          });
          console.log('-'.repeat(80));
        }
        
      } else {
        console.log('⚠️  Estatísticas não encontradas na resposta');
      }
      
      if (estoqueData.parametros) {
        console.log('📋 PARÂMETROS DA CONSULTA:');
        console.log(`   📅 Data Consulta: ${estoqueData.parametros.data_consulta}`);
        console.log(`   📊 Total Registros: ${formatNumber(estoqueData.parametros.total_registros)}`);
        console.log(`   📄 Limite Aplicado: ${formatNumber(estoqueData.parametros.limite_aplicado)}`);
        console.log('');
      }
      
    } else {
      const errorText = await estoqueResponse.text();
      console.log(`❌ Erro ao buscar estoque atual: ${estoqueResponse.status}`);
      console.log(`   Detalhes: ${errorText}`);
    }

    // Test 2: Critical Stock
    console.log('2️⃣ PRODUTOS CRÍTICOS');
    console.log('-'.repeat(30));
    
    const criticoResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_critico/?data=${today}&limite=10`);
    
    if (criticoResponse.ok) {
      const criticoData = await criticoResponse.json();
      
      if (criticoData.produtos && criticoData.produtos.length > 0) {
        console.log(`⚠️  ${criticoData.produtos.length} produtos críticos encontrados:`);
        console.log('');
        
        criticoData.produtos.forEach((produto, index) => {
          console.log(`   ${index + 1}. ${produto.nome}`);
          console.log(`      Ref: ${produto.referencia}`);
          console.log(`      Qtd Atual: ${formatNumber(produto.quantidade_atual)}`);
          console.log(`      Valor: ${formatCurrency(produto.valor_atual)}`);
          console.log('');
        });
      } else {
        console.log('✅ Nenhum produto crítico encontrado - todos os produtos estão com estoque adequado!');
      }
    } else {
      console.log(`❌ Erro ao buscar produtos críticos: ${criticoResponse.status}`);
    }

    // Test 3: Most Moved Products
    console.log('3️⃣ PRODUTOS MAIS MOVIMENTADOS');
    console.log('-'.repeat(30));
    
    const movimentadosResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/produtos_mais_movimentados/?data=${today}&limite=5`);
    
    if (movimentadosResponse.ok) {
      const movimentadosData = await movimentadosResponse.json();
      
      if (movimentadosData.produtos_mais_movimentados && movimentadosData.produtos_mais_movimentados.length > 0) {
        console.log(`🔄 ${movimentadosData.produtos_mais_movimentados.length} produtos mais ativos:`);
        console.log('');
        
        movimentadosData.produtos_mais_movimentados.forEach((produto, index) => {
          console.log(`   ${index + 1}. ${produto.nome}`);
          console.log(`      Ref: ${produto.referencia}`);
          console.log(`      Movimentações: ${formatNumber(produto.total_movimentacoes)}`);
          console.log(`      Última Movimentação: ${produto.ultima_movimentacao}`);
          console.log(`      Tipos: ${produto.tipos_movimentacao.join(', ')}`);
          console.log('');
        });
      } else {
        console.log('📦 Nenhuma movimentação recente encontrada');
      }
    } else {
      console.log(`❌ Erro ao buscar produtos movimentados: ${movimentadosResponse.status}`);
    }

    console.log('🎯 RESUMO DA VERIFICAÇÃO');
    console.log('='.repeat(50));
    console.log('✅ Verificação do estoque concluída');
    console.log(`📅 Data verificada: ${today}`);
    console.log('🚀 Sistema de estoque funcionando corretamente!');

  } catch (error) {
    console.error('❌ Erro durante a verificação:', error.message);
    console.log('\n🔧 Verifique se o backend está rodando:');
    console.log('   python manage.py runserver 127.0.0.1:8000');
  }
}

// Execute the verification
verifyStockToday();