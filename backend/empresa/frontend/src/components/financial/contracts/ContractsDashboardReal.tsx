// src/components/financial/contracts/ContractsDashboardReal.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../ui/tabs";
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
  DollarSign,
  AlertCircle
} from "lucide-react";
import { Alert, AlertDescription } from '../../ui/alert';
import { SeparateDatePicker } from '../../common/SeparateDatePicker';

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
    ativo_no_periodo: boolean;
    periodo_efetivo: {
      inicio: string;
      fim: string;
      dias_vigentes: number;
    };
    meses_no_periodo: number;
  };
  valores_contratuais: {
    valor_mensal: number;
    valor_total_contrato: number;
    numero_parcelas: string;
    faturamento_proporcional: number;
    calculo: string;
  };
  analise_financeira: {
    faturamento_proporcional: number;
    custo_suprimentos: number;
    margem_bruta: number;
    percentual_margem: number;
    observacao: string;
  };
}

interface RespostaVigencia {
  periodo: {
    data_inicial: string;
    data_final: string;
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
  cliente: string;
  contratos: ContratoCompleto[];
  faturamentoTotal: number;
  despesasSuprimentos: number;
  quantidadeContratos: number;
  margemLiquida: number;
  percentualMargem: number;
}

interface ContratoCompleto {
  contrato_id: number;
  contrato_numero: string;
  valor_mensal: number;
  faturamento_periodo: number;
  suprimentos_valor: number;
  margem_liquida: number;
  percentual_margem: number;
  vigencia: {
    inicio: string;
    fim: string;
    ativo: boolean;
    dias_vigentes: number;
  };
  status: string;
  notas_suprimentos: NotaSuprimento[];
}

interface DateRange {
  from: Date;
  to: Date;
}

interface ResumoFinanceiro {
  totalClientes: number;
  totalContratos: number;
  faturamentoTotal: number;
  despesasTotal: number;
  margemTotal: number;
  percentualMargem: number;
}

const ContractsDashboardReal: React.FC = () => {
  const [clientesAgrupados, setClientesAgrupados] = useState<ClienteAgrupado[]>([]);
  const [resumoFinanceiro, setResumoFinanceiro] = useState<ResumoFinanceiro | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [activeTab, setActiveTab] = useState("clientes");

  const defaultFrom = new Date('2025-08-01T00:00:00');
  const defaultTo = new Date('2025-08-31T23:59:59');
  const [dateRange, setDateRange] = useState<DateRange>({
    from: defaultFrom,
    to: defaultTo
  });

  // Função para formatar moeda
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  // Função para formatar porcentagem com verificação de segurança
  const formatPercent = (value: number) => {
    if (isNaN(value) || !isFinite(value)) {
      return '0.0%';
    }
    return `${value.toFixed(1)}%`;
  };

  // Função para carregar dados de vigência
  const carregarDadosVigencia = async (dataInicial: string, dataFinal: string): Promise<RespostaVigencia> => {
    const url = `http://localhost:8000/api/contratos_locacao/suprimentos/?data_inicial=${dataInicial}&data_final=${dataFinal}`;
    console.log('🔄 Carregando dados de vigência:', url);
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Erro na API de vigência: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Dados de vigência carregados:', data);
    return data;
  };

  // Função principal para carregar e processar dados
  const carregarDados = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const dataInicial = dateRange.from.toISOString().split('T')[0];
      const dataFinal = dateRange.to.toISOString().split('T')[0];
      
      console.log('📅 Período selecionado:', dataInicial, 'até', dataFinal);

      // Como o endpoint retorna dados combinados, vamos usar apenas um
      const dadosVigencia = await carregarDadosVigencia(dataInicial, dataFinal);
      
      // Processar dados dos contratos por cliente
      const clientesMap = new Map<number, ClienteAgrupado>();
      
      if (dadosVigencia.resultados) {
        dadosVigencia.resultados.forEach((contrato: ContratoVigencia) => {
          const clienteId = contrato.cliente?.id;
          const clienteNome = contrato.cliente?.nome || 'Cliente não informado';
          
          if (!clienteId) return;
          
          console.log(`✅ PROCESSANDO CONTRATO ${contrato.contrato_numero}:`);
          console.log(`👤 Cliente: ${clienteNome}`);
          console.log(`💰 Valor mensal: R$ ${contrato.valores_contratuais.valor_mensal}`);
          console.log(`💹 Faturamento: R$ ${contrato.valores_contratuais.faturamento_proporcional}`);
          console.log(`💸 Suprimentos: R$ ${contrato.analise_financeira.custo_suprimentos}`);
          console.log(`📈 Margem: R$ ${contrato.analise_financeira.margem_bruta} (${contrato.analise_financeira.percentual_margem.toFixed(1)}%)`);
          
          const contratoCompleto: ContratoCompleto = {
            contrato_id: contrato.contrato_id,
            contrato_numero: contrato.contrato_numero,
            valor_mensal: contrato.valores_contratuais.valor_mensal,
            faturamento_periodo: contrato.valores_contratuais.faturamento_proporcional,
            suprimentos_valor: contrato.analise_financeira.custo_suprimentos,
            margem_liquida: contrato.analise_financeira.margem_bruta,
            percentual_margem: contrato.analise_financeira.percentual_margem,
            vigencia: {
              inicio: contrato.vigencia.inicio,
              fim: contrato.vigencia.fim,
              ativo: contrato.vigencia.ativo_no_periodo,
              dias_vigentes: contrato.vigencia.periodo_efetivo?.dias_vigentes || 0
            },
            status: contrato.vigencia.ativo_no_periodo ? 'Ativo' : 'Inativo',
            notas_suprimentos: [] // Será preenchido depois se necessário
          };
          
          if (clientesMap.has(clienteId)) {
            const clienteExistente = clientesMap.get(clienteId)!;
            clienteExistente.contratos.push(contratoCompleto);
            clienteExistente.faturamentoTotal += contrato.valores_contratuais.faturamento_proporcional;
            clienteExistente.despesasSuprimentos += contrato.analise_financeira.custo_suprimentos;
            clienteExistente.quantidadeContratos += 1;
            clienteExistente.margemLiquida = clienteExistente.faturamentoTotal - clienteExistente.despesasSuprimentos;
            clienteExistente.percentualMargem = clienteExistente.faturamentoTotal > 0 ? 
              (clienteExistente.margemLiquida / clienteExistente.faturamentoTotal) * 100 : 0;
          } else {
            const margemLiquida = contrato.valores_contratuais.faturamento_proporcional - contrato.analise_financeira.custo_suprimentos;
            const percentualMargem = contrato.valores_contratuais.faturamento_proporcional > 0 ? 
              (margemLiquida / contrato.valores_contratuais.faturamento_proporcional) * 100 : 0;
              
            clientesMap.set(clienteId, {
              clienteId,
              cliente: clienteNome,
              contratos: [contratoCompleto],
              faturamentoTotal: contrato.valores_contratuais.faturamento_proporcional,
              despesasSuprimentos: contrato.analise_financeira.custo_suprimentos,
              quantidadeContratos: 1,
              margemLiquida,
              percentualMargem
            });
          }
        });
      }

      const clientesArray = Array.from(clientesMap.values())
        .sort((a, b) => b.faturamentoTotal - a.faturamentoTotal);

      setClientesAgrupados(clientesArray);

      // Calcular resumo financeiro
      const totalClientes = clientesArray.length;
      const totalContratos = dadosVigencia.resumo?.total_contratos_vigentes || 0;
      const faturamentoTotal = dadosVigencia.resumo_financeiro?.faturamento_total_proporcional || 0;
      const despesasTotal = dadosVigencia.resumo_financeiro?.custo_total_suprimentos || 0;
      const margemTotal = dadosVigencia.resumo_financeiro?.margem_bruta_total || 0;
      const percentualMargem = dadosVigencia.resumo_financeiro?.percentual_margem_total || 0;

      setResumoFinanceiro({
        totalClientes,
        totalContratos,
        faturamentoTotal,
        despesasTotal,
        margemTotal,
        percentualMargem
      });

      console.log(`📊 RESUMO FINAL:`);
      console.log(`👥 Total de clientes: ${totalClientes}`);
      console.log(`📋 Total de contratos: ${totalContratos}`);
      console.log(`💰 Faturamento total: R$ ${faturamentoTotal.toFixed(2)}`);
      console.log(`💸 Despesas total: R$ ${despesasTotal.toFixed(2)}`);
      console.log(`📈 Margem total: R$ ${margemTotal.toFixed(2)} (${percentualMargem.toFixed(1)}%)`);

    } catch (error) {
      console.error('❌ Erro ao carregar dados de contratos:', error);
      setError(`Erro ao carregar dados: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  // Carregar dados quando o componente monta ou quando o período muda
  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

  // Função para alternar expansão de linha
  const toggleRowExpansion = (clienteId: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(clienteId)) {
      newExpanded.delete(clienteId);
    } else {
      newExpanded.add(clienteId);
    }
    setExpandedRows(newExpanded);
  };

  // Função para preparar dados para gráficos
  const prepararDadosGraficos = () => {
    return clientesAgrupados.slice(0, 10).map(cliente => ({
      cliente: cliente.cliente.length > 20 ? cliente.cliente.substring(0, 20) + '...' : cliente.cliente,
      faturamento: cliente.faturamentoTotal,
      suprimentos: cliente.despesasSuprimentos,
      margem: cliente.margemLiquida
    }));
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C', '#8DD1E1', '#D084D0'];

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados dos contratos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="m-4">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Filtros de Data */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Contratos por Cliente - Dados Reais
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-end">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Período de Análise</label>
              <SeparateDatePicker
                date={dateRange}
                onDateChange={(newRange) => newRange && setDateRange(newRange)}
              />
            </div>
            <button
              onClick={carregarDados}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Carregando...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Atualizar Dados
                </>
              )}
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Cards de Resumo */}
      {resumoFinanceiro && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Users className="h-8 w-8 text-blue-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600">Clientes</p>
                  <p className="text-2xl font-bold text-gray-900">{resumoFinanceiro.totalClientes}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <FileText className="h-8 w-8 text-green-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600">Contratos</p>
                  <p className="text-2xl font-bold text-gray-900">{resumoFinanceiro.totalContratos}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <DollarSign className="h-8 w-8 text-blue-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600">Faturamento</p>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(resumoFinanceiro.faturamentoTotal)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-green-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600">% Margem</p>
                  <p className="text-2xl font-bold text-gray-900">{formatPercent(resumoFinanceiro.percentualMargem)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs para diferentes visualizações */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="clientes">Por Cliente</TabsTrigger>
          <TabsTrigger value="graficos">Gráficos</TabsTrigger>
          <TabsTrigger value="detalhes">Detalhes</TabsTrigger>
        </TabsList>

        {/* Aba: Por Cliente */}
        <TabsContent value="clientes" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Contratos Agrupados por Cliente</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
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
                    {clientesAgrupados.map((cliente) => (
                      <React.Fragment key={cliente.clienteId}>
                        {/* Linha principal do cliente */}
                        <tr 
                          style={{ borderBottom: '1px solid #f3f4f6', cursor: 'pointer' }}
                          onClick={() => toggleRowExpansion(cliente.clienteId)}
                        >
                          <td style={{ padding: '12px', textAlign: 'center' }}>
                            {expandedRows.has(cliente.clienteId) ? (
                              <ChevronDown className="w-4 h-4 text-gray-500" />
                            ) : (
                              <ChevronRight className="w-4 h-4 text-gray-500" />
                            )}
                          </td>
                          <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', fontWeight: '500' }}>
                            {cliente.cliente}
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                              ID: {cliente.clienteId}
                            </div>
                          </td>
                          <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', textAlign: 'center' }}>
                            {cliente.quantidadeContratos}
                          </td>
                          <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', textAlign: 'right' }}>
                            {formatCurrency(cliente.faturamentoTotal)}
                          </td>
                          <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', textAlign: 'right' }}>
                            {formatCurrency(cliente.despesasSuprimentos)}
                          </td>
                          <td style={{ 
                            padding: '12px', 
                            fontSize: '0.875rem', 
                            textAlign: 'right',
                            fontWeight: '600',
                            color: cliente.margemLiquida >= 0 ? '#059669' : '#dc2626'
                          }}>
                            {formatCurrency(cliente.margemLiquida)}
                          </td>
                          <td style={{ 
                            padding: '12px', 
                            fontSize: '0.875rem', 
                            textAlign: 'center',
                            fontWeight: '600',
                            color: cliente.margemLiquida >= 0 ? '#059669' : '#dc2626'
                          }}>
                            {formatPercent(cliente.percentualMargem)}
                          </td>
                        </tr>

                        {/* Linha expandida - Contratos do cliente */}
                        {expandedRows.has(cliente.clienteId) && (
                          <tr>
                            <td 
                              colSpan={7} 
                              style={{ 
                                backgroundColor: '#f8fafc',
                                padding: '0',
                                borderBottom: '1px solid #f3f4f6'
                              }}
                            >
                              <div style={{ padding: '16px' }}>
                                <h4 style={{ 
                                  fontWeight: '600', 
                                  marginBottom: '12px',
                                  fontSize: '0.875rem',
                                  color: '#111827'
                                }}>
                                  Contratos de {cliente.cliente}
                                </h4>
                                <table style={{ 
                                  width: '100%', 
                                  borderCollapse: 'collapse' as const,
                                  fontSize: '0.875rem'
                                }}>
                                  <thead>
                                    <tr style={{ backgroundColor: '#f9fafb' }}>
                                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Contrato</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Valor Mensal</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Período</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Status</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Faturamento</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Suprimentos</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Margem</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {cliente.contratos.map((contrato) => (
                                      <tr key={contrato.contrato_id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                                        <td style={{ padding: '8px 12px', fontFamily: 'monospace', fontSize: '0.75rem', color: '#111827' }}>
                                          {contrato.contrato_numero}
                                        </td>
                                        <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                          {formatCurrency(contrato.valor_mensal)}
                                        </td>
                                        <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                          {new Date(contrato.vigencia.inicio).toLocaleDateString()} - {' '}
                                          {new Date(contrato.vigencia.fim).toLocaleDateString()}
                                          <div style={{ fontSize: '0.65rem', color: '#6b7280' }}>
                                            {contrato.vigencia.dias_vigentes} dias
                                          </div>
                                        </td>
                                        <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                          <span style={{
                                            padding: '2px 8px',
                                            borderRadius: '9999px',
                                            fontSize: '0.75rem',
                                            backgroundColor: contrato.status === 'Ativo' ? '#dcfce7' : '#f3f4f6',
                                            color: contrato.status === 'Ativo' ? '#166534' : '#374151'
                                          }}>
                                            {contrato.status}
                                          </span>
                                        </td>
                                        <td style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', color: '#111827' }}>
                                          {formatCurrency(contrato.faturamento_periodo)}
                                        </td>
                                        <td style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', color: '#111827' }}>
                                          {formatCurrency(contrato.suprimentos_valor)}
                                        </td>
                                        <td style={{ 
                                          padding: '8px 12px', 
                                          textAlign: 'right', 
                                          fontSize: '0.75rem',
                                          fontWeight: '600',
                                          color: contrato.margem_liquida >= 0 ? '#059669' : '#dc2626'
                                        }}>
                                          {formatCurrency(contrato.margem_liquida)}
                                          <div style={{ fontSize: '0.65rem', fontWeight: '400' }}>
                                            {formatPercent(contrato.percentual_margem)}
                                          </div>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba: Gráficos */}
        <TabsContent value="graficos" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico de Barras */}
            <Card>
              <CardHeader>
                <CardTitle>Top 10 Clientes - Faturamento vs Suprimentos</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={prepararDadosGraficos()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="cliente" 
                      angle={-45}
                      textAnchor="end"
                      height={100}
                      interval={0}
                    />
                    <YAxis 
                      tickFormatter={(value) => `R$ ${(value / 1000).toFixed(0)}k`}
                    />
                    <Tooltip 
                      formatter={(value: number, name: string) => [formatCurrency(value), name]}
                      labelFormatter={(label) => `Cliente: ${label}`}
                    />
                    <Legend />
                    <Bar dataKey="faturamento" fill="#3b82f6" name="Faturamento" />
                    <Bar dataKey="suprimentos" fill="#ef4444" name="Suprimentos" />
                    <Bar dataKey="margem" fill="#10b981" name="Margem" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Gráfico de Pizza */}
            <Card>
              <CardHeader>
                <CardTitle>Distribuição de Faturamento por Cliente</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={prepararDadosGraficos()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ cliente, percent }) => `${cliente}: ${((percent || 0) * 100).toFixed(0)}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="faturamento"
                    >
                      {prepararDadosGraficos().map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Aba: Detalhes */}
        <TabsContent value="detalhes" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Detalhes dos Dados</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold mb-2">Fonte dos Dados</h3>
                  <p className="text-gray-600">
                    Os dados são obtidos diretamente da API Django REST Framework do endpoint:
                    <code className="ml-2 px-2 py-1 bg-gray-100 rounded text-sm">
                      /api/contratos_locacao/suprimentos/
                    </code>
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2">Período Analisado</h3>
                  <p className="text-gray-600">
                    {dateRange.from.toLocaleDateString()} até {dateRange.to.toLocaleDateString()}
                  </p>
                </div>

                {resumoFinanceiro && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Resumo Estatístico</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="p-4 bg-blue-50 rounded">
                        <div className="text-sm text-blue-600 font-medium">Total de Clientes</div>
                        <div className="text-xl font-bold text-blue-900">{resumoFinanceiro.totalClientes}</div>
                      </div>
                      <div className="p-4 bg-green-50 rounded">
                        <div className="text-sm text-green-600 font-medium">Total de Contratos</div>
                        <div className="text-xl font-bold text-green-900">{resumoFinanceiro.totalContratos}</div>
                      </div>
                      <div className="p-4 bg-purple-50 rounded">
                        <div className="text-sm text-purple-600 font-medium">Faturamento Total</div>
                        <div className="text-xl font-bold text-purple-900">{formatCurrency(resumoFinanceiro.faturamentoTotal)}</div>
                      </div>
                      <div className="p-4 bg-red-50 rounded">
                        <div className="text-sm text-red-600 font-medium">Despesas com Suprimentos</div>
                        <div className="text-xl font-bold text-red-900">{formatCurrency(resumoFinanceiro.despesasTotal)}</div>
                      </div>
                      <div className="p-4 bg-yellow-50 rounded">
                        <div className="text-sm text-yellow-600 font-medium">Margem Líquida</div>
                        <div className="text-xl font-bold text-yellow-900">{formatCurrency(resumoFinanceiro.margemTotal)}</div>
                      </div>
                      <div className="p-4 bg-indigo-50 rounded">
                        <div className="text-sm text-indigo-600 font-medium">% Margem</div>
                        <div className="text-xl font-bold text-indigo-900">{formatPercent(resumoFinanceiro.percentualMargem)}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ContractsDashboardReal;
