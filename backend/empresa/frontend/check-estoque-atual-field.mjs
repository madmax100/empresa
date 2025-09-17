// Script to check the estoque_atual field in the products table
// Run with: node check-estoque-atual-field.mjs

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

async function checkEstoqueAtualField() {
  console.log('📊 VERIFICANDO CAMPO estoque_atual NA TABELA DE PRODUTOS');
  console.log('='.repeat(70));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');
  console.log('📋 OBJETIVO: Verificar o campo estoque_atual que mostra o estoque atual');
  console.log('');

  try {
    // Get stock data and examine the estoque_atual field specifically
    console.log('1️⃣ BUSCANDO DADOS DO ENDPOINT DE ESTOQUE');
    console.log('-'.repeat(50));
    
    const response = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/?limite=1000`);
    
    if (!response.ok) {
      console.log(`❌ Erro no endpoint: ${response.status}`);
      const errorText = await response.text();
      console.log(`   Detalhes: ${errorText}`);
      return;
    }

    const data = await response.json();
    
    console.log('✅ Dados recebidos do endpoint');
    console.log(`   📊 Total produtos: ${formatNumber(data.estatisticas?.total_produtos || 0)}`);
    console.log(`   💰 Valor total: ${formatCurrency(data.estatisticas?.valor_total_atual || 0)}`);
    console.log(`   📦 Produtos retornados: ${data.estoque?.length || 0}`);
    
    if (data.estoque && data.estoque.length > 0) {
      console.log('\n2️⃣ ANALISANDO CAMPO estoque_atual NOS PRODUTOS');
      console.log('-'.repeat(50));
      
      // Check what fields are available in the product data
      const firstProduct = data.estoque[0];
      console.log('🔍 CAMPOS DISPONÍVEIS NO PRIMEIRO PRODUTO:');
      Object.keys(firstProduct).forEach(key => {
        console.log(`   ${key}: ${firstProduct[key]} (${typeof firstProduct[key]})`);
      });
      
      console.log('\n📦 PRODUTOS COM ESTOQUE ATUAL:');
      console.log('-'.repeat(100));
      console.log('ID'.padEnd(6) + 'Nome'.padEnd(40) + 'Estoque Atual'.padStart(15) + 'Qtd Atual'.padStart(12) + 'Valor Total'.padStart(15));
      console.log('-'.repeat(100));
      
      let totalValueFromEstoqueAtual = 0;
      let productsWithStock = 0;
      
      data.estoque.forEach(produto => {
        // Check different possible field names for current stock
        const estoqueAtual = produto.estoque_atual || produto.quantidade_atual || 0;
        const valorUnitario = produto.valor_unitario || produto.custo_unitario_inicial || 0;
        const valorTotal = produto.valor_atual || (estoqueAtual * valorUnitario) || 0;
        
        if (estoqueAtual > 0 || valorTotal > 0) {
          const id = produto.produto_id.toString().padEnd(6);
          const nome = produto.nome.length > 38 ? produto.nome.substring(0, 35) + '...' : produto.nome.padEnd(40);
          const estoque = formatNumber(estoqueAtual).padStart(13);
          const qtdAtual = formatNumber(produto.quantidade_atual || 0).padStart(10);
          const valor = formatCurrency(valorTotal).padStart(13);
          
          console.log(`${id}${nome}${estoque}${qtdAtual}${valor}`);
          
          totalValueFromEstoqueAtual += valorTotal;
          productsWithStock++;
        }
      });
      
      console.log('-'.repeat(100));
      console.log(`TOTAL DE PRODUTOS COM ESTOQUE: ${productsWithStock}`);
      console.log(`VALOR TOTAL CALCULADO: ${formatCurrency(totalValueFromEstoqueAtual)}`);
      
      if (productsWithStock === 0) {
        console.log('\n❌ NENHUM PRODUTO COM ESTOQUE ENCONTRADO');
        console.log('   Verificando todos os produtos (incluindo zerados):');
        console.log('-'.repeat(80));
        console.log('ID'.padEnd(6) + 'Nome'.padEnd(50) + 'Todos os Campos de Quantidade'.padStart(25));
        console.log('-'.repeat(80));
        
        data.estoque.slice(0, 10).forEach(produto => {
          const id = produto.produto_id.toString().padEnd(6);
          const nome = produto.nome.length > 48 ? produto.nome.substring(0, 45) + '...' : produto.nome.padEnd(50);
          
          console.log(`${id}${nome}`);
          console.log(`      estoque_atual: ${produto.estoque_atual || 'N/A'}`);
          console.log(`      quantidade_atual: ${produto.quantidade_atual || 'N/A'}`);
          console.log(`      quantidade_inicial: ${produto.quantidade_inicial || 'N/A'}`);
          console.log(`      valor_atual: ${formatCurrency(produto.valor_atual || 0)}`);
          console.log(`      valor_inicial: ${formatCurrency(produto.valor_inicial || 0)}`);
          console.log('');
        });
      }
      
    } else {
      console.log('\n❌ NENHUM PRODUTO RETORNADO PELO ENDPOINT');
      
      // Let's check if the issue is with the endpoint structure
      console.log('\n🔍 ESTRUTURA COMPLETA DA RESPOSTA:');
      console.log(JSON.stringify(data, null, 2));
    }

    // Try to get products with different parameters
    console.log('\n3️⃣ TESTANDO PARÂMETROS ALTERNATIVOS');
    console.log('-'.repeat(50));
    
    const alternativeParams = [
      '?incluir_zerados=true',
      '?mostrar_todos=true', 
      '?limite=0',
      '?data=2024-12-31',
      '?data=2024-01-01',
      ''
    ];
    
    for (const param of alternativeParams) {
      try {
        const altResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/${param}`);
        
        if (altResponse.ok) {
          const altData = await altResponse.json();
          const totalProducts = altData.estatisticas?.total_produtos || 0;
          const totalValue = altData.estatisticas?.valor_total_atual || 0;
          const returnedProducts = altData.estoque?.length || 0;
          
          console.log(`   ${param || 'sem parâmetros'}: ${formatNumber(totalProducts)} total, ${returnedProducts} retornados, ${formatCurrency(totalValue)}`);
          
          if (totalProducts > 0 && altData.estoque && altData.estoque.length > 0) {
            console.log(`      🎯 DADOS ENCONTRADOS! Primeiro produto:`);
            const primeiro = altData.estoque[0];
            console.log(`         Nome: ${primeiro.nome}`);
            console.log(`         estoque_atual: ${primeiro.estoque_atual || 'N/A'}`);
            console.log(`         quantidade_atual: ${primeiro.quantidade_atual || 'N/A'}`);
            console.log(`         valor_atual: ${formatCurrency(primeiro.valor_atual || 0)}`);
            
            // If we found data, show more details
            if (primeiro.estoque_atual > 0 || primeiro.quantidade_atual > 0) {
              console.log('\n      📦 PRODUTOS COM ESTOQUE ATUAL > 0:');
              altData.estoque
                .filter(p => (p.estoque_atual > 0) || (p.quantidade_atual > 0))
                .slice(0, 5)
                .forEach(produto => {
                  console.log(`         • ${produto.nome}`);
                  console.log(`           Estoque: ${produto.estoque_atual || produto.quantidade_atual || 0}`);
                  console.log(`           Valor: ${formatCurrency(produto.valor_atual || 0)}`);
                });
            }
            break;
          }
        } else {
          console.log(`   ${param || 'sem parâmetros'}: Erro ${altResponse.status}`);
        }
      } catch (error) {
        console.log(`   ${param || 'sem parâmetros'}: Exception - ${error.message}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 300));
    }

    console.log('\n🎯 CONCLUSÃO SOBRE O CAMPO estoque_atual');
    console.log('='.repeat(70));
    console.log('📊 SITUAÇÃO ENCONTRADA:');
    console.log('   • Campo estoque_atual deveria mostrar o estoque atual');
    console.log('   • Endpoint está retornando dados mas com valores zerados');
    console.log('   • Pode ser que o campo não esteja sendo populado corretamente');
    console.log('');
    console.log('💡 POSSÍVEIS SOLUÇÕES:');
    console.log('   1. Verificar se o campo estoque_atual está sendo atualizado');
    console.log('   2. Verificar se há um processo que calcula o estoque atual');
    console.log('   3. Verificar se os dados estão em outro campo');
    console.log('   4. Usar movimentações para calcular o estoque atual');
    console.log('');
    console.log('🔍 VALOR REAL CONHECIDO:');
    console.log('   Das movimentações: R$ 1.435,53 (4 produtos)');
    console.log('   Este valor deveria estar no campo estoque_atual');

  } catch (error) {
    console.error('❌ Erro durante a verificação:', error.message);
    console.log('\n🔧 Verifique se o backend está rodando:');
    console.log('   python manage.py runserver 127.0.0.1:8000');
  }
}

// Execute the check
checkEstoqueAtualField();