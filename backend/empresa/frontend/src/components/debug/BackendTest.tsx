// Backend Test Component
// Simple component to test backend connectivity and stock endpoints

import React, { useState, useEffect } from 'react';
import stockService from '../../services/stockService';

const BackendTest: React.FC = () => {
  const [testResults, setTestResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);

  const runTests = async () => {
    setLoading(true);
    setTestResults([]);
    
    const results: any[] = [];

    // Test 1: Basic connectivity
    console.log('🧪 Testing backend connectivity...');
    results.push({ test: 'Backend Connectivity', status: 'running', message: 'Testing...' });
    setTestResults([...results]);

    try {
      const connectionResult = await stockService.testConnection();
      results[0] = {
        test: 'Backend Connectivity',
        status: connectionResult.success ? 'success' : 'error',
        message: connectionResult.success ? 'Backend is reachable' : connectionResult.error,
        data: connectionResult.data
      };
      setBackendConnected(connectionResult.success);
      setTestResults([...results]);
    } catch (error) {
      results[0] = {
        test: 'Backend Connectivity',
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error'
      };
      setBackendConnected(false);
      setTestResults([...results]);
    }

    // Only continue if backend is connected
    if (!backendConnected && results[0].status !== 'success') {
      setLoading(false);
      return;
    }

    // Test 2: Estoque Atual endpoint
    console.log('🧪 Testing estoque atual endpoint...');
    results.push({ test: 'Estoque Atual', status: 'running', message: 'Testing...' });
    setTestResults([...results]);

    try {
      const estoqueResult = await stockService.getEstoqueAtual({ limite: 5 });
      results[1] = {
        test: 'Estoque Atual',
        status: estoqueResult.success ? 'success' : 'error',
        message: estoqueResult.success 
          ? `Found ${estoqueResult.data?.estoque?.length || 0} products` 
          : estoqueResult.error,
        data: estoqueResult.data
      };
      setTestResults([...results]);
    } catch (error) {
      results[1] = {
        test: 'Estoque Atual',
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error'
      };
      setTestResults([...results]);
    }

    // Test 3: Estoque Crítico endpoint
    console.log('🧪 Testing estoque crítico endpoint...');
    results.push({ test: 'Estoque Crítico', status: 'running', message: 'Testing...' });
    setTestResults([...results]);

    try {
      const criticoResult = await stockService.getEstoqueCritico({ limite: 5 });
      results[2] = {
        test: 'Estoque Crítico',
        status: criticoResult.success ? 'success' : 'error',
        message: criticoResult.success 
          ? `Found ${criticoResult.data?.produtos?.length || 0} critical products` 
          : criticoResult.error,
        data: criticoResult.data
      };
      setTestResults([...results]);
    } catch (error) {
      results[2] = {
        test: 'Estoque Crítico',
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error'
      };
      setTestResults([...results]);
    }

    // Test 4: Produtos Mais Movimentados endpoint
    console.log('🧪 Testing produtos movimentados endpoint...');
    results.push({ test: 'Produtos Movimentados', status: 'running', message: 'Testing...' });
    setTestResults([...results]);

    try {
      const movimentadosResult = await stockService.getProdutosMaisMovimentados({ limite: 5 });
      results[3] = {
        test: 'Produtos Movimentados',
        status: movimentadosResult.success ? 'success' : 'error',
        message: movimentadosResult.success 
          ? `Found ${movimentadosResult.data?.produtos_mais_movimentados?.length || 0} most moved products` 
          : movimentadosResult.error,
        data: movimentadosResult.data
      };
      setTestResults([...results]);
    } catch (error) {
      results[3] = {
        test: 'Produtos Movimentados',
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error'
      };
      setTestResults([...results]);
    }

    setLoading(false);
  };

  useEffect(() => {
    runTests();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'running': return '🔄';
      default: return '⏳';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#166534';
      case 'error': return '#b91c1c';
      case 'running': return '#2563eb';
      default: return '#6b7280';
    }
  };

  return (
    <div style={{ padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ 
          fontSize: '2rem', 
          fontWeight: '700', 
          color: '#111827', 
          marginBottom: '8px' 
        }}>
          🧪 Backend Test Suite
        </h1>
        <p style={{ 
          fontSize: '1rem', 
          color: '#6b7280', 
          marginBottom: '32px' 
        }}>
          Testing stock control backend endpoints and connectivity
        </p>

        <div style={{ 
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '24px',
          marginBottom: '24px'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '24px'
          }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827' }}>
              Test Results
            </h2>
            <button
              onClick={runTests}
              disabled={loading}
              style={{
                padding: '8px 16px',
                backgroundColor: loading ? '#9ca3af' : '#2563eb',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? '🔄 Running Tests...' : '🔄 Run Tests'}
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {testResults.map((result, index) => (
              <div key={index} style={{
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '16px',
                backgroundColor: result.status === 'success' ? '#f0fdf4' : 
                                result.status === 'error' ? '#fef2f2' : '#f8fafc'
              }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '12px',
                  marginBottom: '8px'
                }}>
                  <span style={{ fontSize: '1.2rem' }}>
                    {getStatusIcon(result.status)}
                  </span>
                  <h3 style={{ 
                    fontSize: '1rem', 
                    fontWeight: '600', 
                    color: getStatusColor(result.status),
                    margin: 0
                  }}>
                    {result.test}
                  </h3>
                </div>
                
                <div style={{ 
                  fontSize: '0.875rem', 
                  color: '#374151',
                  marginBottom: result.data ? '12px' : '0'
                }}>
                  {result.message}
                </div>

                {result.data && (
                  <details style={{ fontSize: '0.75rem' }}>
                    <summary style={{ 
                      cursor: 'pointer', 
                      color: '#6b7280',
                      marginBottom: '8px'
                    }}>
                      View Response Data
                    </summary>
                    <pre style={{
                      backgroundColor: '#f3f4f6',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px',
                      padding: '12px',
                      overflow: 'auto',
                      maxHeight: '200px',
                      fontSize: '0.7rem',
                      color: '#374151'
                    }}>
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            ))}

            {testResults.length === 0 && !loading && (
              <div style={{ 
                textAlign: 'center', 
                padding: '48px',
                color: '#6b7280'
              }}>
                <div style={{ fontSize: '2rem', marginBottom: '16px' }}>🧪</div>
                <div>Click "Run Tests" to start testing the backend</div>
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div style={{ 
          backgroundColor: '#eff6ff',
          border: '1px solid #bfdbfe',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <h3 style={{ 
            fontSize: '1.125rem', 
            fontWeight: '600', 
            color: '#1e40af',
            marginBottom: '12px'
          }}>
            💡 Troubleshooting
          </h3>
          
          <div style={{ fontSize: '0.875rem', color: '#1e40af', lineHeight: '1.6' }}>
            <p><strong>If tests fail:</strong></p>
            <ol style={{ paddingLeft: '20px' }}>
              <li>Make sure the Django backend is running:
                <br />
                <code style={{ 
                  backgroundColor: '#1f2937', 
                  color: '#f9fafb', 
                  padding: '2px 6px', 
                  borderRadius: '3px',
                  fontSize: '0.8rem'
                }}>
                  python manage.py runserver
                </code>
              </li>
              <li>Check if the stock control app is installed in Django</li>
              <li>Verify the URLs are configured correctly</li>
              <li>Check for CORS issues</li>
            </ol>
            
            <p style={{ marginTop: '16px' }}>
              <strong>Expected backend URL:</strong> <code>http://127.0.0.1:8000</code>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BackendTest;