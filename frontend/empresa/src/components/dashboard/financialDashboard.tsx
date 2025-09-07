// src/components/dashboard/FinancialDashboard.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    AlertCircle,
    ArrowUpCircle,
    ArrowDownCircle,
    Download,
    Search,
} from "lucide-react";
import { financialService } from '@/services/financialService';
import {
    FluxoCaixaFiltros
} from '@/types/financeiro';
import { DashboardOperacional } from '@/types/dashboardNovo';
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

const FinancialDashboard: React.FC = () => {
    // Estados
    const [data, setData] = useState<DashboardOperacional | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filters, setFilters] = useState<FluxoCaixaFiltros>({
        data_inicial: new Date().toISOString().split('T')[0],
        data_final: new Date().toISOString().split('T')[0],
        tipo: 'todos',
        status: 'todos',
        fonte: 'todos'
    });

    // Carregar dados quando os filtros mudarem
    useEffect(() => {
        const loadDataAsync = async () => {
            try {
                setLoading(true);
                const dashboardData = await financialService.getDashboardOperacional({
                    data_inicial: filters.data_inicial,
                    data_final: filters.data_final,
                    tipo: 'todos',
                    fonte: 'todas'
                });
                setData(dashboardData);
                setError(null);
            } catch (err) {
                console.error('Erro ao carregar dashboard:', err);
                setError('Falha ao carregar dados financeiros');
            } finally {
                setLoading(false);
            }
        };
        
        loadDataAsync();
    }, [filters]);

    // Handler para exportação
    const handleExport = async () => {
        try {
            const blob = await financialService.getRelatorioFluxoCaixa();
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
                                from: new Date(filters.data_inicial),
                                to: new Date(filters.data_final)
                            }}
                            onDateChange={(date) => {
                                if (date && date.from && date.to) {
                                    setFilters(prev => ({
                                        ...prev,
                                        data_inicial: date.from ? date.from.toISOString().split('T')[0] : filters.data_inicial,
                                        data_final: date.to ? date.to.toISOString().split('T')[0] : filters.data_final
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
                            change={data.totalizadores.entradas_realizadas.percentual || undefined}
                            color="text-green-600"
                        />
                        <MetricCard
                            title="Saídas Realizadas"
                            value={data.totalizadores.saidas_realizadas.valor}
                            icon={<ArrowDownCircle className="h-4 w-4 text-red-500" />}
                            change={data.totalizadores.saidas_realizadas.percentual || undefined}
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
                            {/* <MovementTable
                                movements={data.movimentos}
                                onStatusChange={handleStatusChange}
                            /> */}
                        </CardContent>
                    </Card>
                </>
            )}
        </div>
    );
};

export default FinancialDashboard;