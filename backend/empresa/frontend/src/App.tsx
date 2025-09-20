import { useState } from 'react';
import FluxoCaixaDashboard from './components/dashboard/FluxoCaixaDashboard';
import FluxoLucroDashboard from './components/dashboard/FluxoLucroDashboard';
import EstoqueDashboard from './components/dashboard/EstoqueDashboard';
import GerenciaDashboard from './components/dashboard/GerenciaDashboard';
import ContratosPage from './pages/ContratosPage';
import ResultadosPage from './pages/ResultadosPage';
import CustosFixosPage from './pages/CustosFixosPage';
import CustosVariaveisPage from './pages/CustosVariaveisPage';
import { FaturamentoPage } from './pages/FaturamentoPage';
import TestApiConnection from './components/TestApiConnection';
import './App.css';

function App() {
  const [activePanel, setActivePanel] = useState<'fluxo-realizado' | 'fluxo-lucro' | 'estoque' | 'gerencia' | 'contratos' | 'resultados' | 'custos-fixos' | 'custos-variaveis' | 'faturamento' | 'test-api'>('fluxo-realizado');

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header de Navegação */}
      <div style={{
        backgroundColor: 'white',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '0 20px',
        marginBottom: '0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: '60px'
        }}>
          <h1 style={{
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            🏢 Sistema Financeiro Empresarial
          </h1>

          <div style={{
            display: 'flex',
            gap: '8px',
            backgroundColor: '#f3f4f6',
            padding: '4px',
            borderRadius: '8px'
          }}>
            <button
              onClick={() => setActivePanel('fluxo-realizado')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'fluxo-realizado' ? '#3b82f6' : 'transparent',
                color: activePanel === 'fluxo-realizado' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📊 Fluxo de Caixa Realizado
            </button>
            
            <button
              onClick={() => setActivePanel('fluxo-lucro')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'fluxo-lucro' ? '#3b82f6' : 'transparent',
                color: activePanel === 'fluxo-lucro' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              💰 Fluxo de Caixa Previsto
            </button>

            <button
              onClick={() => setActivePanel('estoque')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'estoque' ? '#3b82f6' : 'transparent',
                color: activePanel === 'estoque' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📦 Controle de Estoque
            </button>

            <button
              onClick={() => setActivePanel('gerencia')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'gerencia' ? '#3b82f6' : 'transparent',
                color: activePanel === 'gerencia' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              🏢 Painel de Gerência
            </button>

            <button
              onClick={() => setActivePanel('contratos')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'contratos' ? '#3b82f6' : 'transparent',
                color: activePanel === 'contratos' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📋 Contratos de Locação
            </button>

            <button
              onClick={() => setActivePanel('resultados')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'resultados' ? '#3b82f6' : 'transparent',
                color: activePanel === 'resultados' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📈 Resultados do Período
            </button>

            <button
              onClick={() => setActivePanel('custos-fixos')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'custos-fixos' ? '#3b82f6' : 'transparent',
                color: activePanel === 'custos-fixos' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              💳 Custos Fixos
            </button>

            <button
              onClick={() => setActivePanel('custos-variaveis')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'custos-variaveis' ? '#3b82f6' : 'transparent',
                color: activePanel === 'custos-variaveis' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              💰 Custos Variáveis
            </button>

            <button
              onClick={() => setActivePanel('faturamento')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'faturamento' ? '#3b82f6' : 'transparent',
                color: activePanel === 'faturamento' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              🧾 Faturamento
            </button>

            <button
              onClick={() => setActivePanel('test-api')}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: activePanel === 'test-api' ? '#3b82f6' : 'transparent',
                color: activePanel === 'test-api' ? 'white' : '#6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              🧪 Teste API
            </button>
          </div>
        </div>
      </div>

      {/* Conteúdo dos Painéis */}
      <div>
        {activePanel === 'fluxo-realizado' && <FluxoCaixaDashboard />}
        {activePanel === 'fluxo-lucro' && <FluxoLucroDashboard />}
        {activePanel === 'estoque' && <EstoqueDashboard />}
        {activePanel === 'gerencia' && <GerenciaDashboard />}
        {activePanel === 'contratos' && <ContratosPage />}
        {activePanel === 'resultados' && <ResultadosPage />}
        {activePanel === 'custos-fixos' && <CustosFixosPage />}
        {activePanel === 'custos-variaveis' && <CustosVariaveisPage />}
        {activePanel === 'faturamento' && <FaturamentoPage />}
        {activePanel === 'test-api' && <TestApiConnection />}
      </div>
    </div>
  );
}

export default App;
