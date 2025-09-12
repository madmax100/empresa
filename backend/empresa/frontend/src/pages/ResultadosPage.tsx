import React, { useState } from 'react';
import ResultadosEmpresariais from '../components/dashboard/ResultadosEmpresariais';
import PosicaoFinanceira from '../components/dashboard/PosicaoFinanceira';

const ResultadosPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'resultados' | 'posicao'>('resultados');

  return (
    <div style={{ padding: '0', margin: '0' }}>
      {/* Sistema de Abas */}
      <div style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '0 24px'
      }}>
        <div style={{
          display: 'flex',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <button
            onClick={() => setActiveTab('resultados')}
            style={{
              padding: '16px 24px',
              border: 'none',
              background: 'none',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: activeTab === 'resultados' ? '#3b82f6' : '#6b7280',
              borderBottom: activeTab === 'resultados' ? '2px solid #3b82f6' : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            📊 Resultados Empresariais
          </button>
          <button
            onClick={() => setActiveTab('posicao')}
            style={{
              padding: '16px 24px',
              border: 'none',
              background: 'none',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: activeTab === 'posicao' ? '#3b82f6' : '#6b7280',
              borderBottom: activeTab === 'posicao' ? '2px solid #3b82f6' : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            💼 Posição Financeira
          </button>
        </div>
      </div>

      {/* Conteúdo das Abas */}
      <div>
        {activeTab === 'resultados' && <ResultadosEmpresariais />}
        {activeTab === 'posicao' && <PosicaoFinanceira />}
      </div>
    </div>
  );
};

export default ResultadosPage;
