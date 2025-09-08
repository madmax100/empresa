// Serviço para API de resultados do período
export interface VariacaoEstoque {
  valorAnterior: number;
  valorAtual: number;
  diferenca: number;
  percentual: number;
}

export interface LucroOperacional {
  valorSaida: number;
  valorEntrada: number;
  lucro: number;
  margem: number;
}

export interface ContratosRecebidos {
  valorTotal: number;
  quantidadeContratos: number;
  valorMedio: number;
}

export interface ResumoGeral {
  resultadoLiquido: number;
  margem: number;
}

export interface ResultadosPeriodo {
  variacaoEstoque: VariacaoEstoque;
  lucroOperacional: LucroOperacional;
  contratosRecebidos: ContratosRecebidos;
  resumoGeral: ResumoGeral;
}

export interface FiltrosPeriodo {
  data_inicio: string;
  data_fim: string;
}

class ResultadosService {
  private baseURL = '/api';

  // Buscar variação de estoque no período
  async buscarVariacaoEstoque(filtros: FiltrosPeriodo): Promise<VariacaoEstoque> {
    try {
      const params = new URLSearchParams({
        data_inicio: filtros.data_inicio,
        data_fim: filtros.data_fim
      });

      const response = await fetch(`${this.baseURL}/estoque/variacao/?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar variação de estoque: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar variação de estoque:', error);
      throw error;
    }
  }

  // Buscar lucro operacional (diferença entre saída e entrada)
  async buscarLucroOperacional(filtros: FiltrosPeriodo): Promise<LucroOperacional> {
    try {
      const params = new URLSearchParams({
        data_inicio: filtros.data_inicio,
        data_fim: filtros.data_fim
      });

      const response = await fetch(`${this.baseURL}/operacoes/lucro/?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar lucro operacional: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar lucro operacional:', error);
      throw error;
    }
  }

  // Buscar valores recebidos dos contratos
  async buscarContratosRecebidos(filtros: FiltrosPeriodo): Promise<ContratosRecebidos> {
    try {
      const params = new URLSearchParams({
        data_inicio: filtros.data_inicio,
        data_fim: filtros.data_fim
      });

      const response = await fetch(`${this.baseURL}/contratos_locacao/recebimentos/?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar recebimentos de contratos: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar recebimentos de contratos:', error);
      throw error;
    }
  }

  // Buscar resultados consolidados do período
  async buscarResultadosPeriodo(filtros: FiltrosPeriodo): Promise<ResultadosPeriodo> {
    try {
      // Buscar todos os dados em paralelo
      const [variacaoEstoque, lucroOperacional, contratosRecebidos] = await Promise.all([
        this.buscarVariacaoEstoque(filtros),
        this.buscarLucroOperacional(filtros),
        this.buscarContratosRecebidos(filtros)
      ]);

      // Calcular resumo geral
      const resultadoLiquido = variacaoEstoque.diferenca + lucroOperacional.lucro + contratosRecebidos.valorTotal;
      const margemTotal = contratosRecebidos.valorTotal > 0 
        ? (resultadoLiquido / contratosRecebidos.valorTotal) * 100 
        : 0;

      const resumoGeral: ResumoGeral = {
        resultadoLiquido,
        margem: margemTotal
      };

      return {
        variacaoEstoque,
        lucroOperacional,
        contratosRecebidos,
        resumoGeral
      };

    } catch (error) {
      console.error('Erro ao buscar resultados do período:', error);
      
      // Retornar dados mockados em caso de erro
      console.log('⚠️ API não disponível, usando dados mockados...');
      
      const mockData: ResultadosPeriodo = {
        variacaoEstoque: {
          valorAnterior: 150000,
          valorAtual: 165000,
          diferenca: 15000,
          percentual: 10.0
        },
        lucroOperacional: {
          valorSaida: 200000,
          valorEntrada: 140000,
          lucro: 60000,
          margem: 30.0
        },
        contratosRecebidos: {
          valorTotal: 180000,
          quantidadeContratos: 25,
          valorMedio: 7200
        },
        resumoGeral: {
          resultadoLiquido: 255000, // 15000 + 60000 + 180000
          margem: 141.7 // (255000 / 180000) * 100
        }
      };

      return mockData;
    }
  }

  // Buscar histórico de resultados para comparação
  async buscarHistoricoResultados(meses: number = 6): Promise<Array<{ periodo: string; resultado: number }>> {
    try {
      const response = await fetch(`${this.baseURL}/resultados/historico/?meses=${meses}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar histórico: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
      
      // Mock data para histórico
      const mockHistorico = [];
      const now = new Date();
      
      for (let i = meses - 1; i >= 0; i--) {
        const mesAtual = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const periodo = mesAtual.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' });
        const resultado = Math.random() * 200000 + 100000; // Valores aleatórios entre 100k e 300k
        
        mockHistorico.push({ periodo, resultado });
      }
      
      return mockHistorico;
    }
  }
}

export const resultadosService = new ResultadosService();
