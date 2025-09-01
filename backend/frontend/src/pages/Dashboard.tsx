import { useQuery } from '@tanstack/react-query';
import { Box, Paper, Typography } from '@mui/material';
import { api } from '../api/client';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

type Resumo = {
  total_atrasado: number;
  total_pago_periodo: number;
  total_cancelado_periodo: number;
  total_aberto_periodo: number;
  quantidade_titulos: number;
  quantidade_atrasados_periodo: number;
};

export function Dashboard() {
  const { data: receber } = useQuery({
    queryKey: ['receberDashboard'],
    queryFn: async () => (await api.get<{ resumo: Resumo }>('contas_receber/dashboard/')).data,
  });

  const { data: pagar } = useQuery({
    queryKey: ['pagarDashboard'],
    queryFn: async () => (await api.get<{ resumo: Resumo }>('contas_pagar/dashboard/')).data,
  });

  const cards = [
    { title: 'AR Atrasado', value: receber?.resumo.total_atrasado ?? 0 },
    { title: 'AR Aberto Período', value: receber?.resumo.total_aberto_periodo ?? 0 },
    { title: 'AP Aberto Período', value: pagar?.resumo.total_aberto_periodo ?? 0 },
    { title: 'Títulos AR', value: receber?.resumo.quantidade_titulos ?? 0 },
  ];

  const chartData = [
    { name: 'AR Aberto', ar: receber?.resumo.total_aberto_periodo ?? 0 },
    { name: 'AP Aberto', ar: pagar?.resumo.total_aberto_periodo ?? 0 },
  ];

  return (
    <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' } }}>
      {cards.map((c) => (
        <Paper key={c.title} sx={{ p: 2 }}>
          <Typography variant="overline">{c.title}</Typography>
          <Typography variant="h5">
            {typeof c.value === 'number' ? c.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : c.value}
          </Typography>
        </Paper>
      ))}
      <Box sx={{ gridColumn: '1 / -1' }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ mb: 1 }}>
            Comparativo rápido
          </Typography>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(v: number) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} />
              <Bar dataKey="ar" fill="#1976d2" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Box>
    </Box>
  );
}
