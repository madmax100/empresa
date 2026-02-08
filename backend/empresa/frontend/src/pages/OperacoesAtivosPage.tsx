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

const OperacoesAtivosPage: React.FC = () => {
  const [competencia, setCompetencia] = useState('');
  const [ativoId, setAtivoId] = useState('');
  const [tipo, setTipo] = useState('');
  const [custoPrevisto, setCustoPrevisto] = useState('');
  const [manutencaoId, setManutencaoId] = useState('');
  const [depreciacao, setDepreciacao] = useState<OperacaoState>(initialState);
  const [resumo, setResumo] = useState<OperacaoState>(initialState);
  const [abrirManutencao, setAbrirManutencao] = useState<OperacaoState>(initialState);
  const [statusManutencao, setStatusManutencao] = useState<OperacaoState>(initialState);

  const handleDepreciacao = async (event: React.FormEvent) => {
    event.preventDefault();
    setDepreciacao({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/ativos/depreciacao/gerar/', {
        competencia
      });
      setDepreciacao({ loading: false, error: null, data: response.data });
    } catch (err) {
      setDepreciacao({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao gerar depreciação.',
        data: null
      });
    }
  };

  const handleResumo = async () => {
    setResumo({ loading: true, error: null, data: null });

    try {
      const response = await api.get('/contas/ativos/resumo/');
      setResumo({ loading: false, error: null, data: response.data });
    } catch (err) {
      setResumo({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao carregar resumo.',
        data: null
      });
    }
  };

  const handleAbrirManutencao = async (event: React.FormEvent) => {
    event.preventDefault();
    setAbrirManutencao({ loading: true, error: null, data: null });

    try {
      const response = await api.post('/contas/ativos/manutencao/abrir/', {
        ativo_id: Number(ativoId),
        tipo,
        custo_previsto: custoPrevisto
      });
      setAbrirManutencao({ loading: false, error: null, data: response.data });
    } catch (err) {
      setAbrirManutencao({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao abrir manutenção.',
        data: null
      });
    }
  };

  const handleStatusManutencao = async (endpoint: string) => {
    setStatusManutencao({ loading: true, error: null, data: null });

    try {
      const response = await api.post(endpoint, {
        manutencao_id: Number(manutencaoId)
      });
      setStatusManutencao({ loading: false, error: null, data: response.data });
    } catch (err) {
      setStatusManutencao({
        loading: false,
        error: err instanceof Error ? err.message : 'Erro ao atualizar manutenção.',
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
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '8px' }}>Operações de Ativos</h2>
        <p style={{ color: '#6b7280', marginBottom: 0 }}>
          Gere depreciação mensal, acompanhe resumo de ativos e controle manutenções.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        <form
          onSubmit={handleDepreciacao}
          style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Gerar Depreciação</h3>
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
            disabled={depreciacao.loading}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: depreciacao.loading ? '#e5e7eb' : '#2563eb',
              color: depreciacao.loading ? '#6b7280' : 'white',
              cursor: depreciacao.loading ? 'not-allowed' : 'pointer'
            }}
          >
            {depreciacao.loading ? 'Gerando...' : 'Gerar depreciação'}
          </button>
          {depreciacao.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{depreciacao.error}</p>}
          {depreciacao.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(depreciacao.data, null, 2)}
            </pre>
          )}
        </form>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Resumo de Ativos</h3>
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

        <form
          onSubmit={handleAbrirManutencao}
          style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Abrir Manutenção</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Ativo (ID)</span>
            <input
              type="number"
              value={ativoId}
              onChange={(event) => setAtivoId(event.target.value)}
              required
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Tipo</span>
            <input
              type="text"
              value={tipo}
              onChange={(event) => setTipo(event.target.value)}
              required
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Custo Previsto</span>
            <input
              type="number"
              step="0.01"
              value={custoPrevisto}
              onChange={(event) => setCustoPrevisto(event.target.value)}
              required
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <button
            type="submit"
            disabled={abrirManutencao.loading}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: abrirManutencao.loading ? '#e5e7eb' : '#2563eb',
              color: abrirManutencao.loading ? '#6b7280' : 'white',
              cursor: abrirManutencao.loading ? 'not-allowed' : 'pointer'
            }}
          >
            {abrirManutencao.loading ? 'Abrindo...' : 'Abrir manutenção'}
          </button>
          {abrirManutencao.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{abrirManutencao.error}</p>}
          {abrirManutencao.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(abrirManutencao.data, null, 2)}
            </pre>
          )}
        </form>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Status da Manutenção</h3>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>Manutenção (ID)</span>
            <input
              type="number"
              value={manutencaoId}
              onChange={(event) => setManutencaoId(event.target.value)}
              style={{ padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </label>
          <div style={{ display: 'grid', gap: '8px' }}>
            <button type="button" onClick={() => handleStatusManutencao('/contas/ativos/manutencao/finalizar/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', backgroundColor: 'white', cursor: 'pointer' }}>Finalizar</button>
            <button type="button" onClick={() => handleStatusManutencao('/contas/ativos/manutencao/cancelar/')} style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #fee2e2', backgroundColor: '#fee2e2', color: '#b91c1c', cursor: 'pointer' }}>Cancelar</button>
          </div>
          {statusManutencao.loading && <p style={{ color: '#6b7280', marginTop: '12px' }}>Atualizando...</p>}
          {statusManutencao.error && <p style={{ color: '#b91c1c', marginTop: '12px' }}>{statusManutencao.error}</p>}
          {statusManutencao.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '12px', overflowX: 'auto' }}>
              {JSON.stringify(statusManutencao.data, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default OperacoesAtivosPage;
