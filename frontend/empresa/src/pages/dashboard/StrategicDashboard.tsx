import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { MetricCard } from '@/components/dashboard/financialMetrics';
import { Filtros } from '@/types/dashboardNovo';

interface StrategicDashboardProps {
  data: {
    dre: any;
    tendencias: any;
    projecoes: any;
    indicadores: any;
  };
  loading?: boolean;
  onFiltrosChange: (filtros: Partial<Filtros>) => void;
  onRefresh: () => void;
  onExport: () => void;
  
}

export const StrategicDashboard: React.FC<StrategicDashboardProps> = ({ 
  data,
  loading = false 
}) => {
  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-gray-100 animate-pulse rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Erro ao carregar dados do dashboard estratégico.
        </AlertDescription>
      </Alert>
    );
  }

  const { dre, tendencias, projecoes, indicadores } = data;

  return (
    <div className="space-y-6">
      {/* KPIs Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Liquidez Imediata"
          value={indicadores.liquidez_imediata}
          format="number"
          change={0}
        />
        <MetricCard
          title="Ciclo de Caixa"
          value={indicadores.ciclo_caixa}
          format="days"
          change={0}
        />
        <MetricCard
          title="Margem Operacional"
          value={indicadores.margem_operacional}
          format="percentage"
          change={indicadores.crescimento_receitas}
        />
        <MetricCard
          title="Resultado Líquido"
          value={dre.resultado_liquido}
          format="currency"
          change={((dre.resultado_liquido - dre.resultado_antes_impostos) / 
                  dre.resultado_antes_impostos * 100)}
        />
      </div>

      {/* Gráficos Principais */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Evolução DRE */}
        <Card>
          <CardHeader>
            <CardTitle>Evolução DRE</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    { name: 'Receita Bruta', value: dre.receita_bruta },
                    { name: 'Receita Líquida', value: dre.receita_liquida },
                    { name: 'Resultado Operacional', value: dre.resultado_operacional },
                    { name: 'Resultado Líquido', value: dre.resultado_liquido }
                  ]}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 50, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" 
                    tickFormatter={(value) => 
                      new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                        notation: 'compact'
                      }).format(value)
                    }
                  />
                  <YAxis dataKey="name" type="category" />
                  <Tooltip 
                    formatter={(value: any) => 
                      new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(value)
                    }
                  />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Tendências */}
        <Card>
          <CardHeader>
            <CardTitle>Tendências de Receitas e Despesas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={tendencias.receitas}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="periodo" />
                  <YAxis 
                    tickFormatter={(value) => 
                      new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                        notation: 'compact'
                      }).format(value)
                    }
                  />
                  <Tooltip 
                    formatter={(value: any) => 
                      new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(value)
                    }
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="valor_realizado" 
                    name="Realizado"
                    stroke="#10b981" 
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="valor_previsto" 
                    name="Previsto"
                    stroke="#f59e0b" 
                    strokeWidth={2} 
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Projeções */}
        <Card>
          <CardHeader>
            <CardTitle>Projeções Financeiras</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    { 
                      periodo: '30 dias',
                      ...projecoes.proximos_30_dias
                    },
                    { 
                      periodo: '90 dias',
                      ...projecoes.proximos_90_dias
                    },
                    { 
                      periodo: '180 dias',
                      ...projecoes.proximos_180_dias
                    }
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="periodo" />
                  <YAxis
                    tickFormatter={(value) => 
                      new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                        notation: 'compact'
                      }).format(value)
                    }
                  />
                  <Tooltip
                    formatter={(value: any) => 
                      new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(value)
                    }
                  />
                  <Legend />
                  <Bar 
                    dataKey="entradas_total" 
                    name="Entradas" 
                    fill="#10b981"
                  />
                  <Bar 
                    dataKey="saidas_total" 
                    name="Saídas" 
                    fill="#ef4444"
                  />
                  <Bar 
                    dataKey="saldo_projetado" 
                    name="Saldo" 
                    fill="#3b82f6"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Análise de Custos */}
        <Card>
          <CardHeader>
            <CardTitle>Análise de Custos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    { name: 'Custos Operacionais', value: dre.custos_operacionais },
                    { name: 'Despesas Operacionais', value: dre.despesas_operacionais },
                    { name: 'Impostos', value: dre.impostos }
                  ]}
                  layout="vertical"
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number"
                    tickFormatter={(value) => 
                      new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                        notation: 'compact'
                      }).format(value)
                    }
                  />
                  <YAxis dataKey="name" type="category" />
                  <Tooltip
                    formatter={(value: any) => 
                      new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                      }).format(value)
                    }
                  />
                  <Bar dataKey="value" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};