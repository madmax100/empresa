import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import {
  Paper,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Stack,
  TextField,
  Select,
  MenuItem,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { useMemo, useState } from 'react';

type Titulo = {
  id: number;
  historico: string;
  vencimento: string;
  valor: string | number;
  status: 'A' | 'P' | 'C';
  cliente?: { id: number; nome: string };
};

export function ReceberList() {
  const qc = useQueryClient();

  const [vencIni, setVencIni] = useState<string>('');
  const [vencFim, setVencFim] = useState<string>('');
  const [status, setStatus] = useState<string>(''); // '', A, P, C
  const [busca, setBusca] = useState<string>('');
  const [ordenacao, setOrdenacao] = useState<string>('vencimento_desc');

  const params = useMemo(() => {
    const p: Record<string, string> = {};
    if (vencIni) p.vencimento_inicial = vencIni;
    if (vencFim) p.vencimento_final = vencFim;
    if (status) p.status = status;
    if (busca.trim()) p.busca = busca.trim();
    return p;
  }, [vencIni, vencFim, status, busca]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['receberList', params],
    queryFn: async () => (await api.get<Titulo[]>('contas_receber/', { params })).data,
  });

  const sorted = useMemo(() => {
    const arr = [...(data ?? [])];
    const [campo, dir] = ordenacao.split('_');
    const mult = dir === 'desc' ? -1 : 1;
    const get = (t: Titulo) => {
      switch (campo) {
        case 'vencimento':
          return new Date(t.vencimento).getTime();
        case 'valor':
          return Number(t.valor || 0);
        case 'status':
          return t.status;
        case 'cliente':
          return (t.cliente?.nome || '').toLowerCase();
        case 'id':
        default:
          return t.id;
      }
    };
    arr.sort((a, b) => {
      const va = get(a);
      const vb = get(b);
      if (va < vb) return -1 * mult;
      if (va > vb) return 1 * mult;
      return 0;
    });
    return arr;
  }, [data, ordenacao]);

  // Baixar (atualizar_status)
  const [baixarOpen, setBaixarOpen] = useState(false);
  const [baixaTitulo, setBaixaTitulo] = useState<Titulo | null>(null);
  const [dataPagamento, setDataPagamento] = useState<string>('');
  const [valorPago, setValorPago] = useState<string>('');

  const baixarMut = useMutation({
    mutationFn: async (vars: { id: number; data_pagamento: string; valor_pago: string }) => {
      return (
        await api.patch(`contas_receber/${vars.id}/atualizar_status/`, {
          status: 'P',
          data_pagamento: vars.data_pagamento,
          valor_pago: vars.valor_pago,
        })
      ).data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['receberList'] });
      qc.invalidateQueries({ queryKey: ['receberDashboard'] });
      setBaixarOpen(false);
      setBaixaTitulo(null);
      setDataPagamento('');
      setValorPago('');
    },
  });

  // Estornar
  const estornarMut = useMutation({
    mutationFn: async (id: number) => (await api.post(`contas_receber/${id}/estornar_baixa/`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['receberList'] });
      qc.invalidateQueries({ queryKey: ['receberDashboard'] });
    },
  });

  const total = (data ?? []).reduce((acc, t) => acc + Number(t.valor || 0), 0);

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Contas a Receber
      </Typography>

  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ mb: 2 }}>
        <TextField
          label="Venc. inicial"
          type="date"
          InputLabelProps={{ shrink: true }}
          value={vencIni}
          onChange={(e) => setVencIni(e.target.value)}
        />
        <TextField
          label="Venc. final"
          type="date"
          InputLabelProps={{ shrink: true }}
          value={vencFim}
          onChange={(e) => setVencFim(e.target.value)}
        />
        <Select
          displayEmpty
          value={status}
          onChange={(e) => setStatus(e.target.value as string)}
          sx={{ minWidth: 160 }}
        >
          <MenuItem value=""><em>Status (todos)</em></MenuItem>
          <MenuItem value="A">Aberto</MenuItem>
          <MenuItem value="P">Pago</MenuItem>
          <MenuItem value="C">Cancelado</MenuItem>
        </Select>
        <TextField
          label="Buscar"
          placeholder="cliente, histórico, forma"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          sx={{ minWidth: 240, flex: 1 }}
        />
        <Select
          value={ordenacao}
          onChange={(e) => setOrdenacao(e.target.value as string)}
          sx={{ minWidth: 220 }}
        >
          <MenuItem value={'vencimento_desc'}>Vencimento (mais recente)</MenuItem>
          <MenuItem value={'vencimento_asc'}>Vencimento (mais antigo)</MenuItem>
          <MenuItem value={'valor_desc'}>Valor (maior primeiro)</MenuItem>
          <MenuItem value={'valor_asc'}>Valor (menor primeiro)</MenuItem>
          <MenuItem value={'cliente_asc'}>Cliente (A-Z)</MenuItem>
          <MenuItem value={'cliente_desc'}>Cliente (Z-A)</MenuItem>
          <MenuItem value={'status_asc'}>Status (A→P→C)</MenuItem>
          <MenuItem value={'status_desc'}>Status (C→P→A)</MenuItem>
          <MenuItem value={'id_desc'}>ID (decrescente)</MenuItem>
          <MenuItem value={'id_asc'}>ID (crescente)</MenuItem>
        </Select>
        <Button variant="outlined" onClick={() => { setVencIni(''); setVencFim(''); setStatus(''); setBusca(''); }}>
          Limpar
        </Button>
      </Stack>

  {isLoading && <Typography variant="body2">Carregando…</Typography>}
  {error && <Typography color="error">Erro ao carregar dados.</Typography>}
  <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Cliente</TableCell>
            <TableCell>Histórico</TableCell>
            <TableCell>Vencimento</TableCell>
            <TableCell align="right">Valor</TableCell>
            <TableCell>Status</TableCell>
            <TableCell align="right">Ações</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sorted.map((t) => (
            <TableRow key={t.id}>
              <TableCell>{t.id}</TableCell>
              <TableCell>{t.cliente?.nome ?? '-'}</TableCell>
              <TableCell>{t.historico}</TableCell>
              <TableCell>{new Date(t.vencimento).toLocaleDateString('pt-BR')}</TableCell>
              <TableCell align="right">
                {Number(t.valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </TableCell>
              <TableCell>{t.status}</TableCell>
              <TableCell align="right">
                {t.status === 'A' && (
                  <Button size="small" onClick={() => { setBaixaTitulo(t); setBaixarOpen(true); }}>
                    Baixar
                  </Button>
                )}
                {t.status === 'P' && (
                  <Button size="small" color="warning" onClick={() => estornarMut.mutate(t.id)}>
                    Estornar
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
        <tfoot>
          <TableRow>
            <TableCell colSpan={4} align="right">
              <strong>Total</strong>
            </TableCell>
            <TableCell align="right">
              <strong>{total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</strong>
            </TableCell>
            <TableCell />
            <TableCell />
          </TableRow>
        </tfoot>
      </Table>

      <Dialog open={baixarOpen} onClose={() => setBaixarOpen(false)}>
        <DialogTitle>Baixar título {baixaTitulo?.id}</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ mt: 1 }}>
            <TextField
              label="Data pagamento"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={dataPagamento}
              onChange={(e) => setDataPagamento(e.target.value)}
              fullWidth
            />
            <TextField
              label="Valor pago"
              type="number"
              value={valorPago}
              onChange={(e) => setValorPago(e.target.value)}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBaixarOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            disabled={!baixaTitulo || !dataPagamento || !valorPago || baixarMut.isPending}
            onClick={() => baixaTitulo && baixarMut.mutate({ id: baixaTitulo.id, data_pagamento: dataPagamento, valor_pago: valorPago })}
          >
            Confirmar
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}
