import { Cliente, Produto } from "../models";

// Interface principal da Nota Fiscal
export interface NotaFiscalSaida {
    // Identificação
    id: number;
    itens: ItemNotaFiscal[];
    numero_nota: string;
    data: string;  // ISO DateTime string
    cliente?: Cliente;

    // Valores
    valor_produtos: number;
    base_calculo: number;
    desconto: number;
    valor_frete: number;
    tipo_frete?: string;
    valor_icms: number;
    valor_ipi: number;
    valor_icms_fonte: number;
    valor_total_nota: number;
    imposto_federal_total: number;
    outras_despesas: number;
    seguro: number;

    // Informações de Pagamento
    forma_pagamento?: string;
    condicoes?: string;
    parcelas?: string;
    val_ref?: string;

    // Pessoas envolvidas
    //vendedor?: Funcionario;
    operador?: string;
    //transportadora?: Transportadora;

    // Informações de Transporte
    formulario?: string;
    peso?: number;
    volume?: number;

    // Informações Fiscais
    operacao?: string;
    cfop?: string;
    n_serie?: string;
    percentual_icms?: number;
    nf_referencia?: string;
    finalidade?: string;

    // Outros campos
    comissao?: number;
    obs?: string;
    detalhes?: string;
}

// Interface para resumo/listagem de notas
export interface NotaFiscalSaidaResumo {
    id: number;
    numero_nota: string;
    data: string;
    cliente?: {
        id: number;
        nome: string;
    };
    valor_total_nota: number;
    status?: string;
}

// Interface para filtros de busca
export interface NotaFiscalFiltros {
    data_inicial?: string;
    data_final?: string;
    cliente_id?: number;
    numero_nota?: string;
    vendedor_id?: number;
    status?: string;
}

// Interface para totalizadores
export interface NotaFiscalTotais {
    quantidade_notas: number;
    valor_total: number;
    valor_produtos: number;
    valor_impostos: number;
    valor_frete: number;
}

// Interface para resposta da API com paginação
export interface NotaFiscalResponse {
    count: number;
    next?: string | null;
    previous?: string | null;
    results: NotaFiscalSaida[];
    totais: NotaFiscalTotais;
}

// Interface para agrupamentos
export interface NotaFiscalAgrupamento {
    por_cliente: {
        [clienteId: number]: {
            cliente: {
                id: number;
                nome: string;
            };
            quantidade: number;
            valor_total: number;
        };
    };
    por_vendedor: {
        [vendedorId: number]: {
            vendedor: {
                id: number;
                nome: string;
            };
            quantidade: number;
            valor_total: number;
        };
    };
    por_mes: {
        [mes: string]: {
            quantidade: number;
            valor_total: number;
        };
    };
}

export interface ItemNotaFiscal {
    id: number;
    produto: Produto;
    quantidade: number;
    valor_unitario: number;
    valor_total: number;
    descricao?: string;
}

// Estenda a interface NotaFiscalSaida para incluir itens
export interface NotaFiscalSaidaDetalhada extends NotaFiscalSaida {
    itens: ItemNotaFiscal[];
}