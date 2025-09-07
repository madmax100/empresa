import React, { useState } from 'react';
import { contratosService, type ContratoFinanceiro, type ItemContrato } from '../services/contratosService';

// Interfaces para o relatório financeiro consolidado
interface ClienteConsolidado {
  id: number;
  nome: string;
  totalRecebido: number;
  totalGasto: number;
  margem: number;
  contratos: ContratoFinanceiro[];
}

// Função para consolidar dados por cliente
const consolidarDadosPorCliente = (dadosFinanceiros: ContratoFinanceiro[]): ClienteConsolidado[] => {
  const clientesMap = new Map<number, ClienteConsolidado>();
  
  dadosFinanceiros.forEach(item => {
    const clienteId = item.contrato.cliente.id;
    const clienteNome = item.contrato.cliente.nome;
    
    if (!clientesMap.has(clienteId)) {
      clientesMap.set(clienteId, {
        id: clienteId,
        nome: clienteNome,
        totalRecebido: 0,
        totalGasto: 0,
        margem: 0,
        contratos: []
      });
    }
    
    const cliente = clientesMap.get(clienteId)!;
    cliente.totalRecebido += item.total_recebido;
    cliente.totalGasto += item.total_gasto;
    cliente.contratos.push(item);
  });
  
  // Calcular margem final para cada cliente
  Array.from(clientesMap.values()).forEach(cliente => {
    cliente.margem = cliente.totalRecebido > 0 
      ? ((cliente.totalRecebido - cliente.totalGasto) / cliente.totalRecebido) * 100 
      : 0;
  });
  
  return Array.from(clientesMap.values());
};

export const ContratosPage: React.FC = () => {
  const [dataInicio, setDataInicio] = useState<string>('');
  const [dataFim, setDataFim] = useState<string>('');
  const [clientes, setClientes] = useState<ClienteConsolidado[]>([]);
  const [clienteExpandido, setClienteExpandido] = useState<number | null>(null);
  const [itensContratos, setItensContratos] = useState<{[key: number]: ItemContrato[]}>({});
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState<boolean>(false);

  // Carregar itens do contrato quando expandido
  const carregarItensContrato = async (contratoId: string) => {
    const id = parseInt(contratoId);
    if (itensContratos[id]) return; // Já carregado
    
    try {
      const itens = await contratosService.buscarItensContrato(contratoId);
      setItensContratos(prev => ({
        ...prev,
        [id]: itens
      }));
    } catch (error) {
      console.error('Erro ao carregar itens do contrato:', error);
    }
  };

  // Carregar dados da API
  const carregarDados = async () => {
    if (!dataInicio || !dataFim) {
      setErro('Por favor, selecione o período para consulta.');
      return;
    }

    setCarregando(true);
    setErro(null);
    
    try {
      const dadosFinanceiros = await contratosService.buscarDadosFinanceiros(
        dataInicio,
        dataFim
      );
      
      const clientesConsolidados = consolidarDadosPorCliente(dadosFinanceiros);
      setClientes(clientesConsolidados);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setErro('Erro ao carregar dados financeiros. Verifique sua conexão e tente novamente.');
    } finally {
      setCarregando(false);
    }
  };
  
  // Calcular totais gerais
  const totalRecebidoGeral = clientes.reduce((sum: number, cliente: ClienteConsolidado) => sum + cliente.totalRecebido, 0);
  const totalGastoGeral = clientes.reduce((sum: number, cliente: ClienteConsolidado) => sum + cliente.totalGasto, 0);
  const margemGeral = totalRecebidoGeral > 0 ? ((totalRecebidoGeral - totalGastoGeral) / totalRecebidoGeral) * 100 : 0;

  const formatarMoeda = (valor: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const formatarData = (data: string): string => {
    return new Date(data).toLocaleDateString('pt-BR');
  };

  const obterCorMargem = (margem: number): string => {
    if (margem >= 30) return '#10b981'; // Verde
    if (margem >= 15) return '#f59e0b'; // Amarelo
    return '#ef4444'; // Vermelho
  };

  const obterPercentualMargem = (margem: number): string => {
    return `${margem.toFixed(2)}%`;
  };

  const toggleClienteExpandido = (clienteId: number) => {
    const novoEstado = clienteExpandido === clienteId ? null : clienteId;
    setClienteExpandido(novoEstado);
    
    // Carregar itens dos contratos quando expandir
    if (novoEstado !== null) {
      const cliente = clientes.find(c => c.id === clienteId);
      if (cliente) {
        cliente.contratos.forEach(contrato => {
          carregarItensContrato(contrato.contrato.id.toString());
        });
      }
    }
  };

  return (
    <div style={{
      padding: '24px',
      backgroundColor: '#f8fafc',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '32px'
      }}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: 'bold',
          color: '#1f2937',
          margin: '0 0 8px 0'
        }}>
          📊 Relatório Financeiro de Contratos
        </h1>
        <p style={{
          color: '#6b7280',
          margin: '0'
        }}>
          Análise de receitas, custos e margens por cliente
        </p>
      </div>

      {/* Filtros de Data */}
      <div style={{
        backgroundColor: 'white',
        padding: '24px',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        marginBottom: '24px'
      }}>
        <h2 style={{
          fontSize: '1.25rem',
          fontWeight: '600',
          color: '#374151',
          marginBottom: '16px'
        }}>
          📅 Período de Análise
        </h2>
        
        <div style={{
          display: 'flex',
          gap: '16px',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          <div>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>
              Data Início:
            </label>
            <input
              type="date"
              value={dataInicio}
              onChange={(e) => setDataInicio(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '0.875rem'
              }}
            />
          </div>
          
          <div>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>
              Data Fim:
            </label>
            <input
              type="date"
              value={dataFim}
              onChange={(e) => setDataFim(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '0.875rem'
              }}
            />
          </div>
          
          <button
            onClick={carregarDados}
            disabled={carregando || !dataInicio || !dataFim}
            style={{
              padding: '8px 16px',
              backgroundColor: carregando ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: carregando ? 'not-allowed' : 'pointer',
              marginTop: '20px'
            }}
          >
            {carregando ? '🔄 Carregando...' : '🔍 Buscar Dados'}
          </button>
        </div>
        
        {/* Exibir erros */}
        {erro && (
          <div style={{
            marginTop: '16px',
            padding: '12px',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            color: '#dc2626',
            fontSize: '0.875rem'
          }}>
            ⚠️ {erro}
          </div>
        )}
      </div>

      {/* Totais Gerais */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          borderLeft: '4px solid #10b981'
        }}>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#6b7280',
            marginBottom: '4px'
          }}>
            💰 Total Recebido
          </div>
          <div style={{
            fontSize: '1.875rem',
            fontWeight: 'bold',
            color: '#10b981'
          }}>
            {formatarMoeda(totalRecebidoGeral)}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          borderLeft: '4px solid #ef4444'
        }}>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#6b7280',
            marginBottom: '4px'
          }}>
            💸 Total Gasto
          </div>
          <div style={{
            fontSize: '1.875rem',
            fontWeight: 'bold',
            color: '#ef4444'
          }}>
            {formatarMoeda(totalGastoGeral)}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          borderLeft: `4px solid ${obterCorMargem(margemGeral)}`
        }}>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#6b7280',
            marginBottom: '4px'
          }}>
            📈 Margem Geral
          </div>
          <div style={{
            fontSize: '1.875rem',
            fontWeight: 'bold',
            color: obterCorMargem(margemGeral)
          }}>
            {obterPercentualMargem(margemGeral)}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          borderLeft: '4px solid #8b5cf6'
        }}>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#6b7280',
            marginBottom: '4px'
          }}>
            🏢 Total Clientes
          </div>
          <div style={{
            fontSize: '1.875rem',
            fontWeight: 'bold',
            color: '#8b5cf6'
          }}>
            {clientes.length}
          </div>
        </div>
      </div>

      {/* Tabela de Clientes */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #e5e7eb'
        }}>
          <h2 style={{
            fontSize: '1.25rem',
            fontWeight: '600',
            color: '#374151',
            margin: '0'
          }}>
            👤 Clientes e Contratos
          </h2>
        </div>

        {clientes.length === 0 ? (
          <div style={{
            padding: '60px 20px',
            textAlign: 'center' as const,
            color: '#6b7280'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📋</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
              Nenhum dado encontrado
            </h3>
            <p style={{ fontSize: '0.875rem' }}>
              {dataInicio && dataFim 
                ? 'Não foram encontrados contratos para o período selecionado.'
                : 'Selecione um período e clique em "Buscar Dados" para visualizar o relatório.'
              }
            </p>
          </div>
        ) : (
          <div style={{
            overflowX: 'auto'
          }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse'
            }}>
              <thead style={{
                backgroundColor: '#f9fafb'
              }}>
                <tr>
                  <th style={{
                    padding: '12px 16px',
                    textAlign: 'left',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    color: '#374151',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    Cliente
                  </th>
                  <th style={{
                    padding: '12px 16px',
                    textAlign: 'right',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    color: '#374151',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    Total Recebido
                  </th>
                  <th style={{
                    padding: '12px 16px',
                    textAlign: 'right',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    color: '#374151',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    Total Gasto
                  </th>
                  <th style={{
                    padding: '12px 16px',
                    textAlign: 'right',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    color: '#374151',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    Margem
                  </th>
                  <th style={{
                    padding: '12px 16px',
                    textAlign: 'center',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    color: '#374151',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody>
                {clientes.map((cliente) => (
                  <React.Fragment key={cliente.id}>
                    <tr style={{
                      borderBottom: '1px solid #e5e7eb'
                    }}>
                      <td style={{
                        padding: '16px',
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        color: '#1f2937'
                      }}>
                        {cliente.nome}
                      </td>
                      <td style={{
                        padding: '16px',
                        textAlign: 'right',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        color: '#10b981'
                      }}>
                        {formatarMoeda(cliente.totalRecebido)}
                      </td>
                      <td style={{
                        padding: '16px',
                        textAlign: 'right',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        color: '#ef4444'
                      }}>
                        {formatarMoeda(cliente.totalGasto)}
                      </td>
                      <td style={{
                        padding: '16px',
                        textAlign: 'right',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        color: obterCorMargem(cliente.margem)
                      }}>
                        {obterPercentualMargem(cliente.margem)}
                      </td>
                      <td style={{
                        padding: '16px',
                        textAlign: 'center'
                      }}>
                        <button
                          onClick={() => toggleClienteExpandido(cliente.id)}
                          style={{
                            padding: '6px 12px',
                            backgroundColor: clienteExpandido === cliente.id ? '#ef4444' : '#3b82f6',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '500',
                            cursor: 'pointer'
                          }}
                        >
                          {clienteExpandido === cliente.id ? '👆 Recolher' : '👇 Expandir'}
                        </button>
                      </td>
                    </tr>
                    
                    {clienteExpandido === cliente.id && (
                      <tr>
                        <td colSpan={5} style={{
                          padding: '0',
                          backgroundColor: '#f9fafb',
                          borderBottom: '1px solid #e5e7eb'
                        }}>
                          <div style={{
                            padding: '24px'
                          }}>
                            <h3 style={{
                              fontSize: '1rem',
                              fontWeight: '600',
                              color: '#374151',
                              marginBottom: '16px'
                            }}>
                              🛒 Produtos/Equipamentos Fornecidos
                            </h3>

                            <div style={{
                              display: 'grid',
                              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                              gap: '12px'
                            }}>
                              {cliente.contratos.flatMap(contrato => {
                                const contratoId = contrato.contrato.id;
                                const itens = itensContratos[contratoId] || [];
                                
                                return itens.map(item => (
                                  <div
                                    key={`${contratoId}-${item.id}`}
                                    style={{
                                      padding: '16px',
                                      backgroundColor: '#f9fafb',
                                      borderRadius: '8px',
                                      border: '1px solid #e5e7eb'
                                    }}
                                  >
                                    <div style={{
                                      fontSize: '0.875rem',
                                      fontWeight: '600',
                                      color: '#111827',
                                      marginBottom: '8px'
                                    }}>
                                      {item.modelo}
                                    </div>
                                    
                                    <div style={{
                                      fontSize: '0.75rem',
                                      color: '#6b7280',
                                      marginBottom: '8px'
                                    }}>
                                      Categoria: {item.categoria.nome} | Série: {item.numeroserie}
                                    </div>
                                    
                                    <div style={{
                                      display: 'flex',
                                      justifyContent: 'space-between',
                                      fontSize: '0.75rem',
                                      color: '#374151',
                                      marginBottom: '4px'
                                    }}>
                                      <span>Quantidade:</span>
                                      <span style={{ fontWeight: '600' }}>{item.quantidade || 1}</span>
                                    </div>
                                    
                                    <div style={{
                                      display: 'flex',
                                      justifyContent: 'space-between',
                                      fontSize: '0.75rem',
                                      color: '#374151',
                                      marginBottom: '4px'
                                    }}>
                                      <span>Custo Unit.:</span>
                                      <span style={{ fontWeight: '600' }}>{formatarMoeda(item.custo_unitario || 0)}</span>
                                    </div>
                                    
                                    <div style={{
                                      display: 'flex',
                                      justifyContent: 'space-between',
                                      fontSize: '0.75rem',
                                      color: '#111827',
                                      fontWeight: '600',
                                      borderTop: '1px solid #d1d5db',
                                      paddingTop: '8px',
                                      marginTop: '8px'
                                    }}>
                                      <span>Total:</span>
                                      <span style={{ color: '#ef4444' }}>{formatarMoeda(item.custo_total || 0)}</span>
                                    </div>
                                    
                                    <div style={{
                                      fontSize: '0.7rem',
                                      color: '#9ca3af',
                                      marginTop: '8px'
                                    }}>
                                      Período: {formatarData(item.inicio)} - {formatarData(item.fim)}
                                    </div>
                                  </div>
                                ));
                              })}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContratosPage;
