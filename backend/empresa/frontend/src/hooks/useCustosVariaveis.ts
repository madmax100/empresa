// src/hooks/useCustosVariaveis.ts

import { useState } from 'react';
import { CustosVariaveisService, type CustosVariaveisResponse } from '../services/custos-variaveis-service';

export interface DateRange {
  from: Date;
  to: Date;
}

export interface UseCustosVariaveisReturn {
  data: CustosVariaveisResponse | null;
  loading: boolean;
  error: string | null;
  fetchCustosVariaveis: (dateRange: DateRange) => Promise<void>;
}

export function useCustosVariaveis(): UseCustosVariaveisReturn {
  const [data, setData] = useState<CustosVariaveisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCustosVariaveis = async (dateRange: DateRange) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Iniciando busca de custos variáveis...');
      console.log('📅 Range de datas:', dateRange);

      const dataInicio = dateRange.from.toISOString().split('T')[0];
      const dataFim = dateRange.to.toISOString().split('T')[0];
      
      console.log('📅 Datas formatadas:', { dataInicio, dataFim });

      const result = await CustosVariaveisService.buscarCustosVariaveis(dataInicio, dataFim);
      
      console.log('✅ Dados recebidos com sucesso:', result);
      setData(result);
      
    } catch (err) {
      console.error('❌ Erro na busca de custos variáveis:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao buscar custos variáveis';
      setError(errorMessage);
      
      // Em caso de erro, definir dados vazios para evitar erros de renderização
      setData(null);
      
    } finally {
      setLoading(false);
      console.log('🏁 Busca de custos variáveis finalizada');
    }
  };

  return {
    data,
    loading,
    error,
    fetchCustosVariaveis
  };
}
