// src/services/financialService.ts
import config from '@/config';
import { Filtros } from '@/types/dashboardNovo';
import { FluxoCaixaFiltros } from '@/types/financeiro';
import { DashboardResponse2, FilterParams2, PaymentData } from '@/types/models';
import axios, { AxiosInstance } from 'axios';
import type {
    DashboardOperacional as DOperacional,
    DashboardEstrategico as DEstrategico,
    DashboardGerencial as DGerencial,
    DashboardResume,
    Recomendacao,
} from '@/types/dashboardNovo';

interface DateRange {
    inicio: string;
    fim: string;
}



class FinancialService {
    private api!: AxiosInstance;

    constructor() {
        this.api = axios.create({
            baseURL: config.api.baseURL,
            timeout: config.api.timeout,
            headers: {
                'Content-Type': 'application/json',
                //...config.api.defaultHeaders
            }
        });

        // Interceptor de resposta para tratamento de erros
        this.api.interceptors.response.use(
            response => response,
            error => {
                // Log do erro se estiver em desenvolvimento
                if (config.env === 'development') {
                    console.error('API Error:', error);
                }

                if (error.response) {
                    throw new Error(error.response.data.error || 'Erro no servidor');
                }
                if (error.request) {
                    throw new Error('Erro de conexão com o servidor');
                }
                throw error;
            }
        );

        // Interceptor de requisição para adicionar tokens ou outros headers
        this.api.interceptors.request.use(
            requestConfig => {
                // Adiciona token de autenticação se existir
                if (config.api.authToken) {
                    requestConfig.headers.Authorization = `Bearer ${config.api.authToken}`;
                }
                return requestConfig;
            },
            error => {
                return Promise.reject(error);
            }
        );
    }

    // Exemplo de método usando timeout específico
    async getLargeReport(filtros: DateRange) {
    const { data } = await this.api.get('fluxo-caixa/large-report/', {
            params: filtros,
            timeout: config.api.longTimeout // Timeout maior para relatórios grandes
        });
        return data;
    }

    // Dashboard Operacional
    async getDashboardOperacional(filtros: Filtros): Promise<DOperacional> {
        console.log('🚀 Iniciando getDashboardOperacional com filtros:', filtros);
        const params = this.convertFilters(filtros);
        console.log('🔍 Buscando dados operacionais com parâmetros:', params);
        
        // Preferir endpoint dedicado do fluxo de caixa; o proxy Vite usa /contas como baseURL
        const resp = await this.api.get('fluxo-caixa/operacional/', {
            params,
            validateStatus: () => true,
        });
        
        console.log('📊 Resposta fluxo-caixa/operacional:', resp.status, resp.data);
        
        if (resp.status >= 200 && resp.status < 300) {
            const data = resp.data as DOperacional;
            if (data && data.resumo && data.totalizadores) {
                console.log('✅ Dados operacionais encontrados no formato correto');

                // Enriquecer/normalizar totalizadores com dados reais de contas a receber e a pagar
                try {
                    const [recebResp, pagarResp] = await Promise.all([
                        this.api.get('contas_receber/dashboard/', { params }),
                        this.api.get('contas_pagar/dashboard/', { params })
                    ]);

                    const rResumo = recebResp.data?.resumo || {};
                    const pResumo = pagarResp.data?.resumo || {};
                    const rPagos = Array.isArray(recebResp.data?.titulos_pagos_periodo) ? recebResp.data.titulos_pagos_periodo : [];
                    const rAbertos = Array.isArray(recebResp.data?.titulos_abertos_periodo) ? recebResp.data.titulos_abertos_periodo : [];
                    const pPagos = Array.isArray(pagarResp.data?.titulos_pagos_periodo) ? pagarResp.data.titulos_pagos_periodo : [];
                    const pAbertos = Array.isArray(pagarResp.data?.titulos_abertos_periodo) ? pagarResp.data.titulos_abertos_periodo : [];

                    // Conversor seguro para valores monetários vindos como string ("706.841,09"/"706,841.09"/"706841.09")
                    const toNumber = (v: any): number => {
                        if (typeof v === 'number') return v;
                        if (typeof v !== 'string') return 0;
                        const s = v.replace(/[^0-9,.-]/g, '');
                        // Se tem vírgula e ponto, assumir vírgula como decimal quando vírgula vier por último
                        if (/,\d{1,2}$/.test(s) && s.includes('.')) {
                            return Number(s.replace(/\./g, '').replace(',', '.')) || 0;
                        }
                        // Caso apenas vírgula seja decimal
                        if (/,\d{1,2}$/.test(s)) {
                            return Number(s.replace(',', '.')) || 0;
                        }
                        return Number(s) || 0;
                    };
                    const sumValores = (itens: any[], campo: string): number =>
                        itens.reduce((acc, it) => acc + toNumber(it[campo] ?? it.valor), 0);
                    
                    // Mantém coerência: se usarmos array para valor, usamos array para quantidade; caso contrário, caímos para resumo
                    const pairFrom = (
                        arr: any[],
                        valueField: string,
                        resumoValor?: any,
                        resumoQuantidade?: any
                    ) => {
                        if (Array.isArray(arr) && arr.length > 0) {
                            return {
                                valor: sumValores(arr, valueField),
                                quantidade: arr.length
                            };
                        }
                        const v = Number(resumoValor) || 0;
                        return {
                            valor: v,
                            quantidade: v > 0 ? (Number(resumoQuantidade) || 0) : 0
                        };
                    };
                    
                    const entradasRealizadas = pairFrom(rPagos, 'valor_total_pago', rResumo.total_pago_periodo, rResumo.quantidade_pagos_periodo);
                    const entradasPrevistas = pairFrom(rAbertos, 'valor', rResumo.total_aberto_periodo, rResumo.quantidade_abertos_periodo);
                    const saidasRealizadas = pairFrom(pPagos, 'valor_total_pago', pResumo.total_pago_periodo, pResumo.quantidade_pagos_periodo);
                    const saidasPrevistas = pairFrom(pAbertos, 'valor', pResumo.total_aberto_periodo, pResumo.quantidade_abertos_periodo);

                    // Montar lista de movimentos (entradas/saídas) a partir de títulos
                    const movimentos: any[] = [
                        // Entradas realizadas (receber pagos)
                        ...rPagos.map((t: any) => ({
                            id: t.id,
                            data: t.data_pagamento || t.vencimento || t.data_vencimento || new Date().toISOString(),
                            descricao: t.historico || `Cliente: ${t.cliente?.nome || 'Não informado'}`,
                            tipo: 'entrada' as const,
                            valor: toNumber(t.valor_total_pago ?? t.valor),
                            categoria: 'contas_receber',
                            realizado: true,
                            fonte_tipo: 'contas_receber',
                            fonte_id: t.id,
                        })),
                        // Entradas previstas (receber abertos)
                        ...rAbertos.map((t: any) => ({
                            id: t.id,
                            data: t.vencimento || t.data_vencimento || new Date().toISOString(),
                            descricao: t.historico || `Cliente: ${t.cliente?.nome || 'Não informado'}`,
                            tipo: 'entrada' as const,
                            valor: toNumber(t.valor),
                            categoria: 'contas_receber',
                            realizado: !!t.data_pagamento && t.status === 'P',
                            fonte_tipo: 'contas_receber',
                            fonte_id: t.id,
                        })),
                        // Saídas realizadas (pagar pagos)
                        ...pPagos.map((t: any) => ({
                            id: t.id,
                            data: t.data_pagamento || t.vencimento || t.data_vencimento || new Date().toISOString(),
                            descricao: t.historico || `Fornecedor: ${t.fornecedor?.nome || 'Não informado'}`,
                            tipo: 'saida' as const,
                            valor: toNumber(t.valor_total_pago ?? t.valor),
                            categoria: 'contas_pagar',
                            realizado: true,
                            fonte_tipo: 'contas_pagar',
                            fonte_id: t.id,
                        })),
                        // Saídas previstas (pagar abertos)
                        ...pAbertos.map((t: any) => ({
                            id: t.id,
                            data: t.vencimento || t.data_vencimento || new Date().toISOString(),
                            descricao: t.historico || `Fornecedor: ${t.fornecedor?.nome || 'Não informado'}`,
                            tipo: 'saida' as const,
                            valor: toNumber(t.valor),
                            categoria: 'contas_pagar',
                            realizado: !!t.data_pagamento && t.status === 'P',
                            fonte_tipo: 'contas_pagar',
                            fonte_id: t.id,
                        })),
                    ];

                    const enriched: DOperacional = {
                        ...data,
                        totalizadores: {
                            ...data.totalizadores,
                            entradas_realizadas: {
                                valor: entradasRealizadas.valor || Number(data.totalizadores?.entradas_realizadas?.valor) || 0,
                                // quantidade deve refletir TÍTULOS PAGOS no período (coerente com origem do valor)
                                quantidade: entradasRealizadas.valor > 0
                                    ? (entradasRealizadas.quantidade || Number(data.totalizadores?.entradas_realizadas?.quantidade) || 0)
                                    : 0,
                                percentual: data.totalizadores?.entradas_realizadas?.percentual ?? null,
                            },
                            entradas_previstas: {
                                valor: entradasPrevistas.valor || Number(data.totalizadores?.entradas_previstas?.valor) || 0,
                                // quantidade prevista deve refletir TÍTULOS ABERTOS no período (coerente com origem do valor)
                                quantidade: entradasPrevistas.valor > 0
                                    ? (entradasPrevistas.quantidade || Number(data.totalizadores?.entradas_previstas?.quantidade) || 0)
                                    : 0,
                                percentual: data.totalizadores?.entradas_previstas?.percentual ?? null,
                            },
                            saidas_realizadas: {
                                valor: saidasRealizadas.valor || Number(data.totalizadores?.saidas_realizadas?.valor) || 0,
                                quantidade: saidasRealizadas.valor > 0
                                    ? (saidasRealizadas.quantidade || Number(data.totalizadores?.saidas_realizadas?.quantidade) || 0)
                                    : 0,
                                percentual: data.totalizadores?.saidas_realizadas?.percentual ?? null,
                            },
                            saidas_previstas: {
                                valor: saidasPrevistas.valor || Number(data.totalizadores?.saidas_previstas?.valor) || 0,
                                quantidade: saidasPrevistas.valor > 0
                                    ? (saidasPrevistas.quantidade || Number(data.totalizadores?.saidas_previstas?.quantidade) || 0)
                                    : 0,
                                percentual: data.totalizadores?.saidas_previstas?.percentual ?? null,
                            },
                        },
                        movimentos,
                    } as DOperacional;

                    console.log('🧮 Totalizadores enriquecidos (operacional):', enriched.totalizadores);
                    console.log('🔢 Debug Entradas Realizadas -> valor/quantidade', {
                        valor: enriched.totalizadores.entradas_realizadas.valor,
                        quantidade: enriched.totalizadores.entradas_realizadas.quantidade,
                        pagosArray: rPagos?.length || 0,
                        resumoTotalPago: rResumo.total_pago_periodo
                    });
                    return enriched;
                } catch (e) {
                    console.warn('⚠️ Falha ao enriquecer totalizadores, retornando dados originais:', e);
                    return data;
                }
            }
            // Continua para o mapeamento genérico abaixo
        } else {
            // Fallback: tentar endpoint legado com dados de contas a receber E pagar
            console.log('⚠️ Endpoint fluxo-caixa indisponível, usando fallback contas_receber/dashboard + contas_pagar/dashboard');
            
            // Buscar dados em paralelo
            const [receivablesResp, payablesResp] = await Promise.all([
                this.api.get('contas_receber/dashboard/', { params }),
                this.api.get('contas_pagar/dashboard/', { params })
            ]);
            
            const fb = receivablesResp;
            const contasPagar = payablesResp;
            
            console.log('📋 Status da resposta fallback (receber):', fb.status);
            console.log('📋 Status da resposta fallback (pagar):', contasPagar.status);
            console.log('📋 Dados brutos recebidos (receber):', fb.data);
            console.log('📋 Dados brutos recebidos (pagar):', contasPagar.data);
            
            // Extrair valores reais dos dados recebidos
            const resumoData = fb.data?.resumo || {};
            const resumoContasPagar = contasPagar.data?.resumo || {};
            const recebPagos = Array.isArray(fb.data?.titulos_pagos_periodo) ? fb.data.titulos_pagos_periodo : [];
            const recebAbertos = Array.isArray(fb.data?.titulos_abertos_periodo) ? fb.data.titulos_abertos_periodo : [];
            const pagarPagos = Array.isArray(contasPagar.data?.titulos_pagos_periodo) ? contasPagar.data.titulos_pagos_periodo : [];
            const pagarAbertos = Array.isArray(contasPagar.data?.titulos_abertos_periodo) ? contasPagar.data.titulos_abertos_periodo : [];
            const movimentosData = recebAbertos;
            
            console.log('💰 Resumo financeiro extraído (receber):', resumoData);
            console.log('💰 Resumo financeiro extraído (pagar):', resumoContasPagar);
            console.log('� Movimentos encontrados:', movimentosData.length);
            
            if (movimentosData.length > 0) {
                console.log('📄 Primeiro movimento bruto:', movimentosData[0]);
                console.log('📄 Últimos 3 movimentos brutos:', movimentosData.slice(-3));
                
                // Filtrar apenas títulos com valor positivo e de 2024 em diante
                const titulosValidos = movimentosData.filter((titulo: any) => {
                    const valor = Number(titulo.valor) || 0;
                    const vencimento = titulo.vencimento || '';
                    return valor > 0 && (vencimento.includes('2024') || vencimento.includes('2025'));
                });
                
                console.log('📄 Títulos filtrados (valor > 0 e 2024+):', titulosValidos.length);
                if (titulosValidos.length > 0) {
                    console.log('📄 Exemplo de título válido:', titulosValidos[0]);
                }
            }
            
            return {
                filtros,
                resumo: {
                    saldo_inicial: Number(resumoData.saldo_inicial) || 0,
                    saldo_final: Number(resumoData.total_aberto_periodo) || 0,
                    saldo_projetado: Number(resumoData.total_aberto_periodo) + Number(resumoData.total_pago_periodo) || 0,
                    variacao_percentual: 0,
                    entradas_total: Number(resumoData.total_pago_periodo) || 0,
                    saidas_total: Number(resumoData.total_cancelado_periodo) || 0,
                    vendas_equipamentos: Number(resumoData.total_pago_periodo) * 0.3 || 0,
                    alugueis_ativos: Number(resumoData.quantidade_titulos) || 0,
                    contratos_renovados: Number(resumoData.quantidade_titulos) * 0.1 || 0,
                    servicos_total: Number(resumoData.total_pago_periodo) * 0.2 || 0,
                    suprimentos_total: Number(resumoData.total_pago_periodo) * 0.1 || 0,
                    receitas_detalhadas: {
                        vendas: Number(resumoData.total_pago_periodo) * 0.3 || 0,
                        locacao: Number(resumoData.total_pago_periodo) * 0.4 || 0,
                        servicos: Number(resumoData.total_pago_periodo) * 0.2 || 0,
                        manutencao: Number(resumoData.total_pago_periodo) * 0.05 || 0,
                        suprimentos: Number(resumoData.total_pago_periodo) * 0.05 || 0,
                    }
                } as DashboardResume,
                totalizadores: {
                    entradas_realizadas: {
                            valor: Number(resumoData.total_pago_periodo) || recebPagos.reduce((a: number, t: any) => a + (Number(t.valor_total_pago) || Number(t.valor) || 0), 0),
                            // quantidade deve considerar apenas títulos PAGOS
                            quantidade: (recebPagos?.length ?? 0) || Number(resumoData.quantidade_pagos_periodo) || 0,
                            percentual: null,
                        },
                        entradas_previstas: {
                            valor: Number(resumoData.total_aberto_periodo) || recebAbertos.reduce((a: number, t: any) => a + (Number(t.valor) || 0), 0),
                            // quantidade prevista = títulos ABERTOS no período
                            quantidade: (recebAbertos?.length ?? 0) || Number(resumoData.quantidade_abertos_periodo) || 0,
                            percentual: null,
                        },
                        saidas_realizadas: {
                            valor: Number(resumoContasPagar.total_pago_periodo) || pagarPagos.reduce((a: number, t: any) => a + (Number(t.valor_total_pago) || Number(t.valor) || 0), 0),
                            quantidade: (pagarPagos?.length ?? 0) || Number(resumoContasPagar.quantidade_pagos_periodo) || 0,
                            percentual: null,
                        },
                        saidas_previstas: {
                            valor: Number(resumoContasPagar.total_aberto_periodo) || pagarAbertos.reduce((a: number, t: any) => a + (Number(t.valor) || 0), 0),
                            quantidade: (pagarAbertos?.length ?? 0) || Number(resumoContasPagar.quantidade_abertos_periodo) || 0,
                            percentual: null,
                        },
                },
                movimentos: (() => {
                    const toNumber = (v: any) => {
                        if (typeof v === 'number') return v;
                        if (typeof v !== 'string') return 0;
                        const s = v.replace(/[^0-9,.-]/g, '');
                        if (/,\d{1,2}$/.test(s) && s.includes('.')) return Number(s.replace(/\./g, '').replace(',', '.')) || 0;
                        if (/,\d{1,2}$/.test(s)) return Number(s.replace(',', '.')) || 0;
                        return Number(s) || 0;
                    };
                    const mapReceb = (t: any, realizado: boolean) => ({
                        id: t.id,
                        data: (realizado ? t.data_pagamento : (t.vencimento || t.data_vencimento)) || new Date().toISOString(),
                        descricao: t.historico || `Cliente: ${t.cliente?.nome || 'Não informado'}`,
                        tipo: 'entrada' as const,
                        valor: toNumber(realizado ? (t.valor_total_pago ?? t.valor) : t.valor),
                        categoria: 'contas_receber',
                        realizado,
                        fonte_tipo: 'contas_receber',
                        fonte_id: t.id,
                    });
                    const mapPagar = (t: any, realizado: boolean) => ({
                        id: t.id,
                        data: (realizado ? t.data_pagamento : (t.vencimento || t.data_vencimento)) || new Date().toISOString(),
                        descricao: t.historico || `Fornecedor: ${t.fornecedor?.nome || 'Não informado'}`,
                        tipo: 'saida' as const,
                        valor: toNumber(realizado ? (t.valor_total_pago ?? t.valor) : t.valor),
                        categoria: 'contas_pagar',
                        realizado,
                        fonte_tipo: 'contas_pagar',
                        fonte_id: t.id,
                    });
                    const entradas = [
                        ...recebPagos.map((t: any) => mapReceb(t, true)),
                        ...recebAbertos.map((t: any) => mapReceb(t, false)),
                    ];
                    const saidas = [
                        ...pagarPagos.map((t: any) => mapPagar(t, true)),
                        ...pagarAbertos.map((t: any) => mapPagar(t, false)),
                    ];
                    const all = [...entradas, ...saidas];
                    console.log('📄 Movimentos combinados (entradas/saídas):', all.length);
                    return all;
                })(),
                categorias_encontradas: ['vendas', 'locacao', 'servicos', 'manutencao', 'suprimentos'],
            };
        }
        const data = resp.data;
        // Fallback: mapear um payload genérico do dashboard (quando retornou 200 mas num formato antigo)
        const resumo: DashboardResume = {
            saldo_inicial: Number(data?.resumo?.saldo_inicial) || 0,
            saldo_final: Number(data?.resumo?.saldo_final) || 0,
            saldo_projetado: Number(data?.resumo?.saldo_projetado) || 0,
            variacao_percentual: Number(data?.resumo?.variacao_percentual) || 0,
            entradas_total: Number(data?.resumo?.entradas_total) || 0,
            saidas_total: Number(data?.resumo?.saidas_total) || 0,
            vendas_equipamentos: Number(data?.resumo?.vendas_equipamentos) || 0,
            alugueis_ativos: Number(data?.resumo?.alugueis_ativos) || 0,
            contratos_renovados: Number(data?.resumo?.contratos_renovados) || 0,
            servicos_total: Number(data?.resumo?.servicos_total) || 0,
            suprimentos_total: Number(data?.resumo?.suprimentos_total) || 0,
            receitas_detalhadas: {
                vendas: Number(data?.categorias?.vendas_equipamentos?.entradas) || 0,
                locacao: Number(data?.categorias?.aluguel_equipamentos?.entradas) || 0,
                servicos: Number(data?.categorias?.servicos_manutencao?.entradas) || 0,
                manutencao: Number(data?.categorias?.manutencao?.entradas) || 0,
                suprimentos: Number(data?.categorias?.suprimentos?.entradas) || 0,
            }
        } as DashboardResume;

        return {
            filtros,
            resumo,
            totalizadores: {
                entradas_realizadas: {
                    valor: Number(data?.totalizadores?.entradas_realizadas?.valor) || 0,
                    quantidade: Number(data?.totalizadores?.entradas_realizadas?.quantidade) || 0,
                    percentual: data?.totalizadores?.entradas_realizadas?.percentual ?? null,
                },
                entradas_previstas: {
                    valor: Number(data?.totalizadores?.entradas_previstas?.valor) || 0,
                    quantidade: Number(data?.totalizadores?.entradas_previstas?.quantidade) || 0,
                    percentual: data?.totalizadores?.entradas_previstas?.percentual ?? null,
                },
                saidas_realizadas: {
                    valor: Number(data?.totalizadores?.saidas_realizadas?.valor) || 0,
                    quantidade: Number(data?.totalizadores?.saidas_realizadas?.quantidade) || 0,
                    percentual: data?.totalizadores?.saidas_realizadas?.percentual ?? null,
                },
                saidas_previstas: {
                    valor: Number(data?.totalizadores?.saidas_previstas?.valor) || 0,
                    quantidade: Number(data?.totalizadores?.saidas_previstas?.quantidade) || 0,
                    percentual: data?.totalizadores?.saidas_previstas?.percentual ?? null,
                },
            },
            movimentos: Array.isArray(data?.movimentos) ? data.movimentos : [],
            categorias_encontradas: Object.keys(data?.categorias || {}),
        };
    }

    // Dashboard Estratégico
    async getDashboardEstrategico(filtros: Filtros): Promise<DEstrategico> {
        const params = this.convertFilters(filtros);
    const resp = await this.api.get('fluxo-caixa/estrategico/', {
            params,
            validateStatus: () => true,
        });
        if (resp.status >= 200 && resp.status < 300) {
            const data = resp.data;
            if (data && data.dre && data.indicadores) {
                return data as DEstrategico;
            }
            return {
                dre: {
                    receita_bruta: Number(data?.dre?.receita_bruta) || 0,
                    receita_liquida: Number(data?.dre?.receita_liquida) || 0,
                    custos_operacionais: Number(data?.dre?.custos_operacionais) || 0,
                    despesas_operacionais: Number(data?.dre?.despesas_operacionais) || 0,
                    resultado_operacional: Number(data?.dre?.resultado_operacional) || 0,
                    resultado_antes_impostos: Number(data?.dre?.resultado_antes_impostos) || 0,
                    impostos: Number(data?.dre?.impostos) || 0,
                    resultado_liquido: Number(data?.dre?.resultado_liquido) || 0,
                },
                tendencias: {
                    receitas: Array.isArray(data?.tendencias?.receitas) ? data.tendencias.receitas : [],
                    despesas: Array.isArray(data?.tendencias?.despesas) ? data.tendencias.despesas : [],
                },
                projecoes: {
                    proximos_30_dias: data?.projecoes?.proximos_30_dias || { entradas_total: 0, saídas_total: 0, saldo_projetado: 0 },
                    proximos_90_dias: data?.projecoes?.proximos_90_dias || { entradas_total: 0, saídas_total: 0, saldo_projetado: 0 },
                    proximos_180_dias: data?.projecoes?.proximos_180_dias || { entradas_total: 0, saídas_total: 0, saldo_projetado: 0 },
                },
                indicadores: {
                    liquidez_imediata: Number(data?.indicadores?.liquidez_imediata) || 0,
                    ciclo_caixa: Number(data?.indicadores?.ciclo_caixa) || 0,
                    margem_operacional: Number(data?.indicadores?.margem_operacional) || 0,
                    crescimento_receitas: Number(data?.indicadores?.crescimento_receitas) || 0,
                },
            };
        }
        // Fallback: tentar endpoint legado
        const fb = await this.api.get('contas_receber/dashboard/', { params });
        console.log('📊 Dados estratégicos recebidos:', fb.data);
        
        const resumoData = fb.data?.resumo || {};
        const totalPago = Number(resumoData.total_pago_periodo) || 0;
        const totalAberto = Number(resumoData.total_aberto_periodo) || 0;
        
        return {
            dre: {
                receita_bruta: totalPago,
                receita_liquida: totalPago * 0.92,
                custos_operacionais: totalPago * 0.45,
                despesas_operacionais: totalPago * 0.25,
                resultado_operacional: totalPago * 0.22,
                resultado_antes_impostos: totalPago * 0.20,
                impostos: totalPago * 0.08,
                resultado_liquido: totalPago * 0.12,
            },
            tendencias: {
                receitas: [
                    { periodo: "Jan", valor_realizado: totalPago * 0.08, valor_previsto: totalPago * 0.09 },
                    { periodo: "Fev", valor_realizado: totalPago * 0.09, valor_previsto: totalPago * 0.10 },
                    { periodo: "Mar", valor_realizado: totalPago * 0.10, valor_previsto: totalPago * 0.11 },
                    { periodo: "Abr", valor_realizado: totalPago * 0.08, valor_previsto: totalPago * 0.09 },
                    { periodo: "Mai", valor_realizado: totalPago * 0.12, valor_previsto: totalPago * 0.13 },
                    { periodo: "Jun", valor_realizado: totalPago * 0.11, valor_previsto: totalPago * 0.12 },
                ],
                despesas: [
                    { periodo: "Jan", valor_realizado: totalPago * 0.06, valor_previsto: totalPago * 0.07 },
                    { periodo: "Fev", valor_realizado: totalPago * 0.07, valor_previsto: totalPago * 0.08 },
                    { periodo: "Mar", valor_realizado: totalPago * 0.08, valor_previsto: totalPago * 0.09 },
                    { periodo: "Abr", valor_realizado: totalPago * 0.06, valor_previsto: totalPago * 0.07 },
                    { periodo: "Mai", valor_realizado: totalPago * 0.09, valor_previsto: totalPago * 0.10 },
                    { periodo: "Jun", valor_realizado: totalPago * 0.08, valor_previsto: totalPago * 0.09 },
                ],
            },
            projecoes: {
                proximos_30_dias: { entradas_total: totalAberto * 0.3, saidas_total: totalPago * 0.2, saldo_projetado: totalAberto * 0.3 - totalPago * 0.2 },
                proximos_90_dias: { entradas_total: totalAberto * 0.7, saidas_total: totalPago * 0.5, saldo_projetado: totalAberto * 0.7 - totalPago * 0.5 },
                proximos_180_dias: { entradas_total: totalAberto, saidas_total: totalPago * 0.8, saldo_projetado: totalAberto - totalPago * 0.8 },
            },
            indicadores: {
                liquidez_imediata: 2.5,
                ciclo_caixa: 35,
                margem_operacional: 22.0,
                crescimento_receitas: 8.5,
            },
        };
    }

    // Dashboard Gerencial
    async getDashboardGerencial(filtros: Filtros): Promise<DGerencial> {
        const params = this.convertFilters(filtros);
    const resp = await this.api.get('fluxo-caixa/gerencial/', {
            params,
            validateStatus: () => true,
        });
        if (resp.status >= 200 && resp.status < 300) {
            const data = resp.data;
            if (data && data.resumo && data.tendencias && data.indicadores) {
                return data as DGerencial;
            }
        }
        // Fallback: tentar endpoint legado e mapear estrutura antiga (resumo_periodo/evolucao_diaria/analise_categorias) para a nova
        const fb = await this.api.get('contas_receber/dashboard/', { params });
        console.log('💼 Dados gerenciais recebidos:', fb.data);
        
        const resumoData = fb.data?.resumo || {};
        const totalPago = Number(resumoData.total_pago_periodo) || 0;
        const totalAberto = Number(resumoData.total_aberto_periodo) || 0;
        const totalCancelado = Number(resumoData.total_cancelado_periodo) || 0;
        const quantidadeTitulos = Number(resumoData.quantidade_titulos) || 0;
        
        const atual = {
            entradas: totalPago,
            saidas: totalCancelado,
            resultado: totalPago - totalCancelado
        };
        
        // Simular período anterior com valores proporcionais
        const anterior = {
            entradas: totalPago * 0.85,
            saidas: totalCancelado * 0.9,
            resultado: (totalPago * 0.85) - (totalCancelado * 0.9)
        };
        
        const variacoes = {
            entradas: anterior.entradas ? ((atual.entradas - anterior.entradas) / Math.abs(anterior.entradas)) * 100 : (atual.entradas ? 100 : 0),
            saidas: anterior.saidas ? ((atual.saidas - anterior.saidas) / Math.abs(anterior.saidas)) * 100 : (atual.saidas ? 100 : 0)
        };

        return {
            periodo: {
                mes: new Date(filtros.dataFinal).getMonth() + 1,
                ano: new Date(filtros.dataFinal).getFullYear(),
                inicio: filtros.dataInicial,
                fim: filtros.dataFinal,
            },
            resumo: { atual, anterior, variacoes },
            analise_categorias: [
                {
                    categoria: "Impressoras Locação",
                    entradas: totalPago * 0.4,
                    saidas: totalCancelado * 0.3,
                    quantidade: Math.floor(quantidadeTitulos * 0.4),
                    media_valor: (totalPago * 0.4) / Math.max(Math.floor(quantidadeTitulos * 0.4), 1),
                    realizados: Math.floor(quantidadeTitulos * 0.4 * 0.9),
                },
                {
                    categoria: "Multifuncionais Locação", 
                    entradas: totalPago * 0.35,
                    saidas: totalCancelado * 0.4,
                    quantidade: Math.floor(quantidadeTitulos * 0.35),
                    media_valor: (totalPago * 0.35) / Math.max(Math.floor(quantidadeTitulos * 0.35), 1),
                    realizados: Math.floor(quantidadeTitulos * 0.35 * 0.85),
                },
                {
                    categoria: "Vendas Equipamentos",
                    entradas: totalPago * 0.15,
                    saidas: totalCancelado * 0.2,
                    quantidade: Math.floor(quantidadeTitulos * 0.1),
                    media_valor: (totalPago * 0.15) / Math.max(Math.floor(quantidadeTitulos * 0.1), 1),
                    realizados: Math.floor(quantidadeTitulos * 0.1 * 0.95),
                },
                {
                    categoria: "Serviços Técnicos",
                    entradas: totalPago * 0.1,
                    saidas: totalCancelado * 0.1,
                    quantidade: Math.floor(quantidadeTitulos * 0.15),
                    media_valor: (totalPago * 0.1) / Math.max(Math.floor(quantidadeTitulos * 0.15), 1),
                    realizados: Math.floor(quantidadeTitulos * 0.15 * 0.8),
                }
            ],
            tendencias: {
                historico: [
                    { mes: "2024-01", entradas: totalPago * 0.08, saidas: totalCancelado * 0.1 },
                    { mes: "2024-02", entradas: totalPago * 0.12, saidas: totalCancelado * 0.15 },
                    { mes: "2024-03", entradas: totalPago * 0.15, saidas: totalCancelado * 0.12 },
                    { mes: "2024-04", entradas: totalPago * 0.18, saidas: totalCancelado * 0.18 },
                    { mes: "2024-05", entradas: totalPago * 0.22, saidas: totalCancelado * 0.20 },
                    { mes: "2024-06", entradas: totalPago * 0.25, saidas: totalCancelado * 0.25 },
                ],
                projecoes: {
                    proximas_entradas: totalAberto * 0.6,
                    proximas_saidas: totalPago * 0.15,
                },
            },
            indicadores: {
                margem: atual.entradas > 0 ? (atual.resultado / atual.entradas) : 0,
                realizacao_entradas: 85.2,
                realizacao_saidas: 72.8,
                media_diaria_entradas: atual.entradas / 30,
                media_diaria_saidas: atual.saidas / 30,
            },
            recomendacoes: [
                {
                    tipo: "oportunidade",
                    severidade: "alta" as const,
                    mensagem: "Expansão de Contratos de Locação - Identifique clientes com alto volume de impressão para ofertar planos premium",
                    acoes: ["Analisar histórico de impressão", "Contatar clientes de alto volume", "Preparar propostas personalizadas"]
                },
                {
                    tipo: "atencao",
                    severidade: "media" as const,
                    mensagem: "Gestão de Inadimplência - Monitore títulos em atraso para reduzir perdas financeiras",
                    acoes: ["Revisar títulos em atraso", "Contatar clientes inadimplentes", "Implementar política de cobrança"]
                }
            ] as Recomendacao[],
        };
    }

    // Helper method to convert frontend filters to backend params
    private convertFilters(filtros: Filtros) {
        const params: any = {};
        
        // Para dados históricos, usar janeiro 2024 como data mínima
        const minDate = '2024-01-01';
        const currentDate = new Date().toISOString().split('T')[0]; // Data atual
        
        console.log('🗓️ Convertendo filtros:', { filtros, minDate, currentDate });
        
        // Suportar ambos formatos de datas
        if (filtros.dataInicial) {
            const dataInicial = filtros.dataInicial < minDate ? minDate : filtros.dataInicial;
            params.data_inicio = dataInicial;
            params.data_inicial = dataInicial;
            params.dataInicial = dataInicial;
            console.log('📅 Data inicial definida:', dataInicial);
        } else {
            // Se não tem data inicial, usar janeiro 2024
            params.data_inicio = minDate;
            params.data_inicial = minDate;
            params.dataInicial = minDate;
            console.log('📅 Data inicial padrão:', minDate);
        }
        
        if (filtros.dataFinal) {
            const dataFinal = filtros.dataFinal < minDate ? currentDate : filtros.dataFinal;
            params.data_fim = dataFinal;
            params.data_final = dataFinal;
            params.dataFinal = dataFinal;
            console.log('📅 Data final definida:', dataFinal);
        } else {
            // Se não tem data final, usar data atual
            params.data_fim = currentDate;
            params.data_final = currentDate;
            params.dataFinal = currentDate;
            console.log('📅 Data final padrão:', currentDate);
        }
        
        if (filtros.tipo && filtros.tipo !== 'todos') params.tipo = filtros.tipo;
        if (filtros.fonte && filtros.fonte !== 'todos') params.fonte = filtros.fonte;
        
        console.log('🔄 Parâmetros finais enviados para API:', params);
        return params;
    }

    // Dashboard Consolidado
    async getDashboardConsolidado(periodo: number) {
    const { data } = await this.api.get('fluxo-caixa/dashboard_consolidado/', {
            params: { periodo }
        });
        return data;
    }

    // Saldos
    async getSaldos(filtros: DateRange) {
    const { data } = await this.api.get('fluxo-caixa/saldos/', {
            params: filtros
        });
        return data;
    }

    // Análise Cliente
    async getAnaliseCliente(clienteId: number, periodoMeses: number = 12) {
    const { data } = await this.api.get('fluxo-caixa/analise_cliente/', {
            params: {
                cliente_id: clienteId,
                periodo_meses: periodoMeses
            }
        });
        return data;
    }

    // Ranking Clientes
    async getRankingClientes(periodoMeses: number = 12) {
    const { data } = await this.api.get('fluxo-caixa/ranking_clientes/', {
            params: { periodo_meses: periodoMeses }
        });
        return data;
    }

    // Análise Carteira
    async getAnaliseCarteira() {
    const { data } = await this.api.get('fluxo-caixa/analise_carteira/');
        return data;
    }

    // Indicadores Contratos
    async getIndicadoresContratos() {
    const { data } = await this.api.get('fluxo-caixa/indicadores_contratos/');
        return data;
    }

    // Análise Performance
    async getAnalisePerformance(filtros: FluxoCaixaFiltros) {
    const { data } = await this.api.get('fluxo-caixa/analise_performance/', {
            params: filtros
        });
        return data;
    }

    // DRE
    async getDRE(filtros: DateRange) {
    const { data } = await this.api.get('fluxo-caixa/dre/', {
            params: filtros
        });
        return data;
    }

    // Dashboard Comercial
    async getDashboardComercial(filtros: DateRange) {
    const { data } = await this.api.get('fluxo-caixa/dashboard_comercial/', {
            params: filtros
        });
        return data;
    }

    // Análise Rentabilidade
    async getAnaliseRentabilidade(filtros: DateRange) {
    const { data } = await this.api.get('fluxo-caixa/analise_rentabilidade/', {
            params: filtros
        });
        return data;
    }

    // Operações de Lançamentos
    async realizarLancamento(id: number) {
    const { data } = await this.api.post(`fluxo-caixa/${id}/realizar/`);
        return data;
    }

    async estornarLancamento(id: number, motivo: string) {
    const { data } = await this.api.post(`fluxo-caixa/${id}/estornar/`, { motivo });
        return data;
    }

    async conciliarLancamento(id: number) {
    const { data } = await this.api.post(`fluxo-caixa/${id}/conciliar/`);
        return data;
    }

    // Operações em Lote
    async processarLote(operacao: 'realizar' | 'estornar', ids: number[]) {
    const { data } = await this.api.post('fluxo-caixa/processar_lote/', {
            operacao,
            ids
        });
        return data;
    }

    async atualizarLote(atualizacoes: Array<{
        id: number;
        categoria?: string;
        descricao?: string;
        observacoes?: string;
    }>) {
    const { data } = await this.api.post('fluxo-caixa/atualizar_lote/', {
            atualizacoes
        });
        return data;
    }

    // Importação
    async importarPlanilha(file: File) {
        const formData = new FormData();
        formData.append('file', file);

    const { data } = await this.api.post('fluxo-caixa/importar_planilha/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return data;
    }

    // Relatórios
    async getRelatorioFluxoCaixa(filtros: DateRange, formato: 'json' | 'csv' | 'excel' = 'json') {
    const { data } = await this.api.get('fluxo-caixa/relatorio_fluxo_caixa/', {
            params: {
                ...filtros,
                formato
            },
            responseType: formato === 'json' ? 'json' : 'blob'
        });
        return data;
    }

    async getRelatorioDRE(ano: number, mes: number, formato: 'json' | 'csv' | 'excel' = 'json') {
    const { data } = await this.api.get('fluxo-caixa/relatorio_dre/', {
            params: {
                ano,
                mes,
                formato
            },
            responseType: formato === 'json' ? 'json' : 'blob'
        });
        return data;
    }

    async getRelatorioInadimplencia(dataBase: Date, formato: 'json' | 'csv' | 'excel' = 'json') {
    const { data } = await this.api.get('fluxo-caixa/relatorio_inadimplencia/', {
            params: {
                data_base: dataBase.toISOString().split('T')[0],
                formato
            },
            responseType: formato === 'json' ? 'json' : 'blob'
        });
        return data;
    }

    // Utilitários
    exportarRelatorio(blob: Blob, filename: string) {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    }
    async getDashboard(
        type: 'pagar' | 'receber',
        filtros?: FilterParams2
    ): Promise<DashboardResponse2> {
        try {
            const params = new URLSearchParams();

            // Adicionar parâmetros de filtro
            if (filtros) {
                if (filtros.dataInicial) params.append('data_inicial', filtros.dataInicial);
                if (filtros.dataFinal) params.append('data_final', filtros.dataFinal);
                if (filtros.status && filtros.status !== 'all') params.append('status', filtros.status);
                if (filtros.searchTerm) params.append('search_term', filtros.searchTerm);
            }

            // Escolher endpoint baseado no tipo
            const endpoint = type === 'pagar'
                ? `contas_pagar/dashboard/?${params}`
                : `contas_receber/dashboard/?${params}`;

            const response = await this.api.get<DashboardResponse2>(endpoint);
            return response.data;
        } catch (error) {
            console.error(`Erro ao buscar dashboard de contas a ${type}:`, error);
            throw error;
        }
    }

    // Método para atualizar status do título
    async updateStatus(
        type: 'pagar' | 'receber',
        tituloId: number,
        paymentData: PaymentData
    ) {
        try {
            const endpoint = type === 'pagar'
                ? `contas_pagar/${tituloId}/atualizar_status/`
                : `contas_receber/${tituloId}/atualizar_status/`;

            const response = await this.api.patch(endpoint, paymentData);
            return response.data;
        } catch (error) {
            console.error(`Erro ao atualizar status de título a ${type}:`, error);
            throw error;
        }
    }

    // Método para baixa em lote (opcional, baseado no código comentado)
    async batchPayment(
        type: 'pagar' | 'receber',
        paymentData: PaymentData & { titulos: number[] }
    ) {
        try {
            const endpoint = type === 'pagar'
                ? `contas_pagar/baixa-em-lote/`
                : `contas_receber/baixa-em-lote/`;

            const response = await this.api.post(endpoint, paymentData);
            return response.data;
        } catch (error) {
            console.error(`Erro ao realizar baixa em lote de contas a ${type}:`, error);
            throw error;
        }
    }
}

export const financialService = new FinancialService();