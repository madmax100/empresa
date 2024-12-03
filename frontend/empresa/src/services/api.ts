// src/services/api.ts
import { Cliente, ContasPagarResponse, ContasReceberResponse, Contrato, ContratoExpandido, DashboardContrato, DashboardFiltros, DashboardResponse, FilterParams, ItemContrato, Produto } from '@/types/models';
import { NotaFiscalAgrupamento, NotaFiscalFiltros, NotaFiscalResponse, NotaFiscalSaida } from '@/types/notas_fiscais/models';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/contas',
  headers: {
    'Content-Type': 'application/json',
  }
});

export const produtosService = {
  listar: () => api.get<Produto[]>('/produtos/'),
  buscarPorId: (id: number) => api.get<Produto>(`/produtos/${id}/`),
  criar: (produto: Omit<Produto, 'id'>) => api.post<Produto>('/produtos/', produto),
  atualizar: (id: number, produto: Partial<Produto>) => api.patch<Produto>(`/produtos/${id}/`, produto),
  excluir: (id: number) => api.delete(`/produtos/${id}/`)
};

export const clientesService = {
  listar: () => api.get<Cliente[]>('/clientes/'),
  buscarPorId: (id: number) => api.get<Cliente>(`/clientes/${id}/`),
  criar: (cliente: Omit<Cliente, 'id'>) => api.post<Cliente>('/clientes/', cliente),
  atualizar: (id: number, cliente: Partial<Cliente>) => api.patch<Cliente>(`/clientes/${id}/`, cliente),
  excluir: (id: number) => api.delete(`/clientes/${id}/`)
};

export const contratosService = {
    listar: async (): Promise<ContratoExpandido[]> => {
        const response = await api.get<Contrato[]>('/contratos_locacao/');
        return response.data as ContratoExpandido[];
    },

    buscarItens: async (numeroContrato: string): Promise<ItemContrato[]> => {
        const response = await api.get<ItemContrato[]>(`/contratos_locacao/itens/${numeroContrato}/`);
        return response.data;
    },

    buscarDashboard: async (
        numeroContrato: string,
        filtros?: DashboardFiltros
    ): Promise<DashboardContrato> => {
        try {
            const params = new URLSearchParams();

            if (filtros?.data_inicial) {
                params.append('data_inicial', filtros.data_inicial);
            }
            if (filtros?.data_final) {
                params.append('data_final', filtros.data_final);
            }

            const response = await api.get<DashboardContrato>(
                `/contratos_locacao/dashboard/${numeroContrato}/`,
                { params }
            );

            // Garantir que os dados retornados estejam no formato correto
            const formattedResponse: DashboardContrato = {
                ...response.data,
                periodo: {
                    data_inicial: response.data.periodo.data_inicial || filtros?.data_inicial || '',
                    data_final: response.data.periodo.data_final || filtros?.data_final || ''
                }
            };

            return formattedResponse;
        } catch (error) {
            console.error('Erro ao buscar dashboard do contrato:', error);
            throw new Error('Falha ao carregar dados do contrato');
        }
    },

    buscarTudo: async (
        numeroContrato: string,
        filtros?: DashboardFiltros
    ): Promise<ContratoExpandido> => {
        try {
            const [contrato, dashboard] = await Promise.all([
                contratosService.listar().then(contratos =>
                    contratos.find(c => c.contrato === numeroContrato)
                ),
                contratosService.buscarDashboard(numeroContrato, filtros)
            ]);

            if (!contrato) {
                throw new Error('Contrato não encontrado');
            }

            return {
                ...contrato,
                itens: dashboard.itens,
                notas_fiscais: dashboard.notas_fiscais,
                periodo: dashboard.periodo
            };
        } catch (error) {
            console.error('Erro ao buscar dados completos do contrato:', error);
            throw new Error('Falha ao carregar dados completos do contrato');
        }
    },

    formatarMoeda: (valor: number | string): string => {
        const numero = typeof valor === 'string' ? parseFloat(valor) : valor;
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(numero);
    },

    formatarData: (data: string): string => {
        return new Date(data).toLocaleDateString('pt-BR');
    },

    calcularTotais: (dashboard: DashboardContrato) => {
        return {
            totalNotas: dashboard.notas_fiscais.resumo.total_valor,
            quantidadeItens: dashboard.itens.length,
            quantidadeNotas: dashboard.notas_fiscais.resumo.quantidade_notas
        };
    }
};



export const contasReceberService = {
    atualizarStatus: async (tituloId: number, novoStatus: string) => {
        try {
            console.log('Enviando requisição PATCH:', { tituloId, novoStatus });
            const response = await api.patch(`/contas_receber/${tituloId}/atualizar_status/`, {
                status: novoStatus
            });
            
            console.log('Resposta recebida:', response.data);
            return response.data;
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    },

    buscarPorCliente: async (clienteId: number, filtros?: DashboardFiltros
    ): Promise<ContasReceberResponse> => {

        const params = new URLSearchParams();

            if (filtros?.data_inicial) {
                params.append('data_inicial', filtros.data_inicial);
            }
            if (filtros?.data_final) {
                params.append('data_final', filtros.data_final);
            }
        const response = await api.get<ContasReceberResponse>(`/contas_receber/por-cliente/${clienteId}/`,                
            { params }
        );
        return response.data;
    },
};


export const contasPagarService = {
    atualizarStatus: async (tituloId: number, novoStatus: string) => {
        try {
            console.log('Enviando requisição PATCH:', { tituloId, novoStatus });
            const response = await api.patch(`/contas_pagar/${tituloId}/atualizar_status/`, {
                status: novoStatus
            });
            
            console.log('Resposta recebida:', response.data);
            return response.data;
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    },

    
    buscarPorFornecedor: (fornecedorId: number) => 
        api.get<ContasPagarResponse>(`/contas_pagar/por-fornecedor/${fornecedorId}/`),
    
    listarTodas: (dataInicial: string = '2024-01-01') => 
        api.get<ContasPagarResponse>(`/contas_pagar/dashboard/?data_inicial=${dataInicial}`),

    buscarVencidas: () => 
        api.get<ContasPagarResponse>('/contas_pagar/vencidos/')
};


export const financeiroDashboard = {
    resumoGeral: async (filters: FilterParams): Promise<DashboardResponse> => {
        try {
            const params = new URLSearchParams({
                data_inicial: filters.dataInicial,
                data_final: filters.dataFinal,
                status: filters.status,
                ...(filters.searchTerm ? { searchTerm: filters.searchTerm } : {})
            });

            const [contasReceber, contasPagar] = await Promise.all([
                api.get<ContasReceberResponse>(`/contas_receber/dashboard/?${params}`),
                api.get<ContasPagarResponse>(`/contas_pagar/dashboard/?${params}`)
            ]);

            return {
                contasReceber: contasReceber.data,
                contasPagar: contasPagar.data,
                saldo: {
                    total_atrasado: 
                        contasReceber.data.resumo.total_atrasado - 
                        contasPagar.data.resumo.total_atrasado,
                    total_pago_periodo: 
                        contasReceber.data.resumo.total_pago_periodo - 
                        contasPagar.data.resumo.total_pago_periodo,
                    total_cancelado_periodo: 
                        contasReceber.data.resumo.total_cancelado_periodo - 
                        contasPagar.data.resumo.total_cancelado_periodo,
                    total_aberto_periodo: 
                        contasReceber.data.resumo.total_aberto_periodo - 
                        contasPagar.data.resumo.total_aberto_periodo,
                    quantidade_titulos: 
                        contasReceber.data.resumo.quantidade_titulos + 
                        contasPagar.data.resumo.quantidade_titulos,
                    quantidade_atrasados: 
                        contasReceber.data.resumo.quantidade_atrasados_periodo + 
                        contasPagar.data.resumo.quantidade_atrasados_periodo
                }
            };
        } catch (error) {
            console.error('Erro ao buscar dados financeiros:', error);
            throw new Error('Falha ao carregar dados financeiros');
        }
    },

    porCliente: async (clienteId: string) => {
        try {
            const response = await api.get<ContasReceberResponse>(
                `/contas_receber/por-cliente/${clienteId}/`
            );
            return response.data;
        } catch (error) {
            console.error('Erro ao buscar contas do cliente:', error);
            throw new Error('Falha ao carregar contas do cliente');
        }
    },

    porFornecedor: async (fornecedorId: string) => {
        try {
            const response = await api.get<ContasPagarResponse>(
                `/contas_pagar/por-fornecedor/${fornecedorId}/`
            );
            return response.data;
        } catch (error) {
            console.error('Erro ao buscar contas do fornecedor:', error);
            throw new Error('Falha ao carregar contas do fornecedor');
        }
    }
};


// Helpers de formatação
export const formatarMoeda = (valor: string | number | undefined): string => {
    if (!valor) return 'R$ 0,00';
    const numero = Number(valor);
    if (isNaN(numero)) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(numero);
};

export const formatarData = (data: string | undefined): string => {
    if (!data) return '-';
    return new Date(data).toLocaleDateString('pt-BR');
};

export const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
        case 'atrasado':
            return 'bg-red-100 text-red-800';
        case 'recebido':
        case 'pago':
            return 'bg-green-100 text-green-800';
        default:
            return 'bg-yellow-100 text-yellow-800';
    }
};

// Interface para o serviço
export const notasFiscaisService = {
    listar: async (filtros?: NotaFiscalFiltros): Promise<NotaFiscalResponse> => {
        const params = new URLSearchParams();
        if (filtros) {
            Object.entries(filtros).forEach(([key, value]) => {
                if (value) params.append(key, value.toString());
            });
        }
        const response = await api.get<NotaFiscalResponse>('/notas_fiscais_saida/', { params });
        return response.data;
    },

    buscarPorId: async (id: number): Promise<NotaFiscalSaida> => {
        const response = await api.get<NotaFiscalSaida>(`/notas_fiscais_saida/${id}/`);
        return response.data;
    },

    buscarPorNumero: async (numeroNota: string): Promise<NotaFiscalSaida> => {
        const response = await api.get<NotaFiscalSaida>(`/notas_fiscais_saida/numero/${numeroNota}/`);
        return response.data;
    },

    buscarPorContrato: async (
        numeroContrato: string,
        filtros?: NotaFiscalFiltros
    ): Promise<NotaFiscalResponse> => {
        const params = new URLSearchParams();
        if (filtros) {
            Object.entries(filtros).forEach(([key, value]) => {
                if (value) params.append(key, value.toString());
            });
        }
        const response = await api.get<NotaFiscalResponse>(
            `/notas_fiscais_saida/contrato/${numeroContrato}/`,
            { params }
        );
        return response.data;
    },

    buscarAgrupamentos: async (
        filtros?: NotaFiscalFiltros
    ): Promise<NotaFiscalAgrupamento> => {
        const params = new URLSearchParams();
        if (filtros) {
            Object.entries(filtros).forEach(([key, value]) => {
                if (value) params.append(key, value.toString());
            });
        }
        const response = await api.get<NotaFiscalAgrupamento>(
            '/notas_fiscais_saida/agrupamentos/',
            { params }
        );
        return response.data;
    },

    // Funções auxiliares
    formatarValor: (valor: number): string => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    },

    formatarData: (data: string): string => {
        return new Date(data).toLocaleDateString('pt-BR');
    }
};
