// src/hooks/useFaturamento.ts

import { useState, useCallback } from 'react';
import { FaturamentoService, type FaturamentoResponse } from '../services/faturamento-service';

export interface DateRange {
  from: Date;
  to: Date;
}

export interface UseFaturamentoReturn {
  data: FaturamentoResponse | null;
  loading: boolean;
  error: string | null;
  fetchFaturamento: (dateRange: DateRange) => Promise<void>;
}

export function useFaturamento(): UseFaturamentoReturn {
  const [data, setData] = useState<FaturamentoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFaturamento = useCallback(async (dateRange: DateRange) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Iniciando busca de faturamento...');
      console.log('📅 Range de datas:', dateRange);

      const dataInicio = dateRange.from.toISOString().split('T')[0];
      const dataFim = dateRange.to.toISOString().split('T')[0];
      
      console.log('📅 Datas formatadas:', { dataInicio, dataFim });

      const result = await FaturamentoService.buscarFaturamento(dataInicio, dataFim);
      
      console.log('✅ Dados recebidos com sucesso:', result);
      setData(result);
      
    } catch (err) {
      console.error('❌ Erro na busca de faturamento:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao buscar faturamento';
      setError(errorMessage);
      
      // Em caso de erro, definir dados vazios para evitar erros de renderização
      setData(null);
      
    } finally {
      setLoading(false);
      console.log('🏁 Busca de faturamento finalizada');
    }
  }, []);

  return {
    data,
    loading,
    error,
    fetchFaturamento
  };
}
