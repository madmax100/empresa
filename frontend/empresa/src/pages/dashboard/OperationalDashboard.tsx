import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import {
  AlertCircle, Download, TrendingUp,
  CircleDollarSign, Printer, Package, FileText,
  ArrowUpCircle, ArrowDownCircle
} from "lucide-react";
import { Filtros } from '@/types/dashboardNovo';
import IndicadorCard from '@/components/common/IndicadorCard';



interface OperationalDashboardCompleteProps {
  data: {
    filtros: Filtros;
    resumo: any;
    totalizadores: any;
    movimentos: any[];
  } | null;
  loading?: boolean;
  onFiltrosChange: (filtros: Partial<Filtros>) => void;
  onRefresh: () => void;
  onExport: () => void;
  onMovimentoStatusChange?: (id: number) => Promise<void>;
  className?: string;
}

export const OperationalDashboardComplete: React.FC<OperationalDashboardCompleteProps> = ({
  data,
  loading = false,
  onRefresh,
  onExport,
  onMovimentoStatusChange,
  className = ''
}) => {
  const [selectedTab, setSelectedTab] = useState('visao-geral');

  // Debug: verificar dados recebidos
  console.log('📊 OperationalDashboard recebeu dados:', {
    hasData: !!data,
    movimentosCount: data?.movimentos?.length || 0,
    resumo: data?.resumo,
    movimentos: data?.movimentos?.slice(0, 3) // Primeiros 3 para debug
  });

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-12 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Não foi possível carregar os dados do dashboard operacional.
        </AlertDescription>
      </Alert>
    );
  }

  const { 
    resumo = {
      receitas_detalhadas: { locacao: 0 },
      saldo_final: 0,
      variacao_percentual: 0,
      saldo_projetado: 0,
      vendas_equipamentos: 0,
      alugueis_ativos: 0,
      servicos_total: 0,
      suprimentos_total: 0
    }, 
    totalizadores = {
      entradas_realizadas: { valor: 0, quantidade: 0 },
      entradas_previstas: { valor: 0, quantidade: 0 },
      saidas_realizadas: { valor: 0, quantidade: 0 },
      saidas_previstas: { valor: 0, quantidade: 0 }
    }, 
    movimentos = [] 
  } = data;

  // Preparar dados para gráficos
  const movimentosData = (movimentos || []).reduce((acc, movimento) => {
    const data = new Date(movimento.data).toLocaleDateString('pt-BR');
    const existingDay = acc.find(item => item.data === data);
    
    if (existingDay) {
      if (movimento.tipo === 'entrada') {
        existingDay.entradas += movimento.valor;
      } else {
        existingDay.saidas += movimento.valor;
      }
      existingDay.saldo = existingDay.entradas - existingDay.saidas;
    } else {
      acc.push({
        data,
        entradas: movimento.tipo === 'entrada' ? movimento.valor : 0,
        saidas: movimento.tipo === 'saida' ? movimento.valor : 0,
        saldo: movimento.tipo === 'entrada' ? movimento.valor : -movimento.valor
      });
    }
    return acc;
  }, []);

  // Dados para o gráfico de categorias
  const categoriasData = Object.entries(resumo.receitas_detalhadas || {}).map(([categoria, valor]) => ({
    categoria: categoria.charAt(0).toUpperCase() + categoria.slice(1),
    valor
  }));

  const CORES_CATEGORIAS = ['#10B981', '#3B82F6', '#F59E0B', '#EC4899', '#6366F1'];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header com filtros */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Dashboard Operacional</h1>
          <div className="flex gap-2">
            <Button variant="outline" onClick={onRefresh}>
              Atualizar
            </Button>
            <Button variant="outline" onClick={onExport}>
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>
      </div>

      {/* Cards de Totalizadores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <IndicadorCard
          titulo="Entradas Realizadas"
          valor={totalizadores?.entradas_realizadas?.valor || 0}
          icone={<ArrowUpCircle className="h-4 w-4 text-green-500" />}
          cor="green"
          labelSecundario="Quantidade"
          valorSecundario={totalizadores?.entradas_realizadas?.quantidade || 0}
        />
        <IndicadorCard
          titulo="Saídas Realizadas"
          valor={totalizadores?.saidas_realizadas?.valor || 0}
          icone={<ArrowDownCircle className="h-4 w-4 text-red-500" />}
          cor="red"
          labelSecundario="Quantidade"
          valorSecundario={totalizadores?.saidas_realizadas?.quantidade || 0}
        />
        <IndicadorCard
          titulo="Saldo Atual"
          valor={resumo?.saldo_final || 0}
          comparativo={{
            percentual: resumo?.variacao_percentual || 0
          }}
          icone={<CircleDollarSign className="h-4 w-4 text-blue-500" />}
          cor="blue"
        />
        <IndicadorCard
          titulo="Saldo Projetado"
          valor={resumo?.saldo_projetado || 0}
          icone={<TrendingUp className="h-4 w-4 text-purple-500" />}
          cor="purple"
        />
      </div>

      {/* Relação Entradas x Saídas */}
      {(() => {
        const entradas = Number(totalizadores?.entradas_realizadas?.valor || 0);
        const saidas = Number(totalizadores?.saidas_realizadas?.valor || 0);
        const total = entradas + saidas;
        const percEntradas = total > 0 ? (entradas / total) * 100 : 0;
        const percSaidas = total > 0 ? (saidas / total) * 100 : 0;
        const formatCurrency = (v: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);

        return (
          <Card>
            <CardHeader>
              <CardTitle>Relação Entradas x Saídas (Período)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="h-3 w-full rounded bg-gray-100 overflow-hidden">
                  <div
                    className="h-full bg-green-500"
                    style={{ width: `${percEntradas}%` }}
                  />
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-green-600">
                    Entradas: {formatCurrency(entradas)} ({percEntradas.toFixed(1)}%)
                  </span>
                  <span className="text-red-600">
                    Saídas: {formatCurrency(saidas)} ({percSaidas.toFixed(1)}%)
                  </span>
                </div>
                <div className="text-right text-sm">
                  Diferença (Entradas - Saídas): <span className={`${entradas - saidas >= 0 ? 'text-green-600' : 'text-red-600'} font-medium`}>{formatCurrency(entradas - saidas)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })()}

      {/* Documentos filtrados: Entradas e Saídas */}
      <Card>
        <CardHeader>
          <CardTitle>Documentos filtrados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Entradas */}
            <div>
              <h3 className="text-sm font-medium mb-2">Entradas</h3>
              <div className="max-h-80 overflow-auto border rounded-md">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 border-b">
                      <th className="px-3 py-2 text-left">Data</th>
                      <th className="px-3 py-2 text-left">Descrição</th>
                      <th className="px-3 py-2 text-right">Valor</th>
                      <th className="px-3 py-2 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(movimentos || []).filter(m => m.tipo === 'entrada').slice(0, 50).map((m) => (
                      <tr key={`e-${m.id}`} className="border-b">
                        <td className="px-3 py-2">{new Date(m.data).toLocaleDateString('pt-BR')}</td>
                        <td className="px-3 py-2">{m.descricao}</td>
                        <td className="px-3 py-2 text-right">
                          {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(m.valor)}
                        </td>
                        <td className="px-3 py-2 text-center">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${m.realizado ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                            {m.realizado ? 'Realizado' : 'Pendente'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            {/* Saídas */}
            <div>
              <h3 className="text-sm font-medium mb-2">Saídas</h3>
              <div className="max-h-80 overflow-auto border rounded-md">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 border-b">
                      <th className="px-3 py-2 text-left">Data</th>
                      <th className="px-3 py-2 text-left">Descrição</th>
                      <th className="px-3 py-2 text-right">Valor</th>
                      <th className="px-3 py-2 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(movimentos || []).filter(m => m.tipo === 'saida').slice(0, 50).map((m) => (
                      <tr key={`s-${m.id}`} className="border-b">
                        <td className="px-3 py-2">{new Date(m.data).toLocaleDateString('pt-BR')}</td>
                        <td className="px-3 py-2">{m.descricao}</td>
                        <td className="px-3 py-2 text-right">
                          {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(m.valor)}
                        </td>
                        <td className="px-3 py-2 text-center">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${m.realizado ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                            {m.realizado ? 'Realizado' : 'Pendente'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Métricas do Negócio */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <IndicadorCard
          titulo="Vendas"
          valor={resumo?.vendas_equipamentos || 0}
          icone={<Printer className="h-4 w-4 text-green-500" />}
          cor="green"
        />
        <IndicadorCard
          titulo="Locação"
          valor={resumo.receitas_detalhadas?.locacao || 0}
          icone={<Package className="h-4 w-4 text-blue-500" />}
          cor="blue"
          labelSecundario="Contratos Ativos"
          valorSecundario={resumo?.alugueis_ativos || 0}
        />
        <IndicadorCard
          titulo="Serviços"
          valor={resumo?.servicos_total || 0}
          icone={<FileText className="h-4 w-4 text-orange-500" />}
          cor="orange"
        />
        <IndicadorCard
          titulo="Suprimentos"
          valor={resumo?.suprimentos_total || 0}
          icone={<Package className="h-4 w-4 text-purple-500" />}
          cor="purple"
        />
      </div>

      {/* Tabs de conteúdo */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="visao-geral">Visão Geral</TabsTrigger>
          <TabsTrigger value="movimentacoes">Movimentações</TabsTrigger>
          <TabsTrigger value="categorias">Categorias</TabsTrigger>
          <TabsTrigger value="previsoes">Previsões</TabsTrigger>
        </TabsList>

        <TabsContent value="visao-geral">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Fluxo de Caixa</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={movimentosData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="data" />
                      <YAxis tickFormatter={(value) => 
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL',
                          notation: 'compact'
                        }).format(Number(value))
                      } />
                      <Tooltip formatter={(value) => 
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(Number(value))
                      } />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="entradas" 
                        name="Entradas" 
                        stroke="#10B981" 
                        strokeWidth={2}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="saidas" 
                        name="Saídas" 
                        stroke="#EF4444" 
                        strokeWidth={2}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="saldo" 
                        name="Saldo" 
                        stroke="#3B82F6" 
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Distribuição por Categoria</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={categoriasData}
                        dataKey="valor"
                        nameKey="categoria"
                        cx="50%"
                        cy="50%"
                        outerRadius={150}
                        label={({ categoria, percent }) => 
                          `${categoria} (${(percent * 100).toFixed(1)}%)`
                        }
                      >
                        {categoriasData.map((_, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={CORES_CATEGORIAS[index % CORES_CATEGORIAS.length]} 
                          />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => 
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(Number(value))
                      } />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="movimentacoes">
          <Card>
            <CardHeader>
              <CardTitle>Movimentações por Período</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Gráfico de Movimentações */}
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={movimentosData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="data" />
                      <YAxis tickFormatter={(value) => 
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL',
                          notation: 'compact'
                        }).format(Number(value))
                      } />
                      <Tooltip formatter={(value) => 
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(Number(value))
                      } />
                      <Legend />
                      <Bar dataKey="entradas" name="Entradas" fill="#10B981" />
                      <Bar dataKey="saidas" name="Saídas" fill="#EF4444" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Tabela de Movimentações */}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="px-4 py-2 text-left">Data</th>
                        <th className="px-4 py-2 text-left">Descrição</th>
                        <th className="px-4 py-2 text-left">Tipo</th>
                        <th className="px-4 py-2 text-right">Valor</th>
                        <th className="px-4 py-2 text-center">Status</th>
                        <th className="px-4 py-2 text-center">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(movimentos || []).map((movimento) => (
                        <tr key={movimento.id} className="border-b">
                          <td className="px-4 py-2">
                            {new Date(movimento.data).toLocaleDateString('pt-BR')}
                          </td>
                          <td className="px-4 py-2">{movimento.descricao}</td>
                          <td className="px-4 py-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              movimento.tipo === 'entrada' 
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {movimento.tipo === 'entrada' ? 'Entrada' : 'Saída'}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-right">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            }).format(movimento.valor)}
                          </td>
                          <td className="px-4 py-2 text-center">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              movimento.realizado
                                ? 'bg-green-100 text-green-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {movimento.realizado ? 'Realizado' : 'Pendente'}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-center">
                            {!movimento.realizado && onMovimentoStatusChange && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onMovimentoStatusChange(movimento.id)}
                                className="text-blue-600 hover:text-blue-800"
                              >
                                Realizar
                              </Button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categorias">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Receitas por Categoria</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart 
                      data={categoriasData}
                      layout="vertical"
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" tickFormatter={(value) => 
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL',
                          notation: 'compact'
                        }).format(Number(value))
                      } />
                      <YAxis type="category" dataKey="categoria" width={100} />
                      <Tooltip formatter={(value) => 
                        new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(Number(value))
                      } />
                      <Bar dataKey="valor" fill="#10B981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Status das Movimentações</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-4">
                  <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium">Entradas Realizadas</p>
                      <p className="text-2xl font-bold text-green-600">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(totalizadores?.entradas_realizadas?.valor || 0)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Quantidade</p>
                      <p className="text-lg font-medium">
                        {totalizadores?.entradas_realizadas?.quantidade || 0}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium">Entradas Previstas</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(totalizadores?.entradas_previstas?.valor || 0)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Quantidade</p>
                      <p className="text-lg font-medium">
                        {totalizadores?.entradas_previstas?.quantidade || 0}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium">Saídas Realizadas</p>
                      <p className="text-2xl font-bold text-red-600">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(totalizadores?.saidas_realizadas?.valor || 0)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Quantidade</p>
                      <p className="text-lg font-medium">
                        {totalizadores?.saidas_realizadas?.quantidade || 0}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium">Saídas Previstas</p>
                      <p className="text-2xl font-bold text-orange-600">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(totalizadores?.saidas_previstas?.valor || 0)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Quantidade</p>
                      <p className="text-lg font-medium">
                        {totalizadores?.saidas_previstas?.quantidade || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="previsoes">
          <div className="grid grid-cols-1 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Análise de Previsões</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <h3 className="text-lg font-medium mb-4">Entradas Previstas vs Realizadas</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Total Previsto</span>
                          <span className="font-medium">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            }).format(totalizadores?.entradas_previstas?.valor || 0)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Total Realizado</span>
                          <span className="font-medium">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            }).format(totalizadores?.entradas_realizadas?.valor || 0)}
                          </span>
                        </div>
                        <div className="flex justify-between pt-2 border-t">
                          <span className="text-sm font-medium">Taxa de Realização</span>
                          <span className="font-medium text-green-600">
                            {(((totalizadores?.entradas_realizadas?.valor || 0) / 
                              ((totalizadores?.entradas_previstas?.valor || 0) + (totalizadores?.entradas_realizadas?.valor || 0))) * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 bg-gray-50 rounded-lg">
                      <h3 className="text-lg font-medium mb-4">Saídas Previstas vs Realizadas</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Total Previsto</span>
                          <span className="font-medium">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            }).format(totalizadores?.saidas_previstas?.valor || 0)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Total Realizado</span>
                          <span className="font-medium">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL'
                            }).format(totalizadores?.saidas_realizadas?.valor || 0)}
                          </span>
                        </div>
                        <div className="flex justify-between pt-2 border-t">
                          <span className="text-sm font-medium">Taxa de Realização</span>
                          <span className="font-medium text-red-600">
                            {(((totalizadores?.saidas_realizadas?.valor || 0) / 
                              ((totalizadores?.saidas_previstas?.valor || 0) + (totalizadores?.saidas_realizadas?.valor || 0))) * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6">
                    <h3 className="text-lg font-medium mb-4">Saldos Projetados</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-muted-foreground">Saldo Inicial</p>
                        <p className="text-2xl font-bold">
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(resumo?.saldo_inicial || 0)}
                        </p>
                      </div>
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-muted-foreground">Saldo Final</p>
                        <p className="text-2xl font-bold">
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(resumo?.saldo_final || 0)}
                        </p>
                      </div>
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-muted-foreground">Saldo Projetado</p>
                        <p className="text-2xl font-bold">
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(resumo?.saldo_projetado || 0)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OperationalDashboardComplete;