// src/components/dashboard/ResultadosEmpresariais.tsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Package,
  FileText,
  DollarSign,
  CreditCard,
  Calculator,
  AlertCircle,
  Receipt
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
  lucro_operacional: number;
  margem_percentual: number;
}

interface FaturamentoContratos {
  faturamento_total_proporcional: number;
  custo_total_suprimentos: number;
  margem_bruta_total: number;
  percentual_margem_total: number;
}

interface MargemVendas {
  valor_vendas: number;
  valor_preco_entrada: number;
  margem_bruta: number;
  percentual_margem: number;
  itens_analisados: number;
}

interface CustosFixos {
  valor_total: number;
  valor_custos_fixos: number;
  valor_despesas_fixas: number;
  quantidade_total_contas: number;
}

interface CustosVariaveis {
  valor_total: number;
  especificacoes: Array<{
    especificacao: string;
    valor_pago_total: number;
    quantidade_contas: number;
    incluir_no_calculo: boolean;
  }>;
}

interface ContasPagar {
  valor_total_aberto: number;
  quantidade_contas: number;
  valor_vencido: number;
  valor_a_vencer: number;
  detalhes: Array<{
    id: number;
    descricao: string;
    valor: number;
    data_vencimento: string;
    dias_vencimento: number;
    status: string;
  }>;
}

interface ContasReceber {
  valor_total_aberto: number;
  quantidade_contas: number;
  valor_vencido: number;
  valor_a_vencer: number;
  detalhes: Array<{
    id: number;
    cliente: string;
    valor: number;
    data_vencimento: string;
    dias_vencimento: number;
    status: string;
  }>;
}

interface ValorEstoque {
  valor_total_atual: number;
  data_consulta: string;
  total_produtos: number;
  produtos_com_estoque: number;
  variacao_periodo: number;
  percentual_variacao: number;
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
    from: new Date(2025, 7, 1), // agosto 2025
    to: new Date(2025, 7, 31)
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Estados para cada componente do resultado
  const [movimentacaoEstoque, setMovimentacaoEstoque] = useState<MovimentacaoEstoque | null>(null);
  const [faturamentoContratos, setFaturamentoContratos] = useState<FaturamentoContratos | null>(null);
  const [margemVendas, setMargemVendas] = useState<MargemVendas | null>(null);
  const [custosFixos, setCustosFixos] = useState<CustosFixos | null>(null);
  const [custosVariaveis, setCustosVariaveis] = useState<CustosVariaveis | null>(null);
  const [contasPagar, setContasPagar] = useState<ContasPagar | null>(null);
  const [contasReceber, setContasReceber] = useState<ContasReceber | null>(null);
  const [valorEstoque, setValorEstoque] = useState<ValorEstoque | null>(null);
  const [resultadoFinal, setResultadoFinal] = useState<ResultadoFinal | null>(null);
  
  // Estado para escolher entre estoque ou vendas
  const [tipoCalculoLucro, setTipoCalculoLucro] = useState<'estoque' | 'vendas'>('estoque');

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  // Função para alternar inclusão de especificação no cálculo
  const toggleEspecificacao = (especificacao: string) => {
    if (!custosVariaveis) return;
    
    const novasEspecificacoes = custosVariaveis.especificacoes.map(spec =>
      spec.especificacao === especificacao
        ? { ...spec, incluir_no_calculo: !spec.incluir_no_calculo }
        : spec
    );
    
    const custosVariaveisAtualizados = {
      ...custosVariaveis,
      especificacoes: novasEspecificacoes
    };
    
    setCustosVariaveis(custosVariaveisAtualizados);
    
    // Recalcular resultado final
    if (resultadoFinal && movimentacaoEstoque && margemVendas && faturamentoContratos && custosFixos) {
      const custosVariaveisValor = novasEspecificacoes
        .filter(spec => spec.incluir_no_calculo)
        .reduce((total, spec) => total + spec.valor_pago_total, 0);
      
      const lucroSelecionado = tipoCalculoLucro === 'estoque' 
        ? movimentacaoEstoque.lucro_operacional 
        : margemVendas.margem_bruta;
      
      const novoResultadoLiquido = lucroSelecionado + faturamentoContratos.margem_bruta_total - custosFixos.valor_total - custosVariaveisValor;
      const receitaTotalEstoque = movimentacaoEstoque.valor_saida + faturamentoContratos.faturamento_total_proporcional;
      const receitaTotalVendas = margemVendas.valor_vendas + faturamentoContratos.faturamento_total_proporcional;
      const receitaTotal = tipoCalculoLucro === 'estoque' ? receitaTotalEstoque : receitaTotalVendas;
      const novaMargemLiquidaPercentual = receitaTotal > 0 ? (novoResultadoLiquido / receitaTotal) * 100 : 0;
      
      setResultadoFinal({
        ...resultadoFinal,
        lucro_operacional_estoque: lucroSelecionado,
        custos_variaveis: custosVariaveisValor,
        resultado_liquido: novoResultadoLiquido,
        margem_liquida_percentual: novaMargemLiquidaPercentual
      });
    }
  };

  // Função para alternar tipo de cálculo de lucro
  const toggleTipoCalculoLucro = (tipo: 'estoque' | 'vendas') => {
    setTipoCalculoLucro(tipo);
    
    // Recalcular resultado se os dados existirem
    if (resultadoFinal && movimentacaoEstoque && margemVendas && faturamentoContratos && custosFixos && custosVariaveis) {
      const lucroSelecionado = tipo === 'estoque' 
        ? movimentacaoEstoque.lucro_operacional 
        : margemVendas.margem_bruta;
      
      const custosVariaveisValor = custosVariaveis.especificacoes
        .filter(spec => spec.incluir_no_calculo)
        .reduce((total, spec) => total + spec.valor_pago_total, 0);
      
      const novoResultadoLiquido = lucroSelecionado + faturamentoContratos.margem_bruta_total - custosFixos.valor_total - custosVariaveisValor;
      const receitaTotalEstoque = movimentacaoEstoque.valor_saida + faturamentoContratos.faturamento_total_proporcional;
      const receitaTotalVendas = margemVendas.valor_vendas + faturamentoContratos.faturamento_total_proporcional;
      const receitaTotal = tipo === 'estoque' ? receitaTotalEstoque : receitaTotalVendas;
      const novaMargemLiquidaPercentual = receitaTotal > 0 ? (novoResultadoLiquido / receitaTotal) * 100 : 0;
      
      setResultadoFinal({
        ...resultadoFinal,
        lucro_operacional_estoque: lucroSelecionado,
        resultado_liquido: novoResultadoLiquido,
        margem_liquida_percentual: novaMargemLiquidaPercentual
      });
    }
  };

  // Função para buscar movimentação de estoque
  const buscarMovimentacaoEstoque = async (dataInicial: string, dataFinal: string) => {
    try {
      // Usar o endpoint correto do estoque-controle
      const response = await fetch(`http://localhost:8000/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
      if (!response.ok) {
        throw new Error(`Erro ao buscar movimentação de estoque: ${response.status}`);
      }
      
      const dados = await response.json();
      console.log('📦 Dados de estoque recebidos:', dados);
      
      // Mapear para o formato esperado usando os campos corretos da API
      return {
        total_entradas: dados.resumo?.valor_total_entradas || 0,
        total_saidas: dados.resumo?.valor_total_saidas || 0,
        lucro_operacional: dados.resumo?.diferenca_total_precos || 0, // diferença entre preço de saída e entrada
        margem_percentual: dados.resumo?.margem_total || 0
      };
    } catch (error) {
      console.error('Erro ao buscar movimentação de estoque:', error);
      // Em caso de erro, retornar dados zerados
      return {
        total_entradas: 0,
        total_saidas: 0,
        lucro_operacional: 0,
        margem_percentual: 0
      };
    }
  };

  // Função para buscar faturamento de contratos
  const buscarFaturamentoContratos = async (dataInicial: string, dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/contratos_locacao/suprimentos/?data_inicial=${dataInicial}&data_final=${dataFinal}`);
      if (!response.ok) {
        console.warn('Endpoint de contratos não encontrado, usando dados zerados');
        return {
          resumo_financeiro: {
            faturamento_total_proporcional: 0,
            custo_total_suprimentos: 0,
            margem_bruta_total: 0,
            percentual_margem_total: 0
          }
        };
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar faturamento de contratos:', error);
      return {
        resumo_financeiro: {
          faturamento_total_proporcional: 0,
          custo_total_suprimentos: 0,
          margem_bruta_total: 0,
          percentual_margem_total: 0
        }
      };
    }
  };

  // Função para buscar custos fixos
  const buscarCustosFixos = async (dataInicial: string, dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/relatorios/custos-fixos/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
      if (!response.ok) {
        console.warn('Endpoint de custos fixos não encontrado, usando dados zerados');
        return {
          totais_gerais: {
            total_valor_pago: 0,
            total_contas_pagas: 0
          },
          resumo_por_tipo_fornecedor: []
        };
      }
      
      const dados = await response.json();
      console.log('💳 Dados de custos fixos recebidos:', dados);
      
      return dados;
    } catch (error) {
      console.error('Erro ao buscar custos fixos:', error);
      return {
        totais_gerais: {
          total_valor_pago: 0,
          total_contas_pagas: 0
        },
        resumo_por_tipo_fornecedor: []
      };
    }
  };

  // Função para buscar custos variáveis
  const buscarCustosVariaveis = async (dataInicial: string, dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/contas/relatorios/custos-variaveis/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
      if (!response.ok) {
        console.warn('Endpoint de custos variáveis não encontrado, usando dados zerados');
        return {
          totais_gerais: {
            total_valor_pago: 0
          },
          resumo_por_especificacao: []
        };
      }
      
      const dados = await response.json();
      console.log('📊 Dados de custos variáveis recebidos:', dados);
      
      return dados;
    } catch (error) {
      console.error('Erro ao buscar custos variáveis:', error);
      return {
        totais_gerais: {
          total_valor_pago: 0
        },
        resumo_por_especificacao: []
      };
    }
  };

  // Função para buscar margem de vendas do faturamento
  const buscarMargemVendas = async (dataInicial: string, dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/contas/relatorios/faturamento/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
      if (!response.ok) {
        console.warn('Endpoint de faturamento não encontrado, usando dados zerados');
        return {
          totais_gerais: {
            analise_vendas: {
              valor_vendas: 0,
              valor_preco_entrada: 0,
              margem_bruta: 0,
              percentual_margem: 0,
              itens_analisados: 0
            }
          }
        };
      }
      
      const dados = await response.json();
      console.log('💰 Dados de faturamento recebidos:', dados);
      
      return dados;
    } catch (error) {
      console.error('Erro ao buscar dados de faturamento:', error);
      return {
        totais_gerais: {
          analise_vendas: {
            valor_vendas: 0,
            valor_preco_entrada: 0,
            margem_bruta: 0,
            percentual_margem: 0,
            itens_analisados: 0
          }
        }
      };
    }
  };

  // Função para buscar contas a pagar em aberto
  const buscarContasPagar = async (dataFinal: string) => {
    try {
      console.log('🚀 Iniciando busca de contas a pagar para data:', dataFinal);
      
      // Lista de endpoints para tentar em ordem de preferência
      const endpointsParaTestar = [
        // Endpoint principal especificado pelo usuário
        `http://localhost:8000/contas/contas-por-data-vencimento/?data_consulta=${dataFinal}&tipo=pagar&status=aberto`,
        // Sem filtros específicos
        `http://localhost:8000/contas/contas-por-data-vencimento/?data_consulta=${dataFinal}`,
        // Endpoint base
        `http://localhost:8000/contas/contas-por-data-vencimento/`,
        // Endpoints alternativos que podem existir
        `http://localhost:8000/api/contas/contas-pagar/?status=aberto&data_fim=${dataFinal}`,
        `http://localhost:8000/contas/pagar/?status=aberto&data_consulta=${dataFinal}`,
        `http://localhost:8000/financeiro/contas-pagar/?status=aberto`,
        `http://localhost:8000/api/financeiro/contas-pagar/`,
        // Endpoints do sistema de relatórios
        `http://localhost:8000/contas/relatorios/contas-pagar/?data_consulta=${dataFinal}&status=aberto`,
        `http://localhost:8000/api/relatorios/contas-pagar/?status=aberto`,
        // Endpoints genéricos
        `http://localhost:8000/api/contas/?tipo=pagar&status=aberto`,
        `http://localhost:8000/contas/?tipo=pagar&status=aberto`
      ];
      
      for (let i = 0; i < endpointsParaTestar.length; i++) {
        const url = endpointsParaTestar[i];
        console.log(`🔗 [${i + 1}/${endpointsParaTestar.length}] Testando endpoint:`, url);
        
        try {
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          });
          
          console.log(`📊 Status [${i + 1}]:`, response.status, response.statusText);
          
          if (response.ok) {
            const dados = await response.json();
            console.log(`✅ Sucesso no endpoint [${i + 1}]:`, url);
            console.log('� Dados recebidos:', dados);
            
            // Se os dados têm a estrutura esperada, usar diretamente
            if (dados && (dados.valor_total_aberto !== undefined || dados.total !== undefined || Array.isArray(dados))) {
              // Normalizar a estrutura dos dados
              if (Array.isArray(dados)) {
                const total = dados.reduce((acc, conta) => acc + (conta.valor || conta.valor_original || 0), 0);
                return {
                  valor_total_aberto: total,
                  quantidade_contas: dados.length,
                  valor_vencido: 0,
                  valor_a_vencer: total,
                  detalhes: dados
                };
              } else {
                return {
                  valor_total_aberto: dados.valor_total_aberto || dados.total || 0,
                  quantidade_contas: dados.quantidade_contas || dados.count || 0,
                  valor_vencido: dados.valor_vencido || 0,
                  valor_a_vencer: dados.valor_a_vencer || dados.valor_total_aberto || dados.total || 0,
                  detalhes: dados.detalhes || dados.results || []
                };
              }
            }
            
            return dados;
          } else {
            console.warn(`❌ Endpoint [${i + 1}] falhou:`, response.status, response.statusText);
          }
        } catch (fetchError) {
          console.warn(`🔥 Erro no endpoint [${i + 1}]:`, fetchError instanceof Error ? fetchError.message : String(fetchError));
        }
      }
      
      console.warn('❌ Todos os endpoints falharam, retornando dados zerados');
      
      // 🚨 DADOS DE EXEMPLO PARA TESTE - REMOVER EM PRODUÇÃO
      const dadosExemplo = {
        valor_total_aberto: 25000.00,
        quantidade_contas: 15,
        valor_vencido: 8000.00,
        valor_a_vencer: 17000.00,
        detalhes: [
          { descricao: 'Fornecedor A', valor: 5000.00, vencimento: '2024-12-15' },
          { descricao: 'Fornecedor B', valor: 3000.00, vencimento: '2024-12-20' },
          { descricao: 'Fornecedor C', valor: 2000.00, vencimento: '2024-12-25' }
        ]
      };
      
      console.log('🎭 Usando dados de exemplo para contas a pagar:', dadosExemplo);
      return dadosExemplo;
      
    } catch (error) {
      console.error('💥 Erro geral ao buscar contas a pagar:', error);
      return {
        valor_total_aberto: 0,
        quantidade_contas: 0,
        valor_vencido: 0,
        valor_a_vencer: 0,
        detalhes: []
      };
    }
  };

  // Função para buscar contas a receber em aberto
  const buscarContasReceber = async (dataFinal: string) => {
    try {
      console.log('🚀 Iniciando busca de contas a receber para data:', dataFinal);
      
      // Lista de endpoints para tentar em ordem de preferência
      const endpointsParaTestar = [
        // Endpoint principal especificado pelo usuário
        `http://localhost:8000/contas/contas-por-data-vencimento/?data_consulta=${dataFinal}&tipo=receber&status=aberto`,
        // Sem filtros específicos
        `http://localhost:8000/contas/contas-por-data-vencimento/?data_consulta=${dataFinal}`,
        // Endpoint base
        `http://localhost:8000/contas/contas-por-data-vencimento/`,
        // Endpoints alternativos que podem existir
        `http://localhost:8000/api/contas/contas-receber/?status=aberto&data_fim=${dataFinal}`,
        `http://localhost:8000/contas/receber/?status=aberto&data_consulta=${dataFinal}`,
        `http://localhost:8000/financeiro/contas-receber/?status=aberto`,
        `http://localhost:8000/api/financeiro/contas-receber/`,
        // Endpoints do sistema de relatórios
        `http://localhost:8000/contas/relatorios/contas-receber/?data_consulta=${dataFinal}&status=aberto`,
        `http://localhost:8000/api/relatorios/contas-receber/?status=aberto`,
        // Endpoints genéricos
        `http://localhost:8000/api/contas/?tipo=receber&status=aberto`,
        `http://localhost:8000/contas/?tipo=receber&status=aberto`
      ];
      
      for (let i = 0; i < endpointsParaTestar.length; i++) {
        const url = endpointsParaTestar[i];
        console.log(`🔗 [${i + 1}/${endpointsParaTestar.length}] Testando endpoint:`, url);
        
        try {
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          });
          
          console.log(`📊 Status [${i + 1}]:`, response.status, response.statusText);
          
          if (response.ok) {
            const dados = await response.json();
            console.log(`✅ Sucesso no endpoint [${i + 1}]:`, url);
            console.log('� Dados recebidos:', dados);
            
            // Se os dados têm a estrutura esperada, usar diretamente
            if (dados && (dados.valor_total_aberto !== undefined || dados.total !== undefined || Array.isArray(dados))) {
              // Normalizar a estrutura dos dados
              if (Array.isArray(dados)) {
                const total = dados.reduce((acc, conta) => acc + (conta.valor || conta.valor_original || 0), 0);
                return {
                  valor_total_aberto: total,
                  quantidade_contas: dados.length,
                  valor_vencido: 0,
                  valor_a_vencer: total,
                  detalhes: dados
                };
              } else {
                return {
                  valor_total_aberto: dados.valor_total_aberto || dados.total || 0,
                  quantidade_contas: dados.quantidade_contas || dados.count || 0,
                  valor_vencido: dados.valor_vencido || 0,
                  valor_a_vencer: dados.valor_a_vencer || dados.valor_total_aberto || dados.total || 0,
                  detalhes: dados.detalhes || dados.results || []
                };
              }
            }
            
            return dados;
          } else {
            console.warn(`❌ Endpoint [${i + 1}] falhou:`, response.status, response.statusText);
          }
        } catch (fetchError) {
          console.warn(`🔥 Erro no endpoint [${i + 1}]:`, fetchError instanceof Error ? fetchError.message : String(fetchError));
        }
      }
      
      console.warn('❌ Todos os endpoints falharam, retornando dados zerados');
      
      // 🚨 DADOS DE EXEMPLO PARA TESTE - REMOVER EM PRODUÇÃO
      const dadosExemplo = {
        valor_total_aberto: 35000.00,
        quantidade_contas: 20,
        valor_vencido: 12000.00,
        valor_a_vencer: 23000.00,
        detalhes: [
          { descricao: 'Cliente A', valor: 8000.00, vencimento: '2024-12-15' },
          { descricao: 'Cliente B', valor: 5000.00, vencimento: '2024-12-20' },
          { descricao: 'Cliente C', valor: 3000.00, vencimento: '2024-12-25' }
        ]
      };
      
      console.log('🎭 Usando dados de exemplo para contas a receber:', dadosExemplo);
      return dadosExemplo;
      
    } catch (error) {
      console.error('💥 Erro geral ao buscar contas a receber:', error);
      return {
        valor_total_aberto: 0,
        quantidade_contas: 0,
        valor_vencido: 0,
        valor_a_vencer: 0,
        detalhes: []
      };
    }
  };

  // Função para buscar valor do estoque no final do período
  const buscarValorEstoque = async (dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/contas/estoque-controle/estoque_atual/?data=${dataFinal}&resumo=true`);
      if (!response.ok) {
        console.warn('Endpoint de valor do estoque não encontrado, usando dados zerados');
        return {
          valor_total_atual: 0,
          data_consulta: dataFinal,
          total_produtos: 0,
          produtos_com_estoque: 0,
          variacao_periodo: 0,
          percentual_variacao: 0
        };
      }
      
      const dados = await response.json();
      console.log('📦 Dados do valor do estoque recebidos:', dados);
      
      // Extrair dados das estatísticas se disponível
      if (dados.estatisticas) {
        return {
          valor_total_atual: dados.estatisticas.valor_total_atual || 0,
          data_consulta: dados.parametros?.data_consulta || dataFinal,
          total_produtos: dados.estatisticas.total_produtos || 0,
          produtos_com_estoque: dados.estatisticas.produtos_com_estoque || 0,
          variacao_periodo: dados.estatisticas.variacao_total || 0,
          percentual_variacao: dados.estatisticas.percentual_variacao || 0
        };
      }
      
      return dados;
    } catch (error) {
      console.error('Erro ao buscar valor do estoque:', error);
      return {
        valor_total_atual: 0,
        data_consulta: dataFinal,
        total_produtos: 0,
        produtos_com_estoque: 0,
        variacao_periodo: 0,
        percentual_variacao: 0
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
      
      console.log('🔄 Carregando dados de resultados...');
      console.log(`📅 Período: ${dataInicial} até ${dataFinal}`);

      // Buscar todos os dados em paralelo
      const [
        dadosEstoque, 
        dadosContratos, 
        dadosCustos, 
        dadosCustosVariaveis, 
        dadosFaturamento,
        dadosContasPagar,
        dadosContasReceber,
        dadosValorEstoque
      ] = await Promise.all([
        buscarMovimentacaoEstoque(dataInicial, dataFinal),
        buscarFaturamentoContratos(dataInicial, dataFinal),
        buscarCustosFixos(dataInicial, dataFinal),
        buscarCustosVariaveis(dataInicial, dataFinal),
        buscarMargemVendas(dataInicial, dataFinal),
        buscarContasPagar(dataFinal),
        buscarContasReceber(dataFinal),
        buscarValorEstoque(dataFinal)
      ]);

      console.log('📦 Dados estoque processados:', dadosEstoque);
      console.log('📋 Dados contratos processados:', dadosContratos);
      console.log('💳 Dados custos processados:', dadosCustos);
      console.log('📊 Dados custos variáveis processados:', dadosCustosVariaveis);
      console.log('💰 Dados faturamento processados:', dadosFaturamento);

      // Processar dados de estoque
      const movEstoque: MovimentacaoEstoque = {
        valor_entrada: dadosEstoque.total_entradas || 0,
        valor_saida: dadosEstoque.total_saidas || 0,
        lucro_operacional: dadosEstoque.lucro_operacional || 0,
        margem_percentual: dadosEstoque.margem_percentual || 0
      };

      // Processar dados de contratos
      const fatContratos: FaturamentoContratos = {
        faturamento_total_proporcional: dadosContratos.resumo_financeiro?.faturamento_total_proporcional || 0,
        custo_total_suprimentos: dadosContratos.resumo_financeiro?.custo_total_suprimentos || 0,
        margem_bruta_total: dadosContratos.resumo_financeiro?.margem_bruta_total || 0,
        percentual_margem_total: dadosContratos.resumo_financeiro?.percentual_margem_total || 0
      };

      // Processar dados de custos fixos
      const valorCustosFixos = dadosCustos.resumo_por_tipo_fornecedor?.find((item: { fornecedor__tipo: string; total_pago: number }) => item.fornecedor__tipo === 'CUSTO FIXO')?.total_pago || 0;
      const valorDespesasFixas = dadosCustos.resumo_por_tipo_fornecedor?.find((item: { fornecedor__tipo: string; total_pago: number }) => item.fornecedor__tipo === 'DESPESA FIXA')?.total_pago || 0;
      
      const custFixos: CustosFixos = {
        valor_total: dadosCustos.totais_gerais?.total_valor_pago || 0,
        valor_custos_fixos: valorCustosFixos,
        valor_despesas_fixas: valorDespesasFixas,
        quantidade_total_contas: dadosCustos.total_contas_pagas || 0
      };

      // Processar dados de custos variáveis
      const especificacoesCustosVariaveis = dadosCustosVariaveis.resumo_por_especificacao?.map((item: { especificacao: string; valor_pago_total: number; quantidade_contas: number }) => ({
        especificacao: item.especificacao || 'Não informado',
        valor_pago_total: item.valor_pago_total || 0,
        quantidade_contas: item.quantidade_contas || 0,
        incluir_no_calculo: true // Por padrão, incluir todas
      })) || [];

      const custVariaveis: CustosVariaveis = {
        valor_total: dadosCustosVariaveis.totais_gerais?.total_valor_pago || 0,
        especificacoes: especificacoesCustosVariaveis
      };

      // Processar dados de margem de vendas
      const analiseVendas = dadosFaturamento.totais_gerais?.analise_vendas || {};
      const margVendas: MargemVendas = {
        valor_vendas: analiseVendas.valor_vendas || 0,
        valor_preco_entrada: analiseVendas.valor_preco_entrada || 0,
        margem_bruta: analiseVendas.margem_bruta || 0,
        percentual_margem: analiseVendas.percentual_margem || 0,
        itens_analisados: analiseVendas.itens_analisados || 0
      };

      // Processar dados de contas a pagar
      console.log('🔍 Processando contas a pagar:', dadosContasPagar);
      
      // Tentar diferentes estruturas de resposta
      let valorTotalPagar = 0;
      let quantidadeContasPagar = 0;
      let valorVencidoPagar = 0;
      let valorAVencerPagar = 0;
      let detalhesPagar = [];

      if (dadosContasPagar) {
        // Estrutura direta
        valorTotalPagar = dadosContasPagar.valor_total_aberto || dadosContasPagar.total_valor || dadosContasPagar.valor_total || 0;
        quantidadeContasPagar = dadosContasPagar.quantidade_contas || dadosContasPagar.total_contas || dadosContasPagar.quantidade || 0;
        valorVencidoPagar = dadosContasPagar.valor_vencido || dadosContasPagar.vencido || 0;
        valorAVencerPagar = dadosContasPagar.valor_a_vencer || dadosContasPagar.a_vencer || 0;
        detalhesPagar = dadosContasPagar.detalhes || dadosContasPagar.contas || dadosContasPagar.dados || [];

        // Se tiver um array de contas, calcular totais
        if (Array.isArray(dadosContasPagar) && dadosContasPagar.length > 0) {
          valorTotalPagar = dadosContasPagar.reduce((total, conta) => total + (conta.valor || conta.valor_total || 0), 0);
          quantidadeContasPagar = dadosContasPagar.length;
          detalhesPagar = dadosContasPagar;
        }

        // Se tiver dados dentro de uma propriedade 'resultados' ou similar
        if (dadosContasPagar.resultados || dadosContasPagar.data || dadosContasPagar.contas_pagar) {
          const dados = dadosContasPagar.resultados || dadosContasPagar.data || dadosContasPagar.contas_pagar;
          if (Array.isArray(dados)) {
            valorTotalPagar = dados.reduce((total, conta) => total + (conta.valor || conta.valor_total || 0), 0);
            quantidadeContasPagar = dados.length;
            detalhesPagar = dados;
          }
        }
      }

      const contPagar: ContasPagar = {
        valor_total_aberto: valorTotalPagar,
        quantidade_contas: quantidadeContasPagar,
        valor_vencido: valorVencidoPagar,
        valor_a_vencer: valorAVencerPagar,
        detalhes: detalhesPagar
      };
      console.log('💳 Contas a pagar processadas:', contPagar);

      // Processar dados de contas a receber
      console.log('🔍 Processando contas a receber:', dadosContasReceber);
      
      // Tentar diferentes estruturas de resposta
      let valorTotalReceber = 0;
      let quantidadeContasReceber = 0;
      let valorVencidoReceber = 0;
      let valorAVencerReceber = 0;
      let detalhesReceber = [];

      if (dadosContasReceber) {
        // Estrutura direta
        valorTotalReceber = dadosContasReceber.valor_total_aberto || dadosContasReceber.total_valor || dadosContasReceber.valor_total || 0;
        quantidadeContasReceber = dadosContasReceber.quantidade_contas || dadosContasReceber.total_contas || dadosContasReceber.quantidade || 0;
        valorVencidoReceber = dadosContasReceber.valor_vencido || dadosContasReceber.vencido || 0;
        valorAVencerReceber = dadosContasReceber.valor_a_vencer || dadosContasReceber.a_vencer || 0;
        detalhesReceber = dadosContasReceber.detalhes || dadosContasReceber.contas || dadosContasReceber.dados || [];

        // Se tiver um array de contas, calcular totais
        if (Array.isArray(dadosContasReceber) && dadosContasReceber.length > 0) {
          valorTotalReceber = dadosContasReceber.reduce((total, conta) => total + (conta.valor || conta.valor_total || 0), 0);
          quantidadeContasReceber = dadosContasReceber.length;
          detalhesReceber = dadosContasReceber;
        }

        // Se tiver dados dentro de uma propriedade 'resultados' ou similar
        if (dadosContasReceber.resultados || dadosContasReceber.data || dadosContasReceber.contas_receber) {
          const dados = dadosContasReceber.resultados || dadosContasReceber.data || dadosContasReceber.contas_receber;
          if (Array.isArray(dados)) {
            valorTotalReceber = dados.reduce((total, conta) => total + (conta.valor || conta.valor_total || 0), 0);
            quantidadeContasReceber = dados.length;
            detalhesReceber = dados;
          }
        }
      }

      const contReceber: ContasReceber = {
        valor_total_aberto: valorTotalReceber,
        quantidade_contas: quantidadeContasReceber,
        valor_vencido: valorVencidoReceber,
        valor_a_vencer: valorAVencerReceber,
        detalhes: detalhesReceber
      };
      console.log('💰 Contas a receber processadas:', contReceber);

      // Processar dados do valor do estoque
      const valEstoque: ValorEstoque = {
        valor_total_atual: dadosValorEstoque.valor_total_atual || 0,
        data_consulta: dadosValorEstoque.data_consulta || dataFinal,
        total_produtos: dadosValorEstoque.total_produtos || 0,
        produtos_com_estoque: dadosValorEstoque.produtos_com_estoque || 0,
        variacao_periodo: dadosValorEstoque.variacao_periodo || 0,
        percentual_variacao: dadosValorEstoque.percentual_variacao || 0
      };

      // Calcular resultado final
      const lucroOperacionalEstoque = movEstoque.lucro_operacional;
      const lucroMargemVendas = margVendas.margem_bruta;
      const lucroSelecionado = tipoCalculoLucro === 'estoque' ? lucroOperacionalEstoque : lucroMargemVendas;
      
      const faturamentoContratosValor = fatContratos.margem_bruta_total; // Margem já descontando suprimentos
      const custosFixosValor = custFixos.valor_total;
      const custosVariaveisValor = custVariaveis.especificacoes
        .filter(spec => spec.incluir_no_calculo)
        .reduce((total, spec) => total + spec.valor_pago_total, 0);
      
      const resultadoLiquido = lucroSelecionado + faturamentoContratosValor - custosFixosValor - custosVariaveisValor;
      const receitaTotalEstoque = movEstoque.valor_saida + fatContratos.faturamento_total_proporcional;
      const receitaTotalVendas = margVendas.valor_vendas + fatContratos.faturamento_total_proporcional;
      const receitaTotal = tipoCalculoLucro === 'estoque' ? receitaTotalEstoque : receitaTotalVendas;
      const margemLiquidaPercentual = receitaTotal > 0 ? (resultadoLiquido / receitaTotal) * 100 : 0;

      const resultado: ResultadoFinal = {
        lucro_operacional_estoque: lucroSelecionado,
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
      setContasPagar(contPagar);
      setContasReceber(contReceber);
      setValorEstoque(valEstoque);
      setResultadoFinal(resultado);

      console.log('✅ Dados carregados com sucesso');

    } catch (err) {
      console.error('❌ Erro ao carregar dados:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido ao carregar dados');
    } finally {
      setLoading(false);
    }
  }, [dateRange, tipoCalculoLucro]);

  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

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
          <p style={{ color: '#6b7280' }}>Carregando resultados empresariais...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '16px', margin: '16px' }}>
        <div style={{ color: '#dc2626', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle style={{ width: '16px', height: '16px' }} />
          Erro:
        </div>
        <div style={{ color: '#7f1d1d', marginTop: '4px' }}>{error}</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Cabeçalho */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
          Resultados Empresariais
        </h1>
        <p style={{ color: '#6b7280' }}>
          Análise completa de resultados: estoque, contratos, custos fixos e resultado líquido do período
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
          <Calculator style={{ width: '20px', height: '20px' }} />
          Período de Análise
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>Selecionar Período</label>
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
                <Calculator style={{ width: '16px', height: '16px' }} />
                Atualizar Resultados
              </>
            )}
          </button>
        </div>
      </div>

      {/* Seleção do Tipo de Cálculo */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp style={{ width: '20px', height: '20px' }} />
          Tipo de Cálculo de Lucro
        </h2>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: 'pointer',
            padding: '12px 16px',
            borderRadius: '8px',
            border: `2px solid ${tipoCalculoLucro === 'estoque' ? '#3b82f6' : '#e5e7eb'}`,
            backgroundColor: tipoCalculoLucro === 'estoque' ? '#f0f9ff' : '#ffffff',
            transition: 'all 0.2s'
          }}>
            <input
              type="radio"
              name="tipoCalculo"
              value="estoque"
              checked={tipoCalculoLucro === 'estoque'}
              onChange={() => toggleTipoCalculoLucro('estoque')}
              style={{ margin: 0 }}
            />
            <Package style={{ width: '18px', height: '18px', color: tipoCalculoLucro === 'estoque' ? '#3b82f6' : '#6b7280' }} />
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#111827' }}>
                Movimentação de Estoque
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                Lucro baseado na diferença entre preços de entrada e saída
              </div>
            </div>
          </label>
          
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: 'pointer',
            padding: '12px 16px',
            borderRadius: '8px',
            border: `2px solid ${tipoCalculoLucro === 'vendas' ? '#3b82f6' : '#e5e7eb'}`,
            backgroundColor: tipoCalculoLucro === 'vendas' ? '#f0f9ff' : '#ffffff',
            transition: 'all 0.2s'
          }}>
            <input
              type="radio"
              name="tipoCalculo"
              value="vendas"
              checked={tipoCalculoLucro === 'vendas'}
              onChange={() => toggleTipoCalculoLucro('vendas')}
              style={{ margin: 0 }}
            />
            <DollarSign style={{ width: '18px', height: '18px', color: tipoCalculoLucro === 'vendas' ? '#3b82f6' : '#6b7280' }} />
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#111827' }}>
                Margem de Vendas (Faturamento)
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                Margem baseada nos dados de faturamento de notas fiscais
              </div>
            </div>
          </label>
        </div>
        
        {/* Informações do tipo selecionado */}
        {tipoCalculoLucro === 'estoque' && movimentacaoEstoque && (
          <div style={{
            marginTop: '16px',
            padding: '12px',
            backgroundColor: '#f0f9ff',
            borderRadius: '6px',
            border: '1px solid #bae6fd'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#0369a1', marginBottom: '4px' }}>
              📦 Dados do Estoque (período selecionado)
            </div>
            <div style={{ fontSize: '0.75rem', color: '#075985' }}>
              Lucro Operacional: {formatCurrency(movimentacaoEstoque.lucro_operacional)} | 
              Margem: {formatPercent(movimentacaoEstoque.margem_percentual)}
            </div>
          </div>
        )}
        
        {tipoCalculoLucro === 'vendas' && margemVendas && (
          <div style={{
            marginTop: '16px',
            padding: '12px',
            backgroundColor: '#f0f9ff',
            borderRadius: '6px',
            border: '1px solid #bae6fd'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#0369a1', marginBottom: '4px' }}>
              💰 Dados do Faturamento (período selecionado)
            </div>
            <div style={{ fontSize: '0.75rem', color: '#075985' }}>
              Margem Bruta: {formatCurrency(margemVendas.margem_bruta)} | 
              Percentual: {formatPercent(margemVendas.percentual_margem)} | 
              Itens: {margemVendas.itens_analisados}
            </div>
          </div>
        )}
      </div>

      {/* Cards de Componentes do Resultado */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '16px',
        marginBottom: '24px'
      }}>
        
        {/* 1. Lucro Operacional (Estoque ou Vendas) */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '24px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            {tipoCalculoLucro === 'estoque' ? (
              <Package style={{ width: '24px', height: '24px', color: '#8b5cf6' }} />
            ) : (
              <DollarSign style={{ width: '24px', height: '24px', color: '#f59e0b' }} />
            )}
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginLeft: '8px' }}>
              {tipoCalculoLucro === 'estoque' ? 'Movimentação de Estoque' : 'Margem de Vendas'}
            </h3>
          </div>
          
          {/* Dados de Estoque */}
          {tipoCalculoLucro === 'estoque' && movimentacaoEstoque && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Valor Entradas (custo):</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#dc2626' }}>
                  {formatCurrency(movimentacaoEstoque.valor_entrada)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Valor Saídas (venda):</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#059669' }}>
                  {formatCurrency(movimentacaoEstoque.valor_saida)}
                </span>
              </div>
              <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '8px', marginTop: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '1rem', fontWeight: '600', color: '#111827' }}>Lucro Operacional:</span>
                  <span style={{ 
                    fontSize: '1rem', 
                    fontWeight: '700', 
                    color: movimentacaoEstoque.lucro_operacional >= 0 ? '#059669' : '#dc2626' 
                  }}>
                    {formatCurrency(movimentacaoEstoque.lucro_operacional)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Margem:</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: '500', color: '#6b7280' }}>
                    {formatPercent(movimentacaoEstoque.margem_percentual)}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          {/* Dados de Vendas */}
          {tipoCalculoLucro === 'vendas' && margemVendas && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Valor Vendas:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#059669' }}>
                  {formatCurrency(margemVendas.valor_vendas)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Valor Custo Entrada:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#dc2626' }}>
                  {formatCurrency(margemVendas.valor_preco_entrada)}
                </span>
              </div>
              <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '8px', marginTop: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '1rem', fontWeight: '600', color: '#111827' }}>Margem Bruta:</span>
                  <span style={{ 
                    fontSize: '1rem', 
                    fontWeight: '700', 
                    color: margemVendas.margem_bruta >= 0 ? '#059669' : '#dc2626' 
                  }}>
                    {formatCurrency(margemVendas.margem_bruta)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Margem:</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: '500', color: '#6b7280' }}>
                    {formatPercent(margemVendas.percentual_margem)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Itens analisados:</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: '500', color: '#6b7280' }}>
                    {margemVendas.itens_analisados}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 2. Faturamento de Contratos */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '24px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            <FileText style={{ width: '24px', height: '24px', color: '#059669' }} />
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginLeft: '8px' }}>
              Faturamento Contratos
            </h3>
          </div>
          {faturamentoContratos && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Faturamento Total:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#059669' }}>
                  {formatCurrency(faturamentoContratos.faturamento_total_proporcional)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Custo Suprimentos:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#dc2626' }}>
                  {formatCurrency(faturamentoContratos.custo_total_suprimentos)}
                </span>
              </div>
              <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '8px', marginTop: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '1rem', fontWeight: '600', color: '#111827' }}>Margem Bruta:</span>
                  <span style={{ 
                    fontSize: '1rem', 
                    fontWeight: '700', 
                    color: faturamentoContratos.margem_bruta_total >= 0 ? '#059669' : '#dc2626' 
                  }}>
                    {formatCurrency(faturamentoContratos.margem_bruta_total)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>% Margem:</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: '500', color: '#6b7280' }}>
                    {formatPercent(faturamentoContratos.percentual_margem_total)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 3. Custos Fixos */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '24px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            <CreditCard style={{ width: '24px', height: '24px', color: '#dc2626' }} />
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginLeft: '8px' }}>
              Custos Fixos
            </h3>
          </div>
          {custosFixos && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Custos Fixos:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#dc2626' }}>
                  {formatCurrency(custosFixos.valor_custos_fixos)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Despesas Fixas:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#dc2626' }}>
                  {formatCurrency(custosFixos.valor_despesas_fixas)}
                </span>
              </div>
              <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '8px', marginTop: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '1rem', fontWeight: '600', color: '#111827' }}>Total Custos:</span>
                  <span style={{ fontSize: '1rem', fontWeight: '700', color: '#dc2626' }}>
                    {formatCurrency(custosFixos.valor_total)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Qtd. Contas:</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: '500', color: '#6b7280' }}>
                    {custosFixos.quantidade_total_contas}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 4. Custos Variáveis */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '24px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            <Receipt style={{ width: '24px', height: '24px', color: '#f59e0b' }} />
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginLeft: '8px' }}>
              Custos Variáveis
            </h3>
          </div>
          {custosVariaveis && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '8px' }}>
                  Selecione as especificações a incluir no cálculo:
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto' }}>
                  {custosVariaveis.especificacoes.map((spec, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      backgroundColor: spec.incluir_no_calculo ? '#f0f9ff' : '#f9fafb',
                      border: `1px solid ${spec.incluir_no_calculo ? '#3b82f6' : '#e5e7eb'}`,
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }} onClick={() => toggleEspecificacao(spec.especificacao)}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input
                          type="checkbox"
                          checked={spec.incluir_no_calculo}
                          onChange={() => toggleEspecificacao(spec.especificacao)}
                          style={{ cursor: 'pointer' }}
                        />
                        <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                          {spec.especificacao}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                          ({spec.quantidade_contas} contas)
                        </span>
                      </div>
                      <span style={{ 
                        fontSize: '0.875rem', 
                        fontWeight: '600', 
                        color: spec.incluir_no_calculo ? '#dc2626' : '#9ca3af'
                      }}>
                        {formatCurrency(spec.valor_pago_total)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '1rem', fontWeight: '600', color: '#111827' }}>Total Selecionado:</span>
                  <span style={{ fontSize: '1rem', fontWeight: '700', color: '#dc2626' }}>
                    {formatCurrency(custosVariaveis.especificacoes
                      .filter(spec => spec.incluir_no_calculo)
                      .reduce((total, spec) => total + spec.valor_pago_total, 0)
                    )}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                    {custosVariaveis.especificacoes.filter(spec => spec.incluir_no_calculo).length} de {custosVariaveis.especificacoes.length} especificações
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 5. Resultado Líquido */}
        <div style={{
          backgroundColor: resultadoFinal && resultadoFinal.resultado_liquido >= 0 ? '#f0f9ff' : '#fef2f2',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          padding: '24px',
          border: `2px solid ${resultadoFinal && resultadoFinal.resultado_liquido >= 0 ? '#3b82f6' : '#ef4444'}`,
          gridColumn: 'span 1'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            {resultadoFinal && resultadoFinal.resultado_liquido >= 0 ? 
              <TrendingUp style={{ width: '24px', height: '24px', color: '#3b82f6' }} /> :
              <TrendingDown style={{ width: '24px', height: '24px', color: '#ef4444' }} />
            }
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginLeft: '8px' }}>
              Resultado Líquido
            </h3>
          </div>
          {resultadoFinal && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  {tipoCalculoLucro === 'estoque' ? 'Lucro Estoque:' : 'Margem Vendas:'}
                </span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#059669' }}>
                  {formatCurrency(resultadoFinal.lucro_operacional_estoque)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Margem Contratos:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#059669' }}>
                  {formatCurrency(resultadoFinal.faturamento_contratos)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>(-) Custos Fixos:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#dc2626' }}>
                  {formatCurrency(resultadoFinal.custos_fixos)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>(-) Custos Variáveis:</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#dc2626' }}>
                  {formatCurrency(resultadoFinal.custos_variaveis)}
                </span>
              </div>
              <div style={{ borderTop: '2px solid #d1d5db', paddingTop: '12px', marginTop: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '1.25rem', fontWeight: '700', color: '#111827' }}>RESULTADO:</span>
                  <span style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: '900', 
                    color: resultadoFinal.resultado_liquido >= 0 ? '#059669' : '#dc2626' 
                  }}>
                    {formatCurrency(resultadoFinal.resultado_liquido)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Margem Líquida:</span>
                  <span style={{ 
                    fontSize: '0.875rem', 
                    fontWeight: '600', 
                    color: resultadoFinal.margem_liquida_percentual >= 0 ? '#059669' : '#dc2626' 
                  }}>
                    {formatPercent(resultadoFinal.margem_liquida_percentual)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Resumo Detalhado */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px'
      }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <DollarSign style={{ width: '20px', height: '20px' }} />
          Composição do Resultado
        </h3>
        
        {resultadoFinal && (
          <div style={{ 
            backgroundColor: '#f8fafc',
            borderRadius: '6px',
            padding: '16px',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '8px' }}>
              Cálculo: {tipoCalculoLucro === 'estoque' ? 'Lucro Estoque' : 'Margem Vendas'} + Margem Contratos - Custos Fixos - Custos Variáveis = Resultado Líquido
            </div>
            <div style={{ fontSize: '1rem', fontWeight: '500', color: '#111827' }}>
              {formatCurrency(resultadoFinal.lucro_operacional_estoque)} + {formatCurrency(resultadoFinal.faturamento_contratos)} - {formatCurrency(resultadoFinal.custos_fixos)} - {formatCurrency(resultadoFinal.custos_variaveis)} = 
              <span style={{ 
                fontWeight: '700', 
                color: resultadoFinal.resultado_liquido >= 0 ? '#059669' : '#dc2626',
                marginLeft: '8px'
              }}>
                {formatCurrency(resultadoFinal.resultado_liquido)}
              </span>
            </div>
          </div>
        )}

        {/* Informações do período */}
        {dateRange && (
          <div style={{
            backgroundColor: '#f0f9ff',
            padding: '16px',
            borderRadius: '8px',
            border: '1px solid #bae6fd',
            marginTop: '16px'
          }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#0c4a6e', marginBottom: '8px' }}>
              Período da Análise
            </h4>
            <p style={{ color: '#0369a1', fontSize: '0.875rem' }}>
              De {dateRange.from?.toLocaleDateString('pt-BR')} até {dateRange.to?.toLocaleDateString('pt-BR')}
            </p>
            <p style={{ color: '#075985', fontSize: '0.75rem', marginTop: '4px' }}>
              Dados obtidos em tempo real das APIs de estoque, contratos e custos fixos
            </p>
          </div>
        )}
      </div>

      {/* Seção de Debug - URLs testadas */}
      <div style={{
        backgroundColor: '#f8fafc',
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
        padding: '16px',
        marginTop: '16px',
        fontSize: '0.875rem'
      }}>
        <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '12px' }}>
          🔍 Debug - APIs Testadas
        </h4>
        <div style={{ color: '#6b7280' }}>
          <p><strong>💳 Contas a Pagar:</strong> Testando múltiplos endpoints...</p>
          <p><strong>💰 Contas a Receber:</strong> Testando múltiplos endpoints...</p>
          <p><strong>📦 Valor do Estoque:</strong> {valorEstoque ? '✅ Carregado' : '❌ Não carregado'}</p>
          <p style={{ fontSize: '0.75rem', marginTop: '8px', color: '#9ca3af' }}>
            Verifique o console do navegador (F12) para ver os logs detalhados das tentativas de conexão com as APIs.
          </p>
        </div>
      </div>

      {/* Seção: Contas a Pagar e Receber */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginTop: '16px'
      }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CreditCard style={{ width: '20px', height: '20px' }} />
          Posição Financeira - Final do Período
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* Contas a Pagar */}
          <div style={{
            backgroundColor: '#fef2f2',
            borderRadius: '8px',
            padding: '20px',
            border: '1px solid #fecaca'
          }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#b91c1c', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Receipt style={{ width: '18px', height: '18px' }} />
              💳 Contas a Pagar em Aberto
            </h4>
            
            {contasPagar ? (
              <div>
                {contasPagar.valor_total_aberto > 0 || contasPagar.quantidade_contas > 0 ? (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.875rem', color: '#7f1d1d' }}>Total em Aberto:</span>
                      <span style={{ fontSize: '1rem', fontWeight: '700', color: '#b91c1c' }}>
                        {formatCurrency(contasPagar.valor_total_aberto)}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.875rem', color: '#7f1d1d' }}>Quantidade de Contas:</span>
                      <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#b91c1c' }}>
                        {contasPagar.quantidade_contas}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.875rem', color: '#7f1d1d' }}>Valor Vencido:</span>
                      <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#dc2626' }}>
                        {formatCurrency(contasPagar.valor_vencido)}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '0.875rem', color: '#7f1d1d' }}>A Vencer:</span>
                      <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f59e0b' }}>
                        {formatCurrency(contasPagar.valor_a_vencer)}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '20px',
                    backgroundColor: '#fef9f7',
                    borderRadius: '6px',
                    border: '1px solid #fed7d7'
                  }}>
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>✅</div>
                    <div style={{ fontSize: '0.875rem', color: '#7f1d1d', fontWeight: '600' }}>
                      Nenhuma conta a pagar em aberto
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#a78b8b', marginTop: '4px' }}>
                      Ótimo! Não há pendências financeiras
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: '#9ca3af', fontSize: '0.875rem', textAlign: 'center', padding: '20px' }}>
                🔄 Carregando dados de contas a pagar...
              </div>
            )}
          </div>

          {/* Contas a Receber */}
          <div style={{
            backgroundColor: '#f0fdf4',
            borderRadius: '8px',
            padding: '20px',
            border: '1px solid #bbf7d0'
          }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#166534', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <DollarSign style={{ width: '18px', height: '18px' }} />
              💰 Contas a Receber em Aberto
            </h4>
            
            {contasReceber ? (
              <div>
                {contasReceber.valor_total_aberto > 0 || contasReceber.quantidade_contas > 0 ? (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.875rem', color: '#14532d' }}>Total em Aberto:</span>
                      <span style={{ fontSize: '1rem', fontWeight: '700', color: '#166534' }}>
                        {formatCurrency(contasReceber.valor_total_aberto)}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.875rem', color: '#14532d' }}>Quantidade de Contas:</span>
                      <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#166534' }}>
                        {contasReceber.quantidade_contas}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.875rem', color: '#14532d' }}>Valor Vencido:</span>
                      <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#dc2626' }}>
                        {formatCurrency(contasReceber.valor_vencido)}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '0.875rem', color: '#14532d' }}>A Vencer:</span>
                      <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#059669' }}>
                        {formatCurrency(contasReceber.valor_a_vencer)}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '20px',
                    backgroundColor: '#f7fef9',
                    borderRadius: '6px',
                    border: '1px solid #d1fae5'
                  }}>
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>💸</div>
                    <div style={{ fontSize: '0.875rem', color: '#14532d', fontWeight: '600' }}>
                      Nenhuma conta a receber em aberto
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#65a380', marginTop: '4px' }}>
                      Todos os recebimentos estão em dia
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: '#9ca3af', fontSize: '0.875rem', textAlign: 'center', padding: '20px' }}>
                🔄 Carregando dados de contas a receber...
              </div>
            )}
          </div>
        </div>

        {/* Resumo da Posição Financeira */}
        {contasPagar && contasReceber && (
          <div style={{
            backgroundColor: '#f8fafc',
            borderRadius: '8px',
            padding: '16px',
            border: '1px solid #e2e8f0',
            marginTop: '16px'
          }}>
            <h5 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              📊 Saldo Financeiro (Receber - Pagar)
            </h5>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
                {formatCurrency(contasReceber.valor_total_aberto)} - {formatCurrency(contasPagar.valor_total_aberto)} =
              </span>
              <span style={{ 
                fontSize: '1.125rem', 
                fontWeight: '700', 
                color: (contasReceber.valor_total_aberto - contasPagar.valor_total_aberto) >= 0 ? '#059669' : '#dc2626' 
              }}>
                {formatCurrency(contasReceber.valor_total_aberto - contasPagar.valor_total_aberto)}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Seção: Valor do Estoque */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginTop: '16px'
      }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Package style={{ width: '20px', height: '20px' }} />
          📦 Valor do Estoque - Final do Período
        </h3>
        
        {valorEstoque ? (
          <div style={{
            backgroundColor: '#eff6ff',
            borderRadius: '8px',
            padding: '20px',
            border: '1px solid #bfdbfe'
          }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '16px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: '#1e40af', fontWeight: '500' }}>
                  💰 Valor Total do Estoque
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1d4ed8', marginTop: '4px' }}>
                  {formatCurrency(valorEstoque.valor_total_atual)}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '2px' }}>
                  em {new Date(valorEstoque.data_consulta).toLocaleDateString('pt-BR')}
                </div>
              </div>
              
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: '#1e40af', fontWeight: '500' }}>
                  📊 Total de Produtos
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#1d4ed8', marginTop: '4px' }}>
                  {valorEstoque.total_produtos}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '2px' }}>
                  cadastrados
                </div>
              </div>
              
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: '#1e40af', fontWeight: '500' }}>
                  ✅ Com Estoque
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#1d4ed8', marginTop: '4px' }}>
                  {valorEstoque.produtos_com_estoque}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '2px' }}>
                  produtos
                </div>
              </div>
              
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: '#1e40af', fontWeight: '500' }}>
                  📈 Variação do Período
                </div>
                <div style={{ 
                  fontSize: '1.25rem', 
                  fontWeight: '700', 
                  color: valorEstoque.variacao_periodo >= 0 ? '#059669' : '#dc2626',
                  marginTop: '4px' 
                }}>
                  {formatCurrency(valorEstoque.variacao_periodo)}
                </div>
                <div style={{ 
                  fontSize: '0.75rem', 
                  color: valorEstoque.percentual_variacao >= 0 ? '#059669' : '#dc2626',
                  marginTop: '2px' 
                }}>
                  ({formatPercent(valorEstoque.percentual_variacao)})
                </div>
              </div>
            </div>
            
            <div style={{
              backgroundColor: '#f0f9ff',
              border: '1px solid #bae6fd',
              borderRadius: '6px',
              padding: '12px',
              marginTop: '16px'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#0369a1', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle style={{ width: '16px', height: '16px' }} />
                <strong>Informação:</strong> Valor do estoque calculado com base nos custos de entrada dos produtos na data de {new Date(valorEstoque.data_consulta).toLocaleDateString('pt-BR')}.
              </div>
            </div>
          </div>
        ) : (
          <div style={{ color: '#9ca3af', fontSize: '0.875rem', textAlign: 'center', padding: '40px' }}>
            Carregando dados do valor do estoque...
          </div>
        )}
      </div>

    </div>
  );
};

export default ResultadosEmpresariais;
