import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  AlertCircle,
  Download,
  TrendingUp,
  TrendingDown,
  CircleDollarSign,
  Printer,
  Package,
  FileText
} from "lucide-react";

import { 
  DashboardGerencial
} from '@/types/dashboardNovo';

interface IndicadorCardProps {
  titulo: string;
  valor: number;
  comparativo?: {
    valor: number;
    percentual: number;
  };
  cor?: string;
  icone?: React.ReactNode;
  descricao?: string;
}

const IndicadorCard: React.FC<IndicadorCardProps> = ({
  titulo,
  valor,
  comparativo,
  cor = 'blue',
  icone,
  descricao
}) => {
  const formatarValor = (val: number) => {
    if (isNaN(val)) return "N/A";
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(val);
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center">
          {icone && <div className="mr-2">{icone}</div>}
          {titulo}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          <div className={`text-2xl font-bold text-${cor}-600`}>
            {formatarValor(valor)}
          </div>
          {comparativo && (
            <div className="flex items-center text-sm">
              {comparativo.percentual >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
              )}
              <span className={comparativo.percentual >= 0 ? "text-green-500" : "text-red-500"}>
                {comparativo.percentual >= 0 ? "+" : ""}
                {comparativo.percentual.toFixed(1)}%
              </span>
              <span className="text-muted-foreground ml-1">vs. período anterior</span>
            </div>
          )}
          {descricao && (
            <p className="text-sm text-muted-foreground">{descricao}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

interface ManagementDashboardProps {
  data: DashboardGerencial | null;
  loading?: boolean;
  onExport: () => void;
  className?: string;
}

export const ManagementDashboard: React.FC<ManagementDashboardProps> = ({
  data,
  loading = false,
  onExport,
  className = ''
}) => {
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
          Não foi possível carregar os dados do dashboard gerencial.
        </AlertDescription>
      </Alert>
    );
  }

  const { resumo, analise_categorias, tendencias, indicadores, recomendacoes } = data;

  const principais_receitas = (analise_categorias || []).filter(c => c.entradas > 0).map(c => ({ ...c, valor: c.entradas, percentual: (resumo?.atual?.entradas || 0) > 0 ? (c.entradas / (resumo?.atual?.entradas || 1)) * 100 : 0 }));
  const principais_despesas = (analise_categorias || []).filter(c => c.saidas > 0).map(c => ({ ...c, valor: c.saidas }));

  const evolucaoData = (tendencias?.historico || []).map(h => ({
      data: h.mes,
      entradas: h.entradas,
      saidas: h.saidas,
      saldo: h.entradas - h.saidas
  }));

  const faturamentoTotalAnterior = resumo?.anterior?.resultado || 0;
  const faturamentoTotalAtual = resumo?.atual?.resultado || 0;
  const variacaoFaturamento = faturamentoTotalAnterior ? ((faturamentoTotalAtual - faturamentoTotalAnterior) / Math.abs(faturamentoTotalAnterior)) * 100 : (faturamentoTotalAtual > 0 ? 100 : 0);

  const COLORS = ['#10B981', '#F59E0B', '#3B82F6', '#EC4899', '#6366F1'];

  const formatarCategoria = (categoria: string) => {
    const mapeamento: { [key: string]: string } = {
      'vendas_equipamentos': 'Vendas',
      'aluguel_equipamentos': 'Locação',
      'servicos_manutencao': 'Serviços',
      'suprimentos': 'Suprimentos',
      'pecas_reposicao': 'Peças'
    };
    return mapeamento[categoria] || categoria.charAt(0).toUpperCase() + categoria.slice(1);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard Gerencial</h1>
        <Button variant="outline" onClick={onExport}>
          <Download className="h-4 w-4 mr-2" />
          Exportar Relatório
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <IndicadorCard
          titulo="Resultado do Período"
          valor={faturamentoTotalAtual}
          comparativo={{
            valor: faturamentoTotalAnterior,
            percentual: variacaoFaturamento
          }}
          icone={<CircleDollarSign className="h-4 w-4 text-blue-500" />}
          cor="blue"
          descricao="Entradas - Saídas"
        />
        <IndicadorCard
          titulo="Margem de Lucro"
          valor={(indicadores?.margem || 0) * 100}
          descricao={`${((indicadores?.margem || 0) * 100).toFixed(1)}%`}
          icone={<Printer className="h-4 w-4 text-green-500" />}
          cor="green"
        />
        <IndicadorCard
          titulo="Realização de Entradas"
          valor={(indicadores?.realizacao_entradas || 0) * 100}
          descricao={`${((indicadores?.realizacao_entradas || 0) * 100).toFixed(1)}% do previsto`}
          icone={<Package className="h-4 w-4 text-purple-500" />}
          cor="purple"
        />
        <IndicadorCard
          titulo="Realização de Saídas"
          valor={(indicadores?.realizacao_saidas || 0) * 100}
          descricao={`${((indicadores?.realizacao_saidas || 0) * 100).toFixed(1)}% do previsto`}
          icone={<FileText className="h-4 w-4 text-orange-500" />}
          cor="orange"
        />
      </div>

      {/* Gráficos e Análises */}
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="categorias">Análise de Categorias</TabsTrigger>
          <TabsTrigger value="recomendacoes">Recomendações</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico de Evolução */}
            <Card>
              <CardHeader>
                <CardTitle>Evolução Mensal</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={evolucaoData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="data" />
                      <YAxis tickFormatter={(value) => new Intl.NumberFormat('pt-BR', { notation: 'compact', style: 'currency', currency: 'BRL' }).format(value)} />
                      <Tooltip formatter={(value: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)} />
                      <Legend />
                      <Line type="monotone" dataKey="entradas" name="Entradas" stroke="#10B981" strokeWidth={2} />
                      <Line type="monotone" dataKey="saidas" name="Saídas" stroke="#EF4444" strokeWidth={2} />
                      <Line type="monotone" dataKey="saldo" name="Saldo" stroke="#3B82F6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Distribuição de Receitas */}
            <Card>
              <CardHeader>
                <CardTitle>Distribuição de Receitas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={principais_receitas}
                        dataKey="valor"
                        nameKey="categoria"
                        cx="50%"
                        cy="50%"
                        outerRadius={150}
                        label={({ categoria, percentual }) => `${formatarCategoria(categoria)} (${(percentual || 0).toFixed(1)}%)`}
                      >
                        {principais_receitas.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)} />
                      <Legend formatter={(value) => formatarCategoria(value)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="categorias">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Análise de Receitas por Categoria */}
            <Card>
              <CardHeader>
                <CardTitle>Análise de Receitas por Categoria</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={principais_receitas} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" tickFormatter={(value) => new Intl.NumberFormat('pt-BR', { notation: 'compact', style: 'currency', currency: 'BRL' }).format(value)} />
                      <YAxis type="category" dataKey="categoria" tickFormatter={formatarCategoria} width={80} />
                      <Tooltip formatter={(value: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)} />
                      <Bar dataKey="valor" name="Valor" fill="#10B981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Análise de Despesas por Categoria */}
            <Card>
              <CardHeader>
                <CardTitle>Análise de Despesas por Categoria</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={principais_despesas} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" tickFormatter={(value) => new Intl.NumberFormat('pt-BR', { notation: 'compact', style: 'currency', currency: 'BRL' }).format(value)} />
                      <YAxis type="category" dataKey="categoria" tickFormatter={formatarCategoria} width={80} />
                      <Tooltip formatter={(value: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)} />
                      <Bar dataKey="valor" name="Valor" fill="#EF4444" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="recomendacoes">
            <Card>
                <CardHeader>
                    <CardTitle>Recomendações e Alertas</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {recomendacoes && recomendacoes.length > 0 ? recomendacoes.map((rec, index) => (
                            <Alert key={index} variant={rec.severidade === 'alta' ? 'destructive' : 'default'}>
                                <AlertCircle className="h-4 w-4" />
                                <AlertDescription>
                                    <p className="font-bold">{rec.mensagem}</p>
                                    <ul className="list-disc pl-5 mt-2">
                                        {rec.acoes.map((acao, i) => <li key={i}>{acao}</li>)}
                                    </ul>
                                </AlertDescription>
                            </Alert>
                        )) : (
                            <p>Nenhuma recomendação no momento.</p>
                        )}
                    </div>
                </CardContent>
            </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};