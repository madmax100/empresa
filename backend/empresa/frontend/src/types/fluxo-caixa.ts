// Tipos para o fluxo de caixa realizado
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

export interface ResumoFluxoRealizado {
  total_entradas: number;
  total_saidas: number;
  saldo_liquido: number;
  total_movimentacoes: number;
}

export interface MovimentacoesRealizadasResponse {
  periodo: {
    data_inicio: string;
    data_fim: string;
  };
  resumo: ResumoFluxoRealizado;
  movimentacoes: MovimentacaoRealizada[];
}

// Resumo mensal
export interface ResumoMensal {
  mes: string;
  entradas: number;
  saidas: number;
  saldo_liquido: number;
  qtd_entradas: number;
  qtd_saidas: number;
}

export interface ResumoMensalResponse {
  periodo: {
    data_inicio: string;
    data_fim: string;
  };
  totais: {
    total_entradas: number;
    total_saidas: number;
    saldo_liquido: number;
  };
  resumo_mensal: ResumoMensal[];
}

// Movimentações com vencimento em aberto
export interface MovimentacaoVencimentoAberto {
  id: string;
  tipo: 'entrada_pendente' | 'saida_pendente';
  data_emissao: string;
  data_vencimento: string;
  valor: number;
  contraparte: string;
  historico: string;
  forma_pagamento: string;
  origem: 'contas_receber' | 'contas_pagar';
  dias_vencimento: number;
  status_vencimento: 'no_prazo' | 'vence_em_breve' | 'vencido';
}

export interface EstatisticasVencimento {
  no_prazo: {
    entradas: number;
    saidas: number;
    qtd_entradas: number;
    qtd_saidas: number;
  };
  vence_em_breve: {
    entradas: number;
    saidas: number;
    qtd_entradas: number;
    qtd_saidas: number;
  };
  vencido: {
    entradas: number;
    saidas: number;
    qtd_entradas: number;
    qtd_saidas: number;
  };
}

export interface MovimentacoesVencimentoAbertoResponse {
  periodo: {
    data_inicio: string;
    data_fim: string;
  };
  resumo: {
    total_entradas_pendentes: number;
    total_saidas_pendentes: number;
    saldo_liquido_pendente: number;
    total_movimentacoes: number;
  };
  estatisticas_vencimento: EstatisticasVencimento;
  movimentacoes_abertas: MovimentacaoVencimentoAberto[];
}

// Comparativo realizado vs previsto
export interface ComparativoRealizadoVsPrevistoResponse {
  periodo: {
    data_inicio: string;
    data_fim: string;
  };
  realizado: {
    entradas: number;
    saidas: number;
    saldo_liquido: number;
    qtd_contas_recebidas: number;
    qtd_contas_pagas: number;
  };
  previsto: {
    entradas: number;
    saidas: number;
    saldo_liquido: number;
    qtd_contas_a_receber: number;
    qtd_contas_a_pagar: number;
  };
  analise: {
    diferenca_entradas: number;
    diferenca_saidas: number;
    diferenca_saldo: number;
    percentual_realizacao_entradas: number;
    percentual_realizacao_saidas: number;
  };
}

// Filtros para consultas
export interface FiltrosPeriodo {
  data_inicio: string;
  data_fim: string;
}

export interface FiltrosFluxoRealizado extends FiltrosPeriodo {
  tipo?: 'entrada' | 'saida' | 'todos';
  status_vencimento?: 'no_prazo' | 'vence_em_breve' | 'vencido' | 'todos';
}

// Estados da aplicação
export interface DashboardState {
  loading: boolean;
  error: string | null;
  movimentacoesRealizadas: MovimentacoesRealizadasResponse | null;
  resumoMensal: ResumoMensalResponse | null;
  movimentacoesVencimentoAberto: MovimentacoesVencimentoAbertoResponse | null;
  comparativoRealizadoVsPrevisto: ComparativoRealizadoVsPrevistoResponse | null;
}
