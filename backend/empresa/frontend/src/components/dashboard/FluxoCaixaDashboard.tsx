import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { formatCurrency, formatDate } from '../../services/dashboard-service';

// Interfaces para os diferentes endpoints
interface MovimentacaoRealizada {
  id: string;
  tipo: 'entrada' | 'saida';
  data: string;
  valor: number;
  contraparte: string;
  historico: string;
  forma_pagamento: string;
  origem: 'contas_receber' | 'contas_pagar';
}

interface MovimentacaoPrevista {
  id: string;
  tipo: 'entrada_prevista' | 'saida_prevista';
  data_vencimento: string;
  valor: number;
  contraparte: string;
  historico: string;
  dias_para_vencimento: number;
  status: 'no_prazo' | 'urgente' | 'vencido';
}

// EstatisticasVencimento interface removed - simplified backend no longer provides this data

interface ResumoFluxo {
  total_entradas: number;
  total_saidas: number;
  saldo_liquido: number;
  total_movimentacoes?: number;
}

interface ResumoPrevisto {
  total_entradas_previstas: number;
  total_saidas_previstas: number;
  saldo_previsto: number;

  count_periodo: number;

  total_entradas_antes: number;
  total_saidas_antes: number;
  count_antes: number;

  total_entradas_depois: number;
  total_saidas_depois: number;
  count_depois: number;

  total_movimentacoes: number;
}

interface Paginacao {
  page: number;
  page_size: number;
  total_pages: number;
  total_count: number;
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

// Componente de Filtro Checkbox
const FilterCheckboxList: React.FC<{
  title: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  maxHeight?: string;
}> = ({ title, options, selected, onChange, maxHeight = '200px' }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredOptions = options.filter(opt =>
    opt && String(opt).toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleOption = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter(item => item !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  const toggleAll = () => {
    if (selected.length === options.length) {
      onChange([]);
    } else {
      onChange([...options]);
    }
  };

  return (
    <div style={{ marginBottom: '16px', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '12px', backgroundColor: '#f9fafb' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', margin: 0 }}>{title}</h4>
        <button
          onClick={toggleAll}
          style={{ fontSize: '0.75rem', color: '#3b82f6', background: 'none', border: 'none', cursor: 'pointer' }}
        >
          {selected.length === options.length ? 'Limpar' : 'Todos'}
        </button>
      </div>

      <input
        type="text"
        placeholder="Buscar..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{
          width: '100%',
          padding: '6px',
          marginBottom: '8px',
          fontSize: '0.75rem',
          border: '1px solid #d1d5db',
          borderRadius: '4px'
        }}
      />

      <div style={{ maxHeight, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {filteredOptions.map(option => (
          <label key={option} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', cursor: 'pointer', padding: '2px 0' }}>
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={() => toggleOption(option)}
              style={{ borderRadius: '4px' }}
            />
            <span style={{ color: '#4b5563' }}>{option}</span>
          </label>
        ))}
        {filteredOptions.length === 0 && (
          <div style={{ fontSize: '0.75rem', color: '#9ca3af', fontStyle: 'italic' }}>Nenhuma opção encontrada</div>
        )}
      </div>

      {selected.length > 0 && (
        <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#6b7280' }}>
          {selected.length} selecionados
        </div>
      )}
    </div>
  );
};

interface FluxoCaixaDashboardProps {
  dataInicio: string;
  dataFim: string;
}

const FluxoCaixaDashboard: React.FC<FluxoCaixaDashboardProps> = ({ dataInicio, dataFim }) => {
  // Estados para dados
  const [movimentacoesRealizadas, setMovimentacoesRealizadas] = useState<MovimentacaoRealizada[]>([]);
  const [movimentacoesPrevistas, setMovimentacoesPrevistas] = useState<MovimentacaoPrevista[]>([]);
  const [resumoDiario, setResumoDiario] = useState<ResumoDiario | null>(null);
  const [resumoMensal, setResumoMensal] = useState<ResumoMensal | null>(null);
  const [resumoRealizadas, setResumoRealizadas] = useState<ResumoFluxo | null>(null);
  const [resumoPrevisto, setResumoPrevisto] = useState<ResumoPrevisto | null>(null);
  const [viewScope, setViewScope] = useState<'antes' | 'periodo' | 'depois'>('periodo');
  // Estados removidos: estatisticasVencimento, movimentacoesAbertas, resumoAbertas, clientesContrato

  // Estados de paginação
  const [paginacaoRealizadas, setPaginacaoRealizadas] = useState<Paginacao | null>(null);
  const [paginacaoPrevistas, setPaginacaoPrevistas] = useState<Paginacao | null>(null);
  const [pageRealizadas, setPageRealizadas] = useState(1);
  const [pagePrevistas, setPagePrevistas] = useState(1);
  const PAGE_SIZE = 50;

  // Fallback: agrega resumo mensal localmente
  const resumoMensalFallback = useMemo(() => {
    const map = new Map<string, { entradas: number; saidas: number }>();
    for (const m of movimentacoesRealizadas) {
      if (!m.data) continue;
      // Use string parsing to avoid timezone issues
      const key = m.data.substring(0, 7); // YYYY-MM
      if (!map.has(key)) map.set(key, { entradas: 0, saidas: 0 });
      const agg = map.get(key)!;
      if (m.tipo === 'entrada') agg.entradas += m.valor; else if (m.tipo === 'saida') agg.saidas += m.valor;
    }

    const meses = Array.from(map.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, v]) => ({ mes: key, entradas: v.entradas, saidas: v.saidas, saldo_mes: v.entradas - v.saidas }));

    const totais = meses.reduce((acc, m) => {
      acc.total_entradas += m.entradas;
      acc.total_saidas += m.saidas;
      acc.saldo_liquido += (m.entradas - m.saidas);
      return acc;
    }, { total_entradas: 0, total_saidas: 0, saldo_liquido: 0 });

    return { meses, totais };
  }, [movimentacoesRealizadas]);

  // Estados para controle
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'realizadas' | 'abertas' | 'diario' | 'mensal'>('realizadas');

  // Estados para filtros


  // Filtros Multi-select
  const [selectedSpecsPagar, setSelectedSpecsPagar] = useState<string[]>([]);
  const [selectedSpecsReceber, setSelectedSpecsReceber] = useState<string[]>([]);
  const [selectedOrigemReceita, setSelectedOrigemReceita] = useState<string[]>([]);

  const [optionsSpecsPagar, setOptionsSpecsPagar] = useState<string[]>([]);
  const [optionsSpecsReceber, setOptionsSpecsReceber] = useState<string[]>([]);

  // Carregar opções de filtro
  useEffect(() => {
    console.log('Fetching filters...');
    fetch('http://127.0.0.1:8000/api/fluxo-caixa-realizado/filtros/')
      .then(res => res.json())
      .then(data => {
        console.log('Filters received:', data);
        if (data.especificacoes_pagar) setOptionsSpecsPagar(data.especificacoes_pagar);
        if (data.especificacoes_receber) setOptionsSpecsReceber(data.especificacoes_receber);
      })
      .catch(err => console.error('Erro ao carregar filtros:', err));
  }, []);

  // Função para buscar dados de todas as APIs
  const loadData = useCallback(async (realizadasPage = 1, previstasPage = 1) => {
    try {
      setLoading(true);
      setError(null);

      const baseUrl = 'http://127.0.0.1:8000/api/fluxo-caixa-realizado';
      const baseParams = `?data_inicio=${dataInicio}&data_fim=${dataFim}&page_size=${PAGE_SIZE}`;

      const specsPagarParam = selectedSpecsPagar.length > 0 ? `&especificacao_pagar=${selectedSpecsPagar.join(',')}` : '';
      const specsReceberParam = selectedSpecsReceber.length > 0 ? `&especificacao_receber=${selectedSpecsReceber.join(',')}` : '';
      const origemParam = selectedOrigemReceita.length > 0 ? `&origem_receita=${selectedOrigemReceita.join(',')}` : '';

      const filterParams = `${baseParams}${specsPagarParam}${specsReceberParam}${origemParam}`;

      const [realizadasRes, previstasRes, diarioRes] = await Promise.all([
        fetch(`${baseUrl}/movimentacoes_realizadas/${filterParams}&page=${realizadasPage}`),
        fetch(`${baseUrl}/movimentacoes_previstas/${filterParams}&page=${previstasPage}&scope=${viewScope}`),
        fetch(`${baseUrl}/resumo_diario/${baseParams}`)
      ]);

      if (!realizadasRes.ok || !previstasRes.ok || !diarioRes.ok) {
        throw new Error('Erro ao carregar dados dos endpoints');
      }

      const realizadasData = await realizadasRes.json();
      const previstasData = await previstasRes.json();
      const diarioData = await diarioRes.json();

      // Processar dados realizadas
      setMovimentacoesRealizadas(realizadasData.movimentacoes || []);
      setResumoRealizadas(realizadasData.resumo);
      setPaginacaoRealizadas(realizadasData.paginacao || null);
      setPageRealizadas(realizadasPage);

      // Processar dados previstos
      setResumoPrevisto(previstasData.resumo);
      setMovimentacoesPrevistas(previstasData.movimentacoes || []);
      setPaginacaoPrevistas(previstasData.paginacao || null);
      setPagePrevistas(previstasPage);

      // Processar dados diários
      setResumoDiario(diarioData);

      // Tentar carregar dados mensais (pode dar erro no backend)
      try {
        const mensalRes = await fetch(`${baseUrl}/resumo_mensal/${baseParams}`);
        if (mensalRes.ok) {
          const mensalData = await mensalRes.json();
          setResumoMensal(mensalData);
        }
      } catch (err) {
        console.warn('Erro ao carregar dados mensais:', err);
      }

      // Removed: Busca de clientes com contrato - backend simplificado não usa mais

    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setError('Erro ao carregar dados do fluxo de caixa');
    } finally {
      setLoading(false);
    }
  }, [dataInicio, dataFim, PAGE_SIZE, selectedSpecsPagar, selectedSpecsReceber, selectedOrigemReceita, viewScope]);

  useEffect(() => {
    loadData();
  }, [dataInicio, dataFim, selectedSpecsPagar, selectedSpecsReceber, selectedOrigemReceita, viewScope, loadData]);






  if (error) {
    return (
      <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '16px', margin: '16px' }}>
        <div style={{ color: '#dc2626', fontWeight: '600' }}>Erro:</div>
        <div style={{ color: '#7f1d1d', marginTop: '4px' }}>{error}</div>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '20px',
      opacity: loading ? 0.6 : 1,
      pointerEvents: loading ? 'none' : 'auto',
      transition: 'opacity 0.2s ease-in-out'
    }}>
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

      {/* Layout com Sidebar e Tabela */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(250px, 1fr) 3fr', gap: '24px', alignItems: 'start' }}>

        {/* Sidebar de Filtros (Global) */}
        <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#111827', marginBottom: '16px', borderBottom: '1px solid #e5e7eb', paddingBottom: '8px' }}>
            Filtros Avançados
          </h3>

          <FilterCheckboxList
            title={`Especificação (Pagar) [${optionsSpecsPagar.length}]`}
            options={optionsSpecsPagar}
            selected={selectedSpecsPagar}
            onChange={setSelectedSpecsPagar}
          />

          <FilterCheckboxList
            title={`Especificação (Receber) [${optionsSpecsReceber.length}]`}
            options={optionsSpecsReceber}
            selected={selectedSpecsReceber}
            onChange={setSelectedSpecsReceber}
          />

          <div style={{ marginTop: '16px', borderTop: '1px solid #e5e7eb', paddingTop: '16px' }}>
            <FilterCheckboxList
              title="Origem (Receber)"
              options={['CONTRATO', 'VENDA']}
              selected={selectedOrigemReceita}
              onChange={setSelectedOrigemReceita}
            />
          </div>
        </div>

        {/* Conteúdo Principal */}
        <div style={{ minWidth: 0 }}>
          {activeTab === 'realizadas' && (
            <div>
              {/* Legacy breakdown cards removed - simplified backend no longer provides cliente_id/tipo_custo */}
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
                            {formatDate(mov.data)}
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

                  {/* Paginação Realizadas */}
                  {paginacaoRealizadas && paginacaoRealizadas.total_pages > 1 && (
                    <div style={{
                      padding: '16px',
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      gap: '12px',
                      borderTop: '1px solid #e5e7eb'
                    }}>
                      <button
                        onClick={() => loadData(pageRealizadas - 1, pagePrevistas)}
                        disabled={pageRealizadas <= 1}
                        style={{
                          padding: '8px 16px',
                          backgroundColor: pageRealizadas <= 1 ? '#e5e7eb' : '#3b82f6',
                          color: pageRealizadas <= 1 ? '#9ca3af' : 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: pageRealizadas <= 1 ? 'not-allowed' : 'pointer',
                          fontSize: '0.875rem',
                          fontWeight: '500'
                        }}
                      >
                        ← Anterior
                      </button>
                      <span style={{ fontSize: '0.875rem', color: '#374151' }}>
                        Página {paginacaoRealizadas.page} de {paginacaoRealizadas.total_pages}
                        {' '}({paginacaoRealizadas.total_count} movimentações)
                      </span>
                      <button
                        onClick={() => loadData(pageRealizadas + 1, pagePrevistas)}
                        disabled={pageRealizadas >= paginacaoRealizadas.total_pages}
                        style={{
                          padding: '8px 16px',
                          backgroundColor: pageRealizadas >= paginacaoRealizadas.total_pages ? '#e5e7eb' : '#3b82f6',
                          color: pageRealizadas >= paginacaoRealizadas.total_pages ? '#9ca3af' : 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: pageRealizadas >= paginacaoRealizadas.total_pages ? 'not-allowed' : 'pointer',
                          fontSize: '0.875rem',
                          fontWeight: '500'
                        }}
                      >
                        Próxima →
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'abertas' && (
            <div>
              {/* Resumo das Movimentações Abertas */}
              {resumoPrevisto && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                  <div
                    onClick={() => setViewScope('antes')}
                    style={{
                      backgroundColor: 'white',
                      padding: '20px',
                      borderRadius: '8px',
                      borderLeft: '4px solid #ef4444',
                      boxShadow: viewScope === 'antes' ? '0 0 0 2px #ef4444, 0 4px 6px rgba(0,0,0,0.1)' : '0 1px 3px rgba(0,0,0,0.1)',
                      cursor: 'pointer',
                      opacity: viewScope === 'antes' ? 1 : 0.7,
                      transition: 'all 0.2s ease-in-out',
                      transform: viewScope === 'antes' ? 'scale(1.02)' : 'scale(1)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>
                        Anteriores ao Período
                      </div>
                      <div style={{ fontSize: '0.75rem', backgroundColor: '#fee2e2', color: '#b91c1c', padding: '2px 8px', borderRadius: '9999px', fontWeight: '600' }}>
                        {resumoPrevisto.count_antes || 0}
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#059669' }}>
                        <span>Entradas:</span>
                        <span>{formatCurrency(resumoPrevisto.total_entradas_antes || 0)}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#dc2626' }}>
                        <span>Saídas:</span>
                        <span>{formatCurrency(resumoPrevisto.total_saidas_antes || 0)}</span>
                      </div>
                      <div style={{ borderTop: '1px solid #e5e7eb', marginTop: '4px', paddingTop: '4px', display: 'flex', justifyContent: 'space-between', fontWeight: '700', color: (resumoPrevisto.total_entradas_antes - resumoPrevisto.total_saidas_antes) >= 0 ? '#10b981' : '#ef4444' }}>
                        <span>Saldo:</span>
                        <span>{formatCurrency((resumoPrevisto.total_entradas_antes || 0) - (resumoPrevisto.total_saidas_antes || 0))}</span>
                      </div>
                    </div>
                  </div>

                  <div
                    onClick={() => setViewScope('periodo')}
                    style={{
                      backgroundColor: 'white',
                      padding: '20px',
                      borderRadius: '8px',
                      borderLeft: '4px solid #f59e0b',
                      boxShadow: viewScope === 'periodo' ? '0 0 0 2px #f59e0b, 0 4px 6px rgba(0,0,0,0.1)' : '0 1px 3px rgba(0,0,0,0.1)',
                      cursor: 'pointer',
                      opacity: viewScope === 'periodo' ? 1 : 0.7,
                      transition: 'all 0.2s ease-in-out',
                      transform: viewScope === 'periodo' ? 'scale(1.02)' : 'scale(1)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>
                        Período Selecionado
                      </div>
                      <div style={{ fontSize: '0.75rem', backgroundColor: '#fef3c7', color: '#b45309', padding: '2px 8px', borderRadius: '9999px', fontWeight: '600' }}>
                        {resumoPrevisto.count_periodo || 0}
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#059669' }}>
                        <span>Entradas:</span>
                        <span>{formatCurrency(resumoPrevisto.total_entradas_previstas)}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#dc2626' }}>
                        <span>Saídas:</span>
                        <span>{formatCurrency(resumoPrevisto.total_saidas_previstas)}</span>
                      </div>
                      <div style={{ borderTop: '1px solid #e5e7eb', marginTop: '4px', paddingTop: '4px', display: 'flex', justifyContent: 'space-between', fontWeight: '700', color: resumoPrevisto.saldo_previsto >= 0 ? '#10b981' : '#ef4444' }}>
                        <span>Saldo:</span>
                        <span>{formatCurrency(resumoPrevisto.saldo_previsto)}</span>
                      </div>
                    </div>
                  </div>

                  <div
                    onClick={() => setViewScope('depois')}
                    style={{
                      backgroundColor: 'white',
                      padding: '20px',
                      borderRadius: '8px',
                      borderLeft: '4px solid #3b82f6',
                      boxShadow: viewScope === 'depois' ? '0 0 0 2px #3b82f6, 0 4px 6px rgba(0,0,0,0.1)' : '0 1px 3px rgba(0,0,0,0.1)',
                      cursor: 'pointer',
                      opacity: viewScope === 'depois' ? 1 : 0.7,
                      transition: 'all 0.2s ease-in-out',
                      transform: viewScope === 'depois' ? 'scale(1.02)' : 'scale(1)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>
                        Posteriores ao Período
                      </div>
                      <div style={{ fontSize: '0.75rem', backgroundColor: '#dbeafe', color: '#1d4ed8', padding: '2px 8px', borderRadius: '9999px', fontWeight: '600' }}>
                        {resumoPrevisto.count_depois || 0}
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#059669' }}>
                        <span>Entradas:</span>
                        <span>{formatCurrency(resumoPrevisto.total_entradas_depois || 0)}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#dc2626' }}>
                        <span>Saídas:</span>
                        <span>{formatCurrency(resumoPrevisto.total_saidas_depois || 0)}</span>
                      </div>
                      <div style={{ borderTop: '1px solid #e5e7eb', marginTop: '4px', paddingTop: '4px', display: 'flex', justifyContent: 'space-between', fontWeight: '700', color: (resumoPrevisto.total_entradas_depois - resumoPrevisto.total_saidas_depois) >= 0 ? '#10b981' : '#ef4444' }}>
                        <span>Saldo:</span>
                        <span>{formatCurrency((resumoPrevisto.total_entradas_depois || 0) - (resumoPrevisto.total_saidas_depois || 0))}</span>
                      </div>
                    </div>
                  </div>

                  {/* Removed legacy breakdown cards - simplified backend no longer provides required fields */}
                </div>
              )}

              {/* estatisticasVencimento section removed - simplified backend no longer provides this data */}






              <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
                <div style={{ padding: '20px', borderBottom: '1px solid #e5e7eb' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                        Movimentações em Aberto - {{
                          antes: 'Anteriores',
                          periodo: 'Período',
                          depois: 'Posteriores'
                        }[viewScope]} ({movimentacoesPrevistas.length})
                      </h3>
                      <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0 }}>
                        Lista detalhada das movimentações pendentes
                      </p>
                    </div>
                  </div>
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
                      {movimentacoesPrevistas.slice(0, 100).map((mov) => (
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
                              backgroundColor: mov.tipo === 'entrada_prevista' ? '#dcfce7' : '#fee2e2',
                              color: mov.tipo === 'entrada_prevista' ? '#166534' : '#dc2626'
                            }}>
                              {mov.tipo === 'entrada_prevista' ? 'A Receber' : 'A Pagar'}
                            </span>
                          </td>
                          <td style={{
                            padding: '12px',
                            textAlign: 'right',
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            color: mov.tipo === 'entrada_prevista' ? '#059669' : '#dc2626'
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
                                mov.status === 'no_prazo' ? '#dcfce7' :
                                  mov.status === 'urgente' ? '#fef3c7' : '#fee2e2',
                              color:
                                mov.status === 'no_prazo' ? '#166534' :
                                  mov.status === 'urgente' ? '#92400e' : '#dc2626'
                            }}>
                              {mov.dias_para_vencimento > 0 ? `${mov.dias_para_vencimento} dias` :
                                mov.dias_para_vencimento === 0 ? 'Vence hoje' :
                                  `${Math.abs(mov.dias_para_vencimento)} dias atraso`}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {/* Paginação Previstas */}
                  {paginacaoPrevistas && paginacaoPrevistas.total_pages > 1 && (
                    <div style={{
                      padding: '16px',
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      gap: '12px',
                      borderTop: '1px solid #e5e7eb'
                    }}>
                      <button
                        onClick={() => loadData(pageRealizadas, pagePrevistas - 1, selectedSpecsPagar, selectedSpecsReceber, selectedOrigemReceita)}
                        disabled={pagePrevistas <= 1}
                        style={{
                          padding: '8px 16px',
                          backgroundColor: pagePrevistas <= 1 ? '#e5e7eb' : '#3b82f6',
                          color: pagePrevistas <= 1 ? '#9ca3af' : 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: pagePrevistas <= 1 ? 'not-allowed' : 'pointer',
                          fontSize: '0.875rem',
                          fontWeight: '500'
                        }}
                      >
                        ← Anterior
                      </button>
                      <span style={{ fontSize: '0.875rem', color: '#374151' }}>
                        Página {paginacaoPrevistas.page} de {paginacaoPrevistas.total_pages}
                        {' '}({paginacaoPrevistas.total_count} movimentações)
                      </span>
                      <button
                        onClick={() => loadData(pageRealizadas, pagePrevistas + 1, selectedSpecsPagar, selectedSpecsReceber, selectedOrigemReceita)}
                        disabled={pagePrevistas >= paginacaoPrevistas.total_pages}
                        style={{
                          padding: '8px 16px',
                          backgroundColor: pagePrevistas >= paginacaoPrevistas.total_pages ? '#e5e7eb' : '#3b82f6',
                          color: pagePrevistas >= paginacaoPrevistas.total_pages ? '#9ca3af' : 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: pagePrevistas >= paginacaoPrevistas.total_pages ? 'not-allowed' : 'pointer',
                          fontSize: '0.875rem',
                          fontWeight: '500'
                        }}
                      >
                        Próxima →
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
          }

          {
            activeTab === 'diario' && resumoDiario && (
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
                                    {Math.abs(dia.saldo_dia) > 1000 ? `${(dia.saldo_dia / 1000).toFixed(0)}k` : ''}
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
                            <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#059669', textTransform: 'uppercase' }}>Entradas</th>
                            <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#dc2626', textTransform: 'uppercase' }}>Saídas</th>
                            <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Saldo do Dia</th>
                            <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Performance</th>
                            <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Intensidade</th>
                          </tr>
                        </thead>
                        <tbody>
                          {resumoDiario.dias.map((dia, index) => {
                            const isPositive = dia.saldo_dia >= 0;
                            const isWeekend = new Date(dia.data).getUTCDay() === 0 || new Date(dia.data).getUTCDay() === 6;
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
            )
          }

          {
            activeTab === 'mensal' && (
              <div>
                {(() => {
                  const hasApiMeses = !!(resumoMensal && Array.isArray(resumoMensal.meses) && resumoMensal.meses.length > 0);
                  const mesesSource = hasApiMeses ? resumoMensal!.meses : resumoMensalFallback.meses;
                  const totaisSource = hasApiMeses ? resumoMensal!.totais : resumoMensalFallback.totais;
                  if (!mesesSource || mesesSource.length === 0) {
                    return (
                      <div style={{
                        backgroundColor: '#fff3cd',
                        border: '1px solid #ffeaa7',
                        borderRadius: '8px',
                        padding: '20px',
                        textAlign: 'center'
                      }}>
                        <h3 style={{ color: '#856404', marginBottom: '8px' }}>Dados Mensais Indisponíveis</h3>
                        <p style={{ color: '#6c5400', margin: 0 }}>
                          Não foi possível obter dados mensais do período selecionado.
                        </p>
                      </div>
                    );
                  }
                  return (
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
                            {formatCurrency(totaisSource.total_entradas)}
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
                            {formatCurrency(totaisSource.total_saidas)}
                          </div>
                        </div>

                        <div style={{
                          backgroundColor: 'white',
                          padding: '20px',
                          borderRadius: '8px',
                          borderLeft: `4px solid ${totaisSource.saldo_liquido >= 0 ? '#10b981' : '#ef4444'}`,
                          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                        }}>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                            Saldo Líquido
                          </div>
                          <div style={{
                            fontSize: '1.5rem',
                            fontWeight: '700',
                            color: totaisSource.saldo_liquido >= 0 ? '#10b981' : '#ef4444'
                          }}>
                            {formatCurrency(totaisSource.saldo_liquido)}
                          </div>
                        </div>
                      </div>

                      {/* Tabela de Resumo Mensal */}
                      {mesesSource && mesesSource.length > 0 && (
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
                              Movimento Mensal ({mesesSource.length} meses)
                            </h3>
                          </div>

                          <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                              <thead style={{ backgroundColor: '#f9fafb' }}>
                                <tr>
                                  <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Mês</th>
                                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#0369a1', textTransform: 'uppercase' }}>Entradas Contratos</th>
                                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#16a34a', textTransform: 'uppercase' }}>Entradas Vendas</th>
                                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#d97706', textTransform: 'uppercase' }}>Saídas Fixas</th>
                                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#dc2626', textTransform: 'uppercase' }}>Saídas Variáveis</th>
                                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Total Entradas</th>
                                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Total Saídas</th>
                                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '700', color: '#111827', textTransform: 'uppercase' }}>Saldo do Mês</th>
                                </tr>
                              </thead>
                              <tbody>
                                {mesesSource.map((mes: {
                                  mes: string;
                                  entradas_contrato?: number;
                                  entradas_vendas?: number;
                                  saidas_fixas?: number;
                                  saidas_variaveis?: number;
                                  total_entradas?: number;
                                  total_saidas?: number;
                                  entradas?: number;
                                  saidas?: number;
                                  saldo?: number;
                                }, index: number) => {
                                  // Normaliza chave AAAA-MM
                                  let chave = '';
                                  try {
                                    // Use string parsing to avoid timezone issues with Date object
                                    // Backend returns YYYY-MM-DD...
                                    const s = String(mes.mes);
                                    chave = s.length >= 7 ? s.substring(0, 7) : s;
                                  } catch {
                                    chave = String(mes.mes);
                                  }

                                  // Usar dados do backend ou fallback para os campos antigos
                                  const entradasContrato = mes.entradas_contrato ?? 0;
                                  const entradasVendas = mes.entradas_vendas ?? 0;
                                  const saidasFixas = mes.saidas_fixas ?? 0;
                                  const saidasVariaveis = mes.saidas_variaveis ?? 0;
                                  const totalEntradas = mes.total_entradas ?? mes.entradas ?? 0;
                                  const totalSaidas = mes.total_saidas ?? mes.saidas ?? 0;
                                  const saldo = mes.saldo ?? (totalEntradas - totalSaidas);

                                  return (
                                    <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                                        {chave}
                                      </td>
                                      <td style={{
                                        padding: '12px',
                                        textAlign: 'right',
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        color: entradasContrato > 0 ? '#0369a1' : '#9ca3af'
                                      }}>
                                        {entradasContrato > 0 ? formatCurrency(entradasContrato) : '—'}
                                      </td>
                                      <td style={{
                                        padding: '12px',
                                        textAlign: 'right',
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        color: entradasVendas > 0 ? '#16a34a' : '#9ca3af'
                                      }}>
                                        {entradasVendas > 0 ? formatCurrency(entradasVendas) : '—'}
                                      </td>
                                      <td style={{
                                        padding: '12px',
                                        textAlign: 'right',
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        color: saidasFixas > 0 ? '#d97706' : '#9ca3af'
                                      }}>
                                        {saidasFixas > 0 ? formatCurrency(saidasFixas) : '—'}
                                      </td>
                                      <td style={{
                                        padding: '12px',
                                        textAlign: 'right',
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        color: saidasVariaveis > 0 ? '#dc2626' : '#9ca3af'
                                      }}>
                                        {saidasVariaveis > 0 ? formatCurrency(saidasVariaveis) : '—'}
                                      </td>
                                      <td style={{
                                        padding: '12px',
                                        textAlign: 'right',
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        color: '#059669'
                                      }}>
                                        {formatCurrency(totalEntradas)}
                                      </td>
                                      <td style={{
                                        padding: '12px',
                                        textAlign: 'right',
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        color: '#dc2626'
                                      }}>
                                        {formatCurrency(totalSaidas)}
                                      </td>
                                      <td style={{
                                        padding: '12px',
                                        textAlign: 'right',
                                        fontSize: '0.875rem',
                                        fontWeight: '700',
                                        color: saldo >= 0 ? '#059669' : '#dc2626'
                                      }}>
                                        {formatCurrency(saldo)}
                                      </td>
                                    </tr>
                                  )
                                })}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            )
          }
        </div>
      </div>
    </div>
  );
};

export default FluxoCaixaDashboard;

