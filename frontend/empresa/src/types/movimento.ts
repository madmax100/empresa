// types/movimento.ts
export type MovimentoTipo = 'entrada' | 'saida';
export type MovimentoStatus = 'realizado' | 'previsto' | 'cancelado';
export type MovimentoFonte = 'contrato' | 'conta_receber' | 'conta_pagar' | 'outro';

export interface Movimento {
    id: number;
    data: string;
    tipo: MovimentoTipo;
    valor: number;
    realizado: boolean;
    status: MovimentoStatus;
    descricao: string;
    categoria: string;
    fonte: {
        tipo: MovimentoFonte;
        id: number;
        referencia?: string;
    };
    observacoes?: string;
}



