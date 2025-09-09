// src/hooks/useCustosFixos.ts

import { useState } from 'react';
import { CustosFixosService, type CustosFixosResponse } from '../services/custos-fixos-service';

export interface DateRange {
  from: Date;
  to: Date;
}

export function useCustosFixos() {
  const [data, setData] = useState<CustosFixosResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCustosFixos = async (dateRange: DateRange) => {
    setLoading(true);
    setError(null);
    
    try {
      const dataInicio = dateRange.from.toISOString().split('T')[0];
      const dataFim = dateRange.to.toISOString().split('T')[0];
      
      console.log('🎯 Hook - Chamando API com datas:', { dataInicio, dataFim, dateRange });
      
      const response = await CustosFixosService.getCustosFixos(dataInicio, dataFim);
      
      console.log('🎯 Hook - Resposta recebida:', response);
      
      setData(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      console.error('❌ Erro no hook:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    data,
    loading,
    error,
    fetchCustosFixos
  };
}
