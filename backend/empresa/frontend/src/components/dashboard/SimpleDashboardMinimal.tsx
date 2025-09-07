import React, { useState, useEffect } from 'react';
import { fluxoCaixaService, formatCurrency, formatDate, type FluxoCaixaRealizado } from '../../services/dashboard-service';

interface Movimentacao {
  id: string;
  tipo: 'entrada' | 'saida';
  data_pagamento: string;
  valor: number;
  contraparte: string;
  historico: string;
  forma_pagamento: string;
  origem: 'contas_receber' | 'contas_pagar';
}

const SimpleDashboardMinimal: React.FC = () => {
  const [data, setData] = useState<FluxoCaixaRealizado | null>(null);
  const [movimentacoes, setMovimentacoes] = useState<Movimentacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Carregar dados de fluxo de caixa realizado e movimentações
        const [fluxoCaixa, movimentacoesRecentes] = await Promise.all([
          fluxoCaixaService.getFluxoCaixaRealizado(),
          fluxoCaixaService.getMovimentacoesRecentes()
        ]);
        
        setData(fluxoCaixa);
        setMovimentacoes(movimentacoesRecentes);
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
        setError('Erro ao carregar dados do fluxo de caixa realizado');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div style={{
        padding: '20px',
        backgroundColor: '#f8fafc',
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🔄</div>
          <div style={{ fontSize: '1.125rem', color: '#6b7280' }}>
            Carregando dados do backend...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: '20px',
        backgroundColor: '#f8fafc',
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
          maxWidth: '400px'
        }}>
          <div style={{ color: '#dc2626', fontWeight: '600', marginBottom: '10px' }}>
            ❌ Erro ao carregar dados
          </div>
          <div style={{ color: '#7f1d1d', marginBottom: '15px' }}>
            {error}
          </div>
          <button 
            onClick={() => window.location.reload()}
            style={{
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }
  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#f8fafc',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#1e40af',
        color: 'white',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: '600' }}>
          Dashboard - Fluxo de Caixa Real
        </h1>
        <div style={{ margin: '8px 0 0 0', fontSize: '1rem', opacity: 0.9 }}>
          � Dados atualizados do sistema
        </div>
      </div>

      {/* Métricas */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '20px'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          borderLeft: '4px solid #10b981',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
            Total de Entradas (Pagas)
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
            {formatCurrency(data.total_entradas_pagas)}
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
            Total de Saídas (Pagas)
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
            {formatCurrency(data.total_saidas_pagas)}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          borderLeft: '4px solid #3b82f6',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
            Saldo Realizado
          </div>
          <div style={{ 
            fontSize: '1.5rem', 
            fontWeight: '700', 
            color: data.saldo_liquido >= 0 ? '#10b981' : '#ef4444'
          }}>
            {formatCurrency(data.saldo_liquido)}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          borderLeft: '4px solid #8b5cf6',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
            Total de Movimentações
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
            {data.total_movimentacoes}
          </div>
        </div>
      </div>

      {/* Tabela */}
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', margin: '0 0 15px 0' }}>
          Movimentações Recentes ({movimentacoes.length})
        </h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{
                  textAlign: 'left',
                  padding: '12px 15px',
                  backgroundColor: '#f9fafb',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  color: '#374151',
                  borderBottom: '1px solid #e5e7eb'
                }}>Data</th>
                <th style={{
                  textAlign: 'left',
                  padding: '12px 15px',
                  backgroundColor: '#f9fafb',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  color: '#374151',
                  borderBottom: '1px solid #e5e7eb'
                }}>Tipo</th>
                <th style={{
                  textAlign: 'left',
                  padding: '12px 15px',
                  backgroundColor: '#f9fafb',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  color: '#374151',
                  borderBottom: '1px solid #e5e7eb'
                }}>Valor</th>
                <th style={{
                  textAlign: 'left',
                  padding: '12px 15px',
                  backgroundColor: '#f9fafb',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  color: '#374151',
                  borderBottom: '1px solid #e5e7eb'
                }}>Contraparte</th>
                <th style={{
                  textAlign: 'left',
                  padding: '12px 15px',
                  backgroundColor: '#f9fafb',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  color: '#374151',
                  borderBottom: '1px solid #e5e7eb'
                }}>Histórico</th>
              </tr>
            </thead>
            <tbody>
              {movimentacoes.map((mov) => (
                <tr key={mov.id}>
                  <td style={{ padding: '12px 15px', borderBottom: '1px solid #e5e7eb', fontSize: '0.875rem' }}>
                    {formatDate(mov.data_pagamento)}
                  </td>
                  <td style={{ padding: '12px 15px', borderBottom: '1px solid #e5e7eb', fontSize: '0.875rem' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      backgroundColor: mov.tipo === 'entrada' ? '#dcfce7' : '#fee2e2',
                      color: mov.tipo === 'entrada' ? '#166534' : '#dc2626'
                    }}>
                      {mov.tipo === 'entrada' ? '↗️ Entrada' : '↘️ Saída'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 15px', borderBottom: '1px solid #e5e7eb', fontSize: '0.875rem' }}>
                    <strong style={{ color: mov.tipo === 'entrada' ? '#10b981' : '#ef4444' }}>
                      {formatCurrency(mov.valor)}
                    </strong>
                  </td>
                  <td style={{ padding: '12px 15px', borderBottom: '1px solid #e5e7eb', fontSize: '0.875rem' }}>
                    {mov.contraparte}
                  </td>
                  <td style={{ 
                    padding: '12px 15px', 
                    borderBottom: '1px solid #e5e7eb', 
                    fontSize: '0.875rem',
                    maxWidth: '200px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {mov.historico}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {movimentacoes.length === 0 && (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px 20px', 
            color: '#6b7280' 
          }}>
            📋 Nenhuma movimentação encontrada
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleDashboardMinimal;
