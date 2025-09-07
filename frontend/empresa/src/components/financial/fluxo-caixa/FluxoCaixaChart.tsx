import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart } from 'recharts';
import { formatCurrency } from '@/lib/utils';

interface FluxoCaixaChartProps {
  data: any[];
  type?: 'bar' | 'line' | 'composed';
}

export const FluxoCaixaChart = ({ data, type = 'composed' }: FluxoCaixaChartProps) => {
  if (type === 'line') {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis tickFormatter={(value) => formatCurrency(value as number)} />
          <Tooltip formatter={(value) => formatCurrency(value as number)} />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="saldo" 
            stroke="#3b82f6" 
            strokeWidth={3}
            name="Saldo Acumulado" 
            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'bar') {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis tickFormatter={(value) => formatCurrency(value as number)} />
          <Tooltip formatter={(value) => formatCurrency(value as number)} />
          <Legend />
          <Bar dataKey="receitas" fill="#22c55e" name="Receitas" />
          <Bar dataKey="despesas" fill="#ef4444" name="Despesas" />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  // Gráfico composto (barras + linha)
  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis tickFormatter={(value) => formatCurrency(value as number)} />
        <Tooltip formatter={(value) => formatCurrency(value as number)} />
        <Legend />
        <Bar dataKey="receitas" fill="#22c55e" name="Receitas" />
        <Bar dataKey="despesas" fill="#ef4444" name="Despesas" />
        <Line 
          type="monotone" 
          dataKey="saldo" 
          stroke="#3b82f6" 
          strokeWidth={3}
          name="Saldo Acumulado" 
          dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
};
