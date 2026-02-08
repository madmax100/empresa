import React, { useState } from 'react';
import api from '../services/api';

interface OperacaoState {
  loading: boolean;
  error: string | null;
  data: unknown;
}

const initialState: OperacaoState = {
  loading: false,
  error: null,
  data: null
};

const OperacoesVendasPage: React.FC = () => {
  const [pedidoId, setPedidoId] = useState('');
  const [numeroNota, setNumeroNota] = useState('');
  const [localId, setLocalId] = useState('');
  const [vencimento, setVencimento] = useState('');
  const [contaId, setContaId] = useState('');
  const [valorRecebido, setValorRecebido] = useState('');
  const [juros, setJuros] = useState('');
  const [tarifas, setTarifas] = useState('');
  const [desconto, setDesconto] = useState('');
  const [notaId, setNotaId] = useState('');
  const [comissaoPercentual, setComissaoPercentual] = useState('');
  const [operacao, setOperacao] = useState<OperacaoState>(initialState);
  const [listas, setListas] = useState<OperacaoState>(initialState);

  const handlePost = async (endpoint: string, payload: Record<string, unknown>) => {
    setOperacao({ loading: true, error: null, data: null });
    try {
      const response = await api.post(endpoint, payload);
      setOperacao({ loading: false, error: null, data: response.data });
    } catch (err) {
      setOperacao({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao executar operação.',
        data: null
      });
    }
  };

  const handleGet = async (endpoint: string) => {
    setListas({ loading: true, error: null, data: null });
    try {
      const response = await api.get(endpoint);
      setListas({ loading: false, error: null, data: response.data });
    } catch (err) {
      setListas({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao carregar lista.',
        data: null
      });
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{
        backgroundColor: 'white',
        padding: '24px',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        marginBottom: '24px'
      }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '8px' }}>Operações de Vendas</h2>
        <p style={{ color: '#6b7280', marginBottom: 0 }}>
          Execute operações de aprovação, faturamento, devolução, expedição e consultas financeiras.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Pedido</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Pedido (ID)</span>
            <input type="number" value={pedidoId} onChange={(event) => setPedidoId(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={() => handlePost('/contas/vendas/aprovar/', { pedido_id: Number(pedidoId) })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Aprovar</button>
            <button type="button" onClick={() => handlePost('/contas/vendas/cancelar/', { pedido_id: Number(pedidoId) })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #fee2e2', backgroundColor: '#fee2e2', color: '#b91c1c', cursor: 'pointer' }}>Cancelar</button>
            <button type="button" onClick={() => handlePost('/contas/vendas/comissoes/gerar/', { pedido_id: Number(pedidoId), percentual: comissaoPercentual })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Gerar comissão</button>
          </div>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Percentual Comissão</span>
            <input type="number" step="0.01" value={comissaoPercentual} onChange={(event) => setComissaoPercentual(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Faturamento</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Número Nota</span>
            <input type="text" value={numeroNota} onChange={(event) => setNumeroNota(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Vencimento</span>
            <input type="date" value={vencimento} onChange={(event) => setVencimento(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Local (ID)</span>
            <input type="number" value={localId} onChange={(event) => setLocalId(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={() => handlePost('/contas/vendas/faturar/', { pedido_id: Number(pedidoId), numero_nota: numeroNota, vencimento, local_id: Number(localId) })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: '#2563eb', color: 'white', cursor: 'pointer' }}>Faturar</button>
            <button type="button" onClick={() => handlePost('/contas/vendas/faturamento/estornar/', { pedido_id: Number(pedidoId), numero_nota: numeroNota, local_id: Number(localId) })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #fee2e2', backgroundColor: '#fee2e2', color: '#b91c1c', cursor: 'pointer' }}>Estornar faturamento</button>
          </div>
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Contas a Receber</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Conta (ID)</span>
            <input type="number" value={contaId} onChange={(event) => setContaId(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Valor Recebido</span>
            <input type="number" step="0.01" value={valorRecebido} onChange={(event) => setValorRecebido(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Juros</span>
            <input type="number" step="0.01" value={juros} onChange={(event) => setJuros(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Tarifas</span>
            <input type="number" step="0.01" value={tarifas} onChange={(event) => setTarifas(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Desconto</span>
            <input type="number" step="0.01" value={desconto} onChange={(event) => setDesconto(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={() => handlePost('/contas/vendas/conta-receber/baixar/', { conta_id: Number(contaId), data_pagamento: new Date().toISOString(), valor_recebido: valorRecebido, juros, tarifas, desconto })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Baixar conta</button>
            <button type="button" onClick={() => handlePost('/contas/vendas/conta-receber/estornar/', { conta_id: Number(contaId) })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #fee2e2', backgroundColor: '#fee2e2', color: '#b91c1c', cursor: 'pointer' }}>Estornar baixa</button>
          </div>
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Devolução & Expedição</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Nota (ID)</span>
            <input type="number" value={notaId} onChange={(event) => setNotaId(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={() => handlePost('/contas/vendas/devolucao/', { nota_id: Number(notaId), local_id: Number(localId), itens: [] })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Registrar devolução</button>
            <button type="button" onClick={() => handlePost('/contas/vendas/devolucao/cancelar/', { nota_id: Number(notaId) })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #fee2e2', backgroundColor: '#fee2e2', color: '#b91c1c', cursor: 'pointer' }}>Cancelar devolução</button>
            <button type="button" onClick={() => handlePost('/contas/vendas/expedicao/confirmar/', { pedido_id: Number(pedidoId), local_id: Number(localId) })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Confirmar expedição</button>
            <button type="button" onClick={() => handlePost('/contas/vendas/expedicao/estornar/', { pedido_id: Number(pedidoId) })} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #fee2e2', backgroundColor: '#fee2e2', color: '#b91c1c', cursor: 'pointer' }}>Estornar expedição</button>
          </div>
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Consultas</h3>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={() => handleGet('/contas/vendas/',)} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Lista vendas</button>
            <button type="button" onClick={() => handleGet('/contas/vendas/resumo/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Resumo vendas</button>
            <button type="button" onClick={() => handleGet('/contas/vendas/conta-receber/aging/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Aging contas</button>
            <button type="button" onClick={() => handleGet('/contas/vendas/conta-receber/atrasadas/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Contas atrasadas</button>
            <button type="button" onClick={() => handleGet(`/contas/vendas/detalhe/${pedidoId}/`)} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Detalhe pedido</button>
            <button type="button" onClick={() => handleGet('/contas/vendas/comissoes/resumo/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Resumo comissões</button>
            <button type="button" onClick={() => handleGet('/contas/vendas/expedicao/pendentes/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Expedição pendente</button>
            <button type="button" onClick={() => handleGet(`/contas/vendas/devolucao/saldo/${notaId}/`)} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Saldo devolução</button>
          </div>
        </div>
      </div>

      {operacao.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{operacao.error}</p>}
      {operacao.data && (
        <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
          {JSON.stringify(operacao.data, null, 2)}
        </pre>
      )}
      {listas.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{listas.error}</p>}
      {listas.data && (
        <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
          {JSON.stringify(listas.data, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default OperacoesVendasPage;
