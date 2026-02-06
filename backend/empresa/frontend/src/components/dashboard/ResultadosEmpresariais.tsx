// src/components/dashboard/ResultadosEmpresariais.tsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Package,
  FileText,
  DollarSign,
  Calculator,
  AlertCircle,
  Info,
  X
} from "lucide-react";
import { SeparateDatePicker } from '../common/SeparateDatePicker';

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
if (typeof document !== 'undefined' && !document.getElementById('resultados-animations')) {
  const styleElement = document.createElement('style');
  styleElement.id = 'resultados-animations';
  styleElement.textContent = spinKeyframes;
  document.head.appendChild(styleElement);
}

// Interfaces para os dados dos endpoints
interface MovimentacaoEstoque {
  valor_entrada: number;
  valor_saida: number;
  valor_saida_preco_entrada: number;
  saldo_periodo: number;
  lucro_operacional: number;
  margem_percentual: number;
  // Variação calculada por snapshots (valor_total_estoque fim - início)
  variacao_snapshot?: number;
}


interface FaturamentoContratos {
  faturamento_total_proporcional: number;
  custo_total_suprimentos: number;
  margem_bruta_total: number;
  percentual_margem_total: number;
  contratos?: any[];
}

// Interface para detalhes da conta
interface ContaDetalhada {
  id: number;
  data_pagamento: string;
  fornecedor_nome: string;
  fornecedor_tipo: string;
  fornecedor_especificacao: string;
  valor_original: number;
  valor_pago: number;
  juros: number;
  tarifas: number;
  historico: string;
  forma_pagamento: string;
}

interface CustosFixos {
  valor_total: number;
  periodo_inicio: string;
  periodo_fim: string;
  especificacoes: Array<{
    especificacao: string;
    valor_pago_total: number;
    quantidade_contas: number;
    incluir_no_calculo: boolean;
  }>;
  contas_pagas: ContaDetalhada[];
}

interface CustosVariaveis {
  periodo_inicio: string;
  periodo_fim: string;
  valor_total_geral: number;
  especificacoes: Array<{
    especificacao: string;
    valor_pago_total: number;
    quantidade_contas: number;
    incluir_no_calculo: boolean;
  }>;
  contas_pagas: ContaDetalhada[];
}

interface MargemVendas {
  valor_vendas: number;
  valor_custo_entrada: number;
  valor_preco_entrada: number;
  margem_bruta: number;
  percentual_margem: number;
  itens_analisados: number;
  notas_detalhadas?: {
    vendas: any[];
    compras: any[];
    servicos: any[];
  };
}

interface ResultadoFinal {
  lucro_operacional_estoque: number;
  faturamento_contratos: number;
  custos_fixos: number;
  custos_variaveis: number;
  resultado_liquido: number;
  margem_liquida_percentual: number;
}

const ResultadosEmpresariais: React.FC = () => {
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
    to: new Date()
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estados para os dados
  const [movimentacaoEstoque, setMovimentacaoEstoque] = useState<MovimentacaoEstoque | null>(null);
  const [faturamentoContratos, setFaturamentoContratos] = useState<FaturamentoContratos | null>(null);
  const [custosFixos, setCustosFixos] = useState<CustosFixos | null>(null);
  const [custosVariaveis, setCustosVariaveis] = useState<CustosVariaveis | null>(null);
  const [margemVendas, setMargemVendas] = useState<MargemVendas | null>(null);
  const [resultadoFinal, setResultadoFinal] = useState<ResultadoFinal | null>(null);

  // Estados para o Modal de Detalhes
  const [modalOpen, setModalOpen] = useState(false);
  const [categoriaSelecionada, setCategoriaSelecionada] = useState<{ nome: string; tipo: 'FIXO' | 'VARIAVEL' | 'CONTRATOS' | 'VENDAS' | 'SUPRIMENTOS_CONTRATOS' | 'CUSTO_VENDA' } | null>(null);
  const [itensModal, setItensModal] = useState<ContaDetalhada[] | any[]>([]);

  // Função para alternar inclusão de especificação nos custos fixos
  const toggleCustoFixo = (especificacao: string) => {
    if (!custosFixos) return;

    setCustosFixos(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        especificacoes: prev.especificacoes.map(spec =>
          spec.especificacao === especificacao
            ? { ...spec, incluir_no_calculo: !spec.incluir_no_calculo }
            : spec
        )
      };
    });
  };

  // Função para alternar inclusão de especificação nos custos variáveis
  const toggleCustoVariavel = (especificacao: string) => {
    if (!custosVariaveis) return;

    setCustosVariaveis(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        especificacoes: prev.especificacoes.map(spec =>
          spec.especificacao === especificacao
            ? { ...spec, incluir_no_calculo: !spec.incluir_no_calculo }
            : spec
        )
      };
    });
  };

  // Função para calcular resultados com base nas especificações selecionadas
  const calcularResultados = useCallback(() => {
    if (!custosFixos || !custosVariaveis || !faturamentoContratos || !movimentacaoEstoque || !margemVendas) return;

    // Totais na 1ª linha
    // Totais na 1ª linha (Agora usando MARGEM, conforme solicitado)
    // Formula: Margem Contratos + Margem Venda - Custos Fixos - Custos Variáveis

    // Variáveis para o objeto de estado (mantendo visualização de faturamento)
    const movEstoqueValor = (typeof movimentacaoEstoque.variacao_snapshot === 'number')
      ? movimentacaoEstoque.variacao_snapshot || 0
      : (movimentacaoEstoque.saldo_periodo || 0);
    const faturamentoContratosValor = faturamentoContratos.faturamento_total_proporcional || 0;

    const margemContratosValor = faturamentoContratos.margem_bruta_total || 0;
    const margemVendasValor = margemVendas.margem_bruta || 0;

    // Total positivo (apenas margens, ignorando estoque por enquanto na regra do líquido)
    const totalPrimeiraLinha = margemContratosValor + margemVendasValor;

    // Totais na 2ª linha (respeitando seleção de especificações)
    const custoFixoCalculado = (custosFixos.especificacoes || [])
      .filter(spec => spec.incluir_no_calculo)
      .reduce((total, spec) => total + (spec.valor_pago_total || 0), 0);
    const custoVariavelCalculado = (custosVariaveis.especificacoes || [])
      .filter(spec => spec.incluir_no_calculo)
      .reduce((total, spec) => total + (spec.valor_pago_total || 0), 0);
    const totalSegundaLinha = custoFixoCalculado + custoVariavelCalculado;

    const resultadoLiquido = totalPrimeiraLinha - totalSegundaLinha;
    const margemLiquida = totalPrimeiraLinha > 0 ? (resultadoLiquido / totalPrimeiraLinha) * 100 : 0;

    setResultadoFinal({
      lucro_operacional_estoque: movEstoqueValor,
      faturamento_contratos: faturamentoContratosValor,
      custos_fixos: custoFixoCalculado,
      custos_variaveis: custoVariavelCalculado,
      resultado_liquido: resultadoLiquido,
      margem_liquida_percentual: margemLiquida
    });
  }, [custosFixos, custosVariaveis, faturamentoContratos, movimentacaoEstoque, margemVendas]);

  // Funções de formatação
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  // Função para buscar movimentação de estoque
  const buscarMovimentacaoEstoque = async (dataInicial: string, dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/contas/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }
      const data = await response.json();

      // Se não há movimentação no período, retornar zeros
      if (!data.produtos_movimentados || data.produtos_movimentados.length === 0) {
        return {
          valor_entrada: 0,
          valor_saida: 0,
          valor_saida_preco_entrada: 0,
          saldo_periodo: 0,
          lucro_operacional: 0,
          margem_percentual: 0
        };
      }

      const resumo = data.resumo || {};

      return {
        valor_entrada: resumo.valor_total_entradas || 0,
        valor_saida: resumo.valor_total_saidas || 0,
        valor_saida_preco_entrada: resumo.valor_total_saidas_preco_entrada || 0,
        saldo_periodo: resumo.saldo_periodo || 0,
        lucro_operacional: resumo.diferenca_total_precos || 0,
        margem_percentual: resumo.margem_total || 0
      };
    } catch (error) {
      console.error('Erro ao buscar movimentação de estoque:', error);
      return {
        valor_entrada: 0,
        valor_saida: 0,
        valor_saida_preco_entrada: 0,
        saldo_periodo: 0,
        lucro_operacional: 0,
        margem_percentual: 0
      };
    }
  };

  // Buscar valor total de estoque por data (mesmo endpoint do Controle de Estoque)
  const buscarValorTotalEstoque = async (data: string): Promise<number> => {
    try {
      const resp = await fetch(`http://localhost:8000/contas/estoque-controle/valor_total_estoque/?data=${data}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const json = await resp.json();
      return Number(json?.valor_total_estoque) || 0;
    } catch (e) {
      console.warn('Falha ao buscar valor_total_estoque para', data, e);
      return 0;
    }
  };

  // Função para buscar faturamento de contratos
  const buscarFaturamentoContratos = useCallback(async (dataInicial: string, dataFinal: string) => {
    try {
      console.log('🔍 Buscando faturamento de contratos do endpoint principal (mesma fonte da página contratos)...');

      // Usar o mesmo endpoint e parâmetros da página de contratos de locação
      const url = `http://localhost:8000/api/contratos_locacao/suprimentos/?data_inicial=${dataInicial}&data_final=${dataFinal}`;
      console.log(`🌐 URL: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Dados de contratos recebidos (estrutura completa):', data);

      // Usar a mesma estrutura que a página de contratos usa
      const faturamentoTotal = data.resumo_financeiro?.faturamento_total_proporcional || 0;
      const custoSuprimentosTotal = data.resumo_financeiro?.custo_total_suprimentos || 0;
      const margemBruta = data.resumo_financeiro?.margem_bruta_total || 0;
      const percentualMargem = data.resumo_financeiro?.percentual_margem_total || 0;

      console.log('� Valores extraídos do resumo_financeiro:', {
        faturamento: faturamentoTotal,
        custoSuprimentos: custoSuprimentosTotal,
        margem: margemBruta,
        percentual: percentualMargem
      });

      if (faturamentoTotal > 0) {
        console.log(`✅ Faturamento encontrado: ${faturamentoTotal}`);
        return {
          faturamento_total_proporcional: faturamentoTotal,
          custo_total_suprimentos: custoSuprimentosTotal,
          margem_bruta_total: margemBruta,
          percentual_margem_total: percentualMargem,
          contratos: data.resultados || []
        };
      } else {
        console.warn('⚠️ Endpoint principal retornou faturamento zero, tentando endpoints alternativos...');
        return await buscarFaturamentoFallback(dataInicial, dataFinal);
      }

    } catch (error) {
      console.error('❌ Erro no endpoint principal de contratos:', error);
      console.log('🔄 Tentando endpoints alternativos...');
      return await buscarFaturamentoFallback(dataInicial, dataFinal);
    }
  }, []);

  // Função de fallback para tentar outros endpoints se o principal falhar
  const buscarFaturamentoFallback = async (dataInicial: string, dataFinal: string) => {
    const fallbackEndpoints = [
      {
        url: `http://localhost:8000/contas/relatorios/faturamento/?data_inicio=${dataInicial}&data_fim=${dataFinal}`,
        name: 'relatorio-faturamento'
      },
      {
        url: `http://localhost:8000/contas/fluxo-caixa-realizado/movimentacoes_realizadas/?data_inicio=${dataInicial}&data_fim=${dataFinal}`,
        name: 'movimentacoes-realizadas'
      }
    ];

    for (let i = 0; i < fallbackEndpoints.length; i++) {
      const endpoint = fallbackEndpoints[i];
      try {
        console.log(`🔍 [Fallback ${i + 1}/${fallbackEndpoints.length}] Tentando: ${endpoint.name}`);

        const response = await fetch(endpoint.url);

        if (!response.ok) {
          console.warn(`❌ Fallback [${i + 1}] falhou:`, response.status, response.statusText);
          continue;
        }

        const data = await response.json();
        console.log(`✅ Dados recebidos do fallback [${i + 1}] (${endpoint.name}):`, data);

        let faturamentoTotal = 0;
        let custoSuprimentosTotal = 0;

        if (endpoint.name === 'relatorio-faturamento') {
          faturamentoTotal = data.faturamento_total_proporcional || data.valor_total || data.total || 0;
          custoSuprimentosTotal = data.custo_total_suprimentos || 0;
        } else if (endpoint.name === 'movimentacoes-realizadas') {
          const entradas = data.movimentacoes?.filter((mov: { origem: string }) => mov.origem === 'contas_receber') || [];
          faturamentoTotal = entradas.reduce((total: number, mov: { valor: number }) => total + (mov.valor || 0), 0);
          custoSuprimentosTotal = 0;
        }

        const margemBruta = faturamentoTotal - custoSuprimentosTotal;
        const percentualMargem = faturamentoTotal > 0 ? (margemBruta / faturamentoTotal) * 100 : 0;

        console.log(`📊 Resultado do fallback [${i + 1}]:`, {
          endpoint: endpoint.name,
          faturamento: faturamentoTotal,
          custoSuprimentos: custoSuprimentosTotal,
          margem: margemBruta,
          percentual: percentualMargem
        });

        if (faturamentoTotal > 0) {
          console.log(`✅ Faturamento encontrado no fallback [${i + 1}]: ${faturamentoTotal}`);
          return {
            faturamento_total_proporcional: faturamentoTotal,
            custo_total_suprimentos: custoSuprimentosTotal,
            margem_bruta_total: margemBruta,
            percentual_margem_total: percentualMargem
          };
        }

      } catch (fetchError) {
        console.warn(`🔥 Erro no fallback [${i + 1}] (${endpoint.name}):`, fetchError instanceof Error ? fetchError.message : String(fetchError));
      }
    }

    console.error('❌ Todos os endpoints falharam, retornando valores zero');
    return {
      faturamento_total_proporcional: 0,
      custo_total_suprimentos: 0,
      margem_bruta_total: 0,
      percentual_margem_total: 0
    };
  };

  // Função para buscar custos fixos
  const buscarCustosFixos = async (dataInicial: string, dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/contas/relatorios/custos-fixos/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }
      const data = await response.json();

      console.log('📊 Dados de custos fixos recebidos:', data);

      return {
        valor_total: data.totais_gerais?.total_valor_pago || 0,
        periodo_inicio: data.parametros?.data_inicio || dataInicial,
        periodo_fim: data.parametros?.data_fim || dataFinal,
        especificacoes: (data.resumo_por_tipo_fornecedor || []).map((spec: { fornecedor__tipo: string; total_pago: number; quantidade_contas: number }) => ({
          especificacao: spec.fornecedor__tipo,
          valor_pago_total: spec.total_pago || 0,
          quantidade_contas: spec.quantidade_contas || 0,
          incluir_no_calculo: true // default true
        })),
        contas_pagas: data.contas_pagas || []
      };
    } catch (error) {
      console.error('Erro ao buscar custos fixos:', error);
      return {
        valor_total: 0,
        periodo_inicio: dataInicial,
        periodo_fim: dataFinal,
        especificacoes: [],
        contas_pagas: []
      };
    }
  };

  // Função para buscar custos variáveis
  const buscarCustosVariaveis = async (dataInicial: string, dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/contas/relatorios/custos-variaveis/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }
      const data = await response.json();

      console.log('📊 Dados de custos variáveis recebidos:', data);

      return {
        periodo_inicio: data.parametros?.data_inicio || dataInicial,
        periodo_fim: data.parametros?.data_fim || dataFinal,
        valor_total_geral: data.totais_gerais?.total_valor_pago || 0,
        especificacoes: (data.resumo_por_especificacao || []).map((spec: { especificacao: string; valor_pago_total: number; quantidade_contas: number }) => ({
          especificacao: spec.especificacao,
          valor_pago_total: spec.valor_pago_total || 0,
          quantidade_contas: spec.quantidade_contas || 0,
          incluir_no_calculo: true // default true
        })),
        contas_pagas: data.contas_pagas || []
      };
    } catch (error) {
      console.error('Erro ao buscar custos variáveis:', error);
      return {
        periodo_inicio: dataInicial,
        periodo_fim: dataFinal,
        valor_total_geral: 0,
        especificacoes: [],
        contas_pagas: []
      };
    }
  };  // Função para buscar margem de vendas
  const buscarMargemVendas = async (dataInicial: string, dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/contas/relatorios/faturamento/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }
      const data = await response.json();

      console.log('📊 Dados de margem de vendas recebidos:', data);

      const analiseVendas = data.totais_gerais?.analise_vendas || {};

      return {
        valor_vendas: analiseVendas.valor_vendas || 0,
        valor_custo_entrada: analiseVendas.valor_preco_entrada || 0,
        valor_preco_entrada: analiseVendas.valor_preco_entrada || 0,
        margem_bruta: analiseVendas.margem_bruta || 0,
        percentual_margem: analiseVendas.percentual_margem || 0,
        itens_analisados: analiseVendas.itens_analisados || 0,
        notas_detalhadas: data.notas_detalhadas || { vendas: [], compras: [], servicos: [] }
      };
    } catch (error) {
      console.error('Erro ao buscar margem de vendas:', error);
      return {
        valor_vendas: 0,
        valor_custo_entrada: 0,
        valor_preco_entrada: 0,
        margem_bruta: 0,
        percentual_margem: 0,
        itens_analisados: 0
      };
    }
  };

  const carregarDados = useCallback(async () => {
    if (!dateRange.from || !dateRange.to) return;

    setLoading(true);
    setError(null);

    try {
      const dataInicial = dateRange.from.toISOString().split('T')[0];
      const dataFinal = dateRange.to.toISOString().split('T')[0];

      console.log('📅 Carregando dados para período:', dataInicial, 'até', dataFinal);

      const [
        dadosEstoque,
        dadosContratos,
        dadosCustos,
        dadosCustosVariaveis,
        dadosFaturamento
      ] = await Promise.all([
        buscarMovimentacaoEstoque(dataInicial, dataFinal),
        buscarFaturamentoContratos(dataInicial, dataFinal),
        buscarCustosFixos(dataInicial, dataFinal),
        buscarCustosVariaveis(dataInicial, dataFinal),
        buscarMargemVendas(dataInicial, dataFinal)
      ]);

      console.log('📦 Dados estoque processados:', dadosEstoque);
      console.log('📋 Dados contratos processados:', dadosContratos);
      console.log('💳 Dados custos processados:', dadosCustos);
      console.log('📊 Dados custos variáveis processados:', dadosCustosVariaveis);
      console.log('💰 Dados faturamento processados:', dadosFaturamento);

      // Processar dados de estoque + variação por snapshot (alinhado ao Controle)
      const [valorIniSnap, valorFimSnap] = await Promise.all([
        buscarValorTotalEstoque(dataInicial),
        buscarValorTotalEstoque(dataFinal)
      ]);
      const variacaoSnapshot = (valorFimSnap - valorIniSnap) || 0;

      const movEstoque: MovimentacaoEstoque = {
        valor_entrada: dadosEstoque.valor_entrada || 0,
        valor_saida: dadosEstoque.valor_saida || 0,
        valor_saida_preco_entrada: dadosEstoque.valor_saida_preco_entrada || 0,
        saldo_periodo: dadosEstoque.saldo_periodo || 0,
        lucro_operacional: dadosEstoque.lucro_operacional || 0,
        margem_percentual: dadosEstoque.margem_percentual || 0,
        variacao_snapshot: variacaoSnapshot
      };

      // Processar dados de contratos
      const fatContratos: FaturamentoContratos = {
        faturamento_total_proporcional: dadosContratos.faturamento_total_proporcional || 0,
        custo_total_suprimentos: dadosContratos.custo_total_suprimentos || 0,
        margem_bruta_total: dadosContratos.margem_bruta_total || 0,
        percentual_margem_total: dadosContratos.percentual_margem_total || 0,
        contratos: dadosContratos.contratos || []
      };

      // Processar dados de custos fixos
      const custFixos: CustosFixos = {
        valor_total: dadosCustos.valor_total || 0,
        periodo_inicio: dadosCustos.periodo_inicio || dataInicial,
        periodo_fim: dadosCustos.periodo_fim || dataFinal,
        especificacoes: dadosCustos.especificacoes || [],
        contas_pagas: dadosCustos.contas_pagas || []
      };

      // Processar dados de custos variáveis
      const custVariaveis: CustosVariaveis = {
        periodo_inicio: dadosCustosVariaveis.periodo_inicio || dataInicial,
        periodo_fim: dadosCustosVariaveis.periodo_fim || dataFinal,
        valor_total_geral: dadosCustosVariaveis.valor_total_geral || 0,
        especificacoes: dadosCustosVariaveis.especificacoes || [],
        contas_pagas: dadosCustosVariaveis.contas_pagas || []
      };

      // Processar dados de margem de vendas
      const margVendas: MargemVendas = {
        valor_vendas: dadosFaturamento.valor_vendas || 0,
        valor_custo_entrada: dadosFaturamento.valor_custo_entrada || 0,
        valor_preco_entrada: dadosFaturamento.valor_preco_entrada || 0,
        margem_bruta: dadosFaturamento.margem_bruta || 0,
        percentual_margem: dadosFaturamento.percentual_margem || 0,
        itens_analisados: dadosFaturamento.itens_analisados || 0,
        notas_detalhadas: dadosFaturamento.notas_detalhadas
      };

      // Log dos dados recebidos dos endpoints
      console.log('📊 Dados carregados dos endpoints:');
      console.log('- Movimentação Estoque:', movEstoque);
      console.log('- Faturamento Contratos:', fatContratos);
      console.log('- Custos Fixos:', custFixos);
      console.log('- Custos Variáveis:', custVariaveis);
      console.log('- Margem Vendas:', margVendas);

      // Calcular resultado final conforme regra: (Linha 1) - (Linha 2)
      // Calcular resultado final conforme regra solicitada: 
      // Margem Contratos + Margem Venda - Custos Fixos - Custos Variáveis

      const movEstoqueValor = (typeof movEstoque.variacao_snapshot === 'number')
        ? (movEstoque.variacao_snapshot || 0)
        : (movEstoque.saldo_periodo || 0);
      const faturamentoContratosValor = fatContratos.faturamento_total_proporcional || 0;

      // Valores para cálculo
      const margemContratosValor = fatContratos.margem_bruta_total || 0;
      const margemVendasValor = margVendas.margem_bruta || 0;

      const totalPrimeiraLinha = margemContratosValor + margemVendasValor;

      const custosFixosValor = custFixos.especificacoes
        .filter(spec => spec.incluir_no_calculo)
        .reduce((total, spec) => total + (spec.valor_pago_total || 0), 0);
      const custosVariaveisValor = custVariaveis.especificacoes
        .filter(spec => spec.incluir_no_calculo)
        .reduce((total, spec) => total + (spec.valor_pago_total || 0), 0);
      const totalSegundaLinha = custosFixosValor + custosVariaveisValor;

      const resultadoLiquido = totalPrimeiraLinha - totalSegundaLinha;
      const margemLiquidaPercentual = totalPrimeiraLinha > 0 ? (resultadoLiquido / totalPrimeiraLinha) * 100 : 0;

      const resultado: ResultadoFinal = {
        lucro_operacional_estoque: movEstoqueValor,
        faturamento_contratos: faturamentoContratosValor,
        custos_fixos: custosFixosValor,
        custos_variaveis: custosVariaveisValor,
        resultado_liquido: resultadoLiquido,
        margem_liquida_percentual: margemLiquidaPercentual
      };

      // Atualizar estados
      setMovimentacaoEstoque(movEstoque);
      setFaturamentoContratos(fatContratos);
      setCustosFixos(custFixos);
      setCustosVariaveis(custVariaveis);
      setMargemVendas(margVendas);
      setResultadoFinal(resultado);

      console.log('✅ Dados carregados com sucesso');

    } catch (err) {
      console.error('❌ Erro ao carregar dados:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido ao carregar dados');
    } finally {
      setLoading(false);
    }
  }, [dateRange, buscarFaturamentoContratos]);

  // Função para abrir modal de detalhes
  const handleOpenDetalhes = (categoria: string, tipo: 'FIXO' | 'VARIAVEL' | 'CONTRATOS' | 'VENDAS' | 'SUPRIMENTOS_CONTRATOS' | 'CUSTO_VENDA') => {
    setCategoriaSelecionada({ nome: categoria, tipo });

    let itens: any[] = [];
    if (tipo === 'FIXO' && custosFixos) {
      itens = custosFixos.contas_pagas.filter(c => c.fornecedor_tipo === categoria);
      itens.sort((a, b) => new Date(b.data_pagamento).getTime() - new Date(a.data_pagamento).getTime());
    } else if (tipo === 'VARIAVEL' && custosVariaveis) {
      itens = custosVariaveis.contas_pagas.filter(c => c.fornecedor_especificacao === categoria);
      itens.sort((a, b) => new Date(b.data_pagamento).getTime() - new Date(a.data_pagamento).getTime());
    } else if (tipo === 'CONTRATOS' && faturamentoContratos && faturamentoContratos.contratos) {
      itens = faturamentoContratos.contratos;
      // Contratos já vêm agrupados, mas podemos ordenar por valor faturado
      itens.sort((a, b) => b.valores_contratuais.faturamento_proporcional - a.valores_contratuais.faturamento_proporcional);
    } else if (tipo === 'VENDAS' && margemVendas && margemVendas.notas_detalhadas) {
      itens = margemVendas.notas_detalhadas.vendas;
      itens.sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());
    } else if (tipo === 'SUPRIMENTOS_CONTRATOS' && faturamentoContratos && faturamentoContratos.contratos) {
      itens = faturamentoContratos.contratos.flatMap(c =>
        (c.suprimentos.notas || []).map((n: any) => ({
          ...n,
          origem_contrato: c.contrato_numero,
          origem_cliente: c.cliente.nome
        }))
      );
      itens.sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());
    } else if (tipo === 'CUSTO_VENDA' && margemVendas && margemVendas.notas_detalhadas) {
      itens = margemVendas.notas_detalhadas.vendas.flatMap(nf =>
        (nf.itens || []).map((item: any) => ({
          ...item,
          data: nf.data,
          numero_nota: nf.numero_nota,
          cliente: nf.cliente
        }))
      );
      itens.sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());
    }

    setItensModal(itens);
    setModalOpen(true);
  };

  // Carregar dados iniciais
  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

  // Recalcula resultados quando especificações são alteradas
  useEffect(() => {
    calcularResultados();
  }, [calcularResultados]);

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Cabeçalho */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Calculator style={{ width: '28px', height: '28px', color: '#3b82f6' }} />
          📊 Resultados Empresariais
        </h2>
        <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '24px' }}>
          Análise financeira completa incluindo movimentação de estoque, faturamento de contratos, custos fixos e variáveis, com margem de vendas integrada.
        </p>

        {/* Controles */}
        <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '4px' }}>
              📅 Período de Análise
            </label>
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
              fontWeight: '500'
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
                <Calculator style={{ width: '16px', height: '16px' }} />
                Atualizar Dados
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle style={{ width: '20px', height: '20px', color: '#dc2626' }} />
            <span style={{ color: '#dc2626', fontWeight: '500' }}>{error}</span>
          </div>
        </div>
      )}

      {/* Linha 1: Mov. Estoque, Faturamento Contratos, NFs de Venda */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        {/* Movimentação de Estoque */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '20px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', margin: 0 }}>
              📦 Movimentação Estoque
            </h3>
            <Package style={{ width: '20px', height: '20px', color: '#8b5cf6' }} />
          </div>
          {movimentacaoEstoque ? (
            <>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827', marginBottom: '4px' }}>
                {formatCurrency(
                  (typeof movimentacaoEstoque.variacao_snapshot === 'number')
                    ? movimentacaoEstoque.variacao_snapshot
                    : movimentacaoEstoque.saldo_periodo
                )}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <TrendingUp style={{ width: '12px', height: '12px' }} />
                {formatPercent(movimentacaoEstoque.margem_percentual)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '8px' }}>
                Entrada: {formatCurrency(movimentacaoEstoque.valor_entrada)}<br />
                Saída: {formatCurrency(movimentacaoEstoque.valor_saida)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
                Saldo do Período (movtos): {formatCurrency(movimentacaoEstoque.saldo_periodo)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
                Lucro Operacional: {formatCurrency(movimentacaoEstoque.lucro_operacional)}
              </div>
            </>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Carregando...</div>
          )}
        </div>

        {/* Faturamento Contratos */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '20px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', margin: 0 }}>
              📋 Faturamento Contratos
            </h3>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleOpenDetalhes('Contratos de Locação', 'CONTRATOS');
                }}
                style={{
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  padding: '4px',
                  color: '#6b7280',
                  display: 'flex',
                  alignItems: 'center',
                  marginRight: '8px'
                }}
                title="Ver detalhes dos contratos"
              >
                <Info size={16} />
              </button>
              <FileText style={{ width: '20px', height: '20px', color: '#06b6d4' }} />
            </div>
          </div>
          {faturamentoContratos ? (
            <>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827', marginBottom: '4px' }}>
                {formatCurrency(faturamentoContratos.faturamento_total_proporcional)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <TrendingUp style={{ width: '12px', height: '12px' }} />
                {formatPercent(faturamentoContratos.percentual_margem_total)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '8px' }}>
                Margem: {formatCurrency(faturamentoContratos.margem_bruta_total)}<br />
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  Custo suprimentos: {formatCurrency(faturamentoContratos.custo_total_suprimentos)}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenDetalhes('Custo Suprimentos', 'SUPRIMENTOS_CONTRATOS');
                    }}
                    style={{
                      border: 'none',
                      background: 'transparent',
                      cursor: 'pointer',
                      padding: '2px',
                      color: '#6b7280',
                      marginLeft: '4px',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                    title="Ver detalhes dos suprimentos"
                  >
                    <Info size={14} />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Carregando...</div>
          )}
        </div>

        {/* Notas Fiscais de Venda */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '20px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', margin: 0 }}>
              🧾 Notas Fiscais de Venda
            </h3>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleOpenDetalhes('Notas de Venda', 'VENDAS');
                }}
                style={{
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  padding: '4px',
                  color: '#6b7280',
                  display: 'flex',
                  alignItems: 'center',
                  marginRight: '8px'
                }}
                title="Ver detalhes das notas"
              >
                <Info size={16} />
              </button>
              <DollarSign style={{ width: '20px', height: '20px', color: '#0ea5e9' }} />
            </div>
          </div>
          {margemVendas ? (
            <>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827', marginBottom: '4px' }}>
                {formatCurrency(margemVendas.valor_vendas)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <TrendingUp style={{ width: '12px', height: '12px' }} />
                {formatPercent(margemVendas.percentual_margem)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '8px' }}>
                Margem bruta: {formatCurrency(margemVendas.margem_bruta)}<br />
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  Custo Estimado (Últ. Compra): {formatCurrency(margemVendas.valor_custo_entrada)}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenDetalhes('Custo Estimado de Vendas', 'CUSTO_VENDA');
                    }}
                    style={{
                      border: 'none',
                      background: 'transparent',
                      cursor: 'pointer',
                      padding: '2px',
                      color: '#6b7280',
                      marginLeft: '4px',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                    title="Ver detalhes do custo"
                  >
                    <Info size={14} />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Carregando...</div>
          )}
        </div>

      </div>

      {/* Linha 2: Custos Fixos e Variáveis */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        {/* Custos Fixos */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '20px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', margin: 0 }}>
              🏭 Custos Fixos
            </h3>
            <TrendingDown style={{ width: '20px', height: '20px', color: '#ef4444' }} />
          </div>
          {custosFixos ? (
            <>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#dc2626', marginBottom: '4px' }}>
                -{formatCurrency(custosFixos.especificacoes
                  .filter(spec => spec.incluir_no_calculo)
                  .reduce((total, spec) => total + spec.valor_pago_total, 0))}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '8px' }}>
                {custosFixos.especificacoes.length} especificações
              </div>
            </>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Carregando...</div>
          )}
        </div>

        {/* Custos Variáveis */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '20px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', margin: 0 }}>
              ⚙️ Custos Variáveis
            </h3>
            <TrendingDown style={{ width: '20px', height: '20px', color: '#f59e0b' }} />
          </div>
          {custosVariaveis ? (
            <>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#d97706', marginBottom: '4px' }}>
                -{formatCurrency(custosVariaveis.especificacoes
                  .filter(spec => spec.incluir_no_calculo)
                  .reduce((total, spec) => total + spec.valor_pago_total, 0))}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '8px' }}>
                {custosVariaveis.especificacoes.filter(spec => spec.incluir_no_calculo).length} especificações incluídas
              </div>
            </>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Carregando...</div>
          )}
        </div>

      </div>

      {/* Resultado Líquido */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        <div style={{
          backgroundColor: resultadoFinal && resultadoFinal.resultado_liquido >= 0 ? '#f0fdf4' : '#fef2f2',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '20px',
          border: `1px solid ${resultadoFinal && resultadoFinal.resultado_liquido >= 0 ? '#bbf7d0' : '#fecaca'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', margin: 0 }}>
              🎯 Resultado Líquido
            </h3>
            {resultadoFinal && resultadoFinal.resultado_liquido >= 0 ?
              <TrendingUp style={{ width: '20px', height: '20px', color: '#059669' }} /> :
              <TrendingDown style={{ width: '20px', height: '20px', color: '#dc2626' }} />
            }
          </div>
          {resultadoFinal ? (
            <>
              <div style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: resultadoFinal.resultado_liquido >= 0 ? '#059669' : '#dc2626',
                marginBottom: '4px'
              }}>
                {formatCurrency(resultadoFinal.resultado_liquido)}
              </div>
              <div style={{
                fontSize: '0.75rem',
                color: resultadoFinal.resultado_liquido >= 0 ? '#059669' : '#dc2626',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                Margem: {formatPercent(resultadoFinal.margem_liquida_percentual)}
              </div>
            </>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Carregando...</div>
          )}
        </div>
      </div>

      {/* Seções de Configuração dos Custos */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginBottom: '24px' }}>

        {/* Configuração Custos Fixos */}
        {custosFixos && custosFixos.especificacoes.length > 0 && (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '20px',
            border: '1px solid #e5e7eb'
          }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              ⚙️ Configurar Custos Fixos
              <span style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: '400' }}>
                (Selecione os tipos a incluir)
              </span>
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {custosFixos.especificacoes.map((spec, index) => (
                <label key={index} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px',
                  borderRadius: '4px',
                  backgroundColor: spec.incluir_no_calculo ? '#f0fdf4' : '#f9fafb',
                  border: `1px solid ${spec.incluir_no_calculo ? '#bbf7d0' : '#e5e7eb'}`,
                  cursor: 'pointer'
                }}>
                  <input
                    type="checkbox"
                    checked={spec.incluir_no_calculo}
                    onChange={() => toggleCustoFixo(spec.especificacao)}
                    style={{ marginRight: '4px' }}
                  />
                  <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                        {spec.especificacao}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                        {formatCurrency(spec.valor_pago_total)} • {spec.quantidade_contas} contas
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // Evitar toggle do checkbox
                        handleOpenDetalhes(spec.especificacao, 'FIXO');
                      }}
                      style={{
                        border: 'none',
                        background: 'transparent',
                        cursor: 'pointer',
                        padding: '4px',
                        color: '#6b7280',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                      title="Ver detalhes"
                    >
                      <Info size={16} />
                    </button>
                  </div>
                </label>
              ))}
            </div>

            <div style={{
              marginTop: '12px',
              padding: '8px',
              backgroundColor: '#f3f4f6',
              borderRadius: '4px',
              fontSize: '0.875rem',
              color: '#374151'
            }}>
              <strong>Total Selecionado:</strong> {formatCurrency(
                custosFixos.especificacoes
                  .filter(spec => spec.incluir_no_calculo)
                  .reduce((total, spec) => total + spec.valor_pago_total, 0)
              )}
            </div>
          </div>
        )}

        {/* Configuração Custos Variáveis */}
        {custosVariaveis && custosVariaveis.especificacoes.length > 0 && (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '20px',
            border: '1px solid #e5e7eb'
          }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              📊 Configurar Custos Variáveis
              <span style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: '400' }}>
                (Selecione as especificações a incluir)
              </span>
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {custosVariaveis.especificacoes.map((spec, index) => (
                <label key={index} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px',
                  borderRadius: '4px',
                  backgroundColor: spec.incluir_no_calculo ? '#f0fdf4' : '#f9fafb',
                  border: `1px solid ${spec.incluir_no_calculo ? '#bbf7d0' : '#e5e7eb'}`,
                  cursor: 'pointer'
                }}>
                  <input
                    type="checkbox"
                    checked={spec.incluir_no_calculo}
                    onChange={() => toggleCustoVariavel(spec.especificacao)}
                    style={{ marginRight: '4px' }}
                  />
                  <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                        {spec.especificacao}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                        {formatCurrency(spec.valor_pago_total)} • {spec.quantidade_contas} contas
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // Evitar toggle do checkbox
                        handleOpenDetalhes(spec.especificacao, 'VARIAVEL');
                      }}
                      style={{
                        border: 'none',
                        background: 'transparent',
                        cursor: 'pointer',
                        padding: '4px',
                        color: '#6b7280',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                      title="Ver detalhes"
                    >
                      <Info size={16} />
                    </button>
                  </div>
                </label>
              ))}
            </div>

            <div style={{
              marginTop: '12px',
              padding: '8px',
              backgroundColor: '#f3f4f6',
              borderRadius: '4px',
              fontSize: '0.875rem',
              color: '#374151'
            }}>
              <strong>Total Selecionado:</strong> {formatCurrency(
                custosVariaveis.especificacoes
                  .filter(spec => spec.incluir_no_calculo)
                  .reduce((total, spec) => total + spec.valor_pago_total, 0)
              )}
            </div>
          </div>
        )}

      </div>

      {/* Debug removido conforme solicitado */}



      {/* Modal de Detalhes */}
      {
        modalOpen && categoriaSelecionada && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
            padding: '20px'
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              width: '100%',
              maxWidth: '900px',
              maxHeight: '90vh',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            }}>
              {/* Header Modal */}
              <div style={{
                padding: '16px 24px',
                borderBottom: '1px solid #e5e7eb',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', margin: 0 }}>
                    Detalhes: {categoriaSelecionada.nome}
                  </h3>
                  <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    {categoriaSelecionada.tipo === 'FIXO' ? 'Custos Fixos' :
                      categoriaSelecionada.tipo === 'VARIAVEL' ? 'Custos Variáveis' :
                        categoriaSelecionada.tipo === 'CONTRATOS' ? 'Faturamento de Contratos' :
                          categoriaSelecionada.tipo === 'SUPRIMENTOS_CONTRATOS' ? 'Suprimentos por Contrato' :
                            categoriaSelecionada.tipo === 'CUSTO_VENDA' ? 'Custo Estimado por Nota' :
                              'Notas Fiscais de Venda'}
                  </span>
                </div>
                <button
                  onClick={() => setModalOpen(false)}
                  style={{
                    border: 'none',
                    background: 'none',
                    cursor: 'pointer',
                    color: '#6b7280',
                    padding: '4px'
                  }}
                >
                  <X size={24} />
                </button>
              </div>

              {/* Content Table */}
              <div style={{ overflowY: 'auto', padding: '24px' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                  <thead style={{ backgroundColor: '#f9fafb', color: '#374151' }}>
                    <tr>
                      {categoriaSelecionada.tipo === 'CONTRATOS' ? (
                        <>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Contrato</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Cliente</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Vigência Efetiva</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Valor Mensal</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Faturamento Proporcional</th>
                        </>
                      ) : categoriaSelecionada.tipo === 'VENDAS' ? (
                        <>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Data</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Cliente</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Nota Fiscal</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Operação</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Valor Total</th>
                        </>
                      ) : categoriaSelecionada.tipo === 'SUPRIMENTOS_CONTRATOS' ? (
                        <>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Data</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Contrato / Cliente</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Nota / Operação</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Valor Total</th>
                        </>
                      ) : categoriaSelecionada.tipo === 'CUSTO_VENDA' ? (
                        <>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Data / Nota</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Cliente</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Produto</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Quantidade</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Custo Unit.</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Custo Total</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Preço Unit.</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Preço Total</th>
                        </>
                      ) : (
                        <>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Data</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Fornecedor</th>
                          <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Descrição</th>
                          <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Valor</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {itensModal.length > 0 ? (
                      itensModal.map((item, idx) => (
                        <tr key={item.id || idx} style={{ borderBottom: '1px solid #e5e7eb' }}>
                          {categoriaSelecionada.tipo === 'CONTRATOS' ? (
                            <>
                              <td style={{ padding: '12px', fontWeight: '500' }}>{item.contrato_numero}</td>
                              <td style={{ padding: '12px' }}>{item.cliente?.nome || 'N/A'}</td>
                              <td style={{ padding: '12px', fontSize: '0.8rem', color: '#6b7280' }}>
                                {new Date(item.vigencia?.periodo_efetivo?.inicio).toLocaleDateString()} a {new Date(item.vigencia?.periodo_efetivo?.fim).toLocaleDateString()} ({item.vigencia?.periodo_efetivo?.dias_vigentes} dias)
                              </td>
                              <td style={{ padding: '12px', textAlign: 'right', color: '#6b7280' }}>
                                {formatCurrency(item.valores_contratuais?.valor_mensal || 0)}
                              </td>
                              <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#10b981' }}>
                                {formatCurrency(item.valores_contratuais?.faturamento_proporcional || 0)}
                              </td>
                            </>
                          ) : categoriaSelecionada.tipo === 'VENDAS' ? (
                            <>
                              <td style={{ padding: '12px' }}>
                                {new Date(item.data).toLocaleDateString('pt-BR')}
                              </td>
                              <td style={{ padding: '12px' }}>{item.cliente}</td>
                              <td style={{ padding: '12px', fontWeight: '500' }}>{item.numero_nota || 'N/A'}</td>
                              <td style={{ padding: '12px', fontSize: '0.8rem', color: '#6b7280' }}>{item.operacao}</td>
                              <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#3b82f6' }}>
                                {formatCurrency(item.valor_total)}
                              </td>
                            </>
                          ) : categoriaSelecionada.tipo === 'SUPRIMENTOS_CONTRATOS' ? (
                            <>
                              <td style={{ padding: '12px' }}>
                                {item.data ? new Date(item.data).toLocaleDateString('pt-BR') : '-'}
                              </td>
                              <td style={{ padding: '12px' }}>
                                <div style={{ fontSize: '0.85rem', fontWeight: '500' }}>{item.origem_contrato}</div>
                                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{item.origem_cliente}</div>
                              </td>
                              <td style={{ padding: '12px' }}>
                                <div style={{ fontSize: '0.85rem' }}>Nota: {item.numero_nota || 'N/A'}</div>
                                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{item.operacao}</div>
                              </td>
                              <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#ef4444' }}>
                                {formatCurrency(item.valor_total_nota || 0)}
                              </td>
                            </>
                          ) : categoriaSelecionada.tipo === 'CUSTO_VENDA' ? (
                            <>
                              <td style={{ padding: '12px', fontSize: '0.8rem' }}>
                                <div>{new Date(item.data).toLocaleDateString('pt-BR')}</div>
                                <div style={{ color: '#6b7280' }}>{item.numero_nota || 'N/A'}</div>
                              </td>
                              <td style={{ padding: '12px', fontSize: '0.85rem' }}>{item.cliente}</td>
                              <td style={{ padding: '12px', fontSize: '0.85rem' }}>{item.produto_nome}</td>
                              <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.85rem' }}>{item.quantidade}</td>
                              <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.8rem', color: '#6b7280' }}>
                                {formatCurrency(item.custo_unitario || 0)}
                              </td>
                              <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#f59e0b' }}>
                                {formatCurrency(item.custo_total || 0)}
                              </td>
                              <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.8rem', color: '#6b7280' }}>
                                {formatCurrency(item.valor_unitario_venda || 0)}
                              </td>
                              <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#10b981' }}>
                                {formatCurrency(item.valor_total_venda || 0)}
                              </td>
                            </>
                          ) : (
                            <>
                              <td style={{ padding: '12px' }}>
                                {new Date(item.data_pagamento).toLocaleDateString('pt-BR')}
                              </td>
                              <td style={{ padding: '12px' }}>{item.fornecedor_nome}</td>
                              <td style={{ padding: '12px', color: '#6b7280' }}>{item.historico || '-'}</td>
                              <td style={{ padding: '12px', textAlign: 'right', fontWeight: '500' }}>
                                {formatCurrency(item.valor_pago)}
                              </td>
                            </>
                          )}
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4} style={{ padding: '24px', textAlign: 'center', color: '#6b7280' }}>
                          Nenhum registro encontrado para esta categoria.
                        </td>
                      </tr>
                    )}
                  </tbody>
                  <tfoot style={{ backgroundColor: '#f9fafb', fontWeight: '600' }}>
                    <tr>
                      <td colSpan={categoriaSelecionada.tipo === 'CONTRATOS' ? 4 : categoriaSelecionada.tipo === 'VENDAS' ? 4 : categoriaSelecionada.tipo === 'SUPRIMENTOS_CONTRATOS' ? 3 : categoriaSelecionada.tipo === 'CUSTO_VENDA' ? 4 : 3} style={{ padding: '12px', textAlign: 'right' }}>Total:</td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        {formatCurrency(itensModal.reduce((sum, item) => {
                          if (categoriaSelecionada.tipo === 'CONTRATOS') return sum + (item.valores_contratuais?.faturamento_proporcional || 0);
                          if (categoriaSelecionada.tipo === 'VENDAS') return sum + (item.valor_total || 0);
                          if (categoriaSelecionada.tipo === 'SUPRIMENTOS_CONTRATOS') return sum + (item.valor_total_nota || 0);
                          if (categoriaSelecionada.tipo === 'CUSTO_VENDA') return sum + (item.custo_total || 0);
                          return sum + (item.valor_pago || 0);
                        }, 0))}
                      </td>
                      {categoriaSelecionada.tipo === 'CUSTO_VENDA' && (
                        <>
                          <td style={{ padding: '12px' }}></td>
                          <td style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>
                            {formatCurrency(itensModal.reduce((sum, item) => sum + (item.valor_total_venda || 0), 0))}
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

export default ResultadosEmpresariais;
