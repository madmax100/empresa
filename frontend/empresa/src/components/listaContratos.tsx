import React, { useEffect, useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { contasReceberService, contratosService, notasFiscaisService } from '@/services/api';
import {
    ContratoExpandido,
    ContasReceberResponse,
    DashboardContrato,
    DashboardFiltros,
} from '@/types/models';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { format, differenceInDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { ItemNotaFiscal, NotaFiscalSaida } from '@/types/notas_fiscais/models';

const ListaContratos: React.FC = () => {
    const [contratos, setContratos] = useState<ContratoExpandido[]>([]);
    const [loading, setLoading] = useState(true);
    const [totais, setTotais] = useState({ parcelas: 0, contratos: 0 });
    const [filtros, setFiltros] = useState<DashboardFiltros>({
        data_inicial: format(new Date().setDate(1), 'yyyy-MM-dd'),
        data_final: format(new Date(), 'yyyy-MM-dd')
    });
    const [notasExpandidas, setNotasExpandidas] = useState<{ [key: number]: boolean }>({});


    const formatarMoeda = (valor: string | number | undefined): string => {
        if (!valor) return 'R$ 0,00';
        const numero = Number(valor);
        if (isNaN(numero)) return 'R$ 0,00';
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(numero);
    };

    const formatarData = (dataString: string | undefined) => {
        if (!dataString) return '-';
        try {
            return format(new Date(dataString), 'dd/MM/yyyy', { locale: ptBR });
        } catch {
            return '-';
        }
    };

    const calcularDiasAtraso = (dataVencimento: string | undefined): number => {
        if (!dataVencimento) return 0;

        const hoje = new Date();
        const vencimento = new Date(dataVencimento);
        const diffDays = differenceInDays(hoje, vencimento);

        return diffDays > 0 ? diffDays : 0;
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'A':
                return 'text-yellow-600 bg-yellow-50';
            case 'P':
                return 'text-green-600 bg-green-50';
            case 'C':
                return 'text-red-600 bg-red-50';
            default:
                return 'text-gray-600 bg-gray-50';
        }
    };

    const isValidDashboard = (dashboard: any): dashboard is DashboardContrato => {
        return dashboard &&
            dashboard.notas_fiscais &&
            Array.isArray(dashboard.notas_fiscais.notas);
    };

    const carregarDadosContrato = async (contrato: ContratoExpandido) => {
        try {
            if (!contrato.cliente?.id || !contrato.contrato) {
                console.error('ID do cliente ou número do contrato não encontrado');
                return;
            }

            setContratos(prev => prev.map(c => {
                if (c.id === contrato.id) {
                    return { ...c, loading: true };
                }
                return c;
            }));

            const [contasReceberData, dashboardData] = await Promise.all([
                contasReceberService.buscarPorCliente(contrato.cliente.id, filtros),
                contratosService.buscarDashboard(contrato.contrato, filtros)
            ]);

            // Garantir que os dados de contas a receber tenham a estrutura correta
            const formattedContasReceber: ContasReceberResponse = {
                resumo: {
                    total_atrasado: contasReceberData?.resumo?.total_atrasado || 0,
                    total_pago_periodo: contasReceberData?.resumo?.total_pago_periodo || 0,
                    total_cancelado_periodo: contasReceberData?.resumo?.total_cancelado_periodo || 0,
                    total_aberto_periodo: contasReceberData?.resumo?.total_aberto_periodo || 0,
                    quantidade_titulos: contasReceberData?.resumo?.quantidade_titulos || 0,
                    quantidade_atrasados_periodo: contasReceberData?.resumo?.quantidade_atrasados_periodo || 0
                },
                titulos_atrasados: contasReceberData?.titulos_atrasados || [],
                titulos_pagos_periodo: contasReceberData?.titulos_pagos_periodo || [],
                titulos_abertos_periodo: contasReceberData?.titulos_abertos_periodo || []
            };

            // Garantir que os dados do dashboard tenham a estrutura correta
            const formattedDashboard: DashboardContrato = {
                contrato: contrato.contrato,
                itens: dashboardData?.itens || [],
                notas_fiscais: {
                    resumo: {
                        total_valor: dashboardData?.notas_fiscais?.resumo?.total_valor || 0,
                        total_recebido: dashboardData?.notas_fiscais?.resumo?.total_recebido || 0,
                        quantidade_notas: dashboardData?.notas_fiscais?.resumo?.quantidade_notas || 0
                    },
                    notas: dashboardData?.notas_fiscais?.notas || []
                },
                periodo: dashboardData?.periodo || {
                    inicio: filtros.data_inicial,
                    fim: filtros.data_final
                }
            };

            setContratos(prev => prev.map(c => {
                if (c.id === contrato.id) {
                    return {
                        ...c,
                        contasReceber: formattedContasReceber,
                        dashboard: formattedDashboard,
                        loading: false
                    };
                }
                return c;
            }));
        } catch (error) {
            console.error('Erro ao carregar dados do contrato:', error);
            setContratos(prev => prev.map(c => {
                if (c.id === contrato.id) {
                    return {
                        ...c,
                        error: 'Erro ao carregar dados do contrato',
                        loading: false
                    };
                }
                return c;
            }));
        }
    };

    const toggleNotaExpansao = (notaId: number) => {
        setNotasExpandidas(prev => ({
            ...prev,
            [notaId]: !prev[notaId]
        }));
    };

    const toggleExpansao = async (contrato: ContratoExpandido) => {
        const novaLista = contratos.map(c => {
            if (c.id === contrato.id) {
                const novoEstado = !c.expandido;
                if (novoEstado && (!c.contasReceber || !c.dashboard)) {
                    carregarDadosContrato(c);
                    console.log('Dados do contrato carregados:', c);
                }
                return { ...c, expandido: novoEstado };
            }
            return c;
        });
        setContratos(novaLista);
    };

    const handleFiltroChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFiltros(prev => ({
            ...prev,
            [name === 'dataInicial' ? 'data_inicial' : 'data_final']: value
        }));
    };

    const aplicarFiltros = async () => {
        setLoading(true);
        await carregarContratos();
        // Recarregar dados dos contratos expandidos
        contratos.forEach(contrato => {
            if (contrato.expandido) {
                carregarDadosContrato(contrato);
            }
        });
    };

    const carregarContratos = async () => {
        try {
            const response = await contratosService.listar();
            const dataAtual = new Date();
            const contratosAtivos = response
                .filter(contrato => {
                    if (!contrato.fim) return false;
                    const dataFim = new Date(contrato.fim);
                    return dataFim > dataAtual;
                })
                .sort((a, b) => {
                    const dataA = a.fim ? new Date(a.fim).getTime() : 0;
                    const dataB = b.fim ? new Date(b.fim).getTime() : 0;
                    return dataA - dataB;
                })
                .map(contrato => ({
                    ...contrato,
                    expandido: false,
                    loading: false
                }));

            const totalContratos = contratosAtivos.reduce((acc, contrato) =>
                acc + Number(contrato.valorcontrato || 0), 0);

            const totalParcelas = contratosAtivos.reduce((acc, contrato) =>
                acc + Number(contrato.valorpacela || 0), 0);

            setTotais({ parcelas: totalParcelas, contratos: totalContratos });
            setContratos(contratosAtivos);
        } catch (error) {
            console.error('Erro ao carregar contratos:', error);
            setContratos([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        carregarContratos();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-4 space-y-6">
            {/* Filtros de Data */}
            <Card>
                <CardHeader>
                    <CardTitle>Filtros</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex gap-4">
                        <div className="flex flex-col">
                            <label htmlFor="dataInicial" className="text-sm font-medium">
                                Data Inicial
                            </label>
                            <input
                                type="date"
                                id="dataInicial"
                                name="dataInicial"
                                value={filtros.data_inicial}
                                onChange={handleFiltroChange}
                                className="border rounded p-2"
                            />
                        </div>
                        <div className="flex flex-col">
                            <label htmlFor="dataFinal" className="text-sm font-medium">
                                Data Final
                            </label>
                            <input
                                type="date"
                                id="dataFinal"
                                name="dataFinal"
                                value={filtros.data_final}
                                onChange={handleFiltroChange}
                                className="border rounded p-2"
                            />
                        </div>
                        <button
                            onClick={aplicarFiltros}
                            className="px-4 py-2 bg-primary text-white rounded self-end"
                        >
                            Aplicar Filtros
                        </button>
                    </div>
                </CardContent>
            </Card>

            {/* Cards de Totais */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Total Mensal (Parcelas)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-blue-600">
                            {formatarMoeda(totais.parcelas)}
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Total Contratos</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-600">
                            {formatarMoeda(totais.contratos)}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Tabela Principal */}
            <Card>
                <CardHeader>
                    <CardTitle>Contratos de Locação Ativos</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-10"></TableHead>
                                <TableHead>Contrato</TableHead>
                                <TableHead>Cliente</TableHead>
                                <TableHead>Máquinas</TableHead>
                                <TableHead>Tipo</TableHead>
                                <TableHead className="text-right">Valor Parcela</TableHead>
                                <TableHead className="text-right">Valor Total</TableHead>
                                <TableHead className="text-center">Data</TableHead>
                                <TableHead className="text-center">Início</TableHead>
                                <TableHead className="text-center">Fim</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {contratos.map((contrato) => (
                                <React.Fragment key={contrato.id}>
                                    <TableRow
                                        className={`cursor-pointer ${contrato.expandido ? 'bg-muted/50' : ''}`}
                                        onClick={() => toggleExpansao(contrato)}
                                    >
                                        <TableCell>
                                            {contrato.expandido ?
                                                <ChevronDown className="h-4 w-4" /> :
                                                <ChevronRight className="h-4 w-4" />
                                            }
                                        </TableCell>
                                        <TableCell>{contrato.contrato}</TableCell>
                                        <TableCell>{contrato.cliente?.nome || '-'}</TableCell>
                                        <TableCell>{contrato.totalMaquinas || '-'}</TableCell>
                                        <TableCell>{contrato.tipocontrato || '-'}</TableCell>
                                        <TableCell className="text-right">
                                            {formatarMoeda(contrato.valorpacela)}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            {formatarMoeda(contrato.valorcontrato)}
                                        </TableCell>
                                        <TableCell className="text-center">
                                            {formatarData(contrato.data)}
                                        </TableCell>
                                        <TableCell className="text-center">
                                            {formatarData(contrato.inicio)}
                                        </TableCell>
                                        <TableCell className="text-center">
                                            {formatarData(contrato.fim)}
                                        </TableCell>
                                    </TableRow>

                                    {contrato.expandido && (
                                        <TableRow>
                                            <TableCell colSpan={10}>
                                                <Card className="mt-2">
                                                    <CardContent className="p-4">
                                                        {contrato.loading ? (
                                                            <div className="flex items-center justify-center py-8">
                                                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                                                                <span className="ml-2 text-muted-foreground">
                                                                    Carregando informações...
                                                                </span>
                                                            </div>
                                                        ) : (
                                                            <div className="space-y-6">
                                                                {/* Dashboard do Contrato */}
                                                                {contrato.dashboard && isValidDashboard(contrato.dashboard) && (
                                                                    <div className="grid grid-cols-3 gap-4">
                                                                        <Card>
                                                                            <CardHeader>
                                                                                <CardTitle className="text-blue-700">
                                                                                    Total Notas Fiscais
                                                                                </CardTitle>
                                                                            </CardHeader>
                                                                            <CardContent>
                                                                                <div className="text-2xl font-bold text-blue-600">
                                                                                    {formatarMoeda(contrato.dashboard.notas_fiscais.resumo.total_valor)}
                                                                                </div>
                                                                                <p className="text-sm text-muted-foreground">
                                                                                    {contrato.dashboard.notas_fiscais.resumo.quantidade_notas} notas
                                                                                </p>
                                                                            </CardContent>
                                                                        </Card>
                                                                        <Card>
                                                                            <CardHeader>
                                                                                <CardTitle className="text-green-700">
                                                                                    Total Recebido
                                                                                </CardTitle>
                                                                            </CardHeader>
                                                                            <CardContent>
                                                                                <div className="text-2xl font-bold text-green-600">
                                                                                    {formatarMoeda(contrato.contasReceber.resumo.total_pago_periodo)}
                                                                                </div>
                                                                            </CardContent>
                                                                        </Card>
                                                                        <Card>
                                                                            <CardHeader>
                                                                                <CardTitle className="text-red-700">
                                                                                    Total a Receber
                                                                                </CardTitle>
                                                                            </CardHeader>
                                                                            <CardContent>
                                                                                <div className="text-2xl font-bold text-red-600">
                                                                                    {formatarMoeda(
                                                                                        contrato.dashboard.notas_fiscais.resumo.total_valor -
                                                                                        contrato.dashboard.notas_fiscais.resumo.total_recebido
                                                                                    )}
                                                                                </div>
                                                                            </CardContent>
                                                                        </Card>
                                                                    </div>
                                                                )}

                                                                {/* Notas Fiscais */}
                                                                {contrato.dashboard && isValidDashboard(contrato.dashboard) &&
                                                                    contrato.dashboard.notas_fiscais.notas.length > 0 && (
                                                                        <div className="space-y-2">
                                                                            <h4 className="font-semibold">Notas Fiscais</h4>
                                                                            <Table>
                                                                                <TableHeader>
                                                                                    <TableRow>
                                                                                        <TableHead className="w-10"></TableHead>
                                                                                        <TableHead>Número</TableHead>
                                                                                        <TableHead>Data</TableHead>
                                                                                        <TableHead className="text-right">Valor Produtos</TableHead>
                                                                                        <TableHead className="text-right">Valor Total</TableHead>
                                                                                        <TableHead>Operação</TableHead>
                                                                                        <TableHead>CFOP</TableHead>
                                                                                        <TableHead>Finalidade</TableHead>
                                                                                    </TableRow>
                                                                                </TableHeader>
                                                                                <TableBody>
                                                                                    {contrato.dashboard.notas_fiscais.notas.map((nota: NotaFiscalSaida) => (
                                                                                        <React.Fragment key={nota.id}>
                                                                                            <TableRow
                                                                                                className={`cursor-pointer hover:bg-muted/50 ${notasExpandidas[nota.id] ? 'bg-muted/50' : ''}`}
                                                                                                onClick={() => toggleNotaExpansao(nota.id)}
                                                                                            >
                                                                                                <TableCell>
                                                                                                    {notasExpandidas[nota.id] ?
                                                                                                        <ChevronDown className="h-4 w-4" /> :
                                                                                                        <ChevronRight className="h-4 w-4" />
                                                                                                    }
                                                                                                </TableCell>
                                                                                                <TableCell>{nota.numero_nota}</TableCell>
                                                                                                <TableCell>{formatarData(nota.data)}</TableCell>
                                                                                                <TableCell className="text-right">
                                                                                                    {formatarMoeda(nota.valor_produtos)}
                                                                                                </TableCell>
                                                                                                <TableCell className="text-right">
                                                                                                    {formatarMoeda(nota.valor_total_nota)}
                                                                                                </TableCell>
                                                                                                <TableCell>{nota.operacao}</TableCell>
                                                                                                <TableCell>{nota.cfop}</TableCell>
                                                                                                <TableCell>{nota.finalidade}</TableCell>
                                                                                            </TableRow>

                                                                                            {notasExpandidas[nota.id] && (
                                                                                                <TableRow>
                                                                                                    <TableCell colSpan={8}>
                                                                                                        <div className="p-4 space-y-4">
                                                                                                            {/* Informações adicionais da nota */}
                                                                                                            <div className="grid grid-cols-3 gap-4 bg-muted/20 p-4 rounded">
                                                                                                                <div>
                                                                                                                    <p className="text-sm font-medium">Forma de Pagamento</p>
                                                                                                                    <p className="text-sm">{nota.forma_pagamento || '-'}</p>
                                                                                                                </div>
                                                                                                                <div>
                                                                                                                    <p className="text-sm font-medium">Condições</p>
                                                                                                                    <p className="text-sm">{nota.condicoes || '-'}</p>
                                                                                                                </div>
                                                                                                                <div>
                                                                                                                    <p className="text-sm font-medium">Operador</p>
                                                                                                                    <p className="text-sm">{nota.operador || '-'}</p>
                                                                                                                </div>
                                                                                                            </div>

                                                                                                            {/* Tabela de itens */}
                                                                                                            <div>
                                                                                                                <h5 className="font-semibold mb-2">Itens da Nota</h5>
                                                                                                                <Table>
                                                                                                                    <TableHeader>
                                                                                                                        <TableRow>
                                                                                                                            <TableHead>Produto</TableHead>
                                                                                                                            <TableHead className="text-right">Quantidade</TableHead>
                                                                                                                            <TableHead className="text-right">Valor Unit.</TableHead>
                                                                                                                            <TableHead className="text-right">Valor Total</TableHead>
                                                                                                                            <TableHead>Unidade</TableHead>
                                                                                                                            <TableHead>Descrição</TableHead>
                                                                                                                        </TableRow>
                                                                                                                    </TableHeader>
                                                                                                                    <TableBody>
                                                                                                                        {nota.itens?.map((item: ItemNotaFiscal) => (
                                                                                                                            <TableRow key={item.id}>
                                                                                                                                <TableCell className="font-medium">
                                                                                                                                    {item.produto.nome}
                                                                                                                                </TableCell>
                                                                                                                                <TableCell className="text-right">
                                                                                                                                    {item.quantidade}
                                                                                                                                </TableCell>
                                                                                                                                <TableCell className="text-right">
                                                                                                                                    {formatarMoeda(item.valor_unitario)}
                                                                                                                                </TableCell>
                                                                                                                                <TableCell className="text-right">
                                                                                                                                    {formatarMoeda(item.valor_total)}
                                                                                                                                </TableCell>
                                                                                                                                <TableCell>{item.produto.unidade_medida}</TableCell>
                                                                                                                                <TableCell>{item.descricao || '-'}</TableCell>
                                                                                                                            </TableRow>
                                                                                                                        ))}
                                                                                                                    </TableBody>
                                                                                                                    {/* Rodapé com totais */}
                                                                                                                    <tfoot>
                                                                                                                        <tr className="border-t">
                                                                                                                            <td colSpan={3} className="py-2 pr-4 text-right font-medium">
                                                                                                                                Total Produtos:
                                                                                                                            </td>
                                                                                                                            <td className="py-2 text-right font-medium">
                                                                                                                                {formatarMoeda(nota.valor_produtos)}
                                                                                                                            </td>
                                                                                                                            <td colSpan={2}></td>
                                                                                                                        </tr>
                                                                                                                        {nota.valor_frete > 0 && (
                                                                                                                            <tr>
                                                                                                                                <td colSpan={3} className="py-2 pr-4 text-right">
                                                                                                                                    Frete:
                                                                                                                                </td>
                                                                                                                                <td className="py-2 text-right">
                                                                                                                                    {formatarMoeda(nota.valor_frete)}
                                                                                                                                </td>
                                                                                                                                <td colSpan={2}></td>
                                                                                                                            </tr>
                                                                                                                        )}
                                                                                                                        <tr className="border-t">
                                                                                                                            <td colSpan={3} className="py-2 pr-4 text-right font-bold">
                                                                                                                                Total Nota:
                                                                                                                            </td>
                                                                                                                            <td className="py-2 text-right font-bold">
                                                                                                                                {formatarMoeda(nota.valor_total_nota)}
                                                                                                                            </td>
                                                                                                                            <td colSpan={2}></td>
                                                                                                                        </tr>
                                                                                                                    </tfoot>
                                                                                                                </Table>
                                                                                                            </div>

                                                                                                            {/* Observações */}
                                                                                                            {nota.obs && (
                                                                                                                <div className="mt-4">
                                                                                                                    <p className="text-sm font-medium">Observações</p>
                                                                                                                    <p className="text-sm mt-1">{nota.obs}</p>
                                                                                                                </div>
                                                                                                            )}
                                                                                                        </div>
                                                                                                    </TableCell>
                                                                                                </TableRow>
                                                                                            )}
                                                                                        </React.Fragment>
                                                                                    ))}
                                                                                </TableBody>
                                                                            </Table>
                                                                        </div>
                                                                    )}

                                                                {/* Títulos em Aberto */}
                                                                {contrato.contasReceber?.titulos_abertos_periodo &&
                                                                    contrato.contasReceber.titulos_abertos_periodo.length > 0 && (
                                                                        <div className="space-y-2">
                                                                            <h4 className="font-semibold">Títulos em Aberto</h4>
                                                                            <Table>
                                                                                <TableHeader>
                                                                                    <TableRow>
                                                                                        <TableHead>Descrição</TableHead>
                                                                                        <TableHead className="text-right">Valor</TableHead>
                                                                                        <TableHead className="text-center">Vencimento</TableHead>
                                                                                        <TableHead className="text-center">Status</TableHead>
                                                                                    </TableRow>
                                                                                </TableHeader>
                                                                                <TableBody>
                                                                                    {contrato.contasReceber.titulos_abertos_periodo.map((titulo) => (
                                                                                        <TableRow key={titulo.id}>
                                                                                            <TableCell>{titulo.historico}</TableCell>
                                                                                            <TableCell className="text-right">
                                                                                                {formatarMoeda(titulo.valor)}
                                                                                            </TableCell>
                                                                                            <TableCell className="text-center">
                                                                                                {formatarData(titulo.vencimento)}
                                                                                            </TableCell>
                                                                                            <TableCell className="text-center">
                                                                                                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(titulo.status)}`}>
                                                                                                    {titulo.status}
                                                                                                </span>
                                                                                            </TableCell>
                                                                                        </TableRow>
                                                                                    ))}
                                                                                </TableBody>
                                                                            </Table>
                                                                        </div>
                                                                    )}

                                                                {/* Títulos Atrasados */}
                                                                {contrato.contasReceber?.titulos_atrasados &&
                                                                    contrato.contasReceber.titulos_atrasados.length > 0 && (
                                                                        <div className="space-y-2 mt-4">
                                                                            <h4 className="font-semibold text-red-600">Títulos Atrasados</h4>
                                                                            <Table>
                                                                                <TableHeader>
                                                                                    <TableRow>
                                                                                        <TableHead>Descrição</TableHead>
                                                                                        <TableHead className="text-right">Valor</TableHead>
                                                                                        <TableHead className="text-center">Vencimento</TableHead>
                                                                                        <TableHead className="text-center">Dias Atraso</TableHead>
                                                                                        <TableHead className="text-center">Status</TableHead>
                                                                                    </TableRow>
                                                                                </TableHeader>
                                                                                <TableBody>
                                                                                    {contrato.contasReceber.titulos_atrasados.map((titulo) => (
                                                                                        <TableRow key={titulo.id}>
                                                                                            <TableCell>{titulo.historico}</TableCell>
                                                                                            <TableCell className="text-right">
                                                                                                {formatarMoeda(titulo.valor)}
                                                                                            </TableCell>
                                                                                            <TableCell className="text-center">
                                                                                                {formatarData(titulo.vencimento)}
                                                                                            </TableCell>
                                                                                            <TableCell className="text-center">
                                                                                                {calcularDiasAtraso(titulo.vencimento)}
                                                                                            </TableCell>
                                                                                            <TableCell className="text-center">
                                                                                                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(titulo.status)}`}>
                                                                                                    {titulo.status}
                                                                                                </span>
                                                                                            </TableCell>
                                                                                        </TableRow>
                                                                                    ))}
                                                                                </TableBody>
                                                                            </Table>
                                                                        </div>
                                                                    )}

                                                                {/* Itens do Contrato */}
                                                                {contrato.dashboard?.itens &&
                                                                    contrato.dashboard.itens.length > 0 && (
                                                                        <div className="space-y-2">
                                                                            <h4 className="font-semibold">Itens do Contrato</h4>
                                                                            <Table>
                                                                                <TableHeader>
                                                                                    <TableRow>
                                                                                        <TableHead>Modelo</TableHead>
                                                                                        <TableHead>Nº Série</TableHead>
                                                                                    </TableRow>
                                                                                </TableHeader>
                                                                                <TableBody>
                                                                                    {contrato.dashboard.itens.map((item) => (
                                                                                        <TableRow key={item.id}>
                                                                                            <TableCell>{item.modelo || '-'}</TableCell>
                                                                                            <TableCell>{item.numeroserie || '-'}</TableCell>
                                                                                        </TableRow>
                                                                                    ))}
                                                                                </TableBody>
                                                                            </Table>
                                                                        </div>
                                                                    )}
                                                            </div>
                                                        )}
                                                    </CardContent>
                                                </Card>
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </React.Fragment>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Mensagem quando não houver contratos */}
            {contratos.length === 0 && (
                <Card>
                    <CardContent className="flex flex-col items-center justify-center p-6">
                        <p className="text-muted-foreground text-center">
                            Nenhum contrato ativo encontrado
                        </p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default ListaContratos;
