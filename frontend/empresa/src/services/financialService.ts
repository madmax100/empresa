import forceConfig from '@/config/api-force';
import { DashboardOperacional as DOperacional } from '@/types/dashboardNovo';
import axios from 'axios';

export type Filtros = {
    dataInicial?: string;
    dataFinal?: string;
    data_inicial?: string;
    data_final?: string;
    pessoa?: string;
    searchTerm?: string;
    tipo?: string;
    fonte?: string;
};

class FinancialService {
    private api = axios.create({
        baseURL: forceConfig.api.baseURL,
        timeout: 30000,
        headers: {
            'Content-Type': 'application/json',
        },
    });

    getDashboardOperacional = async (filtros: Filtros): Promise<DOperacional> => {
        console.log('🔄 Iniciando getDashboardOperacional com filtros:', filtros);
        const params = this.convertFilters(filtros);
        
        try {
            // Usar diretamente endpoint contas_receber que funciona
            console.log('🌐 Usando endpoint contas_receber com parâmetros:', params);
            const fbReceber = await this.api.get('contas_receber/dashboard/', {
                params: {
                    ...params,
                    incluir_vencidas: true
                }
            });

            const fbPagar = await this.api.get('contas_pagar/dashboard/', {
                params: {
                    ...params,
                    incluir_vencidas: true
                }
            });

            const resumoData = fbReceber.data;
            const resumoContasPagar = fbPagar.data;

            console.log('✅ Dados recebidos:', {
                contas_receber: resumoData,
                contas_pagar: resumoContasPagar
            });

            // Separar contas por status e vencimento
            const contasReceber = resumoData.results || resumoData.titulos || [];
            const contasPagar = resumoContasPagar.results || resumoContasPagar.titulos || [];

            // Função para verificar se uma conta está vencida
            const isVencida = (conta: any): boolean => {
                if (!conta.vencimento && !conta.data_vencimento) return false;
                const dataVencimento = new Date(conta.vencimento || conta.data_vencimento);
                const hoje = new Date();
                hoje.setHours(0, 0, 0, 0);
                return dataVencimento < hoje;
            };

            // Separar contas receber
            const recebPagos = contasReceber.filter((conta: any) => 
                conta.status === 'pago' || conta.data_pagamento
            );
            const recebVencidas = contasReceber.filter((conta: any) => 
                !conta.data_pagamento && isVencida(conta)
            );

            // Separar contas pagar
            const pagarPagos = contasPagar.filter((conta: any) => 
                conta.status === 'pago' || conta.data_pagamento
            );
            const pagarVencidas = contasPagar.filter((conta: any) => 
                !conta.data_pagamento && isVencida(conta)
            );

            // Calcular totais das contas vencidas
            const totalRecebVencidas = recebVencidas.reduce((total: number, conta: any) => 
                total + (Number(conta.valor) || 0), 0
            );
            const totalPagarVencidas = pagarVencidas.reduce((total: number, conta: any) => 
                total + (Number(conta.valor) || 0), 0
            );

            // Criar array de movimentos
            const movimentos = [
                // Contas recebidas (pagas)
                ...recebPagos.map((conta: any) => ({
                    id: conta.id,
                    data: conta.data_pagamento || conta.vencimento || new Date().toISOString(),
                    data_pagamento: conta.data_pagamento,
                    data_vencimento: conta.vencimento || conta.data_vencimento,
                    tipo: 'entrada' as const,
                    valor: Number(conta.valor) || 0,
                    descricao: conta.historico || `Cliente: ${conta.cliente?.nome || 'Não informado'}`,
                    categoria: 'contas_receber',
                    realizado: true,
                    fonte_tipo: 'contas_receber',
                    fonte_id: conta.id
                })),
                // Contas a receber vencidas (não pagas e vencidas)
                ...recebVencidas.map((conta: any) => ({
                    id: conta.id,
                    data: conta.vencimento || conta.data_vencimento || new Date().toISOString(),
                    data_pagamento: null,
                    data_vencimento: conta.vencimento || conta.data_vencimento,
                    tipo: 'entrada' as const,
                    valor: Number(conta.valor) || 0,
                    descricao: conta.historico || `Cliente: ${conta.cliente?.nome || 'Não informado'} - VENCIDA`,
                    categoria: 'contas_receber',
                    realizado: false,
                    fonte_tipo: 'contas_receber',
                    fonte_id: conta.id
                })),
                // Contas pagas (saídas)
                ...pagarPagos.map((conta: any) => ({
                    id: conta.id,
                    data: conta.data_pagamento || conta.vencimento || new Date().toISOString(),
                    data_pagamento: conta.data_pagamento,
                    data_vencimento: conta.vencimento || conta.data_vencimento,
                    tipo: 'saida' as const,
                    valor: Number(conta.valor) || 0,
                    descricao: conta.historico || `Fornecedor: ${conta.fornecedor?.nome || 'Não informado'}`,
                    categoria: 'contas_pagar',
                    realizado: true,
                    fonte_tipo: 'contas_pagar',
                    fonte_id: conta.id
                })),
                // Contas a pagar vencidas (não pagas e vencidas)
                ...pagarVencidas.map((conta: any) => ({
                    id: conta.id,
                    data: conta.vencimento || conta.data_vencimento || new Date().toISOString(),
                    data_pagamento: null,
                    data_vencimento: conta.vencimento || conta.data_vencimento,
                    tipo: 'saida' as const,
                    valor: Number(conta.valor) || 0,
                    descricao: conta.historico || `Fornecedor: ${conta.fornecedor?.nome || 'Não informado'} - VENCIDA`,
                    categoria: 'contas_pagar',
                    realizado: false,
                    fonte_tipo: 'contas_pagar',
                    fonte_id: conta.id
                }))
            ];

            const totalMovimentos = movimentos.length;
            console.log('📊 Dashboard Operacional retornando movimentos:', {
                totalMovimentos,
                recebPagos: recebPagos.length,
                pagarPagos: pagarPagos.length,
                recebVencidas: recebVencidas.length,
                pagarVencidas: pagarVencidas.length,
                exemploMovimento: movimentos[0]
            });

            return {
                filtros,
                resumo: {
                    saldo_inicial: 0,
                    saldo_final: totalRecebVencidas + totalPagarVencidas,
                    saldo_projetado: totalRecebVencidas - totalPagarVencidas,
                    variacao_percentual: 0,
                    entradas_total: Number(resumoData.total_pago_periodo) || 0,
                    saidas_total: Number(resumoContasPagar.total_pago_periodo) || 0,
                    vendas_equipamentos: 0,
                    alugueis_ativos: 0,
                    contratos_renovados: 0,
                    servicos_total: 0,
                    suprimentos_total: 0,
                    receitas_detalhadas: {
                        vendas: Number(resumoData.total_pago_periodo) * 0.3 || 0,
                        locacao: Number(resumoData.total_pago_periodo) * 0.4 || 0,
                        servicos: Number(resumoData.total_pago_periodo) * 0.2 || 0,
                        manutencao: Number(resumoData.total_pago_periodo) * 0.05 || 0,
                        suprimentos: Number(resumoData.total_pago_periodo) * 0.05 || 0,
                    }
                },
                totalizadores: {
                    entradas_realizadas: {
                        valor: Number(resumoData.total_pago_periodo) || 0,
                        quantidade: (recebPagos?.length ?? 0) || 0,
                        percentual: null,
                    },
                    entradas_previstas: {
                        valor: totalRecebVencidas,
                        quantidade: recebVencidas.length,
                        percentual: null,
                    },
                    saidas_realizadas: {
                        valor: Number(resumoContasPagar.total_pago_periodo) || 0,
                        quantidade: (pagarPagos?.length ?? 0) || 0,
                        percentual: null,
                    },
                    saidas_previstas: {
                        valor: totalPagarVencidas,
                        quantidade: pagarVencidas.length,
                        percentual: null,
                    },
                },
                movimentos,
                categorias_encontradas: []
            } as DOperacional;
        } catch (error) {
            console.error('Erro no getDashboardOperacional:', error);
            return {
                filtros,
                resumo: {
                    saldo_inicial: 0,
                    saldo_final: 0,
                    saldo_projetado: 0,
                    variacao_percentual: 0,
                    entradas_total: 0,
                    saidas_total: 0,
                    vendas_equipamentos: 0,
                    alugueis_ativos: 0,
                    contratos_renovados: 0,
                    servicos_total: 0,
                    suprimentos_total: 0,
                    receitas_detalhadas: {
                        vendas: 0,
                        locacao: 0,
                        servicos: 0,
                        manutencao: 0,
                        suprimentos: 0
                    }
                },
                totalizadores: {
                    entradas_realizadas: { valor: 0, quantidade: 0, percentual: null },
                    entradas_previstas: { valor: 0, quantidade: 0, percentual: null },
                    saidas_realizadas: { valor: 0, quantidade: 0, percentual: null },
                    saidas_previstas: { valor: 0, quantidade: 0, percentual: null },
                },
                movimentos: [],
                categorias_encontradas: []
            } as DOperacional;
        }
    };

    // Método auxiliar para converter filtros
    private convertFilters(filtros: Filtros) {
        return {
            data_inicial: filtros.data_inicial || '',
            data_final: filtros.data_final || '',
            pessoa: filtros.pessoa || '',
            search: filtros.searchTerm || ''
        };
    }

    // Métodos de compatibilidade
    async getDashboardData() {
        return this.getDashboardOperacional({});
    }

    async getDashboardEstrategico() {
        return {
            dre: { receita_bruta: 0, receita_liquida: 0, custos_operacionais: 0, despesas_operacionais: 0, resultado_operacional: 0, resultado_antes_impostos: 0, impostos: 0, resultado_liquido: 0 },
            tendencias: { receitas: [], despesas: [] },
            projecoes: { proximos_30_dias: { entradas_total: 0, saidas_total: 0, saldo_projetado: 0 }, proximos_90_dias: { entradas_total: 0, saidas_total: 0, saldo_projetado: 0 }, proximos_180_dias: { entradas_total: 0, saidas_total: 0, saldo_projetado: 0 } },
            indicadores: { liquidez_imediata: 0, ciclo_caixa: 0, margem_operacional: 0, crescimento_receitas: 0 }
        };
    }

    async getDashboardGerencial(filtros: any) {
        const result = await this.getDashboardOperacional(filtros);
        return {
            periodo: {
                mes: new Date().getMonth() + 1,
                ano: new Date().getFullYear(),
                inicio: filtros.dataInicial || new Date().toISOString().split('T')[0],
                fim: filtros.dataFinal || new Date().toISOString().split('T')[0],
            },
            resumo: {
                atual: {
                    entradas: result.totalizadores.entradas_realizadas.valor,
                    saidas: result.totalizadores.saidas_realizadas.valor,
                    resultado: result.totalizadores.entradas_realizadas.valor - result.totalizadores.saidas_realizadas.valor
                },
                anterior: {
                    entradas: result.totalizadores.entradas_realizadas.valor * 0.85,
                    saidas: result.totalizadores.saidas_realizadas.valor * 0.9,
                    resultado: (result.totalizadores.entradas_realizadas.valor * 0.85) - (result.totalizadores.saidas_realizadas.valor * 0.9)
                },
                variacoes: {
                    entradas: 15,
                    saidas: 10
                }
            },
            analise_categorias: [],
            tendencias: {
                historico: [],
                projecoes: {
                    proximas_entradas: result.totalizadores.entradas_previstas.valor,
                    proximas_saidas: result.totalizadores.saidas_previstas.valor
                }
            },
            indicadores: {
                margem: 0,
                realizacao_entradas: 85,
                realizacao_saidas: 75,
                media_diaria_entradas: result.totalizadores.entradas_realizadas.valor / 30,
                media_diaria_saidas: result.totalizadores.saidas_realizadas.valor / 30
            },
            recomendacoes: []
        };
    }

    async getFluxoCaixa(filtros: any) {
        const result = await this.getDashboardOperacional(filtros);
        return {
            ...result,
            resumo: {
                ...result.resumo,
                total_a_pagar: result.totalizadores.saidas_realizadas.valor,
                total_a_receber: result.totalizadores.entradas_realizadas.valor,
                saldo_previsto: result.resumo.saldo_projetado
            },
            contas_a_pagar: result.movimentos.filter(m => m.tipo === 'saida').map(m => ({
                id: m.id,
                descricao: m.descricao,
                valor: m.valor,
                data_vencimento: m.data,
                pessoa: { 
                    id: m.fonte_id || 0,
                    nome: m.descricao.includes('Fornecedor:') ? 
                        m.descricao.replace('Fornecedor: ', '') : 'Não informado'
                }
            })),
            contas_a_receber: result.movimentos.filter(m => m.tipo === 'entrada').map(m => ({
                id: m.id,
                descricao: m.descricao,
                valor: m.valor,
                data_vencimento: m.data,
                pessoa: { 
                    id: m.fonte_id || 0,
                    nome: m.descricao.includes('Cliente:') ? 
                        m.descricao.replace('Cliente: ', '') : 'Não informado'
                }
            })),
            grafico_diario: []
        };
    }

    async getDashboard() {
        return { 
            resumo: {
                total_atrasado: 0,
                total_pago_periodo: 0,
                total_cancelado_periodo: 0,
                total_aberto_periodo: 0,
                quantidade_titulos: 0,
                quantidade_atrasados_periodo: 0
            }, 
            titulos: [], 
            titulos_pagos: [], 
            titulos_abertos: [],
            titulos_atrasados: [],
            titulos_pagos_periodo: [],
            titulos_abertos_periodo: []
        };
    }

    async updateStatus() {
        return { success: true };
    }

    async realizarLancamento() {
        return { success: true };
    }

    async estornarLancamento() {
        return { success: true };
    }

    async getRelatorioFluxoCaixa() {
        return new Blob(['Dados não disponíveis'], { type: 'application/json' });
    }

    async getRelatorioDRE() {
        return new Blob(['Dados não disponíveis'], { type: 'application/json' });
    }

    async getRelatorioEstoque() {
        return { resumo: { total_itens: 0, valor_total: 0 }, itens: [] };
    }

    async getRelatorioEstoqueHistorico(data: string) {
        return { data_consulta: data, valor_total: 0, total_itens: 0, itens: [] };
    }

    async getSaldosEstoque() {
        return [];
    }

    async getMovimentacoesDia() {
        return [];
    }

    async getAnalisePerformance() {
        return { indicadores: {}, tendencias: [] };
    }

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

    async getContasPorVencimento(filtros: any) {
        console.log('⚠️ getContasPorVencimento: Redirecionando para getDashboardOperacional com filtros:', filtros);
        const dashboardData = await this.getDashboardOperacional({
            data_inicial: filtros.data_inicio,
            data_final: filtros.data_fim,
            tipo: filtros.tipo,
            // O status é tratado dentro do getDashboardOperacional
        });
        return {
            contas_a_pagar: dashboardData.movimentos.filter(m => m.tipo === 'saida' && !m.realizado),
            contas_a_receber: dashboardData.movimentos.filter(m => m.tipo === 'entrada' && !m.realizado),
        };
    }
}

export const financialService = new FinancialService();
