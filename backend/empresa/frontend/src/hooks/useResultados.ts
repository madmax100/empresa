import { useState, useEffect, useCallback } from 'react';
import { resultadosService, type ResultadosPeriodo, type FiltrosPeriodo } from '@/services/resultados-service';

interface UseResultadosReturn {
  resultados: ResultadosPeriodo | null;
  loading: boolean;
  error: string | null;
  carregarResultados: () => Promise<void>;
  setFiltros: (filtros: FiltrosPeriodo) => void;
  filtros: FiltrosPeriodo;
}

export const useResultados = (filtrosIniciais?: Partial<FiltrosPeriodo>): UseResultadosReturn => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resultados, setResultados] = useState<ResultadosPeriodo | null>(null);
  
  // Configurar filtros padrão (último mês)
  const defaultFrom = new Date();
  defaultFrom.setMonth(defaultFrom.getMonth() - 1);
  const defaultTo = new Date();
  
  const [filtros, setFiltros] = useState<FiltrosPeriodo>({
    data_inicio: defaultFrom.toISOString().split('T')[0],
    data_fim: defaultTo.toISOString().split('T')[0],
    ...filtrosIniciais
  });

  const carregarResultados = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔄 [Hook] Carregando resultados do período...');
      console.log(`📅 [Hook] Período: ${filtros.data_inicio} até ${filtros.data_fim}`);

      const dados = await resultadosService.buscarResultadosPeriodo(filtros);
      setResultados(dados);

      console.log('✅ [Hook] Resultados carregados com sucesso:', dados);

    } catch (err) {
      console.error('❌ [Hook] Erro ao carregar resultados:', err);
      setError('Falha ao carregar dados dos resultados do período');
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  // Carregar dados quando os filtros mudarem
  useEffect(() => {
    carregarResultados();
  }, [carregarResultados]);

  return {
    resultados,
    loading,
    error,
    carregarResultados,
    setFiltros,
    filtros
  };
};
