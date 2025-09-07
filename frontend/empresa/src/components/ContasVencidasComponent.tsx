import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, AlertCircle } from 'lucide-react';
import { financialService } from '@/services/financialService';
import IndicadorCard from '@/components/common/IndicadorCard';

export const ContasVencidasComponent: React.FC = () => {
  const [contasVencidas, setContasVencidas] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const buscarContasVencidas = async () => {
      try {
        setLoading(true);
        console.log('🔍 [ContasVencidas] Iniciando busca...');
        
        // Usar data atual como referência
        const hoje = new Date();
        const dataHoje = hoje.toISOString().split('T')[0];
        
        // Buscar contas com vencimento até hoje (vencidas)
        const dadosVencidas = await financialService.getContasPorVencimento({
          data_inicio: '2020-01-01',
          data_fim: dataHoje,
          tipo: 'ambos',
          status: 'A',
          incluir_vencidas: true
        });
        
        console.log('📊 [ContasVencidas] Dados recebidos:', dadosVencidas);
        
        if (dadosVencidas) {
            const totalReceber = dadosVencidas.contas_a_receber.reduce((acc, conta) => acc + conta.valor, 0);
            const totalPagar = dadosVencidas.contas_a_pagar.reduce((acc, conta) => acc + conta.valor, 0);

            const resumo = {
                total_contas_receber: dadosVencidas.contas_a_receber.length,
                valor_total_receber: totalReceber,
                total_contas_pagar: dadosVencidas.contas_a_pagar.length,
                valor_total_pagar: totalPagar
            };
            
            setContasVencidas({ resumo });
            console.log('✅ [ContasVencidas] Resumo calculado:', resumo);
        } 
        
      } catch (err: any) {
        console.error('❌ [ContasVencidas] Erro:', err);
        setError(err.message || 'Erro ao carregar contas vencidas');
      } finally {
        setLoading(false);
      }
    };

    buscarContasVencidas();
  }, []);

  if (loading) {
    return (
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-orange-500" />
          Contas Vencidas
        </h3>
        <div className="p-4 text-center text-gray-500">
          Carregando contas vencidas...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-500" />
          Contas Vencidas
        </h3>
        <div className="p-4 text-center text-red-500">
          Erro: {error}
        </div>
      </div>
    );
  }

  if (!contasVencidas?.resumo) {
    return (
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-gray-500" />
          Contas Vencidas
        </h3>
        <div className="p-4 text-center text-gray-500">
          Nenhuma conta vencida encontrada
        </div>
      </div>
    );
  }

  const resumo = contasVencidas.resumo;

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold text-gray-700 flex items-center gap-2">
        <AlertTriangle className="h-5 w-5 text-orange-500" />
        Contas Vencidas (Status A - Vencimento anterior ao período)
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <IndicadorCard
          titulo="Entradas Vencidas"
          valor={resumo.valor_total_receber || 0}
          icone={<Clock className="h-4 w-4 text-orange-500" />}
          cor="orange"
          labelSecundario="Quantidade"
          valorSecundario={resumo.total_contas_receber || 0}
          descricao="Contas a receber vencidas não pagas"
        />
        <IndicadorCard
          titulo="Saídas Vencidas"
          valor={resumo.valor_total_pagar || 0}
          icone={<Clock className="h-4 w-4 text-red-500" />}
          cor="red"
          labelSecundario="Quantidade"
          valorSecundario={resumo.total_contas_pagar || 0}
          descricao="Contas a pagar vencidas não pagas"
        />
        <IndicadorCard
          titulo="Saldo Vencido"
          valor={(resumo.valor_total_receber || 0) - (resumo.valor_total_pagar || 0)}
          icone={<AlertTriangle className="h-4 w-4 text-orange-600" />}
          cor="orange"
          descricao="Diferença entre receber e pagar vencidos"
        />
        <IndicadorCard
          titulo="Total Vencido"
          valor={(resumo.total_contas_receber || 0) + (resumo.total_contas_pagar || 0)}
          icone={<AlertCircle className="h-4 w-4 text-red-600" />}
          cor="red"
          descricao="Volume total de contas vencidas"
        />
      </div>
    </div>
  );
};

export default ContasVencidasComponent;
