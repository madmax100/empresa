// src/components/dashboard/CustosVariaveisDashboard.tsx

import React, { useState, useEffect } from 'react';
import { useCustosVariaveis, type DateRange } from '../../hooks/useCustosVariaveis';
import { formatCurrency } from '../../lib/utils';
import {
  Calendar,
  Download,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Building2,
  Receipt,
  CreditCard,
  Users,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];

// Função local para formatação de percentual
const formatPercent = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(value / 100);
};

export default function CustosVariaveisDashboard() {
  const { data, loading, error, fetchCustosVariaveis } = useCustosVariaveis();
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(new Date().getFullYear(), 0, 1), // Início do ano
    to: new Date() // Hoje
  });

  const [dataInicio, setDataInicio] = useState(
    new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0]
  );
  const [dataFim, setDataFim] = useState(
    new Date().toISOString().split('T')[0]
  );

  // Estado para controlar quais especificações estão expandidas
  const [expandedSpecs, setExpandedSpecs] = useState<Set<string>>(new Set());

  // Carregar dados automaticamente quando o componente for montado
  useEffect(() => {
    console.log('🎬 Componente montado, carregando dados iniciais...');
    fetchCustosVariaveis(dateRange);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Adicionar efeito para monitorar mudanças no dateRange
  useEffect(() => {
    console.log('📅 DateRange alterado:', dateRange);
  }, [dateRange]);

  const handleApplyFilter = () => {
    console.log('🔍 Aplicando filtro com datas:', { dataInicio, dataFim });
    
    const from = new Date(dataInicio + 'T00:00:00');
    const to = new Date(dataFim + 'T23:59:59');
    
    console.log('🔍 Datas convertidas:', { from, to });
    
    if (!isNaN(from.getTime()) && !isNaN(to.getTime())) {
      const newDateRange = { from, to };
      console.log('🔍 Novo range de datas:', newDateRange);
      setDateRange(newDateRange);
      fetchCustosVariaveis(newDateRange);
    } else {
      console.error('❌ Datas inválidas:', { dataInicio, dataFim });
    }
  };

  const exportToCSV = () => {
    if (!data || !data.contas_pagas) return;

    const csvData = data.contas_pagas.map(conta => ({
      Fornecedor: conta.fornecedor_nome,
      Tipo: conta.fornecedor_tipo,
      Especificacao: conta.fornecedor_especificacao,
      'Valor Original': conta.valor_original,
      'Valor Pago': conta.valor_pago,
      Juros: conta.juros,
      Tarifas: conta.tarifas,
      'Data Pagamento': conta.data_pagamento,
      'Forma Pagamento': conta.forma_pagamento,
      Historico: conta.historico
    }));

    const csvContent = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `custos-variaveis-${dataInicio}-${dataFim}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  // Função para toggle da expansão de uma especificação
  const toggleExpansion = (especificacao: string) => {
    const newExpanded = new Set(expandedSpecs);
    if (newExpanded.has(especificacao)) {
      newExpanded.delete(especificacao);
    } else {
      newExpanded.add(especificacao);
    }
    setExpandedSpecs(newExpanded);
  };

  // Função para obter contas pagas de uma especificação específica
  const getContasPorEspecificacao = (especificacao: string) => {
    if (!data?.contas_pagas) return [];
    return data.contas_pagas.filter(conta => conta.fornecedor_especificacao === especificacao);
  };

  // Função para formatar data
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('pt-BR');
    } catch {
      return dateString;
    }
  };

  // Preparar dados para os gráficos
  const chartDataEspecificacao = data?.resumo_por_especificacao?.map((item, index) => ({
    name: item.especificacao,
    valor: item.valor_pago_total,
    contas: item.quantidade_contas,
    fornecedores: item.quantidade_fornecedores,
    color: COLORS[index % COLORS.length]
  })) || [];

  const totalGeral = data?.totais_gerais?.total_valor_pago || 0;

  return (
    <div style={{
      padding: '24px',
      backgroundColor: '#f8fafc',
      minHeight: 'calc(100vh - 60px)'
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '32px'
      }}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: '700',
          color: '#1f2937',
          marginBottom: '8px'
        }}>
          💰 Custos Variáveis
        </h1>
        <p style={{
          color: '#6b7280',
          fontSize: '1rem'
        }}>
          Análise detalhada dos custos variáveis da empresa por especificação de fornecedor
        </p>
      </div>

      {/* Filtros de Data */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Calendar size={20} color="#6b7280" />
            <span style={{
              fontWeight: '500',
              color: '#374151'
            }}>
              Período:
            </span>
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <label style={{
              fontSize: '0.875rem',
              color: '#6b7280'
            }}>
              De:
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
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <label style={{
              fontSize: '0.875rem',
              color: '#6b7280'
            }}>
              Até:
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
            onClick={handleApplyFilter}
            disabled={loading}
            style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              padding: '8px 16px',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            {loading ? 'Carregando...' : 'Aplicar Filtro'}
          </button>

          <button
            onClick={exportToCSV}
            disabled={loading || !data?.contas_pagas?.length}
            style={{
              backgroundColor: '#10b981',
              color: 'white',
              padding: '8px 16px',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: (loading || !data?.contas_pagas?.length) ? 'not-allowed' : 'pointer',
              opacity: (loading || !data?.contas_pagas?.length) ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Download size={16} />
            Exportar CSV
          </button>
        </div>
      </div>

      {/* Estados de Loading e Error */}
      {loading && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '48px',
          textAlign: 'center',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{
            display: 'inline-block',
            width: '32px',
            height: '32px',
            border: '3px solid #e5e7eb',
            borderTop: '3px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            marginBottom: '16px'
          }} />
          <p style={{
            color: '#6b7280',
            fontSize: '1rem'
          }}>
            Carregando dados de custos variáveis...
          </p>
        </div>
      )}

      {error && (
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <AlertCircle size={20} color="#ef4444" />
          <div>
            <h3 style={{
              color: '#dc2626',
              fontWeight: '600',
              margin: '0 0 4px 0'
            }}>
              Erro ao carregar dados
            </h3>
            <p style={{
              color: '#b91c1c',
              fontSize: '0.875rem',
              margin: 0
            }}>
              {error}
            </p>
          </div>
        </div>
      )}

      {/* Dados carregados */}
      {!loading && !error && data && (
        <>
          {/* Cards de Resumo */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px',
            marginBottom: '32px'
          }}>
            {/* Total Pago */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '16px'
              }}>
                <div style={{
                  padding: '12px',
                  backgroundColor: '#eff6ff',
                  borderRadius: '8px'
                }}>
                  <CreditCard size={24} color="#3b82f6" />
                </div>
                <TrendingUp size={20} color="#10b981" />
              </div>
              <h3 style={{
                fontSize: '0.875rem',
                fontWeight: '600',
                color: '#6b7280',
                margin: '0 0 8px 0',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                Total Pago no Período
              </h3>
              <p style={{
                fontSize: '2rem',
                fontWeight: '700',
                color: '#1f2937',
                margin: '0 0 8px 0'
              }}>
                {formatCurrency(data.totais_gerais.total_valor_pago)}
              </p>
              <p style={{
                fontSize: '0.875rem',
                color: '#6b7280',
                margin: 0
              }}>
                {data.total_contas_pagas} contas pagas
              </p>
            </div>

            {/* Fornecedores */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '16px'
              }}>
                <div style={{
                  padding: '12px',
                  backgroundColor: '#f0fdf4',
                  borderRadius: '8px'
                }}>
                  <Building2 size={24} color="#10b981" />
                </div>
                <Users size={20} color="#10b981" />
              </div>
              <h3 style={{
                fontSize: '0.875rem',
                fontWeight: '600',
                color: '#6b7280',
                margin: '0 0 8px 0',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                Fornecedores Ativos
              </h3>
              <p style={{
                fontSize: '2rem',
                fontWeight: '700',
                color: '#1f2937',
                margin: '0 0 8px 0'
              }}>
                {data.estatisticas_fornecedores.fornecedores_com_pagamentos_no_periodo}
              </p>
              <p style={{
                fontSize: '0.875rem',
                color: '#6b7280',
                margin: 0
              }}>
                de {data.estatisticas_fornecedores.total_fornecedores_variaveis_cadastrados} cadastrados
              </p>
            </div>

            {/* Especificações */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '16px'
              }}>
                <div style={{
                  padding: '12px',
                  backgroundColor: '#fef3c7',
                  borderRadius: '8px'
                }}>
                  <Receipt size={24} color="#f59e0b" />
                </div>
                <TrendingDown size={20} color="#ef4444" />
              </div>
              <h3 style={{
                fontSize: '0.875rem',
                fontWeight: '600',
                color: '#6b7280',
                margin: '0 0 8px 0',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                Categorias de Custos
              </h3>
              <p style={{
                fontSize: '2rem',
                fontWeight: '700',
                color: '#1f2937',
                margin: '0 0 8px 0'
              }}>
                {data.resumo_por_especificacao.length}
              </p>
              <p style={{
                fontSize: '0.875rem',
                color: '#6b7280',
                margin: 0
              }}>
                especificações diferentes
              </p>
            </div>
          </div>

          {/* Gráficos */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '2fr 1fr',
            gap: '24px',
            marginBottom: '32px'
          }}>
            {/* Gráfico de Barras - Custos por Especificação */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 style={{
                fontSize: '1.25rem',
                fontWeight: '600',
                color: '#1f2937',
                marginBottom: '24px'
              }}>
                Custos por Especificação
              </h3>
              
              {chartDataEspecificacao.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartDataEspecificacao}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis 
                      dataKey="name" 
                      tick={{ fontSize: 12, fill: '#6b7280' }}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis 
                      tick={{ fontSize: 12, fill: '#6b7280' }}
                      tickFormatter={(value) => `R$ ${(value / 1000).toFixed(0)}k`}
                    />
                    <Tooltip 
                      formatter={(value: number) => [formatCurrency(value), 'Valor Pago']}
                      labelStyle={{ color: '#1f2937' }}
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar 
                      dataKey="valor" 
                      fill="#3b82f6"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div style={{
                  height: '300px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#6b7280'
                }}>
                  Nenhum dado disponível para o período selecionado
                </div>
              )}
            </div>

            {/* Gráfico de Pizza - Distribuição */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 style={{
                fontSize: '1.25rem',
                fontWeight: '600',
                color: '#1f2937',
                marginBottom: '24px'
              }}>
                Distribuição por Especificação
              </h3>
              
              {chartDataEspecificacao.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartDataEspecificacao}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="valor"
                      label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(1)}%`}
                      labelLine={false}
                    >
                      {chartDataEspecificacao.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value: number) => [formatCurrency(value), 'Valor']}
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div style={{
                  height: '300px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#6b7280'
                }}>
                  Nenhum dado disponível
                </div>
              )}
            </div>
          </div>

          {/* Tabela Detalhada por Especificação */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            marginBottom: '32px'
          }}>
            <h3 style={{
              fontSize: '1.25rem',
              fontWeight: '600',
              color: '#1f2937',
              marginBottom: '24px'
            }}>
              Resumo por Especificação
            </h3>
            
            {data.resumo_por_especificacao.length > 0 ? (
              <div style={{
                overflowX: 'auto'
              }}>
                <table style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '0.875rem'
                }}>
                  <thead>
                    <tr style={{
                      backgroundColor: '#f9fafb',
                      borderBottom: '2px solid #e5e7eb'
                    }}>
                      <th style={{
                        padding: '12px',
                        textAlign: 'left',
                        fontWeight: '600',
                        color: '#374151',
                        width: '40px'
                      }}>
                      </th>
                      <th style={{
                        padding: '12px',
                        textAlign: 'left',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        Especificação
                      </th>
                      <th style={{
                        padding: '12px',
                        textAlign: 'right',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        Valor Pago
                      </th>
                      <th style={{
                        padding: '12px',
                        textAlign: 'center',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        Contas
                      </th>
                      <th style={{
                        padding: '12px',
                        textAlign: 'center',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        Fornecedores
                      </th>
                      <th style={{
                        padding: '12px',
                        textAlign: 'right',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        % do Total
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.resumo_por_especificacao.map((item, index) => {
                      const isExpanded = expandedSpecs.has(item.especificacao);
                      const contasEspecificacao = getContasPorEspecificacao(item.especificacao);
                      
                      return (
                        <React.Fragment key={index}>
                          {/* Linha principal da especificação */}
                          <tr 
                            style={{
                              borderBottom: '1px solid #e5e7eb',
                              backgroundColor: index % 2 === 0 ? 'white' : '#f9fafb',
                              cursor: 'pointer'
                            }}
                            onClick={() => toggleExpansion(item.especificacao)}
                          >
                            <td style={{
                              padding: '12px',
                              textAlign: 'center'
                            }}>
                              {isExpanded ? (
                                <ChevronDown size={16} color="#6b7280" />
                              ) : (
                                <ChevronRight size={16} color="#6b7280" />
                              )}
                            </td>
                            <td style={{
                              padding: '12px',
                              fontWeight: '500',
                              color: '#1f2937'
                            }}>
                              {item.especificacao}
                            </td>
                            <td style={{
                              padding: '12px',
                              textAlign: 'right',
                              fontWeight: '600',
                              color: '#1f2937'
                            }}>
                              {formatCurrency(item.valor_pago_total)}
                            </td>
                            <td style={{
                              padding: '12px',
                              textAlign: 'center',
                              color: '#6b7280'
                            }}>
                              {item.quantidade_contas}
                            </td>
                            <td style={{
                              padding: '12px',
                              textAlign: 'center',
                              color: '#6b7280'
                            }}>
                              {item.quantidade_fornecedores}
                            </td>
                            <td style={{
                              padding: '12px',
                              textAlign: 'right',
                              color: '#6b7280'
                            }}>
                              {formatPercent((item.valor_pago_total / totalGeral) * 100)}
                            </td>
                          </tr>
                          
                          {/* Linha expandida com detalhes das contas */}
                          {isExpanded && (
                            <tr>
                              <td colSpan={6} style={{
                                padding: '0',
                                backgroundColor: '#f8fafc',
                                borderBottom: '1px solid #e5e7eb'
                              }}>
                                <div style={{
                                  padding: '16px 24px'
                                }}>
                                  <h4 style={{
                                    fontSize: '0.875rem',
                                    fontWeight: '600',
                                    color: '#374151',
                                    marginBottom: '12px'
                                  }}>
                                    Contas Pagas - {item.especificacao} ({contasEspecificacao.length} contas)
                                  </h4>
                                  
                                  {contasEspecificacao.length > 0 ? (
                                    <div style={{
                                      backgroundColor: 'white',
                                      borderRadius: '8px',
                                      overflow: 'hidden',
                                      border: '1px solid #e5e7eb'
                                    }}>
                                      <table style={{
                                        width: '100%',
                                        borderCollapse: 'collapse',
                                        fontSize: '0.8125rem'
                                      }}>
                                        <thead>
                                          <tr style={{
                                            backgroundColor: '#f1f5f9'
                                          }}>
                                            <th style={{
                                              padding: '8px 12px',
                                              textAlign: 'left',
                                              fontWeight: '600',
                                              color: '#475569',
                                              borderBottom: '1px solid #e2e8f0'
                                            }}>
                                              Fornecedor
                                            </th>
                                            <th style={{
                                              padding: '8px 12px',
                                              textAlign: 'center',
                                              fontWeight: '600',
                                              color: '#475569',
                                              borderBottom: '1px solid #e2e8f0'
                                            }}>
                                              Data Pagamento
                                            </th>
                                            <th style={{
                                              padding: '8px 12px',
                                              textAlign: 'right',
                                              fontWeight: '600',
                                              color: '#475569',
                                              borderBottom: '1px solid #e2e8f0'
                                            }}>
                                              Valor Pago
                                            </th>
                                            <th style={{
                                              padding: '8px 12px',
                                              textAlign: 'center',
                                              fontWeight: '600',
                                              color: '#475569',
                                              borderBottom: '1px solid #e2e8f0'
                                            }}>
                                              Forma Pagamento
                                            </th>
                                            <th style={{
                                              padding: '8px 12px',
                                              textAlign: 'left',
                                              fontWeight: '600',
                                              color: '#475569',
                                              borderBottom: '1px solid #e2e8f0'
                                            }}>
                                              Histórico
                                            </th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {contasEspecificacao.map((conta, contaIndex) => (
                                            <tr key={conta.id} style={{
                                              backgroundColor: contaIndex % 2 === 0 ? 'white' : '#f8fafc',
                                              borderBottom: contaIndex < contasEspecificacao.length - 1 ? '1px solid #f1f5f9' : 'none'
                                            }}>
                                              <td style={{
                                                padding: '8px 12px',
                                                color: '#1e293b',
                                                fontSize: '0.8125rem'
                                              }}>
                                                {conta.fornecedor_nome}
                                              </td>
                                              <td style={{
                                                padding: '8px 12px',
                                                textAlign: 'center',
                                                color: '#64748b',
                                                fontSize: '0.8125rem'
                                              }}>
                                                {formatDate(conta.data_pagamento)}
                                              </td>
                                              <td style={{
                                                padding: '8px 12px',
                                                textAlign: 'right',
                                                fontWeight: '600',
                                                color: '#059669',
                                                fontSize: '0.8125rem'
                                              }}>
                                                {formatCurrency(conta.valor_pago)}
                                              </td>
                                              <td style={{
                                                padding: '8px 12px',
                                                textAlign: 'center',
                                                color: '#64748b',
                                                fontSize: '0.8125rem'
                                              }}>
                                                <span style={{
                                                  backgroundColor: '#e0f2fe',
                                                  color: '#0369a1',
                                                  padding: '2px 8px',
                                                  borderRadius: '4px',
                                                  fontSize: '0.75rem',
                                                  fontWeight: '500'
                                                }}>
                                                  {conta.forma_pagamento}
                                                </span>
                                              </td>
                                              <td style={{
                                                padding: '8px 12px',
                                                color: '#64748b',
                                                fontSize: '0.8125rem',
                                                maxWidth: '200px',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                whiteSpace: 'nowrap'
                                              }}>
                                                {conta.historico}
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </div>
                                  ) : (
                                    <div style={{
                                      textAlign: 'center',
                                      padding: '16px',
                                      color: '#6b7280',
                                      fontSize: '0.875rem'
                                    }}>
                                      Nenhuma conta encontrada para esta especificação
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
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '48px',
                color: '#6b7280'
              }}>
                Nenhuma especificação encontrada para o período selecionado
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
