import React, { useState } from 'react';
import type { ContratoLocacao, ItemContratoLocacao } from '../types/contratos';
import { useContratos } from '../hooks/useContratosFixed';

interface TabelaContratosProps {
  contratos: ContratoLocacao[];
  loading?: boolean;
  onContratoSelect?: (contrato: ContratoLocacao) => void;
}

// Estilos inline seguindo o padrão do EstoqueDashboard
const styles = {
  container: {
    backgroundColor: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    overflow: 'hidden'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const
  },
  thead: {
    backgroundColor: '#f9fafb'
  },
  th: {
    padding: '12px',
    textAlign: 'left' as const,
    fontWeight: '600',
    color: '#374151',
    fontSize: '0.875rem',
    borderBottom: '1px solid #e5e7eb'
  },
  thCenter: {
    padding: '12px',
    textAlign: 'center' as const,
    fontWeight: '600',
    color: '#374151',
    fontSize: '0.875rem',
    borderBottom: '1px solid #e5e7eb'
  },
  thRight: {
    padding: '12px',
    textAlign: 'right' as const,
    fontWeight: '600',
    color: '#374151',
    fontSize: '0.875rem',
    borderBottom: '1px solid #e5e7eb'
  },
  tr: {
    borderBottom: '1px solid #e5e7eb'
  },
  trEven: {
    backgroundColor: '#f9fafb'
  },
  trOdd: {
    backgroundColor: 'white'
  },
  td: {
    padding: '12px',
    color: '#374151',
    fontSize: '0.875rem'
  },
  tdCenter: {
    padding: '12px',
    textAlign: 'center' as const,
    color: '#374151',
    fontSize: '0.875rem'
  },
  tdRight: {
    padding: '12px',
    textAlign: 'right' as const,
    color: '#374151',
    fontSize: '0.875rem'
  },
  badge: {
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '0.7rem',
    fontWeight: '500'
  },
  badgeAtivo: {
    backgroundColor: '#dcfce7',
    color: '#166534'
  },
  badgeInativo: {
    backgroundColor: '#fee2e2',
    color: '#991b1b'
  },
  badgeExpirando: {
    backgroundColor: '#fef3c7',
    color: '#d97706'
  },
  badgeRenovado: {
    backgroundColor: '#dbeafe',
    color: '#1e40af'
  },
  badgeNaoRenovado: {
    backgroundColor: '#f3f4f6',
    color: '#64748b'
  },
  button: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '0.875rem',
    color: '#3b82f6',
    fontWeight: '500',
    padding: '4px 8px',
    borderRadius: '4px',
    transition: 'color 0.15s ease-in-out'
  },
  buttonSuccess: {
    color: '#059669'
  },
  loading: {
    backgroundColor: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '48px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  spinner: {
    width: '32px',
    height: '32px',
    border: '2px solid #e5e7eb',
    borderTop: '2px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },
  emptyState: {
    backgroundColor: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '48px',
    textAlign: 'center' as const,
    color: '#6b7280'
  },
  expandedRow: {
    backgroundColor: '#f8fafc',
    borderBottom: '1px solid #e5e7eb'
  },
  expandedContent: {
    backgroundColor: 'white',
    borderRadius: '6px',
    border: '1px solid #e5e7eb',
    overflow: 'hidden'
  },
  expandedHeader: {
    backgroundColor: '#f1f5f9',
    padding: '12px 16px',
    borderBottom: '1px solid #e5e7eb',
    fontWeight: '600',
    fontSize: '0.875rem',
    color: '#334155'
  },
  itemsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '12px',
    padding: '12px'
  },
  itemCard: {
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    padding: '12px',
    backgroundColor: '#f8fafc'
  }
};

export const TabelaContratos: React.FC<TabelaContratosProps> = ({ 
  contratos, 
  loading = false,
  onContratoSelect 
}) => {
  const [contratoExpandido, setContratoExpandido] = useState<number | null>(null);
  const [itensContrato, setItensContrato] = useState<{ [key: number]: ItemContratoLocacao[] }>({});
  const [loadingItens, setLoadingItens] = useState<{ [key: number]: boolean }>({});
  const { fetchItensContrato } = useContratos();

  const formatarValor = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor);
  };

  const formatarData = (data: string) => {
    return new Date(data).toLocaleDateString('pt-BR');
  };

  const obterStatusContrato = (dataFim: string) => {
    const hoje = new Date();
    const fim = new Date(dataFim);
    
    if (fim < hoje) {
      return { status: 'Inativo', classe: 'bg-red-100 text-red-800' };
    } else {
      const diasRestantes = Math.ceil((fim.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24));
      if (diasRestantes <= 30) {
        return { status: 'Expirando', classe: 'bg-yellow-100 text-yellow-800' };
      }
      return { status: 'Ativo', classe: 'bg-green-100 text-green-800' };
    }
  };

  const toggleExpandirContrato = async (contratoId: number) => {
    if (contratoExpandido === contratoId) {
      setContratoExpandido(null);
      return;
    }

    setContratoExpandido(contratoId);
    
    // Buscar itens se ainda não foram carregados
    if (!itensContrato[contratoId]) {
      setLoadingItens(prev => ({ ...prev, [contratoId]: true }));
      
      try {
        const itens = await fetchItensContrato(contratoId);
        setItensContrato(prev => ({ ...prev, [contratoId]: itens }));
      } catch (error) {
        console.error('Erro ao buscar itens do contrato:', error);
        setItensContrato(prev => ({ ...prev, [contratoId]: [] }));
      } finally {
        setLoadingItens(prev => ({ ...prev, [contratoId]: false }));
      }
    }
  };

  if (loading) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <span style={{ marginLeft: '8px', color: '#6b7280' }}>Carregando contratos...</span>
      </div>
    );
  }

  if (contratos.length === 0) {
    return (
      <div style={styles.emptyState}>
        <div style={{ color: '#6b7280' }}>
          <p style={{ fontSize: '1.125rem', margin: '0 0 4px 0' }}>Nenhum contrato encontrado</p>
          <p style={{ fontSize: '0.875rem', margin: 0 }}>Tente ajustar os filtros para ver mais resultados</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <table style={styles.table}>
        <thead style={styles.thead}>
          <tr>
            <th style={styles.th}>
              Contrato
            </th>
            <th style={styles.th}>
              Cliente
            </th>
            <th style={styles.thRight}>
              Valor
            </th>
            <th style={styles.thCenter}>
              Parcelas
            </th>
            <th style={styles.thCenter}>
              Período
            </th>
            <th style={styles.thCenter}>
              Status
            </th>
            <th style={styles.thCenter}>
              Renovado
            </th>
            <th style={styles.thCenter}>
              Ações
            </th>
          </tr>
        </thead>
        <tbody>
            {contratos.map((contrato, index) => {
              const { status } = obterStatusContrato(contrato.fim);
              const isExpandido = contratoExpandido === contrato.id;
              
              return (
                <React.Fragment key={contrato.id}>
                  <tr 
                    style={{
                      ...styles.tr,
                      ...(index % 2 === 0 ? styles.trOdd : styles.trEven)
                    }}
                  >
                    <td style={styles.td}>
                      <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>
                        {contrato.contrato}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                        Tipo: {contrato.tipocontrato}
                      </div>
                    </td>
                    <td style={styles.td}>
                      <div 
                        style={{ 
                          fontSize: '0.875rem', 
                          color: '#111827', 
                          fontWeight: '500',
                          maxWidth: '200px', 
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }} 
                        title={contrato.cliente.nome}
                      >
                        {contrato.cliente.nome}
                      </div>
                    </td>
                    <td style={styles.tdRight}>
                      <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>
                        {formatarValor(contrato.valorcontrato)}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                        {formatarValor(contrato.valorpacela)}/mês
                      </div>
                    </td>
                    <td style={{ ...styles.tdCenter, fontWeight: '500' }}>
                      {contrato.numeroparcelas}x
                    </td>
                    <td style={styles.tdCenter}>
                      <div style={{ fontSize: '0.875rem', color: '#111827' }}>
                        {formatarData(contrato.inicio)}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                        até {formatarData(contrato.fim)}
                      </div>
                    </td>
                    <td style={styles.tdCenter}>
                      <span style={{
                        ...styles.badge,
                        ...(status === 'Ativo' ? styles.badgeAtivo : 
                            status === 'Inativo' ? styles.badgeInativo : 
                            styles.badgeExpirando)
                      }}>
                        {status}
                      </span>
                    </td>
                    <td style={styles.tdCenter}>
                      <span style={{
                        ...styles.badge,
                        ...(contrato.renovado === 'SIM' ? styles.badgeRenovado : styles.badgeNaoRenovado)
                      }}>
                        {contrato.renovado}
                      </span>
                    </td>
                    <td style={styles.tdCenter}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                        <button
                          onClick={() => toggleExpandirContrato(contrato.id)}
                          style={styles.button}
                          onMouseEnter={(e) => {
                            (e.target as HTMLButtonElement).style.color = '#1e40af';
                          }}
                          onMouseLeave={(e) => {
                            (e.target as HTMLButtonElement).style.color = '#3b82f6';
                          }}
                        >
                          {isExpandido ? 'Fechar' : 'Ver Itens'}
                        </button>
                        {onContratoSelect && (
                          <button
                            onClick={() => onContratoSelect(contrato)}
                            style={{
                              ...styles.button,
                              ...styles.buttonSuccess
                            }}
                            onMouseEnter={(e) => {
                              (e.target as HTMLButtonElement).style.color = '#047857';
                            }}
                            onMouseLeave={(e) => {
                              (e.target as HTMLButtonElement).style.color = '#059669';
                            }}
                          >
                            Detalhes
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                  
                  {/* Linha expandida com itens do contrato */}
                  {isExpandido && (
                    <tr style={styles.expandedRow}>
                      <td colSpan={8} style={{ padding: '16px' }}>
                        <div style={styles.expandedContent}>
                          <div style={styles.expandedHeader}>
                            📝 Itens do Contrato {contrato.contrato}
                          </div>
                          
                          {loadingItens[contrato.id] ? (
                            <div style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              padding: '16px'
                            }}>
                              <div style={{
                                width: '16px',
                                height: '16px',
                                border: '2px solid #e5e7eb',
                                borderTop: '2px solid #3b82f6',
                                borderRadius: '50%',
                                animation: 'spin 1s linear infinite'
                              }}></div>
                              <span style={{ 
                                marginLeft: '8px', 
                                fontSize: '0.875rem', 
                                color: '#6b7280' 
                              }}>
                                Carregando itens...
                              </span>
                            </div>
                          ) : itensContrato[contrato.id]?.length > 0 ? (
                            <div style={styles.itemsGrid}>
                              {itensContrato[contrato.id].map((item) => (
                                <div key={item.id} style={styles.itemCard}>
                                  <div style={{ 
                                    fontSize: '0.875rem', 
                                    fontWeight: '500', 
                                    color: '#111827' 
                                  }}>
                                    {item.modelo}
                                  </div>
                                  <div style={{ 
                                    fontSize: '0.75rem', 
                                    color: '#6b7280', 
                                    marginTop: '4px' 
                                  }}>
                                    S/N: {item.numeroserie}
                                  </div>
                                  <div style={{ 
                                    fontSize: '0.75rem', 
                                    color: '#6b7280' 
                                  }}>
                                    Categoria: {item.categoria.nome}
                                  </div>
                                  <div style={{ 
                                    fontSize: '0.75rem', 
                                    color: '#9ca3af', 
                                    marginTop: '8px' 
                                  }}>
                                    {formatarData(item.inicio)} - {formatarData(item.fim)}
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div style={{ 
                              fontSize: '0.875rem', 
                              color: '#6b7280', 
                              textAlign: 'center', 
                              padding: '16px' 
                            }}>
                              Nenhum item encontrado para este contrato
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

export default TabelaContratos;
