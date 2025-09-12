// src/components/dashboard/PosicaoFinanceira.tsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Package,
  DollarSign,
  CreditCard,
  Calculator,
  AlertCircle,
  Receipt
} from "lucide-react";
import { SeparateDatePicker } from '../common/SeparateDatePicker';

//  Interfaces para os dados
interface ContaItem {
  fornecedor?: {
    id: number;
    nome: string;
    cnpj_cpf: string | null;
    especificacao: string;
    tipo_custo: "FIXO" | "VARIÁVEL" | "NÃO CLASSIFICADO";
  };
  cliente?: {
    id: number;
    nome: string;
    cnpj_cpf: string;
  };
  total_contas: number;
  valor_total: number;
  periodo_vencimento: {
    menor_data: string;
    maior_data: string;
  };
}

interface DetalhesContas {
  antes_data_corte?: ContaItem[];
  depois_data_corte?: ContaItem[];
}

interface ContasPagar {
  valor_total_aberto: number;
  quantidade_contas: number;
  valor_vencido: number;
  valor_a_vencer: number;
  detalhes: DetalhesContas;
}

interface ContasReceber {
  valor_total_aberto: number;
  quantidade_contas: number;
  valor_vencido: number;
  valor_a_vencer: number;
  detalhes: DetalhesContas;
}

interface ValorEstoque {
  valor_total_atual: number;
  data_consulta: string;
  total_produtos: number;
  produtos_com_estoque: number;
  variacao_periodo: number;
  percentual_variacao: number;
}

interface ContasNaoPagas {
  data_corte: string;
  filtros: {
    tipo: string;
    incluir_canceladas: boolean;
  };
  resumo_geral: {
    antes_data_corte: {
      total_contas_pagar: number;
      valor_total_pagar: number;
      total_contas_receber: number;
      valor_total_receber: number;
      total_fornecedores: number;
      total_clientes: number;
      saldo_liquido: number;
    };
    depois_data_corte: {
      total_contas_pagar: number;
      valor_total_pagar: number;
      total_contas_receber: number;
      valor_total_receber: number;
      total_fornecedores: number;
      total_clientes: number;
      saldo_liquido: number;
    };
    saldo_total: number;
  };
  detalhamento: {
    contas_a_pagar: {
      antes_data_corte: ContaItem[];
      depois_data_corte: ContaItem[];
    };
    contas_a_receber: {
      antes_data_corte: ContaItem[];
      depois_data_corte: ContaItem[];
    };
  };
  metadados: {
    data_consulta: string;
    total_registros_antes: number;
    total_registros_depois: number;
  };
}

const PosicaoFinanceira: React.FC = () => {
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
    to: new Date()
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estados para filtros
  const [especificacoesFornecedores, setEspecificacoesFornecedores] = useState<string[]>([]);
  const [especificacoesSelecionadas, setEspecificacoesSelecionadas] = useState<string[]>([]);
  const [contasOriginalPagar, setContasOriginalPagar] = useState<ContasPagar | null>(null);

  // Função para dividir especificações por tipo de custo (da API)
  const dividirEspecificacoesPorTipo = (contas: ContaItem[]) => {
    const custosFixos: string[] = [];
    const custosVariaveis: string[] = [];
    const naoClassificados: string[] = [];
    
    // Extrair especificações únicas e seus tipos
    const especificacoesMap = new Map<string, string>();
    
    contas.forEach(conta => {
      if (conta.fornecedor?.especificacao) {
        const especificacao = conta.fornecedor.especificacao;
        const tipoCusto = conta.fornecedor.tipo_custo || "NÃO CLASSIFICADO";
        especificacoesMap.set(especificacao, tipoCusto);
      }
    });
    
    // Separar por tipo de custo
    especificacoesMap.forEach((tipoCusto, especificacao) => {
      switch(tipoCusto) {
        case "FIXO":
          custosFixos.push(especificacao);
          break;
        case "VARIÁVEL":
          custosVariaveis.push(especificacao);
          break;
        default:
          naoClassificados.push(especificacao);
          break;
      }
    });
    
    return {
      custosFixos: custosFixos.sort(),
      custosVariaveis: custosVariaveis.sort(),
      naoClassificados: naoClassificados.sort()
    };
  };

  // Estados para os dados
  const [contasPagar, setContasPagar] = useState<ContasPagar | null>(null);
  const [contasReceber, setContasReceber] = useState<ContasReceber | null>(null);
  const [valorEstoque, setValorEstoque] = useState<ValorEstoque | null>(null);
  const [contasNaoPagas, setContasNaoPagas] = useState<ContasNaoPagas | null>(null);

  // Funções de formatação
  const formatCurrency = (value: number | null | undefined) => {
    const numericValue = Number(value) || 0;
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(numericValue);
  };

  const formatPercent = (value: number | null | undefined) => {
    const numericValue = Number(value) || 0;
    return `${numericValue.toFixed(1)}%`;
  };

  // Função para buscar contas a pagar em aberto usando endpoint unificado
  const buscarContasPagar = useCallback(async (dataInicial: string, dataFinal: string) => {
    try {
      console.log('🚀 Buscando contas a pagar para período:', dataInicial, 'até', dataFinal);
      
      // Usar a data final como data de corte com filtro por data de emissão
      const url = `http://localhost:8000/contas/contas-nao-pagas-por-data-corte/?data_corte=${dataFinal}&tipo=pagar&filtrar_por_data_emissao=true`;
      console.log('🔗 Endpoint de contas a pagar:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (response.ok) {
        const dados = await response.json();
        console.log('✅ Dados de contas não pagas recebidos para data:', dataFinal, dados);
        
        // Extrair dados de contas a pagar do resumo geral
        const resumoGeral = dados.resumo_geral || {};
        const totalPagar = (resumoGeral.antes_data_corte?.valor_total_pagar || 0) + 
                          (resumoGeral.depois_data_corte?.valor_total_pagar || 0);
        const quantidadePagar = (resumoGeral.antes_data_corte?.total_contas_pagar || 0) + 
                               (resumoGeral.depois_data_corte?.total_contas_pagar || 0);
        
        console.log('💰 Valores de contas a pagar calculados:', {
          dataCorte: dataFinal,
          valorAntes: resumoGeral.antes_data_corte?.valor_total_pagar || 0,
          valorDepois: resumoGeral.depois_data_corte?.valor_total_pagar || 0,
          totalPagar: totalPagar,
          quantidadePagar: quantidadePagar
        });
        
        // Extrair especificações dos fornecedores das contas detalhadas
        const contasDetalhadas = dados.detalhamento?.contas_a_pagar || {};
        const especificacoes = new Set<string>();
        let temEspecificacoesVazias = false;
        
        // Combinar contas antes e depois da data corte
        const todasContas = [
          ...(contasDetalhadas.antes_data_corte || []),
          ...(contasDetalhadas.depois_data_corte || [])
        ];
        
        todasContas.forEach((conta: { fornecedor?: { especificacao?: string } }) => {
          if (conta.fornecedor?.especificacao) {
            especificacoes.add(conta.fornecedor.especificacao);
          } else {
            // Marcar que existem contas sem especificação
            temEspecificacoesVazias = true;
          }
        });
        
        // Atualizar lista de especificações
        const especificacoesArray = Array.from(especificacoes).sort();
        
        // Adicionar opção para especificações em branco se existirem
        if (temEspecificacoesVazias) {
          especificacoesArray.push('(Em Branco)');
        }
        
        // Preservar especificações selecionadas que ainda existem na nova lista
        const especificacoesSelecionadasValidas = especificacoesSelecionadas.filter(
          especSelecionada => especificacoesArray.includes(especSelecionada)
        );
        
        setEspecificacoesFornecedores(especificacoesArray);
        
        // Apenas atualizar as seleções se houve mudança na lista de especificações válidas
        if (especificacoesSelecionadasValidas.length !== especificacoesSelecionadas.length) {
          setEspecificacoesSelecionadas(especificacoesSelecionadasValidas);
          console.log('🔄 Especificações selecionadas ajustadas:', especificacoesSelecionadasValidas);
        }
        
        console.log('📋 Especificações encontradas:', especificacoesArray);
        console.log('✅ Especificações selecionadas preservadas:', especificacoesSelecionadas);
        
        const resultadoContas = {
          valor_total_aberto: totalPagar,
          quantidade_contas: quantidadePagar,
          valor_vencido: resumoGeral.antes_data_corte?.valor_total_pagar || 0,
          valor_a_vencer: resumoGeral.depois_data_corte?.valor_total_pagar || 0,
          detalhes: contasDetalhadas
        };
        
        return resultadoContas;
      } else {
        console.warn('❌ Endpoint retornou erro:', response.status);
        return {
          valor_total_aberto: 0,
          quantidade_contas: 0,
          valor_vencido: 0,
          valor_a_vencer: 0,
          detalhes: []
        };
      }
    } catch (error) {
      console.error('💥 Erro ao buscar contas a pagar:', error);
      return {
        valor_total_aberto: 0,
        quantidade_contas: 0,
        valor_vencido: 0,
        valor_a_vencer: 0,
        detalhes: []
      };
    }
  }, [especificacoesSelecionadas]);

  // Função para lidar com mudança de especificação
  const handleEspecificacaoChange = (especificacao: string, checked: boolean) => {
    let novasEspecificacoes: string[];
    
    if (checked) {
      // Adicionar especificação
      novasEspecificacoes = [...especificacoesSelecionadas, especificacao];
    } else {
      // Remover especificação
      novasEspecificacoes = especificacoesSelecionadas.filter(e => e !== especificacao);
    }
    
    setEspecificacoesSelecionadas(novasEspecificacoes);
  };

  // Função para selecionar/deselecionar todas as especificações
  const handleSelecionarTodas = (selecionarTodas: boolean) => {
    const novasEspecificacoes = selecionarTodas ? [...especificacoesFornecedores] : [];
    setEspecificacoesSelecionadas(novasEspecificacoes);
  };

  // Função para buscar contas a receber em aberto usando endpoint unificado
  const buscarContasReceber = useCallback(async (dataInicial: string, dataFinal: string) => {
    try {
      console.log('🚀 Buscando contas a receber para período:', dataInicial, 'até', dataFinal);
      
      // Usar a data final como data de corte com filtro por data de emissão
      const url = `http://localhost:8000/contas/contas-nao-pagas-por-data-corte/?data_corte=${dataFinal}&tipo=receber&filtrar_por_data_emissao=true`;
      console.log('🔗 Endpoint de contas a receber:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (response.ok) {
        const dados = await response.json();
        console.log('✅ Dados de contas não pagas recebidos para data:', dataFinal, dados);
        
        // Extrair dados de contas a receber do resumo geral
        const resumoGeral = dados.resumo_geral || {};
        const totalReceber = (resumoGeral.antes_data_corte?.valor_total_receber || 0) + 
                            (resumoGeral.depois_data_corte?.valor_total_receber || 0);
        const quantidadeReceber = (resumoGeral.antes_data_corte?.total_contas_receber || 0) + 
                                 (resumoGeral.depois_data_corte?.total_contas_receber || 0);
        
        console.log('💰 Valores de contas a receber calculados:', {
          dataCorte: dataFinal,
          valorAntes: resumoGeral.antes_data_corte?.valor_total_receber || 0,
          valorDepois: resumoGeral.depois_data_corte?.valor_total_receber || 0,
          totalReceber: totalReceber,
          quantidadeReceber: quantidadeReceber
        });
        
        return {
          valor_total_aberto: totalReceber,
          quantidade_contas: quantidadeReceber,
          valor_vencido: resumoGeral.antes_data_corte?.valor_total_receber || 0,
          valor_a_vencer: resumoGeral.depois_data_corte?.valor_total_receber || 0,
          detalhes: dados.detalhamento?.contas_a_receber || []
        };
      } else {
        console.warn('❌ Endpoint retornou erro:', response.status);
        return {
          valor_total_aberto: 0,
          quantidade_contas: 0,
          valor_vencido: 0,
          valor_a_vencer: 0,
          detalhes: []
        };
      }
    } catch (error) {
      console.error('💥 Erro ao buscar contas a receber:', error);
      return {
        valor_total_aberto: 0,
        quantidade_contas: 0,
        valor_vencido: 0,
        valor_a_vencer: 0,
        detalhes: []
      };
    }
  }, []);

  // Função para buscar valor do estoque
  const buscarValorEstoque = useCallback(async (dataFinal: string) => {
    try {
      const response = await fetch(`http://localhost:8000/contas/estoque-controle/estoque_atual/?data=${dataFinal}&resumo=true`);
      if (!response.ok) {
        console.warn('Endpoint de valor do estoque não encontrado');
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
      console.error('💥 Erro ao buscar valor do estoque:', error);
      return {
        valor_total_atual: 0,
        data_consulta: dataFinal,
        total_produtos: 0,
        produtos_com_estoque: 0,
        variacao_periodo: 0,
        percentual_variacao: 0
      };
    }
  }, []);

  // Função para buscar contas não pagas por data de corte
  const buscarContasNaoPagas = useCallback(async (dataCorte: string) => {
    try {
      console.log('🚀 Buscando contas não pagas por data de corte:', dataCorte);
      
      const url = `http://localhost:8000/contas/contas-nao-pagas-por-data-corte/?data_corte=${dataCorte}&tipo=ambos&filtrar_por_data_emissao=true`;
      console.log('🔗 Endpoint de análise temporal:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (response.ok) {
        const dados = await response.json();
        console.log('✅ Dados de contas não pagas recebidos:', dados);
        return dados;
      } else {
        console.warn('❌ Endpoint de contas não pagas retornou erro:', response.status);
        return null;
      }
    } catch (error) {
      console.error('💥 Erro ao buscar contas não pagas:', error);
      return null;
    }
  }, []);

  // Função principal para carregar dados
  const carregarDados = useCallback(async () => {
    if (!dateRange.from || !dateRange.to) return;

    setLoading(true);
    setError(null);

    try {
      const dataInicial = dateRange.from.toISOString().split('T')[0];
      const dataFinal = dateRange.to.toISOString().split('T')[0];

      console.log('📅 Carregando dados para período:', dataInicial, 'até', dataFinal);

      const [
        dadosContasPagar,
        dadosContasReceber,
        dadosValorEstoque,
        dadosContasNaoPagas
      ] = await Promise.all([
        buscarContasPagar(dataInicial, dataFinal),
        buscarContasReceber(dataInicial, dataFinal),
        buscarValorEstoque(dataFinal),
        buscarContasNaoPagas(dataFinal)
      ]);

      // Armazenar dados originais sempre primeiro
      setContasOriginalPagar(dadosContasPagar);
      setContasReceber(dadosContasReceber);
      setValorEstoque(dadosValorEstoque);
      setContasNaoPagas(dadosContasNaoPagas);

      console.log('✅ Dados da posição financeira carregados com sucesso');
      console.log('📊 Resumo final dos valores:', {
        dataCorte: dataFinal,
        contasPagar: dadosContasPagar?.valor_total_aberto || 0,
        contasReceber: dadosContasReceber?.valor_total_aberto || 0,
        valorEstoque: dadosValorEstoque?.valor_total_atual || 0,
        saldoLiquido: (dadosContasReceber?.valor_total_aberto || 0) + (dadosValorEstoque?.valor_total_atual || 0) - (dadosContasPagar?.valor_total_aberto || 0)
      });

      // Inicializar com dados originais - o filtro será aplicado pelo useEffect separado
      setContasPagar(dadosContasPagar);

    } catch (err) {
      console.error('❌ Erro ao carregar dados:', err);
      setError('Erro ao carregar dados da posição financeira');
    } finally {
      setLoading(false);
    }
  }, [dateRange, buscarContasPagar, buscarContasReceber, buscarValorEstoque, buscarContasNaoPagas]);

  // Aplicar filtros sempre que as especificações selecionadas ou dados originais mudarem
  useEffect(() => {
    if (!contasOriginalPagar) return;

    if (especificacoesSelecionadas.length === 0) {
      setContasPagar(contasOriginalPagar);
      return;
    }

    console.log('🔄 Aplicando filtros de especificação:', especificacoesSelecionadas);
    
    const filtrarContas = (contas: ContaItem[]) => {
      return contas.filter((conta: ContaItem) => {
        const especConta = conta.fornecedor?.especificacao || '';
        
        // Se "(Em Branco)" estiver selecionado, incluir contas sem especificação
        if (especificacoesSelecionadas.includes('(Em Branco)') && especConta === '') {
          return true;
        }
        
        // Verificar se a especificação da conta está nas selecionadas (excluindo "(Em Branco)")
        return especificacoesSelecionadas.filter(e => e !== '(Em Branco)').includes(especConta);
      });
    };

    const contasAntesFiltradas = filtrarContas(contasOriginalPagar.detalhes.antes_data_corte || []);
    const contasDepoisFiltradas = filtrarContas(contasOriginalPagar.detalhes.depois_data_corte || []);

    // Recalcular valores baseado nas contas filtradas
    const valorAntesTotal = contasAntesFiltradas.reduce((total: number, conta: ContaItem) => total + (conta.valor_total || 0), 0);
    const valorDepoisTotal = contasDepoisFiltradas.reduce((total: number, conta: ContaItem) => total + (conta.valor_total || 0), 0);

    const contasFiltradas = {
      valor_total_aberto: valorAntesTotal + valorDepoisTotal,
      quantidade_contas: contasAntesFiltradas.length + contasDepoisFiltradas.length,
      valor_vencido: valorAntesTotal,
      valor_a_vencer: valorDepoisTotal,
      detalhes: {
        antes_data_corte: contasAntesFiltradas,
        depois_data_corte: contasDepoisFiltradas
      }
    };

    console.log('📊 Contas filtradas:', contasFiltradas);
    setContasPagar(contasFiltradas);
  }, [especificacoesSelecionadas, contasOriginalPagar]);

  // Carregar dados iniciais
  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

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
          <CreditCard style={{ width: '28px', height: '28px', color: '#3b82f6' }} />
          💼 Posição Financeira
        </h2>
        <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '24px' }}>
          Análise da posição financeira usando <strong>data de corte: {dateRange.to?.toLocaleDateString('pt-BR')}</strong>. 
          Filtra apenas contas <strong>emitidas antes</strong> desta data e ainda em aberto.
        </p>

        {/* Controles */}
        <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '4px' }}>
              📅 Data de Corte (usará a data final)
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

      {/* Seção: Posição Financeira e Análise Temporal */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CreditCard style={{ width: '20px', height: '20px' }} />
          💰 Posição Financeira e Análise Temporal
        </h3>
        
        {contasNaoPagas && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
              <strong>Data de Corte:</strong> {new Date(contasNaoPagas.data_corte).toLocaleDateString('pt-BR')}
            </div>
          </div>
        )}
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '20px' }}>
          {/* Contas a Pagar */}
          <div style={{
            backgroundColor: '#fef2f2',
            borderRadius: '8px',
            padding: '20px',
            border: '1px solid #fecaca'
          }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#b91c1c', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Receipt style={{ width: '18px', height: '18px' }} />
              💳 Contas a Pagar em Aberto
            </h4>
            <p style={{ fontSize: '0.75rem', color: '#7f1d1d', marginBottom: '12px' }}>
              Emitidas antes de {dateRange.to?.toLocaleDateString('pt-BR')} e ainda em aberto
            </p>
            
            {/* Filtro por Especificação do Fornecedor */}
            {especificacoesFornecedores.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <label style={{ 
                  display: 'block', 
                  fontSize: '0.75rem', 
                  fontWeight: '500', 
                  color: '#7f1d1d',
                  marginBottom: '4px' 
                }}>
                  🏷️ Filtrar por Especificação:
                </label>
                
                {/* Controle Selecionar Todas */}
                <div style={{ 
                  marginBottom: '8px',
                  padding: '4px 0',
                  borderBottom: '1px solid #fecaca'
                }}>
                  <label style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    fontSize: '0.75rem',
                    color: '#7f1d1d',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}>
                    <input
                      type="checkbox"
                      checked={especificacoesSelecionadas.length === especificacoesFornecedores.length}
                      onChange={(e) => handleSelecionarTodas(e.target.checked)}
                      style={{ marginRight: '6px' }}
                    />
                    Selecionar Todas ({especificacoesFornecedores.length})
                  </label>
                </div>

                {/* Divisão por Tipo de Custo */}
                <div style={{
                  maxHeight: '200px',
                  overflowY: 'auto',
                  border: '1px solid #fecaca',
                  borderRadius: '4px',
                  backgroundColor: '#ffffff'
                }}>
                  {(() => {
                    if (!contasOriginalPagar) return null;
                    
                    // Obter todas as contas para análise
                    const todasContas = [
                      ...(contasOriginalPagar.detalhes?.antes_data_corte || []),
                      ...(contasOriginalPagar.detalhes?.depois_data_corte || [])
                    ];
                    
                    const { custosFixos, custosVariaveis, naoClassificados } = dividirEspecificacoesPorTipo(todasContas);
                    
                    // Adicionar especificações em branco se existirem
                    const especificacoesComBranco = [...especificacoesFornecedores];
                    
                    return (
                      <>
                        {/* Custos Fixos */}
                        {custosFixos.length > 0 && (
                          <div style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>
                            <div style={{ 
                              fontSize: '0.7rem', 
                              fontWeight: '600', 
                              color: '#059669', 
                              marginBottom: '4px',
                              display: 'flex',
                              alignItems: 'center'
                            }}>
                              💰 CUSTOS FIXOS ({custosFixos.length})
                            </div>
                            {custosFixos.map((especificacao) => (
                              <label 
                                key={`fixo-${especificacao}`}
                                style={{ 
                                  display: 'flex', 
                                  alignItems: 'center', 
                                  fontSize: '0.7rem',
                                  color: '#065f46',
                                  cursor: 'pointer',
                                  padding: '1px 4px',
                                  borderRadius: '2px'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#ecfdf5'}
                                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                              >
                                <input
                                  type="checkbox"
                                  checked={especificacoesSelecionadas.includes(especificacao)}
                                  onChange={(e) => handleEspecificacaoChange(especificacao, e.target.checked)}
                                  style={{ marginRight: '6px', transform: 'scale(0.8)' }}
                                />
                                {especificacao}
                              </label>
                            ))}
                          </div>
                        )}
                        
                        {/* Custos Variáveis */}
                        {custosVariaveis.length > 0 && (
                          <div style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>
                            <div style={{ 
                              fontSize: '0.7rem', 
                              fontWeight: '600', 
                              color: '#dc2626', 
                              marginBottom: '4px',
                              display: 'flex',
                              alignItems: 'center'
                            }}>
                              📈 CUSTOS VARIÁVEIS ({custosVariaveis.length})
                            </div>
                            {custosVariaveis.map((especificacao) => (
                              <label 
                                key={`variavel-${especificacao}`}
                                style={{ 
                                  display: 'flex', 
                                  alignItems: 'center', 
                                  fontSize: '0.7rem',
                                  color: '#991b1b',
                                  cursor: 'pointer',
                                  padding: '1px 4px',
                                  borderRadius: '2px'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fef2f2'}
                                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                              >
                                <input
                                  type="checkbox"
                                  checked={especificacoesSelecionadas.includes(especificacao)}
                                  onChange={(e) => handleEspecificacaoChange(especificacao, e.target.checked)}
                                  style={{ marginRight: '6px', transform: 'scale(0.8)' }}
                                />
                                {especificacao}
                              </label>
                            ))}
                          </div>
                        )}
                        
                        {/* Não Classificados */}
                        {naoClassificados.length > 0 && (
                          <div style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>
                            <div style={{ 
                              fontSize: '0.7rem', 
                              fontWeight: '600', 
                              color: '#92400e', 
                              marginBottom: '4px',
                              display: 'flex',
                              alignItems: 'center'
                            }}>
                              ❓ NÃO CLASSIFICADOS ({naoClassificados.length})
                            </div>
                            {naoClassificados.map((especificacao) => (
                              <label 
                                key={`nao-classificado-${especificacao}`}
                                style={{ 
                                  display: 'flex', 
                                  alignItems: 'center', 
                                  fontSize: '0.7rem',
                                  color: '#78350f',
                                  cursor: 'pointer',
                                  padding: '1px 4px',
                                  borderRadius: '2px'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fef3c7'}
                                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                              >
                                <input
                                  type="checkbox"
                                  checked={especificacoesSelecionadas.includes(especificacao)}
                                  onChange={(e) => handleEspecificacaoChange(especificacao, e.target.checked)}
                                  style={{ marginRight: '6px', transform: 'scale(0.8)' }}
                                />
                                {especificacao}
                              </label>
                            ))}
                          </div>
                        )}
                        
                        {/* Especificações em Branco */}
                        {especificacoesComBranco.includes('(Em Branco)') && (
                          <div style={{ padding: '8px' }}>
                            <div style={{ 
                              fontSize: '0.7rem', 
                              fontWeight: '600', 
                              color: '#6b7280', 
                              marginBottom: '4px',
                              display: 'flex',
                              alignItems: 'center'
                            }}>
                              🔍 ESPECIFICAÇÕES EM BRANCO
                            </div>
                            <label 
                              style={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                fontSize: '0.7rem',
                                color: '#4b5563',
                                cursor: 'pointer',
                                padding: '1px 4px',
                                borderRadius: '2px',
                                fontStyle: 'italic'
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                            >
                              <input
                                type="checkbox"
                                checked={especificacoesSelecionadas.includes('(Em Branco)')}
                                onChange={(e) => handleEspecificacaoChange('(Em Branco)', e.target.checked)}
                                style={{ marginRight: '6px', transform: 'scale(0.8)' }}
                              />
                              (Em Branco)
                            </label>
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>

                {/* Contador de selecionados */}
                {especificacoesSelecionadas.length > 0 && (
                  <div style={{ 
                    fontSize: '0.7rem', 
                    color: '#059669', 
                    marginTop: '4px',
                    fontWeight: '500'
                  }}>
                    ✓ {especificacoesSelecionadas.length} de {especificacoesFornecedores.length} selecionadas
                  </div>
                )}
              </div>
            )}
            
            {contasPagar ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#7f1d1d', fontWeight: '500' }}>
                    Valor Total
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#b91c1c', marginTop: '4px' }}>
                    {formatCurrency(contasPagar?.valor_total_aberto || 0)}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#7f1d1d', fontWeight: '500' }}>
                    Qtd. Contas
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#b91c1c', marginTop: '4px' }}>
                    {contasPagar?.quantidade_contas || 0}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#7f1d1d', fontWeight: '500' }}>
                    Vencidas
                  </div>
                  <div style={{ fontSize: '1rem', fontWeight: '600', color: '#dc2626', marginTop: '4px' }}>
                    {formatCurrency(contasPagar?.valor_vencido || 0)}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#7f1d1d', fontWeight: '500' }}>
                    A Vencer
                  </div>
                  <div style={{ fontSize: '1rem', fontWeight: '600', color: '#ea580c', marginTop: '4px' }}>
                    {formatCurrency(contasPagar?.valor_a_vencer || 0)}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ color: '#9ca3af', fontSize: '0.875rem', textAlign: 'center' }}>
                Carregando...
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
            <h4 style={{ fontSize: '1rem', fontWeight: '600', color: '#15803d', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <DollarSign style={{ width: '18px', height: '18px' }} />
              💰 Contas a Receber em Aberto
            </h4>
            <p style={{ fontSize: '0.75rem', color: '#14532d', marginBottom: '12px' }}>
              Emitidas antes de {dateRange.to?.toLocaleDateString('pt-BR')} e ainda em aberto
            </p>
            
            {contasReceber ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#14532d', fontWeight: '500' }}>
                    Valor Total
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#15803d', marginTop: '4px' }}>
                    {formatCurrency(contasReceber?.valor_total_aberto || 0)}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#14532d', fontWeight: '500' }}>
                    Qtd. Contas
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#15803d', marginTop: '4px' }}>
                    {contasReceber?.quantidade_contas || 0}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#14532d', fontWeight: '500' }}>
                    Vencidas
                  </div>
                  <div style={{ fontSize: '1rem', fontWeight: '600', color: '#dc2626', marginTop: '4px' }}>
                    {formatCurrency(contasReceber?.valor_vencido || 0)}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#14532d', fontWeight: '500' }}>
                    A Vencer
                  </div>
                  <div style={{ fontSize: '1rem', fontWeight: '600', color: '#059669', marginTop: '4px' }}>
                    {formatCurrency(contasReceber?.valor_a_vencer || 0)}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ color: '#9ca3af', fontSize: '0.875rem', textAlign: 'center' }}>
                Carregando...
              </div>
            )}
          </div>
        </div>

        {/* Seção: Valor do Estoque */}
        {valorEstoque && (
          <div style={{
            backgroundColor: '#eff6ff',
            borderRadius: '8px',
            padding: '20px',
            border: '1px solid #bfdbfe',
            marginBottom: '20px'
          }}>
            <h5 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#1e40af', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Package style={{ width: '18px', height: '18px' }} />
              📦 Valor do Estoque
            </h5>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: '#1e40af', fontWeight: '500' }}>
                  💰 Valor Total
                </div>
                <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#1d4ed8', marginTop: '4px' }}>
                  {formatCurrency(valorEstoque.valor_total_atual)}
                </div>
              </div>
              
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: '#1e40af', fontWeight: '500' }}>
                  📊 Produtos
                </div>
                <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#1d4ed8', marginTop: '4px' }}>
                  {valorEstoque.produtos_com_estoque}/{valorEstoque.total_produtos}
                </div>
              </div>
              
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: '#1e40af', fontWeight: '500' }}>
                  📈 Variação
                </div>
                <div style={{ 
                  fontSize: '1.125rem', 
                  fontWeight: '700', 
                  color: valorEstoque.variacao_periodo >= 0 ? '#059669' : '#dc2626',
                  marginTop: '4px' 
                }}>
                  {formatPercent(valorEstoque.percentual_variacao)}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Resumo da Posição Financeira */}
        {contasPagar && contasReceber && (
          <div style={{
            backgroundColor: '#f8fafc',
            borderRadius: '8px',
            padding: '16px',
            border: '1px solid #e2e8f0',
            marginBottom: '20px'
          }}>
            <h5 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              📊 Saldo Financeiro (Receber + Estoque - Pagar)
            </h5>
            <p style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '8px' }}>
              Calculado em {dateRange.to?.toLocaleDateString('pt-BR')}
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
                {formatCurrency(contasReceber?.valor_total_aberto || 0)} + {formatCurrency(valorEstoque?.valor_total_atual || 0)} - {formatCurrency(contasPagar?.valor_total_aberto || 0)} =
              </span>
              <span style={{ 
                fontSize: '1.125rem', 
                fontWeight: '700', 
                color: ((contasReceber?.valor_total_aberto || 0) + (valorEstoque?.valor_total_atual || 0) - (contasPagar?.valor_total_aberto || 0)) >= 0 ? '#059669' : '#dc2626' 
              }}>
                {formatCurrency((contasReceber?.valor_total_aberto || 0) + (valorEstoque?.valor_total_atual || 0) - (contasPagar?.valor_total_aberto || 0))}
              </span>
            </div>
          </div>
        )}


      </div>

    </div>
  );
};

export default PosicaoFinanceira;
