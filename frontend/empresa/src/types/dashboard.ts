import { FluxoCaixaFiltros } from "./filters";
import { Movimento } from "./movimento";

// types/dashboard.ts
export interface Totalizador {
    valor: number;
    quantidade: number;
    percentual?: number;
}

export interface Totalizadores {
    entradas_realizadas: Totalizador;
    entradas_previstas: Totalizador;
    saidas_realizadas: Totalizador;
    saidas_previstas: Totalizador;
    saldo_realizado: number;
    saldo_previsto: number;
}

export interface EvolucaoDiaria {
    data: string;
    entradas: number;
    saidas: number;
    saldo: number;
}

export interface CategoriaTotais {
    entradas: number;
    saidas: number;
    saldo: number;
    quantidade: number;
}

export interface DREResumo {
    receita_bruta: number;
    deducoes: number;
    receita_liquida: number;
    custos_operacionais: number;
    despesas_operacionais: number;
    resultado_operacional: number;
    receitas_financeiras: number;
    despesas_financeiras: number;
    resultado_antes_impostos: number;
    impostos: number;
    resultado_liquido: number;
}

export interface FluxoCaixaResumo {
    saldo_inicial: number;
    saldo_final: number;
    saldo_projetado: number;
    variacao_percentual: number;
    entradas_total: number;
    saidas_total: number;
    // Propriedades específicas do negócio
    vendas_equipamentos: number;
    alugueis_ativos: number;
    contratos_renovados: number;
    servicos_total: number;
    suprimentos_total: number;
}

export interface TendenciaAnalise {
    periodo: string;
    valor_realizado: number;
    valor_previsto: number;
    variacao_percentual: number;
    tendencia: 'alta' | 'baixa' | 'estavel';
}

// Interfaces principais para os diferentes dashboards
export interface DashboardOperacional {
    filtros: FluxoCaixaFiltros;
    resumo: FluxoCaixaResumo;
    movimentos: Movimento[];
    totalizadores: Totalizadores;
    evolucao_diaria: EvolucaoDiaria[];
    categorias: Record<string, CategoriaTotais>;
}

export interface DashboardEstrategico {
    dre: DREResumo;
    tendencias: {
        receitas: TendenciaAnalise[];
        despesas: TendenciaAnalise[];
        saldos: TendenciaAnalise[];
    };
    projecoes: {
        proximos_30_dias: FluxoCaixaResumo;
        proximos_90_dias: FluxoCaixaResumo;
        proximos_180_dias: FluxoCaixaResumo;
    };
    indicadores: {
        liquidez_imediata: number;
        ciclo_caixa: number;
        margem_operacional: number;
        crescimento_receitas: number;
    };
}

export interface DashboardGerencial {
    filtros: FluxoCaixaFiltros;
    resumo_periodo: {
        anterior: FluxoCaixaResumo;
        atual: FluxoCaixaResumo;
        variacao: FluxoCaixaResumo;
    };
    evolucao_diaria: {
        data: string;
        entradas: number;
        saidas: number;
        saldo: number;
    }[];
    principais_receitas: {
        categoria: string;
        valor: number;
        percentual: number;
    }[];
    principais_despesas: {
        categoria: string;
        valor: number;
        percentual: number;
    }[];
    analise_categorias: Record<string, CategoriaTotais>;
    contratos_status: StatusContrato[];
    metricas_contratos: MetricasContratos;
    receita_por_tipo_contrato: ReceitaContrato[];
}

export interface MetricasContratos {
    taxa_renovacao: number;
    ticket_medio: number;
    tempo_medio_meses: number;
    total_ativos: number;
}

export interface StatusContrato {
    status: string;
    quantidade: number;
    valor_total: number;
}

export interface ReceitaContrato {
    tipo: string;
    valor_mensal: number;
    quantidade: number;
}