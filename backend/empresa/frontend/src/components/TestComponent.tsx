import React from 'react';

const TestComponent: React.FC = () => {
  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#ffffff',
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      flexDirection: 'column'
    }}>
      <h1 style={{ color: '#1e40af', fontSize: '2rem', marginBottom: '20px' }}>
        🚀 Dashboard Funcionando!
      </h1>
      <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
        O sistema React está carregando corretamente.
      </p>
      <div style={{
        backgroundColor: '#1e40af',
        color: 'white',
        padding: '10px 20px',
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        ✅ CSS Configurado
      </div>
    </div>
  );
};

export default TestComponent;
