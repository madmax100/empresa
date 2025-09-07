import React, { useState, useEffect, useCallback } from 'react';
import { formatCurrency, formatDate } from '../../services/dashboard-service';

// Interfaces para os diferentes endpoints
interface MovimentacaoRealizada {
  id: string;
  tipo: 'entrada' | 'saida';
  data_pagamento: string;
  valor: number;
  contraparte: string;
  historico: string;
  forma_pagamento: string;
  origem: 'contas_receber' | 'contas_pagar';
}

interface MovimentacaoAberta {
  id: string;
  tipo: 'entrada_pendente' | 'saida_pendente';
  data_emissao: string;
  data_vencimento: string;
  valor: number;
  contraparte: string;
  historico: string;
  forma_pagamento: string;
  origem: 'contas_receber' | 'contas_pagar';
  dias_vencimento: number;
  status_vencimento: 'no_prazo' | 'vence_em_breve' | 'vencido';
}

interface EstatisticasVencimento {
  no_prazo: {
    entradas: number;
    saidas: number;
    qtd_entradas: number;
    qtd_saidas: number;
  };
  vence_em_breve: {
    entradas: number;
    saidas: number;
    qtd_entradas: number;
    qtd_saidas: number;
  };
  vencido: {
    entradas: number;
    saidas: number;
    qtd_entradas: number;
    qtd_saidas: number;
  };
}

interface ResumoFluxo {
  total_entradas: number;
  total_saidas: number;
  saldo_liquido: number;
  total_movimentacoes?: number;
}

interface ResumoAberto {
  total_entradas_pendentes: number;
  total_saidas_pendentes: number;
  saldo_liquido_pendente: number;
  total_movimentacoes_pendentes?: number;
}

interface ResumoDiario {
  periodo: {
    data_inicio: string;
    data_fim: string;
  };
  totais: ResumoFluxo;
  dias: Array<{
    data: string;
    entradas: number;
    saidas: number;
    saldo_dia: number;
  }>;
}

interface ResumoMensal {
  periodo: {
    data_inicio: string;
    data_fim: string;
  };
  totais: ResumoFluxo;
  meses: Array<{
    mes: string;
    entradas: number;
    saidas: number;
    saldo_mes: number;
  }>;
}

const FluxoCaixaDashboard: React.FC = () => {
  // Estados para dados
  const [movimentacoesRealizadas, setMovimentacoesRealizadas] = useState<MovimentacaoRealizada[]>([]);
  const [movimentacoesAbertas, setMovimentacoesAbertas] = useState<MovimentacaoAberta[]>([]);
  const [estatisticasVencimento, setEstatisticasVencimento] = useState<EstatisticasVencimento | null>(null);
  const [resumoDiario, setResumoDiario] = useState<ResumoDiario | null>(null);
  const [resumoMensal, setResumoMensal] = useState<ResumoMensal | null>(null);
  const [resumoRealizadas, setResumoRealizadas] = useState<ResumoFluxo | null>(null);
  const [resumoAbertas, setResumoAbertas] = useState<ResumoAberto | null>(null);

  // Estados para controle
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'realizadas' | 'abertas' | 'diario' | 'mensal'>('realizadas');
  
  // Estados para filtros
  const [dataInicio, setDataInicio] = useState<string>('2024-01-01');
  const [dataFim, setDataFim] = useState<string>('2024-12-31');

  // Função para buscar dados de todas as APIs
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const baseUrl = 'http://127.0.0.1:8000/api/fluxo-caixa-realizado';
      const params = `?data_inicio=${dataInicio}&data_fim=${dataFim}`;

      const [realizadasRes, abertasRes, diarioRes] = await Promise.all([
        fetch(`${baseUrl}/movimentacoes_realizadas/${params}`),
        fetch(`${baseUrl}/movimentacoes_vencimento_aberto/${params}`),
        fetch(`${baseUrl}/resumo_diario/${params}`)
      ]);

      if (!realizadasRes.ok || !abertasRes.ok || !diarioRes.ok) {
        throw new Error('Erro ao carregar dados dos endpoints');
      }

      const realizadasData = await realizadasRes.json();
      const abertasData = await abertasRes.json();
      const diarioData = await diarioRes.json();

      // Processar dados realizadas
      setMovimentacoesRealizadas(realizadasData.movimentacoes || []);
      setResumoRealizadas(realizadasData.resumo);

      // Processar dados abertos
      setResumoAbertas(abertasData.resumo);
      setEstatisticasVencimento(abertasData.estatisticas_vencimento || null);
      setMovimentacoesAbertas(abertasData.movimentacoes_abertas || []);

      // Processar dados diários
      setResumoDiario(diarioData);

      // Tentar carregar dados mensais (pode dar erro no backend)
      try {
        const mensalRes = await fetch(`${baseUrl}/resumo_mensal/${params}`);
        if (mensalRes.ok) {
          const mensalData = await mensalRes.json();
          setResumoMensal(mensalData);
        }
      } catch (err) {
        console.warn('Erro ao carregar dados mensais:', err);
      }

    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setError('Erro ao carregar dados do fluxo de caixa');
    } finally {
      setLoading(false);
    }
  }, [dataInicio, dataFim]);

  useEffect(() => {
    loadData();
  }, [dataInicio, dataFim, loadData]);

  // Função para aplicar filtros
  const handleApplyFilter = () => {
    loadData();
  };

  // Função para definir período pré-definido
  const setPeriodo = (tipo: 'mes_atual' | 'ano_atual' | 'ultimo_mes') => {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = hoje.getMonth();

    switch (tipo) {
      case 'mes_atual':
        setDataInicio(`${ano}-${String(mes + 1).padStart(2, '0')}-01`);
        setDataFim(`${ano}-${String(mes + 1).padStart(2, '0')}-${new Date(ano, mes + 1, 0).getDate()}`);
        break;
      case 'ano_atual':
        setDataInicio(`${ano}-01-01`);
        setDataFim(`${ano}-12-31`);
        break;
      case 'ultimo_mes': {
        const mesAnterior = mes === 0 ? 11 : mes - 1;
        const anoAnterior = mes === 0 ? ano - 1 : ano;
        setDataInicio(`${anoAnterior}-${String(mesAnterior + 1).padStart(2, '0')}-01`);
        setDataFim(`${anoAnterior}-${String(mesAnterior + 1).padStart(2, '0')}-${new Date(anoAnterior, mesAnterior + 1, 0).getDate()}`);
        break;
      }
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div style={{ fontSize: '1.125rem', color: '#6b7280' }}>Carregando dados do fluxo de caixa...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '16px', margin: '16px' }}>
        <div style={{ color: '#dc2626', fontWeight: '600' }}>Erro:</div>
        <div style={{ color: '#7f1d1d', marginTop: '4px' }}>{error}</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Cabeçalho */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
          Fluxo de Caixa Completo
        </h1>
        <p style={{ color: '#6b7280' }}>
          Análise completa das movimentações financeiras realizadas e pendentes
        </p>
      </div>

      {/* Filtros de Período */}
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '24px'
      }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px' }}>Filtros de Período</h3>
        
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Botões de período pré-definido */}
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setPeriodo('mes_atual')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Mês Atual
            </button>
            <button
              onClick={() => setPeriodo('ultimo_mes')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Último Mês
            </button>
            <button
              onClick={() => setPeriodo('ano_atual')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#059669',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Ano Atual
            </button>
          </div>

          {/* Campos de data customizados */}
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
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

      {/* Abas de Navegação */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{
          display: 'flex',
          borderBottom: '2px solid #e5e7eb',
          gap: '4px'
        }}>
          {[
            { key: 'realizadas', label: 'Movimentações Realizadas', icon: '✅' },
            { key: 'abertas', label: 'Movimentações Abertas', icon: '⏳' },
            { key: 'diario', label: 'Resumo Diário', icon: '📅' },
            { key: 'mensal', label: 'Resumo Mensal', icon: '📊' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as 'realizadas' | 'abertas' | 'diario' | 'mensal')}
              style={{
                padding: '12px 20px',
                backgroundColor: activeTab === tab.key ? '#3b82f6' : 'transparent',
                color: activeTab === tab.key ? 'white' : '#6b7280',
                border: 'none',
                borderRadius: '8px 8px 0 0',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s'
              }}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Conteúdo das Abas */}
      {activeTab === 'realizadas' && (
        <div>
          {/* Resumo das Movimentações Realizadas */}
          {resumoRealizadas && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              <div style={{
                backgroundColor: 'white',
                padding: '20px',
                borderRadius: '8px',
                borderLeft: '4px solid #10b981',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                  Total de Entradas Realizadas
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                  {formatCurrency(resumoRealizadas.total_entradas)}
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
                  Total de Saídas Realizadas
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                  {formatCurrency(resumoRealizadas.total_saidas)}
                </div>
              </div>

              <div style={{
                backgroundColor: 'white',
                padding: '20px',
                borderRadius: '8px',
                borderLeft: `4px solid ${resumoRealizadas.saldo_liquido >= 0 ? '#10b981' : '#ef4444'}`,
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                  Saldo Líquido Realizado
                </div>
                <div style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: '700', 
                  color: resumoRealizadas.saldo_liquido >= 0 ? '#10b981' : '#ef4444'
                }}>
                  {formatCurrency(resumoRealizadas.saldo_liquido)}
                </div>
              </div>

              {resumoRealizadas.total_movimentacoes && (
                <div style={{
                  backgroundColor: 'white',
                  padding: '20px',
                  borderRadius: '8px',
                  borderLeft: '4px solid #3b82f6',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                    Total de Movimentações
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                    {resumoRealizadas.total_movimentacoes}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tabela de Movimentações Realizadas */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            overflow: 'hidden'
          }}>
            <div style={{
              padding: '20px',
              borderBottom: '1px solid #e5e7eb'
            }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
                Movimentações Realizadas ({movimentacoesRealizadas.length})
              </h3>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: '#f9fafb' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Data Pagamento</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Tipo</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Valor</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Contraparte</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Histórico</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Forma Pagamento</th>
                  </tr>
                </thead>
                <tbody>
                  {movimentacoesRealizadas.slice(0, 50).map((mov) => (
                    <tr key={mov.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                        {formatDate(mov.data_pagamento)}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: '500',
                          backgroundColor: mov.tipo === 'entrada' ? '#dcfce7' : '#fee2e2',
                          color: mov.tipo === 'entrada' ? '#166534' : '#dc2626'
                        }}>
                          {mov.tipo === 'entrada' ? 'Entrada' : 'Saída'}
                        </span>
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        fontSize: '0.875rem', 
                        fontWeight: '600',
                        color: mov.tipo === 'entrada' ? '#059669' : '#dc2626'
                      }}>
                        {formatCurrency(mov.valor)}
                      </td>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                        {mov.contraparte}
                      </td>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#6b7280' }}>
                        {mov.historico}
                      </td>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#6b7280' }}>
                        {mov.forma_pagamento}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {movimentacoesRealizadas.length === 0 && (
                <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
                  Nenhuma movimentação realizada encontrada no período selecionado.
                </div>
              )}

              {movimentacoesRealizadas.length > 50 && (
                <div style={{ padding: '12px', textAlign: 'center', color: '#6b7280', fontSize: '0.875rem' }}>
                  Mostrando as primeiras 50 de {movimentacoesRealizadas.length} movimentações
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'abertas' && (
        <div>
          {/* Resumo das Movimentações Abertas */}
          {resumoAbertas && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              <div style={{
                backgroundColor: 'white',
                padding: '20px',
                borderRadius: '8px',
                borderLeft: '4px solid #f59e0b',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                  Entradas Pendentes
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                  {formatCurrency(resumoAbertas.total_entradas_pendentes)}
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
                  Saídas Pendentes
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                  {formatCurrency(resumoAbertas.total_saidas_pendentes)}
                </div>
              </div>

              <div style={{
                backgroundColor: 'white',
                padding: '20px',
                borderRadius: '8px',
                borderLeft: `4px solid ${resumoAbertas.saldo_liquido_pendente >= 0 ? '#10b981' : '#ef4444'}`,
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                  Saldo Pendente
                </div>
                <div style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: '700', 
                  color: resumoAbertas.saldo_liquido_pendente >= 0 ? '#10b981' : '#ef4444'
                }}>
                  {formatCurrency(resumoAbertas.saldo_liquido_pendente)}
                </div>
              </div>

              {movimentacoesAbertas.length > 0 && (
                <div style={{
                  backgroundColor: 'white',
                  padding: '20px',
                  borderRadius: '8px',
                  borderLeft: '4px solid #3b82f6',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                    Total de Movimentações
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                    {movimentacoesAbertas.length}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tabela de Estatísticas de Vencimento */}
          {estatisticasVencimento && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              overflow: 'hidden'
            }}>
              <div style={{
                padding: '20px',
                borderBottom: '1px solid #e5e7eb'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
                  Estatísticas de Vencimento
                </h3>
                <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '4px' }}>
                  Análise das movimentações pendentes por situação de vencimento
                </p>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead style={{ backgroundColor: '#f9fafb' }}>
                    <tr>
                      <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Situação</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Entradas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Qtd Entradas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saídas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Qtd Saídas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saldo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* No Prazo */}
                    <tr style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            backgroundColor: '#10b981'
                          }}></div>
                          <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>
                            No Prazo
                          </span>
                        </div>
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '600',
                        color: '#059669'
                      }}>
                        {formatCurrency(estatisticasVencimento.no_prazo.entradas)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#6b7280' }}>
                        {estatisticasVencimento.no_prazo.qtd_entradas}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '600',
                        color: '#dc2626'
                      }}>
                        {formatCurrency(estatisticasVencimento.no_prazo.saidas)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#6b7280' }}>
                        {estatisticasVencimento.no_prazo.qtd_saidas}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '700',
                        color: (estatisticasVencimento.no_prazo.entradas - estatisticasVencimento.no_prazo.saidas) >= 0 ? '#059669' : '#dc2626'
                      }}>
                        {formatCurrency(estatisticasVencimento.no_prazo.entradas - estatisticasVencimento.no_prazo.saidas)}
                      </td>
                    </tr>

                    {/* Vence em Breve */}
                    <tr style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            backgroundColor: '#f59e0b'
                          }}></div>
                          <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>
                            Vence em Breve
                          </span>
                        </div>
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '600',
                        color: '#059669'
                      }}>
                        {formatCurrency(estatisticasVencimento.vence_em_breve.entradas)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#6b7280' }}>
                        {estatisticasVencimento.vence_em_breve.qtd_entradas}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '600',
                        color: '#dc2626'
                      }}>
                        {formatCurrency(estatisticasVencimento.vence_em_breve.saidas)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#6b7280' }}>
                        {estatisticasVencimento.vence_em_breve.qtd_saidas}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '700',
                        color: (estatisticasVencimento.vence_em_breve.entradas - estatisticasVencimento.vence_em_breve.saidas) >= 0 ? '#059669' : '#dc2626'
                      }}>
                        {formatCurrency(estatisticasVencimento.vence_em_breve.entradas - estatisticasVencimento.vence_em_breve.saidas)}
                      </td>
                    </tr>

                    {/* Vencido */}
                    <tr style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            backgroundColor: '#ef4444'
                          }}></div>
                          <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>
                            Vencido
                          </span>
                        </div>
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '600',
                        color: '#059669'
                      }}>
                        {formatCurrency(estatisticasVencimento.vencido.entradas)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#6b7280' }}>
                        {estatisticasVencimento.vencido.qtd_entradas}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '600',
                        color: '#dc2626'
                      }}>
                        {formatCurrency(estatisticasVencimento.vencido.saidas)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#6b7280' }}>
                        {estatisticasVencimento.vencido.qtd_saidas}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        fontSize: '0.875rem', 
                        fontWeight: '700',
                        color: (estatisticasVencimento.vencido.entradas - estatisticasVencimento.vencido.saidas) >= 0 ? '#059669' : '#dc2626'
                      }}>
                        {formatCurrency(estatisticasVencimento.vencido.entradas - estatisticasVencimento.vencido.saidas)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Mensagem caso não haja dados */}
          {!estatisticasVencimento && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              padding: '40px',
              textAlign: 'center'
            }}>
              <div style={{ color: '#6b7280', fontSize: '1rem' }}>
                Nenhuma estatística de vencimento disponível para o período selecionado.
              </div>
            </div>
          )}

          {/* Tabela de Movimentações Abertas Individuais */}
          {movimentacoesAbertas.length > 0 && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              overflow: 'hidden',
              marginTop: '24px'
            }}>
              <div style={{
                padding: '20px',
                borderBottom: '1px solid #e5e7eb'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
                  Movimentações em Aberto ({movimentacoesAbertas.length})
                </h3>
                <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '4px' }}>
                  Lista detalhada das movimentações pendentes
                </p>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead style={{ backgroundColor: '#f9fafb' }}>
                    <tr>
                      <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Data Vencimento</th>
                      <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Tipo</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Valor</th>
                      <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Contraparte</th>
                      <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Histórico</th>
                      <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {movimentacoesAbertas.slice(0, 100).map((mov) => (
                      <tr key={mov.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                        <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                          {formatDate(mov.data_vencimento)}
                        </td>
                        <td style={{ padding: '12px' }}>
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '500',
                            backgroundColor: mov.tipo === 'entrada_pendente' ? '#dcfce7' : '#fee2e2',
                            color: mov.tipo === 'entrada_pendente' ? '#166534' : '#dc2626'
                          }}>
                            {mov.tipo === 'entrada_pendente' ? 'A Receber' : 'A Pagar'}
                          </span>
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          textAlign: 'right',
                          fontSize: '0.875rem', 
                          fontWeight: '600',
                          color: mov.tipo === 'entrada_pendente' ? '#059669' : '#dc2626'
                        }}>
                          {formatCurrency(mov.valor)}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          fontSize: '0.875rem', 
                          color: '#111827',
                          maxWidth: '200px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {mov.contraparte}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          fontSize: '0.875rem', 
                          color: '#6b7280',
                          maxWidth: '250px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {mov.historico}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '500',
                            backgroundColor: 
                              mov.status_vencimento === 'no_prazo' ? '#dcfce7' :
                              mov.status_vencimento === 'vence_em_breve' ? '#fef3c7' : '#fee2e2',
                            color: 
                              mov.status_vencimento === 'no_prazo' ? '#166534' :
                              mov.status_vencimento === 'vence_em_breve' ? '#92400e' : '#dc2626'
                          }}>
                            {mov.dias_vencimento > 0 ? `${mov.dias_vencimento} dias` : 
                             mov.dias_vencimento === 0 ? 'Vence hoje' : 
                             `${Math.abs(mov.dias_vencimento)} dias atraso`}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {movimentacoesAbertas.length > 100 && (
                  <div style={{ padding: '12px', textAlign: 'center', color: '#6b7280', fontSize: '0.875rem' }}>
                    Mostrando as primeiras 100 de {movimentacoesAbertas.length} movimentações
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'diario' && resumoDiario && (
        <div>
          {/* Resumo Geral do Período */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: '4px solid #10b981',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                Total de Entradas
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(resumoDiario.totais.total_entradas)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#10b981', marginTop: '4px' }}>
                📈 {resumoDiario.dias?.filter(d => d.entradas > 0).length || 0} dias com entradas
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
                Total de Saídas
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(resumoDiario.totais.total_saidas)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#ef4444', marginTop: '4px' }}>
                📉 {resumoDiario.dias?.filter(d => d.saidas > 0).length || 0} dias com saídas
              </div>
            </div>

            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: `4px solid ${resumoDiario.totais.saldo_liquido >= 0 ? '#10b981' : '#ef4444'}`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                Saldo Líquido
              </div>
              <div style={{ 
                fontSize: '1.5rem', 
                fontWeight: '700', 
                color: resumoDiario.totais.saldo_liquido >= 0 ? '#10b981' : '#ef4444'
              }}>
                {formatCurrency(resumoDiario.totais.saldo_liquido)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
                💰 {resumoDiario.dias?.filter(d => d.saldo_dia >= 0).length || 0} dias positivos
              </div>
            </div>

            {resumoDiario.dias && resumoDiario.dias.length > 0 && (
              <div style={{
                backgroundColor: 'white',
                padding: '20px',
                borderRadius: '8px',
                borderLeft: '4px solid #3b82f6',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                  Média Diária
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                  {formatCurrency(resumoDiario.totais.saldo_liquido / resumoDiario.dias.length)}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#3b82f6', marginTop: '4px' }}>
                  📊 {resumoDiario.dias.length} dias analisados
                </div>
              </div>
            )}
          </div>

          {/* Análise de Performance e Tendências */}
          {resumoDiario.dias && resumoDiario.dias.length > 1 && (
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              marginBottom: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ 
                margin: '0 0 16px 0', 
                fontSize: '1.125rem', 
                fontWeight: '600', 
                color: '#111827' 
              }}>
                📊 Análise de Performance
              </h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                {/* Melhor e Pior Dia */}
                <div>
                  <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    🏆 Melhor Performance
                  </h4>
                  {(() => {
                    const melhorDia = resumoDiario.dias.reduce((prev, current) => 
                      (current.saldo_dia > prev.saldo_dia) ? current : prev
                    );
                    return (
                      <div style={{ padding: '12px', backgroundColor: '#f0fdf4', borderRadius: '6px', borderLeft: '3px solid #22c55e' }}>
                        <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#166534' }}>
                          {formatDate(melhorDia.data)}
                        </div>
                        <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#15803d' }}>
                          {formatCurrency(melhorDia.saldo_dia)}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#166534', marginTop: '2px' }}>
                          E: {formatCurrency(melhorDia.entradas)} | S: {formatCurrency(melhorDia.saidas)}
                        </div>
                      </div>
                    );
                  })()}
                </div>

                <div>
                  <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    📉 Maior Déficit
                  </h4>
                  {(() => {
                    const piorDia = resumoDiario.dias.reduce((prev, current) => 
                      (current.saldo_dia < prev.saldo_dia) ? current : prev
                    );
                    return (
                      <div style={{ padding: '12px', backgroundColor: '#fef2f2', borderRadius: '6px', borderLeft: '3px solid #ef4444' }}>
                        <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#dc2626' }}>
                          {formatDate(piorDia.data)}
                        </div>
                        <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#dc2626' }}>
                          {formatCurrency(piorDia.saldo_dia)}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#dc2626', marginTop: '2px' }}>
                          E: {formatCurrency(piorDia.entradas)} | S: {formatCurrency(piorDia.saidas)}
                        </div>
                      </div>
                    );
                  })()}
                </div>

                {/* Estatísticas Gerais */}
                <div>
                  <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    📈 Estatísticas Gerais
                  </h4>
                  <div style={{ padding: '12px', backgroundColor: '#f8fafc', borderRadius: '6px', borderLeft: '3px solid #64748b' }}>
                    <div style={{ fontSize: '0.75rem', color: '#475569', marginBottom: '4px' }}>
                      Dias positivos: {resumoDiario.dias.filter(d => d.saldo_dia > 0).length}/{resumoDiario.dias.length}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#475569', marginBottom: '4px' }}>
                      Média entradas: {formatCurrency(resumoDiario.totais.total_entradas / resumoDiario.dias.length)}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#475569' }}>
                      Média saídas: {formatCurrency(resumoDiario.totais.total_saidas / resumoDiario.dias.length)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Gráfico de Evolução Diária */}
          {resumoDiario.dias && resumoDiario.dias.length > 0 && (
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              marginBottom: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ 
                margin: '0 0 16px 0', 
                fontSize: '1.125rem', 
                fontWeight: '600', 
                color: '#111827' 
              }}>
                📊 Evolução do Fluxo de Caixa Diário
              </h3>
              
              <div style={{ overflowX: 'auto', paddingBottom: '10px' }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'end', 
                  gap: '2px', 
                  minWidth: `${resumoDiario.dias.length * 25}px`,
                  height: '200px',
                  padding: '10px 0'
                }}>
                  {(() => {
                    const maxAbsValue = Math.max(...resumoDiario.dias.map(d => Math.abs(d.saldo_dia)));
                    return resumoDiario.dias.map((dia, index) => {
                      const heightPercent = maxAbsValue > 0 ? (Math.abs(dia.saldo_dia) / maxAbsValue) * 90 : 0;
                      const isPositive = dia.saldo_dia >= 0;
                      
                      return (
                        <div key={index} style={{ 
                          display: 'flex', 
                          flexDirection: 'column', 
                          alignItems: 'center',
                          minWidth: '20px',
                          height: '100%'
                        }}>
                          {/* Barra */}
                          <div style={{
                            width: '16px',
                            height: `${heightPercent}%`,
                            backgroundColor: isPositive ? '#22c55e' : '#ef4444',
                            borderRadius: '2px 2px 0 0',
                            marginBottom: '5px',
                            position: 'relative',
                            display: 'flex',
                            alignItems: 'end',
                            justifyContent: 'center'
                          }}
                          title={`${formatDate(dia.data)}: ${formatCurrency(dia.saldo_dia)}\nEntradas: ${formatCurrency(dia.entradas)}\nSaídas: ${formatCurrency(dia.saidas)}`}
                          >
                            <div style={{
                              fontSize: '8px',
                              color: 'white',
                              fontWeight: '600',
                              textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                              transform: 'rotate(-90deg)',
                              whiteSpace: 'nowrap',
                              position: 'absolute',
                              bottom: '2px'
                            }}>
                              {Math.abs(dia.saldo_dia) > 1000 ? `${(dia.saldo_dia/1000).toFixed(0)}k` : ''}
                            </div>
                          </div>
                          
                          {/* Data */}
                          <div style={{
                            fontSize: '8px',
                            color: '#6b7280',
                            transform: 'rotate(-45deg)',
                            whiteSpace: 'nowrap',
                            marginTop: '2px'
                          }}>
                            {formatDate(dia.data).substring(0, 5)}
                          </div>
                        </div>
                      );
                    });
                  })()}
                </div>
                
                {/* Legenda */}
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  gap: '20px', 
                  marginTop: '10px',
                  fontSize: '0.75rem'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <div style={{ width: '12px', height: '12px', backgroundColor: '#22c55e', borderRadius: '2px' }}></div>
                    <span style={{ color: '#6b7280' }}>Saldo Positivo</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <div style={{ width: '12px', height: '12px', backgroundColor: '#ef4444', borderRadius: '2px' }}></div>
                    <span style={{ color: '#6b7280' }}>Saldo Negativo</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tabela de Resumo Diário Aprimorada */}
          {resumoDiario.dias && resumoDiario.dias.length > 0 && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              overflow: 'hidden'
            }}>
              <div style={{
                padding: '20px',
                borderBottom: '1px solid #e5e7eb'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
                  📅 Detalhamento por Dia ({resumoDiario.dias.length} dias)
                </h3>
                <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '4px' }}>
                  Análise detalhada do movimento financeiro diário
                </p>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead style={{ backgroundColor: '#f9fafb' }}>
                    <tr>
                      <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Data</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Entradas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saídas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saldo do Dia</th>
                      <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Performance</th>
                      <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Intensidade</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resumoDiario.dias.map((dia, index) => {
                      const isPositive = dia.saldo_dia >= 0;
                      const isWeekend = new Date(dia.data).getDay() === 0 || new Date(dia.data).getDay() === 6;
                      const hasMovement = dia.entradas > 0 || dia.saidas > 0;
                      const maxDayValue = Math.max(...resumoDiario.dias.map(d => Math.abs(d.saldo_dia)));
                      const intensityPercent = maxDayValue > 0 ? (Math.abs(dia.saldo_dia) / maxDayValue) * 100 : 0;
                      
                      return (
                        <tr key={index} style={{ 
                          borderBottom: '1px solid #f3f4f6',
                          backgroundColor: isWeekend ? '#f8fafc' : 'white'
                        }}>
                          <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span>{formatDate(dia.data)}</span>
                              {isWeekend && (
                                <span style={{
                                  fontSize: '0.6rem',
                                  padding: '2px 4px',
                                  backgroundColor: '#e0e7ff',
                                  color: '#3730a3',
                                  borderRadius: '2px',
                                  fontWeight: '500'
                                }}>
                                  FDS
                                </span>
                              )}
                              {!hasMovement && (
                                <span style={{
                                  fontSize: '0.6rem',
                                  padding: '2px 4px',
                                  backgroundColor: '#f3f4f6',
                                  color: '#6b7280',
                                  borderRadius: '2px'
                                }}>
                                  SEM MOV
                                </span>
                              )}
                            </div>
                          </td>
                          <td style={{ 
                            padding: '12px', 
                            textAlign: 'right',
                            fontSize: '0.875rem', 
                            fontWeight: '600',
                            color: dia.entradas > 0 ? '#059669' : '#9ca3af'
                          }}>
                            {dia.entradas > 0 ? formatCurrency(dia.entradas) : '—'}
                          </td>
                          <td style={{ 
                            padding: '12px', 
                            textAlign: 'right',
                            fontSize: '0.875rem', 
                            fontWeight: '600',
                            color: dia.saidas > 0 ? '#dc2626' : '#9ca3af'
                          }}>
                            {dia.saidas > 0 ? formatCurrency(dia.saidas) : '—'}
                          </td>
                          <td style={{ 
                            padding: '12px', 
                            textAlign: 'right',
                            fontSize: '0.875rem', 
                            fontWeight: '700',
                            color: isPositive ? '#059669' : '#dc2626'
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '6px' }}>
                              <span>{formatCurrency(dia.saldo_dia)}</span>
                              <span style={{ fontSize: '0.75rem' }}>
                                {isPositive ? '📈' : '📉'}
                              </span>
                            </div>
                          </td>
                          <td style={{ padding: '12px', textAlign: 'center' }}>
                            <span style={{
                              padding: '4px 8px',
                              borderRadius: '12px',
                              fontSize: '0.75rem',
                              fontWeight: '500',
                              backgroundColor: 
                                !hasMovement ? '#f3f4f6' :
                                isPositive ? (dia.saldo_dia > 0 ? '#dcfce7' : '#f3f4f6') : '#fee2e2',
                              color: 
                                !hasMovement ? '#6b7280' :
                                isPositive ? (dia.saldo_dia > 0 ? '#166534' : '#6b7280') : '#dc2626'
                            }}>
                              {!hasMovement ? 'Neutro' :
                               isPositive ? (dia.saldo_dia > 0 ? 'Positivo' : 'Zero') : 'Negativo'}
                            </span>
                          </td>
                          <td style={{ padding: '12px', textAlign: 'center' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                              <div style={{
                                width: '60px',
                                height: '8px',
                                backgroundColor: '#f3f4f6',
                                borderRadius: '4px',
                                overflow: 'hidden'
                              }}>
                                <div style={{
                                  width: `${intensityPercent}%`,
                                  height: '100%',
                                  backgroundColor: isPositive ? '#22c55e' : '#ef4444',
                                  borderRadius: '4px'
                                }}></div>
                              </div>
                              <span style={{ 
                                fontSize: '0.7rem', 
                                color: '#6b7280', 
                                marginLeft: '8px',
                                minWidth: '30px'
                              }}>
                                {intensityPercent.toFixed(0)}%
                              </span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'mensal' && (
        <div>
          {resumoMensal ? (
            <>
              {/* Resumo Geral do Período */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                <div style={{
                  backgroundColor: 'white',
                  padding: '20px',
                  borderRadius: '8px',
                  borderLeft: '4px solid #10b981',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                    Total de Entradas
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                    {formatCurrency(resumoMensal.totais.total_entradas)}
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
                    Total de Saídas
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                    {formatCurrency(resumoMensal.totais.total_saidas)}
                  </div>
                </div>

                <div style={{
                  backgroundColor: 'white',
                  padding: '20px',
                  borderRadius: '8px',
                  borderLeft: `4px solid ${resumoMensal.totais.saldo_liquido >= 0 ? '#10b981' : '#ef4444'}`,
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                    Saldo Líquido
                  </div>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: '700', 
                    color: resumoMensal.totais.saldo_liquido >= 0 ? '#10b981' : '#ef4444'
                  }}>
                    {formatCurrency(resumoMensal.totais.saldo_liquido)}
                  </div>
                </div>
              </div>

              {/* Tabela de Resumo Mensal */}
              {resumoMensal.meses && resumoMensal.meses.length > 0 && (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    padding: '20px',
                    borderBottom: '1px solid #e5e7eb'
                  }}>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
                      Movimento Mensal ({resumoMensal.meses.length} meses)
                    </h3>
                  </div>

                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead style={{ backgroundColor: '#f9fafb' }}>
                        <tr>
                          <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Mês</th>
                          <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Entradas</th>
                          <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saídas</th>
                          <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saldo do Mês</th>
                        </tr>
                      </thead>
                      <tbody>
                        {resumoMensal.meses.map((mes, index) => (
                          <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                            <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                              {mes.mes}
                            </td>
                            <td style={{ 
                              padding: '12px', 
                              textAlign: 'right',
                              fontSize: '0.875rem', 
                              fontWeight: '600',
                              color: '#059669'
                            }}>
                              {formatCurrency(mes.entradas)}
                            </td>
                            <td style={{ 
                              padding: '12px', 
                              textAlign: 'right',
                              fontSize: '0.875rem', 
                              fontWeight: '600',
                              color: '#dc2626'
                            }}>
                              {formatCurrency(mes.saidas)}
                            </td>
                            <td style={{ 
                              padding: '12px', 
                              textAlign: 'right',
                              fontSize: '0.875rem', 
                              fontWeight: '700',
                              color: mes.saldo_mes >= 0 ? '#059669' : '#dc2626'
                            }}>
                              {formatCurrency(mes.saldo_mes)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div style={{
              backgroundColor: '#fff3cd',
              border: '1px solid #ffeaa7',
              borderRadius: '8px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <h3 style={{ color: '#856404', marginBottom: '8px' }}>Dados Mensais Indisponíveis</h3>
              <p style={{ color: '#6c5400', margin: 0 }}>
                O endpoint de resumo mensal apresenta problemas técnicos no backend. 
                Por favor, utilize as outras abas para visualizar os dados.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FluxoCaixaDashboard;
