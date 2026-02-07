import { useState } from 'react';
import FluxoCaixaDashboard from './components/dashboard/FluxoCaixaDashboard';
import FluxoLucroDashboard from './components/dashboard/FluxoLucroDashboard';
import EstoqueDashboard from './components/dashboard/EstoqueDashboard';
import GerenciaDashboard from './components/dashboard/GerenciaDashboard';
import EstoqueComparacao from './components/estoque/EstoqueComparacao';
import ContratosPage from './pages/ContratosPage';
import ResultadosPage from './pages/ResultadosPage';
import CustosFixosPage from './pages/CustosFixosPage';
import CustosVariaveisPage from './pages/CustosVariaveisPage';
import { FaturamentoPage } from './pages/FaturamentoPage';
import TestApiConnection from './components/TestApiConnection';
import './App.css';

function App() {
  const [activePanel, setActivePanel] = useState<'fluxo-realizado' | 'fluxo-lucro' | 'estoque' | 'estoque-comparativo' | 'gerencia' | 'contratos' | 'resultados' | 'custos-fixos' | 'custos-variaveis' | 'faturamento' | 'test-api'>('fluxo-realizado');

  // Estado Global de Datas
  const [dataInicio, setDataInicio] = useState<string>(() => {
    const hoje = new Date();
    return `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-01`;
  });
  const [dataFim, setDataFim] = useState<string>(() => {
    const hoje = new Date();
    return `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-${new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0).getDate()}`;
  });

  const setPeriodo = (tipo: 'mes_atual' | 'ano_atual' | 'ultimo_mes' | 'ano_anterior') => {
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = hoje.getMonth();

    switch (tipo) {
      case 'mes_atual':
        setDataInicio(`${ano}-${String(mes + 1).padStart(2, '0')}-01`);
        setDataFim(`${ano}-${String(mes + 1).padStart(2, '0')}-${new Date(ano, mes + 1, 0).getDate()}`);
        break;
      case 'ano_atual':
        setDataInicio(`${ano}-01-01`);
        setDataFim(`${ano}-12-31`);
        break;
      case 'ultimo_mes': {
        const mesAnterior = mes === 0 ? 11 : mes - 1;
        const anoAnterior = mes === 0 ? ano - 1 : ano;
        setDataInicio(`${anoAnterior}-${String(mesAnterior + 1).padStart(2, '0')}-01`);
        setDataFim(`${anoAnterior}-${String(mesAnterior + 1).padStart(2, '0')}-${new Date(anoAnterior, mesAnterior + 1, 0).getDate()}`);
        break;
      }
      case 'ano_anterior':
        setDataInicio(`${ano - 1}-01-01`);
        setDataFim(`${ano - 1}-12-31`);
        break;
    }
  };


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
          flexDirection: 'column',
          gap: '16px',
          paddingTop: '16px',
          paddingBottom: '16px'
        }}>
          <div style={{ width: '100%' }}>
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              color: '#111827',
              margin: 0
            }}>
              🏢 Sistema Financeiro
            </h1>
          </div>

          {/* Filtro Global de Datas */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', backgroundColor: '#f8fafc', padding: '8px 16px', borderRadius: '8px', border: '1px solid #e2e8f0', width: 'fit-content' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button onClick={() => setPeriodo('mes_atual')} style={{ padding: '6px 12px', fontSize: '0.75rem', borderRadius: '4px', border: '1px solid #cbd5e1', cursor: 'pointer', backgroundColor: '#eff6ff', color: '#1e40af', fontWeight: '500' }}>Mês Atual</button>
              <button onClick={() => setPeriodo('ultimo_mes')} style={{ padding: '6px 12px', fontSize: '0.75rem', borderRadius: '4px', border: '1px solid #cbd5e1', cursor: 'pointer', backgroundColor: 'white', color: '#475569' }}>Último Mês</button>
              <button onClick={() => setPeriodo('ano_atual')} style={{ padding: '6px 12px', fontSize: '0.75rem', borderRadius: '4px', border: '1px solid #cbd5e1', cursor: 'pointer', backgroundColor: 'white', color: '#475569' }}>Ano Atual</button>
              <button onClick={() => setPeriodo('ano_anterior')} style={{ padding: '6px 12px', fontSize: '0.75rem', borderRadius: '4px', border: '1px solid #cbd5e1', cursor: 'pointer', backgroundColor: 'white', color: '#475569' }}>Ano Anterior</button>
            </div>
            <div style={{ width: '1px', height: '20px', backgroundColor: '#cbd5e1' }}></div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '0.875rem' }} />
              <span style={{ color: '#64748b' }}>até</span>
              <input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '0.875rem' }} />
            </div>
          </div>
        </div>

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
            onClick={() => setActivePanel('estoque-comparativo')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'estoque-comparativo' ? '#3b82f6' : 'transparent',
              color: activePanel === 'estoque-comparativo' ? 'white' : '#6b7280',
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
            ⚖️ Comp. Estoque (Fis/Fis)
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


      {/* Conteúdo dos Painéis */}
      <div>
        {activePanel === 'fluxo-realizado' && <FluxoCaixaDashboard dataInicio={dataInicio} dataFim={dataFim} />}
        {activePanel === 'fluxo-lucro' && <FluxoLucroDashboard dataInicio={dataInicio} dataFim={dataFim} />}
        {activePanel === 'estoque' && <EstoqueDashboard />}
        {activePanel === 'estoque-comparativo' && <EstoqueComparacao dataInicio={dataInicio} dataFim={dataFim} />}
        {activePanel === 'gerencia' && <GerenciaDashboard dataInicio={dataInicio} dataFim={dataFim} />}
        {activePanel === 'contratos' && <ContratosPage />}
        {activePanel === 'resultados' && <ResultadosPage />}
        {activePanel === 'custos-fixos' && <CustosFixosPage />}
        {activePanel === 'custos-variaveis' && <CustosVariaveisPage />}
        {activePanel === 'faturamento' && <FaturamentoPage />}
        {activePanel === 'test-api' && <TestApiConnection />}
      </div>
    </div >
  );
}

export default App;
