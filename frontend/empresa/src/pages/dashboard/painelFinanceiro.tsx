import { useEffect, useState, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { format } from "date-fns";
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Download, RefreshCcw, ChevronDown, ChevronUp, CalendarIcon, Search } from 'lucide-react';
import { DateRange } from "react-day-picker";
import { ptBR } from 'date-fns/locale';
import { DashboardData, STATUS_OPTIONS } from '@/types/models';
import { contasPagarService, contasReceberService, financeiroDashboard } from '@/services/api';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { toast } from '../../components/ui/toast/use-toast';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alertdialog";
import { Toaster } from '../../components/ui/toast/toaster';
import { cn } from '@/lib/utils';
import { Checkbox } from '@/components/ui/checkbox';

// types.ts
type SortDirection = 'asc' | 'desc' | null;

interface SortConfig {
    key: string;
    direction: SortDirection;
}

// sorting-utils.ts
const sortData = <T extends Record<string, any>>(
    data: T[],
    sortConfig: SortConfig
): T[] => {
    if (!sortConfig.key || !sortConfig.direction) return data;

    return [...data].sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];

        // Handle nested properties (e.g., cliente.nome or fornecedor.nome)
        if (sortConfig.key.includes('.')) {
            const keys = sortConfig.key.split('.');
            aValue = keys.reduce((obj, key) => obj?.[key], a);
            bValue = keys.reduce((obj, key) => obj?.[key], b);
        }

        // Handle monetary values
        if (sortConfig.key === 'valor') {
            aValue = parseFloat(aValue);
            bValue = parseFloat(bValue);
        }

        // Handle dates
        if (sortConfig.key === 'vencimento') {
            aValue = new Date(aValue).getTime();
            bValue = new Date(bValue).getTime();
        }

        // Perform the comparison
        if (typeof aValue === 'string' && typeof bValue === 'string') {
            return sortConfig.direction === 'asc'
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        }

        if (typeof aValue === 'number' && typeof bValue === 'number') {
            return sortConfig.direction === 'asc'
                ? aValue - bValue
                : bValue - aValue;
        }

        return 0;
    });
};

// SortableTableHeader component
const SortableTableHeader = ({
    children,
    sortKey,
    currentSort,
    onSort,
    className = ""
}: {
    children: React.ReactNode;
    sortKey: string;
    currentSort: SortConfig;
    onSort: (key: string) => void;
    className?: string;
}) => {
    const isCurrent = currentSort.key === sortKey;

    return (
        <TableHead
            className={`cursor-pointer hover:bg-muted/50 ${className}`}
            onClick={() => onSort(sortKey)}
        >
            <div className="flex items-center gap-2">
                {children}
                {isCurrent && (
                    currentSort.direction === 'asc'
                        ? <ChevronUp className="h-4 w-4" />
                        : <ChevronDown className="h-4 w-4" />
                )}
            </div>
        </TableHead>
    );
};


const FinancialDashboard = () => {
    const [date, setDate] = useState<DateRange | undefined>(() => {
        const today = new Date();
        const first = new Date(today.getFullYear(), today.getMonth(), 1);
        return { from: first, to: today };
    });
    const [status, setStatus] = useState<'all' | 'A' | 'P' | 'C'>('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [expandedTables, setExpandedTables] = useState({
        receber: false,
        pagar: false
    });
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [debouncedSearchTerm, setDebouncedSearchTerm] = useState(searchTerm);
    const [dialogState, setDialogState] = useState({
        isOpen: false,
        title: '',
        message: '',
        tipo: '' as 'receber' | 'pagar',
        tituloId: 0,
        novoStatus: '',
    });
    // Baixa em lote (contas a pagar)
    const [batchSupplier, setBatchSupplier] = useState<string>('');
    const [batchDialogOpen, setBatchDialogOpen] = useState(false);
    

    // Função de atualização de status
    const handleStatusChange = async (
        tipo: 'receber' | 'pagar',
        tituloId: number,
        novoStatus: string
    ) => {
        console.log('Iniciando atualização:', { tipo, tituloId, novoStatus });
        try {
            setLoading(true);
            const service = tipo === 'receber' ? contasReceberService : contasPagarService;

            const response = await service.atualizarStatus(tituloId, novoStatus);
            console.log('Resposta da atualização:', response);

            // Primeiro fecha o diálogo
            setDialogState(prev => ({ ...prev, isOpen: false }));

            // Atualiza o estado local de forma otimista
            setData(prevData => {
                if (!prevData) return prevData;

                const updateTitulosStatus = (titulos: any[]) =>
                    titulos.map(titulo =>
                        titulo.id === tituloId
                            ? { ...titulo, status: novoStatus }
                            : titulo
                    );

                if (tipo === 'receber') {
                    const contasReceber = {
                        ...prevData.contasReceber,
                        titulos_atrasados: updateTitulosStatus(prevData.contasReceber.titulos_atrasados),
                        titulos_abertos_periodo: updateTitulosStatus(prevData.contasReceber.titulos_abertos_periodo),
                        titulos_pagos_periodo: updateTitulosStatus(prevData.contasReceber.titulos_pagos_periodo)
                    };
                    return { ...prevData, contasReceber };
                } else {
                    const contasPagar = {
                        ...prevData.contasPagar,
                        titulos_atrasados: updateTitulosStatus(prevData.contasPagar.titulos_atrasados),
                        titulos_abertos_periodo: updateTitulosStatus(prevData.contasPagar.titulos_abertos_periodo),
                        titulos_pagos_periodo: updateTitulosStatus(prevData.contasPagar.titulos_pagos_periodo)
                    };
                    return { ...prevData, contasPagar };
                }
            });

            toast({
                title: "Status atualizado",
                description: `Status do título ${novoStatus === 'C' ? 'cancelado' : 'reativado'} com sucesso.`,
                variant: "success",
            });

            // Recarrega os dados após um breve delay
            setTimeout(fetchData, 500);

        } catch (error) {
            console.error('Erro na atualização:', error);
            toast({
                title: "Erro",
                description: "Não foi possível atualizar o status do título.",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    // Excluir título (sem marcar como pago)
    const handleDelete = async (tipo: 'receber' | 'pagar', tituloId: number) => {
        try {
            if (!window.confirm('Tem certeza que deseja excluir este título? Esta ação não pode ser desfeita.')) {
                return;
            }
            setLoading(true);
            if (tipo === 'receber') {
                await contasReceberService.excluir(tituloId);
            } else {
                await contasPagarService.excluir(tituloId);
            }
            toast({ title: 'Excluído', description: 'Título removido com sucesso.', variant: 'success' });
            await fetchData();
        } catch (error) {
            console.error('Erro ao excluir título:', error);
            toast({ title: 'Erro', description: 'Não foi possível excluir o título.', variant: 'destructive' });
        } finally {
            setLoading(false);
        }
    };


    const getStatusLabel = (statusCode: string) => {
        const option = STATUS_OPTIONS.find(opt => opt.value === statusCode);
        return option ? option.label : 'Desconhecido';
    };

    const getStatusColor = (statusCode: string) => {
        switch (statusCode) {
            case 'A':
                return 'text-yellow-600 bg-yellow-50 px-2 py-1 rounded-full text-xs font-medium';
            case 'P':
                return 'text-green-600 bg-green-50 px-2 py-1 rounded-full text-xs font-medium';
            case 'C':
                return 'text-red-600 bg-red-50 px-2 py-1 rounded-full text-xs font-medium';
            default:
                return 'text-gray-600 bg-gray-50 px-2 py-1 rounded-full text-xs font-medium';
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearchTerm(searchTerm);
        }, 500);

        return () => clearTimeout(timer);
    }, [searchTerm]);

    const fetchData = useCallback(async () => {
        if (!date?.from || !date?.to) return;

        try {
            setLoading(true);
            setError(null);

            const response = await financeiroDashboard.resumoGeral({
                dataInicial: date.from.toISOString().split('T')[0],
                dataFinal: date.to.toISOString().split('T')[0],
                status: status,
                searchTerm: debouncedSearchTerm
            });

            setData(response);
        } catch (error) {
            console.error('Error fetching data:', error);
            setError('Falha ao carregar os dados. Por favor, tente novamente.');
        } finally {
            setLoading(false);
        }
    }, [date?.from, date?.to, status, debouncedSearchTerm]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Handler: Baixar todos em aberto do mesmo fornecedor (nome)
    const handleBatchPayFornecedor = async () => {
        if (!data) return;
        try {
            setLoading(true);
            const abertos = data.contasPagar.titulos_abertos_periodo || [];
            const paraBaixar = abertos.filter(t => (t.fornecedor?.nome || '') === batchSupplier);
            if (paraBaixar.length === 0) {
                toast({ title: 'Nada a baixar', description: 'Não há títulos em aberto para o fornecedor selecionado.', variant: 'default' });
                return;
            }
            await Promise.all(
                paraBaixar.map(t => contasPagarService.atualizarStatus(t.id, 'P'))
            );
            toast({ title: 'Baixa em lote concluída', description: `${paraBaixar.length} títulos marcados como pagos para ${batchSupplier}.`, variant: 'success' });
            setBatchDialogOpen(false);
            setBatchSupplier('');
            // Recarregar
            await fetchData();
        } catch (err) {
            console.error('Erro na baixa em lote:', err);
            toast({ title: 'Erro na baixa em lote', description: 'Não foi possível concluir a operação.', variant: 'destructive' });
        } finally {
            setLoading(false);
        }
    };

    const toggleTableExpansion = (table: 'receber' | 'pagar') => {
        setExpandedTables(prev => ({
            ...prev,
            [table]: !prev[table]
        }));
    };


    const [sortConfig, setSortConfig] = useState<SortConfig>({
        key: '',
        direction: null
    });

    const handleSort = (key: string) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
        }));
    };

    // Modified renderTitulosTable function
    const renderTitulosTable = (titulos: any[], tipo: 'receber' | 'pagar') => {
        console.log('Renderizando tabela:', { tipo, quantidadeTitulos: titulos.length });
        return (
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead className="w-12">Status</TableHead>
                        <SortableTableHeader
                            sortKey="historico"
                            currentSort={sortConfig}
                            onSort={handleSort}
                        >
                            Histórico
                        </SortableTableHeader>
                        <SortableTableHeader
                            sortKey={tipo === 'receber' ? 'cliente.nome' : 'fornecedor.nome'}
                            currentSort={sortConfig}
                            onSort={handleSort}
                        >
                            {tipo === 'receber' ? 'Cliente' : 'Fornecedor'}
                        </SortableTableHeader>
                        <SortableTableHeader
                            sortKey="valor"
                            currentSort={sortConfig}
                            onSort={handleSort}
                            className="text-right"
                        >
                            Valor
                        </SortableTableHeader>
                        <SortableTableHeader
                            sortKey="vencimento"
                            currentSort={sortConfig}
                            onSort={handleSort}
                            className="text-center"
                        >
                            Vencimento
                        </SortableTableHeader>
                        <TableHead className="w-24 text-center">Ações</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {sortData(titulos, sortConfig).map((titulo) => {
                        return (
                            <TableRow key={titulo.id}>
                                <TableCell className="flex items-center gap-2">
                                    <div className="flex items-center gap-2">
                                        <Checkbox
                                            id={`checkbox-${titulo.id}`}
                                            checked={titulo.status === 'C'}
                                            onCheckedChange={(checked) => {
                                                console.log('onCheckedChange triggered:', {
                                                    tituloId: titulo.id,
                                                    currentStatus: titulo.status,
                                                    newStatus: checked ? 'C' : 'A',
                                                    checked
                                                });

                                                const newStatus = checked ? 'C' : 'A';
                                                const message = checked
                                                    ? `Deseja cancelar o ${tipo === 'receber' ? 'título a receber' : 'título a pagar'} ${titulo.historico}?`
                                                    : `Deseja remover o cancelamento do ${tipo === 'receber' ? 'título a receber' : 'título a pagar'} ${titulo.historico}?`;

                                                console.log('Abrindo diálogo:', {
                                                    tituloId: titulo.id,
                                                    newStatus,
                                                    message
                                                });

                                                setDialogState({
                                                    isOpen: true,
                                                    title: checked ? 'Confirmar Cancelamento' : 'Remover Cancelamento',
                                                    message,
                                                    tipo,
                                                    tituloId: titulo.id,
                                                    novoStatus: newStatus
                                                });
                                            }}
                                            className="cursor-pointer"
                                        />
                                        <label
                                            htmlFor={`checkbox-${titulo.id}`}
                                            className={cn(
                                                "text-sm font-medium leading-none cursor-pointer",
                                                getStatusColor(titulo.status)
                                            )}
                                        >
                                            {getStatusLabel(titulo.status)}
                                        </label>
                                    </div>
                                </TableCell>
                                <TableCell>{titulo.historico}</TableCell>
                                <TableCell>
                                    {tipo === 'receber' ? titulo.cliente?.nome : titulo.fornecedor?.nome}
                                </TableCell>
                                <TableCell className="text-right">
                                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                        .format(parseFloat(titulo.valor))}
                                </TableCell>
                                <TableCell className="text-center">
                                    {format(new Date(titulo.vencimento), 'dd/MM/yyyy')}
                                </TableCell>
                                <TableCell className="text-center">
                                    <div className="flex items-center justify-center gap-2">
                                        {/* Excluir */}
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="text-red-600 hover:text-red-800"
                                            onClick={() => handleDelete(tipo, titulo.id)}
                                        >
                                            Excluir
                                        </Button>
                                    </div>
                                </TableCell>
                            </TableRow>
                        );

                    })}
                </TableBody>
            </Table>
        );
    }

    if (loading) return <div>Carregando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;
    if (!data) return null;

    const confirmStatusChange = () => {
        console.log('Confirmando mudança de status:', dialogState);
        if (dialogState.tituloId && dialogState.tipo && dialogState.novoStatus) {
            handleStatusChange(
                dialogState.tipo,
                dialogState.tituloId,
                dialogState.novoStatus
            );
        }
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex flex-col space-y-6">
                <h1 className="text-2xl font-bold">Painel Financeiro</h1>

                {/* Filtros */}
                <div className="flex flex-col lg:flex-row gap-6">
                    <div className="w-full lg:w-auto space-y-4">
                        <Card>
                            <CardContent className="p-4">
                                <Popover>
                                    <PopoverTrigger asChild>
                                        <Button
                                            variant="outline"
                                            className="w-full justify-start text-left font-normal"
                                        >
                                            <CalendarIcon className="mr-2 h-4 w-4" />
                                            {date?.from ? (
                                                date.to ? (
                                                    <>
                                                        {format(date.from, "dd/MM/yyyy")} -{" "}
                                                        {format(date.to, "dd/MM/yyyy")}
                                                    </>
                                                ) : (
                                                    format(date.from, "dd/MM/yyyy")
                                                )
                                            ) : (
                                                <span>Selecione um período</span>
                                            )}
                                        </Button>
                                    </PopoverTrigger>
                                    <PopoverContent className="w-auto p-0" align="start">
                                        <Calendar
                                            initialFocus
                                            mode="range"
                                            defaultMonth={date?.from}
                                            selected={date}
                                            onSelect={setDate}
                                            numberOfMonths={2}
                                            locale={ptBR}
                                        />
                                    </PopoverContent>
                                </Popover>
                            </CardContent>
                        </Card>

                        <div className="space-y-2">
                            <div className="relative">
                                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Buscar cliente/fornecedor"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-8"
                                />
                            </div>

                            <Select
                                value={status}
                                onValueChange={(value) => setStatus(value as 'all' | 'A' | 'P' | 'C')}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Status" />
                                </SelectTrigger>
                                <SelectContent>
                                    {STATUS_OPTIONS.map(option => (
                                        <SelectItem key={option.value} value={option.value}>
                                            {option.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>

                            <div className="flex gap-2">
                                <Button variant="secondary" className="w-full gap-2" onClick={fetchData}>
                                    <RefreshCcw className="h-4 w-4" />
                                    <span>Atualizar</span>
                                </Button>

                                <Button variant="outline" className="w-full gap-2">
                                    <Download className="h-4 w-4" />
                                    <span>Exportar</span>
                                </Button>
                            </div>
                        </div>
                    </div>

                    {/* Cards Principais */}
                    <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Contas a Receber */}
                        <Card className="h-fit">
                            <CardHeader>
                                <CardTitle className="flex justify-between items-center">
                                    <span>Contas a Receber</span>
                                    <Button
                                        variant="ghost"
                                        onClick={() => toggleTableExpansion('receber')}
                                        size="sm"
                                    >
                                        {expandedTables.receber ? (
                                            <ChevronUp className="h-4 w-4" />
                                        ) : (
                                            <ChevronDown className="h-4 w-4" />
                                        )}
                                    </Button>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {/* Atrasadas */}
                                <div className="flex justify-between items-center p-2 bg-red-50 rounded-lg">
                                    <span className="text-sm">Atrasadas</span>
                                    <div className="text-right">
                                        <div className="text-base font-semibold text-red-600">
                                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                                .format(data?.contasReceber.resumo.total_atrasado || 0)}
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            {data?.contasReceber.titulos_atrasados.length || 0} títulos
                                        </span>
                                    </div>
                                </div>

                                {/* Em Aberto */}
                                <div className="flex justify-between items-center p-2 bg-yellow-50 rounded-lg">
                                    <span className="text-sm">Em Aberto</span>
                                    <div className="text-right">
                                        <div className="text-base font-semibold text-yellow-600">
                                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                                .format(data?.contasReceber.resumo.total_aberto_periodo || 0)}
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            {data?.contasReceber.titulos_abertos_periodo.length || 0} títulos
                                        </span>
                                    </div>
                                </div>

                                {/* Recebidas */}
                                <div className="flex justify-between items-center p-2 bg-green-50 rounded-lg">
                                    <span className="text-sm">Recebidas</span>
                                    <div className="text-right">
                                        <div className="text-base font-semibold text-green-600">
                                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                                .format(data?.contasReceber.resumo.total_pago_periodo || 0)}
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            {data?.contasReceber.titulos_pagos_periodo.length || 0} títulos
                                        </span>
                                    </div>
                                </div>

                                {/* Total */}
                                <div className="flex justify-between items-center p-2 bg-slate-50 rounded-lg border-t">
                                    <span className="font-medium">Total</span>
                                    <div className="text-right">
                                        <div className="text-lg font-bold">
                                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                                .format((data?.contasReceber.resumo.total_atrasado || 0) +
                                                    (data?.contasReceber.resumo.total_aberto_periodo || 0) +
                                                    (data?.contasReceber.resumo.total_pago_periodo || 0))}
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            Total de títulos: {(data?.contasReceber.titulos_atrasados.length || 0) +
                                                (data?.contasReceber.titulos_abertos_periodo.length || 0) +
                                                (data?.contasReceber.titulos_pagos_periodo.length || 0)}
                                        </span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Contas a Pagar */}
                        <Card className="h-fit">
                            <CardHeader>
                                <CardTitle className="flex justify-between items-center">
                                    <span>Contas a Pagar</span>
                                    <Button
                                        variant="ghost"
                                        onClick={() => toggleTableExpansion('pagar')}
                                        size="sm"
                                    >
                                        {expandedTables.pagar ? (
                                            <ChevronUp className="h-4 w-4" />
                                        ) : (
                                            <ChevronDown className="h-4 w-4" />
                                        )}
                                    </Button>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {/* Atrasadas */}
                                <div className="flex justify-between items-center p-2 bg-red-50 rounded-lg">
                                    <span className="text-sm">Atrasadas</span>
                                    <div className="text-right">
                                        <div className="text-base font-semibold text-red-600">
                                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                                .format(data?.contasPagar.resumo.total_atrasado || 0)}
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            {data?.contasPagar.titulos_atrasados.length || 0} títulos
                                        </span>
                                    </div>
                                </div>

                                {/* Em Aberto */}
                                <div className="flex justify-between items-center p-2 bg-yellow-50 rounded-lg">
                                    <span className="text-sm">Em Aberto</span>
                                    <div className="text-right">
                                        <div className="text-base font-semibold text-yellow-600">
                                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                                .format(data?.contasPagar.resumo.total_aberto_periodo || 0)}
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            {data?.contasPagar.titulos_abertos_periodo.length || 0} títulos
                                        </span>
                                    </div>
                                </div>

                                {/* Baixar todos em aberto por Fornecedor */}
                                <div className="flex gap-2 items-center">
                                    <Select value={batchSupplier} onValueChange={setBatchSupplier}>
                                        <SelectTrigger className="w-full" aria-label="Fornecedor para baixa em lote">
                                            <SelectValue placeholder="Selecionar fornecedor (em aberto)" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {Array.from(new Set((data?.contasPagar.titulos_abertos_periodo || [])
                                                .map(t => t.fornecedor?.nome)
                                                .filter(Boolean)
                                            )).map((nome: any) => (
                                                <SelectItem key={nome as string} value={nome as string}>{nome as string}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <Button
                                        variant="secondary"
                                        disabled={!batchSupplier}
                                        onClick={() => setBatchDialogOpen(true)}
                                    >
                                        Baixar todos
                                    </Button>
                                </div>

                                {/* Pagas */}
                                <div className="flex justify-between items-center p-2 bg-green-50 rounded-lg">
                                    <span className="text-sm">Pagas</span>
                                    <div className="text-right">
                                        <div className="text-base font-semibold text-green-600">
                                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                                .format(data?.contasPagar.resumo.total_pago_periodo || 0)}
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            {data?.contasPagar.titulos_pagos_periodo.length || 0} títulos
                                        </span>
                                    </div>
                                </div>

                                {/* Total */}
                                <div className="flex justify-between items-center p-2 bg-slate-50 rounded-lg border-t">
                                    <span className="font-medium">Total</span>
                                    <div className="text-right">
                                        <div className="text-lg font-bold">
                                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                                .format((data?.contasPagar.resumo.total_atrasado || 0) +
                                                    (data?.contasPagar.resumo.total_aberto_periodo || 0) +
                                                    (data?.contasPagar.resumo.total_pago_periodo || 0))}
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            Total de títulos: {(data?.contasPagar.titulos_atrasados.length || 0) +
                                                (data?.contasPagar.titulos_abertos_periodo.length || 0) +
                                                (data?.contasPagar.titulos_pagos_periodo.length || 0)}
                                        </span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>

                {/* Cards de Saldo */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Saldo Atrasado */}
                    <Card className="bg-slate-50/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Saldo Atrasado</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-lg font-bold ${data?.saldo.total_atrasado >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                    .format(data?.saldo.total_atrasado || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                                Receber - Pagar (Atrasados)
                            </div>
                        </CardContent>
                    </Card>

                    {/* Saldo em Aberto */}
                    <Card className="bg-slate-50/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Saldo em Aberto</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-lg font-bold ${data?.saldo.total_aberto_periodo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                    .format(data?.saldo.total_aberto_periodo || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                                Receber - Pagar (Período)
                            </div>
                        </CardContent>
                    </Card>

                    {/* Saldo Realizado */}
                    <Card className="bg-slate-50/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Saldo Realizado</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-lg font-bold ${data?.saldo.total_pago_periodo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                    .format(data?.saldo.total_pago_periodo || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                                Recebido - Pago (Período)
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Tabelas Expandidas */}
                {expandedTables.receber && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Detalhamento Contas a Receber</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-6">
                                {data?.contasReceber.titulos_atrasados.length > 0 && (
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Títulos Atrasados</h3>
                                        <div className="rounded-md border">
                                            {renderTitulosTable(data.contasReceber.titulos_atrasados, 'receber')}
                                        </div>
                                    </div>
                                )}

                                {data?.contasReceber.titulos_abertos_periodo.length > 0 && (
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Títulos em Aberto</h3>
                                        <div className="rounded-md border">
                                            {renderTitulosTable(data.contasReceber.titulos_abertos_periodo, 'receber')}
                                        </div>
                                    </div>
                                )}

                                {data?.contasReceber.titulos_pagos_periodo.length > 0 && (
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Títulos Recebidos</h3>
                                        <div className="rounded-md border">
                                            {renderTitulosTable(data.contasReceber.titulos_pagos_periodo, 'receber')}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {expandedTables.pagar && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Detalhamento Contas a Pagar</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-6">
                                {data?.contasPagar.titulos_atrasados.length > 0 && (
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Títulos Atrasados</h3>
                                        <div className="rounded-md border">
                                            {renderTitulosTable(data.contasPagar.titulos_atrasados, 'pagar')}
                                        </div>
                                    </div>
                                )}

                                {data?.contasPagar.titulos_abertos_periodo.length > 0 && (
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Títulos em Aberto</h3>
                                        <div className="rounded-md border">
                                            {renderTitulosTable(data.contasPagar.titulos_abertos_periodo, 'pagar')}
                                        </div>
                                    </div>
                                )}

                                {data?.contasPagar.titulos_pagos_periodo.length > 0 && (
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-semibold">Títulos Pagos</h3>
                                        <div className="rounded-md border">
                                            {renderTitulosTable(data.contasPagar.titulos_pagos_periodo, 'pagar')}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                )}
                {/* Cards de Saldo */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Saldo Atrasado */}
                    <Card className="bg-slate-50/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Saldo Atrasado</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-lg font-bold ${data?.saldo.total_atrasado >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                    .format(data?.saldo.total_atrasado || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                                Receber - Pagar (Atrasados)
                            </div>
                        </CardContent>
                    </Card>

                    {/* Saldo em Aberto */}
                    <Card className="bg-slate-50/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Saldo em Aberto</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-lg font-bold ${data?.saldo.total_aberto_periodo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                    .format(data?.saldo.total_aberto_periodo || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                                Receber - Pagar (Período)
                            </div>
                        </CardContent>
                    </Card>

                    {/* Saldo Realizado */}
                    <Card className="bg-slate-50/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Saldo Realizado</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-lg font-bold ${data?.saldo.total_pago_periodo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                                    .format(data?.saldo.total_pago_periodo || 0)}
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">
                                Recebido - Pago (Período)
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Botão Extra de Atualização e Loading States */}
                <div className="flex justify-end mt-4">
                    <Button
                        variant="outline"
                        onClick={fetchData}
                        disabled={loading}
                        className="flex items-center gap-2"
                    >
                        {loading ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary" />
                        ) : (
                            <RefreshCcw className="h-4 w-4" />
                        )}
                        Atualizar Dados
                    </Button>
                </div>

                {/* Legenda dos Status */}
                <div className="flex flex-wrap gap-4 justify-center mt-6 pb-4">
                    {STATUS_OPTIONS.map(status => (
                        <div key={status.value} className="flex items-center gap-2">
                            <span className={getStatusColor(status.value)}>
                                {status.label}
                            </span>
                        </div>
                    ))}
                </div>
                {/* Diálogo de confirmação - Baixa em lote por fornecedor (contas a pagar) */}
                <AlertDialog open={batchDialogOpen}>
                    <AlertDialogContent>
                        <AlertDialogHeader>
                            <AlertDialogTitle>Confirmar baixa em lote</AlertDialogTitle>
                            <AlertDialogDescription>
                                Deseja marcar como pagos todos os títulos em aberto do fornecedor:
                                <br />
                                <strong>{batchSupplier || '-'}</strong>?
                                <br />
                                Esta ação não pode ser desfeita.
                            </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                            <AlertDialogCancel onClick={() => setBatchDialogOpen(false)}>
                                Cancelar
                            </AlertDialogCancel>
                            <AlertDialogAction onClick={handleBatchPayFornecedor}>
                                Confirmar
                            </AlertDialogAction>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialog>
            </div>
            <AlertDialog open={dialogState.isOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>{dialogState.title}</AlertDialogTitle>
                        <AlertDialogDescription>
                            {dialogState.message}
                            <br />
                            Esta ação não pode ser desfeita.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel
                            onClick={() => {
                                console.log('Cancelando diálogo');
                                setDialogState(prev => ({ ...prev, isOpen: false }));
                            }}
                        >
                            Cancelar
                        </AlertDialogCancel>
                        <AlertDialogAction
                            onClick={() => {
                                console.log('Confirmando ação no diálogo');
                                confirmStatusChange();
                            }}
                        >
                            Confirmar
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
            <Toaster />
        </div>
    );
};

export default FinancialDashboard;
