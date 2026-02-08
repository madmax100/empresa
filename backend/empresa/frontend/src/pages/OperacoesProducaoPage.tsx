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

const OperacoesProducaoPage: React.FC = () => {
  const [numeroOrdem, setNumeroOrdem] = useState('');
  const [produtoFinalId, setProdutoFinalId] = useState('');
  const [localId, setLocalId] = useState('');
  const [quantidadePlanejada, setQuantidadePlanejada] = useState('');
  const [insumoId, setInsumoId] = useState('');
  const [insumoQuantidade, setInsumoQuantidade] = useState('');
  const [ordemId, setOrdemId] = useState('');
  const [consumoProdutoId, setConsumoProdutoId] = useState('');
  const [consumoQuantidade, setConsumoQuantidade] = useState('');
  const [quantidadeProduzida, setQuantidadeProduzida] = useState('');
  const [geracao, setGeracao] = useState<OperacaoState>(initialState);
  const [statusUpdate, setStatusUpdate] = useState<OperacaoState>(initialState);
  const [consumo, setConsumo] = useState<OperacaoState>(initialState);
  const [apontamento, setApontamento] = useState<OperacaoState>(initialState);
  const [lista, setLista] = useState<OperacaoState>(initialState);
  const [resumo, setResumo] = useState<OperacaoState>(initialState);

  const handleGerar = async (event: React.FormEvent) => {
    event.preventDefault();
    setGeracao({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/producao/ordens/gerar/', {
        ordem: {
          numero_ordem: numeroOrdem,
          produto_final_id: Number(produtoFinalId),
          local_id: localId ? Number(localId) : null,
          quantidade_planejada: quantidadePlanejada
        },
        itens: [
          insumoId && insumoQuantidade
            ? { produto_insumo_id: Number(insumoId), quantidade: insumoQuantidade }
            : null
        ].filter(Boolean)
      });
      setGeracao({ loading: false, error: null, data: response.data });
    } catch (err) {
      setGeracao({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao gerar ordem.',
        data: null
      });
    }
  };

  const handleStatus = async (endpoint: string) => {
    setStatusUpdate({ loading: true, error: null, data: null });

    try {
      const response = await api.post(endpoint, {
        ordem_id: Number(ordemId)
      });
      setStatusUpdate({ loading: false, error: null, data: response.data });
    } catch (err) {
      setStatusUpdate({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao atualizar ordem.',
        data: null
      });
    }
  };

  const handleConsumo = async () => {
    setConsumo({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/producao/consumo/apontar/', {
        ordem_id: Number(ordemId),
        local_id: localId ? Number(localId) : null,
        itens: [
          consumoProdutoId && consumoQuantidade
            ? { produto_id: Number(consumoProdutoId), quantidade: consumoQuantidade }
            : null
        ].filter(Boolean)
      });
      setConsumo({ loading: false, error: null, data: response.data });
    } catch (err) {
      setConsumo({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao apontar consumo.',
        data: null
      });
    }
  };

  const handleApontamento = async () => {
    setApontamento({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/producao/apontar/', {
        ordem_id: Number(ordemId),
        local_id: localId ? Number(localId) : null,
        quantidade: quantidadeProduzida
      });
      setApontamento({ loading: false, error: null, data: response.data });
    } catch (err) {
      setApontamento({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao apontar produção.',
        data: null
      });
    }
  };

  const handleLista = async () => {
    setLista({ loading: true, error: null, data: null });

    try {
      const response = await api.get('/contas/producao/ordens/lista/');
      setLista({ loading: false, error: null, data: response.data });
    } catch (err) {
      setLista({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao carregar lista.',
        data: null
      });
    }
  };

  const handleResumo = async () => {
    setResumo({ loading: true, error: null, data: null });

    try {
      const response = await api.get('/contas/producao/ordens/resumo/');
      setResumo({ loading: false, error: null, data: response.data });
    } catch (err) {
      setResumo({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao carregar resumo.',
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
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '8px' }}>Operações de Produção</h2>
        <p style={{ color: '#6b7280', marginBottom: 0 }}>
          Gere ordens, aprove, inicie, finalize ou cancele e registre consumos e produção.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        <form
          onSubmit={handleGerar}
          style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Gerar Ordem</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Número</span>
            <input
              type="text"
              value={numeroOrdem}
              onChange={(event) => setNumeroOrdem(event.target.value)}
              required
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Produto Final (ID)</span>
            <input
              type="number"
              value={produtoFinalId}
              onChange={(event) => setProdutoFinalId(event.target.value)}
              required
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Local (ID)</span>
            <input
              type="number"
              value={localId}
              onChange={(event) => setLocalId(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Quantidade Planejada</span>
            <input
              type="number"
              step="0.0001"
              value={quantidadePlanejada}
              onChange={(event) => setQuantidadePlanejada(event.target.value)}
              required
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Insumo (ID)</span>
            <input
              type="number"
              value={insumoId}
              onChange={(event) => setInsumoId(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Quantidade Insumo</span>
            <input
              type="number"
              step="0.0001"
              value={insumoQuantidade}
              onChange={(event) => setInsumoQuantidade(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <button
            type="submit"
            disabled={geracao.loading}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: geracao.loading ? '#e5e7eb' : '#2563eb',
              color: geracao.loading ? '#6b7280' : 'white',
              cursor: geracao.loading ? 'not-allowed' : 'pointer'
            }}
          >
            {geracao.loading ? 'Gerando...' : 'Gerar ordem'}
          </button>
          {geracao.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{geracao.error}</p>}
          {geracao.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(geracao.data, null, 2)}
            </pre>
          )}
        </form>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Status da Ordem</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Ordem (ID)</span>
            <input
              type="number"
              value={ordemId}
              onChange={(event) => setOrdemId(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={() => handleStatus('/contas/producao/ordens/aprovar/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Aprovar</button>
            <button type="button" onClick={() => handleStatus('/contas/producao/ordens/iniciar/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Iniciar</button>
            <button type="button" onClick={() => handleStatus('/contas/producao/ordens/finalizar/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Finalizar</button>
            <button type="button" onClick={() => handleStatus('/contas/producao/ordens/cancelar/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #fee2e2', backgroundColor: '#fee2e2', color: '#b91c1c', cursor: 'pointer' }}>Cancelar</button>
          </div>
          {statusUpdate.loading && <p style={{ color: '#6b7280', marginTop: '12px' }}>Atualizando...</p>}
          {statusUpdate.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{statusUpdate.error}</p>}
          {statusUpdate.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(statusUpdate.data, null, 2)}
            </pre>
          )}
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Apontar Consumo</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Produto (ID)</span>
            <input
              type="number"
              value={consumoProdutoId}
              onChange={(event) => setConsumoProdutoId(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Quantidade</span>
            <input
              type="number"
              step="0.0001"
              value={consumoQuantidade}
              onChange={(event) => setConsumoQuantidade(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <button type="button" onClick={handleConsumo} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Apontar consumo</button>
          {consumo.loading && <p style={{ color: '#6b7280', marginTop: '12px' }}>Salvando...</p>}
          {consumo.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{consumo.error}</p>}
          {consumo.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(consumo.data, null, 2)}
            </pre>
          )}
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Apontar Produção</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Quantidade Produzida</span>
            <input
              type="number"
              step="0.0001"
              value={quantidadeProduzida}
              onChange={(event) => setQuantidadeProduzida(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <button type="button" onClick={handleApontamento} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Apontar produção</button>
          {apontamento.loading && <p style={{ color: '#6b7280', marginTop: '12px' }}>Salvando...</p>}
          {apontamento.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{apontamento.error}</p>}
          {apontamento.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(apontamento.data, null, 2)}
            </pre>
          )}
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Consultas</h3>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={handleLista} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Lista de ordens</button>
            <button type="button" onClick={handleResumo} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Resumo por período</button>
          </div>
          {lista.loading && <p style={{ color: '#6b7280', marginTop: '12px' }}>Carregando...</p>}
          {lista.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{lista.error}</p>}
          {lista.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(lista.data, null, 2)}
            </pre>
          )}
          {resumo.loading && <p style={{ color: '#6b7280', marginTop: '12px' }}>Carregando resumo...</p>}
          {resumo.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{resumo.error}</p>}
          {resumo.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(resumo.data, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default OperacoesProducaoPage;
