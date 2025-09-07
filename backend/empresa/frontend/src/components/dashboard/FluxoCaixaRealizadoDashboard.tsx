import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    ArrowUpCircle,
    ArrowDownCircle,
    TrendingUp,
    TrendingDown,
    Calendar,
    Download,
    Search,
    AlertTriangle,
    CheckCircle,
    Clock,
    DollarSign
} from "lucide-react";
import { 
  fluxoCaixaService, 
  formatCurrency, 
  formatDate,
  getStatusVencimentoColor,
  getStatusVencimentoLabel
} from '@/services/fluxo-caixa-service';
import type {
  MovimentacoesRealizadasResponse,
  MovimentacoesVencimentoAbertoResponse,
  ComparativoRealizadoVsPrevistoResponse,
  FiltrosPeriodo
} from '@/types/fluxo-caixa';

// Componente para card de métrica
interface MetricCardProps {
    title: string;
    value: number;
    icon: React.ReactNode;
    change?: number;
    color: string;
    trend?: 'up' | 'down' | 'neutral';
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  icon, 
  change, 
  color, 
  trend 
}) => (
    <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center justify-between">
                <div className="flex items-center">
                    {icon}
                    <span className="ml-2">{title}</span>
                </div>
                {trend && (
                    <div className="text-xs">
                        {trend === 'up' && <TrendingUp className="h-4 w-4 text-green-500" />}
                        {trend === 'down' && <TrendingDown className="h-4 w-4 text-red-500" />}
                    </div>
                )}
            </CardTitle>
        </CardHeader>
        <CardContent>
            <div className={`text-2xl font-bold ${color}`}>
                {formatCurrency(value)}
            </div>
            {change !== undefined && (
                <div className="text-sm text-muted-foreground mt-1">
                    {change >= 0 ? '+' : ''}{change.toFixed(1)}% vs período anterior
                </div>
            )}
        </CardContent>
    </Card>
);

// Componente para tabela de movimentações
interface MovimentacoesTableProps {
  movimentacoes: Array<{
    id: string;
    tipo: string;
    data_pagamento?: string;
    data_vencimento?: string;
    valor: number;
    contraparte: string;
    status_vencimento?: string;
    dias_vencimento?: number;
  }>;
  tipo: 'realizadas' | 'pendentes';
}

const MovimentacoesTable: React.FC<MovimentacoesTableProps> = ({ movimentacoes, tipo }) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b">
          <th className="text-left p-2">Data</th>
          <th className="text-left p-2">Tipo</th>
          <th className="text-left p-2">Contraparte</th>
          <th className="text-left p-2">Valor</th>
          <th className="text-left p-2">Status</th>
          {tipo === 'pendentes' && <th className="text-left p-2">Vencimento</th>}
        </tr>
      </thead>
      <tbody>
        {movimentacoes.slice(0, 10).map((mov, index) => (
          <tr key={mov.id || index} className="border-b hover:bg-muted/50">
            <td className="p-2">
              {formatDate(tipo === 'realizadas' ? (mov.data_pagamento || '') : (mov.data_vencimento || ''))}
            </td>
            <td className="p-2">
              <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${
                mov.tipo.includes('entrada') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {mov.tipo.includes('entrada') ? (
                  <ArrowUpCircle className="h-3 w-3 mr-1" />
                ) : (
                  <ArrowDownCircle className="h-3 w-3 mr-1" />
                )}
                {mov.tipo.includes('entrada') ? 'Entrada' : 'Saída'}
              </span>
            </td>
            <td className="p-2 truncate max-w-32" title={mov.contraparte}>
              {mov.contraparte}
            </td>
            <td className="p-2 font-semibold">
              {formatCurrency(mov.valor)}
            </td>
            <td className="p-2">
              {tipo === 'pendentes' && mov.status_vencimento ? (
                <span className={`text-xs ${getStatusVencimentoColor(mov.status_vencimento)}`}>
                  {getStatusVencimentoLabel(mov.status_vencimento)}
                </span>
              ) : (
                <span className="text-green-600 text-xs">Realizado</span>
              )}
            </td>
            {tipo === 'pendentes' && (
              <td className="p-2 text-xs">
                {mov.dias_vencimento !== undefined && (
                  <span className={mov.dias_vencimento < 0 ? 'text-red-600' : 'text-gray-600'}>
                    {mov.dias_vencimento < 0 
                      ? `${Math.abs(mov.dias_vencimento)} dias atraso`
                      : `${mov.dias_vencimento} dias`
                    }
                  </span>
                )}
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// Componente principal do dashboard
const FluxoCaixaRealizadoDashboard: React.FC = () => {
    // Estados
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    // Dados
    const [movimentacoesRealizadas, setMovimentacoesRealizadas] = useState<MovimentacoesRealizadasResponse | null>(null);
    const [movimentacoesPendentes, setMovimentacoesPendentes] = useState<MovimentacoesVencimentoAbertoResponse | null>(null);
    const [comparativo, setComparativo] = useState<ComparativoRealizadoVsPrevistoResponse | null>(null);

    // Filtros
    const [filtros, setFiltros] = useState<FiltrosPeriodo>({
        data_inicio: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 dias atrás
        data_fim: new Date().toISOString().split('T')[0] // hoje
    });

    // Carregar dados
    const carregarDados = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            console.log('🔄 Tentando carregar dados da API...');

            try {
                const [realizadas, , pendentes, comp] = await Promise.all([
                    fluxoCaixaService.getMovimentacoesRealizadas(filtros),
                    fluxoCaixaService.getResumoMensal(filtros),
                    fluxoCaixaService.getMovimentacoesVencimentoAberto(filtros),
                    fluxoCaixaService.getComparativoRealizadoVsPrevisto(filtros)
                ]);

                setMovimentacoesRealizadas(realizadas);
                setMovimentacoesPendentes(pendentes);
                setComparativo(comp);
                
                console.log('✅ Dados carregados da API com sucesso!');

            } catch {
                console.log('⚠️ API não disponível, usando dados mockados...');
                
                // Dados mockados como fallback
                const mockRealizadas: MovimentacoesRealizadasResponse = {
                    periodo: {
                        data_inicio: filtros.data_inicio,
                        data_fim: filtros.data_fim
                    },
                    resumo: {
                        total_entradas: 50000,
                        total_saidas: 33000,
                        saldo_liquido: 17000,
                        total_movimentacoes: 3
                    },
                    movimentacoes: [
                        {
                            id: '1',
                            tipo: 'entrada',
                            data_pagamento: '2025-09-01',
                            valor: 50000,
                            contraparte: 'Cliente ABC',
                            historico: 'Receita de Vendas',
                            forma_pagamento: 'Transferência',
                            origem: 'contas_receber'
                        },
                        {
                            id: '2',
                            tipo: 'saida',
                            data_pagamento: '2025-09-03',
                            valor: 25000,
                            contraparte: 'Fornecedor XYZ',
                            historico: 'Pagamento Fornecedor',
                            forma_pagamento: 'PIX',
                            origem: 'contas_pagar'
                        },
                        {
                            id: '3',
                            tipo: 'saida',
                            data_pagamento: '2025-09-05',
                            valor: 8000,
                            contraparte: 'Imobiliária',
                            historico: 'Aluguel Escritório',
                            forma_pagamento: 'Boleto',
                            origem: 'contas_pagar'
                        }
                    ]
                };

                const mockPendentes: MovimentacoesVencimentoAbertoResponse = {
                    periodo: {
                        data_inicio: filtros.data_inicio,
                        data_fim: filtros.data_fim
                    },
                    resumo: {
                        total_entradas_pendentes: 15000,
                        total_saidas_pendentes: 1200,
                        saldo_liquido_pendente: 13800,
                        total_movimentacoes: 2
                    },
                    estatisticas_vencimento: {
                        no_prazo: {
                            entradas: 15000,
                            saidas: 1200,
                            qtd_entradas: 1,
                            qtd_saidas: 1
                        },
                        vence_em_breve: {
                            entradas: 0,
                            saidas: 0,
                            qtd_entradas: 0,
                            qtd_saidas: 0
                        },
                        vencido: {
                            entradas: 0,
                            saidas: 0,
                            qtd_entradas: 0,
                            qtd_saidas: 0
                        }
                    },
                    movimentacoes_abertas: [
                        {
                            id: '4',
                            tipo: 'saida_pendente',
                            data_emissao: '2025-08-20',
                            data_vencimento: '2025-09-10',
                            valor: 1200,
                            contraparte: 'Companhia Elétrica',
                            historico: 'Conta de Luz',
                            forma_pagamento: 'Boleto',
                            origem: 'contas_pagar',
                            dias_vencimento: 5,
                            status_vencimento: 'no_prazo'
                        },
                        {
                            id: '5',
                            tipo: 'entrada_pendente',
                            data_emissao: '2025-08-25',
                            data_vencimento: '2025-09-12',
                            valor: 15000,
                            contraparte: 'Cliente A',
                            historico: 'Recebimento Cliente A',
                            forma_pagamento: 'Transferência',
                            origem: 'contas_receber',
                            dias_vencimento: 7,
                            status_vencimento: 'no_prazo'
                        }
                    ]
                };

                const mockComparativo: ComparativoRealizadoVsPrevistoResponse = {
                    periodo: {
                        data_inicio: filtros.data_inicio,
                        data_fim: filtros.data_fim
                    },
                    realizado: {
                        entradas: 130000,
                        saidas: 78000,
                        saldo_liquido: 52000,
                        qtd_contas_recebidas: 5,
                        qtd_contas_pagas: 8
                    },
                    previsto: {
                        entradas: 120000,
                        saidas: 85000,
                        saldo_liquido: 35000,
                        qtd_contas_a_receber: 3,
                        qtd_contas_a_pagar: 5
                    },
                    analise: {
                        diferenca_entradas: 10000,
                        diferenca_saidas: -7000,
                        diferenca_saldo: 17000,
                        percentual_realizacao_entradas: 108.33,
                        percentual_realizacao_saidas: 91.76
                    }
                };

                setMovimentacoesRealizadas(mockRealizadas);
                setMovimentacoesPendentes(mockPendentes);
                setComparativo(mockComparativo);
            }

        } catch (err) {
            console.error('❌ Erro crítico ao carregar dados:', err);
            setError('Falha ao carregar dados do fluxo de caixa');
        } finally {
            setLoading(false);
        }
    }, [filtros]);

    // Carregar dados quando os filtros mudarem
    useEffect(() => {
        carregarDados();
    }, [carregarDados]);

    // Loading state
    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="container mx-auto p-6">
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center text-red-600">
                            <AlertTriangle className="h-5 w-5 mr-2" />
                            {error}
                        </div>
                        <Button onClick={carregarDados} className="mt-4">
                            Tentar Novamente
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 space-y-6 bg-background min-h-screen">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Dashboard - Fluxo de Caixa Realizado</h1>
                <div className="flex items-center space-x-2">
                    <Calendar className="h-5 w-5 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                        {formatDate(filtros.data_inicio)} - {formatDate(filtros.data_fim)}
                    </span>
                </div>
            </div>

            {/* Filtros */}
            <Card>
                <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="text-sm font-medium mb-2 block">Data Início</label>
                            <Input
                                type="date"
                                value={filtros.data_inicio}
                                onChange={(e) => setFiltros(prev => ({ ...prev, data_inicio: e.target.value }))}
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-2 block">Data Fim</label>
                            <Input
                                type="date"
                                value={filtros.data_fim}
                                onChange={(e) => setFiltros(prev => ({ ...prev, data_fim: e.target.value }))}
                            />
                        </div>
                        <div className="flex items-end">
                            <Button onClick={carregarDados} className="w-full">
                                <Search className="h-4 w-4 mr-2" />
                                Buscar
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Métricas Principais */}
            {movimentacoesRealizadas && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <MetricCard
                        title="Entradas Realizadas"
                        value={movimentacoesRealizadas.resumo.total_entradas}
                        icon={<ArrowUpCircle className="h-5 w-5 text-green-500" />}
                        color="text-green-600"
                        trend="up"
                    />
                    <MetricCard
                        title="Saídas Realizadas"
                        value={movimentacoesRealizadas.resumo.total_saidas}
                        icon={<ArrowDownCircle className="h-5 w-5 text-red-500" />}
                        color="text-red-600"
                        trend="down"
                    />
                    <MetricCard
                        title="Saldo Realizado"
                        value={movimentacoesRealizadas.resumo.saldo_liquido}
                        icon={<DollarSign className="h-5 w-5 text-blue-500" />}
                        color={movimentacoesRealizadas.resumo.saldo_liquido >= 0 ? "text-green-600" : "text-red-600"}
                        trend={movimentacoesRealizadas.resumo.saldo_liquido >= 0 ? "up" : "down"}
                    />
                    <MetricCard
                        title="Total Movimentações"
                        value={movimentacoesRealizadas.resumo.total_movimentacoes}
                        icon={<CheckCircle className="h-5 w-5 text-blue-500" />}
                        color="text-blue-600"
                    />
                </div>
            )}

            {/* Cards de Comparativo e Pendências */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Comparativo Realizado vs Previsto */}
                {comparativo && (
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <TrendingUp className="h-5 w-5 mr-2" />
                                Realizado vs Previsto
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm text-muted-foreground">Entradas</p>
                                        <p className="font-semibold">{formatCurrency(comparativo.realizado.entradas)}</p>
                                        <p className="text-xs text-green-600">
                                            {comparativo.analise.percentual_realizacao_entradas.toFixed(1)}% do previsto
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground">Saídas</p>
                                        <p className="font-semibold">{formatCurrency(comparativo.realizado.saidas)}</p>
                                        <p className="text-xs text-red-600">
                                            {comparativo.analise.percentual_realizacao_saidas.toFixed(1)}% do previsto
                                        </p>
                                    </div>
                                </div>
                                <div className="pt-2 border-t">
                                    <p className="text-sm text-muted-foreground">Diferença no Saldo</p>
                                    <p className={`font-bold ${comparativo.analise.diferenca_saldo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatCurrency(comparativo.analise.diferenca_saldo)}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Resumo de Pendências */}
                {movimentacoesPendentes && (
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Clock className="h-5 w-5 mr-2" />
                                Movimentações Pendentes
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="grid grid-cols-3 gap-2 text-center">
                                    <div className="p-2 bg-green-50 rounded">
                                        <p className="text-xs text-green-700">No Prazo</p>
                                        <p className="font-semibold text-green-800">
                                            {movimentacoesPendentes.estatisticas_vencimento.no_prazo.qtd_entradas + 
                                             movimentacoesPendentes.estatisticas_vencimento.no_prazo.qtd_saidas}
                                        </p>
                                    </div>
                                    <div className="p-2 bg-yellow-50 rounded">
                                        <p className="text-xs text-yellow-700">Vence em Breve</p>
                                        <p className="font-semibold text-yellow-800">
                                            {movimentacoesPendentes.estatisticas_vencimento.vence_em_breve.qtd_entradas + 
                                             movimentacoesPendentes.estatisticas_vencimento.vence_em_breve.qtd_saidas}
                                        </p>
                                    </div>
                                    <div className="p-2 bg-red-50 rounded">
                                        <p className="text-xs text-red-700">Vencido</p>
                                        <p className="font-semibold text-red-800">
                                            {movimentacoesPendentes.estatisticas_vencimento.vencido.qtd_entradas + 
                                             movimentacoesPendentes.estatisticas_vencimento.vencido.qtd_saidas}
                                        </p>
                                    </div>
                                </div>
                                <div className="pt-2 border-t">
                                    <p className="text-sm text-muted-foreground">Saldo Pendente</p>
                                    <p className={`font-bold ${movimentacoesPendentes.resumo.saldo_liquido_pendente >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatCurrency(movimentacoesPendentes.resumo.saldo_liquido_pendente)}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>

            {/* Tabelas de Movimentações */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Movimentações Realizadas */}
                {movimentacoesRealizadas && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Últimas Movimentações Realizadas</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <MovimentacoesTable 
                                movimentacoes={movimentacoesRealizadas.movimentacoes} 
                                tipo="realizadas"
                            />
                        </CardContent>
                    </Card>
                )}

                {/* Movimentações Pendentes */}
                {movimentacoesPendentes && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Movimentações Pendentes</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <MovimentacoesTable 
                                movimentacoes={movimentacoesPendentes.movimentacoes_abertas} 
                                tipo="pendentes"
                            />
                        </CardContent>
                    </Card>
                )}
            </div>

            {/* Botão de Exportação */}
            <div className="flex justify-end">
                <Button variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Exportar Relatório
                </Button>
            </div>
        </div>
    );
};

export default FluxoCaixaRealizadoDashboard;
