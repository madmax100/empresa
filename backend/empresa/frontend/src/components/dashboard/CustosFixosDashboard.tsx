// src/components/dashboard/CustosFixosDashboard.tsx

import { useState, useEffect } from 'react';
import { useCustosFixos, type DateRange } from '../../hooks/useCustosFixos';
import { formatCurrency } from '../../lib/utils';
import {
  Calendar,
  Download,
  AlertCircle
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

export default function CustosFixosDashboard() {
  const { data, loading, error, fetchCustosFixos } = useCustosFixos();
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

  // Carregar dados automaticamente quando o componente for montado
  useEffect(() => {
    console.log('🎬 Componente montado, carregando dados iniciais...');
    fetchCustosFixos(dateRange);
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
      fetchCustosFixos(newDateRange);
    } else {
      console.error('❌ Datas inválidas:', { dataInicio, dataFim });
    }
  };

  const exportToCSV = () => {
    if (!data || !data.contas_pagas) return;

    const csvData = data.contas_pagas.map(conta => ({
      Fornecedor: conta.fornecedor,
      Tipo: conta.tipo_fornecedor,
      Descrição: conta.descricao,
      Valor: conta.valor,
      'Data Vencimento': conta.data_vencimento,
      'Data Pagamento': conta.data_pagamento,
      Categoria: conta.categoria || '',
      Observações: conta.observacoes || ''
    }));

    const csvContent = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `custos-fixos-${dataInicio}-${dataFim}.csv`;
    a.click();
  };

  // Preparar dados para gráficos
  const dadosGraficoTipos = data?.resumo_por_tipo_fornecedor?.map(item => ({
    nome: item.tipo_fornecedor || 'N/A',
    valor: item.valor_total || 0,
    quantidade: item.quantidade_contas || 0,
    percentual: item.percentual_valor || 0
  })) || [];

  const dadosGraficoFornecedores = data?.resumo_por_fornecedor?.slice(0, 10).map(item => ({
    fornecedor: item.fornecedor && item.fornecedor.length > 15 ? item.fornecedor.substring(0, 15) + '...' : (item.fornecedor || 'N/A'),
    valor: item.valor_total,
    tipo: item.tipo_fornecedor
  })) || [];

  // Loading state
  if (loading) {
    return (
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '24px', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px' 
      }}>
        <div style={{ color: '#6b7280', fontSize: '1rem' }}>Carregando dados...</div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '24px', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px' 
      }}>
        <div style={{ color: '#dc2626', fontSize: '1rem' }}>Erro ao carregar dados: {error}</div>
      </div>
    );
  }

  // No data state
  if (!data) {
    return (
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '24px', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px' 
      }}>
        <div style={{ color: '#6b7280', fontSize: '1rem' }}>Nenhum dado disponível</div>
      </div>
    );
  }

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '24px', 
      backgroundColor: '#f8fafc', 
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px'
    }}>
      {/* Cabeçalho */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', fontWeight: '700', color: '#111827' }}>
            Dashboard de Custos Fixos
          </h1>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Análise detalhada de custos fixos e despesas fixas
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6b7280' }}>
          <Calendar style={{ width: '20px', height: '20px' }} />
          <span style={{ fontSize: '0.875rem' }}>
            {dateRange.from.toLocaleDateString()} - {dateRange.to.toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Filtros de Data */}
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '16px'
        }}>
          <span style={{
            backgroundColor: '#e0e7ff',
            color: '#3730a3',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '0.75rem',
            fontWeight: '500'
          }}>
            📅 PERÍODO
          </span>
          <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
            Filtros de Data
          </h2>
        </div>
        
        <div style={{ display: 'flex', gap: '16px', alignItems: 'end', flexWrap: 'wrap' }}>
          {/* Botões de período pré-definido */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={() => {
                const hoje = new Date();
                const inicioMes = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
                setDataInicio(inicioMes.toISOString().split('T')[0]);
                setDataFim(hoje.toISOString().split('T')[0]);
              }}
              style={{
                padding: '8px 12px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.75rem'
              }}
            >
              Este Mês
            </button>
            <button
              onClick={() => {
                const hoje = new Date();
                const inicioAno = new Date(hoje.getFullYear(), 0, 1);
                setDataInicio(inicioAno.toISOString().split('T')[0]);
                setDataFim(hoje.toISOString().split('T')[0]);
              }}
              style={{
                padding: '8px 12px',
                backgroundColor: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.75rem'
              }}
            >
              Este Ano
            </button>
            <button
              onClick={() => {
                const hoje = new Date();
                const anoPassado = new Date(hoje.getFullYear() - 1, 0, 1);
                const fimAnoPassado = new Date(hoje.getFullYear() - 1, 11, 31);
                setDataInicio(anoPassado.toISOString().split('T')[0]);
                setDataFim(fimAnoPassado.toISOString().split('T')[0]);
              }}
              style={{
                padding: '8px 12px',
                backgroundColor: '#059669',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.75rem'
              }}
            >
              Ano Passado
            </button>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <label style={{ fontSize: '0.875rem', color: '#374151' }}>De:</label>
            <input
              type="date"
              value={dataInicio}
              onChange={(e) => setDataInicio(e.target.value)}
              style={{
                padding: '8px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '0.875rem'
              }}
            />
            <label style={{ fontSize: '0.875rem', color: '#374151' }}>Até:</label>
            <input
              type="date"
              value={dataFim}
              onChange={(e) => setDataFim(e.target.value)}
              style={{
                padding: '8px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '0.875rem'
              }}
            />
            <button
              onClick={handleApplyFilter}
              style={{
                padding: '8px 16px',
                backgroundColor: '#dc2626',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Aplicar
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertCircle style={{ width: '16px', height: '16px', color: '#dc2626' }} />
          <span style={{ color: '#dc2626', fontSize: '0.875rem' }}>{error}</span>
        </div>
      )}

      {/* Cards de Estatísticas */}
      {data && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #3b82f6',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              Valor Total
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(data.totais_gerais.valor_total)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {data.total_contas_pagas} contas pagas
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #ef4444',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              Custos Fixos
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(data.totais_gerais.valor_custos_fixos)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {formatPercent((data.totais_gerais.valor_custos_fixos / data.totais_gerais.valor_total) * 100)} do total
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #10b981',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              Despesas Fixas
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(data.totais_gerais.valor_despesas_fixas)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {formatPercent((data.totais_gerais.valor_despesas_fixas / data.totais_gerais.valor_total) * 100)} do total
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #f59e0b',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              Fornecedores Ativos
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {data.estatisticas_fornecedores.fornecedores_ativos}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {data.estatisticas_fornecedores.fornecedores_custo_fixo} custos, {data.estatisticas_fornecedores.fornecedores_despesa_fixa} despesas
            </div>
          </div>
        </div>
      )}

      {/* Gráficos */}
      {data && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
          {/* Gráfico de Barras - Top Fornecedores */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
              Top 10 Fornecedores
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={dadosGraficoFornecedores}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="fornecedor" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                <Bar dataKey="valor" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Gráfico de Pizza - Distribuição por Tipo */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
              Distribuição por Tipo
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={dadosGraficoTipos}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({nome, percentual}) => `${nome} ${percentual.toFixed(1)}%`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="valor"
                >
                  {dadosGraficoTipos.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Tabela de Fornecedores */}
      {data && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '20px',
            borderBottom: '1px solid #f3f4f6',
            backgroundColor: '#f9fafb'
          }}>
            <h2 style={{ 
              fontSize: '1.25rem', 
              fontWeight: '600',
              color: '#111827',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span style={{
                backgroundColor: '#e0e7ff',
                color: '#3730a3',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '0.75rem',
                fontWeight: '500'
              }}>
                📊 RESUMO
              </span>
              Detalhamento por Fornecedor
            </h2>
          </div>
          <div style={{ padding: '20px', overflowX: 'auto' }}>
            <table style={{ 
              width: '100%', 
              borderCollapse: 'collapse' as const,
              fontSize: '0.875rem'
            }}>
              <thead>
                <tr style={{ backgroundColor: '#f9fafb' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #f3f4f6' }}>Fornecedor</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #f3f4f6' }}>Tipo</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #f3f4f6' }}>Qtd. Contas</th>
                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #f3f4f6' }}>Valor Total</th>
                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #f3f4f6' }}>% do Total</th>
                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #f3f4f6' }}>Valor Médio</th>
                </tr>
              </thead>
              <tbody>
                {data?.resumo_por_fornecedor?.map((fornecedor, index) => (
                  <tr 
                    key={index}
                    style={{ 
                      borderBottom: '1px solid #f3f4f6'
                    }}
                  >
                    <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', fontWeight: '500' }}>
                      {fornecedor.fornecedor}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', fontSize: '0.875rem' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        backgroundColor: fornecedor.tipo_fornecedor === 'CUSTO FIXO' ? '#dbeafe' : '#dcfce7',
                        color: fornecedor.tipo_fornecedor === 'CUSTO FIXO' ? '#1e40af' : '#166534'
                      }}>
                        {fornecedor.tipo_fornecedor}
                      </span>
                    </td>
                    <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', textAlign: 'center' }}>
                      {fornecedor.quantidade_contas}
                    </td>
                    <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', textAlign: 'right', fontWeight: '600' }}>
                      {formatCurrency(fornecedor.valor_total)}
                    </td>
                    <td style={{ 
                      padding: '12px', 
                      fontSize: '0.875rem', 
                      textAlign: 'right',
                      fontWeight: '600',
                      color: '#059669'
                    }}>
                      {formatPercent(fornecedor.percentual_do_total)}
                    </td>
                    <td style={{ padding: '12px', fontSize: '0.875rem', color: '#6b7280', textAlign: 'right' }}>
                      {formatCurrency(fornecedor.valor_medio_conta)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Botão de Exportação */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
        <button
          onClick={exportToCSV}
          disabled={!data}
          style={{
            padding: '8px 16px',
            backgroundColor: data ? 'white' : '#f3f4f6',
            color: data ? '#374151' : '#9ca3af',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            cursor: data ? 'pointer' : 'not-allowed',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Download style={{ width: '16px', height: '16px' }} />
          Exportar Relatório CSV
        </button>
      </div>

      {loading && (
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          padding: '40px' 
        }}>
          <div style={{ 
            animation: 'spin 1s linear infinite',
            borderRadius: '50%',
            height: '32px',
            width: '32px',
            borderWidth: '2px',
            borderStyle: 'solid',
            borderColor: 'transparent transparent #3b82f6 transparent'
          }} />
          <span style={{ marginLeft: '12px', color: '#6b7280' }}>Carregando dados...</span>
        </div>
      )}
    </div>
  );
}
