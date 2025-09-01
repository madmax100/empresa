import { MovimentoFonte, MovimentoStatus, MovimentoTipo } from "./movimento";

// types/filters.ts
export interface FluxoCaixaFiltros {
    dataInicial: string;
    dataFinal: string;
    tipo?: MovimentoTipo | 'todos';
    fonte?: MovimentoFonte | 'todos';
    status?: MovimentoStatus | 'todos';
    categoria?: string;
    searchTerm?: string;
}