// src/hooks/useGerencia.ts

import { useState, useCallback } from 'react';
import { GerenciaService, type GerenciaData } from '../services/gerencia-service';

export interface DateRange {
  from: Date;
  to: Date;
}

export interface UseGerenciaReturn {
  data: GerenciaData | null;
  loading: boolean;
  error: string | null;
  fetchGerencia: (dateRange: DateRange) => Promise<void>;
}

export function useGerencia(): UseGerenciaReturn {
  const [data, setData] = useState<GerenciaData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGerencia = useCallback(async (dateRange: DateRange) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Iniciando busca de dados de gerência...');
      console.log('📅 Range de datas:', dateRange);

      const dataInicio = dateRange.from.toISOString().split('T')[0];
      const dataFim = dateRange.to.toISOString().split('T')[0];
      
      // Implementar lógica inteligente como no controle de estoque
      const today = new Date().toISOString().split('T')[0];
      const isCurrentPeriod = dataFim === today;
      
      console.log('📅 Datas formatadas:', { dataInicio, dataFim });
      console.log('📋 Lógica inteligente:', { 
        isCurrentPeriod, 
        today, 
        fonteDados: isCurrentPeriod ? 'atual' : 'historico' 
      });

      const result = await GerenciaService.buscarDadosGerencia(dataInicio, dataFim);
      
      console.log('✅ Dados de gerência recebidos com sucesso:', result);
      console.log('📊 Fonte dos dados:', result.fonteDados);
      setData(result);
      
    } catch (err) {
      console.error('❌ Erro na busca de dados de gerência:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao buscar dados de gerência';
      setError(errorMessage);
      
      // Em caso de erro, definir dados vazios para evitar erros de renderização
      setData(null);
      
    } finally {
      setLoading(false);
      console.log('🏁 Busca de dados de gerência finalizada');
    }
  }, []);

  return {
    data,
    loading,
    error,
    fetchGerencia
  };
}