// src/types/fluxo_caixa/models.ts

export interface FluxoCaixaMovimento {
    id: number;
    data: string;
    tipo: 'entrada' | 'saida';
    valor: number;
    realizado: boolean;
    descricao: string;
    categoria: string;
    fonte: {
        tipo: 'contrato' | 'conta_receber' | 'conta_pagar' | 'outro';
        id: number;
    };
    observacoes: string;
}

export interface FluxoCaixaDia {
    data: string;
    saldo_inicial: number;
    saldo_final: number;
    movimentos: FluxoCaixaMovimento[];
    total_entradas: number;
    total_saidas: number;
    saldo_realizado: number;
    saldo_projetado: number;
}

export interface FluxoCaixaSemana {
    inicio: string;
    fim: string;
    dias: FluxoCaixaDia[];
    total_entradas: number;
    total_saidas: number;
    saldo_realizado: number;
    saldo_projetado: number;
}

export interface FluxoCaixaMes {
    mes: string;
    ano: number;
    semanas: FluxoCaixaSemana[];
    total_entradas: number;
    total_saidas: number;
    saldo_realizado: number;
    saldo_projetado: number;
}



export interface FluxoCaixaResponse {
    periodo: {
        inicio: string;
        fim: string;
    };
    saldo_inicial: number;
    saldo_final_realizado: number;
    saldo_final_projetado: number;
    meses: FluxoCaixaMes[];
    totalizadores: {
        entradas_realizadas: number;
        entradas_previstas: number;
        saidas_realizadas: number;
        saidas_previstas: number;
        saldo_realizado: number;
        saldo_projetado: number;
    };
}

// types.ts
export interface DateRange {
    inicio: Date;
    fim: Date;
  }
  
  export interface FinancialMetrics {
    saldo_atual: number;
    entradas_mes: number;
    saidas_mes: number;
    resultado_mes: number;
    indice_inadimplencia: number;
    indice_pontualidade: number;
  }
  
  export interface CashFlowEntry {
    data: Date;
    tipo: 'entrada' | 'saida';
    valor: number;
    descricao: string;
    categoria: string;
    realizado: boolean;
    cliente?: string;
    fornecedor?: string;
  }
  
  export interface CategoryAnalysis {
    categoria: string;
    entradas: number;
    saidas: number;
    quantidade: number;
    participacao: number;
  }
  
  export interface ContractAnalysis {
    total_contratos: number;
    valor_total: number;
    ticket_medio: number;
    distribuicao_categorias: CategoryAnalysis[];
  }
  
  export interface InventoryItem {
    codigo: string;
    nome: string;
    quantidade: number;
    valor_unitario: number;
    estoque_minimo: number;
    estoque_maximo: number;
  }
  
  export interface SalesAnalysis {
    valor_total: number;
    quantidade: number;
    ticket_medio: number;
    margem: number;
    produtos: {
      codigo: string;
      nome: string;
      quantidade: number;
      valor_total: number;
    }[];
  }