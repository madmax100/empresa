// Serviço para API de contratos de locação
export interface ContratoDashboard {
  id: number;
  contrato: string;
  cliente: {
    id: number;
    nome: string;
  };
  valorcontrato: number;
  valorpacela: number;
  numeroparcelas: number;
  tipocontrato: string;
  inicio: string;
  fim: string;
  renovado: string;
  total_recebido?: number;
  total_gasto?: number;
  margem?: number;
  totalMaquinas?: number;
  status?: string;
  data?: string;
}

export interface ItemContrato {
  id: number;
  modelo: string;
  numeroserie: string;
  categoria: {
    id: number;
    nome: string;
  };
  inicio: string;
  fim: string;
  custo_unitario?: number;
  custo_total?: number;
  quantidade?: number;
}

export interface ContratoFinanceiro {
  contrato: ContratoDashboard;
  itens: ItemContrato[];
  total_recebido: number;
  total_gasto: number;
  margem: number;
}

export interface SuprimentoDetalhado {
  id: number;
  numero_nota: string;
  data: string;
  valor_total_nota: number;
  operacao: string;
  cfop: string;
  obs?: string;
}

export interface SuprimentosResponse {
  resultados: Array<{
    contrato_id: number;
    contrato_numero: string;
    cliente: {
      id: number;
      nome: string;
    };
    suprimentos: {
      quantidade_notas: number;
      notas: SuprimentoDetalhado[];
    };
  }>;
}

class ContratosService {
  private baseURL = '/api';

  // Buscar todos os contratos - compatibilidade com ContractsDashboardGrouped
  async listar(): Promise<ContratoDashboard[]> {
    return this.buscarContratos();
  }

  // Buscar todos os contratos
  async buscarContratos(): Promise<ContratoDashboard[]> {
    try {
      const response = await fetch(`${this.baseURL}/contratos_locacao/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar contratos: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar contratos:', error);
      throw error;
    }
  }

  // Buscar detalhes do dashboard de um contrato específico
  async buscarDashboardContrato(numeroContrato: string): Promise<ContratoDashboard> {
    try {
      const response = await fetch(`${this.baseURL}/contratos_locacao/dashboard/${numeroContrato}/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar dashboard do contrato: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar dashboard do contrato:', error);
      throw error;
    }
  }

  // Buscar itens de um contrato específico
  async buscarItensContrato(numeroContrato: string): Promise<ItemContrato[]> {
    try {
      const response = await fetch(`${this.baseURL}/contratos_locacao/itens/${numeroContrato}/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar itens do contrato: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar itens do contrato:', error);
      throw error;
    }
  }

  // Buscar detalhes de um contrato específico
  async buscarContratoDetalhes(id: number): Promise<ContratoDashboard> {
    try {
      const response = await fetch(`${this.baseURL}/contratos_locacao/${id}/`);
      if (!response.ok) {
        throw new Error(`Erro ao buscar detalhes do contrato: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar detalhes do contrato:', error);
      throw error;
    }
  }

  // Buscar dados financeiros consolidados (combinando dados de múltiplos endpoints)
  async buscarDadosFinanceiros(dataInicio?: string, dataFim?: string): Promise<ContratoFinanceiro[]> {
    try {
      // Primeiro buscar todos os contratos
      const contratos = await this.buscarContratos();
      
      // Filtrar por período se fornecido
      const contratosFiltrados = contratos.filter(contrato => {
        if (!dataInicio && !dataFim) return true;
        
        const inicioContrato = new Date(contrato.inicio);
        const fimContrato = new Date(contrato.fim);
        
        if (dataInicio && dataFim) {
          const inicio = new Date(dataInicio);
          const fim = new Date(dataFim);
          return (inicioContrato >= inicio && inicioContrato <= fim) ||
                 (fimContrato >= inicio && fimContrato <= fim) ||
                 (inicioContrato <= inicio && fimContrato >= fim);
        }
        
        return true;
      });

      // Para cada contrato, buscar dados do dashboard e itens
      const dadosFinanceiros: ContratoFinanceiro[] = [];
      
      for (const contrato of contratosFiltrados) {
        try {
          let dashboardData = null;
          let itens: ItemContrato[] = [];
          
          // Tentar buscar dashboard, mas não falhar se não conseguir
          try {
            dashboardData = await this.buscarDashboardContrato(contrato.contrato);
          } catch (dashboardError) {
            console.warn(`Não foi possível buscar dashboard do contrato ${contrato.contrato}:`, dashboardError);
          }
          
          // Tentar buscar itens, mas não falhar se não conseguir
          try {
            itens = await this.buscarItensContrato(contrato.contrato);
          } catch (itensError) {
            console.warn(`Não foi possível buscar itens do contrato ${contrato.contrato}:`, itensError);
            // Se não conseguir buscar os itens, usar array vazio
            itens = [];
          }
          
          // Calcular valores financeiros - usar dados do dashboard se disponível, senão usar do contrato
          const totalRecebido = dashboardData?.total_recebido || contrato.valorcontrato || 0;
          const totalGasto = dashboardData?.total_gasto || itens.reduce((sum, item) => {
            return sum + (item.custo_total || item.custo_unitario || 0);
          }, 0);
          const margem = totalRecebido > 0 ? ((totalRecebido - totalGasto) / totalRecebido) * 100 : 0;
          
          dadosFinanceiros.push({
            contrato: {
              ...contrato,
              total_recebido: totalRecebido,
              total_gasto: totalGasto,
              margem: margem
            },
            itens,
            total_recebido: totalRecebido,
            total_gasto: totalGasto,
            margem: margem
          });
        } catch (error) {
          console.error(`Erro geral ao processar contrato ${contrato.contrato}:`, error);
          
          // Mesmo em caso de erro total, incluir dados básicos do contrato
          const totalRecebido = contrato.valorcontrato || 0;
          const totalGasto = 0; // Se não conseguimos buscar, assumir 0
          const margem = 0;
          
          dadosFinanceiros.push({
            contrato: {
              ...contrato,
              total_recebido: totalRecebido,
              total_gasto: totalGasto,
              margem: margem
            },
            itens: [],
            total_recebido: totalRecebido,
            total_gasto: totalGasto,
            margem: margem
          });
        }
      }
      
      return dadosFinanceiros;
    } catch (error) {
      console.error('Erro ao buscar dados financeiros:', error);
      throw error;
    }
  }

  // Buscar suprimentos com filtros
  async buscarSuprimentos(filtros: {
    data_inicial: string;
    data_final: string;
    contrato_id?: string;
    cliente_id?: string;
  }): Promise<SuprimentosResponse> {
    try {
      const params = new URLSearchParams();
      params.append('data_inicial', filtros.data_inicial);
      params.append('data_final', filtros.data_final);
      
      if (filtros.contrato_id) {
        params.append('contrato_id', filtros.contrato_id);
      }
      
      if (filtros.cliente_id) {
        params.append('cliente_id', filtros.cliente_id);
      }

      const response = await fetch(`${this.baseURL}/contratos_locacao/suprimentos/?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar suprimentos: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar suprimentos:', error);
      throw error;
    }
  }
}

export const contratosService = new ContratosService();
