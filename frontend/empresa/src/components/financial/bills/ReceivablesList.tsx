import React, { useEffect, useState, useCallback } from 'react';
import { financeiroDashboard } from '@/services/api';
import { DashboardData, FilterParams, STATUS_OPTIONS } from '@/types/models';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { format } from "date-fns";

const ContasPage: React.FC = () => {
    const [dashboard, setDashboard] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState<FilterParams>({
        dataInicial: '2024-01-01',
        dataFinal: new Date().toISOString().split('T')[0],
        status: 'all'
    });

    const handleFilterChange = (name: string, value: string) => {
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const aplicarFiltros = useCallback(async () => {
        try {
            setLoading(true);
            console.log('🏦 Carregando dados de contas a receber com filtros:', filters);
            const data = await financeiroDashboard.resumoGeral({
                ...filters,
                searchTerm: filters.searchTerm || ''
            });
            console.log('🏦 Dados recebidos:', data);
            console.log('🏦 Contas a receber:', {
                resumo: data.contasReceber.resumo,
                titulosAbertosPeriodo: data.contasReceber.titulos_abertos_periodo.length,
                titulosAtrasados: data.contasReceber.titulos_atrasados.length
            });
            setDashboard(data);
        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
        } finally {
            setLoading(false);
        }
    }, [filters]);

    useEffect(() => {
        aplicarFiltros();
    }, [aplicarFiltros]);

    const formatarMoeda = (valor: number | string) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(typeof valor === 'string' ? parseFloat(valor) : valor);
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


    const getStatusLabel = (statusCode: string) => {
        const option = STATUS_OPTIONS.find(opt => opt.value === statusCode);
        return option ? option.label : 'Desconhecido';
    };

    if (loading || !dashboard) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-4 space-y-6">
            {/* Filtros */}

            <Card>
                <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">
                                Data Inicial
                            </label>
                            <Input
                                type="date"
                                value={filters.dataInicial}
                                onChange={(e) => handleFilterChange('dataInicial', e.target.value)}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">
                                Data Final
                            </label>
                            <Input
                                type="date"
                                value={filters.dataFinal}
                                onChange={(e) => handleFilterChange('dataFinal', e.target.value)}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">
                                Status
                            </label>
                            <Select
                                value={filters.status}
                                onValueChange={(value) => handleFilterChange('status', value)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Selecione o status" />
                                </SelectTrigger>
                                <SelectContent>
                                    {STATUS_OPTIONS.map(option => (
                                        <SelectItem key={option.value} value={option.value}>
                                            {option.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex items-end">
                            <Button
                                className="w-full"
                                onClick={aplicarFiltros}
                            >
                                Aplicar Filtros
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Cards de Resumo */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Contas a Receber</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <p className="text-sm text-muted-foreground">Total em Aberto</p>
                            <p className="text-2xl font-bold text-green-600">
                                {formatarMoeda(dashboard.contasReceber.resumo.total_aberto_periodo)}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Total Atrasado</p>
                            <p className="text-xl font-bold text-red-600">
                                {formatarMoeda(dashboard.contasReceber.resumo.total_atrasado)}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Saldo</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <p className="text-sm text-muted-foreground">Saldo em Aberto</p>
                            <p className={`text-2xl font-bold ${dashboard.saldo.total_aberto_periodo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatarMoeda(dashboard.saldo.total_aberto_periodo)}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Saldo Atrasado</p>
                            <p className={`text-xl font-bold ${dashboard.saldo.total_atrasado >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatarMoeda(dashboard.saldo.total_atrasado)}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Contas a Pagar</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <p className="text-sm text-muted-foreground">Total em Aberto</p>
                            <p className="text-2xl font-bold text-red-600">
                                {formatarMoeda(dashboard.contasPagar.resumo.total_aberto_periodo)}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Total Atrasado</p>
                            <p className="text-xl font-bold text-red-600">
                                {formatarMoeda(dashboard.contasPagar.resumo.total_atrasado)}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Tabelas */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Contas a Pagar */}
                <Card>
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <CardTitle>
                                Contas a Pagar
                                <span className="ml-2 text-sm text-muted-foreground">
                                    ({dashboard.contasPagar.titulos_abertos_periodo.length +
                                        dashboard.contasPagar.titulos_atrasados.length} títulos)
                                </span>
                            </CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            {dashboard.contasPagar.titulos_atrasados.length > 0 && (
                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Títulos Atrasados</h3>
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Fornecedor</TableHead>
                                                <TableHead>Descrição</TableHead>
                                                <TableHead className="text-right">Valor</TableHead>
                                                <TableHead className="text-center">Vencimento</TableHead>
                                                <TableHead className="text-center">Status</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {dashboard.contasPagar.titulos_atrasados.map((conta) => (
                                                <TableRow key={conta.id}>
                                                    <TableCell>{conta.fornecedor?.nome || '-'}</TableCell>
                                                    <TableCell>{conta.historico}</TableCell>
                                                    <TableCell className="text-right">
                                                        {formatarMoeda(conta.valor)}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        {format(new Date(conta.vencimento), 'dd/MM/yyyy')}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(conta.status)}`}>
                                                            {getStatusLabel(conta.status)}
                                                        </span>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            )}

                            {dashboard.contasPagar.titulos_abertos_periodo.length > 0 && (
                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Títulos em Aberto</h3>
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Fornecedor</TableHead>
                                                <TableHead>Descrição</TableHead>
                                                <TableHead className="text-right">Valor</TableHead>
                                                <TableHead className="text-center">Vencimento</TableHead>
                                                <TableHead className="text-center">Status</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {dashboard.contasPagar.titulos_abertos_periodo.map((conta) => (
                                                <TableRow key={conta.id}>
                                                    <TableCell>{conta.fornecedor?.nome || '-'}</TableCell>
                                                    <TableCell>{conta.historico}</TableCell>
                                                    <TableCell className="text-right">
                                                        {formatarMoeda(conta.valor)}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        {format(new Date(conta.vencimento), 'dd/MM/yyyy')}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(conta.status)}`}>
                                                            {getStatusLabel(conta.status)}
                                                        </span>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Contas a Receber */}
                <Card>
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <CardTitle>
                                Contas a Receber
                                <span className="ml-2 text-sm text-muted-foreground">
                                    ({dashboard.contasReceber.titulos_abertos_periodo.length +
                                        dashboard.contasReceber.titulos_atrasados.length} títulos)
                                </span>
                            </CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            {dashboard.contasReceber.titulos_atrasados.length > 0 && (
                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Títulos Atrasados</h3>
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Cliente</TableHead>
                                                <TableHead>Descrição</TableHead>
                                                <TableHead className="text-right">Valor</TableHead>
                                                <TableHead className="text-center">Vencimento</TableHead>
                                                <TableHead className="text-center">Status</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {dashboard.contasReceber.titulos_atrasados.map((conta) => (
                                                <TableRow key={conta.id}>
                                                    <TableCell>{conta.cliente?.nome || '-'}</TableCell>
                                                    <TableCell>{conta.historico}</TableCell>
                                                    <TableCell className="text-right">
                                                        {formatarMoeda(conta.valor)}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        {format(new Date(conta.vencimento), 'dd/MM/yyyy')}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(conta.status)}`}>
                                                            {getStatusLabel(conta.status)}
                                                        </span>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            )}

                            {dashboard.contasReceber.titulos_abertos_periodo.length > 0 && (
                                <div className="space-y-4">
                                    <h3 className="text-lg font-semibold">Títulos em Aberto</h3>
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Cliente</TableHead>
                                                <TableHead>Descrição</TableHead>
                                                <TableHead className="text-right">Valor</TableHead>
                                                <TableHead className="text-center">Vencimento</TableHead>
                                                <TableHead className="text-center">Status</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {dashboard.contasReceber.titulos_abertos_periodo.map((conta) => (
                                                <TableRow key={conta.id}>
                                                    <TableCell>{conta.cliente?.nome || '-'}</TableCell>
                                                    <TableCell>{conta.historico}</TableCell>
                                                    <TableCell className="text-right">
                                                        {formatarMoeda(conta.valor)}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        {format(new Date(conta.vencimento), 'dd/MM/yyyy')}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(conta.status)}`}>
                                                            {getStatusLabel(conta.status)}
                                                        </span>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            )}

                            {/* Mensagem quando não houver títulos */}
                            {dashboard.contasReceber.titulos_atrasados.length === 0 &&
                                dashboard.contasReceber.titulos_abertos_periodo.length === 0 && (
                                    <div className="text-center py-8 text-gray-500">
                                        Nenhum título encontrado para o período selecionado
                                    </div>
                                )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Métricas Adicionais */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium">Total Pago no Período</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-lg font-bold">
                            {formatarMoeda(dashboard.saldo.total_pago_periodo)}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Recebimentos - Pagamentos
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium">Total Cancelado</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-lg font-bold">
                            {formatarMoeda(dashboard.saldo.total_cancelado_periodo)}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Títulos cancelados no período
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium">Quantidade de Títulos</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-lg font-bold">
                            {dashboard.saldo.quantidade_titulos}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Total de títulos no período
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Footer com Legendas */}
            <div className="flex flex-wrap gap-4 justify-center mt-6">
                {STATUS_OPTIONS.map(option => (
                    <div key={option.value} className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(option.value)}`}>
                            {option.label}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ContasPage;