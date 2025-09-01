import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, ChevronDown, ChevronRight, CalendarIcon } from 'lucide-react';
import { financeiroDashboard } from '@/services/api';
import { format } from "date-fns";
import { ptBR } from 'date-fns/locale';
import { DateRange } from "react-day-picker";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";

// Types
interface BasePessoa {
    id: number;
    nome: string;
    cpf_cnpj: string;
    tipo_pessoa?: 'F' | 'J';
}

interface Titulo {
    id: number;
    historico: string;
    valor: string;
    vencimento: string;
    status: 'A' | 'P' | 'C';
    data_pagamento: string | null;
}

interface TituloReceber extends Titulo {
    cliente: BasePessoa;
}

interface TituloPagar extends Titulo {
    fornecedor: BasePessoa;
}

interface ResumoCliente {
    cliente: BasePessoa;
    totalReceber: number;
    totalPagar: number;
    saldo: number;
    quantidadeTitulos: number;
    titulosReceber: TituloReceber[];
    titulosPagar: TituloPagar[];
    expandido: boolean;
}

const ResumoPorCliente = () => {
    const [date, setDate] = useState<DateRange | undefined>({
        from: new Date(),
        to: new Date(),
    });
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);
    const [resumoClientes, setResumoClientes] = useState<ResumoCliente[]>([]);

    const toggleExpansao = (clienteId: number) => {
        setResumoClientes(prev => prev.map(cliente =>
            cliente.cliente.id === clienteId
                ? { ...cliente, expandido: !cliente.expandido }
                : cliente
        ));
    };

    const formatarMoeda = (valor: number | string): string => {
        const numero = typeof valor === 'string' ? parseFloat(valor) : valor;
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(numero);
    };

    const getStatusColor = (status: 'A' | 'P' | 'C'): string => {
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

    const getStatusLabel = (status: 'A' | 'P' | 'C'): string => {
        switch (status) {
            case 'A':
                return 'Aberto';
            case 'P':
                return 'Pago';
            case 'C':
                return 'Cancelado';
            default:
                return 'Desconhecido';
        }
    };

    const carregarResumo = async () => {
        if (!date?.from || !date?.to) return;

        try {
            setLoading(true);
            const response = await financeiroDashboard.resumoGeral({
                dataInicial: date.from.toISOString(),
                dataFinal: date.to.toISOString(),
                status: 'all',
                searchTerm: searchTerm.trim()
            });

            const resumoPorCliente = new Map<number, ResumoCliente>();

            // Função auxiliar para criar um resumo vazio
            const criarResumoVazio = (dadosPessoa: BasePessoa): ResumoCliente => ({
                cliente: dadosPessoa,
                totalReceber: 0,
                totalPagar: 0,
                saldo: 0,
                quantidadeTitulos: 0,
                titulosReceber: [],
                titulosPagar: [],
                expandido: false
            });

            // Processa contas a receber
            response.contasReceber.titulos_abertos_periodo.forEach(titulo => {
                if (!titulo.cliente) return;

                const clienteId = titulo.cliente.id;
                const clienteBase: BasePessoa = {
                    id: titulo.cliente.id,
                    nome: titulo.cliente.nome,
                    cpf_cnpj: titulo.cliente.cpf_cnpj || '',
                    tipo_pessoa: titulo.cliente.tipo_pessoa
                };

                const resumoAtual = resumoPorCliente.get(clienteId) ||
                    criarResumoVazio(clienteBase);

                resumoAtual.totalReceber += Number(titulo.valor);
                resumoAtual.quantidadeTitulos += 1;
                resumoAtual.saldo = resumoAtual.totalReceber - resumoAtual.totalPagar;
                resumoAtual.titulosReceber.push(titulo);

                resumoPorCliente.set(clienteId, resumoAtual);
            });

            // Processa contas a pagar
            response.contasPagar.titulos_abertos_periodo.forEach(titulo => {
                if (!titulo.fornecedor) return;

                const fornecedorId = titulo.fornecedor.id;
                const fornecedorBase: BasePessoa = {
                    id: fornecedorId,
                    nome: titulo.fornecedor.nome,
                    cpf_cnpj: titulo.fornecedor.cpf_cnpj || '',
                    tipo_pessoa: titulo.fornecedor.tipo_pessoa
                };

                const resumoAtual = resumoPorCliente.get(fornecedorId) ||
                    criarResumoVazio(fornecedorBase);

                resumoAtual.totalPagar += Number(titulo.valor);
                resumoAtual.quantidadeTitulos += 1;
                resumoAtual.saldo = resumoAtual.totalReceber - resumoAtual.totalPagar;
                resumoAtual.titulosPagar.push(titulo);

                resumoPorCliente.set(fornecedorId, resumoAtual);
            });

            const resumoOrdenado = Array.from(resumoPorCliente.values())
                .sort((a, b) => Math.abs(b.saldo) - Math.abs(a.saldo));

            setResumoClientes(resumoOrdenado);
        } catch (error) {
            console.error('Erro ao carregar resumo:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        carregarResumo();
    }, [date]);

    return (
        <div className="p-6 space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Resumo Financeiro por Cliente</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex gap-4 mb-6">
                        <div className="flex-1 flex gap-4">
                            <Popover>
                                <PopoverTrigger asChild>
                                    <Button
                                        variant="outline"
                                        className="justify-start text-left font-normal w-[280px]"
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

                            <div className="relative flex-1">
                                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Buscar cliente..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-8"
                                />
                            </div>
                        </div>

                        <Button onClick={carregarResumo}>
                            Atualizar
                        </Button>
                    </div>

                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-10"></TableHead>
                                    <TableHead>Cliente/Fornecedor</TableHead>
                                    <TableHead>CPF/CNPJ</TableHead>
                                    <TableHead className="text-right">Total a Receber</TableHead>
                                    <TableHead className="text-right">Total a Pagar</TableHead>
                                    <TableHead className="text-right">Saldo</TableHead>
                                    <TableHead className="text-center">Títulos</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={7} className="h-24 text-center">
                                            <div className="flex items-center justify-center">
                                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                                                <span className="ml-2">Carregando...</span>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ) : resumoClientes.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={7} className="h-24 text-center">
                                            Nenhum resultado encontrado
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    resumoClientes.map((resumo) => (
                                        <React.Fragment key={resumo.cliente.id}>
                                            <TableRow
                                                className="cursor-pointer hover:bg-muted/50"
                                                onClick={() => toggleExpansao(resumo.cliente.id)}
                                            >
                                                <TableCell>
                                                    {resumo.expandido ?
                                                        <ChevronDown className="h-4 w-4" /> :
                                                        <ChevronRight className="h-4 w-4" />
                                                    }
                                                </TableCell>
                                                <TableCell className="font-medium">
                                                    {resumo.cliente.nome}
                                                </TableCell>
                                                <TableCell>{resumo.cliente.cpf_cnpj}</TableCell>
                                                <TableCell className="text-right font-medium text-green-600">
                                                    {formatarMoeda(resumo.totalReceber)}
                                                </TableCell>
                                                <TableCell className="text-right font-medium text-red-600">
                                                    {formatarMoeda(resumo.totalPagar)}
                                                </TableCell>
                                                <TableCell className={`text-right font-medium ${resumo.saldo >= 0 ? 'text-green-600' : 'text-red-600'
                                                    }`}>
                                                    {formatarMoeda(resumo.saldo)}
                                                </TableCell>
                                                <TableCell className="text-center">
                                                    {resumo.quantidadeTitulos}
                                                </TableCell>
                                            </TableRow>

                                            {resumo.expandido && (
                                                <TableRow>
                                                    <TableCell colSpan={7} className="p-0">
                                                        <div className="bg-muted/50 p-4 space-y-4">
                                                            {resumo.titulosReceber.length > 0 && (
                                                                <div>
                                                                    <h4 className="font-semibold mb-2">Títulos a Receber</h4>
                                                                    <Table>
                                                                        <TableHeader>
                                                                            <TableRow>
                                                                                <TableHead>Histórico</TableHead>
                                                                                <TableHead className="text-right">Valor</TableHead>
                                                                                <TableHead className="text-center">Vencimento</TableHead>
                                                                                <TableHead className="text-center">Status</TableHead>
                                                                            </TableRow>
                                                                        </TableHeader>
                                                                        <TableBody>
                                                                            {resumo.titulosReceber.map(titulo => (
                                                                                <TableRow key={titulo.id}>
                                                                                    <TableCell>{titulo.historico}</TableCell>
                                                                                    <TableCell className="text-right">
                                                                                        {formatarMoeda(titulo.valor)}
                                                                                    </TableCell>
                                                                                    <TableCell className="text-center">
                                                                                        {format(new Date(titulo.vencimento), 'dd/MM/yyyy')}
                                                                                    </TableCell>
                                                                                    <TableCell className="text-center">
                                                                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(titulo.status)}`}>
                                                                                            {getStatusLabel(titulo.status)}
                                                                                        </span>
                                                                                    </TableCell>
                                                                                </TableRow>
                                                                            ))}
                                                                        </TableBody>
                                                                    </Table>
                                                                </div>
                                                            )}

                                                            {resumo.titulosPagar.length > 0 && (
                                                                <div>
                                                                    <h4 className="font-semibold mb-2">Títulos a Pagar</h4>
                                                                    <Table>
                                                                        <TableHeader>
                                                                            <TableRow>
                                                                                <TableHead>Histórico</TableHead>
                                                                                <TableHead className="text-right">Valor</TableHead>
                                                                                <TableHead className="text-center">Vencimento</TableHead>
                                                                                <TableHead className="text-center">Status</TableHead>
                                                                            </TableRow>
                                                                        </TableHeader>
                                                                        <TableBody>
                                                                            {resumo.titulosPagar.map(titulo => (
                                                                                <TableRow key={titulo.id}>
                                                                                    <TableCell>{titulo.historico}</TableCell>
                                                                                    <TableCell className="text-right">
                                                                                        {formatarMoeda(titulo.valor)}
                                                                                    </TableCell>
                                                                                    <TableCell className="text-center">
                                                                                        {format(new Date(titulo.vencimento), 'dd/MM/yyyy')}
                                                                                    </TableCell>
                                                                                    <TableCell className="text-center">
                                                                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(titulo.status)}`}>
                                                                                            {getStatusLabel(titulo.status)}
                                                                                        </span>
                                                                                    </TableCell>
                                                                                </TableRow>
                                                                            ))}
                                                                        </TableBody>
                                                                    </Table>
                                                                </div>
                                                            )}

                                                            {resumo.titulosReceber.length === 0 && resumo.titulosPagar.length === 0 && (
                                                                <div className="text-center py-4 text-muted-foreground">
                                                                    Nenhum título encontrado para o período selecionado
                                                                </div>
                                                            )}
                                                        </div>
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </React.Fragment>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    {/* Rodapé com legendas de status */}
                    <div className="mt-4 flex justify-center gap-4">
                        <div className="flex items-center">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor('A')}`}>
                                {getStatusLabel('A')}
                            </span>
                        </div>
                        <div className="flex items-center">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor('P')}`}>
                                {getStatusLabel('P')}
                            </span>
                        </div>
                        <div className="flex items-center">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor('C')}`}>
                                {getStatusLabel('C')}
                            </span>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default ResumoPorCliente;