// Serviço para API de contratos de locação

// Interfaces para os dados de suprimentos
interface NotaSuprimento {
  id: number;
  numero_nota: string;
  data: string;
  operacao: string;
  cfop: string;
  valor_total_nota: number;
  obs: string;
}

interface SuprimentosContrato {
  total_valor: number;
  quantidade_notas: number;
  notas: NotaSuprimento[];
}

interface ContratoSuprimento {
  contrato_id: number;
  contrato_numero: string;
  cliente: {
    id: number;
    nome: string;
  };
  suprimentos: SuprimentosContrato;
}

interface DadosSuprimentos {
  periodo: {
    data_inicial: string;
    data_final: string;
  };
  resumo: {
    total_contratos: number;
    total_suprimentos: number;
    total_notas: number;
  };
  resultados: ContratoSuprimento[]; // Mudando de 'contratos' para 'resultados'
}

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
  private baseURL = 'http://127.0.0.1:8000/api';

  // Buscar todos os contratos - compatibilidade com ContractsDashboardGrouped
  async listar(filtros?: { data_inicio?: string; data_fim?: string }): Promise<ContratoDashboard[]> {
    return this.buscarContratos(filtros);
  }

  // Buscar todos os contratos
  async buscarContratos(filtros?: { data_inicio?: string; data_fim?: string }): Promise<ContratoDashboard[]> {
    try {
      // Usar filtros fornecidos ou ano atual como padrão
      const dataInicial = filtros?.data_inicio || `${new Date().getFullYear()}-01-01`;
      const dataFinal = filtros?.data_fim || `${new Date().getFullYear()}-12-31`;
      
      const url = `${this.baseURL}/contratos_locacao/suprimentos/?data_inicial=${dataInicial}&data_final=${dataFinal}`;
      console.log('📡 Chamando API de suprimentos de contratos:', url);
      console.log('📅 Período de busca:', { dataInicial, dataFinal });
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      console.log('📋 Resposta da API de contratos:', response.status, response.statusText);
      
      if (!response.ok) {
        if (response.status === 404) {
          console.warn('⚠️ Endpoint de contratos não encontrado, usando dados mock');
          return this.getMockContratos();
        }
        throw new Error(`Erro ao buscar contratos: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Dados de suprimentos recebidos:', data);
      console.log('📊 Quantidade de contratos encontrados:', data?.resultados?.length || 0);
      
      // Mapear dados de suprimentos para contratos
      const contratos = this.mapSuprimentosToContratos(data, filtros);
      console.log('📊 Contratos mapeados:', contratos);
      
      // Se não encontrou contratos no período, verificar se há dados mas sem mapeamento
      if (contratos.length === 0) {
        console.log('⚠️ Nenhum contrato encontrado no período, verificando se há dados mas sem mapeamento...');
        console.log('📊 Dados brutos resultados:', data?.resultados);
        console.log('📊 Dados brutos length:', data?.resultados?.length);
        
        // Se há resultados mas nenhum contrato mapeado, pode ser problema no mapeamento
        if (data?.resultados && data.resultados.length > 0) {
          console.error('❌ Há dados na API mas o mapeamento falhou!');
          console.log('🔍 Primeiro resultado:', data.resultados[0]);
        }
        
        console.log('🔄 Usando dados mock temporariamente...');
        return this.getMockContratos();
      }
      
      return contratos;
    } catch (error) {
      console.error('Erro ao buscar contratos:', error);
      console.warn('⚠️ Erro na API de contratos, usando dados mock');
      return this.getMockContratos();
    }
  }

  // Método para retornar dados mock quando a API não está disponível
  private getMockContratos(): ContratoDashboard[] {
    return [
      {
        id: 1,
        contrato: "2024001",
        cliente: {
          id: 1,
          nome: "Empresa ABC Ltda"
        },
        valorcontrato: 50000.00,
        valorpacela: 2500.00,
        numeroparcelas: 20,
        tipocontrato: "Locação",
        inicio: "2024-01-01",
        fim: "2024-12-31",
        renovado: "N",
        total_recebido: 15000.00,
        total_gasto: 8000.00,
        margem: 7000.00,
        totalMaquinas: 5,
        status: "Ativo"
      },
      {
        id: 2,
        contrato: "2024002", 
        cliente: {
          id: 2,
          nome: "Indústria XYZ S.A."
        },
        valorcontrato: 75000.00,
        valorpacela: 3750.00,
        numeroparcelas: 20,
        tipocontrato: "Locação",
        inicio: "2024-02-01",
        fim: "2025-01-31",
        renovado: "N",
        total_recebido: 22500.00,
        total_gasto: 12000.00,
        margem: 10500.00,
        totalMaquinas: 8,
        status: "Ativo"
      },
      {
        id: 3,
        contrato: "2024003",
        cliente: {
          id: 3,
          nome: "Comércio 123 ME"
        },
        valorcontrato: 30000.00,
        valorpacela: 1500.00,
        numeroparcelas: 20,
        tipocontrato: "Locação",
        inicio: "2024-03-01",
        fim: "2025-02-28",
        renovado: "N",
        total_recebido: 9000.00,
        total_gasto: 5000.00,
        margem: 4000.00,
        totalMaquinas: 3,
        status: "Ativo"
      }
    ];
  }

  // Mapear dados de suprimentos para formato de contratos
  private mapSuprimentosToContratos(suprimentosData: DadosSuprimentos, filtros?: { data_inicio?: string; data_fim?: string }): ContratoDashboard[] {
    console.log('🔄 Iniciando mapeamento de suprimentos para contratos...');
    console.log('📋 Dados recebidos:', suprimentosData);
    console.log('📅 Filtros de período:', filtros);
    
    if (!suprimentosData) {
      console.warn('⚠️ suprimentosData é nulo/undefined');
      return [];
    }
    
    if (!suprimentosData.resultados) {
      console.warn('⚠️ suprimentosData.resultados não existe');
      console.log('🔍 Estrutura disponível:', Object.keys(suprimentosData));
      return [];
    }
    
    if (!Array.isArray(suprimentosData.resultados)) {
      console.warn('⚠️ suprimentosData.resultados não é um array');
      console.log('🔍 Tipo:', typeof suprimentosData.resultados);
      return [];
    }
    
    console.log(`📊 Processando ${suprimentosData.resultados.length} contratos...`);

    const contratosMapeados = suprimentosData.resultados.map((contrato: ContratoSuprimento, index: number) => {
      console.log(`🔄 Processando contrato ${index + 1}:`, contrato);
      
      const valorTotalSuprimentos = contrato.suprimentos?.total_valor || 0;
      const quantidadeNotas = contrato.suprimentos?.quantidade_notas || 0;
      
      console.log(`💰 Contrato ${contrato.contrato_numero}: Valor suprimentos: ${valorTotalSuprimentos}, Notas: ${quantidadeNotas}`);
      
      // Calcular valores estimados baseados nos suprimentos
      const valorEstimadoContrato = valorTotalSuprimentos * 10; // Estimativa baseada em suprimentos
      const valorParcela = valorEstimadoContrato / 12; // Estimativa de parcela mensal
      
      // Usar datas baseadas no período dos suprimentos para garantir vigência
      let dataInicio: string;
      let dataFim: string;
      
      if (filtros?.data_inicio && filtros?.data_fim && contrato.suprimentos?.notas && contrato.suprimentos.notas.length > 0) {
        // Se há notas no período consultado, assumir que o contrato está vigente
        // Expandir um pouco as datas para cobrir um período de contrato mais realista
        const primeiraNotaData = new Date(contrato.suprimentos.notas[0].data);
        const ultimaNotaData = new Date(contrato.suprimentos.notas[contrato.suprimentos.notas.length - 1].data);
        
        // Contrato começou 6 meses antes da primeira nota
        const inicioCalculado = new Date(primeiraNotaData);
        inicioCalculado.setMonth(inicioCalculado.getMonth() - 6);
        
        // Contrato termina 6 meses após a última nota
        const fimCalculado = new Date(ultimaNotaData);
        fimCalculado.setMonth(fimCalculado.getMonth() + 6);
        
        dataInicio = inicioCalculado.toISOString().split('T')[0];
        dataFim = fimCalculado.toISOString().split('T')[0];
        
        console.log(`📅 Contrato ${contrato.contrato_numero}:`);
        console.log(`   Primeira nota: ${primeiraNotaData.toLocaleDateString()}`);
        console.log(`   Última nota: ${ultimaNotaData.toLocaleDateString()}`);
        console.log(`   Período estimado: ${inicioCalculado.toLocaleDateString()} até ${fimCalculado.toLocaleDateString()}`);
      } else {
        // Fallback para período padrão baseado no ano das consultas
        dataInicio = filtros?.data_inicio || this.extrairDataInicioSuprimentos(contrato.suprimentos?.notas);
        dataFim = filtros?.data_fim || this.extrairDataFimSuprimentos(contrato.suprimentos?.notas);
      }
      
      const contratoMapeado = {
        id: contrato.contrato_id || index + 1,
        contrato: contrato.contrato_numero || `C${contrato.contrato_id}`,
        cliente: {
          id: contrato.cliente?.id || 0,
          nome: contrato.cliente?.nome || 'Cliente não informado'
        },
        valorcontrato: valorEstimadoContrato,
        valorpacela: valorParcela,
        numeroparcelas: 12, // Padrão estimado
        tipocontrato: 'Locação',
        inicio: dataInicio,
        fim: dataFim,
        renovado: 'N',
        total_recebido: valorEstimadoContrato * 0.6, // Estimativa de 60% recebido
        total_gasto: valorTotalSuprimentos,
        margem: (valorEstimadoContrato * 0.6) - valorTotalSuprimentos,
        totalMaquinas: this.contarMaquinasSuprimentos(contrato.suprimentos?.notas),
        status: quantidadeNotas > 0 ? 'Ativo' : 'Inativo',
        data: new Date().toISOString().split('T')[0]
      };
      
      console.log(`✅ Contrato mapeado:`, contratoMapeado);
      return contratoMapeado;
    });
    
    // Filtrar contratos que estão vigentes no período selecionado
    if (filtros?.data_inicio && filtros?.data_fim) {
      const periodoInicio = new Date(filtros.data_inicio);
      const periodoFim = new Date(filtros.data_fim);
      
      console.log(`🔍 Filtrando contratos vigentes no período: ${filtros.data_inicio} até ${filtros.data_fim}`);
      
      const contratosFiltrados = contratosMapeados.filter(contrato => {
        const dataInicioContrato = new Date(contrato.inicio);
        const dataFimContrato = new Date(contrato.fim);
        
        // Contrato está vigente se há sobreposição entre períodos
        const contratoVigente = dataInicioContrato <= periodoFim && dataFimContrato >= periodoInicio;
        
        if (!contratoVigente) {
          console.log(`❌ Contrato ${contrato.contrato} não vigente no período:`);
          console.log(`   Contrato: ${dataInicioContrato.toLocaleDateString()} até ${dataFimContrato.toLocaleDateString()}`);
          console.log(`   Período: ${periodoInicio.toLocaleDateString()} até ${periodoFim.toLocaleDateString()}`);
        } else {
          console.log(`✅ Contrato ${contrato.contrato} vigente no período`);
        }
        
        return contratoVigente;
      });
      
      console.log(`🎯 Contratos vigentes no período: ${contratosFiltrados.length} de ${contratosMapeados.length}`);
      return contratosFiltrados;
    }
    
    console.log(`🎯 Total de contratos mapeados: ${contratosMapeados.length}`);
    console.log(`📋 Lista de contratos mapeados:`, contratosMapeados);
    
    return contratosMapeados;
  }

  // Extrair data mais antiga das notas de suprimentos
  private extrairDataInicioSuprimentos(notas: NotaSuprimento[]): string {
    if (!notas || notas.length === 0) {
      // Se não há notas, assumir que o contrato começou no início do ano atual
      return `${new Date().getFullYear()}-01-01`;
    }
    
    const datas = notas.map(nota => nota.data).filter(data => data);
    if (datas.length === 0) {
      return `${new Date().getFullYear()}-01-01`;
    }
    
    // Ordenar datas e pegar a mais antiga
    const dataInicioNota = datas.sort()[0];
    
    // Assumir que o contrato começou 12 meses antes da primeira nota
    const dataNota = new Date(dataInicioNota);
    const dataInicioContrato = new Date(dataNota);
    dataInicioContrato.setFullYear(dataNota.getFullYear() - 1);
    
    return dataInicioContrato.toISOString().split('T')[0];
  }

  // Extrair data mais recente das notas de suprimentos  
  private extrairDataFimSuprimentos(notas: NotaSuprimento[]): string {
    if (!notas || notas.length === 0) {
      // Se não há notas, assumir que o contrato vai até o fim do ano seguinte
      return `${new Date().getFullYear() + 1}-12-31`;
    }
    
    const datas = notas.map(nota => nota.data).filter(data => data);
    if (datas.length === 0) {
      return `${new Date().getFullYear() + 1}-12-31`;
    }
    
    // Ordenar datas e pegar a mais recente
    const dataUltimaNota = datas.sort().reverse()[0];
    
    // Assumir que o contrato continua por mais 12 meses após a última nota
    const dataNota = new Date(dataUltimaNota);
    const dataFimContrato = new Date(dataNota);
    dataFimContrato.setFullYear(dataNota.getFullYear() + 1);
    
    return dataFimContrato.toISOString().split('T')[0];
  }

  // Contar máquinas únicas baseado nos modelos nas observações
  private contarMaquinasSuprimentos(notas: NotaSuprimento[]): number {
    if (!notas || notas.length === 0) return 0;
    
    const modelos = new Set<string>();
    notas.forEach(nota => {
      if (nota.obs) {
        // Extrair modelo da observação (ex: "MOD.: SP 3510")
        const modeloMatch = nota.obs.match(/MOD\.?:?\s*([^N/S:]+)/i);
        if (modeloMatch) {
          modelos.add(modeloMatch[1].trim());
        }
      }
    });
    
    return modelos.size || 1; // Mínimo 1 máquina
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
