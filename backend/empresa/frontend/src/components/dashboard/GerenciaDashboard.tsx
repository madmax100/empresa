// src/components/dashboard/GerenciaDashboard.tsx
// Painel de Gerência - Demonstrativo de Resultados (DRE)

import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Calculator,
  Info,
  Wallet,
  CheckCircle,
  AlertTriangle,
  Filter
} from 'lucide-react';

// Interface para item de invoice no modal
interface InvoiceItem {
  numero: string;
  data: string;
  cliente: string;
  valor: number;
  obs?: string;
}

// Interface para item de custo detalhado
interface CustoItem {
  data: string;
  descricao: string;
  valor: number;
}

// Interface para categoria de custo
interface CustoCategoria {
  categoria: string;
  valor: number;
  itens: CustoItem[];
}

// Interface para item de CMV no modal
interface CMVItem {
  data: string;
  nota_fiscal: string;
  cliente: string;
  produto: string;
  quantidade: number;
  custo_unitario: number;
  custo_total: number;
  preco_venda_unitario: number;
  preco_venda_total: number;
  tipo: string;
  operacao: string;
}

// Interfaces para os dados do DRE
interface DREData {
  faturamento_bruto: number;
  faturamento_vendas: number;
  faturamento_servicos: number;
  faturamento_servicos_contratos: number;
  faturamento_servicos_avulsos: number;
  lista_vendas: InvoiceItem[];
  lista_servicos_contratos: InvoiceItem[];
  lista_servicos_avulsos: InvoiceItem[];
  lista_cmv: CMVItem[];
  lista_cmv_vendas: CMVItem[];
  lista_cmv_contratos: CMVItem[];
  lista_cmv_outros: CMVItem[];
  impostos_vendas: number;
  percentual_impostos: number;
  estoque_inicio: number;
  compras_periodo: number;
  estoque_fim: number;
  cmv: number;
  cmv_vendas: number;
  cmv_contratos: number;
  cmv_outros: number;
  lucro_bruto: number;
  margem_bruta_percent: number;
  custos_fixos: number;
  custos_variaveis: number;
  detalhe_custos_fixos: CustoCategoria[];
  detalhe_custos_variaveis: CustoCategoria[];
  despesas_operacionais: number;
  resultado_liquido: number;
  margem_liquida_percent: number;
}

interface SaudeFinanceira {
  liquidez_imediata: number;
  contas_receber: number;
  contas_receber_count: number;
  contas_pagar: number;
  contas_pagar_count: number;
  capital_giro_estoque: number;
  saldo_liquido: number;
}

interface CicloCaixa {
  entradas_previstas: number;
  saidas_previstas: number;
  necessidade_capital: number;
  sobra_caixa: number;
  situacao: 'POSITIVO' | 'NEGATIVO';
  analise: string;
}

interface ResumoMensalItem {
  mes: string;
  entradas_contrato: number;
  entradas_vendas: number;
  total_entradas: number;
  saidas_fixas: number;
  saidas_variaveis: number;
  total_saidas: number;
  saldo: number;
  detalhe_fixos: Record<string, number>;
  detalhe_variaveis: Record<string, number>;
}


interface ResumoMensalData {
  totais: {
    entradas_contrato: number;
    entradas_vendas: number;
    total_entradas: number;
    saidas_fixas: number;
    saidas_variaveis: number;
    total_saidas: number;
    saldo_liquido: number;
  };
  meses: ResumoMensalItem[];
  categorias_fixas: string[];
  categorias_variaveis: string[];
}


interface DREResponse {
  periodo: {
    inicio: string;
    fim: string;
  };
  dre: DREData;
  saude_financeira: SaudeFinanceira;
  ciclo_caixa: CicloCaixa;
}

interface GerenciaDashboardProps {
  dataInicio: string;
  dataFim: string;
}

const GerenciaDashboard: React.FC<GerenciaDashboardProps> = ({ dataInicio, dataFim }) => {
  // Estado de datas


  // Estado de dados
  const [data, setData] = useState<DREResponse | null>(null);
  const [resumoMensal, setResumoMensal] = useState<ResumoMensalData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'visao_geral' | 'resumo_mensal'>('visao_geral');
  const [expandFixas, setExpandFixas] = useState(false);
  const [expandVariaveis, setExpandVariaveis] = useState(false);


  // Estado do modal de detalhes
  const [modalOpen, setModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [modalItems, setModalItems] = useState<any[]>([]);
  const [modalType, setModalType] = useState<'default' | 'cmv' | 'custos' | 'detalhe_custo'>('default');

  // Estado para seleção de categorias de custos (Filtro interativo)
  const [selectedFixed, setSelectedFixed] = useState<string[]>([]);
  const [selectedVariable, setSelectedVariable] = useState<string[]>([]);

  // Inicializar seleção quando os dados chegarem
  // Inicializar seleção quando os dados chegarem
  useEffect(() => {
    if (data?.dre) {
      // Fixos: Selecionar todos por padrão
      if (data.dre.detalhe_custos_fixos) {
        // Só atualizar se estiver vazio (primeira carga ou reset)
        if (selectedFixed.length === 0) {
          setSelectedFixed(data.dre.detalhe_custos_fixos.map(c => c.categoria));
        }
      }
      // Variáveis: Selecionar todos exceto "Mercadorias" e "Empréstimos"
      if (data.dre.detalhe_custos_variaveis) {
        if (selectedVariable.length === 0) {
          const excluded = ['Mercadorias', 'Mercadoria', 'Empréstimos', 'Empréstimo'];
          const defaults = data.dre.detalhe_custos_variaveis
            .map(c => c.categoria)
            .filter(c => !excluded.includes(c));
          setSelectedVariable(defaults);
        }
      }
    }
  }, [data]);

  // Função para alternar seleção de categoria
  const toggleFixed = (category: string) => {
    setSelectedFixed(prev =>
      prev.includes(category) ? prev.filter(c => c !== category) : [...prev, category]
    );
  };

  const toggleVariable = (category: string) => {
    setSelectedVariable(prev =>
      prev.includes(category) ? prev.filter(c => c !== category) : [...prev, category]
    );
  };

  // Cálculos dinâmicos baseados na seleção (Frontend - Visão Geral)
  const calculatedFixedCosts = data?.dre?.detalhe_custos_fixos
    .filter(c => selectedFixed.includes(c.categoria))
    .reduce((sum, c) => sum + c.valor, 0) || 0;

  const calculatedVariableCosts = data?.dre?.detalhe_custos_variaveis
    .filter(c => selectedVariable.includes(c.categoria))
    .reduce((sum, c) => sum + c.valor, 0) || 0;

  const calculatedOperatingExpenses = calculatedFixedCosts + calculatedVariableCosts;

  // Recalculating Gross Profit as Revenue - CMV (ignoring taxes as requested)
  const calculatedGrossProfit = (data?.dre?.faturamento_bruto || 0) - (data?.dre?.cmv || 0);
  const calculatedNetResult = calculatedGrossProfit - calculatedOperatingExpenses;

  const calculatedNetMargin = data?.dre?.faturamento_bruto
    ? (calculatedNetResult / data.dre.faturamento_bruto) * 100
    : 0;

  // --- FETCHING RESUMO MENSAL SEPARATELY ---
  // Quando os filtros mudam, recarregar apenas o Resumo Mensal
  useEffect(() => {
    // Evitar chamar se não tiver dados iniciais ou se estiver carregando tudo
    if (!data || loading) return;

    const fetchResumo = async () => {
      try {
        // Usar caminhos relativos para evitar problemas de porta/host
        const params = new URLSearchParams();
        if (dataInicio) params.append('data_inicio', dataInicio);
        if (dataFim) params.append('data_fim', dataFim);

        // Calcular Exclusões (com verificação de existência)
        const allFixed = data.dre?.detalhe_custos_fixos?.map(c => c.categoria) || [];
        const allVariable = data.dre?.detalhe_custos_variaveis?.map(c => c.categoria) || [];

        const excludeFixed = allFixed.filter(c => !selectedFixed.includes(c));
        const excludeVariable = allVariable.filter(c => !selectedVariable.includes(c));

        if (excludeFixed.length) params.append('exclude_fixed', excludeFixed.join(','));
        if (excludeVariable.length) params.append('exclude_variable', excludeVariable.join(','));

        const res = await fetch(`/api/fluxo-caixa-realizado/resumo_mensal/?${params.toString()}`);
        if (res.ok) {
          const resumoData = await res.json();
          setResumoMensal(resumoData);
        } else {
          console.error("Erro na resposta do resumo mensal:", res.status);
        }
      } catch (e) {
        console.error("Erro ao atualizar resumo mensal", e);
      }
    };

    const timeoutId = setTimeout(fetchResumo, 500); // Debounce
    return () => clearTimeout(timeoutId);

  }, [selectedFixed, selectedVariable, data, dataInicio, dataFim]); // data dependency for base categories

  // Função para abrir modal
  const openModal = (title: string, items: any[], type: 'default' | 'cmv' | 'custos' = 'default') => {
    setModalTitle(title);
    setModalItems(items);
    setModalType(type);
    setModalOpen(true);
  };

  // Formatação de moeda
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  // --- THEME & STYLES ---
  const theme = {
    colors: {
      primary: '#0f172a',
      secondary: '#64748b',
      accent: '#2563eb', // blue-600
      success: '#10b981', // emerald-500
      successBg: '#ecfdf5', // emerald-50
      danger: '#ef4444', // red-500
      dangerBg: '#fef2f2', // red-50
      warning: '#f59e0b', // amber-500
      warningBg: '#fffbeb', // amber-50
      purple: '#6366f1',
      purpleBg: '#e0e7ff',
      background: '#f8fafc',
      card: '#ffffff',
      border: '#e2e8f0',
      sidebar: '#ffffff',
    },
    shadows: {
      sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
      md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
      lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
      hover: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    },
    radius: '12px',
  };

  // --- SUB-COMPONENTS ---

  // Card genérico com estilo moderno
  const ModernCard: React.FC<{
    children: React.ReactNode;
    title?: React.ReactNode;
    subtitle?: string;
    className?: string;
    action?: React.ReactNode;
    style?: React.CSSProperties;
    onClick?: () => void;
  }> = ({ children, title, subtitle, className, action, style, onClick }) => (
    <div
      onClick={onClick}
      style={{
        backgroundColor: theme.colors.card,
        borderRadius: theme.radius,
        boxShadow: onClick ? theme.shadows.md : theme.shadows.sm,
        border: `1px solid ${theme.colors.border}`,
        padding: '24px',
        transition: 'all 0.2s ease-in-out',
        cursor: onClick ? 'pointer' : 'default',
        transform: onClick ? 'translateY(0)' : 'none',
        ...style
      }}
      onMouseEnter={(e) => onClick && (e.currentTarget.style.transform = 'translateY(-2px)', e.currentTarget.style.boxShadow = theme.shadows.hover)}
      onMouseLeave={(e) => onClick && (e.currentTarget.style.transform = 'none', e.currentTarget.style.boxShadow = theme.shadows.md)}
    >
      {(title || action) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div>
            {title && (
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600', color: theme.colors.primary }}>
                {title}
              </h3>
            )}
            {subtitle && (
              <div style={{ fontSize: '13px', color: theme.colors.secondary, marginTop: '4px' }}>
                {subtitle}
              </div>
            )}
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  );

  // Card de Indicador Simples (Stat)
  const StatCard: React.FC<{
    label: string;
    value: string;
    subValue?: string;
    icon?: React.ReactNode;
    trend?: 'up' | 'down' | 'neutral';
    trendValue?: string;
    color?: string; // Hex color for the icon/value
    onClick?: () => void;
    children?: React.ReactNode;
  }> = ({ label, value, subValue, icon, trend, trendValue, color = theme.colors.primary, onClick, children }) => (
    <div
      onClick={onClick}
      style={{
        backgroundColor: theme.colors.card,
        borderRadius: theme.radius,
        padding: '20px',
        border: `1px solid ${theme.colors.border}`,
        boxShadow: theme.shadows.sm,
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s',
      }}
      onMouseEnter={(e) => onClick && (e.currentTarget.style.transform = 'translateY(-2px)')}
      onMouseLeave={(e) => onClick && (e.currentTarget.style.transform = 'none')}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '13px', fontWeight: '500', color: theme.colors.secondary, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {label}
        </span>
        {icon && (
          <div style={{
            padding: '8px',
            borderRadius: '8px',
            backgroundColor: `${color}15`, // 10% opacity
            color: color
          }}>
            {icon}
          </div>
        )}
      </div>

      <div>
        <div style={{ fontSize: '24px', fontWeight: '700', color: theme.colors.primary, letterSpacing: '-0.02em' }}>
          {value}
        </div>
        {(subValue || trendValue) && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px', fontSize: '13px' }}>
            {trend === 'up' && <TrendingUp size={14} color={theme.colors.success} />}
            {trend === 'down' && <TrendingDown size={14} color={theme.colors.danger} />}
            <span style={{ color: trend === 'up' ? theme.colors.success : trend === 'down' ? theme.colors.danger : theme.colors.secondary }}>
              {trendValue}
            </span>
            {subValue && <span style={{ color: theme.colors.secondary }}>{subValue}</span>}
          </div>
        )}
      </div>
    </div>
  );

  // Linha do DRE
  const DRELine: React.FC<{
    label: string;
    value: number;
    color?: string;
    bold?: boolean;
    large?: boolean;
    highlight?: boolean;
    indent?: number;
    action?: () => void;
  }> = ({ label, value, color, bold, large, highlight, indent = 0, action }) => (
    <div
      onClick={action}
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: highlight ? '12px 16px' : '8px 0',
        backgroundColor: highlight ? `${color || theme.colors.primary}10` : 'transparent',
        borderRadius: highlight ? '8px' : '0',
        cursor: action ? 'pointer' : 'default',
        borderBottom: highlight ? 'none' : `1px dashed ${theme.colors.border}`,
        marginBottom: highlight ? '8px' : '0'
      }}
    >
      <div style={{
        paddingLeft: `${indent * 16}px`,
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        color: bold ? theme.colors.primary : theme.colors.secondary,
        fontWeight: bold ? '600' : '400',
        fontSize: large ? '16px' : '14px'
      }}>
        {label}
        {action && <Info size={14} style={{ opacity: 0.5 }} />}
      </div>
      <div style={{
        fontWeight: bold ? '700' : '500',
        fontSize: large ? '18px' : '14px',
        color: color || theme.colors.primary,
        fontFamily: "'Inter', sans-serif" // Ensure tabular nums in font setup if possible, or manual 
      }}>
        {formatCurrency(value)}
      </div>
    </div>
  );

  // Componente de Section Header
  const SectionHeader: React.FC<{ title: string; icon?: React.ReactNode; subtitle?: string }> = ({ title, icon, subtitle }) => (
    <div style={{ marginBottom: '24px' }}>
      <h2 style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        fontSize: '20px',
        fontWeight: '700',
        color: theme.colors.primary,
        margin: '0 0 4px 0'
      }}>
        {icon}
        {title}
      </h2>
      {subtitle && <p style={{ margin: 0, color: theme.colors.secondary, fontSize: '14px' }}>{subtitle}</p>}
    </div>
  );

  // Cor baseada no valor (positivo/negativo)
  const getValueColor = (value: number): string => {
    if (value > 0) return '#16a34a'; // green
    if (value < 0) return '#dc2626'; // red
    return '#64748b'; // gray
  };

  // Buscar dados (DRE + Resumo Mensal)
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (dataInicio) params.append('data_inicio', dataInicio);
      if (dataFim) params.append('data_fim', dataFim);

      const [dreRes, resumoRes] = await Promise.all([
        fetch(`/api/dre/?${params.toString()}`),
        fetch(`/api/fluxo-caixa-realizado/resumo_mensal/?${params.toString()}`)
      ]);

      if (!dreRes.ok) throw new Error('Erro ao carregar DRE');
      const dreData = await dreRes.json();
      setData(dreData);

      if (resumoRes.ok) {
        const resumoData = await resumoRes.json();
        setResumoMensal(resumoData);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [dataInicio, dataFim]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Loading state
  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #e5e7eb',
          borderTopColor: '#3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 16px'
        }} />
        <div style={{ fontSize: '18px', color: '#6b7280' }}>Carregando DRE...</div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{
        padding: '20px',
        margin: '20px',
        backgroundColor: '#fee2e2',
        border: '1px solid #fecaca',
        borderRadius: '12px',
        color: '#dc2626'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Erro ao carregar dados</div>
        <div>{error}</div>
      </div>
    );
  }

  const dre = data?.dre;
  const saude = data?.saude_financeira;
  const ciclo = data?.ciclo_caixa;

  return (
    <div style={{
      padding: '32px',
      backgroundColor: theme.colors.background,
      minHeight: '100vh',
      fontFamily: "'Inter', sans-serif",
      color: theme.colors.primary
    }}>

      <div style={{ display: 'flex', gap: '24px' }}>

        {/* SIDEBAR FILTERS */}
        <div style={{ width: '280px', flexShrink: 0 }}>
          <div style={{
            backgroundColor: theme.colors.card,
            borderRadius: theme.radius,
            padding: '20px',
            boxShadow: theme.shadows.sm,
            border: `1px solid ${theme.colors.border}`,
            position: 'sticky',
            top: '20px'
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: theme.colors.primary, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Filter size={18} /> Filtros de Custo
            </h3>

            {/* Filtros de Custos Fixos */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '13px', fontWeight: '600', color: theme.colors.secondary, marginBottom: '8px', textTransform: 'uppercase' }}>
                Custos Fixos
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '300px', overflowY: 'auto' }}>
                {dre?.detalhe_custos_fixos?.length ? dre.detalhe_custos_fixos.map((cat, idx) => (
                  <label key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer', color: theme.colors.primary }}>
                    <input
                      type="checkbox"
                      checked={selectedFixed.includes(cat.categoria)}
                      onChange={() => toggleFixed(cat.categoria)}
                      style={{ cursor: 'pointer', accentColor: theme.colors.primary }}
                    />
                    <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={cat.categoria}>{cat.categoria}</span>
                  </label>
                )) : <div style={{ fontSize: '12px', color: theme.colors.secondary, fontStyle: 'italic' }}>Nenhum custo fixo</div>}
              </div>
            </div>

            {/* Filtros de Custos Variáveis */}
            <div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: theme.colors.secondary, marginBottom: '8px', textTransform: 'uppercase' }}>
                Custos Variáveis
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '300px', overflowY: 'auto' }}>
                {dre?.detalhe_custos_variaveis?.length ? dre.detalhe_custos_variaveis.map((cat, idx) => (
                  <label key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer', color: theme.colors.danger }}>
                    <input
                      type="checkbox"
                      checked={selectedVariable.includes(cat.categoria)}
                      onChange={() => toggleVariable(cat.categoria)}
                      style={{ cursor: 'pointer', accentColor: theme.colors.danger }}
                    />
                    <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={cat.categoria}>{cat.categoria}</span>
                  </label>
                )) : <div style={{ fontSize: '12px', color: theme.colors.secondary, fontStyle: 'italic' }}>Nenhum custo variável</div>}
              </div>
              <div style={{ marginTop: '12px', fontSize: '11px', color: theme.colors.secondary, lineHeight: '1.4' }}>
                * "Mercadorias" e "Empréstimos" desmarcados por padrão a pedido.
              </div>
            </div>
          </div>
        </div>

        {/* MAIN CONTENT AREA */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* HEADER & TABS moved here */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', flexWrap: 'wrap', gap: '20px' }}>
            <div>
              <h1 style={{ fontSize: '28px', fontWeight: '800', color: theme.colors.primary, margin: 0 }}>
                Painel de Gerência
              </h1>
              <p style={{ margin: '8px 0 0', color: theme.colors.secondary }}>
                Visão geral financeira e operacional
              </p>
            </div>

            {/* TABS */}
            <div style={{ display: 'flex', gap: '16px', borderBottom: `1px solid ${theme.colors.border}` }}>
              <button
                onClick={() => setActiveTab('visao_geral')}
                style={{
                  padding: '8px 16px',
                  background: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'visao_geral' ? `2px solid ${theme.colors.accent}` : '2px solid transparent',
                  color: activeTab === 'visao_geral' ? theme.colors.accent : theme.colors.secondary,
                  fontWeight: activeTab === 'visao_geral' ? '600' : '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                Visão Geral (DRE)
              </button>
              <button
                onClick={() => setActiveTab('resumo_mensal')}
                style={{
                  padding: '8px 16px',
                  background: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'resumo_mensal' ? `2px solid ${theme.colors.accent}` : '2px solid transparent',
                  color: activeTab === 'resumo_mensal' ? theme.colors.accent : theme.colors.secondary,
                  fontWeight: activeTab === 'resumo_mensal' ? '600' : '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                Resumo Mensal
              </button>
            </div>
          </div>

          {activeTab === 'visao_geral' ? (
            <>

              {/* HERO STATS */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '40px' }}>
                <StatCard
                  label="Faturamento Bruto"
                  value={formatCurrency(dre?.faturamento_bruto || 0)}
                  icon={<TrendingUp size={20} />}
                  color={theme.colors.accent}
                  trend="up"
                  trendValue="Receita Total"
                  subValue="do período"
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span style={{ color: theme.colors.secondary }}>Vendas</span>
                      <span style={{ fontWeight: '600', color: theme.colors.primary }}>{formatCurrency(dre?.faturamento_vendas || 0)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span style={{ color: theme.colors.secondary }}>Contratos</span>
                      <span style={{ fontWeight: '600', color: theme.colors.primary }}>{formatCurrency(dre?.faturamento_servicos_contratos || 0)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span style={{ color: theme.colors.secondary }}>Outros</span>
                      <span style={{ fontWeight: '600', color: theme.colors.primary }}>{formatCurrency(dre?.faturamento_servicos_avulsos || 0)}</span>
                    </div>
                  </div>
                </StatCard>
                <StatCard
                  label="Lucro Líquido"
                  value={formatCurrency(calculatedNetResult)}
                  icon={calculatedNetResult >= 0 ? <CheckCircle size={20} /> : <AlertTriangle size={20} />}
                  color={calculatedNetResult >= 0 ? theme.colors.success : theme.colors.danger}
                  trend={calculatedNetResult >= 0 ? 'up' : 'down'}
                  trendValue={`Margem: ${calculatedNetMargin.toFixed(1)}%`}
                />

              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '32px' }}>

                {/* COLUNA ESQUERDA - DRE */}
                <div>
                  <SectionHeader title="DRE" subtitle="Demonstrativo do Resultado do Exercício" icon={<Calculator size={24} color={theme.colors.accent} />} />

                  <ModernCard>
                    {/* FATURAMENTO */}
                    <div style={{ marginBottom: '24px' }}>
                      <DRELine
                        label="(+) Faturamento Bruto"
                        value={dre?.faturamento_bruto || 0}
                        bold large color={theme.colors.success}
                        highlight
                      />
                      <DRELine
                        label="Vendas (NF Saída)"
                        value={dre?.faturamento_vendas || 0}
                        indent={1}
                        action={() => dre?.lista_vendas && openModal('Vendas (NF Saída)', dre.lista_vendas)}
                      />
                      <DRELine
                        label="Serviços (Contratos)"
                        value={dre?.faturamento_servicos_contratos || 0}
                        indent={1}
                        action={() => dre?.lista_servicos_contratos && openModal('Serviços - Contratos', dre.lista_servicos_contratos)}
                      />
                      <DRELine
                        label="Serviços (Avulsos)"
                        value={dre?.faturamento_servicos_avulsos || 0}
                        indent={1}
                        action={() => dre?.lista_servicos_avulsos && openModal('Serviços - Avulsos', dre.lista_servicos_avulsos)}
                      />
                    </div>

                    {/* DEDUÇÕES & CUSTOS */}
                    <div style={{ marginBottom: '24px' }}>

                      <DRELine
                        label="(-) CMV (Custo Mercadoria)"
                        value={-(dre?.cmv || 0)}
                        color={theme.colors.warning}
                        bold
                        action={() => dre?.lista_cmv && openModal('CMV - Detalhamento', dre.lista_cmv, 'cmv')}
                      />
                      <DRELine
                        label="Custos Vendas"
                        value={-(dre?.cmv_vendas || 0)}
                        indent={1}
                        color={theme.colors.secondary}
                        action={() => dre?.lista_cmv_vendas && openModal('CMV - Vendas', dre.lista_cmv_vendas, 'cmv')}
                      />
                      <DRELine
                        label="Custos Contratos"
                        value={-(dre?.cmv_contratos || 0)}
                        indent={1}
                        color={theme.colors.secondary}
                        action={() => dre?.lista_cmv_contratos && openModal('CMV - Contratos', dre.lista_cmv_contratos, 'cmv')}
                      />
                      <DRELine
                        label="Custos Outros"
                        value={-(dre?.cmv_outros || 0)}
                        indent={1}
                        color={theme.colors.secondary}
                        action={() => dre?.lista_cmv_outros && openModal('CMV - Outros', dre.lista_cmv_outros, 'cmv')}
                      />
                    </div>

                    {/* MARGEM BRUTA */}
                    <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: theme.colors.background, borderRadius: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontSize: '13px', color: theme.colors.secondary, fontWeight: '600', textTransform: 'uppercase' }}>Lucro Bruto (Faturamento - CMV)</div>
                          <div style={{ fontSize: '24px', fontWeight: '700', color: theme.colors.primary }}>{formatCurrency((dre?.faturamento_bruto || 0) - (dre?.cmv || 0))}</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '13px', color: theme.colors.secondary }}>Margem Bruta</div>
                          <div style={{ fontSize: '16px', fontWeight: '700', color: theme.colors.primary }}>{(dre?.margem_bruta_percent || 0).toFixed(1)}%</div>
                        </div>
                      </div>
                    </div>

                    {/* DESPESAS OPERACIONAIS */}
                    <div style={{ marginBottom: '24px' }}>
                      <DRELine
                        label="(-) Despesas Operacionais (Calculado)"
                        value={-calculatedOperatingExpenses}
                        color={theme.colors.danger}
                        bold highlight
                      />

                      <div style={{ marginTop: '12px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: theme.colors.secondary, marginBottom: '8px', paddingLeft: '8px' }}>
                          <span>Custos Fixos (Selecionados)</span>
                          <span>{formatCurrency(calculatedFixedCosts)}</span>
                        </div>

                        <div style={{
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '2px',
                          paddingLeft: '8px',
                          marginBottom: '16px',
                          maxHeight: '300px',
                          overflowY: 'auto'
                        }}>
                          {dre?.detalhe_custos_fixos
                            ?.filter(cat => selectedFixed.includes(cat.categoria))
                            .map((cat, idx) => (
                              <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px', padding: '4px 0' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                  <span style={{ color: theme.colors.primary }}>
                                    {cat.categoria}
                                  </span>
                                  <button
                                    onClick={() => cat.itens && openModal(cat.categoria, cat.itens, 'detalhe_custo')}
                                    style={{ border: 'none', background: 'transparent', cursor: 'pointer', padding: '2px', display: 'flex', alignItems: 'center' }}
                                    title="Ver detalhes"
                                  >
                                    <Info size={14} color={theme.colors.secondary} />
                                  </button>
                                </div>
                                <span style={{ color: theme.colors.secondary }}>
                                  {formatCurrency(cat.valor)}
                                </span>
                              </div>
                            ))}
                          {!calculatedFixedCosts && <div style={{ fontSize: '12px', color: theme.colors.secondary, fontStyle: 'italic' }}>Nenhum custo fixo selecionado.</div>}
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: theme.colors.secondary, marginBottom: '8px', paddingLeft: '8px' }}>
                          <span>Custos Variáveis (Selecionados)</span>
                          <span>{formatCurrency(calculatedVariableCosts)}</span>
                        </div>

                        <div style={{
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '2px',
                          paddingLeft: '8px',
                          maxHeight: '300px',
                          overflowY: 'auto'
                        }}>
                          {dre?.detalhe_custos_variaveis
                            ?.filter(cat => selectedVariable.includes(cat.categoria))
                            .map((cat, idx) => (
                              <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px', padding: '4px 0' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                  <span style={{ color: theme.colors.danger }}>
                                    {cat.categoria}
                                  </span>
                                  <button
                                    onClick={() => cat.itens && openModal(cat.categoria, cat.itens, 'detalhe_custo')}
                                    style={{ border: 'none', background: 'transparent', cursor: 'pointer', padding: '2px', display: 'flex', alignItems: 'center' }}
                                    title="Ver detalhes"
                                  >
                                    <Info size={14} color={theme.colors.secondary} />
                                  </button>
                                </div>
                                <span style={{ color: theme.colors.danger }}>
                                  {formatCurrency(cat.valor)}
                                </span>
                              </div>
                            ))}
                          {!calculatedVariableCosts && <div style={{ fontSize: '12px', color: theme.colors.secondary, fontStyle: 'italic' }}>Nenhum custo variável selecionado.</div>}
                        </div>
                      </div>
                    </div>

                    {/* RESULTADO FINAL */}
                    <div style={{
                      marginTop: '16px',
                      padding: '20px',
                      backgroundColor: calculatedNetResult >= 0 ? theme.colors.successBg : theme.colors.dangerBg,
                      borderRadius: '8px',
                      border: `1px solid ${calculatedNetResult >= 0 ? theme.colors.success : theme.colors.danger}40`,
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: '14px', fontWeight: '600', color: calculatedNetResult >= 0 ? theme.colors.success : theme.colors.danger, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Resultado Líquido (Lucro/Prejuízo)
                      </div>
                      <div style={{ fontSize: '32px', fontWeight: '800', margin: '8px 0', color: calculatedNetResult >= 0 ? theme.colors.success : theme.colors.danger }}>
                        {formatCurrency(calculatedNetResult)}
                      </div>
                      <div style={{ fontSize: '14px', color: theme.colors.secondary }}>
                        Margem Líquida: <strong>{calculatedNetMargin.toFixed(1)}%</strong>
                      </div>
                    </div>
                    <div style={{
                      marginTop: '16px',
                      padding: '16px',
                      borderRadius: '8px',
                      backgroundColor: '#f1f5f9',
                      fontSize: '12px',
                      color: theme.colors.secondary,
                      lineHeight: '1.5',
                      textAlign: 'left'
                    }}>
                      <strong>Nota:</strong> O DRE utiliza o regime de competência. O CMV é calculado: Estoque Inicial + Compras - Estoque Final. Os impostos são estimados em {(dre?.percentual_impostos || 0).toFixed(0)}%.
                    </div>

                  </ModernCard>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200" style={{
              backgroundColor: theme.colors.card,
              borderRadius: '16px',
              padding: '24px',
              boxShadow: theme.shadows.card,
              border: `1px solid ${theme.colors.border}`
            }}>
              <SectionHeader title="Resumo Mensal Detalhado" icon={<TrendingUp size={24} color={theme.colors.accent} />} />
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                  <thead style={{ backgroundColor: '#f8fafc', color: theme.colors.secondary, textTransform: 'uppercase', fontSize: '11px' }}>
                    <tr>
                      <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Mês</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '600', color: theme.colors.success }}>Rec. Contratos</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '600', color: theme.colors.success }}>Rec. Vendas</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '700', color: theme.colors.success, backgroundColor: '#f0fdf4' }}>Total Receitas</th>

                      {/* Custos Fixos EXPANDABLE */}
                      <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '600', color: theme.colors.danger, borderLeft: '1px solid #e2e8f0' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px' }}>
                          <span>Desp. Fixas</span>
                          <button
                            onClick={() => setExpandFixas(!expandFixas)}
                            style={{ padding: '2px 4px', fontSize: '10px', background: '#fee2e2', border: '1px solid #fecaca', borderRadius: '4px', cursor: 'pointer', color: theme.colors.danger }}
                          >
                            {expandFixas ? '«' : '»'}
                          </button>
                        </div>
                      </th>
                      {expandFixas && resumoMensal?.categorias_fixas.map(cat => (
                        <th key={cat} style={{ padding: '12px 8px', textAlign: 'right', fontWeight: '400', color: '#7f1d1d', fontSize: '10px', backgroundColor: '#fff5f5' }}>
                          {cat}
                        </th>
                      ))}

                      {/* Custos Variáveis EXPANDABLE */}
                      <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '600', color: theme.colors.danger, borderLeft: '1px solid #e2e8f0' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px' }}>
                          <span>Desp. Variáveis</span>
                          <button
                            onClick={() => setExpandVariaveis(!expandVariaveis)}
                            style={{ padding: '2px 4px', fontSize: '10px', background: '#fee2e2', border: '1px solid #fecaca', borderRadius: '4px', cursor: 'pointer', color: theme.colors.danger }}
                          >
                            {expandVariaveis ? '«' : '»'}
                          </button>
                        </div>
                      </th>
                      {expandVariaveis && resumoMensal?.categorias_variaveis.map(cat => (
                        <th key={cat} style={{ padding: '12px 8px', textAlign: 'right', fontWeight: '400', color: '#7f1d1d', fontSize: '10px', backgroundColor: '#fff5f5' }}>
                          {cat}
                        </th>
                      ))}

                      <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '700', color: theme.colors.danger, backgroundColor: '#fef2f2', borderLeft: '1px solid #e2e8f0' }}>Total Saídas</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '700' }}>Resultado</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right' }}>Margem %</th>
                    </tr>
                  </thead>

                  <tbody>
                    {resumoMensal?.meses.map((mes, idx) => {
                      const margem = mes.total_entradas > 0
                        ? ((mes.saldo / mes.total_entradas) * 100)
                        : 0;

                      return (
                        <tr key={idx} style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                          <td style={{ padding: '12px 16px', fontWeight: '500' }}>
                            {new Date(mes.mes).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric', timeZone: 'UTC' })}
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                            {mes.entradas_contrato.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                            {mes.entradas_vendas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '700', color: theme.colors.success, backgroundColor: '#f0fdf4' }}>
                            {mes.total_entradas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>

                          {/* Coluna Principal Fixa */}
                          <td style={{ padding: '12px 16px', textAlign: 'right', color: theme.colors.danger, borderLeft: '1px solid #f1f5f9' }}>
                            {mes.saidas_fixas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>
                          {/* Colunas Detalhadas Fixas */}
                          {expandFixas && resumoMensal?.categorias_fixas.map(cat => (
                            <td key={cat} style={{ padding: '12px 8px', textAlign: 'right', color: '#991b1b', fontSize: '11px', backgroundColor: '#fffafa' }}>
                              {(mes.detalhe_fixos[cat] || 0) > 0 ? mes.detalhe_fixos[cat].toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : '-'}
                            </td>
                          ))}

                          {/* Coluna Principal Variável */}
                          <td style={{ padding: '12px 16px', textAlign: 'right', color: theme.colors.danger, borderLeft: '1px solid #f1f5f9' }}>
                            {mes.saidas_variaveis.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>
                          {/* Colunas Detalhadas Variáveis */}
                          {expandVariaveis && resumoMensal?.categorias_variaveis.map(cat => (
                            <td key={cat} style={{ padding: '12px 8px', textAlign: 'right', color: '#991b1b', fontSize: '11px', backgroundColor: '#fffafa' }}>
                              {(mes.detalhe_variaveis[cat] || 0) > 0 ? mes.detalhe_variaveis[cat].toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : '-'}
                            </td>
                          ))}

                          <td style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '700', color: theme.colors.danger, backgroundColor: '#fef2f2', borderLeft: '1px solid #f1f5f9' }}>
                            {mes.total_saidas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '700', color: mes.saldo >= 0 ? theme.colors.success : theme.colors.danger, borderLeft: '1px solid #f1f5f9' }}>
                            {mes.saldo.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </td>
                          <td style={{ padding: '12px 16px', textAlign: 'right', fontWeight: '500', color: margem >= 0 ? theme.colors.success : theme.colors.danger }}>
                            {margem.toFixed(1)}%
                          </td>
                        </tr>
                      );

                    })}
                    {/* Linha de Totais */}
                    {resumoMensal?.totais && (
                      <tr style={{ backgroundColor: '#f1f5f9', fontWeight: '700', borderTop: '2px solid #cbd5e1' }}>
                        <td style={{ padding: '12px 16px' }}>TOTAL</td>
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: theme.colors.success }}>
                          {resumoMensal.totais.entradas_contrato.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: theme.colors.success }}>
                          {resumoMensal.totais.entradas_vendas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: theme.colors.success }}>
                          {resumoMensal.totais.total_entradas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>

                        {/* Totais Fixos */}
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: theme.colors.danger }}>
                          {resumoMensal.totais.saidas_fixas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>
                        {expandFixas && resumoMensal.categorias_fixas.map(cat => {
                          const totalCat = resumoMensal.meses.reduce((sum, m) => sum + (m.detalhe_fixos[cat] || 0), 0);
                          return (
                            <td key={cat} style={{ padding: '12px 8px', textAlign: 'right', color: '#991b1b', fontSize: '11px' }}>
                              {totalCat.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </td>
                          );
                        })}

                        {/* Totais Variáveis */}
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: theme.colors.danger }}>
                          {resumoMensal.totais.saidas_variaveis.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>
                        {expandVariaveis && resumoMensal.categorias_variaveis.map(cat => {
                          const totalCat = resumoMensal.meses.reduce((sum, m) => sum + (m.detalhe_variaveis[cat] || 0), 0);
                          return (
                            <td key={cat} style={{ padding: '12px 8px', textAlign: 'right', color: '#991b1b', fontSize: '11px' }}>
                              {totalCat.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </td>
                          );
                        })}

                        <td style={{ padding: '12px 16px', textAlign: 'right', color: theme.colors.danger }}>
                          {resumoMensal.totais.total_saidas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: resumoMensal.totais.saldo_liquido >= 0 ? theme.colors.success : theme.colors.danger }}>
                          {resumoMensal.totais.saldo_liquido.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                          {(resumoMensal.totais.total_entradas > 0
                            ? ((resumoMensal.totais.saldo_liquido / resumoMensal.totais.total_entradas) * 100)
                            : 0).toFixed(1)}%
                        </td>
                      </tr>
                    )}

                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Detalhes */}
      {
        modalOpen && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
          }} onClick={() => setModalOpen(false)}>
            <div
              onClick={(e) => e.stopPropagation()}
              style={{
                backgroundColor: theme.colors.card,
                borderRadius: '16px',
                padding: '0',
                maxWidth: '900px',
                width: '90%',
                maxHeight: '85vh',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: theme.shadows.lg,
                border: `1px solid ${theme.colors.border}`,
                animation: 'slideIn 0.2s ease-out'
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '20px 24px',
                borderBottom: `1px solid ${theme.colors.border}`
              }}>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: theme.colors.primary, display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: '4px', height: '24px', backgroundColor: theme.colors.accent, borderRadius: '2px' }} />
                  {modalTitle}
                </h3>
                <button
                  onClick={() => setModalOpen(false)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: theme.colors.secondary,
                    cursor: 'pointer',
                    padding: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '50%',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f1f5f9'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <span style={{ fontSize: '24px', lineHeight: '1' }}>×</span>
                </button>
              </div>

              <div style={{ overflow: 'auto', padding: '0' }}>
                <table style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '13px'
                }}>
                  <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f8fafc', zIndex: 10 }}>
                    <tr>
                      {modalType === 'cmv' ? (
                        <>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Tipo</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Operação</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>NF</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Cliente</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Item</th>
                          <th style={{ padding: '12px 16px', textAlign: 'right', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Qtd</th>
                          <th style={{ padding: '12px 16px', textAlign: 'right', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Custo Total</th>
                          <th style={{ padding: '12px 16px', textAlign: 'right', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Venda Total</th>
                        </>
                      ) : modalType === 'detalhe_custo' ? (
                        <>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Data</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Descrição</th>
                          <th style={{ padding: '12px 16px', textAlign: 'right', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Valor</th>
                        </>
                      ) : modalType === 'custos' ? (
                        <>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Categoria</th>
                          <th style={{ padding: '12px 16px', textAlign: 'right', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Valor Total</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Principais Itens</th>
                        </>
                      ) : (
                        <>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>NF</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Data</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Cliente</th>
                          <th style={{ padding: '12px 16px', textAlign: 'right', borderBottom: `1px solid ${theme.colors.border}`, color: theme.colors.secondary, fontWeight: '600' }}>Valor</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {modalItems.map((item, idx) => (
                      <tr key={idx} style={{ backgroundColor: idx % 2 === 0 ? 'white' : '#f8fafc' }}>
                        {modalType === 'cmv' ? (
                          <>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}` }}>
                              <span style={{
                                fontSize: '10px',
                                fontWeight: '700',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                backgroundColor: item.tipo === 'VENDA' ? '#dbeafe' : item.tipo === 'CONTRATO' ? '#dcfce7' : '#f3f4f6',
                                color: item.tipo === 'VENDA' ? '#1e40af' : item.tipo === 'CONTRATO' ? '#166534' : '#374151'
                              }}>
                                {item.tipo}
                              </span>
                            </td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, fontSize: '11px', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.operacao}>
                              {item.operacao}
                            </td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, fontFamily: "'JetBrains Mono', monospace", fontSize: '12px' }}>{item.nota_fiscal}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.cliente}>{item.cliente}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.produto}>{item.produto}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, textAlign: 'right' }}>{item.quantidade}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '500', color: theme.colors.danger }}>{formatCurrency(item.custo_total)}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '500', color: theme.colors.success }}>{formatCurrency(item.preco_venda_total)}</td>
                          </>
                        ) : modalType === 'detalhe_custo' ? (
                          <>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}` }}>{item.data}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.descricao}>{item.descricao}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: 'bold' }}>{formatCurrency(item.valor)}</td>
                          </>
                        ) : modalType === 'custos' ? (
                          <>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, fontWeight: '600', color: theme.colors.primary }}>{item.categoria}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: 'bold', fontFamily: "'JetBrains Mono', monospace" }}>{formatCurrency(item.valor)}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, fontSize: '12px', color: theme.colors.secondary, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '300px' }}>
                              {item.itens ? (
                                <>
                                  {item.itens.slice(0, 3).map((i: any) => i.descricao.split(' - ')[0]).join(', ')}
                                  {item.itens.length > 3 && '...'}
                                </>
                              ) : '-'}
                            </td>
                          </>
                        ) : (
                          <>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, fontFamily: "'JetBrains Mono', monospace" }}>{item.numero}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}` }}>{item.data}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}` }}>{item.cliente}</td>
                            <td style={{ padding: '10px 16px', borderBottom: `1px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '600', color: theme.colors.primary }}>
                              {formatCurrency(item.valor)}
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                  <tfoot style={{ position: 'sticky', bottom: 0, backgroundColor: '#f1f5f9', zIndex: 10 }}>
                    <tr>
                      {modalType === 'cmv' ? (
                        <>
                          <td colSpan={5} style={{ padding: '12px 16px', borderTop: `2px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '700', color: theme.colors.secondary }}>TOTAIS:</td>
                          <td style={{ padding: '12px 16px', borderTop: `2px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '700', color: theme.colors.danger, fontSize: '14px' }}>
                            {formatCurrency(modalItems.reduce((sum, item) => sum + (item.custo_total || 0), 0))}
                          </td>
                          <td style={{ padding: '12px 16px', borderTop: `2px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '700', color: theme.colors.success, fontSize: '14px' }}>
                            {formatCurrency(modalItems.reduce((sum, item) => sum + (item.preco_venda_total || 0), 0))}
                          </td>
                        </>
                      ) : modalType === 'custos' ? (
                        <>
                          <td style={{ padding: '12px 16px', borderTop: `2px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '700', color: theme.colors.secondary }}>TOTAL GERAL:</td>
                          <td style={{ padding: '12px 16px', borderTop: `2px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '700', fontSize: '15px' }}>{formatCurrency(modalItems.reduce((acc, curr) => acc + curr.valor, 0))}</td>
                          <td style={{ padding: '12px 16px', borderTop: `2px solid ${theme.colors.border}` }}></td>
                        </>
                      ) : (
                        <>
                          <td colSpan={3} style={{ padding: '12px 16px', borderTop: `2px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '700', color: theme.colors.secondary }}>TOTAL:</td>
                          <td style={{ padding: '12px 16px', borderTop: `2px solid ${theme.colors.border}`, textAlign: 'right', fontWeight: '700', fontSize: '15px', color: theme.colors.primary }}>
                            {formatCurrency(modalItems.reduce((sum, item) => sum + item.valor, 0))}
                          </td>
                        </>
                      )}
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          </div>
        )
      }
    </div>
  );
};

export default GerenciaDashboard;