import React, { useState, useEffect } from 'react';

import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Bill, DashboardResponse2, FilterParams2 } from '@/types/models';
import { financialService } from '@/services/financialService';
import { contasPagarService, contasReceberService } from '@/services/api';



interface FiltersProps {
    onFilterChange: (filters: FilterParams2) => void;
}

// Componente de Filtros
const Filters: React.FC<FiltersProps> = ({ onFilterChange }) => {
    // Função para obter a data atual no formato YYYY-MM-DD
    const getCurrentDate = () => {
        const today = new Date();
        return today.toISOString().split('T')[0];
    };

    const [filters, setFilters] = useState<FilterParams2>({
        dataInicial: getCurrentDate(),
        dataFinal: getCurrentDate(),
        status: 'all',
        searchTerm: ''
    });

    // Dispara a busca inicial com as datas ao montar o componente
    useEffect(() => {
        onFilterChange(filters);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filters.dataInicial, filters.dataFinal, filters.status, filters.searchTerm]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const newFilters = {
            ...filters,
            [e.target.name]: e.target.value
        };
        setFilters(newFilters);
        onFilterChange(newFilters);
    };

    return (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Data Inicial
                    </label>
                    <input
                        type="date"
                        name="dataInicial"
                        value={filters.dataInicial}
                        onChange={handleChange}
                        className="mt-1 block w-full p-2 text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Data Final
                    </label>
                    <input
                        type="date"
                        name="dataFinal"
                        value={filters.dataFinal}
                        onChange={handleChange}
                        className="mt-1 block w-full p-2 text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Status
                    </label>
                    <select
                        name="status"
                        value={filters.status}
                        onChange={handleChange}
                        className="mt-1 block w-full p-2 text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">Todos</option>
                        <option value="A">Em Aberto</option>
                        <option value="P">Pago</option>
                        <option value="C">Cancelado</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Buscar
                    </label>
                    <input
                        type="text"
                        name="searchTerm"
                        value={filters.searchTerm}
                        onChange={handleChange}
                        placeholder="Buscar por nome ou histórico..."
                        className="mt-1 block w-full p-2 text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            </div>
        </div>
    );
};

interface SummaryData {
    total_receber?: number;
    total_pagar?: number;
    total_atrasado?: number;
    total_aberto_periodo?: number;
    total_pago_periodo?: number;
    trend_receber?: number;
    trend_pagar?: number;
    trend_saldo?: number;
}

interface FinancialSummaryProps {
    data: SummaryData;
}

// Componente de Resumo
const FinancialSummary: React.FC<FinancialSummaryProps> = ({ data }) => {
    if (!data) return null;

    const cards = [
        {
            title: "Total em Aberto",
            value: data.total_aberto_periodo || 0,
            type: "warning"
        },
        {
            title: "Total Atrasado",
            value: data.total_atrasado || 0,
            type: "error"
        },
        {
            title: "Total Pago",
            value: data.total_pago_periodo || 0,
            type: "success"
        }
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {cards.map((card) => (
                <div key={card.title} className="bg-white rounded-lg shadow p-4">
                    <h3 className="text-sm font-medium text-gray-500">{card.title}</h3>
                    <p className="mt-2 text-3xl font-bold">
                        {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                        }).format(card.value)}
                    </p>
                </div>
            ))}
        </div>
    );
};



interface BillsTableProps {
    data: Bill[];
    onUpdateStatus: (billId: number, newStatus: string) => void;
    onDelete?: (billId: number) => void;
    onBatchDelete?: (billIds: number[]) => void;
    contextType?: 'pagar' | 'receber';
}

// Tabela de Títulos
type SortDirection = 'asc' | 'desc' | null;
type SortKey = 'vencimento' | 'valor' | 'nome' | 'status';

const BillsTable: React.FC<BillsTableProps> = ({ data, onUpdateStatus, onDelete, onBatchDelete, contextType = 'pagar' }) => {
    const [selectedBills, setSelectedBills] = useState<number[]>([]);
    const [lastClickedIndex, setLastClickedIndex] = useState<number | null>(null);
    const [sortKey, setSortKey] = useState<SortKey | null>(null);
    const [sortDirection, setSortDirection] = useState<SortDirection>(null);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'A': return 'bg-yellow-100 text-yellow-800';
            case 'P': return 'bg-green-100 text-green-800';
            case 'C': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getStatusText = (status: string) => {
        switch (status) {
            case 'A': return 'Em Aberto';
            case 'P': return 'Pago';
            case 'C': return 'Cancelado';
            default: return 'Desconhecido';
        }
    };

    const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.checked) {
            setSelectedBills(data.map(bill => bill.id));
        } else {
            setSelectedBills([]);
        }
        setLastClickedIndex(null);
    };

    const handleSelect = (id: number, index: number, shiftKey?: boolean, checked?: boolean) => {
        setSelectedBills(prev => {
            const selected = new Set(prev);
            if (shiftKey && lastClickedIndex !== null) {
                const start = Math.min(lastClickedIndex, index);
                const end = Math.max(lastClickedIndex, index);
                for (let i = start; i <= end; i++) {
                    const rowId = data[i]?.id;
                    if (rowId == null) continue;
                    if (checked) selected.add(rowId);
                    else selected.delete(rowId);
                }
            } else {
                if (checked) selected.add(id);
                else selected.delete(id);
            }
            return Array.from(selected);
        });
        setLastClickedIndex(index);
    };

    const handleBatchPayment = async () => {
        if (!selectedBills.length) return;

        try {
            // await api.post('/contas/baixa-em-lote', paymentData);
            setSelectedBills([]);
        } catch (error) {
            console.error('Erro ao realizar baixa em lote:', error);
        }
    };

    const isInteractive = (el: HTMLElement | null): boolean => {
        if (!el) return false;
        const tag = el.tagName.toLowerCase();
        if (["button", "a", "input", "select", "textarea", "label"].includes(tag)) return true;
        if (el.getAttribute('role') === 'button') return true;
        return !!el.closest('button, a, [role="button"], input, select, textarea, label');
    };

    const handleRowClick = (e: React.MouseEvent<HTMLTableRowElement>, id: number, index: number) => {
        const target = e.target as HTMLElement;
        if (isInteractive(target)) return;
        const nextChecked = !selectedBills.includes(id);
        handleSelect(id, index, e.shiftKey, nextChecked);
    };

    const getComparable = (bill: Bill, key: SortKey): string | number => {
        switch (key) {
            case 'valor':
                return bill.valor ?? 0;
            case 'vencimento':
                return new Date(bill.vencimento).getTime();
            case 'status': {
                const order: Record<Bill['status'], number> = { A: 1, P: 2, C: 3 };
                return order[bill.status] ?? 99;
            }
            case 'nome':
            default:
                return ((bill as any).cliente_nome || (bill as any).fornecedor_nome || bill.cliente?.nome || bill.fornecedor?.nome || '').toLowerCase();
        }
    };

    const sortedData = React.useMemo(() => {
        if (!sortKey || !sortDirection) return data;
        const arr = [...data];
        arr.sort((a, b) => {
            const av = getComparable(a, sortKey);
            const bv = getComparable(b, sortKey);
            if (typeof av === 'number' && typeof bv === 'number') {
                return sortDirection === 'asc' ? av - bv : bv - av;
            }
            const as = String(av);
            const bs = String(bv);
            return sortDirection === 'asc' ? as.localeCompare(bs) : bs.localeCompare(as);
        });
        return arr;
    }, [data, sortKey, sortDirection]);

    const toggleSort = (key: SortKey) => {
        if (sortKey !== key) {
            setSortKey(key);
            setSortDirection('asc');
        } else {
            setSortDirection(prev => (prev === 'asc' ? 'desc' : prev === 'desc' ? null : 'asc'));
            if (sortDirection === null) setSortKey(key); // ensure key set when enabling again
        }
    };

    const sortIndicator = (key: SortKey) => {
        if (sortKey !== key || !sortDirection) return null;
        return <span className="ml-1 text-xs">{sortDirection === 'asc' ? '▲' : '▼'}</span>;
    };

    return (
        <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 border-b flex justify-between items-center">
                <h2 className="text-lg font-medium">Títulos</h2>
                {selectedBills.length > 0 && (
                    <div className="flex gap-2">
                        <button
                            onClick={handleBatchPayment}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                            Baixar Selecionados
                        </button>
                        {onBatchDelete && (
                            <button
                                onClick={() => onBatchDelete(selectedBills)}
                                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                            >
                                Excluir Selecionados
                            </button>
                        )}
                    </div>
                )}
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-3 text-left">
                                <input
                                    type="checkbox"
                                    onChange={handleSelectAll}
                                    checked={selectedBills.length === data.length}
                                />
                            </th>
                            <th
                                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer select-none"
                                onClick={() => toggleSort('vencimento')}
                                title="Ordenar por vencimento"
                            >
                                <span className="inline-flex items-center">Vencimento {sortIndicator('vencimento')}</span>
                            </th>
                            <th
                                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer select-none"
                                onClick={() => toggleSort('valor')}
                                title="Ordenar por valor"
                            >
                                <span className="inline-flex items-center">Valor {sortIndicator('valor')}</span>
                            </th>
                            <th
                                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer select-none"
                                onClick={() => toggleSort('nome')}
                                title="Ordenar por cliente/fornecedor"
                            >
                                <span className="inline-flex items-center">{contextType === 'receber' ? 'Cliente' : 'Cliente/Fornecedor'} {sortIndicator('nome')}</span>
                            </th>
                            <th
                                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer select-none"
                                onClick={() => toggleSort('status')}
                                title="Ordenar por status"
                            >
                                <span className="inline-flex items-center">Status {sortIndicator('status')}</span>
                            </th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Ações
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {sortedData.map((bill, idx) => (
                            <tr key={bill.id} onClick={(e) => handleRowClick(e, bill.id, idx)}>
                                <td className="px-4 py-3">
                                    <input
                                        type="checkbox"
                                        checked={selectedBills.includes(bill.id)}
                                        onClick={(e) => {
                                            const nextChecked = !selectedBills.includes(bill.id);
                                            handleSelect(bill.id, idx, (e as React.MouseEvent<HTMLInputElement>).shiftKey, nextChecked);
                                        }}
                                        onChange={(e) => {
                                            // Fallback for keyboard interaction (no shift). Toggle single item.
                                            handleSelect(bill.id, idx, false, (e.target as HTMLInputElement).checked);
                                        }}
                                    />
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap">
                                    {new Date(bill.vencimento).toLocaleDateString()}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap">
                                    {new Intl.NumberFormat('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL'
                                    }).format(bill.valor)}
                                </td>
                                <td className="px-4 py-3">
                                    {(bill as any).cliente_nome || (bill as any).fornecedor_nome || bill.cliente?.nome || bill.fornecedor?.nome}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(bill.status)}`}>
                                        {getStatusText(bill.status)}
                                    </span>
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                                    {bill.status === 'A' && (
                                        <button
                                            onClick={() => onUpdateStatus(bill.id, 'P')}
                                            className="text-blue-600 hover:text-blue-900 mr-2"
                                        >
                                            Baixar
                                        </button>
                                    )}
                                    {bill.status === 'P' && (
                                        <button
                                            onClick={() => onUpdateStatus(bill.id, 'A')}
                                            className="text-yellow-600 hover:text-yellow-900"
                                        >
                                            Estornar
                                        </button>
                                    )}
                                    {onDelete && (
                                        <button
                                            onClick={() => onDelete(bill.id)}
                                            className="text-red-600 hover:text-red-900 ml-2"
                                        >
                                            Excluir
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

interface PaymentFormData {
    data_pagamento: string;
    forma_pagamento: string;
    valor_pago: number;
}

interface PaymentFormProps {
    bill: Bill;
    onSubmit: (data: PaymentFormData & { status: string }) => void;
    onCancel: () => void;
}

// Formulário de Baixa
const PaymentForm: React.FC<PaymentFormProps> = ({ bill, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState<PaymentFormData>({
        data_pagamento: new Date().toISOString().split('T')[0],
        forma_pagamento: '',
        valor_pago: bill?.valor || 0
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
        setFormData({
            ...formData,
            [e.target.name]: value
        });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({ ...formData, status: 'P' });
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h3 className="text-lg font-medium mb-4">Realizar Baixa</h3>
                <form onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Data do Pagamento
                            </label>
                            <input
                                type="date"
                                name="data_pagamento"
                                value={formData.data_pagamento}
                                onChange={handleChange}
                                required
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Forma de Pagamento
                            </label>
                            <select
                                name="forma_pagamento"
                                value={formData.forma_pagamento}
                                onChange={handleChange}
                                required
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            >
                                <option value="">Selecione...</option>
                                <option value="DINHEIRO">Dinheiro</option>
                                <option value="PIX">PIX</option>
                                <option value="CARTAO">Cartão</option>
                                <option value="BOLETO">Boleto</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Valor Pago
                            </label>
                            <input
                                type="number"
                                name="valor_pago"
                                value={formData.valor_pago}
                                onChange={handleChange}
                                required
                                step="0.01"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                        </div>
                    </div>
                    <div className="mt-6 flex justify-end space-x-3">
                        <button
                            type="button"
                            onClick={onCancel}
                            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                            Confirmar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

interface BillsManagementProps {
    type?: 'pagar' | 'receber';
}



// Componente Principal
const BillsManagement: React.FC<BillsManagementProps> = ({ type = 'pagar' }) => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<DashboardResponse2>({
        resumo: {
            total_atrasado: 0,
            total_pago_periodo: 0,
            total_cancelado_periodo: 0,
            total_aberto_periodo: 0,
            quantidade_titulos: 0,
            quantidade_atrasados_periodo: 0
        },
        titulos_atrasados: [],
        titulos_pagos_periodo: [],
        titulos_abertos_periodo: []
    });
    const [selectedBill, setSelectedBill] = useState<Bill | null>(null);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const result = await financialService.getDashboard();
            setData(result);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar os dados');
            console.error('Erro:', err);
        } finally {
            setLoading(false);
        }
    };

    const handlePaymentSubmit = async () => {
        if (!selectedBill) return;
    
        try {
            setLoading(true);
            await financialService.updateStatus();
            setSelectedBill(null);
            
            // Use os filtros atuais ao recarregar os dados
            await fetchData();
            
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao atualizar o título');
            console.error('Erro:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (billId: number) => {
        try {
            if (!window.confirm('Tem certeza que deseja excluir este título? Esta ação não pode ser desfeita.')) {
                return;
            }
            setLoading(true);
            if (type === 'pagar') {
                await contasPagarService.excluir(billId);
            } else {
                await contasReceberService.excluir(billId);
            }
            await fetchData();
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao excluir o título');
            console.error('Erro:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleBatchDelete = async (billIds: number[]) => {
        if (!billIds.length) return;
        const confirm = window.confirm(`Excluir ${billIds.length} título(s) selecionado(s)? Essa ação não pode ser desfeita.`);
        if (!confirm) return;
        try {
            setLoading(true);
            if (type === 'pagar') {
                await Promise.all(billIds.map(id => contasPagarService.excluir(id)));
            } else {
                await Promise.all(billIds.map(id => contasReceberService.excluir(id)));
            }
            await fetchData();
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao excluir os títulos selecionados');
            console.error('Erro:', err);
        } finally {
            setLoading(false);
        }
    };

    // Baixa em lote por fornecedor (somente pagar)
    const [batchSupplier, setBatchSupplier] = useState<string>('');
    const handleBatchPayBySupplier = async () => {
        try {
            if (type !== 'pagar' || !batchSupplier) return;
            const abertos = data.titulos_abertos_periodo.filter(b => b.fornecedor?.nome === batchSupplier);
            if (abertos.length === 0) return;
            setLoading(true);
            // Fazer atualização em paralelo
            await Promise.all(abertos.map(b => contasPagarService.atualizarStatus(b.id, 'P')));
            await fetchData();
        } catch (err) {
            console.error('Erro na baixa em lote por fornecedor:', err);
        } finally {
            setLoading(false);
        }
    };

    // Baixa em lote por cliente (receber)
    const [batchCliente, setBatchCliente] = useState<string>('');
    const handleBatchPayByCliente = async () => {
        try {
            if (type !== 'receber' || !batchCliente) return;
            const abertos = data.titulos_abertos_periodo.filter(b => ((b as any).cliente_nome || b.cliente?.nome) === batchCliente);
            if (abertos.length === 0) return;
            setLoading(true);
            await Promise.all(abertos.map(b => contasReceberService.atualizarStatus(b.id, 'P')));
            await fetchData();
        } catch (err) {
            console.error('Erro na baixa em lote por cliente:', err);
        } finally {
            setLoading(false);
        }
    };

    /* const handleBatchPayment = async (selectedIds: number[], paymentData: PaymentData) => {
        try {
            setLoading(true);
            await financialService.batchPayment(type, {
                ...paymentData,
                titulos: selectedIds
            });
            fetchData();
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao realizar baixa em lote');
            console.error('Erro:', err);
        } finally {
            setLoading(false);
        }
    };
 */


    const handleFilterChange = () => {
        fetchData();
    };

    const handleUpdateStatus = (billId: number) => {
        const bill = [...data.titulos_atrasados, ...data.titulos_abertos_periodo, ...data.titulos_pagos_periodo]
            .find(b => b.id === billId);

        if (bill) {
            setSelectedBill(bill);
        }
    };

    return (
        <div className="container mx-auto p-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold mb-2">
                    Contas a {type === 'pagar' ? 'Pagar' : 'Receber'}
                </h1>
                <p className="text-gray-600">
                    Gerencie suas {type === 'pagar' ? 'despesas' : 'receitas'} de forma eficiente
                </p>
            </div>

            {error && (
                <Alert variant="destructive" className="mb-6">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            <Filters onFilterChange={handleFilterChange} />

            <FinancialSummary data={data.resumo} />

            {data.titulos_atrasados.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-xl font-semibold mb-4 text-red-600">
                        Títulos Atrasados
                    </h2>
                    <BillsTable
                        data={data.titulos_atrasados}
                        onUpdateStatus={handleUpdateStatus}
                        onDelete={handleDelete}
                        onBatchDelete={handleBatchDelete}
                        contextType={type}
                    />
                </div>
            )}

            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">
                    Títulos em Aberto
                </h2>
                {type === 'pagar' && (
                    <div className="flex items-center gap-2 mb-3">
                        <select
                            value={batchSupplier}
                            onChange={(e) => setBatchSupplier(e.target.value)}
                            className="border rounded px-2 py-1"
                        >
                            <option value="">Selecionar fornecedor...</option>
                            {Array.from(new Set(data.titulos_abertos_periodo
                                .map(b => b.fornecedor?.nome)
                                .filter(Boolean)))
                                .map((nome) => (
                                    <option key={nome as string} value={nome as string}>{nome as string}</option>
                                ))}
                        </select>
                        <button
                            onClick={handleBatchPayBySupplier}
                            disabled={!batchSupplier}
                            className="px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-50"
                        >
                            Baixar todos desse fornecedor
                        </button>
                    </div>
                )}
                {type === 'receber' && (
                    <div className="flex items-center gap-2 mb-3">
                        <select
                            value={batchCliente}
                            onChange={(e) => setBatchCliente(e.target.value)}
                            className="border rounded px-2 py-1"
                        >
                            <option value="">Selecionar cliente...</option>
                            {Array.from(new Set(data.titulos_abertos_periodo
                                .map(b => (b as any).cliente_nome || b.cliente?.nome)
                                .filter(Boolean)))
                                .map((nome) => (
                                    <option key={nome as string} value={nome as string}>{nome as string}</option>
                                ))}
                        </select>
                        <button
                            onClick={handleBatchPayByCliente}
                            disabled={!batchCliente}
                            className="px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-50"
                        >
                            Baixar todos desse cliente
                        </button>
                    </div>
                )}
                <BillsTable
                    data={data.titulos_abertos_periodo}
                    onUpdateStatus={handleUpdateStatus}
                    onDelete={handleDelete}
                    onBatchDelete={handleBatchDelete}
                    contextType={type}
                />
            </div>

            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">
                    Títulos Pagos no Período
                </h2>
                <BillsTable
                    data={data.titulos_pagos_periodo}
                    onUpdateStatus={handleUpdateStatus}
                    onDelete={handleDelete}
                    onBatchDelete={handleBatchDelete}
                    contextType={type}
                />
            </div>

            {selectedBill && (
                <PaymentForm
                    bill={selectedBill}
                    onSubmit={handlePaymentSubmit}
                    onCancel={() => setSelectedBill(null)}
                />
            )}

            {loading && (
                <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                    <div className="bg-white rounded-lg p-4">
                        Carregando...
                    </div>
                </div>
            )}
        </div>
    );
};

export default BillsManagement;