import React, { useState } from 'react';

interface TestResult {
  status: number;
  sucesso: boolean;
  dados: any;
  erro: string | null;
}

interface TestResults {
  [key: string]: TestResult;
}

const TestApiConnection: React.FC = () => {
  const [resultados, setResultados] = useState<TestResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testarEndpoints = async () => {
    setLoading(true);
    setError(null);
    setResultados(null);

    const endpoints = [
      {
        nome: 'Estoque Atual',
        url: 'http://127.0.0.1:8000/contas/estoque-controle/estoque_atual/?limite=5'
      },
      {
        nome: 'Estoque Crítico',
        url: 'http://127.0.0.1:8000/contas/estoque-controle/estoque_critico/?limite=5'
      },
      {
        nome: 'Produtos Movimentados',
        url: 'http://127.0.0.1:8000/contas/estoque-controle/produtos_mais_movimentados/?limite=5'
      }
    ];

    const testes: TestResults = {};

    for (const endpoint of endpoints) {
      try {
        console.log(`🔍 Testando: ${endpoint.nome} - ${endpoint.url}`);
        
        const response = await fetch(endpoint.url);
        
        console.log(`📊 Status ${endpoint.nome}:`, response.status, response.statusText);
        
        if (response.ok) {
          const data = await response.json();
          testes[endpoint.nome] = {
            status: response.status,
            sucesso: true,
            dados: data,
            erro: null
          };
          console.log(`✅ ${endpoint.nome} - Dados:`, data);
        } else {
          const errorText = await response.text();
          testes[endpoint.nome] = {
            status: response.status,
            sucesso: false,
            dados: null,
            erro: errorText
          };
          console.log(`❌ ${endpoint.nome} - Erro:`, errorText);
        }
      } catch (err) {
        testes[endpoint.nome] = {
          status: 0,
          sucesso: false,
          dados: null,
          erro: err instanceof Error ? err.message : 'Erro desconhecido'
        };
        console.log(`💥 ${endpoint.nome} - Exceção:`, err);
      }
    }

    setResultados(testes);
    setLoading(false);
  };

  return (
    <div style={{ 
      padding: '24px', 
      backgroundColor: '#f8fafc', 
      borderRadius: '8px',
      margin: '24px',
      border: '2px solid #e2e8f0'
    }}>
      <h2 style={{ 
        fontSize: '1.5rem', 
        fontWeight: '600', 
        color: '#111827', 
        marginBottom: '16px' 
      }}>
        🧪 Teste de Conexão com API
      </h2>
      
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>
        Este componente testa a conectividade com os endpoints da API de estoque.
      </p>

      <button
        onClick={testarEndpoints}
        disabled={loading}
        style={{
          padding: '12px 24px',
          backgroundColor: loading ? '#9ca3af' : '#2563eb',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          fontSize: '1rem',
          fontWeight: '500',
          cursor: loading ? 'not-allowed' : 'pointer',
          marginBottom: '24px'
        }}
      >
        {loading ? '🔄 Testando...' : '🚀 Testar Endpoints'}
      </button>

      {resultados && (
        <div>
          <h3 style={{ 
            fontSize: '1.25rem', 
            fontWeight: '600', 
            color: '#111827', 
            marginBottom: '16px' 
          }}>
            📋 Resultados dos Testes
          </h3>
          
          {Object.entries(resultados).map(([nome, resultado]: [string, TestResult]) => (
            <div
              key={nome}
              style={{
                backgroundColor: resultado.sucesso ? '#f0fdf4' : '#fef2f2',
                border: `1px solid ${resultado.sucesso ? '#bbf7d0' : '#fecaca'}`,
                borderRadius: '6px',
                padding: '16px',
                marginBottom: '16px'
              }}
            >
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                marginBottom: '8px' 
              }}>
                <span style={{ fontSize: '1.5rem', marginRight: '8px' }}>
                  {resultado.sucesso ? '✅' : '❌'}
                </span>
                <strong style={{ 
                  color: resultado.sucesso ? '#166534' : '#b91c1c',
                  fontSize: '1.125rem'
                }}>
                  {nome}
                </strong>
                <span style={{ 
                  marginLeft: 'auto',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  backgroundColor: resultado.sucesso ? '#dcfce7' : '#fee2e2',
                  color: resultado.sucesso ? '#166534' : '#b91c1c'
                }}>
                  Status: {resultado.status}
                </span>
              </div>
              
              {resultado.erro && (
                <div style={{ 
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '4px',
                  padding: '8px',
                  fontSize: '0.875rem',
                  color: '#b91c1c',
                  marginBottom: '8px'
                }}>
                  <strong>Erro:</strong> {resultado.erro}
                </div>
              )}
              
              {resultado.dados && (
                <div style={{ 
                  backgroundColor: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '4px',
                  padding: '8px',
                  fontSize: '0.875rem',
                  overflow: 'auto',
                  maxHeight: '200px'
                }}>
                  <strong>Dados recebidos:</strong>
                  <pre style={{ 
                    margin: '8px 0 0 0',
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    lineHeight: '1.2'
                  }}>
                    {JSON.stringify(resultado.dados, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {error && (
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '6px',
          padding: '16px',
          color: '#b91c1c'
        }}>
          <strong>❌ Erro geral:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default TestApiConnection;
