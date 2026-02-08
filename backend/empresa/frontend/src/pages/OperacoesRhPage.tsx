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

const OperacoesRhPage: React.FC = () => {
  const [competencia, setCompetencia] = useState('');
  const [folhaId, setFolhaId] = useState('');
  const [gerarFolha, setGerarFolha] = useState<OperacaoState>(initialState);
  const [fecharFolha, setFecharFolha] = useState<OperacaoState>(initialState);
  const [resumoBeneficios, setResumoBeneficios] = useState<OperacaoState>(initialState);

  const handleGerarFolha = async (event: React.FormEvent) => {
    event.preventDefault();
    setGerarFolha({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/rh/folha/gerar/', {
        competencia
      });
      setGerarFolha({ loading: false, error: null, data: response.data });
    } catch (err) {
      setGerarFolha({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao gerar folha.',
        data: null
      });
    }
  };

  const handleFecharFolha = async () => {
    setFecharFolha({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/rh/folha/fechar/', {
        folha_id: Number(folhaId)
      });
      setFecharFolha({ loading: false, error: null, data: response.data });
    } catch (err) {
      setFecharFolha({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao fechar folha.',
        data: null
      });
    }
  };

  const handleResumoBeneficios = async () => {
    setResumoBeneficios({ loading: true, error: null, data: null });

    try {
      const response = await api.get('/contas/rh/beneficios/resumo/');
      setResumoBeneficios({ loading: false, error: null, data: response.data });
    } catch (err) {
      setResumoBeneficios({
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
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '8px' }}>Operações de RH</h2>
        <p style={{ color: '#6b7280', marginBottom: 0 }}>
          Gere e feche folhas de pagamento e consulte o resumo de benefícios.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        <form
          onSubmit={handleGerarFolha}
          style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Gerar Folha</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Competência</span>
            <input
              type="date"
              value={competencia}
              onChange={(event) => setCompetencia(event.target.value)}
              required
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <button
            type="submit"
            disabled={gerarFolha.loading}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: gerarFolha.loading ? '#e5e7eb' : '#2563eb',
              color: gerarFolha.loading ? '#6b7280' : 'white',
              cursor: gerarFolha.loading ? 'not-allowed' : 'pointer'
            }}
          >
            {gerarFolha.loading ? 'Gerando...' : 'Gerar folha'}
          </button>
          {gerarFolha.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{gerarFolha.error}</p>}
          {gerarFolha.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(gerarFolha.data, null, 2)}
            </pre>
          )}
        </form>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Fechar Folha</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Folha (ID)</span>
            <input
              type="number"
              value={folhaId}
              onChange={(event) => setFolhaId(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <button
            type="button"
            onClick={handleFecharFolha}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: 'white',
              cursor: 'pointer'
            }}
          >
            Fechar folha
          </button>
          {fecharFolha.loading && <p style={{ color: '#6b7280', marginTop: '12px' }}>Fechando...</p>}
          {fecharFolha.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{fecharFolha.error}</p>}
          {fecharFolha.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(fecharFolha.data, null, 2)}
            </pre>
          )}
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Resumo de Benefícios</h3>
          <button
            type="button"
            onClick={handleResumoBeneficios}
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
          {resumoBeneficios.loading && <p style={{ color: '#6b7280' }}>Carregando...</p>}
          {resumoBeneficios.error && <p style={{ color: '#b91c1c' }}>{resumoBeneficios.error}</p>}
          {resumoBeneficios.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
              {JSON.stringify(resumoBeneficios.data, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default OperacoesRhPage;
