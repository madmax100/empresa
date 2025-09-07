// src/types/financeiro.ts

export interface DateRange {
    inicio: string;
    fim: string;
  }
  
  export type MovimentoTipo = 'entrada' | 'saida';
  export type MovimentoFonte = 'contrato' | 'conta_receber' | 'conta_pagar' | 'outro';
  export type MovimentoStatus = 'realizado' | 'previsto' | 'cancelado';
  
  export interface FluxoCaixaFiltros {
    data_inicial: string;
    data_final: string;
    tipo?: MovimentoTipo | 'todos';
    fonte?: MovimentoFonte | 'todos';
    status?: MovimentoStatus | 'todos';
    categoria?: string;
    searchTerm?: string;
  }

  
  export interface Movimento {
    id: number;
    data: string;
    tipo: MovimentoTipo;
    valor: number;
    descricao: string;
    categoria: string;
    fonte: MovimentoFonte;
    fonte_id?: number;
    status: MovimentoStatus;
    realizado: boolean;
    data_realizacao?: string;
    data_pagamento?: string;
    data_vencimento?: string;
    data_estorno?: string;
    observacoes?: string;
  }
  
  export interface DashboardOperacional {
    filtros: FluxoCaixaFiltros;
    totalizadores: {
      entradas_realizadas: { valor: number; quantidade: number; percentual: number; };
      saidas_realizadas: { valor: number; quantidade: number; percentual: number; };
      entradas_previstas: { valor: number; quantidade: number; };
      saidas_previstas: { valor: number; quantidade: number; };
    };
    resumo: {
      saldo_inicial: number;
      saldo_final: number;
      saldo_projetado: number;
      variacao_percentual: number;
    };
    evolucao_diaria: Array<{
      data: string;
      entradas: number;
      saidas: number;
      saldo: number;
    }>;
    categorias: {
      [key: string]: {
        entradas: number;
        saidas: number;
        quantidade: number;
        saldo: number;
      }
    };
    movimentos: Movimento[];
  }
  
  export interface DashboardGerencial {
    periodo: {
      mes: number;
      ano: number;
    };
    resumo: {
      atual: {
        entradas: number;
        saidas: number;
        resultado: number;
      };
      anterior: {
        entradas: number;
        saidas: number;
        resultado: number;
      };
      variacao: {
        entradas: number;
        saidas: number;
      };
    };
    analise_categorias: {
      [key: string]: {
        entradas: number;
        saidas: number;
        quantidade: number;
        percentual: number;
      }
    };
    evolucao_mensal: Array<{
      mes: string;
      entradas: number;
      saidas: number;
      resultado: number;
      variacao: number;
    }>;
  }
  
  export interface DashboardEstrategico {
    indicadores: {
      liquidez_imediata: number;
      ciclo_caixa: number;
      margem_operacional: number;
      crescimento_receitas: number;
    };
    tendencias: {
      receitas: Array<{
        periodo: string;
        valor_realizado: number;
        valor_previsto: number;
        variacao_percentual: number;
      }>;
    };
    projecoes: {
      proximos_30_dias: {
        saldo_inicial: number;
        saldo_final: number;
        saldo_projetado: number;
      };
      proximos_90_dias: {
        saldo_inicial: number;
        saldo_final: number;
        saldo_projetado: number;
      };
      proximos_180_dias: {
        saldo_inicial: number;
        saldo_final: number;
        saldo_projetado: number;
      };
    };
    dre: {
      receita_bruta: number;
      receita_liquida: number;
      resultado_operacional: number;
      resultado_liquido: number;
    };
  }
  
  export interface Pessoa {
    id: number;
    nome: string;
  }
  
  export interface Conta {
    id: number;
    descricao: string;
    valor: number;
    data_vencimento: string;
    pessoa?: Pessoa;
    // Outros campos relevantes
  }
  
  export interface FluxoCaixaData {
    contas_a_pagar: Conta[];
    contas_a_receber: Conta[];
    total_a_pagar: number;
    total_a_receber: number;
    saldo_periodo: number;
    grafico_diario: {
      name: string;
      receitas: number;
      despesas: number;
    }[];
  }

  export interface ItemEstoque {
    id: number;
    nome: string;
    categoria: string;
    quantidade: number;
    valor_unitario: number;
    valor_total: number;
    data_ultima_atualizacao: string;
  }

  export interface RelatorioEstoque {
    resumo: {
      total_itens: number;
      valor_total: number;
      total_categorias: number;
    };
    categorias: {
      [key: string]: {
        itens: number;
        valor: number;
        percentual: number;
      }
    };
    itens: ItemEstoque[];
  }