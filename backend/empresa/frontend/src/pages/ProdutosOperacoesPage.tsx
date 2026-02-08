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

const ProdutosOperacoesPage: React.FC = () => {
  const [produtoId, setProdutoId] = useState('');
  const [tabelaId, setTabelaId] = useState('');
  const [clienteId, setClienteId] = useState('');
  const [quantidade, setQuantidade] = useState('');
  const [dataBase, setDataBase] = useState('');
  const [unidadeOrigem, setUnidadeOrigem] = useState('');
  const [unidadeDestino, setUnidadeDestino] = useState('');
  const [alertas, setAlertas] = useState<OperacaoState>(initialState);
  const [ficha, setFicha] = useState<OperacaoState>(initialState);
  const [composicao, setComposicao] = useState<OperacaoState>(initialState);
  const [preco, setPreco] = useState<OperacaoState>(initialState);
  const [conversao, setConversao] = useState<OperacaoState>(initialState);
  const [substitutos, setSubstitutos] = useState<OperacaoState>(initialState);
  const [historico, setHistorico] = useState<OperacaoState>(initialState);

  const handleGet = async (endpoint: string, setter: React.Dispatch<React.SetStateAction<OperacaoState>>) => {
    setter({ loading: true, error: null, data: null });
    try {
      const response = await api.get(endpoint);
      setter({ loading: false, error: null, data: response.data });
    } catch (err) {
      setter({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao carregar dados.',
        data: null
      });
    }
  };

  const handlePreco = async (event: React.FormEvent) => {
    event.preventDefault();
    setPreco({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/produtos/preco/', {
        produto_id: Number(produtoId),
        tabela_id: Number(tabelaId),
        cliente_id: Number(clienteId),
        quantidade: Number(quantidade || 0),
        data_base: dataBase || null
      });
      setPreco({ loading: false, error: null, data: response.data });
    } catch (err) {
      setPreco({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao calcular preço.',
        data: null
      });
    }
  };

  const handleConversao = async (event: React.FormEvent) => {
    event.preventDefault();
    setConversao({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/produtos/conversao/', {
        produto_id: Number(produtoId),
        unidade_origem: unidadeOrigem,
        unidade_destino: unidadeDestino,
        quantidade: Number(quantidade || 0)
      });
      setConversao({ loading: false, error: null, data: response.data });
    } catch (err) {
      setConversao({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao converter unidade.',
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
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '8px' }}>Operações de Produtos</h2>
        <p style={{ color: '#6b7280', marginBottom: 0 }}>
          Consulte alertas, ficha técnica, composição, preços e conversões de unidade.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Consultas rápidas</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Produto (ID)</span>
            <input
              type="number"
              value={produtoId}
              onChange={(event) => setProdutoId(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={() => handleGet('/contas/produtos/alertas/', setAlertas)} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Alertas operacionais</button>
            <button type="button" onClick={() => handleGet(`/contas/produtos/ficha/${produtoId}/`, setFicha)} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Ficha do produto</button>
            <button type="button" onClick={() => handleGet(`/contas/produtos/composicao/${produtoId}/`, setComposicao)} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Resumo composição</button>
            <button type="button" onClick={() => handleGet(`/contas/produtos/substitutos/${produtoId}/`, setSubstitutos)} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Substitutos</button>
            <button type="button" onClick={() => handleGet(`/contas/produtos/historico-preco/${produtoId}/`, setHistorico)} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Histórico de preço</button>
          </div>
          {[{ label: 'Alertas', state: alertas }, { label: 'Ficha', state: ficha }, { label: 'Composição', state: composicao }, { label: 'Substitutos', state: substitutos }, { label: 'Histórico', state: historico }].map(({ label, state }) => (
            state.data ? (
              <div key={label} style={{ marginTop: '12px' }}>
                <p style={{ fontWeight: 600, marginBottom: '6px' }}>{label}</p>
                <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
                  {JSON.stringify(state.data, null, 2)}
                </pre>
              </div>
            ) : null
          ))}
        </div>

        <form onSubmit={handlePreco} style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Preço Efetivo</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Tabela (ID)</span>
            <input type="number" value={tabelaId} onChange={(event) => setTabelaId(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Cliente (ID)</span>
            <input type="number" value={clienteId} onChange={(event) => setClienteId(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Quantidade</span>
            <input type="number" step="0.01" value={quantidade} onChange={(event) => setQuantidade(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Data Base</span>
            <input type="date" value={dataBase} onChange={(event) => setDataBase(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <button type="submit" style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: '#2563eb', color: 'white', cursor: 'pointer' }}>Calcular preço</button>
          {preco.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{preco.error}</p>}
          {preco.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(preco.data, null, 2)}
            </pre>
          )}
        </form>

        <form onSubmit={handleConversao} style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Conversão de Unidade</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Unidade Origem</span>
            <input type="text" value={unidadeOrigem} onChange={(event) => setUnidadeOrigem(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Unidade Destino</span>
            <input type="text" value={unidadeDestino} onChange={(event) => setUnidadeDestino(event.target.value)} style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }} />
          </label>
          <button type="submit" style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: '#2563eb', color: 'white', cursor: 'pointer' }}>Calcular conversão</button>
          {conversao.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{conversao.error}</p>}
          {conversao.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(conversao.data, null, 2)}
            </pre>
          )}
        </form>
      </div>
    </div>
  );
};

export default ProdutosOperacoesPage;
