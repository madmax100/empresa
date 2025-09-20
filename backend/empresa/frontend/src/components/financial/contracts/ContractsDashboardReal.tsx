// src/components/financial/contracts/ContractsDashboardReal.tsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  ChevronDown,
  ChevronRight,
  TrendingUp,
  Users,
  FileText,
  DollarSign
} from "lucide-react";
import { SeparateDatePicker } from '../../common/SeparateDatePicker';

// Adicionar CSS para animações
const spinKeyframes = `
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
`;

// Adicionar o CSS ao head se ainda não existir
if (typeof document !== 'undefined' && !document.getElementById('contracts-animations')) {
  const styleElement = document.createElement('style');
  styleElement.id = 'contracts-animations';
  styleElement.textContent = spinKeyframes;
  document.head.appendChild(styleElement);
}

// Interfaces baseadas no formato real da API
interface NotaSuprimento {
  id: number;
  numero_nota: string;
  data: string;
  operacao: string;
  cfop: string;
  valor_total_nota: number;
  obs?: string;
}

// Interface para dados de vigência (endpoint separado)
interface ContratoVigencia {
  contrato_id: number;
  contrato_numero: string;
  cliente: {
    id: number;
    nome: string;
  };
  vigencia: {
    inicio: string;
    fim: string;
  };
  valores_contratuais: {
    valor_mensal: number;
    faturamento_proporcional: number;
    percentual_proporcional: number;
  };
  analise_financeira: {
    custo_suprimentos: number;
    margem_liquida: number;
    percentual_margem: number;
  };
  notas_suprimentos: NotaSuprimento[];
}

// Interface para resposta completa da API
interface RespostaVigencia {
  periodo: {
    data_inicio: string;
    data_fim: string;
  };
  resumo: {
    total_contratos_vigentes: number;
    contratos_ativos: number;
    contratos_inativos: number;
  };
  resumo_financeiro: {
    faturamento_total_proporcional: number;
    custo_total_suprimentos: number;
    margem_bruta_total: number;
    percentual_margem_total: number;
  };
  resultados: ContratoVigencia[];
}

// Interface para dados agrupados por cliente
interface ClienteAgrupado {
  clienteId: number;
  clienteNome: string;
  contratos: ContratoCompleto[];
  totalContratos: number;
  faturamentoTotal: number;
  despesasSuprimentos: number;
  margemLiquida: number;
  percentualMargem: number;
}

// Interface para contratos processados
interface ContratoCompleto extends ContratoVigencia {
  valor_mensal: number;
  faturamento_periodo: number;
  suprimentos_valor: number;
  margem_liquida: number;
  percentual_margem: number;
}

// Interface para resumo financeiro
interface ResumoFinanceiro {
  totalClientes: number;
  totalContratos: number;
  faturamentoTotal: number;
  despesasTotal: number;
  margemTotal: number;
  percentualMargem: number;
}

const ContractsDashboardReal: React.FC = () => {
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(2025, 7, 1), // agosto 2025
    to: new Date(2025, 7, 31)
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clientesAgrupados, setClientesAgrupados] = useState<ClienteAgrupado[]>([]);
  const [resumoFinanceiro, setResumoFinanceiro] = useState<ResumoFinanceiro | null>(null);
  const [activeTab, setActiveTab] = useState<'clientes' | 'graficos' | 'detalhes'>('clientes');
  const [clientesExpandidos, setClientesExpandidos] = useState<Set<number>>(new Set());

  const formatCurrency = (value: number) => {
    // Validação robusta para evitar NaN
    const numValue = Number(value);
    if (isNaN(numValue) || !isFinite(numValue)) {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(0);
    }
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(numValue);
  };

  const formatPercent = (value: number) => {
    // Validação robusta para evitar NaN
    const numValue = Number(value);
    if (isNaN(numValue) || !isFinite(numValue)) {
      return '0.0%';
    }
    return `${numValue.toFixed(1)}%`;
  };

  // Função helper para garantir valores numéricos válidos (versão mais permissiva)
  const safeMath = {
    toNumber: (value: unknown): number => {
      if (value === null || value === undefined || value === '') {
        return 0;
      }
      const num = Number(value);
      return isNaN(num) || !isFinite(num) ? 0 : num;
    },
    add: (a: unknown, b: unknown): number => {
      const numA = safeMath.toNumber(a);
      const numB = safeMath.toNumber(b);
      return numA + numB;
    },
    subtract: (a: unknown, b: unknown): number => {
      const numA = safeMath.toNumber(a);
      const numB = safeMath.toNumber(b);
      return numA - numB;
    },
    percentage: (part: unknown, total: unknown): number => {
      const numPart = safeMath.toNumber(part);
      const numTotal = safeMath.toNumber(total);
      if (numTotal === 0) return 0;
      return (numPart / numTotal) * 100;
    }
  };

  const toggleClienteExpansao = (clienteId: number) => {
    const novosExpandidos = new Set(clientesExpandidos);
    if (novosExpandidos.has(clienteId)) {
      novosExpandidos.delete(clienteId);
    } else {
      novosExpandidos.add(clienteId);
    }
    setClientesExpandidos(novosExpandidos);
  };

  const carregarDados = useCallback(async () => {
    if (!dateRange.from || !dateRange.to) return;

    setLoading(true);
    setError(null);

    try {
      const dataInicial = dateRange.from.toISOString().split('T')[0];
      const dataFinal = dateRange.to.toISOString().split('T')[0];
      
      const url = `http://localhost:8000/api/contratos_locacao/suprimentos/?data_inicial=${dataInicial}&data_final=${dataFinal}`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status} ${response.statusText}`);
      }

      const data: RespostaVigencia = await response.json();

      // Processar e agrupar dados por cliente
      const clienteMap = new Map<number, ClienteAgrupado>();

      data.resultados.forEach((contrato) => {
        const clienteId = contrato.cliente.id;
        const clienteNome = contrato.cliente.nome;

        // Calcular margem líquida se não estiver disponível na API ou for zero
        let margemLiquidaFinal = safeMath.toNumber(contrato.analise_financeira.margem_liquida);
        
        if (margemLiquidaFinal === 0) {
          // Recalcular manualmente: faturamento - suprimentos
          const faturamento = safeMath.toNumber(contrato.valores_contratuais.faturamento_proporcional);
          const suprimentos = safeMath.toNumber(contrato.analise_financeira.custo_suprimentos);
          margemLiquidaFinal = safeMath.subtract(faturamento, suprimentos);
        }

        const contratoProcessado: ContratoCompleto = {
          ...contrato,
          valor_mensal: safeMath.toNumber(contrato.valores_contratuais.valor_mensal),
          faturamento_periodo: safeMath.toNumber(contrato.valores_contratuais.faturamento_proporcional),
          suprimentos_valor: safeMath.toNumber(contrato.analise_financeira.custo_suprimentos),
          margem_liquida: margemLiquidaFinal,
          percentual_margem: safeMath.toNumber(contrato.analise_financeira.percentual_margem)
        };

        if (clienteMap.has(clienteId)) {
          const clienteExistente = clienteMap.get(clienteId)!;
          clienteExistente.contratos.push(contratoProcessado);
          clienteExistente.totalContratos++;
          clienteExistente.faturamentoTotal = safeMath.add(clienteExistente.faturamentoTotal, contrato.valores_contratuais.faturamento_proporcional);
          clienteExistente.despesasSuprimentos = safeMath.add(clienteExistente.despesasSuprimentos, contrato.analise_financeira.custo_suprimentos);
          clienteExistente.margemLiquida = safeMath.add(clienteExistente.margemLiquida, margemLiquidaFinal);
        } else {
          clienteMap.set(clienteId, {
            clienteId,
            clienteNome,
            contratos: [contratoProcessado],
            totalContratos: 1,
            faturamentoTotal: safeMath.toNumber(contrato.valores_contratuais.faturamento_proporcional),
            despesasSuprimentos: safeMath.toNumber(contrato.analise_financeira.custo_suprimentos),
            margemLiquida: margemLiquidaFinal,
            percentualMargem: 0 // Será calculado abaixo
          });
        }
      });

      // Calcular percentual de margem para cada cliente
      // E recalcular margem líquida se necessário
      clienteMap.forEach((cliente) => {
        // Recalcular margem se estiver zerada mas há faturamento
        if (cliente.margemLiquida === 0 && cliente.faturamentoTotal > 0) {
          cliente.margemLiquida = safeMath.subtract(cliente.faturamentoTotal, cliente.despesasSuprimentos);
        }
        
        cliente.percentualMargem = safeMath.percentage(cliente.margemLiquida, cliente.faturamentoTotal);
      });

      const clientesArray = Array.from(clienteMap.values()).sort((a, b) => b.faturamentoTotal - a.faturamentoTotal);
      setClientesAgrupados(clientesArray);

      // Calcular resumo financeiro
      const totalClientes = clientesArray.length;
      const totalContratos = data.resumo?.total_contratos_vigentes || 0;
      const faturamentoTotal = data.resumo_financeiro?.faturamento_total_proporcional || 0;
      const despesasTotal = data.resumo_financeiro?.custo_total_suprimentos || 0;
      const margemTotal = data.resumo_financeiro?.margem_bruta_total || 0;
      const percentualMargem = data.resumo_financeiro?.percentual_margem_total || 0;

      setResumoFinanceiro({
        totalClientes,
        totalContratos,
        faturamentoTotal,
        despesasTotal,
        margemTotal,
        percentualMargem
      });

    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido ao carregar dados');
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

  // Função para preparar dados para gráficos
  const prepararDadosGraficos = () => {
    return clientesAgrupados.slice(0, 10).map((cliente) => ({
      nome: cliente.clienteNome.length > 20 ? cliente.clienteNome.substring(0, 20) + '...' : cliente.clienteNome,
      faturamento: cliente.faturamentoTotal,
      suprimentos: cliente.despesasSuprimentos,
      margem: cliente.margemLiquida
    }));
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C', '#8DD1E1', '#D084D0'];

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '32px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '48px', 
            height: '48px', 
            border: '2px solid #e5e7eb', 
            borderTop: '2px solid #3b82f6', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px auto'
          }}></div>
          <p style={{ color: '#6b7280' }}>Carregando dados dos contratos...</p>
        </div>
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
          Contratos por Cliente
        </h1>
        <p style={{ color: '#6b7280' }}>
          Análise detalhada dos contratos de locação organizados por cliente
        </p>
      </div>

      {/* Filtros de Período */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText style={{ width: '20px', height: '20px' }} />
          Filtros de Período
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>Período de Análise</label>
            <SeparateDatePicker
              date={dateRange}
              onDateChange={(newRange) => newRange && setDateRange(newRange)}
            />
          </div>
          <button
            onClick={carregarDados}
            disabled={loading}
            style={{
              padding: '8px 16px',
              backgroundColor: loading ? '#9ca3af' : '#3b82f6',
              color: 'white',
              borderRadius: '6px',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.875rem',
              fontWeight: '500',
              alignSelf: 'flex-start'
            }}
          >
            {loading ? (
              <>
                <div style={{ 
                  width: '16px', 
                  height: '16px', 
                  border: '2px solid #ffffff', 
                  borderTop: '2px solid transparent', 
                  borderRadius: '50%', 
                  animation: 'spin 1s linear infinite'
                }}></div>
                Carregando...
              </>
            ) : (
              <>
                <FileText style={{ width: '16px', height: '16px' }} />
                Atualizar Dados
              </>
            )}
          </button>
        </div>
      </div>

      {/* Cards de Resumo */}
      {resumoFinanceiro && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '16px',
          marginBottom: '24px'
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <Users style={{ width: '32px', height: '32px', color: '#3b82f6' }} />
              <div style={{ marginLeft: '12px' }}>
                <p style={{ fontSize: '0.875rem', fontWeight: '500', color: '#6b7280' }}>Clientes</p>
                <p style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{resumoFinanceiro.totalClientes}</p>
              </div>
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <FileText style={{ width: '32px', height: '32px', color: '#10b981' }} />
              <div style={{ marginLeft: '12px' }}>
                <p style={{ fontSize: '0.875rem', fontWeight: '500', color: '#6b7280' }}>Contratos</p>
                <p style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{resumoFinanceiro.totalContratos}</p>
              </div>
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <DollarSign style={{ width: '32px', height: '32px', color: '#3b82f6' }} />
              <div style={{ marginLeft: '12px' }}>
                <p style={{ fontSize: '0.875rem', fontWeight: '500', color: '#6b7280' }}>Faturamento</p>
                <p style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{formatCurrency(resumoFinanceiro.faturamentoTotal)}</p>
              </div>
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <TrendingUp style={{ width: '32px', height: '32px', color: '#10b981' }} />
              <div style={{ marginLeft: '12px' }}>
                <p style={{ fontSize: '0.875rem', fontWeight: '500', color: '#6b7280' }}>% Margem</p>
                <p style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{formatPercent(resumoFinanceiro.percentualMargem)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navegação entre diferentes visualizações */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{
          display: 'flex',
          gap: '8px',
          backgroundColor: '#f3f4f6',
          padding: '4px',
          borderRadius: '8px',
          width: 'fit-content'
        }}>
          <button
            onClick={() => setActiveTab('clientes')}
            style={{
              padding: '8px 16px',
              border: 'none',
              backgroundColor: activeTab === 'clientes' ? '#3b82f6' : 'transparent',
              color: activeTab === 'clientes' ? 'white' : '#6b7280',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            Por Cliente
          </button>
          <button
            onClick={() => setActiveTab('graficos')}
            style={{
              padding: '8px 16px',
              border: 'none',
              backgroundColor: activeTab === 'graficos' ? '#3b82f6' : 'transparent',
              color: activeTab === 'graficos' ? 'white' : '#6b7280',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            Gráficos
          </button>
          <button
            onClick={() => setActiveTab('detalhes')}
            style={{
              padding: '8px 16px',
              border: 'none',
              backgroundColor: activeTab === 'detalhes' ? '#3b82f6' : 'transparent',
              color: activeTab === 'detalhes' ? 'white' : '#6b7280',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            Detalhes
          </button>
        </div>
      </div>

      {/* Aba: Por Cliente */}
      {activeTab === 'clientes' && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '24px'
        }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>
            Contratos Agrupados por Cliente
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}></th>
                  <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Cliente</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Contratos</th>
                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Faturamento Período</th>
                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Suprimentos</th>
                  <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Margem Líquida</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>% Margem</th>
                </tr>
              </thead>
              <tbody>
                {clientesAgrupados.map((cliente, index) => (
                  <React.Fragment key={cliente.clienteId}>
                    <tr style={{
                      borderBottom: '1px solid #e2e8f0',
                      backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8fafc',
                      cursor: 'pointer'
                    }} onClick={() => toggleClienteExpansao(cliente.clienteId)}>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        {clientesExpandidos.has(cliente.clienteId) ? 
                          <ChevronDown style={{ width: '16px', height: '16px', color: '#6b7280' }} /> : 
                          <ChevronRight style={{ width: '16px', height: '16px', color: '#6b7280' }} />
                        }
                      </td>
                      <td style={{ padding: '12px', fontWeight: '500', color: '#111827' }}>
                        {cliente.clienteNome}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', color: '#6b7280' }}>
                        {cliente.totalContratos}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#059669' }}>
                        {formatCurrency(safeMath.toNumber(cliente.faturamentoTotal))}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#dc2626' }}>
                        {formatCurrency(safeMath.toNumber(cliente.despesasSuprimentos))}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontWeight: '700', color: safeMath.toNumber(cliente.margemLiquida) >= 0 ? '#059669' : '#dc2626' }}>
                        {formatCurrency(safeMath.toNumber(cliente.margemLiquida))}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          backgroundColor: safeMath.toNumber(cliente.percentualMargem) >= 70 ? '#dcfce7' : 
                                          safeMath.toNumber(cliente.percentualMargem) >= 50 ? '#fef3c7' : '#fecaca',
                          color: safeMath.toNumber(cliente.percentualMargem) >= 70 ? '#166534' : 
                                 safeMath.toNumber(cliente.percentualMargem) >= 50 ? '#92400e' : '#991b1b'
                        }}>
                          {formatPercent(safeMath.toNumber(cliente.percentualMargem))}
                        </span>
                      </td>
                    </tr>

                    {/* Detalhes expandidos dos contratos do cliente */}
                    {clientesExpandidos.has(cliente.clienteId) && cliente.contratos.map((contrato) => (
                      <tr key={contrato.contrato_id} style={{ backgroundColor: '#f1f5f9', borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '8px 12px' }}></td>
                        <td style={{ padding: '8px 12px', fontSize: '0.875rem', color: '#64748b' }}>
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontWeight: '500' }}>📋 {contrato.contrato_numero}</span>
                            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                              {new Date(contrato.vigencia.inicio).toLocaleDateString('pt-BR')} - {new Date(contrato.vigencia.fim).toLocaleDateString('pt-BR')}
                            </span>
                          </div>
                        </td>
                        <td style={{ padding: '8px 12px', textAlign: 'center', fontSize: '0.875rem', color: '#64748b' }}>
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontWeight: '500' }}>R$ {contrato.valor_mensal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>valor mensal</span>
                          </div>
                        </td>
                        <td style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '500', color: '#059669' }}>
                          {formatCurrency(contrato.faturamento_periodo)}
                        </td>
                        <td style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '500', color: '#dc2626' }}>
                          {formatCurrency(contrato.suprimentos_valor)}
                        </td>
                        <td style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: contrato.margem_liquida >= 0 ? '#059669' : '#dc2626' }}>
                          {formatCurrency(contrato.margem_liquida)}
                        </td>
                        <td style={{ padding: '8px 12px', textAlign: 'center', fontSize: '0.875rem', fontWeight: '500', color: '#64748b' }}>
                          {formatPercent(contrato.percentual_margem)}
                        </td>
                      </tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Aba: Gráficos */}
      {activeTab === 'graficos' && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', 
          gap: '24px'
        }}>
          {/* Gráfico de Barras */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '24px'
          }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>
              Top 10 Clientes - Faturamento vs Suprimentos
            </h3>
            <div style={{ width: '100%', height: '400px' }}>
              <ResponsiveContainer>
                <BarChart data={prepararDadosGraficos()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="nome" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number, name: string) => [formatCurrency(value), name]}
                  />
                  <Legend />
                  <Bar dataKey="faturamento" fill="#3b82f6" name="Faturamento" />
                  <Bar dataKey="suprimentos" fill="#ef4444" name="Suprimentos" />
                  <Bar dataKey="margem" fill="#10b981" name="Margem" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Gráfico de Pizza */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '24px'
          }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>
              Distribuição do Faturamento
            </h3>
            <div style={{ width: '100%', height: '400px' }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={prepararDadosGraficos()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ nome, percent }) => `${nome}: ${((percent || 0) * 100).toFixed(0)}%`}
                    outerRadius={150}
                    fill="#8884d8"
                    dataKey="faturamento"
                  >
                    {prepararDadosGraficos().map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Aba: Detalhes */}
      {activeTab === 'detalhes' && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '24px'
        }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>
            Detalhes dos Dados
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px'
            }}>
              <div style={{
                backgroundColor: '#faf5ff',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #e9d5ff'
              }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#6b46c1', marginBottom: '4px' }}>
                  Total Faturamento
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#581c87' }}>
                  {resumoFinanceiro && formatCurrency(resumoFinanceiro.faturamentoTotal)}
                </div>
              </div>
              <div style={{
                backgroundColor: '#fef2f2',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #fecaca'
              }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#dc2626', marginBottom: '4px' }}>
                  Total Despesas
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#7f1d1d' }}>
                  {resumoFinanceiro && formatCurrency(resumoFinanceiro.despesasTotal)}
                </div>
              </div>
              <div style={{
                backgroundColor: '#fffbeb',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #fed7aa'
              }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#d97706', marginBottom: '4px' }}>
                  Margem Líquida
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#92400e' }}>
                  {resumoFinanceiro && formatCurrency(resumoFinanceiro.margemTotal)}
                </div>
              </div>
            </div>

            {/* Informações adicionais sobre os dados */}
            {dateRange && (
              <div style={{
                backgroundColor: '#f0f9ff',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #bae6fd'
              }}>
                <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#0c4a6e', marginBottom: '8px' }}>
                  Período da Análise
                </h4>
                <p style={{ color: '#0369a1', fontSize: '0.875rem' }}>
                  De {dateRange.from?.toLocaleDateString('pt-BR')} até {dateRange.to?.toLocaleDateString('pt-BR')}
                </p>
                <p style={{ color: '#075985', fontSize: '0.75rem', marginTop: '4px' }}>
                  Dados obtidos em tempo real da API de contratos
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractsDashboardReal;
