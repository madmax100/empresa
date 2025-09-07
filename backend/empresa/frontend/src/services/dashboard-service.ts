import axios from 'axios';

// Configuração base da API
const API_BASE_URL = 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tipos para os dados do dashboard do backend
export interface DashboardResumo {
  total_atrasado: number;
  total_pago_periodo: number;
  total_cancelado_periodo: number;
  total_aberto_periodo: number;
  quantidade_titulos: number;
  quantidade_atrasados_periodo: number;
}

export interface DashboardContasPagar {
  resumo: DashboardResumo;
  titulos_atrasados: unknown[];
  titulos_vencendo: unknown[];
}

export interface DashboardContasReceber {
  resumo: DashboardResumo;
  titulos_atrasados: unknown[];
  titulos_vencendo: unknown[];
}

// Interface para o endpoint de movimentações realizadas
export interface MovimentacaoRealizada {
  id: string;
  tipo: 'entrada' | 'saida';
  data_pagamento: string;
  valor: number;
  contraparte: string;
  historico: string;
  forma_pagamento: string;
  origem: 'contas_receber' | 'contas_pagar';
}

export interface FluxoCaixaRealizadoResponse {
  periodo: {
    data_inicio: string;
    data_fim: string;
  };
  resumo: {
    total_entradas: number;
    total_saidas: number;
    saldo_liquido: number;
    total_movimentacoes: number;
  };
  movimentacoes: MovimentacaoRealizada[];
}

export interface FluxoCaixaRealizado {
  total_entradas_pagas: number;
  total_saidas_pagas: number;
  saldo_liquido: number;
  total_movimentacoes: number;
  entradas_periodo: number;
  saidas_periodo: number;
  titulos_atrasados_pagar: number;
  titulos_atrasados_receber: number;
  periodo_analise: string;
}

// Função para formatar currency
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

// Função para formatar data
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('pt-BR').format(date);
};

// Serviço para buscar dados do fluxo de caixa realizado
export const fluxoCaixaService = {
  async getFluxoCaixaRealizado(): Promise<FluxoCaixaRealizado> {
    try {
      console.log('🔄 Buscando dados de fluxo de caixa realizado...');
      
      // Buscar dados de fluxo de caixa realizado
      const currentYear = new Date().getFullYear();
      const dataInicio = `${currentYear}-01-01`;
      const dataFim = `${currentYear}-12-31`;
      
      const response = await apiClient.get<FluxoCaixaRealizadoResponse>(
        `/api/fluxo-caixa-realizado/movimentacoes_realizadas/?data_inicio=${dataInicio}&data_fim=${dataFim}`
      );

      const dados = response.data;

      console.log('📊 Dados do fluxo de caixa recebidos:', dados.resumo);

      // Buscar dados de dashboard para informações adicionais
      const [contasPagarResponse, contasReceberResponse] = await Promise.all([
        apiClient.get<DashboardContasPagar>('/api/contas_pagar/dashboard/'),
        apiClient.get<DashboardContasReceber>('/api/contas_receber/dashboard/')
      ]);

      const fluxoCaixa: FluxoCaixaRealizado = {
        total_entradas_pagas: dados.resumo.total_entradas,
        total_saidas_pagas: dados.resumo.total_saidas,
        saldo_liquido: dados.resumo.saldo_liquido,
        total_movimentacoes: dados.resumo.total_movimentacoes,
        entradas_periodo: dados.resumo.total_entradas,
        saidas_periodo: dados.resumo.total_saidas,
        titulos_atrasados_pagar: contasPagarResponse.data.resumo.quantidade_atrasados_periodo,
        titulos_atrasados_receber: contasReceberResponse.data.resumo.quantidade_atrasados_periodo,
        periodo_analise: `${dataInicio} a ${dataFim}`
      };

      console.log('✅ Fluxo de caixa realizado calculado:', {
        entradas: formatCurrency(fluxoCaixa.total_entradas_pagas),
        saidas: formatCurrency(fluxoCaixa.total_saidas_pagas),
        saldo: formatCurrency(fluxoCaixa.saldo_liquido),
        movimentacoes: fluxoCaixa.total_movimentacoes,
        atrasados: `${fluxoCaixa.titulos_atrasados_pagar + fluxoCaixa.titulos_atrasados_receber} títulos`
      });

      return fluxoCaixa;

    } catch (error) {
      console.error('❌ Erro ao buscar dados de fluxo de caixa:', error);
      throw error;
    }
  },

  async getMovimentacoesRecentes(): Promise<MovimentacaoRealizada[]> {
    try {
      console.log('🔄 Buscando movimentações recentes...');
      
      const currentYear = new Date().getFullYear();
      const dataInicio = `${currentYear}-01-01`;
      const dataFim = `${currentYear}-12-31`;
      
      const response = await apiClient.get<FluxoCaixaRealizadoResponse>(
        `/api/fluxo-caixa-realizado/movimentacoes_realizadas/?data_inicio=${dataInicio}&data_fim=${dataFim}`
      );

      console.log('📊 Movimentações encontradas:', response.data.movimentacoes.length);

      // Retornar apenas as últimas 20 movimentações ordenadas por data (mais recentes primeiro)
      const movimentacoesRecentes = response.data.movimentacoes
        .sort((a, b) => new Date(b.data_pagamento).getTime() - new Date(a.data_pagamento).getTime())
        .slice(0, 20);

      console.log('✅ Retornando', movimentacoesRecentes.length, 'movimentações recentes');
      
      return movimentacoesRecentes;

    } catch (error) {
      console.error('❌ Erro ao buscar movimentações recentes:', error);
      return [];
    }
  }
};
