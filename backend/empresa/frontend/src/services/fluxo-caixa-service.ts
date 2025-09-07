import axios from 'axios';
import type {
  MovimentacoesRealizadasResponse,
  ResumoMensalResponse,
  MovimentacoesVencimentoAbertoResponse,
  ComparativoRealizadoVsPrevistoResponse,
  FiltrosPeriodo
} from '@/types/fluxo-caixa';

// Configuração base da API
const API_BASE_URL = 'http://127.0.0.1:8000/contas';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para logs de request/response (apenas em desenvolvimento)
if (import.meta.env.DEV) {
  apiClient.interceptors.request.use(
    (config) => {
      console.log('🚀 API Request:', config.method?.toUpperCase(), config.url, config.params);
      return config;
    },
    (error) => {
      console.error('❌ API Request Error:', error);
      return Promise.reject(error);
    }
  );

  apiClient.interceptors.response.use(
    (response) => {
      console.log('✅ API Response:', response.status, response.config.url);
      return response;
    },
    (error) => {
      console.error('❌ API Response Error:', error.response?.status, error.response?.data);
      return Promise.reject(error);
    }
  );
}

export class FluxoCaixaRealizadoService {
  
  /**
   * Busca movimentações realizadas (pagas/recebidas) no período
   */
  async getMovimentacoesRealizadas(filtros: FiltrosPeriodo): Promise<MovimentacoesRealizadasResponse> {
    try {
      const response = await apiClient.get('/fluxo-caixa-realizado/movimentacoes_realizadas/', {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar movimentações realizadas:', error);
      throw new Error('Falha ao carregar movimentações realizadas');
    }
  }

  /**
   * Busca resumo mensal das movimentações realizadas
   */
  async getResumoMensal(filtros: FiltrosPeriodo): Promise<ResumoMensalResponse> {
    try {
      const response = await apiClient.get('/fluxo-caixa-realizado/resumo_mensal/', {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar resumo mensal:', error);
      throw new Error('Falha ao carregar resumo mensal');
    }
  }

  /**
   * Busca resumo diário das movimentações realizadas
   */
  async getResumoDiario(filtros: FiltrosPeriodo): Promise<ResumoMensalResponse> {
    try {
      const response = await apiClient.get('/fluxo-caixa-realizado/resumo_diario/', {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar resumo diário:', error);
      throw new Error('Falha ao carregar resumo diário');
    }
  }

  /**
   * Busca movimentações com vencimento no período que estão em aberto
   */
  async getMovimentacoesVencimentoAberto(filtros: FiltrosPeriodo): Promise<MovimentacoesVencimentoAbertoResponse> {
    try {
      const response = await apiClient.get('/fluxo-caixa-realizado/movimentacoes_vencimento_aberto/', {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar movimentações vencimento aberto:', error);
      throw new Error('Falha ao carregar movimentações pendentes');
    }
  }

  /**
   * Busca comparativo entre realizado vs previsto
   */
  async getComparativoRealizadoVsPrevisto(filtros: FiltrosPeriodo): Promise<ComparativoRealizadoVsPrevistoResponse> {
    try {
      const response = await apiClient.get('/analise-fluxo-caixa/comparativo_realizado_vs_previsto/', {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar comparativo realizado vs previsto:', error);
      throw new Error('Falha ao carregar análise comparativa');
    }
  }

  /**
   * Busca análise de inadimplência
   */
  async getAnaliseInadimplencia(dataLimite?: string) {
    try {
      const response = await apiClient.get('/analise-fluxo-caixa/inadimplencia/', {
        params: dataLimite ? { data_limite: dataLimite } : {}
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar análise de inadimplência:', error);
      throw new Error('Falha ao carregar análise de inadimplência');
    }
  }

  /**
   * Busca projeção semanal
   */
  async getProjecaoSemanal(semanas: number = 4) {
    try {
      const response = await apiClient.get('/analise-fluxo-caixa/projecao_semanal/', {
        params: { semanas }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar projeção semanal:', error);
      throw new Error('Falha ao carregar projeção semanal');
    }
  }
}

// Instância singleton do serviço
export const fluxoCaixaService = new FluxoCaixaRealizadoService();

// Utilitários para formatação
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('pt-BR');
};

export const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('pt-BR');
};

export const getStatusVencimentoColor = (status: string): string => {
  switch (status) {
    case 'no_prazo':
      return 'text-green-600';
    case 'vence_em_breve':
      return 'text-yellow-600';
    case 'vencido':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

export const getStatusVencimentoLabel = (status: string): string => {
  switch (status) {
    case 'no_prazo':
      return 'No Prazo';
    case 'vence_em_breve':
      return 'Vence em Breve';
    case 'vencido':
      return 'Vencido';
    default:
      return 'Indefinido';
  }
};
