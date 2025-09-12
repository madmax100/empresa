// src/components/dashboard/FaturamentoDashboard.tsx

import { useState, useEffect } from 'react';
import { useFaturamento } from '../../hooks/useFaturamento';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface FaturamentoDashboardProps {
  dateRange: {
    from: Date;
    to: Date;
  };
}

export function FaturamentoDashboard({ dateRange }: FaturamentoDashboardProps) {
  const { data, loading, error, fetchFaturamento } = useFaturamento();
  const [expandedCompras, setExpandedCompras] = useState(false);
  const [expandedVendas, setExpandedVendas] = useState(false);
  const [expandedServicos, setExpandedServicos] = useState(false);

  useEffect(() => {
    fetchFaturamento(dateRange);
  }, [dateRange, fetchFaturamento]);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px',
        fontSize: '18px',
        color: '#6B7280' 
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            border: '4px solid #E5E7EB', 
            borderTop: '4px solid #3B82F6', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }} />
          Carregando dados de faturamento...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '24px', 
        backgroundColor: '#FEF2F2', 
        border: '1px solid #FECACA', 
        borderRadius: '8px',
        color: '#DC2626'
      }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '600' }}>
          Erro ao carregar faturamento
        </h3>
        <p style={{ margin: 0 }}>{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ 
        padding: '24px', 
        backgroundColor: '#F9FAFB', 
        border: '1px solid #E5E7EB', 
        borderRadius: '8px',
        textAlign: 'center',
        color: '#6B7280'
      }}>
        Nenhum dado de faturamento encontrado para o período selecionado.
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString + 'T00:00:00').toLocaleDateString('pt-BR');
  };

  // Dados para gráfico de resumo por tipo
  const resumoData = data.resumo_por_tipo.map(item => ({
    name: item.tipo,
    value: item.valor_total,
    count: item.quantidade_notas
  }));

  const COLORS = ['#EF4444', '#10B981', '#3B82F6'];

  const renderTotalsCard = () => (
    <div style={{ 
      backgroundColor: '#F8FAFC', 
      padding: '24px', 
      borderRadius: '8px', 
      border: '1px solid #E2E8F0',
      marginBottom: '24px'
    }}>
      <h3 style={{ margin: '0 0 16px 0', fontSize: '20px', fontWeight: '600', color: '#1E293B' }}>
        Totais Gerais
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#3B82F6' }}>
            {data.totais_gerais.total_quantidade_notas}
          </div>
          <div style={{ fontSize: '14px', color: '#64748B', marginTop: '4px' }}>
            Total de Notas
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#10B981' }}>
            {formatCurrency(data.totais_gerais.total_valor_produtos)}
          </div>
          <div style={{ fontSize: '14px', color: '#64748B', marginTop: '4px' }}>
            Valor Produtos
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#6366F1' }}>
            {formatCurrency(data.totais_gerais.total_valor_geral)}
          </div>
          <div style={{ fontSize: '14px', color: '#64748B', marginTop: '4px' }}>
            Valor Geral
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#F59E0B' }}>
            {formatCurrency(data.totais_gerais.total_impostos)}
          </div>
          <div style={{ fontSize: '14px', color: '#64748B', marginTop: '4px' }}>
            Impostos
          </div>
        </div>
      </div>

      {/* Análise de Vendas */}
      <div style={{ marginTop: '24px' }}>
        <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '600', color: '#1E293B' }}>
          📊 Análise de Margem de Vendas
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
          <div style={{ textAlign: 'center', backgroundColor: '#F0FDF4', padding: '12px', borderRadius: '6px', border: '1px solid #BBF7D0' }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#15803D' }}>
              {formatCurrency(data.totais_gerais.analise_vendas.valor_vendas)}
            </div>
            <div style={{ fontSize: '12px', color: '#16A34A', marginTop: '2px' }}>
              Valor das Vendas
            </div>
          </div>
          <div style={{ textAlign: 'center', backgroundColor: '#FEF3C7', padding: '12px', borderRadius: '6px', border: '1px solid #FDE68A' }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#B45309' }}>
              {formatCurrency(data.totais_gerais.analise_vendas.valor_preco_entrada)}
            </div>
            <div style={{ fontSize: '12px', color: '#D97706', marginTop: '2px' }}>
              Custo dos Produtos
            </div>
          </div>
          <div style={{ textAlign: 'center', backgroundColor: '#DBEAFE', padding: '12px', borderRadius: '6px', border: '1px solid #93C5FD' }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#1D4ED8' }}>
              {formatCurrency(data.totais_gerais.analise_vendas.margem_bruta)}
            </div>
            <div style={{ fontSize: '12px', color: '#2563EB', marginTop: '2px' }}>
              Margem Bruta
            </div>
          </div>
          <div style={{ textAlign: 'center', backgroundColor: '#F3E8FF', padding: '12px', borderRadius: '6px', border: '1px solid #C4B5FD' }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#7C3AED' }}>
              {data.totais_gerais.analise_vendas.percentual_margem.toFixed(1)}%
            </div>
            <div style={{ fontSize: '12px', color: '#8B5CF6', marginTop: '2px' }}>
              % Margem
            </div>
          </div>
          <div style={{ textAlign: 'center', backgroundColor: '#F1F5F9', padding: '12px', borderRadius: '6px', border: '1px solid #CBD5E1' }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#475569' }}>
              {data.totais_gerais.analise_vendas.itens_analisados}
            </div>
            <div style={{ fontSize: '12px', color: '#64748B', marginTop: '2px' }}>
              Itens Analisados
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderResumoChart = () => (
    <div style={{ 
      backgroundColor: '#FFFFFF', 
      padding: '24px', 
      borderRadius: '8px', 
      border: '1px solid #E2E8F0',
      marginBottom: '24px'
    }}>
      <h3 style={{ margin: '0 0 16px 0', fontSize: '20px', fontWeight: '600', color: '#1E293B' }}>
        Resumo por Tipo
      </h3>
      
      {/* Cards de Resumo */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {data.resumo_por_tipo.map((item, index) => (
          <div key={index} style={{
            backgroundColor: '#FFFFFF',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #E2E8F0',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '600', color: COLORS[index % COLORS.length] }}>
              {item.tipo}
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#64748B' }}>Quantidade</div>
                <div style={{ fontSize: '18px', fontWeight: '600' }}>{item.quantidade_notas} notas</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#64748B' }}>Valor Total</div>
                <div style={{ fontSize: '18px', fontWeight: '600' }}>{formatCurrency(item.valor_total)}</div>
              </div>
            </div>
            
            {item.valor_preco_entrada !== undefined && item.margem_bruta !== undefined && (
              <div style={{ 
                marginTop: '12px', 
                padding: '12px', 
                backgroundColor: '#F0FDF4', 
                borderRadius: '6px',
                border: '1px solid #BBF7D0'
              }}>
                <div style={{ fontSize: '12px', color: '#059669', fontWeight: '500', marginBottom: '6px' }}>
                  📊 Análise de Margem
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <div>
                    <div style={{ fontSize: '11px', color: '#047857' }}>Custo</div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#047857' }}>
                      {formatCurrency(item.valor_preco_entrada)}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '11px', color: '#047857' }}>Margem</div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#047857' }}>
                      {formatCurrency(item.margem_bruta)}
                    </div>
                  </div>
                </div>
                {item.detalhes.itens_calculados && (
                  <div style={{ fontSize: '11px', color: '#065F46', marginTop: '6px' }}>
                    {item.detalhes.itens_calculados} itens calculados
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Gráficos */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', alignItems: 'center' }}>
        <div style={{ height: '300px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={resumoData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${formatCurrency(Number(value) || 0)}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {resumoData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div style={{ height: '300px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={resumoData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(value) => formatCurrency(value)} />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderTopRankings = () => (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
      {/* Top Fornecedores */}
      <div style={{ 
        backgroundColor: '#FFFFFF', 
        padding: '24px', 
        borderRadius: '8px', 
        border: '1px solid #E2E8F0'
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#1E293B' }}>
          Top 10 Fornecedores
        </h3>
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {data.top_fornecedores?.map((fornecedor, index) => (
            <div key={index} style={{ 
              padding: '12px', 
              borderBottom: '1px solid #F1F5F9',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontWeight: '500', color: '#1E293B' }}>
                  {fornecedor.fornecedor}
                </div>
                <div style={{ fontSize: '12px', color: '#64748B' }}>
                  {fornecedor.quantidade_notas} notas
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: '600', color: '#10B981' }}>
                  {formatCurrency(fornecedor.valor_total)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Clientes */}
      <div style={{ 
        backgroundColor: '#FFFFFF', 
        padding: '24px', 
        borderRadius: '8px', 
        border: '1px solid #E2E8F0'
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#1E293B' }}>
          Top 10 Clientes
        </h3>
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {data.top_clientes?.map((cliente, index) => (
            <div key={index} style={{ 
              padding: '12px', 
              borderBottom: '1px solid #F1F5F9',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontWeight: '500', color: '#1E293B' }}>
                  {cliente.cliente}
                </div>
                <div style={{ fontSize: '12px', color: '#64748B' }}>
                  {cliente.quantidade_notas} notas
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: '600', color: '#3B82F6' }}>
                  {formatCurrency(cliente.valor_total)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderNotasDetalhadas = (
    title: string,
    notas: Array<Record<string, unknown>>,
    isExpanded: boolean,
    setExpanded: (expanded: boolean) => void,
    color: string,
    type: 'compras' | 'vendas' | 'servicos'
  ) => (
    <div style={{ 
      backgroundColor: '#FFFFFF', 
      padding: '24px', 
      borderRadius: '8px', 
      border: '1px solid #E2E8F0',
      marginBottom: '24px'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#1E293B' }}>
          {title} ({notas?.length || 0} notas)
        </h3>
        <button
          onClick={() => setExpanded(!isExpanded)}
          style={{
            padding: '8px 16px',
            backgroundColor: color,
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          {isExpanded ? 'Recolher' : 'Expandir'}
        </button>
      </div>
      
      {isExpanded && (
        <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#F8FAFC' }}>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #E2E8F0' }}>
                  Número
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #E2E8F0' }}>
                  Data
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #E2E8F0' }}>
                  {type === 'compras' ? 'Fornecedor' : 'Cliente'}
                </th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #E2E8F0' }}>
                  Valor Produtos
                </th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #E2E8F0' }}>
                  {type === 'compras' ? 'ICMS/IPI' : type === 'vendas' ? 'ICMS/Desc.' : 'ISS'}
                </th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #E2E8F0' }}>
                  Total
                </th>
                {type === 'vendas' && (
                  <>
                    <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #E2E8F0' }}>
                      Custo Entrada
                    </th>
                    <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #E2E8F0' }}>
                      Margem Bruta
                    </th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {notas?.map((nota, index) => (
                <tr key={index} style={{ borderBottom: '1px solid #F1F5F9' }}>
                  <td style={{ padding: '12px' }}>
                    {nota.numero_nota as string}
                  </td>
                  <td style={{ padding: '12px' }}>
                    {type === 'compras' 
                      ? formatDate((nota.data_emissao as string).split('T')[0])
                      : formatDate((nota.data as string).split('T')[0])
                    }
                  </td>
                  <td style={{ padding: '12px' }}>
                    {type === 'compras' ? (nota.fornecedor as string) : (nota.cliente as string)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {formatCurrency(nota.valor_produtos as number)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {type === 'compras' 
                      ? formatCurrency((nota.valor_icms as number || 0) + (nota.valor_ipi as number || 0))
                      : type === 'vendas'
                      ? formatCurrency((nota.valor_icms as number || 0) + (nota.desconto as number || 0))
                      : formatCurrency(nota.valor_iss as number || 0)
                    }
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600' }}>
                    {formatCurrency(nota.valor_total as number)}
                  </td>
                  {type === 'vendas' && (
                    <>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        {formatCurrency(nota.valor_preco_entrada as number || 0)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#059669' }}>
                        {formatCurrency(nota.margem_bruta as number || 0)}
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  return (
    <div style={{ padding: '24px' }}>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      
      <h2 style={{ margin: '0 0 24px 0', fontSize: '28px', fontWeight: '700', color: '#1E293B' }}>
        Relatório de Faturamento
      </h2>

      <div style={{ 
        backgroundColor: '#EFF6FF', 
        padding: '16px', 
        borderRadius: '8px', 
        border: '1px solid #DBEAFE',
        marginBottom: '24px'
      }}>
        <p style={{ margin: 0, color: '#1E40AF' }}>
          <strong>Período:</strong> {formatDate(data.parametros.data_inicio)} até {formatDate(data.parametros.data_fim)}
        </p>
      </div>

      {renderTotalsCard()}
      {renderResumoChart()}
      {renderTopRankings()}

      {/* Notas Detalhadas */}
      <h3 style={{ margin: '0 0 16px 0', fontSize: '20px', fontWeight: '600', color: '#1E293B' }}>
        Notas Detalhadas
      </h3>

      {renderNotasDetalhadas(
        'Compras (NF Entrada)',
        data.notas_detalhadas.compras,
        expandedCompras,
        setExpandedCompras,
        '#EF4444',
        'compras'
      )}

      {renderNotasDetalhadas(
        'Vendas (NF Saída)',
        data.notas_detalhadas.vendas,
        expandedVendas,
        setExpandedVendas,
        '#10B981',
        'vendas'
      )}

      {renderNotasDetalhadas(
        'Serviços (NF Serviço)',
        data.notas_detalhadas.servicos,
        expandedServicos,
        setExpandedServicos,
        '#3B82F6',
        'servicos'
      )}
    </div>
  );
}
