// Stock Service for handling stock control API calls
// This service manages all stock-related data fetching

const API_BASE_URL = 'http://127.0.0.1:8000';

// Interfaces for stock data
export interface ProdutoEstoque {
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

export interface EstoqueAtualData {
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

export interface ProdutoCritico {
  produto_id: number;
  nome: string;
  referencia: string;
  quantidade_inicial: number;
  quantidade_atual: number;
  valor_atual: number;
  total_movimentacoes: number;
}

export interface EstoqueCriticoData {
  produtos: ProdutoCritico[];
  parametros: {
    data_consulta: string;
    limite_critico: number;
    total_produtos_criticos: number;
  };
}

export interface ProdutoMovimentado {
  produto_id: number;
  nome: string;
  referencia: string;
  total_movimentacoes: number;
  ultima_movimentacao: string;
  tipos_movimentacao: string[];
}

export interface ProdutosMaisMovimentadosData {
  produtos_mais_movimentados: ProdutoMovimentado[];
  parametros: {
    data_consulta: string;
    limite: number;
    total_produtos_analisados: number;
  };
}

export interface MovimentacaoDetalhada {
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

export interface ProdutoMovimentadoPeriodo {
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

export interface MovimentacoesPeriodoData {
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

// API Response wrapper
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  status?: number;
}

class StockService {
  private async makeRequest<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      console.log(`🔍 StockService: Fetching ${API_BASE_URL}${endpoint}`);
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log(`📊 StockService: Response status ${response.status} for ${endpoint}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ StockService: Error ${response.status} - ${errorText}`);
        return {
          success: false,
          error: `HTTP ${response.status}: ${errorText}`,
          status: response.status
        };
      }

      const data = await response.json();
      console.log(`✅ StockService: Success for ${endpoint}`, data);
      
      return {
        success: true,
        data
      };
    } catch (error) {
      console.error(`❌ StockService: Network error for ${endpoint}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  // Get current stock data
  async getEstoqueAtual(params?: {
    limite?: number;
    offset?: number;
    data?: string;
    produto_id?: number;
    ordem?: string;
    reverso?: boolean;
  }): Promise<ApiResponse<EstoqueAtualData>> {
    const queryParams = new URLSearchParams();
    
    if (params?.limite) queryParams.append('limite', params.limite.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    if (params?.data) queryParams.append('data', params.data);
    if (params?.produto_id) queryParams.append('produto_id', params.produto_id.toString());
    if (params?.ordem) queryParams.append('ordem', params.ordem);
    if (params?.reverso) queryParams.append('reverso', 'true');

    const endpoint = `/api/estoque-controle/estoque_atual/?${queryParams.toString()}`;
    return this.makeRequest<EstoqueAtualData>(endpoint);
  }

  // Get critical stock data
  async getEstoqueCritico(params?: {
    limite?: number;
    data?: string;
  }): Promise<ApiResponse<EstoqueCriticoData>> {
    const queryParams = new URLSearchParams();
    
    if (params?.limite) queryParams.append('limite', params.limite.toString());
    if (params?.data) queryParams.append('data', params.data);

    const endpoint = `/api/estoque-controle/estoque_critico/?${queryParams.toString()}`;
    return this.makeRequest<EstoqueCriticoData>(endpoint);
  }

  // Get most moved products
  async getProdutosMaisMovimentados(params?: {
    limite?: number;
    data?: string;
  }): Promise<ApiResponse<ProdutosMaisMovimentadosData>> {
    const queryParams = new URLSearchParams();
    
    if (params?.limite) queryParams.append('limite', params.limite.toString());
    if (params?.data) queryParams.append('data', params.data);

    const endpoint = `/api/estoque-controle/produtos_mais_movimentados/?${queryParams.toString()}`;
    return this.makeRequest<ProdutosMaisMovimentadosData>(endpoint);
  }

  // Get period movements
  async getMovimentacoesPeriodo(params: {
    data_inicio: string;
    data_fim: string;
    incluir_detalhes?: boolean;
    produto_id?: number;
  }): Promise<ApiResponse<MovimentacoesPeriodoData>> {
    const queryParams = new URLSearchParams();
    
    queryParams.append('data_inicio', params.data_inicio);
    queryParams.append('data_fim', params.data_fim);
    if (params.incluir_detalhes) queryParams.append('incluir_detalhes', 'true');
    if (params.produto_id) queryParams.append('produto_id', params.produto_id.toString());

    const endpoint = `/api/estoque-controle/movimentacoes_periodo/?${queryParams.toString()}`;
    return this.makeRequest<MovimentacoesPeriodoData>(endpoint);
  }

  // Test backend connectivity
  async testConnection(): Promise<ApiResponse<any>> {
    try {
      console.log('🌐 StockService: Testing backend connectivity...');
      
      const response = await fetch(`${API_BASE_URL}/`, {
        method: 'GET',
      });

      if (response.ok) {
        console.log('✅ StockService: Backend is reachable');
        return { success: true, data: { message: 'Backend is reachable' } };
      } else {
        console.log(`❌ StockService: Backend returned ${response.status}`);
        return { 
          success: false, 
          error: `Backend returned ${response.status}`,
          status: response.status 
        };
      }
    } catch (error) {
      console.error('❌ StockService: Cannot reach backend:', error);
      return {
        success: false,
        error: 'Cannot reach backend. Make sure it is running on http://127.0.0.1:8000'
      };
    }
  }

  // Get comprehensive stock dashboard data
  async getDashboardData(data?: string): Promise<{
    estoqueGeral: ApiResponse<EstoqueAtualData>;
    estoqueTop: ApiResponse<EstoqueAtualData>;
    estoqueCritico: ApiResponse<EstoqueCriticoData>;
    produtosMovimentados: ApiResponse<ProdutosMaisMovimentadosData>;
  }> {
    console.log('📊 StockService: Loading comprehensive dashboard data...');

    const [estoqueGeral, estoqueTop, estoqueCritico, produtosMovimentados] = await Promise.all([
      this.getEstoqueAtual({ limite: 50, data }),
      this.getEstoqueAtual({ limite: 100, ordem: 'valor_atual', reverso: true, data }),
      this.getEstoqueCritico({ limite: 10, data }),
      this.getProdutosMaisMovimentados({ limite: 10, data })
    ]);

    return {
      estoqueGeral,
      estoqueTop,
      estoqueCritico,
      produtosMovimentados
    };
  }
}

// Export singleton instance
export const stockService = new StockService();
export default stockService;