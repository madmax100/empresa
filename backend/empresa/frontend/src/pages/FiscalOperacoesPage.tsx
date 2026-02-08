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

const FiscalOperacoesPage: React.FC = () => {
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [geracao, setGeracao] = useState<OperacaoState>(initialState);
  const [resumo, setResumo] = useState<OperacaoState>(initialState);

  const handleGerar = async (event: React.FormEvent) => {
    event.preventDefault();
    setGeracao({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/fiscal/apuracao/gerar/', {
        data_inicio: dataInicio,
        data_fim: dataFim
      });
      setGeracao({ loading: false, error: null, data: response.data });
    } catch (err) {
      setGeracao({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao gerar apuração.',
        data: null
      });
    }
  };

  const handleResumo = async () => {
    setResumo({ loading: true, error: null, data: null });

    try {
      const response = await api.get('/contas/fiscal/apuracao/resumo/');
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
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '8px' }}>Operações Fiscais</h2>
        <p style={{ color: '#6b7280', marginBottom: 0 }}>
          Gere apurações fiscais por período e consulte o resumo consolidado.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        <form
          onSubmit={handleGerar}
          style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Gerar Apuração</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Data Início</span>
            <input
              type="date"
              value={dataInicio}
              onChange={(event) => setDataInicio(event.target.value)}
              required
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Data Fim</span>
            <input
              type="date"
              value={dataFim}
              onChange={(event) => setDataFim(event.target.value)}
              required
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
            {geracao.loading ? 'Gerando...' : 'Gerar apuração'}
          </button>
          {geracao.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{geracao.error}</p>}
          {geracao.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(geracao.data, null, 2)}
            </pre>
          )}
        </form>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Resumo de Apurações</h3>
          <button
            type="button"
            onClick={handleResumo}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: 'white',
              cursor: 'pointer',
              marginBottom: '12px'
            }}
          >
            Atualizar resumo
          </button>
          {resumo.loading && <p style={{ color: '#6b7280' }}>Carregando...</p>}
          {resumo.error && <p style={{ color: '#b91c1c' }}>{resumo.error}</p>}
          {resumo.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
              {JSON.stringify(resumo.data, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default FiscalOperacoesPage;
