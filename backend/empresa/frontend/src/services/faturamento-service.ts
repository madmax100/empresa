// src/services/faturamento-service.ts

const API_BASE_URL = 'http://localhost:8000';

export interface FaturamentoResponse {
  parametros: {
    data_inicio: string;
    data_fim: string;
    filtros_aplicados: {
      nf_entrada: string;
      nf_saida: string;
      nf_servico: string;
    };
    fonte_dados: string;
  };
  totais_gerais: {
    total_quantidade_notas: number;
    total_valor_produtos: number;
    total_valor_geral: number;
    total_impostos: number;
    analise_vendas: {
      valor_vendas: number;
      valor_preco_entrada: number;
      margem_bruta: number;
      percentual_margem: number;
      itens_analisados: number;
      produtos_sem_preco_entrada: number;
    };
  };
  resumo_por_tipo: Array<{
    tipo: string;
    quantidade_notas: number;
    valor_produtos: number;
    valor_total: number;
    impostos: number;
    valor_preco_entrada?: number;
    margem_bruta?: number;
    detalhes: {
      valor_icms?: number;
      valor_ipi?: number;
      valor_desconto?: number;
      valor_iss?: number;
      itens_calculados?: number;
      produtos_sem_preco_entrada?: number;
    };
  }>;
  top_fornecedores: Array<{
    fornecedor: string;
    valor_total: number;
    quantidade_notas: number;
  }>;
  top_clientes: Array<{
    cliente: string;
    valor_total: number;
    quantidade_notas: number;
    tipo: string;
  }>;
  notas_detalhadas: {
    compras: Array<{
      id: number;
      numero_nota: string;
      data_emissao: string;
      fornecedor: string;
      operacao: string;
      valor_produtos: number;
      valor_total: number;
      valor_icms: number;
      valor_ipi: number;
    }>;
    vendas: Array<{
      id: number;
      numero_nota: string;
      data: string;
      cliente: string;
      operacao: string;
      valor_produtos: number;
      valor_total: number;
      valor_icms: number;
      desconto: number;
      valor_preco_entrada: number;
      margem_bruta: number;
    }>;
    servicos: Array<{
      id: number;
      numero_nota: string;
      data: string;
      cliente: string;
      operacao: string;
      valor_produtos: number;
      valor_total: number;
      valor_iss: number;
    }>;
  };
}

export class FaturamentoService {
  static async buscarFaturamento(dataInicio: string, dataFim: string): Promise<FaturamentoResponse> {
    try {
      const params = new URLSearchParams({
        data_inicio: dataInicio,
        data_fim: dataFim,
        // Adicionar timestamp para evitar cache
        _t: new Date().getTime().toString()
      });

      const url = `${API_BASE_URL}/contas/relatorios/faturamento/?${params}`;
      console.log('📡 Chamando API de faturamento:', url);
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
      const validatedData = FaturamentoService.validateAndNormalizeData(data, dataInicio, dataFim);

      console.log('✨ Dados validados e normalizados:', validatedData);
      
      return validatedData;
    } catch (error) {
      console.error('❌ Erro ao buscar faturamento:', error);
      throw error;
    }
  }

  static validateAndNormalizeData(data: unknown, dataInicio: string, dataFim: string): FaturamentoResponse {
    try {
      console.log('🔍 Validando dados recebidos...');
      
      if (!data || typeof data !== 'object') {
        console.warn('⚠️ Dados inválidos ou ausentes, usando fallback');
        return FaturamentoService.getEmptyResponse(dataInicio, dataFim);
      }

      const apiData = data as Record<string, unknown>;

      // Garantir que todos os campos obrigatórios existam
      const normalized: FaturamentoResponse = {
        parametros: {
          data_inicio: (apiData.parametros as Record<string, unknown>)?.data_inicio as string || dataInicio,
          data_fim: (apiData.parametros as Record<string, unknown>)?.data_fim as string || dataFim,
          filtros_aplicados: {
            nf_entrada: ((apiData.parametros as Record<string, unknown>)?.filtros_aplicados as Record<string, unknown>)?.nf_entrada as string || 'Operação contendo COMPRA',
            nf_saida: ((apiData.parametros as Record<string, unknown>)?.filtros_aplicados as Record<string, unknown>)?.nf_saida as string || 'Operação contendo VENDA',
            nf_servico: ((apiData.parametros as Record<string, unknown>)?.filtros_aplicados as Record<string, unknown>)?.nf_servico as string || 'Todas as notas de serviço'
          },
          fonte_dados: (apiData.parametros as Record<string, unknown>)?.fonte_dados as string || 'Notas Fiscais (Entrada, Saída e Serviço)'
        },
        totais_gerais: {
          total_quantidade_notas: (apiData.totais_gerais as Record<string, unknown>)?.total_quantidade_notas as number || 0,
          total_valor_produtos: (apiData.totais_gerais as Record<string, unknown>)?.total_valor_produtos as number || 0,
          total_valor_geral: (apiData.totais_gerais as Record<string, unknown>)?.total_valor_geral as number || 0,
          total_impostos: (apiData.totais_gerais as Record<string, unknown>)?.total_impostos as number || 0,
          analise_vendas: {
            valor_vendas: ((apiData.totais_gerais as Record<string, unknown>)?.analise_vendas as Record<string, unknown>)?.valor_vendas as number || 0,
            valor_preco_entrada: ((apiData.totais_gerais as Record<string, unknown>)?.analise_vendas as Record<string, unknown>)?.valor_preco_entrada as number || 0,
            margem_bruta: ((apiData.totais_gerais as Record<string, unknown>)?.analise_vendas as Record<string, unknown>)?.margem_bruta as number || 0,
            percentual_margem: ((apiData.totais_gerais as Record<string, unknown>)?.analise_vendas as Record<string, unknown>)?.percentual_margem as number || 0,
            itens_analisados: ((apiData.totais_gerais as Record<string, unknown>)?.analise_vendas as Record<string, unknown>)?.itens_analisados as number || 0,
            produtos_sem_preco_entrada: ((apiData.totais_gerais as Record<string, unknown>)?.analise_vendas as Record<string, unknown>)?.produtos_sem_preco_entrada as number || 0
          }
        },
        resumo_por_tipo: Array.isArray(apiData.resumo_por_tipo) 
          ? (apiData.resumo_por_tipo as Record<string, unknown>[]).map((item: Record<string, unknown>) => ({
              tipo: item.tipo as string || '',
              quantidade_notas: item.quantidade_notas as number || 0,
              valor_produtos: item.valor_produtos as number || 0,
              valor_total: item.valor_total as number || 0,
              impostos: item.impostos as number || 0,
              valor_preco_entrada: item.valor_preco_entrada as number || 0,
              margem_bruta: item.margem_bruta as number || 0,
              detalhes: {
                valor_icms: (item.detalhes as Record<string, unknown>)?.valor_icms as number || 0,
                valor_ipi: (item.detalhes as Record<string, unknown>)?.valor_ipi as number || 0,
                valor_desconto: (item.detalhes as Record<string, unknown>)?.valor_desconto as number || 0,
                valor_iss: (item.detalhes as Record<string, unknown>)?.valor_iss as number || 0,
                itens_calculados: (item.detalhes as Record<string, unknown>)?.itens_calculados as number || 0,
                produtos_sem_preco_entrada: (item.detalhes as Record<string, unknown>)?.produtos_sem_preco_entrada as number || 0
              }
            }))
          : [],
        top_fornecedores: Array.isArray(apiData.top_fornecedores)
          ? (apiData.top_fornecedores as Record<string, unknown>[]).map((fornecedor: Record<string, unknown>) => ({
              fornecedor: fornecedor.fornecedor as string || '',
              valor_total: fornecedor.valor_total as number || 0,
              quantidade_notas: fornecedor.quantidade_notas as number || 0
            }))
          : [],
        top_clientes: Array.isArray(apiData.top_clientes)
          ? (apiData.top_clientes as Record<string, unknown>[]).map((cliente: Record<string, unknown>) => ({
              cliente: cliente.cliente as string || '',
              valor_total: cliente.valor_total as number || 0,
              quantidade_notas: cliente.quantidade_notas as number || 0,
              tipo: cliente.tipo as string || ''
            }))
          : [],
        notas_detalhadas: {
          compras: Array.isArray((apiData.notas_detalhadas as Record<string, unknown>)?.compras)
            ? ((apiData.notas_detalhadas as Record<string, unknown>).compras as Record<string, unknown>[]).map((nota: Record<string, unknown>) => ({
                id: nota.id as number || 0,
                numero_nota: nota.numero_nota as string || '',
                data_emissao: nota.data_emissao as string || '',
                fornecedor: nota.fornecedor as string || '',
                operacao: nota.operacao as string || '',
                valor_produtos: nota.valor_produtos as number || 0,
                valor_total: nota.valor_total as number || 0,
                valor_icms: nota.valor_icms as number || 0,
                valor_ipi: nota.valor_ipi as number || 0
              }))
            : [],
          vendas: Array.isArray((apiData.notas_detalhadas as Record<string, unknown>)?.vendas)
            ? ((apiData.notas_detalhadas as Record<string, unknown>).vendas as Record<string, unknown>[]).map((nota: Record<string, unknown>) => ({
                id: nota.id as number || 0,
                numero_nota: nota.numero_nota as string || '',
                data: nota.data as string || '',
                cliente: nota.cliente as string || '',
                operacao: nota.operacao as string || '',
                valor_produtos: nota.valor_produtos as number || 0,
                valor_total: nota.valor_total as number || 0,
                valor_icms: nota.valor_icms as number || 0,
                desconto: nota.desconto as number || 0,
                valor_preco_entrada: nota.valor_preco_entrada as number || 0,
                margem_bruta: nota.margem_bruta as number || 0
              }))
            : [],
          servicos: Array.isArray((apiData.notas_detalhadas as Record<string, unknown>)?.servicos)
            ? ((apiData.notas_detalhadas as Record<string, unknown>).servicos as Record<string, unknown>[]).map((nota: Record<string, unknown>) => ({
                id: nota.id as number || 0,
                numero_nota: nota.numero_nota as string || '',
                data: nota.data as string || '',
                cliente: nota.cliente as string || '',
                operacao: nota.operacao as string || '',
                valor_produtos: nota.valor_produtos as number || 0,
                valor_total: nota.valor_total as number || 0,
                valor_iss: nota.valor_iss as number || 0
              }))
            : []
        }
      };

      console.log('✅ Dados normalizados com sucesso');
      return normalized;

    } catch (error) {
      console.error('❌ Erro na validação dos dados:', error);
      return FaturamentoService.getEmptyResponse(dataInicio, dataFim);
    }
  }

  static getEmptyResponse(dataInicio: string, dataFim: string): FaturamentoResponse {
    console.log('📝 Retornando resposta vazia para faturamento');
    
    return {
      parametros: {
        data_inicio: dataInicio,
        data_fim: dataFim,
        filtros_aplicados: {
          nf_entrada: 'Operação contendo COMPRA',
          nf_saida: 'Operação contendo VENDA',
          nf_servico: 'Todas as notas de serviço'
        },
        fonte_dados: 'Notas Fiscais (Entrada, Saída e Serviço)'
      },
      totais_gerais: {
        total_quantidade_notas: 0,
        total_valor_produtos: 0,
        total_valor_geral: 0,
        total_impostos: 0,
        analise_vendas: {
          valor_vendas: 0,
          valor_preco_entrada: 0,
          margem_bruta: 0,
          percentual_margem: 0,
          itens_analisados: 0,
          produtos_sem_preco_entrada: 0
        }
      },
      resumo_por_tipo: [],
      top_fornecedores: [],
      top_clientes: [],
      notas_detalhadas: {
        compras: [],
        vendas: [],
        servicos: []
      }
    };
  }
}
