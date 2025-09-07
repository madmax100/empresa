import React, { useState, useEffect } from 'react';
import { financialService } from '../services/financialService';

export const TesteContasVencidas: React.FC = () => {
  const [dados, setDados] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const buscarDados = async () => {
      try {
        console.log('🚀 Iniciando busca de contas vencidas...');
        
        const resultado = await financialService.getContasPorVencimento({
          data_inicio: '2020-01-01',
          data_fim: '2024-09-01',
          tipo: 'ambos',
          status: 'A'
        });
        
        console.log('✅ Dados recebidos:', resultado);
        setDados(resultado);
        
      } catch (err: any) {
        console.error('❌ Erro:', err);
        setError(err.message || 'Erro ao carregar dados');
      } finally {
        setLoading(false);
      }
    };

    buscarDados();
  }, []);

  if (loading) {
    return <div className="p-4">Carregando contas vencidas...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Erro: {error}</div>;
  }

  if (!dados) {
    return <div className="p-4">Nenhum dado encontrado</div>;
  }

  const receber = dados.contas_a_receber || [];
  const pagar = dados.contas_a_pagar || [];
  
  // Filtrar por data de vencimento
  const dataLimite = new Date('2024-09-01');
  const receberVencidas = receber.filter((conta: any) => {
    const vencimento = new Date(conta.vencimento);
    return vencimento < dataLimite;
  });
  
  const pagarVencidas = pagar.filter((conta: any) => {
    const vencimento = new Date(conta.vencimento);
    return vencimento < dataLimite;
  });

  const valorReceber = receberVencidas.reduce((sum: number, conta: any) => sum + parseFloat(conta.valor || 0), 0);
  const valorPagar = pagarVencidas.reduce((sum: number, conta: any) => sum + parseFloat(conta.valor || 0), 0);

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">🧪 Teste Contas Vencidas</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="p-4 bg-orange-50 rounded-lg">
          <h3 className="font-semibold text-orange-700">Entradas Vencidas</h3>
          <p className="text-2xl font-bold text-orange-600">R$ {valorReceber.toFixed(2)}</p>
          <p className="text-sm text-gray-600">Quantidade: {receberVencidas.length}</p>
        </div>
        
        <div className="p-4 bg-red-50 rounded-lg">
          <h3 className="font-semibold text-red-700">Saídas Vencidas</h3>
          <p className="text-2xl font-bold text-red-600">R$ {valorPagar.toFixed(2)}</p>
          <p className="text-sm text-gray-600">Quantidade: {pagarVencidas.length}</p>
        </div>
        
        <div className="p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-700">Saldo Vencido</h3>
          <p className={`text-2xl font-bold ${valorReceber - valorPagar >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            R$ {(valorReceber - valorPagar).toFixed(2)}
          </p>
        </div>
        
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-700">Total Vencido</h3>
          <p className="text-2xl font-bold text-gray-600">{receberVencidas.length + pagarVencidas.length}</p>
          <p className="text-sm text-gray-600">Contas</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold mb-2">📈 Contas a Receber Vencidas ({receberVencidas.length})</h3>
          <div className="max-h-60 overflow-y-auto">
            {receberVencidas.slice(0, 5).map((conta: any, index: number) => (
              <div key={index} className="p-2 border-b">
                <p className="font-medium">{conta.cliente_nome}</p>
                <p className="text-sm text-gray-600">R$ {conta.valor} - Venc: {new Date(conta.vencimento).toLocaleDateString('pt-BR')}</p>
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <h3 className="font-semibold mb-2">📉 Contas a Pagar Vencidas ({pagarVencidas.length})</h3>
          <div className="max-h-60 overflow-y-auto">
            {pagarVencidas.slice(0, 5).map((conta: any, index: number) => (
              <div key={index} className="p-2 border-b">
                <p className="font-medium">{conta.fornecedor_nome}</p>
                <p className="text-sm text-gray-600">R$ {conta.valor} - Venc: {new Date(conta.vencimento).toLocaleDateString('pt-BR')}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="mt-4 p-4 bg-gray-100 rounded">
        <h4 className="font-semibold">🔍 Debug Info:</h4>
        <pre className="text-xs overflow-auto">
          {JSON.stringify({
            periodo: dados.periodo,
            filtros: dados.filtros,
            resumo: dados.resumo,
            arrays: {
              receber_total: receber.length,
              pagar_total: pagar.length,
              receber_vencidas: receberVencidas.length,
              pagar_vencidas: pagarVencidas.length
            }
          }, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default TesteContasVencidas;
