// Interfaces para os dados de contratos
export interface Cliente {
  id: number;
  nome: string;
}

export interface Categoria {
  id: number;
  nome: string;
}

export interface ContratoLocacao {
  id: number;
  cliente: Cliente;
  contrato: string;
  tipocontrato: number;
  renovado: string;
  totalmaquinas: number;
  valorcontrato: number;
  numeroparcelas: number;
  valorpacela: number;
  data: string;
  inicio: string;
  fim: string;
}

export interface ItemContratoLocacao {
  id: number;
  numeroserie: string;
  modelo: string;
  inicio: string;
  fim: string;
  categoria: Categoria;
}

export interface ContratosResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ContratoLocacao[];
}

export interface ContratoDetalhado extends ContratoLocacao {
  itens?: ItemContratoLocacao[];
  totalItens?: number;
}

export interface FiltrosContratos {
  cliente?: string;
  contrato?: string;
  status?: 'ativo' | 'inativo' | 'todos';
  dataInicio?: string;
  dataFim?: string;
  valorMin?: number;
  valorMax?: number;
  renovado?: string;
}

export interface ContratosDashboard {
  totalContratos: number;
  contratosAtivos: number;
  contratosInativos: number;
  totalMaquinas: number;
  valorTotalContratos: number;
  valorMedioContrato: number;
  distribuicaoTipos: Array<{
    tipo: number;
    quantidade: number;
    valorTotal: number;
  }>;
  evolutionMensal: Array<{
    mes: string;
    novosContratos: number;
    renovacoes: number;
    valor: number;
  }>;
}
