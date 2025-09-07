import React, { useState, useEffect, useCallback } from 'react';

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
  estoque: ProdutoEstoque[];
  estatisticas: {
    total_produtos: number;
    produtos_com_estoque: number;
    produtos_zerados: number;
    valor_total_inicial: number;
    valor_total_atual: number;
    variacao_total: number;
    data_calculo: string;
  };
  parametros: {
    data_consulta: string;
    produto_id: number | null;
    total_registros: number;
    limite_aplicado: number;
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
    fornecedor?: string;
    cliente?: string;
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
  // ✨ NOVOS CAMPOS DO BACKEND
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
    // ✨ NOVOS CAMPOS DO RESUMO
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

const EstoqueDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('geral');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados para os diferentes endpoints
  const [estoqueGeralData, setEstoqueGeralData] = useState<EstoqueAtualData | null>(null);
  const [estoqueTopData, setEstoqueTopData] = useState<EstoqueAtualData | null>(null);
  const [estoqueCriticoData, setEstoqueCriticoData] = useState<EstoqueCriticoData | null>(null);
  const [produtosMovimentadosData, setProdutosMovimentadosData] = useState<ProdutosMaisMovimentadosData | null>(null);
  const [produtoEspecificoId, setProdutoEspecificoId] = useState<string>('10');
  const [produtoEspecificoData, setProdutoEspecificoData] = useState<EstoqueAtualData | null>(null);
  const [movimentacoesPeriodoData, setMovimentacoesPeriodoData] = useState<MovimentacoesPeriodoData | null>(null);
  
  // Estado para controlar produtos expandidos na tabela de movimentações
  const [produtosExpandidos, setProdutosExpandidos] = useState<Set<number>>(new Set());
  
  // Estado para a data selecionada
  const [dataSelecionada, setDataSelecionada] = useState<string>(
    new Date().toISOString().split('T')[0] // Data atual no formato YYYY-MM-DD
  );

  // Estados para paginação
  const [paginaAtual, setPaginaAtual] = useState<number>(1);
  const [itensPorPagina, setItensPorPagina] = useState<number>(50);
  const [totalItens, setTotalItens] = useState<number>(0);
  const [valorTotalEstoque, setValorTotalEstoque] = useState<number>(0);
  const [todosOsProdutos, setTodosOsProdutos] = useState<ProdutoEstoque[]>([]);  // Cache de todos os produtos

  // Função para formatar valores monetários
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  // Função para formatar números com verificação de segurança
  const formatNumber = (value: number | undefined | null): string => {
    if (value === undefined || value === null || isNaN(value) || typeof value !== 'number') {
      return '0';
    }
    try {
      return value.toLocaleString('pt-BR');
    } catch {
      return '0';
    }
  };

  // Função para formatar data
  const formatDate = (dateString: string): string => {
    if (!dateString || typeof dateString !== 'string') return 'N/A';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'N/A';
      return date.toLocaleDateString('pt-BR');
    } catch {
      return 'N/A';
    }
  };

  // Função para alternar a expansão de um produto
  const toggleProdutoExpansao = async (produtoId: number) => {
    const jaExpandido = produtosExpandidos.has(produtoId);
    
    setProdutosExpandidos(prev => {
      const novoSet = new Set(prev);
      if (novoSet.has(produtoId)) {
        novoSet.delete(produtoId);
      } else {
        novoSet.add(produtoId);
      }
      return novoSet;
    });

    // Se está expandindo e ainda não carregou os detalhes, carregar dados com detalhes
    if (!jaExpandido && movimentacoesPeriodoData && !movimentacoesPeriodoData.parametros.incluir_detalhes) {
      await carregarMovimentacoesPeriodoComDetalhes();
    }
  };

  // Função para carregar dados dos endpoints
  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const dataQuery = dataSelecionada ? `&data=${dataSelecionada}` : '';
      const offset = (paginaAtual - 1) * itensPorPagina;

      const [
        estoqueGeralResponse,
        estoqueTopResponse,
        estoqueCriticoResponse,
        produtosMovimentadosResponse
      ] = await Promise.all([
        fetch(`http://127.0.0.1:8000/api/estoque-controle/estoque_atual/?limite=${itensPorPagina}&offset=${offset}${dataQuery}`),
        fetch(`http://127.0.0.1:8000/api/estoque-controle/estoque_atual/?limite=100&ordem=valor_atual&reverso=true${dataQuery}`),
        fetch(`http://127.0.0.1:8000/api/estoque-controle/estoque_critico/?limite=10${dataQuery}`),
        fetch(`http://127.0.0.1:8000/api/estoque-controle/produtos_mais_movimentados/?limite=10${dataQuery}`)
      ]);

      const estoqueGeral = await estoqueGeralResponse.json();
      const estoqueTop = await estoqueTopResponse.json();
      const estoqueCritico = await estoqueCriticoResponse.json();
      const produtosMovimentados = await produtosMovimentadosResponse.json();

      setEstoqueGeralData(estoqueGeral);
      setEstoqueTopData(estoqueTop);
      setEstoqueCriticoData(estoqueCritico);
      setProdutosMovimentadosData(produtosMovimentados);

      // Extrair informações de paginação e valor total
      if (estoqueGeral?.parametros) {
        setTotalItens(estoqueGeral.parametros.total_registros || 0);
      }
      
      // Calcular valor total do estoque das estatísticas
      if (estoqueGeral?.estatisticas) {
        setValorTotalEstoque(estoqueGeral.estatisticas.valor_total_atual || 0);
      }
    } catch (err) {
      console.error('Erro ao carregar dados do estoque:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  // Função para buscar produto específico
  const buscarProdutoEspecifico = async () => {
    if (!produtoEspecificoId) return;
    
    try {
      const dataQuery = dataSelecionada ? `&data=${dataSelecionada}` : '';
      const response = await fetch(`http://127.0.0.1:8000/api/estoque-controle/estoque_atual/?produto_id=${produtoEspecificoId}${dataQuery}`);
      const data = await response.json();
      setProdutoEspecificoData(data);
    } catch (err) {
      console.error('Erro ao buscar produto específico:', err);
      setError('Erro ao buscar produto específico');
    }
  };

  // Função para carregar movimentações do período
  const carregarMovimentacoesPeriodo = useCallback(async (incluirDetalhes: boolean = false) => {
    try {
      // Calcular data de início (30 dias atrás da data selecionada)
      const dataFim = dataSelecionada || new Date().toISOString().split('T')[0];
      const dataInicio = new Date(dataFim);
      dataInicio.setDate(dataInicio.getDate() - 30);
      const dataInicioStr = dataInicio.toISOString().split('T')[0];

      const parametrosDetalhes = incluirDetalhes ? '&incluir_detalhes=true' : '';
      const response = await fetch(`http://127.0.0.1:8000/api/estoque-controle/movimentacoes_periodo/?data_inicio=${dataInicioStr}&data_fim=${dataFim}${parametrosDetalhes}`);
      const data = await response.json();
      setMovimentacoesPeriodoData(data);
    } catch (err) {
      console.error('Erro ao carregar movimentações do período:', err);
      setError('Erro ao carregar movimentações do período');
    }
  }, [dataSelecionada]);

  // Função auxiliar para carregar com detalhes
  const carregarMovimentacoesPeriodoComDetalhes = () => carregarMovimentacoesPeriodo(true);

  // Efeito para fazer paginação no frontend usando todos os produtos carregados
  useEffect(() => {
    if (todosOsProdutos.length > 0) {
      const inicio = (paginaAtual - 1) * itensPorPagina;
      const fim = inicio + itensPorPagina;
      const produtosPaginados = todosOsProdutos.slice(inicio, fim);
      
      console.log(`📄 Paginação: página ${paginaAtual}, mostrando ${produtosPaginados.length} de ${todosOsProdutos.length} produtos`);
      console.log(`🔢 Intervalo: ${inicio + 1} - ${fim > todosOsProdutos.length ? todosOsProdutos.length : fim}`);
      
      // Criar objeto compatível com o formato esperado
      const dadosEstoqueGeral: EstoqueAtualData = {
        estoque: produtosPaginados,
        estatisticas: {
          total_produtos: todosOsProdutos.length,
          produtos_com_estoque: todosOsProdutos.filter(p => p.quantidade_atual > 0).length,
          produtos_zerados: todosOsProdutos.filter(p => p.quantidade_atual === 0).length,
          valor_total_inicial: valorTotalEstoque, // Usando valor atual como inicial
          valor_total_atual: valorTotalEstoque,
          variacao_total: 0, // Sem dados de variação no frontend
          data_calculo: new Date().toISOString()
        },
        parametros: {
          data_consulta: dataSelecionada || new Date().toISOString().split('T')[0],
          produto_id: null,
          total_registros: todosOsProdutos.length,
          limite_aplicado: itensPorPagina
        }
      };
      
      setEstoqueGeralData(dadosEstoqueGeral);
    }
  }, [todosOsProdutos, paginaAtual, itensPorPagina, valorTotalEstoque, dataSelecionada]);

  useEffect(() => {
    console.log('🚀 useEffect EstoqueDashboard executado!');
    console.log('📅 Data selecionada atual:', dataSelecionada);
    console.log('🔄 Recarregando dados do estoque devido à mudança de data...');
    
    const carregarDados = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('� Fazendo requisição simples para testar...');
        
        // Teste simples primeiro
        const response = await fetch(`http://127.0.0.1:8000/api/estoque-controle/estoque_atual/${dataSelecionada ? `?data=${dataSelecionada}` : ''}`);
        const dados = await response.json();
        
        console.log('✅ Resposta recebida:', dados);
        console.log('📊 Total produtos na base:', dados?.parametros?.total_registros);
        
        if (dados?.estoque) {
          setTodosOsProdutos(dados.estoque);
          setTotalItens(dados.parametros?.total_registros || dados.estoque.length);
          setValorTotalEstoque(dados.estatisticas?.valor_total_atual || 0);
          
          console.log(`🎯 Produtos carregados: ${dados.estoque.length} de ${dados.parametros?.total_registros || 0} total`);
        }

        // Carregar outros dados também com filtro de data
        const dataQueryParam = dataSelecionada ? `&data=${dataSelecionada}` : '';
        const [
          estoqueTopResponse,
          estoqueCriticoResponse,
          produtosMovimentadosResponse
        ] = await Promise.all([
          fetch(`http://127.0.0.1:8000/api/estoque-controle/estoque_atual/?limite=100&ordem=valor_atual&reverso=true${dataQueryParam}`),
          fetch(`http://127.0.0.1:8000/api/estoque-controle/estoque_critico/?limite=10${dataQueryParam}`),
          fetch(`http://127.0.0.1:8000/api/estoque-controle/produtos_mais_movimentados/?limite=10${dataQueryParam}`)
        ]);

        const estoqueTop = await estoqueTopResponse.json();
        const estoqueCritico = await estoqueCriticoResponse.json();
        const produtosMovimentados = await produtosMovimentadosResponse.json();

        setEstoqueTopData(estoqueTop);
        setEstoqueCriticoData(estoqueCritico);
        setProdutosMovimentadosData(produtosMovimentados);

      } catch (err) {
        console.error('Erro ao carregar dados do estoque:', err);
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };
    
    carregarDados();
  }, [dataSelecionada]); // Removemos paginaAtual e itensPorPagina pois agora fazemos paginação no frontend

  // useEffect para carregar movimentações do período quando a aba for selecionada
  useEffect(() => {
    if (activeTab === 'movimentacoes-periodo') {
      carregarMovimentacoesPeriodo();
    }
  }, [activeTab, dataSelecionada, carregarMovimentacoesPeriodo]);

  // Função para recarregar dados manualmente
  const recarregarDados = () => {
    loadData();
  };

  // Funções de paginação
  const totalPaginas = Math.ceil(totalItens / itensPorPagina);
  
  const irParaPagina = (numeroPagina: number) => {
    if (numeroPagina >= 1 && numeroPagina <= totalPaginas) {
      setPaginaAtual(numeroPagina);
    }
  };

  const proximaPagina = () => {
    if (paginaAtual < totalPaginas) {
      setPaginaAtual(paginaAtual + 1);
    }
  };

  const paginaAnterior = () => {
    if (paginaAtual > 1) {
      setPaginaAtual(paginaAtual - 1);
    }
  };

  const tabs = [
    { id: 'geral', label: '📦 Estoque Geral', icon: '📦' },
    { id: 'top-produtos', label: '💎 Top Produtos', icon: '💎' },
    { id: 'criticos', label: '⚠️ Produtos Críticos', icon: '⚠️' },
    { id: 'movimentados', label: '🔄 Mais Movimentados', icon: '🔄' },
    { id: 'movimentacoes-periodo', label: '📅 Movimentações Período', icon: '📅' },
    { id: 'especifico', label: '🔍 Produto Específico', icon: '🔍' }
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
              onChange={(e) => setDataSelecionada(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '0.875rem',
                color: '#374151',
                backgroundColor: 'white',
                outline: 'none'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#2563eb';
                e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#d1d5db';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>
          <button
            onClick={recarregarDados}
            style={{
              padding: '8px 16px',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#1d4ed8';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = '#2563eb';
            }}
          >
            🔄 Atualizar Dados
          </button>
          {loading && (
            <div style={{ 
              fontSize: '0.875rem', 
              color: '#6b7280',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              ⏳ Carregando...
            </div>
          )}
        </div>
        
        {/* Informações do Estoque */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flexWrap: 'wrap' }}>
          <div style={{ 
            backgroundColor: '#dcfce7', 
            border: '1px solid #bbf7d0', 
            borderRadius: '6px', 
            padding: '8px 12px' 
          }}>
            <div style={{ fontSize: '0.75rem', color: '#166534', fontWeight: '500' }}>💰 Valor Total do Estoque</div>
            <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#166534' }}>
              {formatCurrency(valorTotalEstoque)}
            </div>
          </div>
          <div style={{ 
            backgroundColor: '#dbeafe', 
            border: '1px solid #bfdbfe', 
            borderRadius: '6px', 
            padding: '8px 12px' 
          }}>
            <div style={{ fontSize: '0.75rem', color: '#1e40af', fontWeight: '500' }}>📦 Total de Produtos</div>
            <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#1e40af' }}>
              {formatNumber(totalItens)}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ 
        display: 'flex', 
        gap: '8px', 
        marginBottom: '24px',
        flexWrap: 'wrap'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '12px 16px',
              backgroundColor: activeTab === tab.id ? '#2563eb' : 'white',
              color: activeTab === tab.id ? 'white' : '#374151',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        
        {/* Estoque Geral Tab */}
        {activeTab === 'geral' && estoqueGeralData && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              📦 Estoque Geral - Página {paginaAtual} de {totalPaginas}
            </h2>
            
            {/* Controles de Paginação - Topo */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: '24px',
              padding: '16px',
              backgroundColor: '#f8fafc',
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <label style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  📄 Itens por página:
                </label>
                <select 
                  value={itensPorPagina} 
                  onChange={(e) => {
                    setItensPorPagina(Number(e.target.value));
                    setPaginaAtual(1);
                  }}
                  style={{
                    padding: '6px 10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    backgroundColor: 'white'
                  }}
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={200}>200</option>
                </select>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  onClick={paginaAnterior}
                  disabled={paginaAtual <= 1}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: paginaAtual <= 1 ? '#f3f4f6' : '#2563eb',
                    color: paginaAtual <= 1 ? '#9ca3af' : 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    cursor: paginaAtual <= 1 ? 'not-allowed' : 'pointer'
                  }}
                >
                  ← Anterior
                </button>
                
                <span style={{ 
                  fontSize: '0.875rem', 
                  color: '#374151',
                  padding: '0 12px',
                  fontWeight: '500'
                }}>
                  {paginaAtual} de {totalPaginas}
                </span>
                
                <button
                  onClick={proximaPagina}
                  disabled={paginaAtual >= totalPaginas}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: paginaAtual >= totalPaginas ? '#f3f4f6' : '#2563eb',
                    color: paginaAtual >= totalPaginas ? '#9ca3af' : 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    cursor: paginaAtual >= totalPaginas ? 'not-allowed' : 'pointer'
                  }}
                >
                  Próxima →
                </button>
              </div>
            </div>
            
            {/* Resumo */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '16px',
              marginBottom: '24px'
            }}>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#eff6ff', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#2563eb', fontWeight: '500' }}>
                  📊 Total de Produtos
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#1d4ed8', marginTop: '4px' }}>
                  {formatNumber(estoqueGeralData?.estatisticas?.total_produtos)}
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#166534', fontWeight: '500' }}>
                  💰 Valor Total do Estoque
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#15803d', marginTop: '4px' }}>
                  {formatCurrency(estoqueGeralData?.estatisticas?.valor_total_atual || 0)}
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fefce8', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.875rem', color: '#ca8a04', fontWeight: '500' }}>
                  📅 Data da Consulta
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#a16207', marginTop: '4px' }}>
                  {formatDate(estoqueGeralData?.parametros?.data_consulta || '')}
                </div>
              </div>
            </div>

            {/* Tabela de produtos */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: '#f9fafb' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>ID</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Produto</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Quantidade</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Valor Unit.</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Valor Total</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Última Mov.</th>
                  </tr>
                </thead>
                <tbody>
                  {(estoqueGeralData?.estoque || []).map((produto, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                        {produto?.produto_id || 'N/A'}
                      </td>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                        <div>{produto?.nome || 'N/A'}</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{produto?.referencia || ''}</div>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: '#374151' }}>
                        {formatNumber(produto?.quantidade_atual)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#374151' }}>
                        {formatCurrency(produto?.custo_unitario_inicial || 0)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: '#059669' }}>
                        {formatCurrency(produto?.valor_atual || 0)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', color: '#6b7280' }}>
                        <div>{formatDate(produto?.data_calculo || '')}</div>
                        <div style={{ color: '#9ca3af', fontSize: '0.7rem' }}>
                          {formatNumber(produto?.total_movimentacoes)} movs
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Controles de Paginação - Rodapé */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginTop: '24px',
              padding: '16px',
              backgroundColor: '#f8fafc',
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                Mostrando {Math.min((paginaAtual - 1) * itensPorPagina + 1, totalItens)} até {Math.min(paginaAtual * itensPorPagina, totalItens)} de {formatNumber(totalItens)} produtos
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  onClick={() => irParaPagina(1)}
                  disabled={paginaAtual <= 1}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: paginaAtual <= 1 ? '#f3f4f6' : '#6b7280',
                    color: paginaAtual <= 1 ? '#9ca3af' : 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    cursor: paginaAtual <= 1 ? 'not-allowed' : 'pointer'
                  }}
                >
                  ⏮ Primeira
                </button>
                
                <button
                  onClick={paginaAnterior}
                  disabled={paginaAtual <= 1}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: paginaAtual <= 1 ? '#f3f4f6' : '#2563eb',
                    color: paginaAtual <= 1 ? '#9ca3af' : 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    cursor: paginaAtual <= 1 ? 'not-allowed' : 'pointer'
                  }}
                >
                  ← Anterior
                </button>
                
                <span style={{ 
                  fontSize: '0.875rem', 
                  color: '#374151',
                  padding: '0 12px',
                  fontWeight: '500'
                }}>
                  Página {paginaAtual} de {totalPaginas}
                </span>
                
                <button
                  onClick={proximaPagina}
                  disabled={paginaAtual >= totalPaginas}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: paginaAtual >= totalPaginas ? '#f3f4f6' : '#2563eb',
                    color: paginaAtual >= totalPaginas ? '#9ca3af' : 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    cursor: paginaAtual >= totalPaginas ? 'not-allowed' : 'pointer'
                  }}
                >
                  Próxima →
                </button>
                
                <button
                  onClick={() => irParaPagina(totalPaginas)}
                  disabled={paginaAtual >= totalPaginas}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: paginaAtual >= totalPaginas ? '#f3f4f6' : '#6b7280',
                    color: paginaAtual >= totalPaginas ? '#9ca3af' : 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    cursor: paginaAtual >= totalPaginas ? 'not-allowed' : 'pointer'
                  }}
                >
                  Última ⏭
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Top Produtos Tab */}
        {activeTab === 'top-produtos' && estoqueTopData && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              💎 Top 100 Produtos por Valor
            </h2>
            
            {/* Similar structure as above but for top products */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: '#f9fafb' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Ranking</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Produto</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Quantidade</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Valor Total</th>
                  </tr>
                </thead>
                <tbody>
                  {(estoqueTopData?.estoque || []).slice(0, 20).map((produto, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px', fontSize: '0.875rem', fontWeight: '600', color: '#2563eb' }}>
                        #{index + 1}
                      </td>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                        {produto?.nome || 'N/A'}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#374151' }}>
                        {formatNumber(produto?.quantidade_atual)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: '#059669' }}>
                        {formatCurrency(produto?.valor_atual || 0)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Produtos Críticos Tab */}
        {activeTab === 'criticos' && estoqueCriticoData && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              ⚠️ Produtos com Estoque Crítico
            </h2>
            
            {/* Alertas */}
            <div style={{ 
              backgroundColor: '#fef2f2', 
              border: '1px solid #fecaca', 
              borderRadius: '8px', 
              padding: '16px', 
              marginBottom: '24px' 
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '1.5rem' }}>⚠️</span>
                <div>
                  <div style={{ fontSize: '1rem', fontWeight: '600', color: '#dc2626' }}>
                    {formatNumber(estoqueCriticoData?.parametros?.total_produtos_criticos)} produtos com estoque crítico
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#7f1d1d' }}>
                    {(estoqueCriticoData?.parametros?.limite_critico || 0).toFixed(1)} limite crítico configurado
                  </div>
                </div>
              </div>
            </div>

            {/* Tabela de produtos críticos */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: '#f9fafb' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Produto</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Qtd Atual</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Valor Atual</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Movimentações</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(estoqueCriticoData?.produtos || []).map((produto, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                        <div>{produto?.nome || 'N/A'}</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{produto?.referencia || ''}</div>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: '#dc2626' }}>
                        {formatNumber(produto?.quantidade_atual)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#374151' }}>
                        {formatCurrency(produto?.valor_atual || 0)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: '#dc2626' }}>
                        {formatNumber(produto?.total_movimentacoes)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <span style={{
                          padding: '4px 8px',
                          backgroundColor: '#fef2f2',
                          color: '#dc2626',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: '500'
                        }}>
                          Crítico
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Produtos Mais Movimentados Tab */}
        {activeTab === 'movimentados' && produtosMovimentadosData && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              🔄 Produtos Mais Movimentados
            </h2>
            
            {/* Info do período */}
            <div style={{ 
              backgroundColor: '#eff6ff', 
              border: '1px solid #bfdbfe', 
              borderRadius: '8px', 
              padding: '16px', 
              marginBottom: '24px' 
            }}>
              <div style={{ fontSize: '0.875rem', color: '#1d4ed8' }}>
                📊 Data da consulta: {produtosMovimentadosData?.parametros?.data_consulta || 'N/A'}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#1d4ed8', marginTop: '4px' }}>
                Total de produtos analisados: {formatNumber(produtosMovimentadosData?.parametros?.total_produtos_analisados)}
              </div>
            </div>

            {/* Tabela de produtos movimentados */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: '#f9fafb' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Ranking</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Produto</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Total Movimentações</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Última Movimentação</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Tipos de Movimentação</th>
                  </tr>
                </thead>
                <tbody>
                  {(produtosMovimentadosData?.produtos_mais_movimentados || []).map((produto, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px', fontSize: '0.875rem', fontWeight: '600', color: '#2563eb' }}>
                        #{index + 1}
                      </td>
                      <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                        <div>{produto?.nome || 'N/A'}</div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{produto?.referencia || ''}</div>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: '#059669' }}>
                        {formatNumber(produto?.total_movimentacoes)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '0.875rem', color: '#374151' }}>
                        {formatDate(produto?.ultima_movimentacao || '')}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#059669' }}>
                        {produto?.tipos_movimentacao?.join(', ') || 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Movimentações Período Tab */}
        {activeTab === 'movimentacoes-periodo' && movimentacoesPeriodoData && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              📅 Movimentações do Período (Últimos 30 dias)
            </h2>

            {/* Resumo das movimentações */}
            <div style={{ 
              backgroundColor: '#f3f4f6', 
              padding: '20px', 
              borderRadius: '8px', 
              marginBottom: '24px',
              border: '1px solid #e5e7eb'
            }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>
                📊 Resumo Geral
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Total de Produtos</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                    {formatNumber(movimentacoesPeriodoData.resumo.total_produtos)}
                  </div>
                </div>
                <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Total Entradas</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#059669' }}>
                    {formatNumber(movimentacoesPeriodoData.resumo.quantidade_total_entradas)}
                  </div>
                </div>
                <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Total Saídas</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#dc2626' }}>
                    {formatNumber(movimentacoesPeriodoData.resumo.quantidade_total_saidas)}
                  </div>
                </div>
                <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Valor Total Entrada</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#059669' }}>
                    {formatCurrency(movimentacoesPeriodoData.resumo.valor_total_entradas)}
                  </div>
                </div>
                <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Valor Total Saída</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#dc2626' }}>
                    {formatCurrency(movimentacoesPeriodoData.resumo.valor_total_saidas)}
                  </div>
                </div>
                <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Saldo do Período</div>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: '700', 
                    color: movimentacoesPeriodoData.resumo.saldo_periodo >= 0 ? '#059669' : '#dc2626' 
                  }}>
                    {formatCurrency(movimentacoesPeriodoData.resumo.saldo_periodo)}
                  </div>
                </div>
                {/* ✨ NOVOS CAMPOS DO BACKEND */}
                {movimentacoesPeriodoData.resumo.valor_total_saidas_preco_entrada !== undefined && (
                  <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Valor Saída (Preço Entrada)</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#8b5cf6' }}>
                      {formatCurrency(movimentacoesPeriodoData.resumo.valor_total_saidas_preco_entrada)}
                    </div>
                  </div>
                )}
                {movimentacoesPeriodoData.resumo.diferenca_total_precos !== undefined && (
                  <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Diferença de Preços</div>
                    <div style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: '700', 
                      color: movimentacoesPeriodoData.resumo.diferenca_total_precos >= 0 ? '#059669' : '#dc2626' 
                    }}>
                      {formatCurrency(movimentacoesPeriodoData.resumo.diferenca_total_precos)}
                    </div>
                  </div>
                )}
                {movimentacoesPeriodoData.resumo.margem_total !== undefined && (
                  <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Margem Total (%)</div>
                    <div style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: '700', 
                      color: movimentacoesPeriodoData.resumo.margem_total >= 0 ? '#059669' : '#dc2626' 
                    }}>
                      {movimentacoesPeriodoData.resumo.margem_total.toFixed(2)}%
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Tabela de produtos movimentados */}
            <div style={{ 
              backgroundColor: 'white', 
              border: '1px solid #e5e7eb', 
              borderRadius: '8px',
              overflow: 'hidden'
            }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: '#f9fafb' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb', width: '50px' }}></th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>ID</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Produto</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Referência</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Total Movimentações</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Qtd Entrada</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Qtd Saída</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Valor Entrada</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Valor Saída</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Valor Saída (Preço Entrada)</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', color: '#374151', fontSize: '0.875rem', borderBottom: '1px solid #e5e7eb' }}>Saldo</th>
                  </tr>
                </thead>
                <tbody>
                  {movimentacoesPeriodoData.produtos_movimentados.map((produto, index) => (
                    <React.Fragment key={produto.produto_id}>
                      {/* Linha principal do produto */}
                      <tr style={{ 
                        backgroundColor: index % 2 === 0 ? 'white' : '#f9fafb',
                        borderBottom: produtosExpandidos.has(produto.produto_id) ? 'none' : '1px solid #e5e7eb'
                      }}>
                        {/* Botão de expansão */}
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <button
                            onClick={() => toggleProdutoExpansao(produto.produto_id)}
                            style={{
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              fontSize: '1rem',
                              color: '#6b7280',
                              transition: 'transform 0.2s ease'
                            }}
                            title={produtosExpandidos.has(produto.produto_id) ? 'Recolher detalhes' : 'Expandir detalhes'}
                          >
                            {produtosExpandidos.has(produto.produto_id) ? '▼' : '▶'}
                          </button>
                        </td>
                        <td style={{ padding: '12px', color: '#374151', fontSize: '0.875rem' }}>{produto.produto_id}</td>
                        <td style={{ padding: '12px', color: '#111827', fontSize: '0.875rem', fontWeight: '500' }}>{produto.nome}</td>
                        <td style={{ padding: '12px', color: '#6b7280', fontSize: '0.875rem' }}>{produto.referencia || 'N/A'}</td>
                        <td style={{ padding: '12px', textAlign: 'center', color: '#374151', fontSize: '0.875rem', fontWeight: '600' }}>
                          {formatNumber(produto.total_movimentacoes)}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'center', color: '#059669', fontSize: '0.875rem' }}>
                          {formatNumber(produto.quantidade_entrada)}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'center', color: '#dc2626', fontSize: '0.875rem' }}>
                          {formatNumber(produto.quantidade_saida)}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'right', color: '#059669', fontSize: '0.875rem', fontWeight: '500' }}>
                          {formatCurrency(produto.valor_entrada)}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'right', color: '#dc2626', fontSize: '0.875rem', fontWeight: '500' }}>
                          {formatCurrency(produto.valor_saida)}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'right', color: '#8b5cf6', fontSize: '0.875rem', fontWeight: '500' }}>
                          {formatCurrency(produto.valor_saida_preco_entrada || 0)}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          textAlign: 'right', 
                          fontSize: '0.875rem', 
                          fontWeight: '600',
                          color: produto.saldo_valor >= 0 ? '#059669' : '#dc2626'
                        }}>
                          {formatCurrency(produto.saldo_valor)}
                        </td>
                      </tr>

                      {/* Linha expandida com detalhes das movimentações */}
                      {produtosExpandidos.has(produto.produto_id) && produto.movimentacoes_detalhadas && (
                        <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e5e7eb' }}>
                          <td colSpan={11} style={{ padding: '16px' }}>
                            <div style={{ 
                              backgroundColor: 'white', 
                              borderRadius: '6px', 
                              border: '1px solid #e5e7eb',
                              overflow: 'hidden'
                            }}>
                              <div style={{ 
                                backgroundColor: '#f1f5f9', 
                                padding: '12px 16px', 
                                borderBottom: '1px solid #e5e7eb',
                                fontWeight: '600',
                                fontSize: '0.875rem',
                                color: '#334155'
                              }}>
                                📝 Detalhes das Movimentações - {produto.nome}
                              </div>
                              <div style={{ padding: '12px' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                  <thead style={{ backgroundColor: '#f8fafc' }}>
                                    <tr>
                                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#64748b', borderBottom: '1px solid #e2e8f0' }}>Data</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#64748b', borderBottom: '1px solid #e2e8f0' }}>Tipo</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '600', color: '#64748b', borderBottom: '1px solid #e2e8f0' }}>Quantidade</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#64748b', borderBottom: '1px solid #e2e8f0' }}>Valor Unit.</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#64748b', borderBottom: '1px solid #e2e8f0' }}>Valor Total</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '600', color: '#64748b', borderBottom: '1px solid #e2e8f0' }}>Documento</th>
                                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#64748b', borderBottom: '1px solid #e2e8f0' }}>Observações</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {Array.isArray(produto.movimentacoes_detalhadas) && produto.movimentacoes_detalhadas.map((mov: MovimentacaoDetalhada, movIndex: number) => {
                                      return (
                                        <tr key={movIndex} style={{ 
                                          backgroundColor: movIndex % 2 === 0 ? 'white' : '#f8fafc',
                                          borderBottom: '1px solid #f1f5f9'
                                        }}>
                                          <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#475569' }}>
                                            {formatDate(mov.data)}
                                          </td>
                                          <td style={{ padding: '8px 12px', fontSize: '0.75rem' }}>
                                            <span style={{
                                              padding: '2px 6px',
                                              borderRadius: '4px',
                                              fontSize: '0.7rem',
                                              fontWeight: '500',
                                              backgroundColor: mov.is_entrada ? '#dcfce7' : '#fee2e2',
                                              color: mov.is_entrada ? '#166534' : '#991b1b'
                                            }}>
                                              {mov.is_entrada ? '⬆️ ENTRADA' : '⬇️ SAÍDA'}
                                            </span>
                                          </td>
                                          <td style={{ 
                                            padding: '8px 12px', 
                                            fontSize: '0.75rem', 
                                            textAlign: 'center',
                                            color: mov.is_entrada ? '#059669' : '#dc2626',
                                            fontWeight: '500'
                                          }}>
                                            {formatNumber(mov.quantidade)}
                                          </td>
                                          <td style={{ 
                                            padding: '8px 12px', 
                                            fontSize: '0.75rem', 
                                            textAlign: 'right',
                                            color: '#475569'
                                          }}>
                                            {formatCurrency(mov.valor_unitario)}
                                          </td>
                                          <td style={{ 
                                            padding: '8px 12px', 
                                            fontSize: '0.75rem', 
                                            textAlign: 'right',
                                            color: mov.is_entrada ? '#059669' : '#dc2626',
                                            fontWeight: '500'
                                          }}>
                                            {formatCurrency(mov.valor_total)}
                                          </td>
                                          <td style={{ 
                                            padding: '8px 12px', 
                                            fontSize: '0.75rem', 
                                            textAlign: 'center',
                                            color: '#475569'
                                          }}>
                                            {mov.documento || 'N/A'}
                                          </td>
                                          <td style={{ 
                                            padding: '8px 12px', 
                                            fontSize: '0.7rem', 
                                            color: '#64748b',
                                            maxWidth: '200px',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            whiteSpace: 'nowrap'
                                          }} title={mov.observacoes || ''}>
                                            {mov.observacoes || 'N/A'}
                                          </td>
                                        </tr>
                                      );
                                    })}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Informações do período */}
            <div style={{ 
              marginTop: '16px', 
              padding: '16px', 
              backgroundColor: '#f3f4f6', 
              borderRadius: '6px',
              fontSize: '0.875rem',
              color: '#6b7280'
            }}>
              <strong>Período:</strong> {movimentacoesPeriodoData.resumo.periodo} | 
              <strong> Total de produtos movimentados:</strong> {formatNumber(movimentacoesPeriodoData.resumo.total_produtos)} |
              <strong> Total de movimentações:</strong> {formatNumber(movimentacoesPeriodoData.resumo.total_movimentacoes)}
            </div>
          </div>
        )}

        {/* Produto Específico Tab */}
        {activeTab === 'especifico' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>
              🔍 Consulta de Produto Específico
            </h2>
            
            {/* Formulário de busca */}
            <div style={{ 
              backgroundColor: '#f9fafb', 
              border: '1px solid #e5e7eb', 
              borderRadius: '8px', 
              padding: '20px', 
              marginBottom: '24px' 
            }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'end', flexWrap: 'wrap' }}>
                <div style={{ flex: '1', minWidth: '200px' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>
                    ID do Produto
                  </label>
                  <input
                    type="number"
                    value={produtoEspecificoId}
                    onChange={(e) => setProdutoEspecificoId(e.target.value)}
                    placeholder="Digite o ID do produto"
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  />
                </div>
                <button
                  onClick={buscarProdutoEspecifico}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#2563eb',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  🔍 Buscar
                </button>
              </div>
            </div>

            {/* Resultado da busca */}
            {produtoEspecificoData && (
              <div>
                {(produtoEspecificoData?.estoque || []).length > 0 ? (
                  <div style={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '8px', 
                    padding: '20px' 
                  }}>
                    {(produtoEspecificoData?.estoque || []).map((produto: ProdutoEstoque, index: number) => (
                      <div key={index} style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                        gap: '16px' 
                      }}>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Nome do Produto</div>
                          <div style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>{produto?.nome || 'N/A'}</div>
                          <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{produto?.referencia || ''}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Quantidade Atual</div>
                          <div style={{ fontSize: '1.125rem', fontWeight: '600', color: '#059669' }}>{formatNumber(produto?.quantidade_atual)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Qtd Inicial</div>
                          <div style={{ fontSize: '1.125rem', fontWeight: '600', color: '#374151' }}>{formatNumber(produto?.quantidade_inicial)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Variação Qtd</div>
                          <div style={{ fontSize: '1.125rem', fontWeight: '600', color: produto?.variacao_quantidade >= 0 ? '#059669' : '#dc2626' }}>
                            {produto?.variacao_quantidade >= 0 ? '+' : ''}{formatNumber(produto?.variacao_quantidade)}
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Valor Inicial</div>
                          <div style={{ fontSize: '1.125rem', fontWeight: '600', color: '#374151' }}>{formatCurrency(produto?.valor_inicial || 0)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Total Movimentações</div>
                          <div style={{ fontSize: '1rem', fontWeight: '600', color: '#374151' }}>{formatNumber(produto?.total_movimentacoes)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500' }}>Data de Cálculo</div>
                          <div style={{ fontSize: '1rem', fontWeight: '600', color: '#374151' }}>{formatDate(produto?.data_calculo || '')}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '40px', 
                    backgroundColor: '#fefce8', 
                    border: '1px solid #fde047', 
                    borderRadius: '8px' 
                  }}>
                    <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🔍</div>
                    <div style={{ fontSize: '1rem', fontWeight: '600', color: '#a16207' }}>
                      Produto não encontrado
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#92400e', marginTop: '4px' }}>
                      Verifique se o ID do produto está correto
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EstoqueDashboard;
