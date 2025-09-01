// dashboard.types.ts

// Tipos básicos
export interface Filtros {
    dataInicial: string;
    dataFinal: string;
    tipo: string;
    fonte: string;
  }
  
  export interface Totalizador {
    valor: number;
    quantidade: number;
    percentual: number | null;
  }
  
  export interface Totalizadores {
    entradas_realizadas: Totalizador;
    entradas_previstas: Totalizador;
    saidas_realizadas: Totalizador;
    saidas_previstas: Totalizador;
  }
  
  export interface Receitas {
    vendas: number;
    locacao: number;
    servicos: number;
    manutencao: number;
    suprimentos: number;
  }
  
  export interface Movimento {
    id: number;
    data: string;
    tipo: 'entrada' | 'saida';
    valor: number;
    descricao: string;
    categoria: string;
    realizado: boolean;
    fonte_tipo: string;
    fonte_id: number;
  }
  
  export interface DashboardResume {
    saldo_inicial: number;
    saldo_final: number;
    saldo_projetado: number;
    variacao_percentual: number;
    entradas_total: number;
    saidas_total: number;
    vendas_equipamentos: number;
    alugueis_ativos: number;
    contratos_renovados: number;
    servicos_total: number;
    suprimentos_total: number;
    receitas_detalhadas: Receitas;
  }
  
  // Interface principal do Dashboard Operacional
  export interface DashboardOperacional {
    filtros: Filtros;
    resumo: DashboardResume;
    movimentos: Movimento[];
    totalizadores: Totalizadores;
    categorias_encontradas: string[];
  }
  
  // Interfaces para o Dashboard Gerencial
  export interface Periodo {
    mes: number;
    ano: number;
    inicio: string;
    fim: string;
  }
  
  export interface ResumoGerencial {
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
    variacoes: {
      entradas: number;
      saidas: number;
    };
  }
  
  export interface CategoriaGerencial {
    categoria: string;
    entradas: number;
    saidas: number;
    quantidade: number;
    media_valor: number;
    realizados: number;
  }
  
  export interface TendenciaGerencial {
    historico: Array<{
      mes: string;
      entradas: number;
      saidas: number;
    }>;
    projecoes: {
      proximas_entradas: number;
      proximas_saidas: number;
    };
  }
  
  export interface IndicadoresGerenciais {
    margem: number;
    realizacao_entradas: number;
    realizacao_saidas: number;
    media_diaria_entradas: number;
    media_diaria_saidas: number;
  }
  
  export interface Recomendacao {
    tipo: string;
    severidade: 'alta' | 'media' | 'baixa';
    mensagem: string;
    acoes: string[];
  }
  
  export interface DashboardGerencial {
    periodo: Periodo;
    resumo: ResumoGerencial;
    analise_categorias: CategoriaGerencial[];
    tendencias: TendenciaGerencial;
    indicadores: IndicadoresGerenciais;
    recomendacoes: Recomendacao[];
  }
  
  // Interfaces para o Dashboard Consolidado
  export interface PeriodoConsolidado {
    inicio: string;
    fim: string;
    dias: number;
  }
  
  export interface VisaoGeral {
    total_lancamentos: number;
    total_entradas: number;
    total_saidas: number;
    percentual_realizado: number;
  }
  
  export interface MetricasConsolidadas {
    fluxo: {
      saldo_atual: number;
      previsao_proximos_dias: number;
    };
    operacional: {
      media_diaria_lancamentos: number;
      ticket_medio_entradas: number;
    };
    realizacao: {
      percentual_entradas: number;
      percentual_saidas: number;
    };
  }
  
  export interface Destaque {
    data: string;
    descricao: string;
    valor: number;
    categoria: string;
  }
  
  export interface Destaques {
    maiores_entradas: Destaque[];
    maiores_saidas: Destaque[];
    categorias_relevantes: Array<{
      categoria: string;
      total: number;
    }>;
    dias_relevantes: Array<{
      data_ref: string;
      total: number;
    }>;
  }
  
  export interface Comparativos {
    periodo_anterior: {
      total_lancamentos: number;
      total_entradas: number;
      total_saidas: number;
    };
    variacoes: {
      quantidade: number;
      entradas: number;
      saidas: number;
    };
  }
  
  export interface DashboardConsolidado {
    periodo: PeriodoConsolidado;
    visao_geral: VisaoGeral;
    metricas: MetricasConsolidadas;
    destaques: Destaques;
    comparativos: Comparativos;
  }
  
  // Interfaces para o Dashboard Estratégico
export interface Dre {
  receita_bruta: number;
  receita_liquida: number;
  custos_operacionais: number;
  despesas_operacionais: number;
  resultado_operacional: number;
  resultado_antes_impostos: number;
  impostos: number;
  resultado_liquido: number;
}

export interface Tendencia {
  periodo: string;
  valor_realizado: number;
  valor_previsto: number;
}

export interface Projecao {
  entradas_total: number;
  saidas_total: number;
  saldo_projetado: number;
}

export interface IndicadoresEstrategicos {
  liquidez_imediata: number;
  ciclo_caixa: number;
  margem_operacional: number;
  crescimento_receitas: number;
}

export interface DashboardEstrategico {
  dre: Dre;
  tendencias: {
      receitas: Tendencia[];
      despesas: Tendencia[];
  };
  projecoes: {
      proximos_30_dias: Projecao;
      proximos_90_dias: Projecao;
      proximos_180_dias: Projecao;
  };
  indicadores: IndicadoresEstrategicos;
}