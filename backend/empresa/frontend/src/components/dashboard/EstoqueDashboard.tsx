import React, { useState, useEffect, useCallback } from 'react';
import Select from 'react-select';
import api from '../../services/api'; // Importando o serviço da API

// Função para formatar moeda
const formatCurrency = (value: number) => {
  const numValue = Number(value) || 0;
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(numValue);
};

// Função para formatar números
const formatNumber = (value: number) => {
  const numValue = Number(value) || 0;
  return new Intl.NumberFormat('pt-BR').format(numValue);
};

// Função para formatar data
const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleDateString('pt-BR');
  } catch {
    return '-';
  }
};

// Interfaces para os dados dos endpoints - Estrutura real dos dados
interface ProdutoEstoque {
  produto_id: number;
  nome: string;
  referencia: string;
  quantidade_inicial: number;
  quantidade_atual: number;
  variacao_quantidade: number;
  custo_unitario_inicial: number;
  valor_inicial: number;
  valor_atual: number;
  variacao_valor: number;
  total_movimentacoes: number;
  data_calculo: string;
  movimentacoes_recentes: unknown[];
}

interface EstoqueAtualData {
  results: ProdutoEstoque[];
  count: number;
  estatisticas?: { // Opcional para evitar quebras
    total_produtos: number;
    produtos_com_estoque: number;
    produtos_zerados: number;
    valor_total_inicial: number;
    valor_total_atual: number;
    variacao_total: number;
    data_calculo: string;
  };
}

interface ProdutoCritico {
  produto_id: number;
  nome: string;
  referencia: string;
  quantidade_inicial: number;
  quantidade_atual: number;
  valor_atual: number;
  total_movimentacoes: number;
}

interface EstoqueCriticoData {
  produtos: ProdutoCritico[];
  parametros: {
    data_consulta: string;
    limite_critico: number;
    total_produtos_criticos: number;
  };
}

interface ProdutoMovimentado {
  produto_id: number;
  nome: string;
  referencia: string;
  total_movimentacoes: number;
  ultima_movimentacao: string;
  tipos_movimentacao: string[];
}

interface ProdutosMaisMovimentadosData {
  produtos_mais_movimentados: ProdutoMovimentado[];
  parametros: {
    data_consulta: string;
    limite: number;
    total_produtos_analisados: number;
  };
}

// Interface para Movimentações do Período
interface MovimentacaoDetalhada {
  id: number;
  data: string;
  tipo: string;
  tipo_codigo: string;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
  documento: string;
  operador: string;
  observacoes: string;
  nota_fiscal?: {
    numero: string;
    tipo: string;
    fornecedor?: string | null;
    cliente?: string | null;
  };
  is_entrada: boolean;
  is_saida: boolean;
  valor_saida_preco_entrada?: number;
  diferenca_unitaria?: number;
}

interface ProdutoMovimentadoPeriodo {
  produto_id: number;
  nome: string;
  referencia: string;
  quantidade_entrada: number;
  quantidade_saida: number;
  valor_entrada: number;
  valor_saida: number;
  saldo_quantidade: number;
  saldo_valor: number;
  total_movimentacoes: number;
  primeira_movimentacao?: string;
  ultima_movimentacao?: string;
  ultimo_preco_entrada: number;
  data_ultimo_preco_entrada?: string;
  valor_saida_preco_entrada: number;
  diferenca_preco: number;
  tem_entrada_anterior: boolean;
  movimentacoes_detalhadas?: MovimentacaoDetalhada[];
}

interface MovimentacoesPeriodoData {
  produtos_movimentados: ProdutoMovimentadoPeriodo[];
  resumo: {
    periodo: string;
    total_produtos: number;
    total_movimentacoes: number;
    valor_total_entradas: number;
    valor_total_saidas: number;
    valor_total_saidas_preco_entrada: number;
    diferenca_total_precos: number;
    margem_total: number;
    saldo_periodo: number;
    quantidade_total_entradas: number;
    quantidade_total_saidas: number;
    produtos_com_entrada_anterior: number;
    produtos_sem_entrada_anterior: number;
  };
  parametros: {
    data_inicio: string;
    data_fim: string;
    incluir_detalhes: boolean;
    limite_aplicado: number | null;
    produto_id?: number;
  };
}

// Novas interfaces para o endpoint de estoque por grupo
interface EstoquePorGrupo {
  grupo_id: number;
  grupo_nome: string;
  valor_total_estoque: number;
  num_produtos?: number; // Tornando opcional caso o backend não envie
}

// Interface para a lista de grupos
// (removido interface Grupo não utilizada)

// Interface para as opções do react-select
interface GrupoOption {
  value: number;
  label: string;
}

// Interface para produtos resetados
interface ProdutoResetado {
  produto_id: number;
  codigo: string;
  nome: string;
  grupo_id: number | null;
  grupo_nome: string;
  data_reset: string;
  quantidade_reset: number;
  estoque_atual: number;
  preco_custo: number;
  valor_atual: number;
  ativo: boolean;
}

interface ProdutosResetadosData {
  success: boolean;
  data: ProdutoResetado[];
  meta: {
    total_registros: number;
    limite: number;
    offset: number;
    tem_proximo: boolean;
    tem_anterior: boolean;
  };
  estatisticas: {
    total_produtos_resetados: number;
    produtos_ativos: number;
    produtos_com_estoque: number;
    valor_total_estoque: number;
    data_limite: string;
    resets_por_mes: Record<string, number>;
  };
}

// (removido interface EstoquePorGrupoData não utilizada)

const EstoqueDashboard: React.FC = () => {
  const [estoqueAtual, setEstoqueAtual] = useState<EstoqueAtualData | null>(null);
  const [produtosCriticos, setProdutosCriticos] = useState<EstoqueCriticoData | null>(null);
  const [produtosMaisMovimentados, setProdutosMaisMovimentados] = useState<ProdutosMaisMovimentadosData | null>(null);
  const [valorTotalEstoque, setValorTotalEstoque] = useState<number>(0);
  const [estoquePorGrupo, setEstoquePorGrupo] = useState<EstoquePorGrupo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [dataSelecionada, setDataSelecionada] = useState(new Date().toISOString().split('T')[0]);
  const grupos: GrupoOption[] = [];
  const [gruposSelecionados, setGruposSelecionados] = useState<GrupoOption[]>([]);
  // (removido estado expandedGrupos não utilizado)
  const [selectedGrupos, setSelectedGrupos] = useState<Set<number>>(new Set());
  const [produtosPorGrupo, setProdutosPorGrupo] = useState<Record<number, ProdutoEstoque[]>>({});
  const [valorTotalSelecionado, setValorTotalSelecionado] = useState<number>(0);
  const [totalItens, setTotalItens] = useState<number>(0);
  const [grupoExpandidoId, setGrupoExpandidoId] = useState<number | null>(null);
  const [loadingGrupo, setLoadingGrupo] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState('geral');
  const [produtosResetados, setProdutosResetados] = useState<ProdutosResetadosData | null>(null);
  const [loadingResetados, setLoadingResetados] = useState<boolean>(false);
  const [movimentacoesPeriodoData, setMovimentacoesPeriodoData] = useState<MovimentacoesPeriodoData | null>(null);
  const [produtosExpandidos, setProdutosExpandidos] = useState<Set<number>>(new Set());
  const [loadingDetalhesProdutos, setLoadingDetalhesProdutos] = useState<Set<number>>(new Set());

  const toggleProdutoExpansaoMovimentacoes = async (produtoId: number) => {
    const newExpanded = new Set(produtosExpandidos);
    const willExpand = !newExpanded.has(produtoId);
    if (willExpand) {
      newExpanded.add(produtoId);
      setProdutosExpandidos(newExpanded);
      // Sempre carregar detalhes ao expandir para evitar cache vazio/stale
      const newLoading = new Set(loadingDetalhesProdutos);
      newLoading.add(produtoId);
      setLoadingDetalhesProdutos(newLoading);
      try {
        await carregarMovimentacoesPeriodo(true, produtoId);
      } finally {
        setLoadingDetalhesProdutos(prev => {
          const s = new Set(prev);
          s.delete(produtoId);
          return s;
        });
      }
    } else {
      newExpanded.delete(produtoId);
      setProdutosExpandidos(newExpanded);
    }
  };


  // (removido toggleGrupoExpansion não utilizado)

  const handleGrupoSelection = (grupoId: number) => {
    const newSelected = new Set(selectedGrupos);
    if (newSelected.has(grupoId)) {
      newSelected.delete(grupoId);
    } else {
      newSelected.add(grupoId);
    }
    setSelectedGrupos(newSelected);
  };

  // Efeito para calcular o total dos grupos selecionados
  useEffect(() => {
    if (estoquePorGrupo.length > 0 && selectedGrupos.size > 0) {
      const gruposSelecionadosData = estoquePorGrupo.filter(g => selectedGrupos.has(g.grupo_id));
      
      console.log('Grupos selecionados:', gruposSelecionadosData);
      
      const total = gruposSelecionadosData.reduce((acc, g) => {
        const valor = Number(g.valor_total_estoque) || 0;
        return acc + valor;
      }, 0);
      
      // Calcular total de produtos
      let totalProdutos = 0;
      
      // Primeiro, tentar usar num_produtos se disponível
      const totalFromNumProdutos = gruposSelecionadosData.reduce((acc, g) => {
        if (g.num_produtos !== undefined && g.num_produtos !== null && !isNaN(g.num_produtos)) {
          return acc + Number(g.num_produtos);
        }
        return acc;
      }, 0);
      
      if (totalFromNumProdutos > 0) {
        totalProdutos = totalFromNumProdutos;
      } else {
        // Fallback: contar produtos dos grupos expandidos
        totalProdutos = gruposSelecionadosData.reduce((acc, g) => {
          const produtosDoGrupo = produtosPorGrupo[g.grupo_id];
          if (produtosDoGrupo && Array.isArray(produtosDoGrupo)) {
            return acc + produtosDoGrupo.length;
          }
          // Se não temos dados dos produtos, assumir pelo menos 1 produto por grupo
          return acc + 1;
        }, 0);
      }
      
      console.log('Total calculado:', total, 'Total produtos:', totalProdutos);
      
      setValorTotalSelecionado(total);
      setTotalItens(totalProdutos);
    } else {
      setValorTotalSelecionado(0);
      setTotalItens(0);
    }
  }, [estoquePorGrupo, selectedGrupos, produtosPorGrupo]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {

      const grupoParams = new URLSearchParams();
      gruposSelecionados.forEach(g => grupoParams.append('grupo_id', g.value.toString()));
      const grupoQueryString = grupoParams.toString();

      const buildUrl = (base: string, params: Record<string, string | number | undefined>) => {
        const url = new URL(base, api.defaults.baseURL);
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined) {
            url.searchParams.append(key, String(value));
          }
        });
        if (grupoQueryString) {
            new URLSearchParams(grupoQueryString).forEach((value, key) => {
                url.searchParams.append(key, value);
            });
        }
        return url.pathname + url.search;
      };

      const [
        maisMovimentadosRes, 
        valorTotalRes, 
        estoqueGrupoRes, 
        estoqueTopRes, 
        estoqueCriticoRes
      ] = await Promise.all([
        api.get(buildUrl('/contas/estoque-controle/produtos_mais_movimentados/', { data: dataSelecionada })),
        api.get(buildUrl('/contas/estoque-controle/valor_total_estoque/', { data: dataSelecionada })),
        api.get(buildUrl('/contas/estoque-controle/valor_estoque_por_grupo/', { data: dataSelecionada })),
        api.get(buildUrl('/contas/estoque-controle/estoque_atual/', { ordering: '-valor_atual', limit: 10, data: dataSelecionada })),
        api.get(buildUrl('/contas/estoque-controle/produtos_criticos/', { data: dataSelecionada }))
      ]);

      setProdutosMaisMovimentados(maisMovimentadosRes.data);
      setValorTotalEstoque(valorTotalRes.data.valor_total_estoque);
      setEstoquePorGrupo(estoqueGrupoRes.data.estoque_por_grupo);
      setEstoqueAtual(estoqueTopRes.data);
      setProdutosCriticos(estoqueCriticoRes.data);

      // Debug: verificar estrutura dos dados
      console.log('Dados de estoque por grupo:', estoqueGrupoRes.data.estoque_por_grupo);

    } catch (err) {
      console.error('Erro ao carregar dados do estoque:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [dataSelecionada, gruposSelecionados]);

  // Função para carregar produtos resetados
  const carregarProdutosResetados = useCallback(async () => {
    setLoadingResetados(true);
    try {
      const response = await api.get('/contas/produtos-resetados/', {
        params: {
          meses: 12,
          limite: 50,
          offset: 0,
          ordem: 'data_reset',
          reverso: 'true'
        }
      });
      setProdutosResetados(response.data);
    } catch (err) {
      console.error('Erro ao carregar produtos resetados:', err);
      setError(err instanceof Error ? err.message : 'Erro ao carregar produtos resetados');
    } finally {
      setLoadingResetados(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const carregarProdutosDoGrupo = async (grupoId: number) => {
    if (produtosPorGrupo[grupoId]) {
      setGrupoExpandidoId(grupoExpandidoId === grupoId ? null : grupoId);
      return;
    }

    setLoadingGrupo(grupoId);
    try {
      const response = await api.get(`/contas/estoque-controle/estoque_atual/?grupo_id=${grupoId}&data=${dataSelecionada}`);
      setProdutosPorGrupo(prev => ({
        ...prev,
        [grupoId]: response.data.results || []
      }));
      setGrupoExpandidoId(grupoId);
    } catch (error) {
      console.error(`Falha ao carregar produtos para o grupo ${grupoId}`, error);
    } finally {
      setLoadingGrupo(null);
    }
  };

  const carregarMovimentacoesPeriodo = useCallback(async (incluirDetalhes: boolean = false, produtoId?: number) => {
    try {
      const dataFim = dataSelecionada || new Date().toISOString().split('T')[0];
      const dataInicio = new Date(dataFim);
      dataInicio.setDate(dataInicio.getDate() - 30);
      const dataInicioStr = dataInicio.toISOString().split('T')[0];

      const params = new URLSearchParams({
        data_inicio: dataInicioStr,
        data_fim: dataFim,
      });
      if (incluirDetalhes) {
        params.append('incluir_detalhes', 'true');
      }
      if (produtoId !== undefined) {
        params.append('produto_id', String(produtoId));
      }

      const response = await api.get(`/contas/estoque-controle/movimentacoes_periodo/?${params.toString()}`);
      const data = response.data as MovimentacoesPeriodoData;
      if (produtoId !== undefined) {
        // Merge detalhes do produto na lista existente (encontra pelo id)
        const detalhesProduto = data.produtos_movimentados?.find(p => p.produto_id === produtoId);
        if (detalhesProduto) {
          setMovimentacoesPeriodoData(prev => {
            if (!prev) return data;
            const atualizados = prev.produtos_movimentados.map(p =>
              p.produto_id === produtoId
                ? { ...p, movimentacoes_detalhadas: detalhesProduto.movimentacoes_detalhadas || [] }
                : p
            );
            return { ...prev, produtos_movimentados: atualizados };
          });
        } else {
          // Fallback: logar para debug e evitar estado sem merge
          console.warn('Detalhes do produto não encontrados no retorno da API.', {
            produtoId,
            idsRetornados: (data.produtos_movimentados || []).map(p => p.produto_id)
          });
          // Opcionalmente, se por algum motivo o produto não estiver na lista anterior,
          // podemos adicioná-lo para exibir os detalhes retornados (se existir apenas 1 no payload)
          if (data.produtos_movimentados && data.produtos_movimentados.length === 1) {
            const unico = data.produtos_movimentados[0];
            setMovimentacoesPeriodoData(prev => {
              if (!prev) return data;
              const jaExiste = prev.produtos_movimentados.some(p => p.produto_id === unico.produto_id);
              return {
                ...prev,
                produtos_movimentados: jaExiste
                  ? prev.produtos_movimentados
                  : [...prev.produtos_movimentados, unico]
              };
            });
          }
        }
      } else {
        // Merge seguro: preserva detalhes já carregados para não perder após resposta do resumo
        setMovimentacoesPeriodoData(prev => {
          if (!prev) return data;
          const prevMap = new Map(prev.produtos_movimentados.map(p => [p.produto_id, p]));
          const merged = data.produtos_movimentados.map(novo => {
            const antigo = prevMap.get(novo.produto_id);
            if (antigo && antigo.movimentacoes_detalhadas && antigo.movimentacoes_detalhadas.length > 0) {
              return { ...novo, movimentacoes_detalhadas: antigo.movimentacoes_detalhadas };
            }
            return novo;
          });
          return { ...data, produtos_movimentados: merged };
        });
      }
    } catch (err) {
      console.error('Erro ao carregar movimentações do período:', err);
      setError('Erro ao carregar movimentações do período');
    }
  }, [dataSelecionada]);

  useEffect(() => {
    if (activeTab === 'movimentacoes-periodo') {
      // Carrega resumo sem detalhes inicialmente; detalhes serão carregados sob demanda ao expandir
      carregarMovimentacoesPeriodo(false);
    } else if (activeTab === 'resetados') {
      carregarProdutosResetados();
    }
  }, [activeTab, dataSelecionada, carregarMovimentacoesPeriodo, carregarProdutosResetados]);

  const recarregarDados = () => {
    loadData();
  };

  const tabs = [
    { id: 'geral', label: 'Estoque por Grupo', icon: '�' },
    { id: 'top-produtos', label: 'Top Produtos', icon: '💎' },
    { id: 'criticos', label: 'Produtos Críticos', icon: '⚠️' },
    { id: 'movimentados', label: 'Mais Movimentados', icon: '🔄' },
    { id: 'movimentacoes-periodo', label: 'Movimentações Período', icon: '📅' },
    { id: 'resetados', label: 'Produtos Resetados', icon: '�' },
  ];

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px',
        backgroundColor: '#f9fafb',
        borderRadius: '8px',
        fontSize: '1.1rem',
        color: '#6b7280'
      }}>
        🔄 Carregando dados do estoque...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '24px', 
        textAlign: 'center',
        backgroundColor: '#fef2f2',
        border: '1px solid #fecaca',
        borderRadius: '8px',
        color: '#b91c1c'
      }}>
        <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⚠️</div>
        <div style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '8px' }}>
          Erro ao carregar dados
        </div>
        <div style={{ fontSize: '0.875rem' }}>{error}</div>
        <button 
          onClick={recarregarDados}
          style={{
            marginTop: '16px',
            padding: '8px 16px',
            backgroundColor: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ 
          fontSize: '2rem', 
          fontWeight: '700', 
          color: '#111827', 
          margin: '0 0 8px 0' 
        }}>
          📦 Dashboard de Controle de Estoque
        </h1>
        <p style={{ 
          fontSize: '1rem', 
          color: '#6b7280', 
          margin: 0 
        }}>
          Análise completa do estoque, produtos críticos e movimentações
        </p>
      </div>

      {/* Filtro de Data e Informações */}
      <div style={{ 
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        flexWrap: 'wrap',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ 
              fontSize: '0.875rem', 
              fontWeight: '600', 
              color: '#374151' 
            }}>
              📅 Consultar estoque na data:
            </label>
            <input
              type="date"
              value={dataSelecionada}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDataSelecionada(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '0.875rem'
              }}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '300px', zIndex: 10 }}>
            <label style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151' }}>
              Grupos:
            </label>
            <Select
              isMulti
              options={grupos}
              value={gruposSelecionados}
              onChange={(options) => setGruposSelecionados(options as GrupoOption[])}
              placeholder="Selecione os grupos..."
              styles={{
                container: (base) => ({ ...base, flex: 1 }),
                control: (base) => ({ ...base, borderColor: '#d1d5db' }),
              }}
            />
          </div>
        </div>
        <button 
          onClick={recarregarDados}
          style={{
            padding: '8px 16px',
            backgroundColor: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600'
          }}
        >
          Atualizar
        </button>
      </div>

      {/* Cards de Resumo */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: '16px', 
        marginBottom: '24px' 
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '16px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '4px' }}>💰 Valor Total do Estoque</div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{formatCurrency(valorTotalEstoque)}</div>
        </div>
        <div style={{
          backgroundColor: 'white',
          padding: '16px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '4px' }}>📦 Total de Itens</div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{totalItens > 0 ? formatNumber(totalItens) : '0'}</div>
        </div>
        <div style={{
          backgroundColor: 'white',
          padding: '16px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '4px' }}>💵 Total Grupos Selecionados</div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{valorTotalSelecionado > 0 ? formatCurrency(valorTotalSelecionado) : 'R$ 0,00'}</div>
        </div>
      </div>

      {/* Abas de Navegação */}
      <div style={{ marginBottom: '24px', borderBottom: '1px solid #d1d5db', display: 'flex' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '12px 20px',
              border: 'none',
              borderBottom: activeTab === tab.id ? '3px solid #10b981' : '3px solid transparent',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontWeight: activeTab === tab.id ? '600' : '500',
              color: activeTab === tab.id ? '#10b981' : '#6b7280',
              fontSize: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Conteúdo das Abas */}
      <div>
        {activeTab === 'geral' && estoquePorGrupo && (
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>Estoque por Grupo</h2>
            
            {/* Resumo dos grupos selecionados */}
            {selectedGrupos.size > 0 && (
              <div style={{ 
                backgroundColor: '#f0f9ff', 
                padding: '12px', 
                borderRadius: '6px', 
                marginBottom: '16px',
                border: '1px solid #0ea5e9'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#0c4a6e', marginBottom: '4px' }}>
                  📊 {selectedGrupos.size} grupo(s) selecionado(s)
                </div>
                <div style={{ fontSize: '1.1rem', fontWeight: '600', color: '#0c4a6e' }}>
                  Total: {formatCurrency(valorTotalSelecionado)} | Produtos: {totalItens > 0 ? formatNumber(totalItens) : '0'}
                </div>
              </div>
            )}
            
            {/* Tabela de grupos */}
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#374151' }}>
                    <input 
                      type="checkbox" 
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedGrupos(new Set(estoquePorGrupo.map(g => g.grupo_id)));
                        } else {
                          setSelectedGrupos(new Set());
                        }
                      }}
                      checked={selectedGrupos.size === estoquePorGrupo.length && estoquePorGrupo.length > 0}
                      style={{ marginRight: '8px' }}
                    />
                    Grupo
                  </th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#374151' }}>Valor em Estoque</th>
                </tr>
              </thead>
              <tbody>
                {estoquePorGrupo.map(grupo => (
                  <React.Fragment key={grupo.grupo_id}>
                    <tr style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input
                          type="checkbox"
                          checked={selectedGrupos.has(grupo.grupo_id)}
                          onChange={() => handleGrupoSelection(grupo.grupo_id)}
                          onClick={(e) => e.stopPropagation()}
                        />
                        <span
                          onClick={() => carregarProdutosDoGrupo(grupo.grupo_id)}
                          style={{ 
                            cursor: 'pointer', 
                            fontSize: '14px', 
                            color: '#6b7280',
                            marginRight: '4px'
                          }}
                        >
                          {grupoExpandidoId === grupo.grupo_id ? '▼' : '►'}
                        </span>
                        <span 
                          onClick={() => carregarProdutosDoGrupo(grupo.grupo_id)}
                          style={{ cursor: 'pointer' }}
                        >
                          {grupo.grupo_nome}
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontWeight: '500' }}>{formatCurrency(grupo.valor_total_estoque)}</td>
                    </tr>
                    {grupoExpandidoId === grupo.grupo_id && (
                      <tr>
                        <td colSpan={2} style={{ padding: '16px', backgroundColor: '#f9fafb' }}>
                          {loadingGrupo === grupo.grupo_id ? <p>Carregando produtos...</p> : (
                            <table style={{ width: '100%' }}>
                              <thead>
                                <tr>
                                  <th>Produto</th>
                                  <th style={{ textAlign: 'right' }}>Quantidade</th>
                                  <th style={{ textAlign: 'right' }}>Valor</th>
                                </tr>
                              </thead>
                              <tbody>
                                {produtosPorGrupo[grupo.grupo_id]?.map(p => (
                                  <tr key={p.produto_id}>
                                    <td>{p.nome}</td>
                                    <td style={{ textAlign: 'right' }}>{formatNumber(p.quantidade_atual)}</td>
                                    <td style={{ textAlign: 'right' }}>{formatCurrency(p.valor_atual)}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          )}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'top-produtos' && estoqueAtual && (
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>Top 10 Produtos por Valor</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Produto</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Quantidade</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Valor em Estoque</th>
                </tr>
              </thead>
              <tbody>
                {estoqueAtual.results.map(p => (
                  <tr key={p.produto_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '12px' }}>{p.nome}</td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>{formatNumber(p.quantidade_atual)}</td>
                    <td style={{ padding: '12px', textAlign: 'right', fontWeight: '500' }}>{formatCurrency(p.valor_atual)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'criticos' && produtosCriticos && (
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>Produtos com Estoque Crítico</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Produto</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Quantidade</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Valor</th>
                </tr>
              </thead>
              <tbody>
                {produtosCriticos.produtos.map(p => (
                  <tr key={p.produto_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '12px' }}>{p.nome}</td>
                    <td style={{ padding: '12px', textAlign: 'right', color: '#ef4444' }}>{formatNumber(p.quantidade_atual)}</td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>{formatCurrency(p.valor_atual)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'movimentados' && produtosMaisMovimentados && (
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>Produtos Mais Movimentados (Últimos 30 dias)</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Produto</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Total de Movimentações</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Última Movimentação</th>
                </tr>
              </thead>
              <tbody>
                {produtosMaisMovimentados.produtos_mais_movimentados.map(p => (
                  <tr key={p.produto_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '12px' }}>{p.nome}</td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>{formatNumber(p.total_movimentacoes)}</td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>{formatDate(p.ultima_movimentacao)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'movimentacoes-periodo' && movimentacoesPeriodoData && (
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>Movimentações no Período</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Produto</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Entradas</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Saídas</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Saldo</th>
                </tr>
              </thead>
              <tbody>
                {movimentacoesPeriodoData.produtos_movimentados.map(p => (
                  <React.Fragment key={p.produto_id}>
                    <tr onClick={() => toggleProdutoExpansaoMovimentacoes(p.produto_id)} style={{ cursor: 'pointer' }}>
                      <td style={{ padding: '12px' }}>{p.nome}</td>
                      <td style={{ padding: '12px', textAlign: 'right', color: 'green' }}>{formatCurrency(p.valor_entrada)}</td>
                      <td style={{ padding: '12px', textAlign: 'right', color: 'red' }}>{formatCurrency(p.valor_saida)}</td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>{formatCurrency(p.saldo_valor)}</td>
                    </tr>
                    {produtosExpandidos.has(p.produto_id) && (
                      <tr>
                        <td colSpan={4} style={{ padding: '16px', backgroundColor: '#f9fafb' }}>
                          {loadingDetalhesProdutos.has(p.produto_id) ? (
                            <div style={{ color: '#6b7280' }}>Carregando detalhes...</div>
                          ) : p.movimentacoes_detalhadas && p.movimentacoes_detalhadas.length > 0 ? (
                            <table style={{ width: '100%' }}>
                              <thead>
                                <tr>
                                  <th>Data</th>
                                  <th>Tipo</th>
                                  <th>Nota Fiscal</th>
                                  <th>Cliente/Fornecedor</th>
                                  <th style={{ textAlign: 'right' }}>Qtd</th>
                                  <th style={{ textAlign: 'right' }}>Valor Unit.</th>
                                  <th style={{ textAlign: 'right' }}>Valor Total</th>
                                </tr>
                              </thead>
                              <tbody>
                                {p.movimentacoes_detalhadas.map(m => (
                                  <tr key={m.id}>
                                    <td>{formatDate(m.data)}</td>
                                    <td>{m.tipo}</td>
                                    <td>{m.nota_fiscal?.numero || m.documento || '-'}</td>
                                    <td>
                                      {m.nota_fiscal?.tipo === 'entrada' && (m.nota_fiscal?.fornecedor || '-')}
                                      {m.nota_fiscal?.tipo === 'saida' && (m.nota_fiscal?.cliente || '-')}
                                      {!m.nota_fiscal?.tipo && '-'}
                                    </td>
                                    <td style={{ textAlign: 'right' }}>{formatNumber(m.quantidade)}</td>
                                    <td style={{ textAlign: 'right' }}>{formatCurrency(m.valor_unitario)}</td>
                                    <td style={{ textAlign: 'right' }}>{formatCurrency(m.valor_total)}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          ) : (
                            <div style={{ color: '#6b7280' }}>Sem movimentações detalhadas no período.</div>
                          )}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'resetados' && (
          <div>
            {loadingResetados ? <p>Carregando produtos resetados...</p> : (
              produtosResetados && (
                <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '16px' }}>Produtos com Reset de Estoque (Último Ano)</h2>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                        <th style={{ padding: '12px', textAlign: 'left' }}>Produto</th>
                        <th style={{ padding: '12px', textAlign: 'left' }}>Grupo</th>
                        <th style={{ padding: '12px', textAlign: 'right' }}>Data do Reset</th>
                        <th style={{ padding: '12px', textAlign: 'right' }}>Qtd. Reset</th>
                        <th style={{ padding: '12px', textAlign: 'right' }}>Estoque Atual</th>
                      </tr>
                    </thead>
                    <tbody>
                      {produtosResetados.data.map(p => (
                        <tr key={p.produto_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                          <td style={{ padding: '12px' }}>{p.nome}</td>
                          <td style={{ padding: '12px' }}>{p.grupo_nome}</td>
                          <td style={{ padding: '12px', textAlign: 'right' }}>{formatDate(p.data_reset)}</td>
                          <td style={{ padding: '12px', textAlign: 'right' }}>{formatNumber(p.quantidade_reset)}</td>
                          <td style={{ padding: '12px', textAlign: 'right' }}>{formatNumber(p.estoque_atual)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EstoqueDashboard;