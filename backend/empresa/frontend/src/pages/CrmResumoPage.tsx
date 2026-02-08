import React, { useState } from 'react';
import api from '../services/api';

interface ResumoState {
  loading: boolean;
  error: string | null;
  data: unknown;
}

const initialResumo: ResumoState = {
  loading: false,
  error: null,
  data: null
};

const CrmResumoPage: React.FC = () => {
  const [funilResumo, setFunilResumo] = useState<ResumoState>(initialResumo);
  const [atividadesPendentes, setAtividadesPendentes] = useState<ResumoState>(initialResumo);
  const [oportunidadesResumo, setOportunidadesResumo] = useState<ResumoState>(initialResumo);

  const fetchResumo = async (
    endpoint: string,
    setter: React.Dispatch<React.SetStateAction<ResumoState>>
  ) => {
    setter({ loading: true, error: null, data: null });
    try {
      const response = await api.get(endpoint);
      setter({ loading: false, error: null, data: response.data });
    } catch (err) {
      setter({
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
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '8px' }}>Resumo CRM</h2>
        <p style={{ color: '#6b7280', marginBottom: 0 }}>
          Consulte rapidamente os indicadores do funil, atividades pendentes e oportunidades.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Resumo do Funil</h3>
          <button
            type="button"
            onClick={() => fetchResumo('/contas/crm/funil/resumo/', setFunilResumo)}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: 'white',
              cursor: 'pointer',
              marginBottom: '12px'
            }}
          >
            Atualizar
          </button>
          {funilResumo.loading && <p style={{ color: '#6b7280' }}>Carregando...</p>}
          {funilResumo.error && <p style={{ color: '#b91c1c' }}>{funilResumo.error}</p>}
          {funilResumo.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
              {JSON.stringify(funilResumo.data, null, 2)}
            </pre>
          )}
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Atividades Pendentes</h3>
          <button
            type="button"
            onClick={() => fetchResumo('/contas/crm/atividades/pendentes/', setAtividadesPendentes)}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: 'white',
              cursor: 'pointer',
              marginBottom: '12px'
            }}
          >
            Atualizar
          </button>
          {atividadesPendentes.loading && <p style={{ color: '#6b7280' }}>Carregando...</p>}
          {atividadesPendentes.error && <p style={{ color: '#b91c1c' }}>{atividadesPendentes.error}</p>}
          {atividadesPendentes.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
              {JSON.stringify(atividadesPendentes.data, null, 2)}
            </pre>
          )}
        </div>

        <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Resumo de Oportunidades</h3>
          <button
            type="button"
            onClick={() => fetchResumo('/contas/crm/oportunidades/resumo/', setOportunidadesResumo)}
            style={{
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              backgroundColor: 'white',
              cursor: 'pointer',
              marginBottom: '12px'
            }}
          >
            Atualizar
          </button>
          {oportunidadesResumo.loading && <p style={{ color: '#6b7280' }}>Carregando...</p>}
          {oportunidadesResumo.error && <p style={{ color: '#b91c1c' }}>{oportunidadesResumo.error}</p>}
          {oportunidadesResumo.data && (
            <pre style={{ fontSize: '0.75rem', backgroundColor: '#f8fafc', padding: '12px', borderRadius: '8px', overflowX: 'auto' }}>
              {JSON.stringify(oportunidadesResumo.data, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default CrmResumoPage;
