import React, { useState, useCallback, useEffect } from 'react';

// Interfaces para os dados dos endpoints
interface PeriodoInfo {
  inicio: string;
  fim: string;
}

interface Totalizadores {
  entradas_realizadas: number | string;
  saidas_realizadas: number | string;
  entradas_previstas: number | string;
  saidas_previstas: number | string;
}

interface SemanaInfo {
  semana: number;
  dias: DiaInfo[];
  total_entradas: number;
  total_saidas: number;
  saldo_realizado: number;
  saldo_projetado: number;
}

interface DiaInfo {
  data: string;
  entradas: number;
  saidas: number;
  saldo: number;
}

interface MesInfo {
  mes: string;
  ano: number;
  semanas: SemanaInfo[];
  total_entradas: number | string;
  total_saidas: number | string;
  saldo_realizado: number | string;
  saldo_projetado: number | string;
}

interface DashboardData {
  periodo: PeriodoInfo;
  saldo_inicial: number | string;
  saldo_final_realizado: number | string;
  saldo_final_projetado: number | string;
  meses: MesInfo[];
  totalizadores: Totalizadores;
}

interface LiquidezInfo {
  indice: string;
  saldo_atual: number;
  contas_receber: number;
  contas_pagar: number;
}

interface VariacaoMensal {
  receitas: number;
  despesas: number;
}

interface MesAtual {
  receitas: number;
  despesas: number;
  resultado: number;
}

interface MaiorDespesa {
  categoria: string;
  valor: number;
  percentual: number;
}

interface MaiorCliente {
  cliente: string;
  valor: number;
  percentual: number;
}

interface IndicadoresData {
  data_calculo: string;
  liquidez: LiquidezInfo;
  variacao_mensal: VariacaoMensal;
  maiores_despesas: MaiorDespesa[];
  maiores_clientes: MaiorCliente[];
  mes_atual: MesAtual;
}

interface AlertaItem {
  tipo: string;
  severidade: string;
  mensagem: string;
  recomendacao: string;
}

interface AlertasData {
  data_analise: string;
  quantidade_alertas: number;
  alertas: AlertaItem[];
}

interface ComparativoMensal {
  mes: string;
  ano: number;
  receitas: number;
  despesas: number;
  resultado: number;
}

interface ProjecaoMes {
  mes: string;
  saldo_inicial: number;
  entradas_previstas: number;
  saidas_previstas: number;
  saldo_final: number;
}

interface ProjecaoFluxo {
  data_base: string;
  periodo_projecao: string;
  projecao: ProjecaoMes[];
}

interface RelatorioDRE {
  periodo: PeriodoInfo;
  resultados: {
    receita_bruta: number;
    custos_produtos: number;
    lucro_bruto: number;
    margem_bruta_percentual: number;
    despesas_operacionais: number;
    resultado_operacional: number;
    margem_liquida_percentual: number;
  };
  detalhamento: {
    receitas: CategoriaDRE[];
    despesas: CategoriaDRE[];
  };
  analise_produtos: {
    periodo: PeriodoInfo;
    totais: MetricasRelevantes;
    produtos: ProdutoAnalise[];
    metricas_relevantes: MetricasRelevantes;
  };
  indicadores: {
    giro_estoque: number;
    prazo_medio_pagamento: number;
    prazo_medio_recebimento: number;
  };
}

interface CategoriaDRE {
  categoria: string;
  valor: number;
  percentual: number;
}

interface Tendencia {
  periodo: string;
  indicador: string;
  valor: number;
  variacao: number;
}

interface ProdutoAnalise {
  produto: string;
  receita: number;
  custo: number;
  margem: number;
}

interface MetricasRelevantes {
  produto_mais_rentavel: string;
  produto_maior_volume: string;
  margem_media: number;
}

interface EstativicasData {
  periodo: PeriodoInfo;
  resumo_geral: {
    receitas_totais: number;
    despesas_totais: number;
    resultado_liquido: number;
    margem_lucro: number;
  };
  comparativo_mensal: ComparativoMensal[];
  tendencias: Tendencia[];
}

interface FluxoLucroDashboardProps {
  dataInicio: string;
  dataFim: string;
}

const FluxoLucroDashboard: React.FC<FluxoLucroDashboardProps> = ({ dataInicio, dataFim }) => {
  // Estados para os dados
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [indicadoresData, setIndicadoresData] = useState<IndicadoresData | null>(null);
  const [alertasData, setAlertasData] = useState<AlertasData | null>(null);
  const [estatisticasData, setEstatisticasData] = useState<EstativicasData | null>(null);
  const [projecaoData, setProjecaoData] = useState<ProjecaoFluxo | null>(null);
  const [dreData, setDreData] = useState<RelatorioDRE | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Função para formatar valores monetários
  const formatCurrency = (value: number | string): string => {
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(numValue || 0);
  };

  // Função para converter número do mês para nome
  const getMonthName = (mesString: string): string => {
    const monthNames = [
      'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];

    // Se já é um nome de mês, retorna como está
    if (isNaN(Number(mesString))) {
      return mesString;
    }

    // Se é um número, converte para nome
    const mesNumero = parseInt(mesString);
    if (mesNumero >= 1 && mesNumero <= 12) {
      return monthNames[mesNumero - 1];
    }

    return mesString; // Retorna o valor original se não conseguir converter
  };

  // Função para obter todas as semanas de todos os meses
  const obterTodasSemanas = (meses: MesInfo[]): SemanaInfo[] => {
    const todasSemanas: SemanaInfo[] = [];

    meses.forEach(mes => {
      mes.semanas.forEach(semana => {
        todasSemanas.push(semana);
      });
    });

    return todasSemanas;
  };

  // Função para formatar período da semana
  const formatarPeriodoSemana = (semana: SemanaInfo): string => {
    const dataInicio = new Date(semana.dias[0]?.data || '');
    const dataFim = new Date(semana.dias[semana.dias.length - 1]?.data || '');

    const formatarData = (data: Date): string => {
      return data.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit'
      });
    };

    return `${formatarData(dataInicio)} - ${formatarData(dataFim)}`;
  };

  // Função para converter string para número
  const parseValue = (value: number | string): number => {
    if (typeof value === 'string') {
      return parseFloat(value) || 0;
    }
    return value || 0;
  };

  // Função para formatar data
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  // Função para carregar os dados
  const carregarDados = useCallback(async () => {
    setLoading(true);
    setError(null);

    // Evita requisições com dados indefinidos
    if (!dataInicio || !dataFim || dataInicio === 'undefined' || dataFim === 'undefined') {
      setLoading(false);
      return;
    }

    try {
      const params = `?data_inicial=${dataInicio}&data_final=${dataFim}`;
      const [dashboardRes, indicadoresRes, alertasRes, estatisticasRes, projecaoRes, dreRes] = await Promise.all([
        fetch(`http://127.0.0.1:8000/api/fluxo-caixa-lucro/dashboard/${params}`),
        fetch(`http://127.0.0.1:8000/api/fluxo-caixa-lucro/indicadores/${params}`),
        fetch(`http://127.0.0.1:8000/api/fluxo-caixa-lucro/alertas_inteligentes/${params}`),
        fetch(`http://127.0.0.1:8000/api/fluxo-caixa-lucro/estatisticas/${params}`),
        fetch(`http://127.0.0.1:8000/api/fluxo-caixa-lucro/projecao_fluxo/${params}`),
        fetch(`http://127.0.0.1:8000/api/fluxo-caixa-lucro/relatorio_dre/${params}`)
      ]);

      if (!dashboardRes.ok || !indicadoresRes.ok || !alertasRes.ok || !estatisticasRes.ok || !projecaoRes.ok || !dreRes.ok) {
        throw new Error('Erro ao carregar dados dos endpoints');
      }

      const [dashboard, indicadores, alertas, estatisticas, projecao, dre] = await Promise.all([
        dashboardRes.json(),
        indicadoresRes.json(),
        alertasRes.json(),
        estatisticasRes.json(),
        projecaoRes.json(),
        dreRes.json()
      ]);

      setDashboardData(dashboard);
      setIndicadoresData(indicadores);
      setAlertasData(alertas);
      setEstatisticasData(estatisticas);
      setProjecaoData(projecao);
      setDreData(dre);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [dataInicio, dataFim]);

  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '400px',
        fontSize: '1.1rem',
        color: '#6b7280'
      }}>
        🔄 Carregando dados de Fluxo de Caixa Previsto...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        backgroundColor: '#fee2e2',
        border: '1px solid #fca5a5',
        borderRadius: '8px',
        padding: '16px',
        margin: '20px',
        color: '#dc2626'
      }}>
        ❌ Erro: {error}
        <button
          onClick={carregarDados}
          style={{
            marginLeft: '10px',
            padding: '4px 8px',
            backgroundColor: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: '700',
          color: '#111827',
          margin: '0 0 8px 0'
        }}>
          💰 Dashboard de Fluxo de Caixa Previsto
        </h1>
        <p style={{
          fontSize: '1rem',
          color: '#6b7280',
          margin: 0
        }}>
          Análise completa de performance financeira e projeções de fluxo de caixa
        </p>
      </div>

      {/* Navegação por Tabs */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '24px',
        borderBottom: '2px solid #e5e7eb'
      }}>
        {[
          { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
          { id: 'indicadores', label: '📈 Indicadores', icon: '📈' },
          { id: 'alertas', label: '🚨 Alertas', icon: '🚨' },
          { id: 'estatisticas', label: '📋 Estatísticas', icon: '📋' },
          { id: 'projecao', label: '🔮 Projeção', icon: '🔮' },
          { id: 'dre', label: '💼 DRE', icon: '💼' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '12px 20px',
              border: 'none',
              backgroundColor: activeTab === tab.id ? '#3b82f6' : 'transparent',
              color: activeTab === tab.id ? 'white' : '#6b7280',
              borderRadius: '8px 8px 0 0',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && dashboardData && (
        <div>
          {/* Alerta quando não há dados */}
          {parseValue(dashboardData.saldo_inicial) === 0 &&
            parseValue(dashboardData.totalizadores.entradas_realizadas) === 0 &&
            parseValue(dashboardData.totalizadores.saidas_realizadas) === 0 && (
              <div style={{
                backgroundColor: '#fffbeb',
                border: '1px solid #f59e0b',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '24px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <span style={{ fontSize: '1.5rem' }}>ℹ️</span>
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#92400e' }}>
                    Período sem dados financeiros
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#78350f', marginTop: '2px' }}>
                    O período atual ({formatDate(dashboardData.periodo.inicio)} - {formatDate(dashboardData.periodo.fim)}) não possui movimentações registradas.
                    Para ver dados reais, selecione um período com transações financeiras.
                  </div>
                </div>
              </div>
            )}

          {/* Cards de Resumo */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: '4px solid #10b981',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                💰 Saldo Inicial
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(parseValue(dashboardData.saldo_inicial))}
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
                ✅ Saldo Realizado
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(parseValue(dashboardData.saldo_final_realizado))}
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
                🔮 Saldo Projetado
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(parseValue(dashboardData.saldo_final_projetado))}
              </div>
            </div>
          </div>

          {/* Totalizadores */}
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
              💼 Totalizadores do Período
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#166534', fontWeight: '500' }}>
                  📈 Entradas Realizadas
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#15803d', marginTop: '4px' }}>
                  {formatCurrency(parseValue(dashboardData.totalizadores.entradas_realizadas))}
                </div>
                {parseValue(dashboardData.totalizadores.entradas_realizadas) === 0 && (
                  <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '2px' }}>
                    Sem entradas no período
                  </div>
                )}
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fef2f2', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#dc2626', fontWeight: '500' }}>
                  📉 Saídas Realizadas
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#dc2626', marginTop: '4px' }}>
                  {formatCurrency(parseValue(dashboardData.totalizadores.saidas_realizadas))}
                </div>
                {parseValue(dashboardData.totalizadores.saidas_realizadas) === 0 && (
                  <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '2px' }}>
                    Sem saídas no período
                  </div>
                )}
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#eff6ff', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#2563eb', fontWeight: '500' }}>
                  🔮 Entradas Previstas
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#2563eb', marginTop: '4px' }}>
                  {formatCurrency(parseValue(dashboardData.totalizadores.entradas_previstas))}
                </div>
                {parseValue(dashboardData.totalizadores.entradas_previstas) === 0 && (
                  <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '2px' }}>
                    Sem previsões de entrada
                  </div>
                )}
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fdf4ff', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#7c3aed', fontWeight: '500' }}>
                  🔮 Saídas Previstas
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#7c3aed', marginTop: '4px' }}>
                  {formatCurrency(parseValue(dashboardData.totalizadores.saidas_previstas))}
                </div>
                {parseValue(dashboardData.totalizadores.saidas_previstas) === 0 && (
                  <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '2px' }}>
                    Sem previsões de saída
                  </div>
                )}
              </div>
            </div>

            {/* Resumo Consolidado */}
            {(parseValue(dashboardData.totalizadores.entradas_realizadas) > 0 ||
              parseValue(dashboardData.totalizadores.saidas_realizadas) > 0) && (
                <div style={{
                  marginTop: '20px',
                  padding: '16px',
                  backgroundColor: '#f8fafc',
                  borderRadius: '8px',
                  borderLeft: '4px solid #3b82f6'
                }}>
                  <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    📊 Resumo Consolidado
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Resultado Realizado</div>
                      <div style={{
                        fontSize: '1rem',
                        fontWeight: '700',
                        color: (parseValue(dashboardData.totalizadores.entradas_realizadas) - parseValue(dashboardData.totalizadores.saidas_realizadas)) >= 0 ? '#10b981' : '#ef4444'
                      }}>
                        {formatCurrency(parseValue(dashboardData.totalizadores.entradas_realizadas) - parseValue(dashboardData.totalizadores.saidas_realizadas))}
                      </div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Resultado Previsto</div>
                      <div style={{
                        fontSize: '1rem',
                        fontWeight: '700',
                        color: (parseValue(dashboardData.totalizadores.entradas_previstas) - parseValue(dashboardData.totalizadores.saidas_previstas)) >= 0 ? '#3b82f6' : '#7c3aed'
                      }}>
                        {formatCurrency(parseValue(dashboardData.totalizadores.entradas_previstas) - parseValue(dashboardData.totalizadores.saidas_previstas))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
          </div>

          {/* Resumo por Mês */}
          {dashboardData.meses && dashboardData.meses.length > 0 && (
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
                  📅 Resumo Semanal ({obterTodasSemanas(dashboardData.meses).length} semanas)
                </h3>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead style={{ backgroundColor: '#f9fafb' }}>
                    <tr>
                      <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Período</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Entradas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saídas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saldo Realizado</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saldo Projetado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {obterTodasSemanas(dashboardData.meses).map((semana, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                        <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                          {formatarPeriodoSemana(semana)}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: '#059669'
                        }}>
                          {formatCurrency(parseValue(semana.total_entradas))}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: '#dc2626'
                        }}>
                          {formatCurrency(parseValue(semana.total_saidas))}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '700',
                          color: parseValue(semana.saldo_realizado) >= 0 ? '#059669' : '#dc2626'
                        }}>
                          {formatCurrency(parseValue(semana.saldo_realizado))}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '700',
                          color: parseValue(semana.saldo_projetado) >= 0 ? '#3b82f6' : '#7c3aed'
                        }}>
                          {formatCurrency(parseValue(semana.saldo_projetado))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Indicadores Tab */}
      {activeTab === 'indicadores' && indicadoresData && (
        <div>
          {/* Cards de Indicadores */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: '4px solid #f59e0b',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                💧 Índice de Liquidez
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {indicadoresData.liquidez.indice || 'N/A'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#f59e0b', marginTop: '4px' }}>
                Saldo: {formatCurrency(indicadoresData.liquidez.saldo_atual)}
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
                📈 Receitas do Mês
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(indicadoresData.mes_atual.receitas)}
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
                📉 Despesas do Mês
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(indicadoresData.mes_atual.despesas)}
              </div>
            </div>

            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: `4px solid ${indicadoresData.mes_atual.resultado >= 0 ? '#10b981' : '#ef4444'}`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                💰 Resultado do Mês
              </div>
              <div style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: indicadoresData.mes_atual.resultado >= 0 ? '#10b981' : '#ef4444'
              }}>
                {formatCurrency(indicadoresData.mes_atual.resultado)}
              </div>
            </div>
          </div>

          {/* Detalhes de Liquidez */}
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
              💧 Análise de Liquidez
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#166534', fontWeight: '500' }}>
                  💰 Contas a Receber
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#15803d', marginTop: '4px' }}>
                  {formatCurrency(indicadoresData.liquidez.contas_receber)}
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fef2f2', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#dc2626', fontWeight: '500' }}>
                  💳 Contas a Pagar
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#dc2626', marginTop: '4px' }}>
                  {formatCurrency(indicadoresData.liquidez.contas_pagar)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alertas Tab */}
      {activeTab === 'alertas' && alertasData && (
        <div>
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
              🚨 Alertas Inteligentes ({alertasData.quantidade_alertas})
            </h3>
            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '16px' }}>
              Análise realizada em: {formatDate(alertasData.data_analise)}
            </p>

            {alertasData.alertas && alertasData.alertas.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {alertasData.alertas.map((alerta, index) => (
                  <div key={index} style={{
                    padding: '16px',
                    borderRadius: '8px',
                    borderLeft: `4px solid ${alerta.severidade === 'alta' ? '#ef4444' :
                      alerta.severidade === 'media' ? '#f59e0b' : '#10b981'
                      }`,
                    backgroundColor:
                      alerta.severidade === 'alta' ? '#fef2f2' :
                        alerta.severidade === 'media' ? '#fffbeb' : '#f0fdf4'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <span style={{ fontSize: '1.25rem' }}>
                        {alerta.severidade === 'alta' ? '🔴' :
                          alerta.severidade === 'media' ? '🟡' : '🟢'}
                      </span>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        textTransform: 'uppercase',
                        color:
                          alerta.severidade === 'alta' ? '#dc2626' :
                            alerta.severidade === 'media' ? '#d97706' : '#059669'
                      }}>
                        {alerta.tipo.replace('_', ' ')} - {alerta.severidade}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#374151', marginBottom: '8px' }}>
                      {alerta.mensagem}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', fontStyle: 'italic' }}>
                      💡 {alerta.recomendacao}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
                ✅ Nenhum alerta no momento
              </div>
            )}
          </div>
        </div>
      )}

      {/* Estatísticas Tab */}
      {activeTab === 'estatisticas' && estatisticasData && (
        <div>
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
              📋 Estatísticas Gerais
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#166534', fontWeight: '500' }}>
                  💰 Receitas Totais
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#15803d', marginTop: '4px' }}>
                  {formatCurrency(estatisticasData.resumo_geral?.receitas_totais || 0)}
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fef2f2', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#dc2626', fontWeight: '500' }}>
                  💸 Despesas Totais
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#dc2626', marginTop: '4px' }}>
                  {formatCurrency(estatisticasData.resumo_geral?.despesas_totais || 0)}
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#eff6ff', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#2563eb', fontWeight: '500' }}>
                  📊 Resultado Líquido
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#2563eb', marginTop: '4px' }}>
                  {formatCurrency(estatisticasData.resumo_geral?.resultado_liquido || 0)}
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fdf4ff', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#7c3aed', fontWeight: '500' }}>
                  📈 Margem de Lucro
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#7c3aed', marginTop: '4px' }}>
                  {((estatisticasData.resumo_geral?.margem_lucro || 0) * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Projeção Tab */}
      {activeTab === 'projecao' && projecaoData && (
        <div>
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
              🔮 Projeção de Fluxo de Caixa - {projecaoData.periodo_projecao}
            </h3>
            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '16px' }}>
              Base de cálculo: {formatDate(projecaoData.data_base)}
            </p>

            {projecaoData.projecao && projecaoData.projecao.length > 0 && (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead style={{ backgroundColor: '#f9fafb' }}>
                    <tr>
                      <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Mês</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saldo Inicial</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Entradas Previstas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saídas Previstas</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saldo Final</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projecaoData.projecao.map((mes, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                        <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                          {getMonthName(mes.mes)}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          color: '#6b7280'
                        }}>
                          {formatCurrency(mes.saldo_inicial)}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: '#059669'
                        }}>
                          {formatCurrency(mes.entradas_previstas)}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: '#dc2626'
                        }}>
                          {formatCurrency(mes.saidas_previstas)}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '700',
                          color: mes.saldo_final >= 0 ? '#059669' : '#dc2626'
                        }}>
                          {formatCurrency(mes.saldo_final)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* DRE Tab */}
      {activeTab === 'dre' && dreData && (
        <div>
          {/* Resumo dos Resultados */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: '4px solid #10b981',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                💰 Receita Bruta
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(dreData.resultados.receita_bruta)}
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
                📊 Lucro Bruto
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(dreData.resultados.lucro_bruto)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#3b82f6', marginTop: '4px' }}>
                {dreData.resultados.margem_bruta_percentual.toFixed(1)}% margem
              </div>
            </div>

            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: `4px solid ${dreData.resultados.resultado_operacional >= 0 ? '#10b981' : '#ef4444'}`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                ⚡ Resultado Operacional
              </div>
              <div style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: dreData.resultados.resultado_operacional >= 0 ? '#10b981' : '#ef4444'
              }}>
                {formatCurrency(dreData.resultados.resultado_operacional)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
                {dreData.resultados.margem_liquida_percentual.toFixed(1)}% margem líquida
              </div>
            </div>
          </div>

          {/* Indicadores Operacionais */}
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
              📈 Indicadores Operacionais
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#166534', fontWeight: '500' }}>
                  🔄 Giro do Estoque
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#15803d', marginTop: '4px' }}>
                  {dreData.indicadores.giro_estoque.toFixed(1)}x
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#eff6ff', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#2563eb', fontWeight: '500' }}>
                  📅 Prazo Médio Recebimento
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#2563eb', marginTop: '4px' }}>
                  {dreData.indicadores.prazo_medio_recebimento} dias
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fef2f2', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#dc2626', fontWeight: '500' }}>
                  📅 Prazo Médio Pagamento
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#dc2626', marginTop: '4px' }}>
                  {dreData.indicadores.prazo_medio_pagamento} dias
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FluxoLucroDashboard;
