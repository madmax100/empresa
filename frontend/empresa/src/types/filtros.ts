// Tipos de Filtros
interface FluxoCaixaFiltros {
    dataInicial: string;
    dataFinal: string;
    tipo?: MovimentoTipo | 'todos';
    fonte?: MovimentoFonte | 'todos';
    status?: MovimentoStatus | 'todos';
    categoria?: string;
    searchTerm?: string;
}