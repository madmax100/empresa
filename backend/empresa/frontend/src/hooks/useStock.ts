// Custom hook for stock data management
// Provides centralized state management for stock control data

import { useState, useEffect, useCallback } from 'react';
import stockService, { 
  EstoqueAtualData, 
  EstoqueCriticoData, 
  ProdutosMaisMovimentadosData,
  MovimentacoesPeriodoData 
} from '../services/stockService';

export interface UseStockOptions {
  autoLoad?: boolean;
  data?: string;
  limite?: number;
  offset?: number;
}

export interface UseStockReturn {
  // Data states
  estoqueGeral: EstoqueAtualData | null;
  estoqueTop: EstoqueAtualData | null;
  estoqueCritico: EstoqueCriticoData | null;
  produtosMovimentados: ProdutosMaisMovimentadosData | null;
  movimentacoesPeriodo: MovimentacoesPeriodoData | null;
  
  // Loading states
  loading: boolean;
  loadingGeral: boolean;
  loadingTop: boolean;
  loadingCritico: boolean;
  loadingMovimentados: boolean;
  loadingPeriodo: boolean;
  
  // Error states
  error: string | null;
  errors: {
    geral: string | null;
    top: string | null;
    critico: string | null;
    movimentados: string | null;
    periodo: string | null;
  };
  
  // Connection state
  backendConnected: boolean;
  
  // Actions
  loadAllData: (data?: string) => Promise<void>;
  loadEstoqueGeral: (params?: any) => Promise<void>;
  loadEstoqueTop: (data?: string) => Promise<void>;
  loadEstoqueCritico: (data?: string) => Promise<void>;
  loadProdutosMovimentados: (data?: string) => Promise<void>;
  loadMovimentacoesPeriodo: (dataInicio: string, dataFim: string, incluirDetalhes?: boolean) => Promise<void>;
  testConnection: () => Promise<void>;
  clearErrors: () => void;
  
  // Computed values
  totalProdutos: number;
  valorTotalEstoque: number;
  produtosComEstoque: number;
  produtosZerados: number;
}

export const useStock = (options: UseStockOptions = {}): UseStockReturn => {
  const { autoLoad = true, data, limite = 50, offset = 0 } = options;

  // Data states
  const [estoqueGeral, setEstoqueGeral] = useState<EstoqueAtualData | null>(null);
  const [estoqueTop, setEstoqueTop] = useState<EstoqueAtualData | null>(null);
  const [estoqueCritico, setEstoqueCritico] = useState<EstoqueCriticoData | null>(null);
  const [produtosMovimentados, setProdutosMovimentados] = useState<ProdutosMaisMovimentadosData | null>(null);
  const [movimentacoesPeriodo, setMovimentacoesPeriodo] = useState<MovimentacoesPeriodoData | null>(null);

  // Loading states
  const [loading, setLoading] = useState(false);
  const [loadingGeral, setLoadingGeral] = useState(false);
  const [loadingTop, setLoadingTop] = useState(false);
  const [loadingCritico, setLoadingCritico] = useState(false);
  const [loadingMovimentados, setLoadingMovimentados] = useState(false);
  const [loadingPeriodo, setLoadingPeriodo] = useState(false);

  // Error states
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState({
    geral: null as string | null,
    top: null as string | null,
    critico: null as string | null,
    movimentados: null as string | null,
    periodo: null as string | null,
  });

  // Connection state
  const [backendConnected, setBackendConnected] = useState(false);

  // Clear errors
  const clearErrors = useCallback(() => {
    setError(null);
    setErrors({
      geral: null,
      top: null,
      critico: null,
      movimentados: null,
      periodo: null,
    });
  }, []);

  // Test backend connection
  const testConnection = useCallback(async () => {
    console.log('🌐 useStock: Testing backend connection...');
    
    try {
      const result = await stockService.testConnection();
      setBackendConnected(result.success);
      
      if (!result.success) {
        setError(result.error || 'Backend connection failed');
        console.error('❌ useStock: Backend connection failed:', result.error);
      } else {
        console.log('✅ useStock: Backend connection successful');
      }
    } catch (err) {
      console.error('❌ useStock: Connection test error:', err);
      setBackendConnected(false);
      setError('Failed to test backend connection');
    }
  }, []);

  // Load estoque geral
  const loadEstoqueGeral = useCallback(async (params?: any) => {
    console.log('📦 useStock: Loading estoque geral...');
    setLoadingGeral(true);
    setErrors(prev => ({ ...prev, geral: null }));

    try {
      const result = await stockService.getEstoqueAtual({
        limite,
        offset,
        data,
        ...params
      });

      if (result.success && result.data) {
        setEstoqueGeral(result.data);
        console.log('✅ useStock: Estoque geral loaded successfully');
      } else {
        const errorMsg = result.error || 'Failed to load estoque geral';
        setErrors(prev => ({ ...prev, geral: errorMsg }));
        console.error('❌ useStock: Estoque geral error:', errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setErrors(prev => ({ ...prev, geral: errorMsg }));
      console.error('❌ useStock: Estoque geral exception:', err);
    } finally {
      setLoadingGeral(false);
    }
  }, [limite, offset, data]);

  // Load estoque top
  const loadEstoqueTop = useCallback(async (dataParam?: string) => {
    console.log('💎 useStock: Loading estoque top...');
    setLoadingTop(true);
    setErrors(prev => ({ ...prev, top: null }));

    try {
      const result = await stockService.getEstoqueAtual({
        limite: 100,
        ordem: 'valor_atual',
        reverso: true,
        data: dataParam || data
      });

      if (result.success && result.data) {
        setEstoqueTop(result.data);
        console.log('✅ useStock: Estoque top loaded successfully');
      } else {
        const errorMsg = result.error || 'Failed to load estoque top';
        setErrors(prev => ({ ...prev, top: errorMsg }));
        console.error('❌ useStock: Estoque top error:', errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setErrors(prev => ({ ...prev, top: errorMsg }));
      console.error('❌ useStock: Estoque top exception:', err);
    } finally {
      setLoadingTop(false);
    }
  }, [data]);

  // Load estoque crítico
  const loadEstoqueCritico = useCallback(async (dataParam?: string) => {
    console.log('⚠️ useStock: Loading estoque crítico...');
    setLoadingCritico(true);
    setErrors(prev => ({ ...prev, critico: null }));

    try {
      const result = await stockService.getEstoqueCritico({
        limite: 10,
        data: dataParam || data
      });

      if (result.success && result.data) {
        setEstoqueCritico(result.data);
        console.log('✅ useStock: Estoque crítico loaded successfully');
      } else {
        const errorMsg = result.error || 'Failed to load estoque crítico';
        setErrors(prev => ({ ...prev, critico: errorMsg }));
        console.error('❌ useStock: Estoque crítico error:', errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setErrors(prev => ({ ...prev, critico: errorMsg }));
      console.error('❌ useStock: Estoque crítico exception:', err);
    } finally {
      setLoadingCritico(false);
    }
  }, [data]);

  // Load produtos movimentados
  const loadProdutosMovimentados = useCallback(async (dataParam?: string) => {
    console.log('🔄 useStock: Loading produtos movimentados...');
    setLoadingMovimentados(true);
    setErrors(prev => ({ ...prev, movimentados: null }));

    try {
      const result = await stockService.getProdutosMaisMovimentados({
        limite: 10,
        data: dataParam || data
      });

      if (result.success && result.data) {
        setProdutosMovimentados(result.data);
        console.log('✅ useStock: Produtos movimentados loaded successfully');
      } else {
        const errorMsg = result.error || 'Failed to load produtos movimentados';
        setErrors(prev => ({ ...prev, movimentados: errorMsg }));
        console.error('❌ useStock: Produtos movimentados error:', errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setErrors(prev => ({ ...prev, movimentados: errorMsg }));
      console.error('❌ useStock: Produtos movimentados exception:', err);
    } finally {
      setLoadingMovimentados(false);
    }
  }, [data]);

  // Load movimentações período
  const loadMovimentacoesPeriodo = useCallback(async (
    dataInicio: string, 
    dataFim: string, 
    incluirDetalhes: boolean = false
  ) => {
    console.log('📅 useStock: Loading movimentações período...');
    setLoadingPeriodo(true);
    setErrors(prev => ({ ...prev, periodo: null }));

    try {
      const result = await stockService.getMovimentacoesPeriodo({
        data_inicio: dataInicio,
        data_fim: dataFim,
        incluir_detalhes: incluirDetalhes
      });

      if (result.success && result.data) {
        setMovimentacoesPeriodo(result.data);
        console.log('✅ useStock: Movimentações período loaded successfully');
      } else {
        const errorMsg = result.error || 'Failed to load movimentações período';
        setErrors(prev => ({ ...prev, periodo: errorMsg }));
        console.error('❌ useStock: Movimentações período error:', errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setErrors(prev => ({ ...prev, periodo: errorMsg }));
      console.error('❌ useStock: Movimentações período exception:', err);
    } finally {
      setLoadingPeriodo(false);
    }
  }, []);

  // Load all data
  const loadAllData = useCallback(async (dataParam?: string) => {
    console.log('🚀 useStock: Loading all stock data...');
    setLoading(true);
    clearErrors();

    try {
      // Test connection first
      await testConnection();

      if (!backendConnected) {
        setError('Backend is not connected. Cannot load stock data.');
        return;
      }

      // Load all data in parallel
      await Promise.all([
        loadEstoqueGeral({ data: dataParam }),
        loadEstoqueTop(dataParam),
        loadEstoqueCritico(dataParam),
        loadProdutosMovimentados(dataParam)
      ]);

      console.log('✅ useStock: All data loaded successfully');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load stock data';
      setError(errorMsg);
      console.error('❌ useStock: Load all data error:', err);
    } finally {
      setLoading(false);
    }
  }, [backendConnected, testConnection, loadEstoqueGeral, loadEstoqueTop, loadEstoqueCritico, loadProdutosMovimentados, clearErrors]);

  // Computed values
  const totalProdutos = estoqueGeral?.estatisticas?.total_produtos || 0;
  const valorTotalEstoque = estoqueGeral?.estatisticas?.valor_total_atual || 0;
  const produtosComEstoque = estoqueGeral?.estatisticas?.produtos_com_estoque || 0;
  const produtosZerados = estoqueGeral?.estatisticas?.produtos_zerados || 0;

  // Auto-load effect
  useEffect(() => {
    if (autoLoad) {
      console.log('🔄 useStock: Auto-loading data...');
      testConnection();
    }
  }, [autoLoad, testConnection]);

  // Load data when connection is established
  useEffect(() => {
    if (backendConnected && autoLoad) {
      loadAllData(data);
    }
  }, [backendConnected, autoLoad, data, loadAllData]);

  return {
    // Data
    estoqueGeral,
    estoqueTop,
    estoqueCritico,
    produtosMovimentados,
    movimentacoesPeriodo,
    
    // Loading states
    loading,
    loadingGeral,
    loadingTop,
    loadingCritico,
    loadingMovimentados,
    loadingPeriodo,
    
    // Error states
    error,
    errors,
    
    // Connection
    backendConnected,
    
    // Actions
    loadAllData,
    loadEstoqueGeral,
    loadEstoqueTop,
    loadEstoqueCritico,
    loadProdutosMovimentados,
    loadMovimentacoesPeriodo,
    testConnection,
    clearErrors,
    
    // Computed values
    totalProdutos,
    valorTotalEstoque,
    produtosComEstoque,
    produtosZerados,
  };
};

export default useStock;