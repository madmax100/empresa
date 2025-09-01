// Tipos de Dashboard
interface DashboardBase {
    periodo: BasePeriodo;
    totalizadores: {
        entradas_realizadas: BaseValores;
        entradas_previstas: BaseValores;
        saidas_realizadas: BaseValores;
        saidas_previstas: BaseValores;
        saldo_realizado: number;
        saldo_projetado: number;
    };
}

interface DashboardOperacional extends DashboardBase {
    filtros: FluxoCaixaFiltros;
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
    categorias: Record<string, {
        entradas: number;
        saidas: number;
        quantidade: number;
        saldo: number;
    }>;
    movimentos: Movimento[];
}

interface DashboardEstrategico extends DashboardBase {
    dre: {
        receita_bruta: number;
        receita_liquida: number;
        resultado_operacional: number;
        resultado_liquido: number;
    };
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
}