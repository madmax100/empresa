// src/services/custos-fixos-service.ts

export interface CustoFixoParametros {
  data_inicio: string;
  data_fim: string;
}

export interface EstatisticasFornecedores {
  total_fornecedores: number;
  fornecedores_custo_fixo: number;
  fornecedores_despesa_fixa: number;
  fornecedores_ativos: number;
}

export interface TotaisGerais {
  valor_total: number;
  valor_custos_fixos: number;
  valor_despesas_fixas: number;
  quantidade_total_contas: number;
}

export interface ResumoTipoFornecedor {
  tipo_fornecedor: string;
  quantidade_contas: number;
  valor_total: number;
  percentual_quantidade: number;
  percentual_valor: number;
}

export interface ResumoFornecedor {
  fornecedor: string;
  tipo_fornecedor: string;
  quantidade_contas: number;
  valor_total: number;
  percentual_do_total: number;
  valor_medio_conta: number;
}

export interface ContaPaga {
  id: number;
  fornecedor: string;
  tipo_fornecedor: string;
  descricao: string;
  valor: number;
  data_vencimento: string;
  data_pagamento: string;
  observacoes?: string;
  categoria?: string;
}

export interface CustosFixosResponse {
  parametros: CustoFixoParametros;
  estatisticas_fornecedores: EstatisticasFornecedores;
  totais_gerais: TotaisGerais;
  resumo_por_tipo_fornecedor: ResumoTipoFornecedor[];
  resumo_por_fornecedor: ResumoFornecedor[];
  total_contas_pagas: number;
  contas_pagas: ContaPaga[];
}

const API_BASE_URL = 'http://127.0.0.1:8000';

export class CustosFixosService {
  // Flag para usar dados mock para teste (pode ser removida depois)
  private static USE_MOCK_DATA = false;
  
  static async getCustosFixos(dataInicio: string, dataFim: string): Promise<CustosFixosResponse> {
    console.log('🔍 Buscando custos fixos via API:', { dataInicio, dataFim });
    
    // Modo de teste com dados mock
    if (this.USE_MOCK_DATA) {
      console.log('🧪 Modo teste: retornando dados mock');
      return this.getMockData(dataInicio, dataFim);
    }
    
    try {
      const params = new URLSearchParams({
        data_inicio: dataInicio,
        data_fim: dataFim,
        // Adicionar timestamp para evitar cache
        _t: new Date().getTime().toString()
      });

      const url = `${API_BASE_URL}/api/relatorios/custos-fixos/?${params}`;
      console.log('📡 Chamando API:', url);
      console.log('📅 Parâmetros de data enviados:', { data_inicio: dataInicio, data_fim: dataFim });

      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Erro na API: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Dados brutos recebidos da API:', data);
      console.log('📊 Tipo dos dados:', typeof data);
      console.log('🔍 Estrutura dos dados:', Object.keys(data || {}));
      
      // Validar e normalizar os dados recebidos
      const validatedData = CustosFixosService.validateAndNormalizeData(data, dataInicio, dataFim);
      console.log('🔧 Dados validados:', validatedData);
      
      return validatedData;
      
    } catch (error) {
      console.error('❌ Erro ao buscar dados de custos fixos:', error);
      
      // Verificar o tipo de erro para fornecer feedback mais específico
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.warn('🔌 Backend não disponível, retornando dados vazios');
        // Retornar dados vazios ao invés de falhar completamente
        return CustosFixosService.createEmptyResponse(dataInicio, dataFim);
      }
      
      throw error; // Propagar outros tipos de erro
    }
  }

  private static validateAndNormalizeData(data: unknown, dataInicio: string, dataFim: string): CustosFixosResponse {
    console.log('🔧 Iniciando validação dos dados:', { data, dataInicio, dataFim });
    
    // Se os dados estão vazios ou malformados, retornar estrutura padrão
    if (!data || typeof data !== 'object') {
      console.warn('⚠️ Dados inválidos recebidos da API, retornando estrutura vazia');
      return CustosFixosService.createEmptyResponse(dataInicio, dataFim);
    }

    const apiData = data as Record<string, unknown>;
    
    console.log('📋 Validando campos individuais...');
    console.log('estatisticas_fornecedores:', apiData.estatisticas_fornecedores);
    console.log('totais_gerais:', apiData.totais_gerais);
    console.log('resumo_por_tipo_fornecedor:', apiData.resumo_por_tipo_fornecedor);

    // Mapear dados da API real para o formato esperado
    const estatisticasAPI = apiData.estatisticas_fornecedores as Record<string, unknown>;
    const totaisAPI = apiData.totais_gerais as Record<string, unknown>;

    // Normalizar e validar cada campo
    const normalized: CustosFixosResponse = {
      parametros: {
        data_inicio: dataInicio,
        data_fim: dataFim
      },
      estatisticas_fornecedores: {
        total_fornecedores: Number(estatisticasAPI?.total_fornecedores_fixos_cadastrados) || 0,
        fornecedores_custo_fixo: 0, // API não retorna este campo específico
        fornecedores_despesa_fixa: 0, // API não retorna este campo específico
        fornecedores_ativos: Number(estatisticasAPI?.fornecedores_com_pagamentos_no_periodo) || 0
      },
      totais_gerais: {
        valor_total: Number(totaisAPI?.total_valor_pago) || 0,
        valor_custos_fixos: 0, // Será calculado a partir do resumo por tipo
        valor_despesas_fixas: 0, // Será calculado a partir do resumo por tipo
        quantidade_total_contas: Number(apiData.total_contas_pagas) || 0
      },
      resumo_por_tipo_fornecedor: Array.isArray(apiData.resumo_por_tipo_fornecedor) 
        ? apiData.resumo_por_tipo_fornecedor.map((item: unknown) => {
            const tipoItem = item as Record<string, unknown>;
            const valorTotal = Number(tipoItem.total_pago) || 0;
            const quantidadeContas = Number(tipoItem.quantidade_contas) || 0;
            const totalGeral = Number(totaisAPI?.total_valor_pago) || 1; // Evitar divisão por zero
            
            return {
              tipo_fornecedor: String(tipoItem.fornecedor__tipo || ''),
              quantidade_contas: quantidadeContas,
              valor_total: valorTotal,
              percentual_quantidade: totalGeral > 0 ? (quantidadeContas / Number(apiData.total_contas_pagas || 1)) * 100 : 0,
              percentual_valor: totalGeral > 0 ? (valorTotal / totalGeral) * 100 : 0
            };
          })
        : [],
      resumo_por_fornecedor: Array.isArray(apiData.resumo_por_fornecedor)
        ? apiData.resumo_por_fornecedor.map((item: unknown) => {
            const fornecedorItem = item as Record<string, unknown>;
            const valorTotal = Number(fornecedorItem.total_pago) || 0;
            const quantidadeContas = Number(fornecedorItem.quantidade_contas) || 0;
            const totalGeral = Number(totaisAPI?.total_valor_pago) || 1;
            
            return {
              fornecedor: String(fornecedorItem.fornecedor__nome || ''),
              tipo_fornecedor: String(fornecedorItem.fornecedor__tipo || ''),
              quantidade_contas: quantidadeContas,
              valor_total: valorTotal,
              percentual_do_total: totalGeral > 0 ? (valorTotal / totalGeral) * 100 : 0,
              valor_medio_conta: quantidadeContas > 0 ? valorTotal / quantidadeContas : 0
            };
          })
        : [],
      total_contas_pagas: Number(apiData.total_contas_pagas) || 0,
      contas_pagas: Array.isArray(apiData.contas_pagas)
        ? apiData.contas_pagas.map((item: unknown) => {
            const contaItem = item as Record<string, unknown>;
            return {
              id: Number(contaItem.id) || 0,
              fornecedor: String(contaItem.fornecedor || ''),
              tipo_fornecedor: String(contaItem.fornecedor_tipo || ''),
              descricao: String(contaItem.historico || ''),
              valor: Number(contaItem.valor_pago) || 0,
              data_vencimento: String(contaItem.data_vencimento || ''),
              data_pagamento: String(contaItem.data_pagamento || ''),
              observacoes: contaItem.numero_duplicata ? String(contaItem.numero_duplicata) : undefined,
              categoria: contaItem.forma_pagamento ? String(contaItem.forma_pagamento) : undefined
            };
          })
        : []
    };

    // Calcular valores por tipo de fornecedor
    let valorCustosFixos = 0;
    let valorDespesasFixas = 0;
    let fornecedoresCustoFixo = 0;
    let fornecedoresDespesaFixa = 0;

    normalized.resumo_por_tipo_fornecedor.forEach(tipo => {
      if (tipo.tipo_fornecedor === 'CUSTO FIXO') {
        valorCustosFixos += tipo.valor_total;
      } else if (tipo.tipo_fornecedor === 'DESPESA FIXA') {
        valorDespesasFixas += tipo.valor_total;
      }
    });

    normalized.resumo_por_fornecedor.forEach(fornecedor => {
      if (fornecedor.tipo_fornecedor === 'CUSTO FIXO') {
        fornecedoresCustoFixo++;
      } else if (fornecedor.tipo_fornecedor === 'DESPESA FIXA') {
        fornecedoresDespesaFixa++;
      }
    });

    // Atualizar totais calculados
    normalized.totais_gerais.valor_custos_fixos = valorCustosFixos;
    normalized.totais_gerais.valor_despesas_fixas = valorDespesasFixas;
    normalized.estatisticas_fornecedores.fornecedores_custo_fixo = fornecedoresCustoFixo;
    normalized.estatisticas_fornecedores.fornecedores_despesa_fixa = fornecedoresDespesaFixa;

    console.log('✅ Dados normalizados finais:', normalized);
    return normalized;
  }

  private static createEmptyResponse(dataInicio: string, dataFim: string): CustosFixosResponse {
    return {
      parametros: {
        data_inicio: dataInicio,
        data_fim: dataFim
      },
      estatisticas_fornecedores: {
        total_fornecedores: 0,
        fornecedores_custo_fixo: 0,
        fornecedores_despesa_fixa: 0,
        fornecedores_ativos: 0
      },
      totais_gerais: {
        valor_total: 0,
        valor_custos_fixos: 0,
        valor_despesas_fixas: 0,
        quantidade_total_contas: 0
      },
      resumo_por_tipo_fornecedor: [],
      resumo_por_fornecedor: [],
      total_contas_pagas: 0,
      contas_pagas: []
    };
  }

  // Método para dados mock de teste
  private static getMockData(dataInicio: string, dataFim: string): CustosFixosResponse {
    return {
      parametros: {
        data_inicio: dataInicio,
        data_fim: dataFim
      },
      estatisticas_fornecedores: {
        total_fornecedores: 21,
        fornecedores_custo_fixo: 12,
        fornecedores_despesa_fixa: 9,
        fornecedores_ativos: 21
      },
      totais_gerais: {
        valor_total: 211550.03,
        valor_custos_fixos: 142420.65,
        valor_despesas_fixas: 69129.38,
        quantidade_total_contas: 295
      },
      resumo_por_tipo_fornecedor: [
        {
          tipo_fornecedor: "CUSTO FIXO",
          quantidade_contas: 185,
          valor_total: 142420.65,
          percentual_quantidade: 62.7,
          percentual_valor: 67.3
        },
        {
          tipo_fornecedor: "DESPESA FIXA",
          quantidade_contas: 110,
          valor_total: 69129.38,
          percentual_quantidade: 37.3,
          percentual_valor: 32.7
        }
      ],
      resumo_por_fornecedor: [
        {
          fornecedor: "ENERGIA ELÉTRICA",
          tipo_fornecedor: "CUSTO FIXO",
          quantidade_contas: 25,
          valor_total: 5892.45,
          percentual_do_total: 2.8,
          valor_medio_conta: 235.70
        },
        {
          fornecedor: "TELEFONIA",
          tipo_fornecedor: "DESPESA FIXA",
          quantidade_contas: 12,
          valor_total: 2847.32,
          percentual_do_total: 1.3,
          valor_medio_conta: 237.28
        },
        {
          fornecedor: "INTERNET",
          tipo_fornecedor: "CUSTO FIXO",
          quantidade_contas: 12,
          valor_total: 1680.00,
          percentual_do_total: 0.8,
          valor_medio_conta: 140.00
        }
      ],
      total_contas_pagas: 295,
      contas_pagas: [
        {
          id: 1,
          fornecedor: "ENERGIA ELÉTRICA",
          tipo_fornecedor: "CUSTO FIXO",
          descricao: "Conta de luz - Janeiro",
          valor: 245.67,
          data_vencimento: "2024-01-15",
          data_pagamento: "2024-01-15",
          categoria: "Utilidades"
        },
        {
          id: 2,
          fornecedor: "TELEFONIA",
          tipo_fornecedor: "DESPESA FIXA",
          descricao: "Conta de telefone - Janeiro",
          valor: 89.50,
          data_vencimento: "2024-01-10",
          data_pagamento: "2024-01-10",
          categoria: "Comunicação"
        },
        {
          id: 3,
          fornecedor: "ALUGUEL",
          tipo_fornecedor: "CUSTO FIXO",
          descricao: "Aluguel do Escritório - Janeiro",
          valor: 1050.34,
          data_vencimento: "2024-01-05",
          data_pagamento: "2024-01-05",
          categoria: "Aluguel"
        }
      ]
    };
  }
}
