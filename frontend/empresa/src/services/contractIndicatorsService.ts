// src/services/contractIndicatorsService.ts
import axios from 'axios';
import config from '@/config';

// Types
interface IndicadorGeral {
  data_referencia: string;
  indicadores_base: {
    total_contratos: number;
    total_itens: number;
    valor_total_contratos: number;
    valor_medio_item: number;
  };
  contratos_por_tipo: Array<{
    tipo: string;
    quantidade: number;
    valor_total: number;
  }>;
  vencimentos_proximos: Array<{
    id: number;
    contrato: string;
    cliente: string;
    fim: string;
    valor: number;
  }>;
}

interface PrevisaoRenovacao {
  periodo_analise: {
    inicio: string;
    fim: string;
    meses: number;
  };
  metricas_historicas: {
    total_contratos_encerrados: number;
    total_renovacoes: number;
    taxa_renovacao: number;
  };
  contratos_analise: Array<{
    contrato: string;
    cliente: string;
    data_vencimento: string;
    valor_contrato: number;
    historico_cliente: {
      total_contratos: number;
      renovacoes: number;
      taxa_renovacao: number;
    };
    indicadores_recentes: {
      faturamento: number;
      custos_manutencao: number;
      margem: number;
    };
    previsao: {
      score_renovacao: number;
      probabilidade_renovacao: number;
      recomendacoes: string[];
    };
  }>;
  resumo_previsao: {
    total_contratos: number;
    valor_em_risco: number;
    probabilidade_media_renovacao: number;
  };
}

interface AnalisePerformance {
  periodo_analise: {
    inicio: string;
    fim: string;
    meses: number;
  };
  resultados: Array<{
    contrato: string;
    cliente: string;
    tipo_contrato: string;
    metricas_operacionais: {
      quantidade_equipamentos: number;
      manutencoes_periodo: number;
      uptime_percentual: number;
      mtbf_dias: number;
      manutencoes_por_equipamento: number;
    };
    metricas_financeiras: {
      faturamento: number;
      custos: number;
      margem: number;
      custo_por_equipamento: number;
    };
    comparativo_mercado: {
      uptime: {
        valor_contrato: number;
        valor_mercado: number;
        diferenca_percentual: number;
      };
      custo_manutencao: {
        valor_contrato: number;
        valor_mercado: number;
      };
    };
    alertas: Array<{
      tipo: string;
      severidade: 'alta' | 'media' | 'baixa';
      mensagem: string;
    }>;
  }>;
  indicadores_consolidados: {
    operacionais: {
      total_equipamentos: number;
      total_manutencoes: number;
      media_manutencoes_por_equip: number;
      uptime_medio: number;
    };
    financeiros: {
      faturamento_total: number;
      custos_totais: number;
      margem_total: number;
      margem_percentual: number;
    };
  };
}

// Use env-driven baseURL. In dev, set VITE_API_URL=/contas and Vite proxy will route to backend.
const api = axios.create({
  baseURL: config.api.baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const contractIndicatorsService = {
  getIndicadoresGerais: async () => {
    try {
      const response = await api.get<IndicadorGeral>(
        '/contratos_locacao/'
      );
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar indicadores gerais:', error);
      throw error;
    }
  },

  getPrevisaoRenovacoes: async (_meses: number = 6) => {
    try {
      const response = await api.get<PrevisaoRenovacao>(
        `/contratos_locacao/`
      );
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar previsão de renovações:', error);
      throw error;
    }
  },

  getAnalisePerformance: async (_meses: number = 12) => {
    try {
      const response = await api.get<AnalisePerformance>(
        `/contratos_locacao/`
      );
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar análise de performance:', error);
      throw error;
    }
  },

  formatarMoeda: (valor: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  },

  formatarData: (data: string): string => {
    return new Date(data).toLocaleDateString('pt-BR');
  },

  formatarPercentual: (valor: number): string => {
    return `${valor.toFixed(2)}%`;
  }
};

export type { IndicadorGeral, PrevisaoRenovacao, AnalisePerformance };