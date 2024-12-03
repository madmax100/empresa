import React from 'react'
import './App.css'
import ListaContratos from './components/listaContratos'

import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import ContasPage from './components/listaContas'
import FinancialDashboard from './components/painelFinanceiro'
import ResumoPorCliente from './components/resumoPorCliente'

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
                  <span className="text-xl font-bold text-gray-800">C3M Cópias</span>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
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
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Conteúdo */}
        <main>
          <Routes>
            <Route path="/contratos" element={<ListaContratos />} />
            <Route path="/contas" element={<ContasPage />} />
            <Route path="/financial" element={<FinancialDashboard />} />
            <Route path="/cliente" element={<ResumoPorCliente />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App
