// New EstoqueDashboard component using the stock service and hook
// This version provides better error handling and connection management

import React, { useState, useEffect } from 'react';
import { useStock } from '../../hooks/useStock';
import { formatCurrency } from '../../lib/utils';

const EstoqueDashboardNew: React.FC = () => {
  const [activeTab, setActiveTab] = useState('geral');
  const [dataSelecionada, setDataSelecionada] = useState<string>(
    new Date().toISOString().split('T')[0]
  );

  // Use the stock hook
  const {
    estoqueGeral,
    estoqueTop,
    estoqueCritico,
    produtosMovimentados,
    loading,
    error,
    errors,
    backendConnected,
    loadAllData,
    testConnection,
    clearErrors,
    totalProdutos,
    valorTotalEstoque,
    produtosComEstoque,
    produtosZerados,
  } = useStock({
    autoLoad: true,
    data: dataSelecionada
  });

  // Handle date change
  const handleDateChange = (newDate: string) => {
    setDataSelecionada(newDate);
    clearErrors();
    loadAllData(newDate);
  };

  // Format number helper
  const formatNumber = (value: number | undefined | null): string => {
    if (value === undefined || value === null || isNaN(value)) {
      return '0';
    }
    return value.toLocaleString('pt-BR');
  };

  // Format date helper
  const formatDate = (dateString: string): string => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('pt-BR');
    } catch {
      return 'N/A';
    }
  };

  const tabs = [
    { id: 'geral', label: '📦 Estoque Geral', icon: '📦' },
    { id: 'top-produtos', label: '💎 Top Produtos', icon: '💎' },
    { id: 'criticos', label: '⚠️ Produtos Críticos', icon: '⚠️' },
    { id: 'movimentados', label: '🔄 Mais Movimentados', icon: '🔄' },
  ];

  // Connection error component
  if (!backendConnected && !loading) {
    return (
      <div style={{ padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
        <div style={{ 
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          padding: '24px',
          textAlign: 'center',
          maxWidth: '600px',
          margin: '0 auto'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🚨</div>
          <h2 style={{ 
            fontSize: '1.5rem', 
            fontWeight: '600', 
            color: '#b91c1c', 
            marginBottom: '16px' 
          }}>
            Backend Não Conectado
          </h2>
          <p style={{ 
            fontSize: '1rem', 
            color: '#7f1d1d', 
            marginBottom: '24px',
            lineHeight: '1.5'
          }}>
            Não foi possível conectar ao backend do sistema de estoque.
            <br />
            Verifique se o servidor está rodando em <code>http://127.0.0.1:8000</code>
          </p>
          
          <div style={{ 
            backgroundColor: '#f3f4f6', 
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '16px',
            marginBottom: '24px',
            textAlign: 'left'
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '12px' }}>
              💡 Como resolver:
            </h3>
            <ol style={{ fontSize: '0.875rem', color: '#374151', paddingLeft: '20px' }}>
              <li style={{ marginBottom: '8px' }}>
                Abra o terminal na pasta do backend:
                <br />
                <code style={{ 
                  backgroundColor: '#1f2937', 
                  color: '#f9fafb', 
                  padding: '2px 6px', 
                  borderRadius: '3px',
                  fontSize: '0.8rem'
                }}>
                  cd C:\Users\Cirilo\Documents\kiro\empresa\backend
                </code>
              </li>
              <li style={{ marginBottom: '8px' }}>
                Execute o servidor Django:
                <br />
                <code style={{ 
                  backgroundColor: '#1f2937', 
                  color: '#f9fafb', 
                  padding: '2px 6px', 
                  borderRadius: '3px',
                  fontSize: '0.8rem'
                }}>
                  python manage.py runserver
                </code>
              </li>
              <li>
                Verifique se o módulo de estoque está configurado no backend
              </li>
            </ol>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button
              onClick={testConnection}
              style={{
                padding: '10px 20px',
                backgroundColor: '#dc2626',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              🔄 Testar Conexão
            </button>
          </div>

          {error && (
            <div style={{ 
              marginTop: '16px',
              padding: '12px',
              backgroundColor: '#fee2e2',
              border: '1px solid #fecaca',
              borderRadius: '4px',
              fontSize: '0.875rem',
              color: '#991b1b'
            }}>
              <strong>Erro:</strong> {error}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Loading state
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
          <div>Carregando dados do estoque...</div>
          {backendConnected && (
            <div style={{ fontSize: '0.875rem', marginTop: '8px', color: '#10b981' }}>
              ✅ Backend conectado
            </div>
          )}
        </div>
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
          Análise completa do estoque, produtos críticos e movimentações
        </p>
      </div>

      {/* Connection Status */}
      <div style={{ 
        backgroundColor: backendConnected ? '#dcfce7' : '#fef2f2',
        border: `1px solid ${backendConnected ? '#bbf7d0' : '#fecaca'}`,
        borderRadius: '6px',
        padding: '12px 16px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span style={{ fontSize: '1.2rem' }}>
          {backendConnected ? '✅' : '❌'}
        </span>
        <span style={{ 
          fontSize: '0.875rem', 
          fontWeight: '500',
          color: backendConnected ? '#166534' : '#b91c1c'
        }}>
          {backendConnected ? 'Backend Conectado' : 'Backend Desconectado'}
        </span>
        {!backendConnected && (
          <button
            onClick={testConnection}
            style={{
              marginLeft: 'auto',
              padding: '4px 8px',
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '0.75rem',
              cursor: 'pointer'
            }}
          >
            Reconectar
          </button>
        )}
      </div>

      {/* Date Filter and Summary */}
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
            onClick={() => loadAllData(dataSelecionada)}
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
        
        {/* Summary Cards */}
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ 
            backgroundColor: '#dcfce7', 
            border: '1px solid #bbf7d0', 
            borderRadius: '6px', 
            padding: '8px 12px' 
          }}>
            <div style={{ fontSize: '0.75rem', color: '#166534', fontWeight: '500' }}>
              💰 Valor Total
            </div>
            <div style={{ fontSize: '1rem', fontWeight: '700', color: '#166534' }}>
              {formatCurrency(valorTotalEstoque)}
            </div>
          </div>
          <div style={{ 
            backgroundColor: '#dbeafe', 
            border: '1px solid #bfdbfe', 
            borderRadius: '6px', 
            padding: '8px 12px' 
          }}>
            <div style={{ fontSize: '0.75rem', color: '#1e40af', fontWeight: '500' }}>
              📦 Total Produtos
            </div>
            <div style={{ fontSize: '1rem', fontWeight: '700', color: '#1e40af' }}>
              {formatNumber(totalProdutos)}
            </div>
          </div>
          <div style={{ 
            backgroundColor: '#fef3c7', 
            border: '1px solid #fde68a', 
            borderRadius: '6px', 
            padding: '8px 12px' 
          }}>
            <div style={{ fontSize: '0.75rem', color: '#92400e', fontWeight: '500' }}>
              ⚠️ Zerados
            </div>
            <div style={{ fontSize: '1rem', fontWeight: '700', color: '#92400e' }}>
              {formatNumber(produtosZerados)}
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {(error || Object.values(errors).some(e => e)) && (
        <div style={{ 
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px'
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#b91c1c', marginBottom: '8px' }}>
            ⚠️ Erros encontrados:
          </h3>
          {error && (
            <div style={{ fontSize: '0.875rem', color: '#7f1d1d', marginBottom: '4px' }}>
              • Geral: {error}
            </div>
          )}
          {Object.entries(errors).map(([key, err]) => err && (
            <div key={key} style={{ fontSize: '0.875rem', color: '#7f1d1d', marginBottom: '4px' }}>
              • {key}: {err}
            </div>
          ))}
          <button
            onClick={clearErrors}
            style={{
              marginTop: '8px',
              padding: '4px 8px',
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '0.75rem',
              cursor: 'pointer'
            }}
          >
            Limpar Erros
          </button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div style={{ 
        display: 'flex', 
        gap: '8px', 
        marginBottom: '24px',
        flexWrap: 'wrap'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '12px 16px',
              backgroundColor: activeTab === tab.id ? '#2563eb' : 'white',
              color: activeTab === tab.id ? 'white' : '#374151',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        padding: '24px', 
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)' 
      }}>
        
        {/* Estoque Geral Tab */}
        {activeTab === 'geral' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              📦 Estoque Geral
            </h2>
            
            {estoqueGeral ? (
              <div>
                {/* Statistics */}
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                  gap: '16px',
                  marginBottom: '24px'
                }}>
                  <div style={{ 
                    backgroundColor: '#f8fafc', 
                    border: '1px solid #e2e8f0', 
                    borderRadius: '8px', 
                    padding: '16px' 
                  }}>
                    <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '4px' }}>
                      Total de Produtos
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1e293b' }}>
                      {formatNumber(estoqueGeral.estatisticas.total_produtos)}
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: '#f0fdf4', 
                    border: '1px solid #bbf7d0', 
                    borderRadius: '8px', 
                    padding: '16px' 
                  }}>
                    <div style={{ fontSize: '0.875rem', color: '#166534', marginBottom: '4px' }}>
                      Com Estoque
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#166534' }}>
                      {formatNumber(estoqueGeral.estatisticas.produtos_com_estoque)}
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: '#fef2f2', 
                    border: '1px solid #fecaca', 
                    borderRadius: '8px', 
                    padding: '16px' 
                  }}>
                    <div style={{ fontSize: '0.875rem', color: '#b91c1c', marginBottom: '4px' }}>
                      Zerados
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#b91c1c' }}>
                      {formatNumber(estoqueGeral.estatisticas.produtos_zerados)}
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: '#eff6ff', 
                    border: '1px solid #bfdbfe', 
                    borderRadius: '8px', 
                    padding: '16px' 
                  }}>
                    <div style={{ fontSize: '0.875rem', color: '#1e40af', marginBottom: '4px' }}>
                      Valor Total
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1e40af' }}>
                      {formatCurrency(estoqueGeral.estatisticas.valor_total_atual)}
                    </div>
                  </div>
                </div>

                {/* Products Table */}
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
                          Valor Atual
                        </th>
                        <th style={{ 
                          padding: '12px 8px', 
                          textAlign: 'right', 
                          borderBottom: '1px solid #e2e8f0',
                          fontWeight: '600',
                          color: '#374151'
                        }}>
                          Movimentações
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {estoqueGeral.estoque.slice(0, 10).map((produto, index) => (
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
                            fontWeight: '500',
                            color: '#1e293b'
                          }}>
                            {formatCurrency(produto.valor_atual)}
                          </td>
                          <td style={{ 
                            padding: '12px 8px', 
                            textAlign: 'right',
                            color: '#64748b'
                          }}>
                            {formatNumber(produto.total_movimentacoes)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {estoqueGeral.estoque.length > 10 && (
                  <div style={{ 
                    marginTop: '16px', 
                    textAlign: 'center',
                    fontSize: '0.875rem',
                    color: '#64748b'
                  }}>
                    Mostrando 10 de {estoqueGeral.estoque.length} produtos
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
                <div>Nenhum dado de estoque encontrado</div>
              </div>
            )}
          </div>
        )}

        {/* Top Produtos Tab */}
        {activeTab === 'top-produtos' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              💎 Top Produtos por Valor
            </h2>
            
            {estoqueTop && estoqueTop.estoque.length > 0 ? (
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
                        Ranking
                      </th>
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
                        Valor Total
                      </th>
                      <th style={{ 
                        padding: '12px 8px', 
                        textAlign: 'right', 
                        borderBottom: '1px solid #e2e8f0',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        Quantidade
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {estoqueTop.estoque.slice(0, 20).map((produto, index) => (
                      <tr key={produto.produto_id} style={{ 
                        borderBottom: '1px solid #f1f5f9',
                        backgroundColor: index % 2 === 0 ? 'white' : '#fafbfc'
                      }}>
                        <td style={{ padding: '12px 8px', textAlign: 'center' }}>
                          <div style={{ 
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            backgroundColor: index < 3 ? '#fbbf24' : '#e5e7eb',
                            color: index < 3 ? 'white' : '#6b7280',
                            fontSize: '0.75rem',
                            fontWeight: '600'
                          }}>
                            {index + 1}
                          </div>
                        </td>
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
                          fontWeight: '600',
                          color: '#166534'
                        }}>
                          {formatCurrency(produto.valor_atual)}
                        </td>
                        <td style={{ 
                          padding: '12px 8px', 
                          textAlign: 'right',
                          color: '#64748b'
                        }}>
                          {formatNumber(produto.quantidade_atual)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '48px',
                color: '#64748b'
              }}>
                <div style={{ fontSize: '2rem', marginBottom: '16px' }}>💎</div>
                <div>Nenhum produto encontrado</div>
              </div>
            )}
          </div>
        )}

        {/* Produtos Críticos Tab */}
        {activeTab === 'criticos' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              ⚠️ Produtos Críticos
            </h2>
            
            {estoqueCritico && estoqueCritico.produtos.length > 0 ? (
              <div>
                <div style={{ 
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '8px',
                  padding: '16px',
                  marginBottom: '24px'
                }}>
                  <div style={{ fontSize: '0.875rem', color: '#b91c1c' }}>
                    <strong>⚠️ Atenção:</strong> {estoqueCritico.produtos.length} produtos com estoque crítico encontrados
                  </div>
                </div>

                <div style={{ overflowX: 'auto' }}>
                  <table style={{ 
                    width: '100%', 
                    borderCollapse: 'collapse',
                    fontSize: '0.875rem'
                  }}>
                    <thead>
                      <tr style={{ backgroundColor: '#fef2f2' }}>
                        <th style={{ 
                          padding: '12px 8px', 
                          textAlign: 'left', 
                          borderBottom: '1px solid #fecaca',
                          fontWeight: '600',
                          color: '#b91c1c'
                        }}>
                          Produto
                        </th>
                        <th style={{ 
                          padding: '12px 8px', 
                          textAlign: 'right', 
                          borderBottom: '1px solid #fecaca',
                          fontWeight: '600',
                          color: '#b91c1c'
                        }}>
                          Qtd Atual
                        </th>
                        <th style={{ 
                          padding: '12px 8px', 
                          textAlign: 'right', 
                          borderBottom: '1px solid #fecaca',
                          fontWeight: '600',
                          color: '#b91c1c'
                        }}>
                          Valor
                        </th>
                        <th style={{ 
                          padding: '12px 8px', 
                          textAlign: 'right', 
                          borderBottom: '1px solid #fecaca',
                          fontWeight: '600',
                          color: '#b91c1c'
                        }}>
                          Movimentações
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {estoqueCritico.produtos.map((produto, index) => (
                        <tr key={produto.produto_id} style={{ 
                          borderBottom: '1px solid #fee2e2',
                          backgroundColor: index % 2 === 0 ? '#fef2f2' : '#fef7f7'
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
                            color: '#b91c1c',
                            fontWeight: '600'
                          }}>
                            {formatNumber(produto.quantidade_atual)}
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
                            textAlign: 'right',
                            color: '#64748b'
                          }}>
                            {formatNumber(produto.total_movimentacoes)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '48px',
                color: '#64748b'
              }}>
                <div style={{ fontSize: '2rem', marginBottom: '16px' }}>✅</div>
                <div>Nenhum produto crítico encontrado</div>
                <div style={{ fontSize: '0.875rem', marginTop: '8px' }}>
                  Todos os produtos estão com estoque adequado
                </div>
              </div>
            )}
          </div>
        )}

        {/* Produtos Mais Movimentados Tab */}
        {activeTab === 'movimentados' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              🔄 Produtos Mais Movimentados
            </h2>
            
            {produtosMovimentados && produtosMovimentados.produtos_mais_movimentados.length > 0 ? (
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
                        Total Movimentações
                      </th>
                      <th style={{ 
                        padding: '12px 8px', 
                        textAlign: 'left', 
                        borderBottom: '1px solid #e2e8f0',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        Tipos
                      </th>
                      <th style={{ 
                        padding: '12px 8px', 
                        textAlign: 'left', 
                        borderBottom: '1px solid #e2e8f0',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        Última Movimentação
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {produtosMovimentados.produtos_mais_movimentados.map((produto, index) => (
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
                          fontWeight: '600',
                          color: '#2563eb'
                        }}>
                          {formatNumber(produto.total_movimentacoes)}
                        </td>
                        <td style={{ padding: '12px 8px' }}>
                          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                            {produto.tipos_movimentacao.map((tipo, i) => (
                              <span key={i} style={{
                                fontSize: '0.75rem',
                                padding: '2px 6px',
                                backgroundColor: '#e0e7ff',
                                color: '#3730a3',
                                borderRadius: '4px'
                              }}>
                                {tipo}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td style={{ 
                          padding: '12px 8px',
                          color: '#64748b'
                        }}>
                          {formatDate(produto.ultima_movimentacao)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '48px',
                color: '#64748b'
              }}>
                <div style={{ fontSize: '2rem', marginBottom: '16px' }}>🔄</div>
                <div>Nenhuma movimentação encontrada</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EstoqueDashboardNew;