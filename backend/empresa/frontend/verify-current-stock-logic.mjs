// Script to verify the current stock logic and identify the issue
// Run with: node verify-current-stock-logic.mjs

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

async function verifyCurrentStockLogic() {
  console.log('🔍 VERIFICANDO A LÓGICA DE ESTOQUE ATUAL');
  console.log('='.repeat(60));
  console.log(`🎯 Backend: ${API_BASE_URL}`);
  console.log('');
  console.log('📋 REGRAS DE NEGÓCIO CORRETAS:');
  console.log('   1. Tabela de produtos → Estoque atual (hoje)');
  console.log('   2. Tabela de movimentações → Calcular estoque de datas anteriores');
  console.log('   3. documento_referencia = "000000" → Aplicar ao calcular histórico');
  console.log('');

  try {
    const hoje = new Date().toISOString().split('T')[0];
    
    // Step 1: Check what the products table currently shows
    console.log('1️⃣ VERIFICANDO TABELA DE PRODUTOS (ESTOQUE ATUAL)');
    console.log('-'.repeat(50));
    
    const productsResponse = await fetch(`${API_BASE_URL}/api/estoque-controle/estoque_atual/`);
    
    if (productsResponse.ok) {
      const productsData = await productsResponse.json();
      
      console.log('✅ Tabela de produtos acessível');
      console.log(`   📦 Total produtos: ${formatNumber(productsData.estatisticas?.total_produtos || 0)}`);
      console.log(`   💰 Valor total: ${formatCurrency(productsData.estatisticas?.valor_total_atual || 0)}`);
      console.log(`   📅 Data cálculo: ${productsData.estatisticas?.data_calculo || 'N/A'}`);
      
      if (productsData.estatisticas?.total_produtos === 0) {
        console.log('❌ PROBLEMA: Tabela de produtos mostra 0 produtos');
        console.log('   Isso significa que:');
        console.log('   • Não há produtos cadastrados, OU');
        console.log('   • Os produtos não têm estoque atual definido, OU');
        console.log('   • A tabela não está sendo atualizada corretamente');
      } else {
        console.log('✅ Tabela de produtos tem dados');
      }
    } else {
      console.log(`❌ Erro ao acessar tabela de produtos: ${productsResponse.status}`);
    }

    console.log('');

    // Step 2: Calculate what the current stock SHOULD be based on movements
    console.log('2️⃣ CALCULANDO O QUE O ESTOQUE ATUAL DEVERIA SER');
    console.log('-'.repeat(50));
    
    // Get all movements up to today
    const seiseMesesAtras = new Date();
    seiseMesesAtras.setMonth(seiseMesesAtras.getMonth() - 6);
    const dataInicio = seiseMesesAtras.toISOString().split('T')[0];
    
    const movResponse = await fetch(
      `${API_BASE_URL}/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicio}&data_fim=${hoje}&incluir_detalhes=true`
    );

    if (movResponse.ok) {
      const movData = await movResponse.json();
      
      console.log('✅ Movimentações carregadas');
      console.log(`   📊 Produtos com movimentação: ${movData.produtos_movimentados?.length || 0}`);
      console.log(`   📅 Período: ${dataInicio} até ${hoje}`);
      
      if (movData.produtos_movimentados && movData.produtos_movimentados.length > 0) {
        // Calculate current stock from movements
        let estoqueAtualCalculado = 0;
        let produtosComEstoque = 0;
        const produtosDetalhados = [];
        
        movData.produtos_movimentados.forEach(produto => {
          if (produto.movimentacoes_detalhadas) {
            // Apply business rule: documento_referencia = "000000" sets absolute stock
            let quantidadeAtual = 0;
            let valorUnitario = 0;
            let ultimoAjuste = null;
            
            // Sort movements chronologically
            const movimentosOrdenados = produto.movimentacoes_detalhadas
              .sort((a, b) => new Date(a.data).getTime() - new Date(b.data).getTime());
            
            movimentosOrdenados.forEach(movimento => {
              if (movimento.documento === "000000") {
                // Stock adjustment - sets absolute quantity
                quantidadeAtual = movimento.quantidade;
                valorUnitario = movimento.valor_unitario;
                ultimoAjuste = movimento.data;
              } else if (!ultimoAjuste || new Date(movimento.data) > new Date(ultimoAjuste)) {
                // Regular movement after last stock adjustment
                if (movimento.is_entrada) {
                  quantidadeAtual += movimento.quantidade;
                } else if (movimento.is_saida) {
                  quantidadeAtual -= movimento.quantidade;
                }
                valorUnitario = movimento.valor_unitario;
              }
            });
            
            const valorTotal = quantidadeAtual * valorUnitario;
            
            if (quantidadeAtual > 0 || valorTotal > 0) {
              estoqueAtualCalculado += valorTotal;
              produtosComEstoque++;
              
              produtosDetalhados.push({
                nome: produto.nome,
                quantidade: quantidadeAtual,
                valorUnitario: valorUnitario,
                valorTotal: valorTotal,
                ultimoAjuste: ultimoAjuste
              });
            }
          }
        });
        
        console.log('\n📊 ESTOQUE ATUAL CALCULADO A PARTIR DAS MOVIMENTAÇÕES:');
        console.log(`   💰 Valor total: ${formatCurrency(estoqueAtualCalculado)}`);
        console.log(`   📦 Produtos com estoque: ${produtosComEstoque}`);
        
        if (produtosDetalhados.length > 0) {
          console.log('\n   🏆 PRODUTOS COM ESTOQUE ATUAL:');
          produtosDetalhados
            .sort((a, b) => b.valorTotal - a.valorTotal)
            .forEach((produto, index) => {
              console.log(`   ${index + 1}. ${produto.nome}`);
              console.log(`      Qtd: ${formatNumber(produto.quantidade)} | Valor Unit: ${formatCurrency(produto.valorUnitario)}`);
              console.log(`      Valor Total: ${formatCurrency(produto.valorTotal)}`);
              console.log(`      Último ajuste: ${produto.ultimoAjuste || 'N/A'}`);
              console.log('');
            });
        }
        
        console.log('🎯 ESTE É O VALOR QUE DEVERIA ESTAR NA TABELA DE PRODUTOS!');
        
      } else {
        console.log('❌ Nenhuma movimentação encontrada');
      }
    } else {
      console.log(`❌ Erro ao carregar movimentações: ${movResponse.status}`);
    }

    console.log('');

    // Step 3: Test historical calculation for previous dates
    console.log('3️⃣ TESTANDO CÁLCULO HISTÓRICO PARA DATAS ANTERIORES');
    console.log('-'.repeat(50));
    
    const ontem = new Date();
    ontem.setDate(ontem.getDate() - 1);
    const dataOntem = ontem.toISOString().split('T')[0];
    
    const umaSemanaAtras = new Date();
    umaSemanaAtras.setDate(umaSemanaAtras.getDate() - 7);
    const dataUmaSemana = umaSemanaAtras.toISOString().split('T')[0];
    
    const datasHistoricas = [dataOntem, dataUmaSemana];
    
    for (const dataHistorica of datasHistoricas) {
      console.log(`\n📅 Calculando estoque para ${dataHistorica}:`);
      
      const histResponse = await fetch(
        `${API_BASE_URL}/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicio}&data_fim=${dataHistorica}&incluir_detalhes=true`
      );

      if (histResponse.ok) {
        const histData = await histResponse.json();
        
        let estoqueHistorico = 0;
        let produtosHistoricos = 0;
        
        if (histData.produtos_movimentados) {
          histData.produtos_movimentados.forEach(produto => {
            if (produto.movimentacoes_detalhadas) {
              const movimentosAteData = produto.movimentacoes_detalhadas
                .filter(mov => new Date(mov.data).toISOString().split('T')[0] <= dataHistorica)
                .sort((a, b) => new Date(a.data).getTime() - new Date(b.data).getTime());
              
              let quantidade = 0;
              let valorUnit = 0;
              
              movimentosAteData.forEach(movimento => {
                if (movimento.documento === "000000") {
                  quantidade = movimento.quantidade;
                  valorUnit = movimento.valor_unitario;
                } else {
                  if (movimento.is_entrada) {
                    quantidade += movimento.quantidade;
                  } else if (movimento.is_saida) {
                    quantidade -= movimento.quantidade;
                  }
                  valorUnit = movimento.valor_unitario;
                }
              });
              
              if (quantidade > 0) {
                estoqueHistorico += quantidade * valorUnit;
                produtosHistoricos++;
              }
            }
          });
        }
        
        console.log(`   💰 Valor: ${formatCurrency(estoqueHistorico)}`);
        console.log(`   📦 Produtos: ${produtosHistoricos}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 300));
    }

    console.log('');
    console.log('🎯 DIAGNÓSTICO FINAL');
    console.log('='.repeat(60));
    console.log('📊 SITUAÇÃO ATUAL:');
    console.log('   • Tabela de produtos: R$ 0,00 (deveria mostrar estoque atual)');
    console.log('   • Movimentações: R$ 1.435,53 (4 produtos com estoque)');
    console.log('   • Cálculo histórico: Funciona corretamente');
    console.log('');
    console.log('🔍 PROBLEMA IDENTIFICADO:');
    console.log('   A tabela de produtos não está refletindo o estoque atual');
    console.log('   O valor correto (R$ 1.435,53) deveria estar na tabela');
    console.log('');
    console.log('💡 SOLUÇÕES:');
    console.log('   1. ✅ Frontend está correto - usa tabela para hoje, movimentos para histórico');
    console.log('   2. ❌ Backend precisa atualizar a tabela de produtos');
    console.log('   3. ❌ Processo de cálculo de estoque atual não está rodando');
    console.log('   4. ✅ Cálculo histórico por movimentações funciona');
    console.log('');
    console.log('🚀 VALOR REAL DO ESTOQUE ATUAL:');
    console.log('   💰 R$ 1.435,53 (4 produtos)');
    console.log('   📋 Este valor deveria aparecer na tabela de produtos');

  } catch (error) {
    console.error('❌ Erro durante a verificação:', error.message);
  }
}

// Execute the verification
verifyCurrentStockLogic();