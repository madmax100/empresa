import React from 'react';
import type { ContratoLocacao } from '../types/contratos';
import { formatCurrency, formatDate } from '../lib/utils';

interface DetalhesContratoModalProps {
  contrato: ContratoLocacao;
  onClose: () => void;
}

// Interface para InfoCard atualizada
const InfoCard: React.FC<{ 
  label: string; 
  value: string | number | React.ReactNode; 
  className?: string; 
  valueClassName?: string 
}> = ({ label, value, className = '', valueClassName = '' }) => (
  <div className={`bg-gray-50 p-4 rounded-lg border border-gray-200 ${className}`}>
    <label className="block text-sm font-medium text-gray-600 mb-1">{label}</label>
    <p className={`text-lg font-bold text-gray-800 ${valueClassName}`}>{value}</p>
  </div>
);

// Interface para StatusBadge atualizada
const StatusBadge: React.FC<{ renovado: string }> = ({ renovado }) => {
  const isRenovado = renovado === 'SIM';
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
      isRenovado 
        ? 'bg-green-100 text-green-800' 
        : 'bg-red-100 text-red-800'
    }`}>
      {isRenovado ? 'Renovado' : 'Não Renovado'}
    </span>
  );
};

export const DetalhesContratoModal: React.FC<DetalhesContratoModalProps> = ({ contrato, onClose }) => {
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 relative">
          <h2 className="text-2xl font-bold">Detalhes do Contrato</h2>
          <p className="text-blue-100 mt-1">Contrato #{contrato.contrato}</p>
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 text-white hover:text-gray-200 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Conteúdo */}
        <div className="p-8 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="md:col-span-2 bg-blue-50 p-6 rounded-lg border border-blue-200">
              <label className="block text-sm font-medium text-blue-800 mb-1">Cliente</label>
              <p className="text-xl font-bold text-blue-900">{contrato.cliente.nome}</p>
            </div>
            <InfoCard 
              label="Status de Renovação" 
              value={<StatusBadge renovado={contrato.renovado} />} 
            />
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            <InfoCard 
              label="Valor Total do Contrato" 
              value={formatCurrency(contrato.valorcontrato)} 
              className="bg-green-50 border-green-200"
              valueClassName="text-green-800 !text-xl"
            />
            <InfoCard 
              label="Valor da Parcela" 
              value={formatCurrency(contrato.valorpacela)} 
              className="bg-blue-50 border-blue-200"
              valueClassName="text-blue-800"
            />
            <InfoCard 
              label="Número de Parcelas" 
              value={`${contrato.numeroparcelas}x`} 
              className="bg-purple-50 border-purple-200"
              valueClassName="text-purple-800"
            />
            <InfoCard 
              label="Tipo de Contrato" 
              value={contrato.tipocontrato} 
              className="bg-gray-50 border-gray-200"
              valueClassName="text-gray-800"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <InfoCard 
              label="Data de Início" 
              value={formatDate(contrato.inicio)} 
              className="bg-green-50 border-green-200"
              valueClassName="text-green-800"
            />
            <InfoCard 
              label="Data de Fim" 
              value={formatDate(contrato.fim)} 
              className="bg-red-50 border-red-200"
              valueClassName="text-red-800"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-8 py-4 border-t">
          <div className="flex justify-end">
            <button 
              onClick={onClose}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetalhesContratoModal;
