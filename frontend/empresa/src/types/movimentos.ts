type MovimentoTipo = 'entrada' | 'saida';
type MovimentoFonte = 'contrato' | 'conta_receber' | 'conta_pagar' | 'outro';
type MovimentoStatus = 'realizado' | 'previsto' | 'cancelado';

interface Movimento {
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
    data_estorno?: string;
    observacoes?: string;
}