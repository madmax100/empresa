// Correct Stock Dashboard following the proper business rules:
// 1. Products table = current stock (today)
// 2. Movement table = historical stock calculation (previous dates)
// 3. documento_referencia field must be observed for historical calculations

import React, { useState, useEffect } from 'react';
import { formatCurrency } from '../../lib/utils';

interface ProdutoEstoque {
  produto_id: number;
  nome: string;
  referencia: string;
  quantidade_inicial: number;
  quantidade_atual: number;
  variacao_quantidade: number;
  custo_unitario_inicial: number;
  valor_inicial: number;
  valor_atual: number;
  variacao_valor: number;
  total_movimentacoes: number;
  data_calculo: string;
  movimentacoes_recentes: unknown[];
}

interface EstoqueAtualData {
  estoque: ProdutoEstoque[];
  estatisticas: {
    total_produtos: number;
    produtos_com_estoque: number;
    produtos_zerados: number;
    valor_total_inicial: number;
    valor_total_atual: number;
    variacao_total: number;
    data_calculo: string;
  };
  parametros: {
    data_consulta: string;
    produto_id: number | null;
    total_registros: number;
    limite_aplicado: number;
  };
}

interface MovimentacaoDetalhada {
  id: number;
  data: string;
  tipo: string;
  tipo_codigo: string;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
  documento: string;
  operador: string;
  observacoes: string;
  is_entrada: boolean;
  is_saida: boolean;
}

interface ProdutoMovimentado {
  produto_id: number;
  nome: string;
  referencia: string;
  quantidade_entrada: number;
  quantidade_saida: number;
  valor_entrada: number;
  valor_saida: number;
  saldo_quantidade: number;
  saldo_valor: number;
  total_movimentacoes: number;
  movimentacoes_detalhadas?: MovimentacaoDetalhada[];
}

interface MovimentacoesPeriodoData {
  produtos_movimentados: ProdutoMovimentado[];
  resumo: {
    periodo: string;
    total_produtos: number;
    total_movimentacoes: number;
    valor_total_entradas: number;
    valor_total_saidas: number;
  };
}

const EstoqueDashboardCorrect: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSelecionada, setDataSelecionada] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [estoqueData, setEstoqueData] = useState<EstoqueAtualData | null>(null);
  const [movimentacoesData, setMovimentacoesData] = useState<MovimentacoesPeriodoData | null>(null);
  const [isCurrentDate, setIsCurrentDate] = useState(true);

  const formatNumber = (value: number | undefined | null): string => {
    if (value === undefined || value === null || isNaN(value)) {
      return '0';
    }
    return value.toLocaleString('pt-BR');
  };

  const formatDate = (dateString: string): string => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('pt-BR');
    } catch {
      return 'N/A';
    }
  };

  const isToday = (date: string): boolean => {
    const today = new Date().toISOString().split('T')[0];
    return date === today;
  };

  const loadStockForDate = async (targetDate: string) => {
    try {
      console.log(`📦 Loading stock for date: ${targetDate}`);
      
      // Always use the backend endpoint with date parameter
      // Let the backend decide whether to use products table or calculate from movements
      const response = await fetch(`http://127.0.0.1:8000/api/estoque-controle/estoque_atual/?data=${targetDate}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      const data: EstoqueAtualData = await response.json();
      setEstoqueData(data);
      
      console.log(`✅ Stock loaded for ${targetDate}`);
      console.log(`📊 Total products: ${data.estatisticas?.total_produtos || 0}`);
      console.log(`💰 Total value: ${formatCurrency(data.estatisticas?.valor_total_atual || 0)}`);
      console.log(`📅 Data calculation: ${data.estatisticas?.data_calculo || 'N/A'}`);
      
      return data;
    } catch (err) {
      console.error(`❌ Error loading stock for ${targetDate}:`, err);
      throw err;
    }
  };

  const loadMovementDataForAnalysis = async (targetDate: string) => {
    try {
      console.log(`📊 Loading movement data for analysis: ${targetDate}`);
      
      // Get movements from a period that includes the target date for analysis
      const startDate = new Date(targetDate);
      startDate.setMonth(startDate.getMonth() - 3); // 3 months before target date
      
      const dataInicio = startDate.toISOString().split('T')[0];
      const dataFim = targetDate;
      
      const response = await fetch(
        `http://127.0.0.1:8000/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicio}&data_fim=${dataFim}&incluir_detalhes=true`
      );

      if (!response.ok) {
        console.log('⚠️ Could not load movement data for analysis');
        return null;
      }

      const data: MovimentacoesPeriodoData = await response.json();
      setMovimentacoesData(data);
      
      console.log('✅ Movement data loaded for analysis');
      console.log(`📊 Products with movements: ${data.produtos_movimentados?.length || 0}`);
      
      return data;
    } catch (err) {
      console.error('❌ Error loading movement data:', err);
      return null;
    }
  };

  const calculateHistoricalStock = (movData: MovimentacoesPeriodoData, targetDate: string): EstoqueAtualData => {
    console.log(`🧮 Calculating historical stock for ${targetDate}...`);
    console.log('📋 Applying documento_referencia business rules...');
    
    const produtos: ProdutoEstoque[] = [];
    let totalProdutos = 0;
    let produtosComEstoque = 0;
    let produtosZerados = 0;
    let valorTotalAtual = 0;
    
    movData.produtos_movimentados.forEach(produto => {
      if (!produto.movimentacoes_detalhadas) return;
      
      // Filter movements up to target date and apply documento_referencia rules
      const movimentosValidos = produto.movimentacoes_detalhadas
        .filter(mov => {
          const movDate = new Date(mov.data).toISOString().split('T')[0];
          return movDate <= targetDate;
        })
        .sort((a, b) => new Date(a.data).getTime() - new Date(b.data).getTime());
      
      if (movimentosValidos.length === 0) return;
      
      let quantidadeAtual = 0;
      let valorUnitario = 0;
      let valorTotal = 0;
      
      // Apply business rule for documento_referencia
      let stockSetByAdjustment = false;
      
      movimentosValidos.forEach(movimento => {
        if (movimento.documento === "000000") {
          // Stock adjustment - this sets the absolute stock quantity
          quantidadeAtual = movimento.quantidade;
          valorUnitario = movimento.valor_unitario;
          stockSetByAdjustment = true;
          console.log(`📦 Stock adjustment for ${produto.nome}: ${quantidadeAtual} units`);
        } else if (!stockSetByAdjustment) {
          // Regular movement - only apply if no stock adjustment has been made
          if (movimento.is_entrada) {
            quantidadeAtual += movimento.quantidade;
          } else if (movimento.is_saida) {
            quantidadeAtual -= movimento.quantidade;
          }
          valorUnitario = movimento.valor_unitario;
        }
        // If stock was set by adjustment, ignore regular movements after that
      });
      
      valorTotal = quantidadeAtual * valorUnitario;
      
      if (quantidadeAtual !== 0 || valorTotal !== 0) {
        produtos.push({
          produto_id: produto.produto_id,
          nome: produto.nome,
          referencia: produto.referencia,
          quantidade_inicial: 0, // Not available in movements
          quantidade_atual: quantidadeAtual,
          variacao_quantidade: 0, // Not calculated for historical
          custo_unitario_inicial: valorUnitario,
          valor_inicial: 0, // Not available
          valor_atual: valorTotal,
          variacao_valor: 0, // Not calculated for historical
          total_movimentacoes: movimentosValidos.length,
          data_calculo: targetDate,
          movimentacoes_recentes: []
        });
        
        totalProdutos++;
        if (quantidadeAtual > 0) {
          produtosComEstoque++;
        } else {
          produtosZerados++;
        }
        valorTotalAtual += valorTotal;
      }
    });
    
    console.log(`✅ Historical calculation complete:`);
    console.log(`   📦 Products: ${totalProdutos}`);
    console.log(`   ✅ With stock: ${produtosComEstoque}`);
    console.log(`   ❌ Zero stock: ${produtosZerados}`);
    console.log(`   💰 Total value: ${formatCurrency(valorTotalAtual)}`);
    
    return {
      estoque: produtos,
      estatisticas: {
        total_produtos: totalProdutos,
        produtos_com_estoque: produtosComEstoque,
        produtos_zerados: produtosZerados,
        valor_total_inicial: 0,
        valor_total_atual: valorTotalAtual,
        variacao_total: 0,
        data_calculo: targetDate
      },
      parametros: {
        data_consulta: targetDate,
        produto_id: null,
        total_registros: totalProdutos,
        limite_aplicado: totalProdutos
      }
    };
  };

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const currentDate = isToday(dataSelecionada);
      setIsCurrentDate(currentDate);
      
      console.log(`📅 Loading stock data for ${dataSelecionada}`);
      console.log(`📋 Is current date: ${currentDate ? 'Yes' : 'No'}`);
      
      // Always load stock for the selected date
      await loadStockForDate(dataSelecionada);
      
      // Optionally load movement data for additional analysis
      await loadMovementDataForAnalysis(dataSelecionada);
      
    } catch (err) {
      console.error('❌ Error loading data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (newDate: string) => {
    setDataSelecionada(newDate);
  };

  useEffect(() => {
    loadData();
  }, [dataSelecionada]);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px',
        backgroundColor: '#f9fafb',
        borderRadius: '8px',
        fontSize: '1.1rem',
        color: '#6b7280'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', marginBottom: '16px' }}>🔄</div>
          <div>
            Carregando estoque para {formatDate(dataSelecionada)}...
          </div>
          <div style={{ fontSize: '0.875rem', marginTop: '8px', color: '#9ca3af' }}>
            Aplicando regras de negócio e documento_referencia
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '24px', 
        textAlign: 'center',
        backgroundColor: '#fef2f2',
        border: '1px solid #fecaca',
        borderRadius: '8px',
        color: '#b91c1c'
      }}>
        <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⚠️</div>
        <div style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '8px' }}>
          Erro ao carregar dados do estoque
        </div>
        <div style={{ fontSize: '0.875rem' }}>{error}</div>
        <button 
          onClick={loadData}
          style={{
            marginTop: '16px',
            padding: '8px 16px',
            backgroundColor: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ 
          fontSize: '2rem', 
          fontWeight: '700', 
          color: '#111827', 
          margin: '0 0 8px 0' 
        }}>
          📦 Dashboard de Controle de Estoque
        </h1>
        <p style={{ 
          fontSize: '1rem', 
          color: '#6b7280', 
          margin: 0 
        }}>
          Estoque atual e histórico com regras de negócio aplicadas
        </p>
      </div>

      {/* Business Rules Info */}
      <div style={{ 
        backgroundColor: '#eff6ff',
        border: '1px solid #bfdbfe',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '24px'
      }}>
        <h3 style={{ 
          fontSize: '1rem', 
          fontWeight: '600', 
          color: '#1e40af',
          marginBottom: '8px'
        }}>
          📋 Regras de Negócio
        </h3>
        <div style={{ fontSize: '0.875rem', color: '#1e40af', lineHeight: '1.5' }}>
          • <strong>Tabela de produtos:</strong> Mostra o estoque atual (hoje)<br/>
          • <strong>Cálculo histórico:</strong> Para datas anteriores, usa tabela de movimentações<br/>
          • <strong>documento_referencia = "000000":</strong> Define estoque absoluto, ignora movimentos posteriores<br/>
          • <strong>Backend inteligente:</strong> Escolhe automaticamente a fonte de dados correta
        </div>
      </div>

      {/* Date Filter and Data Source Info */}
      <div style={{ 
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        flexWrap: 'wrap',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ 
              fontSize: '0.875rem', 
              fontWeight: '600', 
              color: '#374151' 
            }}>
              📅 Data de consulta:
            </label>
            <input
              type="date"
              value={dataSelecionada}
              onChange={(e) => handleDateChange(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '0.875rem',
                color: '#374151',
                backgroundColor: 'white'
              }}
            />
          </div>
          <button
            onClick={loadData}
            style={{
              padding: '8px 16px',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            🔄 Atualizar
          </button>
        </div>
        
        {/* Data Source Indicator */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px',
          padding: '8px 12px',
          backgroundColor: estoqueData?.estatisticas?.total_produtos > 0 ? '#dcfce7' : '#fef2f2',
          border: `1px solid ${estoqueData?.estatisticas?.total_produtos > 0 ? '#bbf7d0' : '#fecaca'}`,
          borderRadius: '6px'
        }}>
          <span style={{ fontSize: '1rem' }}>
            {estoqueData?.estatisticas?.total_produtos > 0 ? '✅' : '📊'}
          </span>
          <span style={{ 
            fontSize: '0.875rem', 
            fontWeight: '500',
            color: estoqueData?.estatisticas?.total_produtos > 0 ? '#166534' : '#b91c1c'
          }}>
            {estoqueData?.estatisticas?.total_produtos > 0 
              ? `Dados encontrados para ${formatDate(dataSelecionada)}`
              : `Sem dados para ${formatDate(dataSelecionada)}`
            }
          </span>
        </div>
      </div>

      {/* Statistics Cards */}
      {estoqueData && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '16px',
          marginBottom: '32px'
        }}>
          <div style={{ 
            backgroundColor: 'white', 
            border: '1px solid #e5e7eb', 
            borderRadius: '8px', 
            padding: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>📦</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1e293b', marginBottom: '4px' }}>
              {formatNumber(estoqueData.estatisticas.total_produtos)}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#64748b' }}>
              Total de Produtos
            </div>
          </div>

          <div style={{ 
            backgroundColor: 'white', 
            border: '1px solid #bbf7d0', 
            borderRadius: '8px', 
            padding: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>✅</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#166534', marginBottom: '4px' }}>
              {formatNumber(estoqueData.estatisticas.produtos_com_estoque)}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#166534' }}>
              Com Estoque
            </div>
          </div>

          <div style={{ 
            backgroundColor: 'white', 
            border: '1px solid #fecaca', 
            borderRadius: '8px', 
            padding: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>❌</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#b91c1c', marginBottom: '4px' }}>
              {formatNumber(estoqueData.estatisticas.produtos_zerados)}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#b91c1c' }}>
              Zerados
            </div>
          </div>

          <div style={{ 
            backgroundColor: 'white', 
            border: '1px solid #bfdbfe', 
            borderRadius: '8px', 
            padding: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>💰</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1e40af', marginBottom: '4px' }}>
              {formatCurrency(estoqueData.estatisticas.valor_total_atual)}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#1e40af' }}>
              Valor Total
            </div>
          </div>
        </div>
      )}

      {/* Products Table */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        padding: '24px', 
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)' 
      }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
          📦 Produtos em Estoque - {formatDate(dataSelecionada)}
        </h2>

        {estoqueData && estoqueData.estoque.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ 
              width: '100%', 
              borderCollapse: 'collapse',
              fontSize: '0.875rem'
            }}>
              <thead>
                <tr style={{ backgroundColor: '#f8fafc' }}>
                  <th style={{ 
                    padding: '12px 8px', 
                    textAlign: 'left', 
                    borderBottom: '1px solid #e2e8f0',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    Produto
                  </th>
                  <th style={{ 
                    padding: '12px 8px', 
                    textAlign: 'right', 
                    borderBottom: '1px solid #e2e8f0',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    Qtd Atual
                  </th>
                  <th style={{ 
                    padding: '12px 8px', 
                    textAlign: 'right', 
                    borderBottom: '1px solid #e2e8f0',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    Valor Unit.
                  </th>
                  <th style={{ 
                    padding: '12px 8px', 
                    textAlign: 'right', 
                    borderBottom: '1px solid #e2e8f0',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    Valor Total
                  </th>
                  <th style={{ 
                    padding: '12px 8px', 
                    textAlign: 'center', 
                    borderBottom: '1px solid #e2e8f0',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    Movimentações
                  </th>
                </tr>
              </thead>
              <tbody>
                {estoqueData.estoque
                  .sort((a, b) => b.valor_atual - a.valor_atual)
                  .slice(0, 20)
                  .map((produto, index) => (
                  <tr key={produto.produto_id} style={{ 
                    borderBottom: '1px solid #f1f5f9',
                    backgroundColor: index % 2 === 0 ? 'white' : '#fafbfc'
                  }}>
                    <td style={{ padding: '12px 8px' }}>
                      <div style={{ fontWeight: '500', color: '#1e293b' }}>
                        {produto.nome}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        Ref: {produto.referencia}
                      </div>
                    </td>
                    <td style={{ 
                      padding: '12px 8px', 
                      textAlign: 'right',
                      color: produto.quantidade_atual > 0 ? '#166534' : '#b91c1c',
                      fontWeight: '500'
                    }}>
                      {formatNumber(produto.quantidade_atual)}
                    </td>
                    <td style={{ 
                      padding: '12px 8px', 
                      textAlign: 'right',
                      color: '#64748b'
                    }}>
                      {formatCurrency(produto.custo_unitario_inicial)}
                    </td>
                    <td style={{ 
                      padding: '12px 8px', 
                      textAlign: 'right',
                      fontWeight: '500',
                      color: '#1e293b'
                    }}>
                      {formatCurrency(produto.valor_atual)}
                    </td>
                    <td style={{ 
                      padding: '12px 8px', 
                      textAlign: 'center',
                      color: '#64748b'
                    }}>
                      {formatNumber(produto.total_movimentacoes)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {estoqueData.estoque.length > 20 && (
              <div style={{ 
                marginTop: '16px', 
                textAlign: 'center',
                fontSize: '0.875rem',
                color: '#64748b'
              }}>
                Mostrando 20 de {estoqueData.estoque.length} produtos
              </div>
            )}
          </div>
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '48px',
            color: '#64748b'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>📦</div>
            <div>Nenhum produto encontrado para esta data</div>
            <div style={{ fontSize: '0.875rem', marginTop: '8px' }}>
              Verifique se há dados de estoque para a data selecionada
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EstoqueDashboardCorrect;