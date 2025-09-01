// src/services/api.ts
import { Cliente, ContasPagarResponse, ContasReceberResponse, Contrato, ContratoExpandido, DashboardContrato, DashboardFiltros, DashboardResponse, FilterParams, ItemContrato, Produto } from '@/types/models';
import { NotaFiscalAgrupamento, NotaFiscalFiltros, NotaFiscalResponse, NotaFiscalSaida } from '@/types/notas_fiscais/models';
import axios from 'axios';
import config from '@/config';

// Use unified baseURL from config (env-driven). In dev, Vite proxy handles CORS.
export const api = axios.create({
    baseURL: config.api.baseURL,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Helper genérico: tenta via baseURL (p.ex. /contas) e, se 404/400, tenta na raiz do host
async function getWithFallback<T>(relativePath: string, params?: URLSearchParams | Record<string, any>): Promise<T> {
    try {
        const response = await api.get<T>(relativePath, { params: params as any });
        return response.data as T;
    } catch (err: any) {
        const status = err?.response?.status;
        if (status !== 404 && status !== 400) throw err;
        let origin = '';
        try {
            const u = new URL(config.api.baseURL);
            origin = u.origin;
        } catch {
            origin = 'http://127.0.0.1:8000';
        }
        const response2 = await axios.get<T>(`${origin}${relativePath}`, { params: params as any });
        return response2.data as T;
    }
}

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

    // Novo endpoint otimizado para suprimentos
    buscarSuprimentos: async (filtros: {
        data_inicial: string;
        data_final: string;
        contrato_id?: string;
        cliente_id?: string;
    }) => {
        const params = new URLSearchParams();
        Object.entries(filtros).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                params.append(key, value.toString());
            }
        });
        const response = await api.get(`/contratos_locacao/suprimentos/?${params}`);
        return response.data;
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
    excluir: async (tituloId: number) => {
        try {
            const response = await api.delete(`/contas_receber/${tituloId}/`);
            return response.data;
        } catch (error) {
            console.error('Erro ao excluir título a receber:', error);
            throw error;
        }
    },
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

    listarTodas: async (dataInicial: string = '2024-01-01', dataFinal: string = '2024-12-31') => {
        const response = await api.get<ContasReceberResponse>(`/contas_receber/dashboard/?data_inicio=${dataInicial}&data_fim=${dataFinal}`);
        return response.data;
    },  
};


export const contasPagarService = {
    excluir: async (tituloId: number) => {
        try {
            const response = await api.delete(`/contas_pagar/${tituloId}/`);
            return response.data;
        } catch (error) {
            console.error('Erro ao excluir título a pagar:', error);
            throw error;
        }
    },
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
    
    listarTodas: (dataInicial: string = '2024-01-01', dataFinal: string = '2024-12-31') => 
        api.get<ContasPagarResponse>(`/contas_pagar/dashboard/?data_inicio=${dataInicial}&data_fim=${dataFinal}`),

    buscarVencidas: () => 
        api.get<ContasPagarResponse>('/contas_pagar/vencidos/')
};


export const financeiroDashboard = {
    resumoGeral: async (filters: FilterParams): Promise<DashboardResponse> => {
        try {
            const params = new URLSearchParams({
                data_inicio: filters.dataInicial,
                data_fim: filters.dataFinal,
                ...(filters.status && filters.status !== 'all' ? { status: filters.status } : {}),
                ...(filters.searchTerm ? { searchTerm: filters.searchTerm } : {})
            });

            console.log('🏦 Parâmetros enviados para API:', Object.fromEntries(params));

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
    // Helper: normaliza respostas (paginação DRF ou lista crua)
    _normalizeLista(resp: any): NotaFiscalResponse {
        const toNum = (v: any): number => {
            if (v === null || v === undefined) return 0;
            const n = typeof v === 'number' ? v : Number(String(v).replace(/[^0-9.-]/g, ''));
            return isNaN(n) ? 0 : n;
        };
        if (Array.isArray(resp)) {
            const results = resp as unknown as NotaFiscalSaida[];
            const count = results.length;
            const valor_total = results.reduce((acc, n) => acc + toNum((n as any).valor_total_nota), 0);
            const valor_produtos = results.reduce((acc, n) => acc + toNum((n as any).valor_produtos), 0);
            const valor_frete = results.reduce((acc, n) => acc + toNum((n as any).valor_frete), 0);
            // muitos backends não fornecem esses totais; preenchemos o básico
            return {
                count,
                next: null,
                previous: null,
                results,
                totais: {
                    quantidade_notas: count,
                    valor_total,
                    valor_produtos,
                    valor_impostos: 0,
                    valor_frete,
                },
            } as NotaFiscalResponse;
        }
        // Já está no formato esperado
        return resp as NotaFiscalResponse;
    },
    listar: async (filtros?: NotaFiscalFiltros): Promise<NotaFiscalResponse> => {
        const params = new URLSearchParams();
        if (filtros) {
            Object.entries(filtros).forEach(([key, value]) => {
                if (value !== undefined && value !== null) params.append(key, value.toString());
            });
        }
    const resp = await getWithFallback<NotaFiscalResponse | NotaFiscalSaida[]>('/notas_fiscais_venda/', params);
    return notasFiscaisService._normalizeLista(resp);
    },

    buscarPorId: async (id: number): Promise<NotaFiscalSaida> => {
    return await getWithFallback<NotaFiscalSaida>(`/notas_fiscais_venda/${id}/`);
    },

    buscarPorNumero: async (numeroNota: string): Promise<NotaFiscalSaida> => {
    // Algumas APIs não expõem detalhe por número; filtra via listagem e retorna o primeiro registro
    const params = new URLSearchParams();
    params.append('numero_nota', numeroNota);
    const resp = await getWithFallback<NotaFiscalResponse | NotaFiscalSaida[]>(`/notas_fiscais_venda/`, params);
    const normalized = notasFiscaisService._normalizeLista(resp);
    const first = (normalized.results || []).find(n => String((n as any).numero_nota) === String(numeroNota));
    if (!first) throw new Error('Nota fiscal não encontrada');
    return first as NotaFiscalSaida;
    },

    buscarPorContrato: async (
        numeroContrato: string,
        filtros?: NotaFiscalFiltros
    ): Promise<NotaFiscalResponse> => {
        const params = new URLSearchParams();
        if (filtros) {
            Object.entries(filtros).forEach(([key, value]) => {
                if (value !== undefined && value !== null) params.append(key, value.toString());
            });
        }
        // A API não tem endpoint dedicado; usar query param
        params.append('contrato', numeroContrato);
        const resp = await getWithFallback<NotaFiscalResponse | NotaFiscalSaida[]>(`/notas_fiscais_venda/`, params);
        return notasFiscaisService._normalizeLista(resp);
    },

    buscarAgrupamentos: async (
        filtros?: NotaFiscalFiltros
    ): Promise<NotaFiscalAgrupamento> => {
        const params = new URLSearchParams();
        if (filtros) {
            Object.entries(filtros).forEach(([key, value]) => {
                if (value !== undefined && value !== null) params.append(key, value.toString());
            });
        }
    return await getWithFallback<NotaFiscalAgrupamento>(
            '/notas_fiscais_venda/agrupamentos/',
            params
        );
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

