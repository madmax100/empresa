import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  ComposedChart,
  Area
} from 'recharts';
import { DashboardOperacional } from '../../../types';

interface FluxoCaixaChartsProps {
  data: DashboardOperacional | null;
  loading?: boolean;
  className?: string;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

export const FluxoCaixaCharts: React.FC<FluxoCaixaChartsProps> = ({
  data,
  loading = false,
  className = ''
}) => {
  if (loading) {
    return (
      <div className={`grid grid-cols-1 lg:grid-cols-2 gap-6 ${className}`}>
        {[1, 2].map((index) => (
          <Card key={index}>
            <CardHeader>
              <div className="h-6 bg-gray-200 rounded w-1/3 animate-pulse"></div>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] bg-gray-100 rounded animate-pulse"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const { evolucao_diaria, categorias } = data;

  // Preparar dados para o gráfico de categorias
  const categoriasData = Object.entries(categorias).map(([categoria, valores]) => ({
    categoria,
    entradas: valores.entradas,
    saidas: valores.saidas,
    saldo: valores.saldo
  }));

  return (
    <div className={`grid grid-cols-1 lg:grid-cols-2 gap-6 ${className}`}>
      {/* Gráfico de Evolução */}
      <Card>
        <CardHeader>
          <CardTitle>Evolução do Fluxo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={evolucao_diaria}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="data" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR')}
                />
                <YAxis 
                  yAxisId="left"
                  orientation="left"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => formatCurrency(value)}
                />
                <YAxis 
                  yAxisId="right"
                  orientation="right"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => formatCurrency(value)}
                />
                <Tooltip 
                  formatter={(value: number) => formatCurrency(value)}
                  labelFormatter={(label) => new Date(label).toLocaleDateString('pt-BR')}
                />
                <Legend />
                <Bar
                  yAxisId="left"
                  dataKey="entradas"
                  name="Entradas"
                  fill="#10b981"
                  barSize={20}
                />
                <Bar
                  yAxisId="left"
                  dataKey="saidas"
                  name="Saídas"
                  fill="#ef4444"
                  barSize={20}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="saldo"
                  name="Saldo"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Gráfico por Categoria */}
      <Card>
        <CardHeader>
          <CardTitle>Análise por Categoria</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoriasData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="categoria" 
                  tick={{ fontSize: 12 }}
                  interval={0}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => formatCurrency(value)}
                />
                <Tooltip 
                  formatter={(value: number) => formatCurrency(value)}
                />
                <Legend />
                <Bar 
                  dataKey="entradas" 
                  name="Entradas" 
                  fill="#10b981" 
                  stackId="a"
                />
                <Bar 
                  dataKey="saidas" 
                  name="Saídas" 
                  fill="#ef4444" 
                  stackId="a"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Gráfico de Tendência */}
      <Card>
        <CardHeader>
          <CardTitle>Tendência de Saldo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={evolucao_diaria}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="data"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR')}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => formatCurrency(value)}
                />
                <Tooltip 
                  formatter={(value: number) => formatCurrency(value)}
                  labelFormatter={(label) => new Date(label).toLocaleDateString('pt-BR')}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="saldo"
                  name="Saldo"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.1}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Gráfico de Comparação */}
      <Card>
        <CardHeader>
          <CardTitle>Comparativo Entrada/Saída</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={evolucao_diaria}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="data"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR')}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => formatCurrency(value)}
                />
                <Tooltip 
                  formatter={(value: number) => formatCurrency(value)}
                  labelFormatter={(label) => new Date(label).toLocaleDateString('pt-BR')}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="entradas"
                  name="Entradas"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="saidas"
                  name="Saídas"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

