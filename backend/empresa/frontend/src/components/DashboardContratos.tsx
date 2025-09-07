import React from 'react';
import type { ContratosDashboard } from '../types/contratos';

interface DashboardContratosProps {
  dashboard: ContratosDashboard;
  loading?: boolean;
}

export const DashboardContratosComponent: React.FC<DashboardContratosProps> = ({ 
  dashboard, 
  loading = false 
}) => {
  const formatarValor = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor);
  };

  const formatarNumero = (numero: number) => {
    return new Intl.NumberFormat('pt-BR').format(numero);
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      titulo: 'Total de Contratos',
      valor: formatarNumero(dashboard.totalContratos),
      subtitulo: `${dashboard.contratosAtivos} ativos`,
      cor: 'bg-blue-50 border-blue-200',
      icone: '📋'
    },
    {
      titulo: 'Valor Total',
      valor: formatarValor(dashboard.valorTotalContratos),
      subtitulo: `Média: ${formatarValor(dashboard.valorMedioContrato)}`,
      cor: 'bg-green-50 border-green-200',
      icone: '💰'
    },
    {
      titulo: 'Contratos Ativos',
      valor: formatarNumero(dashboard.contratosAtivos),
      subtitulo: `${dashboard.contratosInativos} inativos`,
      cor: 'bg-emerald-50 border-emerald-200',
      icone: '✅'
    },
    {
      titulo: 'Total de Máquinas',
      valor: formatarNumero(dashboard.totalMaquinas),
      subtitulo: 'Em contratos ativos',
      cor: 'bg-purple-50 border-purple-200',
      icone: '🖨️'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, index) => (
          <div key={index} className={`p-6 rounded-lg border ${card.cor}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{card.titulo}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{card.valor}</p>
                <p className="text-sm text-gray-500 mt-1">{card.subtitulo}</p>
              </div>
              <div className="text-2xl">{card.icone}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Distribuição por Tipo */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Distribuição por Tipo de Contrato
          </h3>
          <div className="space-y-3">
            {dashboard.distribuicaoTipos.map((tipo) => (
              <div key={tipo.tipo} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <span className="font-medium text-gray-900">Tipo {tipo.tipo}</span>
                  <div className="text-sm text-gray-600">
                    {formatarNumero(tipo.quantidade)} contrato{tipo.quantidade !== 1 ? 's' : ''}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900">
                    {formatarValor(tipo.valorTotal)}
                  </div>
                  <div className="text-sm text-gray-600">
                    {((tipo.valorTotal / dashboard.valorTotalContratos) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Evolução Mensal */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Evolução Mensal (Últimos 12 meses)
          </h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {dashboard.evolutionMensal.map((mes) => (
              <div key={mes.mes} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                <div className="text-sm font-medium text-gray-700">
                  {new Date(mes.mes + '-01').toLocaleDateString('pt-BR', { 
                    year: 'numeric', 
                    month: 'short' 
                  })}
                </div>
                <div className="flex space-x-4 text-sm">
                  <div className="text-blue-600">
                    {mes.novosContratos} novos
                  </div>
                  <div className="text-green-600">
                    {mes.renovacoes} renovações
                  </div>
                  <div className="font-semibold text-gray-900">
                    {formatarValor(mes.valor)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Resumo de Status */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Resumo Executivo
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {((dashboard.contratosAtivos / dashboard.totalContratos) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Taxa de Contratos Ativos</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {formatarValor(dashboard.valorMedioContrato)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Valor Médio por Contrato</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">
              {dashboard.totalMaquinas > 0 ? 
                (dashboard.valorTotalContratos / dashboard.totalMaquinas).toLocaleString('pt-BR', {
                  style: 'currency',
                  currency: 'BRL'
                }) : 
                'N/A'
              }
            </div>
            <div className="text-sm text-gray-600 mt-1">Valor por Máquina</div>
          </div>
        </div>
      </div>
    </div>
  );
};
