// src/types/models.ts

import { NotaFiscalSaida } from "./notas_fiscais/models";

// Interfaces Base
export interface BaseEntity {
    id: number;
    created_at?: string;
    updated_at?: string;
}

// Produto e Relacionados
export interface Produto extends BaseEntity {
    codigo: string;
    nome: string;
    descricao?: string;
    preco_custo?: number;
    preco_venda?: number;
    estoque_atual?: number;
    ativo?: boolean;
    unidade_medida?: string;
    categoria?: {
        id: number;
        nome: string;
    };
}

export interface BasePessoa {
    id: number;
    nome: string;
    cpf_cnpj: string;
    tipo_pessoa?: 'F' | 'J';
}

// Cliente e Fornecedor
export interface Fornecedor extends BaseEntity {
    tipo_pessoa: 'F' | 'J';
    nome: string;
    cpf_cnpj: string;
    rg_ie?: string;
    data_nascimento?: string | null;
    endereco?: string;
    numero?: string | null;
    complemento?: string | null;
    bairro?: string;
    cidade?: string;
    estado?: string;
    cep?: string;
    telefone?: string;
    email?: string;
    limite_credito?: string;
    data_cadastro?: string;
    ativo?: boolean;
    contato?: string;
}

export interface Cliente extends BaseEntity {
    tipo_pessoa: 'F' | 'J';
    nome: string;
    cpf_cnpj: string;
    rg_ie?: string;
    data_nascimento?: string | null;
    endereco?: string;
    numero?: string | null;
    complemento?: string | null;
    bairro?: string;
    cidade?: string;
    estado?: string;
    cep?: string;
    telefone?: string;
    email?: string;
    limite_credito?: string;
    data_cadastro?: string;
    ativo?: boolean;
    contato?: string;
}



// Contratos
export interface ItemContrato {
    id: number;
    numeroserie?: string;
    modelo: string;
    inicio?: string;
    fim?: string;
    categoria?: {
        id: number;
        nome: string;
    };
}

export interface Contrato {
    id: number;
    contrato: string;
    cliente?: Cliente;
    tipocontrato?: string;
    valorcontrato?: number;
    valorpacela?: number;
    data?: string;
    inicio?: string;
    fim?: string;
    totalMaquinas?: string;
    status?: string;
}


// Contas
interface TituloBase extends BaseEntity {
    historico: string;
    valor: string;
    vencimento: string;
    data_pagamento: string | null;
    status: 'A' | 'P' | 'C';
    valor_total_pago: string;
    forma_pagamento: string;
}

export interface TituloReceber extends TituloBase {
    cliente: Cliente;
}

export interface TituloPagar extends TituloBase {
    fornecedor: Fornecedor;
}

// Resumos Financeiros
export interface ResumoFinanceiro {
    total_atrasado: number;
    total_pago_periodo: number;
    total_cancelado_periodo: number;
    total_aberto_periodo: number;
    quantidade_titulos: number;
    quantidade_atrasados_periodo: number;
}

// Respostas da API
export interface ContasReceberResponse {
    resumo: ResumoFinanceiro;
    titulos_atrasados: TituloReceber[];
    titulos_pagos_periodo: TituloReceber[];
    titulos_abertos_periodo: TituloReceber[];
}

export interface ContasPagarResponse {
    resumo: ResumoFinanceiro;
    titulos_atrasados: TituloPagar[];
    titulos_pagos_periodo: TituloPagar[];
    titulos_abertos_periodo: TituloPagar[];
}



// Dashboard e Filtros
export interface DashboardData {
    contasReceber: ContasReceberResponse;
    contasPagar: ContasPagarResponse;
    saldo: {
        total_atrasado: number;
        total_pago_periodo: number;
        total_cancelado_periodo: number;
        total_aberto_periodo: number;
        quantidade_titulos: number;
        quantidade_atrasados: number;
    };
}

export interface FilterParams {
    dataInicial: string;
    dataFinal: string;
    status: 'all' | 'A' | 'P' | 'C';
    searchTerm?: string;
}

// Status
export type StatusConta = 'all' | 'A' | 'P' | 'C';

export interface StatusOption {
    value: StatusConta;
    label: string;
}

export const STATUS_OPTIONS: StatusOption[] = [
    { value: 'all', label: 'Todos' },
    { value: 'A', label: 'Em Aberto' },
    { value: 'P', label: 'Pago' },
    { value: 'C', label: 'Cancelado' }
];

export interface DashboardResponse {
    contasReceber: ContasReceberResponse;
    contasPagar: ContasPagarResponse;
    saldo: {
        total_atrasado: number;
        total_pago_periodo: number;
        total_cancelado_periodo: number;
        total_aberto_periodo: number;
        quantidade_titulos: number;
        quantidade_atrasados: number;
    };
}

export interface Bill {
    id: number;
    vencimento: string;
    valor: number;
    status: 'A' | 'P' | 'C';
    cliente?: {
        id: number;
        nome: string;
    };
    fornecedor?: {
        id: number;
        nome: string;
    };
}

export interface FilterParams2 {
    dataInicial?: string;
    dataFinal?: string;
    status?: string;
    searchTerm?: string;
};

export interface PaymentData {
    status: string;
    data_pagamento: string;
    forma_pagamento: string;
    valor_pago: number;
}

export interface DashboardResponse2 {
    resumo: {
        total_atrasado: number;
        total_pago_periodo: number;
        total_cancelado_periodo: number;
        total_aberto_periodo: number;
        quantidade_titulos: number;
        quantidade_atrasados_periodo: number;
    };
    titulos_atrasados: Bill[];
    titulos_pagos_periodo: Bill[];
    titulos_abertos_periodo: Bill[];
}

export interface Titulo {
    id: number;
    historico: string;
    valor: string;
    vencimento: string;
    status: string;
}

export interface ResumoCliente {
    cliente: {
        id: number;
        nome: string;
        cpf_cnpj: string;
    };
    totalReceber: number;
    totalPagar: number;
    saldo: number;
    quantidadeTitulos: number;
    titulosReceber: Titulo[];
    titulosPagar: Titulo[];
    expandido?: boolean;
}

export interface ResumoDashboard {
    total_valor: number;
    total_recebido: number;
    quantidade_notas: number;
}

export interface DashboardFiltros {
    data_inicial?: string;
    data_final?: string;
}

export interface DashboardContrato {
    contrato: string;
    itens: ItemContrato[];
    notas_fiscais: {
        resumo: {
            total_valor: number;
            total_recebido: number;
            quantidade_notas: number;
        };
        notas: NotaFiscalSaida[];
    };
    periodo: {
        data_inicial: string;
        data_final: string;
    };
}

export interface ContratoExpandido extends Contrato {
    expandido?: boolean;
    loading?: boolean;
    error?: string;
    itens?: ItemContrato[];
    contasReceber: ContasReceberResponse;
    dashboard?: DashboardContrato;
    notas_fiscais?: {
        resumo: {
            total_valor: number;
            quantidade_notas: number;
        };
        notas: NotaFiscalSaida[];
    };
    periodo?: {
        data_inicial: string;
        data_final: string;
    };
}
