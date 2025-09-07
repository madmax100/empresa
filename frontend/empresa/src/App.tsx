// src/App.tsx
import React from 'react';
import './App.css';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import FinancialDashboard from './pages/dashboard/painelFinanceiro';
import ResumoPorCliente from './pages/dashboard/resumoPorCliente';
import ContractIndicators from './pages/dashboard/contractDashboard';
import Home from './pages/home';
import ContractsDashboardGrouped from './components/financial/contracts/ContractsDashboardGrouped';
import ListaContratos from './components/financial/contracts/ContractList';
import ContasPage from './components/financial/bills/ReceivablesList';
import BillsManagement from './components/financial/bills/PayblesList';
import FluxoCaixa from './pages/financial/FluxoCaixa';
import RelatorioEstoque from './pages/financial/RelatorioEstoque';
import EstoqueCompleto from './pages/financial/EstoqueCompleto';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        {/* Navbar */}
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <Link to="/" className="text-xl font-bold text-gray-800">
                    C3M Cópias
                  </Link>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                    to="/"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/contratos_gestao"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/contratos"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Contratos
                  </Link>
                  <Link
                    to="/contas"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Contas
                  </Link>
                  <Link
                    to="/financial"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Financeiro
                  </Link>
                  <Link
                    to="/cliente"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Cliente/Fornecedor
                  </Link>
                  <Link
                    to="/management"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Painel
                  </Link>
                  <Link
                    to="/management-receber"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Painel Receber
                  </Link>
                  <Link
                    to="/contracts"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Indicadores de Contrato
                  </Link>
                  <Link
                    to="/financeiro/fluxo-caixa"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Fluxo de Caixa
                  </Link>
                  <Link
                    to="/financeiro/relatorio-estoque"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Relatório Estoque
                  </Link>
                  <Link
                    to="/financeiro/estoque-completo"
                    className="border-b-2 border-transparent hover:border-gray-300 inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700"
                  >
                    Estoque Completo
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Conteúdo */}
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
      <Route path="/contratos_gestao" element={<ContractsDashboardGrouped />} />
            <Route path="/contratos" element={<ListaContratos />} />
            <Route path="/contas" element={<ContasPage />} />
            <Route path="/financial" element={<FinancialDashboard />} />
            <Route path="/cliente" element={<ResumoPorCliente />} />
            <Route path="/management" element={<BillsManagement />} />
            <Route path="/management-receber" element={<BillsManagement type="receber" />} />
            <Route path="/contracts" element={<ContractIndicators />} />
            <Route path="/fluxo_caixa" element={<FluxoCaixa />} />
            <Route path="/financeiro/fluxo-caixa" element={<FluxoCaixa />} />
            <Route path="/financeiro/relatorio-estoque" element={<RelatorioEstoque />} />
            <Route path="/financeiro/estoque-completo" element={<EstoqueCompleto />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;