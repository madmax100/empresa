// src/components/dashboard/FinancialDashboard.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    AlertCircle,
    ArrowUpCircle,
    ArrowDownCircle,
    Download,
    Search,
} from "lucide-react";
import { financialService } from '@/services/financialService';
import {
    DashboardOperacional,
    Movimento,
    FluxoCaixaFiltros
} from '@/types/financeiro';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { DateRangePicker } from '../common/DataRangerPicker';

// Novos subcomponentes
const MetricCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    change?: number;
    color: string;
}> = ({ title, value, icon, change, color }) => (
    <Card>
        <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
                {icon}
                <span className="ml-2">{title}</span>
            </CardTitle>
        </CardHeader>
        <CardContent>
            <div className={`text-2xl font-bold ${color}`}>
                {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                }).format(value)}
            </div>
            {change !== undefined && (
                <div className="text-sm text-muted-foreground">
                    {change >= 0 ? '+' : ''}{change.toFixed(1)}% vs mês anterior
                </div>
            )}
        </CardContent>
    </Card>
);

const MovementTable: React.FC<{
    movements: Movimento[];
    onStatusChange: (id: number, status: string) => Promise<void>;
}> = ({ movements, onStatusChange }) => (
    <Table>
        <TableHeader>
            <TableRow>
                <TableHead>Data</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead className="text-right">Valor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead></TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            {movements.map((movement) => (
                <TableRow key={movement.id}>
                    <TableCell>{new Date(movement.data).toLocaleDateString()}</TableCell>
                    <TableCell>{movement.descricao}</TableCell>
                    <TableCell>{movement.categoria}</TableCell>
                    <TableCell className={`text-right font-medium ${movement.tipo === 'entrada' ? 'text-green-600' : 'text-red-600'
                        }`}>
                        {movement.tipo === 'saida' ? '- ' : ''}
                        {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                        }).format(movement.valor)}
                    </TableCell>
                    <TableCell>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${movement.status === 'realizado'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                            }`}>
                            {movement.status}
                        </span>
                    </TableCell>
                    <TableCell>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onStatusChange(movement.id,
                                movement.status === 'realizado' ? 'previsto' : 'realizado'
                            )}
                        >
                            {movement.status === 'realizado' ? 'Estornar' : 'Realizar'}
                        </Button>
                    </TableCell>
                </TableRow>
            ))}
        </TableBody>
    </Table>
);

const FinancialDashboard: React.FC = () => {
    // Estados
    const [data, setData] = useState<DashboardOperacional | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filters, setFilters] = useState<FluxoCaixaFiltros>({
        dataInicial: new Date().toISOString().split('T')[0],
        dataFinal: new Date().toISOString().split('T')[0],
        tipo: 'todos',
        status: 'todos',
        fonte: 'todos'
    });

    // Carregar dados
    const loadData = async () => {
        try {
            setLoading(true);
            const dashboardData = await financialService.getDashboardOperacional(filters);
            setData(dashboardData);
            setError(null);
        } catch (err) {
            console.error('Erro ao carregar dashboard:', err);
            setError('Falha ao carregar dados financeiros');
        } finally {
            setLoading(false);
        }
    };

    // Carregar dados quando os filtros mudarem
    useEffect(() => {
        loadData();
    }, [filters]);

    // Handler para mudança de status
    const handleStatusChange = async (id: number, newStatus: string) => {
        try {
            setLoading(true);
            if (newStatus === 'realizado') {
                await financialService.realizarLancamento(id);
            } else {
                await financialService.estornarLancamento(id, 'Estorno operacional');
            }
            await loadData();
        } catch (err) {
            console.error('Erro ao atualizar status:', err);
            setError('Falha ao atualizar status do lançamento');
        } finally {
            setLoading(false);
        }
    };

    // Handler para exportação
    const handleExport = async () => {
        try {
            const blob = await financialService.getRelatorioFluxoCaixa(
                {
                    inicio: filters.dataInicial,
                    fim: filters.dataFinal
                },
                'excel'
            );
            financialService.exportarRelatorio(blob, 'fluxo-caixa.xlsx');
        } catch (err) {
            console.error('Erro ao exportar:', err);
            setError('Falha ao exportar dados');
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 space-y-6">
            {error && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            {/* Filtros */}
            <Card>
                <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <DateRangePicker
                            date={{
                                from: new Date(filters.dataInicial),
                                to: new Date(filters.dataFinal)
                            }}
                            onDateChange={(date) => {
                                if (date && date.from && date.to) {
                                    setFilters(prev => ({
                                        ...prev,
                                        dataInicial: date.from ? date.from.toISOString().split('T')[0] : filters.dataInicial,
                                        dataFinal: date.to ? date.to.toISOString().split('T')[0] : filters.dataFinal
                                    }));
                                }
                            }}
                        />

                        <Select
                            value={filters.tipo}
                            onValueChange={(value) => setFilters(prev => ({ ...prev, tipo: value as FluxoCaixaFiltros['tipo'] }))}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Tipo de Movimento" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="todos">Todos</SelectItem>
                                <SelectItem value="entrada">Entradas</SelectItem>
                                <SelectItem value="saida">Saídas</SelectItem>
                            </SelectContent>
                        </Select>

                        <div className="relative">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Buscar..."
                                className="pl-8"
                                value={filters.searchTerm || ''}
                                onChange={(e) => setFilters(prev => ({
                                    ...prev,
                                    searchTerm: e.target.value
                                }))}
                            />
                        </div>

                        <Button variant="outline" onClick={handleExport}>
                            <Download className="h-4 w-4 mr-2" />
                            Exportar
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {data && (
                <>
                    {/* Métricas */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <MetricCard
                            title="Entradas Realizadas"
                            value={data.totalizadores.entradas_realizadas.valor}
                            icon={<ArrowUpCircle className="h-4 w-4 text-green-500" />}
                            change={data.totalizadores.entradas_realizadas.percentual}
                            color="text-green-600"
                        />
                        <MetricCard
                            title="Saídas Realizadas"
                            value={data.totalizadores.saidas_realizadas.valor}
                            icon={<ArrowDownCircle className="h-4 w-4 text-red-500" />}
                            change={data.totalizadores.saidas_realizadas.percentual}
                            color="text-red-600"
                        />
                        <MetricCard
                            title="Saldo Atual"
                            value={data.resumo.saldo_final}
                            icon={<ArrowUpCircle className="h-4 w-4 text-blue-500" />}
                            change={data.resumo.variacao_percentual}
                            color="text-blue-600"
                        />
                        <MetricCard
                            title="Saldo Projetado"
                            value={data.resumo.saldo_projetado}
                            icon={<ArrowUpCircle className="h-4 w-4 text-purple-500" />}
                            color="text-purple-600"
                        />
                    </div>

                    {/* Movimentações */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Movimentações</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <MovementTable
                                movements={data.movimentos}
                                onStatusChange={handleStatusChange}
                            />
                        </CardContent>
                    </Card>
                </>
            )}
        </div>
    );
};

export default FinancialDashboard;