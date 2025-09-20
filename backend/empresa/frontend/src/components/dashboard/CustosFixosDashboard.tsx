// src/components/dashboard/CustosFixosDashboard.tsx

import { useState, useEffect } from 'react';
import { useCustosFixos, type DateRange } from '../../hooks/useCustosFixos';
import { formatCurrency } from '../../lib/utils';
import {
  Calendar,
  Download,
  AlertCircle,
  Info
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

  const applyFilterWithDates = (startISO: string, endISO: string) => {
    console.log('🔍 Aplicando filtro (helper) com datas:', { startISO, endISO });
    // Atualiza inputs
    setDataInicio(startISO);
    setDataFim(endISO);

    const from = new Date(startISO + 'T00:00:00');
    const to = new Date(endISO + 'T23:59:59');

    console.log('🔍 Datas convertidas (helper):', { from, to });

    if (!isNaN(from.getTime()) && !isNaN(to.getTime())) {
      const newDateRange = { from, to };
      console.log('🔍 Novo range de datas (helper):', newDateRange);
      setDateRange(newDateRange);
      fetchCustosFixos(newDateRange);
    } else {
      console.error('❌ Datas inválidas (helper):', { startISO, endISO });
    }
  };

  const handleApplyFilter = () => applyFilterWithDates(dataInicio, dataFim);

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

  // Previsto: agora traz TODOS os custos por data de vencimento (pagos e abertos) via endpoint dedicado
  type PrevistoRow = {
    data_vencimento: string;
    valor_total: number;
    qtd: number;
    valor_pagos: number;
    qtd_pagos: number;
    valor_abertos: number;
    qtd_abertos: number;
  };
  const [previstos, setPrevistos] = useState<PrevistoRow[]>([]);
  const [previstoTotaisPorTipo, setPrevistoTotaisPorTipo] = useState<Record<string, { total: number; pagos: number; abertos: number }>>({});
  const [filtroTipoComparativo, setFiltroTipoComparativo] = useState<'AMBOS' | 'CUSTO FIXO' | 'DESPESA FIXA'>('AMBOS');
  type PrevistoModo = 'TOTAL' | 'ABERTOS';
  const [previstoModo, setPrevistoModo] = useState<PrevistoModo>(() => {
    try {
      const saved = localStorage.getItem('custosFixos.previstoModo');
      return (saved === 'ABERTOS' || saved === 'TOTAL') ? (saved as PrevistoModo) : 'TOTAL';
    } catch {
      return 'TOTAL';
    }
  });
  useEffect(() => {
    try { localStorage.setItem('custosFixos.previstoModo', previstoModo); } catch { /* ignore */ }
  }, [previstoModo]);
  type DebugStats = {
    total_endpoint: number;
    fixos_por_tipo: number;
    fixos_por_especificacao: number;
    nao_classificados: number;
    status_A: number;
    status_P: number;
    soma_abertos: number;
  };
  const [debugStats, setDebugStats] = useState<DebugStats | null>(null);

  useEffect(() => {
    const loadPrevistos = async () => {
      try {
        const baseUrl = 'http://127.0.0.1:8000/contas/contas-por-data-vencimento/';
  const params = `?data_inicio=${dataInicio}&data_fim=${dataFim}&tipo=pagar&status=TODOS`;
        const res = await fetch(`${baseUrl}${params}`);
        if (!res.ok) return;
        const json = await res.json();
        const toNumber = (v: unknown): number => {
          if (typeof v === 'number') return v;
          if (typeof v === 'string') {
            const s = v.replace(/\s+/g, '');
            // Tenta parsear representações "1234.56" ou "1.234,56"
            const normalized = /,/.test(s) && /\./.test(s)
              ? s.replace(/\./g, '').replace(',', '.')
              : s.replace(',', '.');
            const n = parseFloat(normalized);
            return isNaN(n) ? 0 : n;
          }
          return 0;
        };
        const contas = (json?.contas_a_pagar || []) as Array<{
          vencimento: string;
          valor: unknown;
          status: string;
          fornecedor_nome?: string;
          fornecedor_tipo?: string;
          fornecedor_especificacao?: string;
        }>;
        // Filtrar por fornecedores fixos (CUSTO FIXO / DESPESA FIXA)
        const tipoUp = (s?: string) => (s || '').trim().toUpperCase();
        const classificaPorEspecificacao = (e?: string): 'CUSTO FIXO' | 'DESPESA FIXA' | 'NAO' => {
          const E = tipoUp(e);
          const FIXOS = ['SALARIOS', 'PRO-LABORE', 'HONOR. CONTABEIS', 'LUZ', 'AGUA', 'TELEFONE', 'IMPOSTOS', 'ENCARGOS', 'REFEICAO', 'BENEFICIOS', 'OUTRAS DESPESAS', 'MAT. DE ESCRITORIO', 'PAGTO SERVICOS', 'EMPRESTIMO', 'DESP. FINANCEIRAS'];
          const DESPESAS = ['DESPESA FIXA'];
          if (!E) return 'NAO';
          if (E === 'DESPESA FIXA' || DESPESAS.includes(E)) return 'DESPESA FIXA';
          if (FIXOS.includes(E)) return 'CUSTO FIXO';
          return 'NAO';
        };
        const isFixoTipo = (t?: string) => ['CUSTO FIXO', 'DESPESA FIXA', 'FIXO'].includes(tipoUp(t));
        let fixos_por_tipo = 0;
        let fixos_por_especificacao = 0;
        let nao_classificados = 0;
        const fixos = contas.filter(c => {
          if (isFixoTipo(c.fornecedor_tipo)) return true;
          const cls = classificaPorEspecificacao(c.fornecedor_especificacao);
          return cls !== 'NAO';
        });
        // Contabilizar classificações
        for (const c of contas) {
          if (isFixoTipo(c.fornecedor_tipo)) fixos_por_tipo += 1;
          else {
            const cls = classificaPorEspecificacao(c.fornecedor_especificacao);
            if (cls !== 'NAO') fixos_por_especificacao += 1; else nao_classificados += 1;
          }
        }

        // Agregar por vencimento e separar Pagos x Abertos
        const map = new Map<string, { valor_total: number; qtd: number; valor_pagos: number; qtd_pagos: number; valor_abertos: number; qtd_abertos: number }>();
        // Totais por tipo para o comparador
        const totaisPorTipo: Record<string, { total: number; pagos: number; abertos: number }> = {};

        let status_A = 0;
        let status_P = 0;
        let soma_abertos = 0;
        for (const it of fixos) {
          const key = (it.vencimento || '').toString().slice(0, 10);
          if (!key) continue;
          if (!map.has(key)) map.set(key, { valor_total: 0, qtd: 0, valor_pagos: 0, qtd_pagos: 0, valor_abertos: 0, qtd_abertos: 0 });
          const agg = map.get(key)!;
          const valor = toNumber(it.valor);
          const s = (it.status ?? '').toString().trim().toUpperCase();
          const status = s.length > 1
            ? (s.startsWith('P') ? 'P' : (s.startsWith('A') ? 'A' : s))
            : s; // normaliza 'PAGO'/'ABERTO' em 'P'/'A'
          agg.valor_total += valor;
          agg.qtd += 1;
          if (status === 'P') {
            agg.valor_pagos += valor;
            agg.qtd_pagos += 1;
            status_P += 1;
          } else if (status === 'A') {
            agg.valor_abertos += valor;
            agg.qtd_abertos += 1;
            status_A += 1;
            soma_abertos += valor;
          }

          const tipoFornecedor = ((): 'CUSTO FIXO' | 'DESPESA FIXA' => {
            const t = tipoUp(it.fornecedor_tipo);
            if (t === 'DESPESA FIXA') return 'DESPESA FIXA';
            if (t === 'CUSTO FIXO' || t === 'FIXO') return 'CUSTO FIXO';
            // fallback pela especificação
            const cls = classificaPorEspecificacao(it.fornecedor_especificacao);
            return cls === 'DESPESA FIXA' ? 'DESPESA FIXA' : 'CUSTO FIXO';
          })();
          if (!totaisPorTipo[tipoFornecedor]) totaisPorTipo[tipoFornecedor] = { total: 0, pagos: 0, abertos: 0 };
          totaisPorTipo[tipoFornecedor].total += valor;
          if (status === 'P') totaisPorTipo[tipoFornecedor].pagos += valor;
          if (status === 'A') totaisPorTipo[tipoFornecedor].abertos += valor;
        }

        const arr = Array.from(map.entries()).map(([data_vencimento, v]) => ({ data_vencimento, ...v }))
          .sort((a, b) => a.data_vencimento.localeCompare(b.data_vencimento));
        setPrevistos(arr);
        setPrevistoTotaisPorTipo(totaisPorTipo);
        setDebugStats({
          total_endpoint: contas.length,
          fixos_por_tipo,
          fixos_por_especificacao,
          nao_classificados,
          status_A,
          status_P,
          soma_abertos
        });
      } catch (e) {
        console.warn('Falha ao carregar previstos (vencimento aberto):', e);
        setPrevistos([]);
        setPrevistoTotaisPorTipo({});
        setDebugStats(null);
      }
    };
    loadPrevistos();
  }, [dataInicio, dataFim]);

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

  // Totais previstos (pagos + abertos por vencimento)
  const qtdPrevistaFixos = previstos.reduce((acc, r) => acc + (r.qtd || 0), 0);
  const totalPrevistoPagos = previstos.reduce((acc, r) => acc + (r.valor_pagos || 0), 0);
  const totalPrevistoAbertos = previstos.reduce((acc, r) => acc + (r.valor_abertos || 0), 0);
  // Headline Previsto: total (pagos + abertos) por vencimento no período
  const totalPrevistoFixos = previstoModo === 'TOTAL'
    ? previstos.reduce((acc, r) => acc + (r.valor_total || 0), 0)
    : totalPrevistoAbertos;

  // Total realizado de fixos (somatório de custos fixos e despesas fixas pagos no período)
  // Nota: já exibimos o total realizado via data.totais_gerais.valor_total no card abaixo

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
                const startISO = inicioMes.toISOString().split('T')[0];
                const endISO = hoje.toISOString().split('T')[0];
                applyFilterWithDates(startISO, endISO);
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
                const startISO = inicioAno.toISOString().split('T')[0];
                const endISO = hoje.toISOString().split('T')[0];
                applyFilterWithDates(startISO, endISO);
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
                const startISO = anoPassado.toISOString().split('T')[0];
                const endISO = fimAnoPassado.toISOString().split('T')[0];
                applyFilterWithDates(startISO, endISO);
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
          {/* Previsto - Custos Fixos (por Vencimento) */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #f59e0b',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px', fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>Previsto (Fixos - por Vencimento)</span>
                <span title="Previsto por vencimento. Modo TOTAL: pagos + em aberto. Modo ABERTOS: apenas em aberto." style={{ display: 'inline-flex', alignItems: 'center' }}>
                <Info style={{ width: '16px', height: '16px', color: '#f59e0b', cursor: 'help' }} />
                </span>
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                {(['TOTAL','ABERTOS'] as const).map(m => (
                  <button
                    key={m}
                    onClick={() => setPrevistoModo(m)}
                    style={{
                      padding: '2px 8px',
                      borderRadius: '9999px',
                      border: previstoModo === m ? '1px solid #f59e0b' : '1px solid #e5e7eb',
                      backgroundColor: previstoModo === m ? '#fffbeb' : 'white',
                      color: '#92400e',
                      fontSize: '0.7rem',
                      cursor: 'pointer'
                    }}
                    title={m === 'TOTAL' ? 'Pagos + Em aberto (por vencimento)' : 'Apenas Em aberto (por vencimento)'}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(totalPrevistoFixos)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {qtdPrevistaFixos} contas previstas
            </div>
            <div style={{ display: 'flex', gap: '12px', marginTop: '6px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.75rem', color: '#16a34a' }}>Pagos (por vencimento): <strong>{formatCurrency(totalPrevistoPagos)}</strong></span>
              <span style={{ fontSize: '0.75rem', color: '#dc2626' }}>Em aberto (por vencimento): <strong>{formatCurrency(totalPrevistoAbertos)}</strong></span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '2px' }}>
              Período: {dateRange.from.toLocaleDateString()} — {dateRange.to.toLocaleDateString()}
            </div>
          </div>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #3b82f6',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              <span>Valor Total Realizado</span>
              <span title="Realizado considera a data de pagamento (aquilo que já saiu do caixa) no período selecionado." style={{ display: 'inline-flex', alignItems: 'center' }}>
                <Info style={{ width: '16px', height: '16px', color: '#3b82f6', cursor: 'help' }} />
              </span>
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(data.totais_gerais.valor_total)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {data.total_contas_pagas} contas pagas
            </div>
            <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '2px' }}>
              Período: {dateRange.from.toLocaleDateString()} — {dateRange.to.toLocaleDateString()}
            </div>
          </div>

          {/* Comparativo Previsto x Realizado (Fixos) */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #8b5cf6',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '8px' }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>
                Comparativo Previsto x Realizado (Fixos)
              </div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {(['AMBOS','CUSTO FIXO','DESPESA FIXA'] as const).map(t => (
                  <button
                    key={t}
                    onClick={() => setFiltroTipoComparativo(t)}
                    style={{
                      padding: '4px 8px',
                      borderRadius: '9999px',
                      border: filtroTipoComparativo === t ? '1px solid #8b5cf6' : '1px solid #e5e7eb',
                      backgroundColor: filtroTipoComparativo === t ? '#ede9fe' : 'white',
                      color: '#4b5563',
                      fontSize: '0.75rem',
                      cursor: 'pointer'
                    }}
                    title={t === 'AMBOS' ? 'Somar CUSTO FIXO + DESPESA FIXA' : `Mostrar apenas ${t}`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
            {(() => {
              const realizadoCF = data?.totais_gerais?.valor_custos_fixos || 0;
              const realizadoDF = data?.totais_gerais?.valor_despesas_fixas || 0;
              const realizadoFiltrado = filtroTipoComparativo === 'AMBOS' ? (realizadoCF + realizadoDF) : (filtroTipoComparativo === 'CUSTO FIXO' ? realizadoCF : realizadoDF);

              const pCF = (previstoModo === 'TOTAL'
                ? (previstoTotaisPorTipo['CUSTO FIXO']?.total || 0)
                : (previstoTotaisPorTipo['CUSTO FIXO']?.abertos || 0));
              const pDF = (previstoModo === 'TOTAL'
                ? (previstoTotaisPorTipo['DESPESA FIXA']?.total || 0)
                : (previstoTotaisPorTipo['DESPESA FIXA']?.abertos || 0));
              const previstoFiltrado = filtroTipoComparativo === 'AMBOS' ? (pCF + pDF) : (filtroTipoComparativo === 'CUSTO FIXO' ? pCF : pDF);
              const delta = previstoFiltrado - realizadoFiltrado;
              return (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '12px' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Previsto</div>
                    <div style={{ fontSize: '1.125rem', fontWeight: 700, color: '#111827' }}>{formatCurrency(previstoFiltrado)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Realizado (Fixos)</div>
                    <div style={{ fontSize: '1.125rem', fontWeight: 700, color: '#111827' }}>{formatCurrency(realizadoFiltrado)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Δ (Previsto − Realizado)</div>
                    <div style={{ fontSize: '1.125rem', fontWeight: 700, color: delta >= 0 ? '#059669' : '#dc2626' }}>
                      {formatCurrency(delta)}
                    </div>
                  </div>
                </div>
              );
            })()}
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '6px' }}>
              Observação: Previsto agrupa por data de vencimento. Modo TOTAL = pagos + abertos; Modo ABERTOS = somente abertos. Realizado soma custos/despesas fixas por data de pagamento.
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
              Custos Fixos (Realizado)
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(data.totais_gerais.valor_custos_fixos)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {data.totais_gerais.valor_total > 0 
                ? formatPercent((data.totais_gerais.valor_custos_fixos / data.totais_gerais.valor_total) * 100)
                : formatPercent(0)
              } do total
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
              Despesas Fixas (Realizado)
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(data.totais_gerais.valor_despesas_fixas)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {data.totais_gerais.valor_total > 0 
                ? formatPercent((data.totais_gerais.valor_despesas_fixas / data.totais_gerais.valor_total) * 100)
                : formatPercent(0)
              } do total
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
          {/* Debug Badges (temporário) */}
          {debugStats && (
            <div style={{
              backgroundColor: '#f9fafb',
              border: '1px dashed #e5e7eb',
              borderRadius: '6px',
              padding: '8px 10px',
              marginTop: '8px',
              display: 'flex',
              gap: '8px',
              flexWrap: 'wrap'
            }}>
              <span style={{ fontSize: '0.7rem', color: '#374151' }}>Debug:</span>
              <span style={{ fontSize: '0.7rem', background: '#eef2ff', color: '#3730a3', padding: '2px 6px', borderRadius: '9999px' }}>endpoint: {debugStats.total_endpoint}</span>
              <span style={{ fontSize: '0.7rem', background: '#ecfeff', color: '#155e75', padding: '2px 6px', borderRadius: '9999px' }}>fixo(tipo): {debugStats.fixos_por_tipo}</span>
              <span style={{ fontSize: '0.7rem', background: '#f0fdf4', color: '#166534', padding: '2px 6px', borderRadius: '9999px' }}>fixo(espec): {debugStats.fixos_por_especificacao}</span>
              <span style={{ fontSize: '0.7rem', background: '#fff7ed', color: '#9a3412', padding: '2px 6px', borderRadius: '9999px' }}>ign: {debugStats.nao_classificados}</span>
              <span style={{ fontSize: '0.7rem', background: '#fee2e2', color: '#991b1b', padding: '2px 6px', borderRadius: '9999px' }}>A: {debugStats.status_A}</span>
              <span style={{ fontSize: '0.7rem', background: '#e0f2fe', color: '#075985', padding: '2px 6px', borderRadius: '9999px' }}>P: {debugStats.status_P}</span>
              <span style={{ fontSize: '0.7rem', background: '#f1f5f9', color: '#0f172a', padding: '2px 6px', borderRadius: '9999px' }}>Σ abertos: {formatCurrency(debugStats.soma_abertos)}</span>
            </div>
          )}
        </div>
      )}

      {/* Gráficos */}
      {data && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
          {/* Totais previstos por data de vencimento */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
              Totais Previsto (Fixos) por Vencimento
            </h3>
            {previstos.length === 0 ? (
              <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Sem contas a pagar fixas (pagas ou em aberto) no período.</div>
            ) : (
              <div style={{ maxHeight: '360px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' as const, fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f9fafb' }}>
                      <th style={{ padding: '8px', textAlign: 'left', color: '#374151', fontSize: '0.75rem' }}>Vencimento</th>
                      <th style={{ padding: '8px', textAlign: 'right', color: '#374151', fontSize: '0.75rem' }}>Previsto (Total)</th>
                      <th style={{ padding: '8px', textAlign: 'right', color: '#374151', fontSize: '0.75rem' }}>Pagos</th>
                      <th style={{ padding: '8px', textAlign: 'right', color: '#374151', fontSize: '0.75rem' }}>Em aberto</th>
                      <th style={{ padding: '8px', textAlign: 'center', color: '#374151', fontSize: '0.75rem' }}>Qtd Pagos</th>
                      <th style={{ padding: '8px', textAlign: 'center', color: '#374151', fontSize: '0.75rem' }}>Qtd Abertos</th>
                      <th style={{ padding: '8px', textAlign: 'center', color: '#374151', fontSize: '0.75rem' }}>Qtd</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previstos.map((row, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid #f3f4f6' }}>
                        <td style={{ padding: '8px', color: '#111827' }}>{new Date(row.data_vencimento).toLocaleDateString()}</td>
                        <td style={{ padding: '8px', textAlign: 'right', fontWeight: 600 }}>{formatCurrency(row.valor_total)}</td>
                        <td style={{ padding: '8px', textAlign: 'right', color: '#16a34a' }}>{formatCurrency(row.valor_pagos)}</td>
                        <td style={{ padding: '8px', textAlign: 'right', color: '#dc2626' }}>{formatCurrency(row.valor_abertos)}</td>
                        <td style={{ padding: '8px', textAlign: 'center' }}>{row.qtd_pagos}</td>
                        <td style={{ padding: '8px', textAlign: 'center' }}>{row.qtd_abertos}</td>
                        <td style={{ padding: '8px', textAlign: 'center' }}>{row.qtd}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div style={{ marginTop: '12px', color: '#6b7280', fontSize: '0.75rem' }}>
              Observação: valores previstos agrupados por data de vencimento (inclui pagos e em aberto), considerando fornecedores do tipo CUSTO FIXO e DESPESA FIXA.
            </div>
          </div>
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
