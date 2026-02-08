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
import ClientesPage from './pages/ClientesPage';
import FornecedoresPage from './pages/FornecedoresPage';
import FuncionariosPage from './pages/FuncionariosPage';
import EmpresasPage from './pages/EmpresasPage';
import TransportadorasPage from './pages/TransportadorasPage';
import EtapasFunilPage from './pages/EtapasFunilPage';
import LeadsPage from './pages/LeadsPage';
import OportunidadesPage from './pages/OportunidadesPage';
import AtividadesCrmPage from './pages/AtividadesCrmPage';
import PropostasVendaCrmPage from './pages/PropostasVendaCrmPage';
import ItensPropostaVendaPage from './pages/ItensPropostaVendaPage';
import CrmResumoPage from './pages/CrmResumoPage';
import ImpostosFiscaisPage from './pages/ImpostosFiscaisPage';
import ApuracoesFiscaisPage from './pages/ApuracoesFiscaisPage';
import ItensApuracaoFiscalPage from './pages/ItensApuracaoFiscalPage';
import FiscalOperacoesPage from './pages/FiscalOperacoesPage';
import OrdensProducaoPage from './pages/OrdensProducaoPage';
import ItensOrdemProducaoPage from './pages/ItensOrdemProducaoPage';
import ConsumosProducaoPage from './pages/ConsumosProducaoPage';
import ApontamentosProducaoPage from './pages/ApontamentosProducaoPage';
import OperacoesProducaoPage from './pages/OperacoesProducaoPage';
import TestApiConnection from './components/TestApiConnection';
import './App.css';

function App() {
  const [activePanel, setActivePanel] = useState<'fluxo-realizado' | 'fluxo-lucro' | 'estoque' | 'estoque-comparativo' | 'gerencia' | 'contratos' | 'resultados' | 'custos-fixos' | 'custos-variaveis' | 'faturamento' | 'test-api' | 'clientes' | 'fornecedores' | 'funcionarios' | 'empresas' | 'transportadoras' | 'crm-resumo' | 'etapas-funil' | 'leads' | 'oportunidades' | 'atividades-crm' | 'propostas-crm' | 'itens-proposta' | 'impostos-fiscais' | 'apuracoes-fiscais' | 'itens-apuracao-fiscal' | 'fiscal-operacoes' | 'ordens-producao' | 'itens-ordem-producao' | 'consumos-producao' | 'apontamentos-producao' | 'operacoes-producao'>('fluxo-realizado');

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
            onClick={() => setActivePanel('clientes')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'clientes' ? '#3b82f6' : 'transparent',
              color: activePanel === 'clientes' ? 'white' : '#6b7280',
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
            🧑‍🤝‍🧑 Clientes
          </button>

          <button
            onClick={() => setActivePanel('fornecedores')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'fornecedores' ? '#3b82f6' : 'transparent',
              color: activePanel === 'fornecedores' ? 'white' : '#6b7280',
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
            🧾 Fornecedores
          </button>

          <button
            onClick={() => setActivePanel('funcionarios')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'funcionarios' ? '#3b82f6' : 'transparent',
              color: activePanel === 'funcionarios' ? 'white' : '#6b7280',
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
            👥 Funcionários
          </button>

          <button
            onClick={() => setActivePanel('empresas')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'empresas' ? '#3b82f6' : 'transparent',
              color: activePanel === 'empresas' ? 'white' : '#6b7280',
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
            🏭 Empresas
          </button>

          <button
            onClick={() => setActivePanel('transportadoras')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'transportadoras' ? '#3b82f6' : 'transparent',
              color: activePanel === 'transportadoras' ? 'white' : '#6b7280',
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
            🚚 Transportadoras
          </button>

          <button
            onClick={() => setActivePanel('crm-resumo')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'crm-resumo' ? '#3b82f6' : 'transparent',
              color: activePanel === 'crm-resumo' ? 'white' : '#6b7280',
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
            🤝 CRM Resumo
          </button>

          <button
            onClick={() => setActivePanel('etapas-funil')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'etapas-funil' ? '#3b82f6' : 'transparent',
              color: activePanel === 'etapas-funil' ? 'white' : '#6b7280',
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
            🧭 Etapas Funil
          </button>

          <button
            onClick={() => setActivePanel('leads')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'leads' ? '#3b82f6' : 'transparent',
              color: activePanel === 'leads' ? 'white' : '#6b7280',
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
            🗂️ Leads
          </button>

          <button
            onClick={() => setActivePanel('oportunidades')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'oportunidades' ? '#3b82f6' : 'transparent',
              color: activePanel === 'oportunidades' ? 'white' : '#6b7280',
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
            🎯 Oportunidades
          </button>

          <button
            onClick={() => setActivePanel('atividades-crm')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'atividades-crm' ? '#3b82f6' : 'transparent',
              color: activePanel === 'atividades-crm' ? 'white' : '#6b7280',
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
            📝 Atividades CRM
          </button>

          <button
            onClick={() => setActivePanel('propostas-crm')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'propostas-crm' ? '#3b82f6' : 'transparent',
              color: activePanel === 'propostas-crm' ? 'white' : '#6b7280',
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
            📄 Propostas CRM
          </button>

          <button
            onClick={() => setActivePanel('itens-proposta')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'itens-proposta' ? '#3b82f6' : 'transparent',
              color: activePanel === 'itens-proposta' ? 'white' : '#6b7280',
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
            🧾 Itens Proposta
          </button>

          <button
            onClick={() => setActivePanel('impostos-fiscais')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'impostos-fiscais' ? '#3b82f6' : 'transparent',
              color: activePanel === 'impostos-fiscais' ? 'white' : '#6b7280',
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
            🧾 Impostos Fiscais
          </button>

          <button
            onClick={() => setActivePanel('apuracoes-fiscais')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'apuracoes-fiscais' ? '#3b82f6' : 'transparent',
              color: activePanel === 'apuracoes-fiscais' ? 'white' : '#6b7280',
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
            📅 Apurações Fiscais
          </button>

          <button
            onClick={() => setActivePanel('itens-apuracao-fiscal')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'itens-apuracao-fiscal' ? '#3b82f6' : 'transparent',
              color: activePanel === 'itens-apuracao-fiscal' ? 'white' : '#6b7280',
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
            🧮 Itens Apuração
          </button>

          <button
            onClick={() => setActivePanel('fiscal-operacoes')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'fiscal-operacoes' ? '#3b82f6' : 'transparent',
              color: activePanel === 'fiscal-operacoes' ? 'white' : '#6b7280',
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
            🧾 Operações Fiscais
          </button>

          <button
            onClick={() => setActivePanel('ordens-producao')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'ordens-producao' ? '#3b82f6' : 'transparent',
              color: activePanel === 'ordens-producao' ? 'white' : '#6b7280',
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
            🏭 Ordens Produção
          </button>

          <button
            onClick={() => setActivePanel('itens-ordem-producao')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'itens-ordem-producao' ? '#3b82f6' : 'transparent',
              color: activePanel === 'itens-ordem-producao' ? 'white' : '#6b7280',
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
            🧰 Itens Ordem
          </button>

          <button
            onClick={() => setActivePanel('consumos-producao')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'consumos-producao' ? '#3b82f6' : 'transparent',
              color: activePanel === 'consumos-producao' ? 'white' : '#6b7280',
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
            🧪 Consumos
          </button>

          <button
            onClick={() => setActivePanel('apontamentos-producao')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'apontamentos-producao' ? '#3b82f6' : 'transparent',
              color: activePanel === 'apontamentos-producao' ? 'white' : '#6b7280',
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
            📌 Apontamentos
          </button>

          <button
            onClick={() => setActivePanel('operacoes-producao')}
            style={{
              padding: '10px 20px',
              border: 'none',
              backgroundColor: activePanel === 'operacoes-producao' ? '#3b82f6' : 'transparent',
              color: activePanel === 'operacoes-producao' ? 'white' : '#6b7280',
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
            🏗️ Operações Produção
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
        {activePanel === 'clientes' && <ClientesPage />}
        {activePanel === 'fornecedores' && <FornecedoresPage />}
        {activePanel === 'funcionarios' && <FuncionariosPage />}
        {activePanel === 'empresas' && <EmpresasPage />}
        {activePanel === 'transportadoras' && <TransportadorasPage />}
        {activePanel === 'crm-resumo' && <CrmResumoPage />}
        {activePanel === 'etapas-funil' && <EtapasFunilPage />}
        {activePanel === 'leads' && <LeadsPage />}
        {activePanel === 'oportunidades' && <OportunidadesPage />}
        {activePanel === 'atividades-crm' && <AtividadesCrmPage />}
        {activePanel === 'propostas-crm' && <PropostasVendaCrmPage />}
        {activePanel === 'itens-proposta' && <ItensPropostaVendaPage />}
        {activePanel === 'impostos-fiscais' && <ImpostosFiscaisPage />}
        {activePanel === 'apuracoes-fiscais' && <ApuracoesFiscaisPage />}
        {activePanel === 'itens-apuracao-fiscal' && <ItensApuracaoFiscalPage />}
        {activePanel === 'fiscal-operacoes' && <FiscalOperacoesPage />}
        {activePanel === 'ordens-producao' && <OrdensProducaoPage />}
        {activePanel === 'itens-ordem-producao' && <ItensOrdemProducaoPage />}
        {activePanel === 'consumos-producao' && <ConsumosProducaoPage />}
        {activePanel === 'apontamentos-producao' && <ApontamentosProducaoPage />}
        {activePanel === 'operacoes-producao' && <OperacoesProducaoPage />}
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
