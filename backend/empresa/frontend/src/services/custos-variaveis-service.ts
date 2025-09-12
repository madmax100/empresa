// src/services/custos-variaveis-service.ts

const API_BASE_URL = 'http://localhost:8000';

export interface CustosVariaveisResponse {
  parametros: {
    data_inicio: string;
    data_fim: string;
    filtro_aplicado: string;
    fonte_dados: string;
  };
  estatisticas_fornecedores: {
    total_fornecedores_variaveis_cadastrados: number;
    fornecedores_com_pagamentos_no_periodo: number;
  };
  totais_gerais: {
    total_valor_original: number;
    total_valor_pago: number;
    total_juros: number;
    total_tarifas: number;
  };
  resumo_por_especificacao: Array<{
    especificacao: string;
    valor_original_total: number;
    valor_pago_total: number;
    juros_total: number;
    tarifas_total: number;
    quantidade_contas: number;
    quantidade_fornecedores: number;
    fornecedores: string[];
  }>;
  total_contas_pagas: number;
  contas_pagas: Array<{
    id: number;
    data_pagamento: string;
    fornecedor_nome: string;
    fornecedor_tipo: string;
    fornecedor_especificacao: string;
    valor_original: number;
    valor_pago: number;
    juros: number;
    tarifas: number;
    historico: string;
    forma_pagamento: string;
  }>;
}

export class CustosVariaveisService {
  static async buscarCustosVariaveis(dataInicio: string, dataFim: string): Promise<CustosVariaveisResponse> {
    try {
      const params = new URLSearchParams({
        data_inicio: dataInicio,
        data_fim: dataFim,
        // Adicionar timestamp para evitar cache
        _t: new Date().getTime().toString()
      });

      const url = `${API_BASE_URL}/contas/relatorios/custos-variaveis/?${params}`;
      console.log('📡 Chamando API de custos variáveis:', url);
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
      const validatedData = CustosVariaveisService.validateAndNormalizeData(data, dataInicio, dataFim);

      console.log('✨ Dados validados e normalizados:', validatedData);
      
      return validatedData;
    } catch (error) {
      console.error('❌ Erro ao buscar custos variáveis:', error);
      
      // Retornar dados vazios em caso de erro
      return CustosVariaveisService.getEmptyResponse(dataInicio, dataFim);
    }
  }

  static validateAndNormalizeData(data: unknown, dataInicio: string, dataFim: string): CustosVariaveisResponse {
    try {
      console.log('🔍 Validando dados recebidos...');
      
      if (!data || typeof data !== 'object') {
        console.warn('⚠️ Dados inválidos ou ausentes, usando fallback');
        return CustosVariaveisService.getEmptyResponse(dataInicio, dataFim);
      }

      const apiData = data as Record<string, unknown>;

      // Garantir que todos os campos obrigatórios existam
      const normalized: CustosVariaveisResponse = {
        parametros: {
          data_inicio: (apiData.parametros as Record<string, unknown>)?.data_inicio as string || dataInicio,
          data_fim: (apiData.parametros as Record<string, unknown>)?.data_fim as string || dataFim,
          filtro_aplicado: (apiData.parametros as Record<string, unknown>)?.filtro_aplicado as string || 'Fornecedores com tipo relacionado a CUSTOS VARIÁVEIS',
          fonte_dados: (apiData.parametros as Record<string, unknown>)?.fonte_dados as string || 'Contas a Pagar (status: Pago)'
        },
        estatisticas_fornecedores: {
          total_fornecedores_variaveis_cadastrados: (apiData.estatisticas_fornecedores as Record<string, unknown>)?.total_fornecedores_variaveis_cadastrados as number || 0,
          fornecedores_com_pagamentos_no_periodo: (apiData.estatisticas_fornecedores as Record<string, unknown>)?.fornecedores_com_pagamentos_no_periodo as number || 0
        },
        totais_gerais: {
          total_valor_original: (apiData.totais_gerais as Record<string, unknown>)?.total_valor_original as number || 0,
          total_valor_pago: (apiData.totais_gerais as Record<string, unknown>)?.total_valor_pago as number || 0,
          total_juros: (apiData.totais_gerais as Record<string, unknown>)?.total_juros as number || 0,
          total_tarifas: (apiData.totais_gerais as Record<string, unknown>)?.total_tarifas as number || 0
        },
        resumo_por_especificacao: Array.isArray(apiData.resumo_por_especificacao) 
          ? (apiData.resumo_por_especificacao as Record<string, unknown>[]).map((item: Record<string, unknown>) => ({
              especificacao: item.especificacao as string || 'Sem Especificação',
              valor_original_total: item.valor_original_total as number || 0,
              valor_pago_total: item.valor_pago_total as number || 0,
              juros_total: item.juros_total as number || 0,
              tarifas_total: item.tarifas_total as number || 0,
              quantidade_contas: item.quantidade_contas as number || 0,
              quantidade_fornecedores: item.quantidade_fornecedores as number || 0,
              fornecedores: Array.isArray(item.fornecedores) ? item.fornecedores as string[] : []
            }))
          : [],
        total_contas_pagas: apiData.total_contas_pagas as number || 0,
        contas_pagas: Array.isArray(apiData.contas_pagas)
          ? (apiData.contas_pagas as Record<string, unknown>[]).map((conta: Record<string, unknown>) => ({
              id: conta.id as number || 0,
              data_pagamento: conta.data_pagamento as string || '',
              fornecedor_nome: conta.fornecedor_nome as string || '',
              fornecedor_tipo: conta.fornecedor_tipo as string || '',
              fornecedor_especificacao: conta.fornecedor_especificacao as string || 'Sem Especificação',
              valor_original: conta.valor_original as number || 0,
              valor_pago: conta.valor_pago as number || 0,
              juros: conta.juros as number || 0,
              tarifas: conta.tarifas as number || 0,
              historico: conta.historico as string || '',
              forma_pagamento: conta.forma_pagamento as string || ''
            }))
          : []
      };

      console.log('✅ Dados normalizados com sucesso');
      return normalized;

    } catch (error) {
      console.error('❌ Erro na validação dos dados:', error);
      return CustosVariaveisService.getEmptyResponse(dataInicio, dataFim);
    }
  }

  static getEmptyResponse(dataInicio: string, dataFim: string): CustosVariaveisResponse {
    console.log('📝 Retornando resposta vazia para custos variáveis');
    
    return {
      parametros: {
        data_inicio: dataInicio,
        data_fim: dataFim,
        filtro_aplicado: 'Fornecedores com tipo relacionado a CUSTOS VARIÁVEIS',
        fonte_dados: 'Contas a Pagar (status: Pago)'
      },
      estatisticas_fornecedores: {
        total_fornecedores_variaveis_cadastrados: 0,
        fornecedores_com_pagamentos_no_periodo: 0
      },
      totais_gerais: {
        total_valor_original: 0,
        total_valor_pago: 0,
        total_juros: 0,
        total_tarifas: 0
      },
      resumo_por_especificacao: [],
      total_contas_pagas: 0,
      contas_pagas: []
    };
  }

  // Método para gerar dados de exemplo/mockados
  static getMockData(dataInicio: string, dataFim: string): CustosVariaveisResponse {
    console.log('🎭 Gerando dados de exemplo para custos variáveis');
    
    return {
      parametros: {
        data_inicio: dataInicio,
        data_fim: dataFim,
        filtro_aplicado: 'Fornecedores com tipo relacionado a CUSTOS VARIÁVEIS',
        fonte_dados: 'Contas a Pagar (status: Pago)'
      },
      estatisticas_fornecedores: {
        total_fornecedores_variaveis_cadastrados: 254,
        fornecedores_com_pagamentos_no_periodo: 24
      },
      totais_gerais: {
        total_valor_original: 26134.28,
        total_valor_pago: 26134.28,
        total_juros: 0,
        total_tarifas: 0
      },
      resumo_por_especificacao: [
        {
          especificacao: 'FORNECEDORES',
          valor_original_total: 14826.56,
          valor_pago_total: 14826.56,
          juros_total: 0,
          tarifas_total: 0,
          quantidade_contas: 18,
          quantidade_fornecedores: 10,
          fornecedores: ['CONECTA EQUIPAMENTOS E SERVICOS LTDA', 'TECH SOLUTIONS LTDA', 'GLOBAL PARTS LTDA']
        },
        {
          especificacao: 'IMPOSTOS',
          valor_original_total: 6509.42,
          valor_pago_total: 6509.42,
          juros_total: 0,
          tarifas_total: 0,
          quantidade_contas: 10,
          quantidade_fornecedores: 4,
          fornecedores: ['RECEITA FEDERAL', 'SECRETARIA DA FAZENDA', 'PREFEITURA MUNICIPAL']
        },
        {
          especificacao: 'TRANSPORTES',
          valor_original_total: 4798.30,
          valor_pago_total: 4798.30,
          juros_total: 0,
          tarifas_total: 0,
          quantidade_contas: 15,
          quantidade_fornecedores: 6,
          fornecedores: ['TRANSPORTADORA RÁPIDA LTDA', 'LOGÍSTICA EXPRESS', 'FRETE & CIA']
        }
      ],
      total_contas_pagas: 43,
      contas_pagas: [
        {
          id: 1234,
          data_pagamento: '2025-08-29',
          fornecedor_nome: 'CONECTA EQUIPAMENTOS E SERVICOS LTDA',
          fornecedor_tipo: 'DESPESA VARIAVEL',
          fornecedor_especificacao: 'FORNECEDORES',
          valor_original: 1274.0,
          valor_pago: 1274.0,
          juros: 0,
          tarifas: 0,
          historico: 'Pagamento de equipamentos',
          forma_pagamento: 'PIX'
        },
        {
          id: 1235,
          data_pagamento: '2025-08-28',
          fornecedor_nome: 'RECEITA FEDERAL',
          fornecedor_tipo: 'CUSTO VARIAVEL',
          fornecedor_especificacao: 'IMPOSTOS',
          valor_original: 2500.0,
          valor_pago: 2500.0,
          juros: 0,
          tarifas: 0,
          historico: 'Pagamento de impostos federais',
          forma_pagamento: 'DEBITO'
        }
      ]
    };
  }
}
