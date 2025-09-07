import { useState, useCallback } from 'react';
import type { ContratoLocacao, ItemContratoLocacao, FiltrosContratos, ContratosDashboard } from '../types/contratos';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const useContratos = () => {
  const [contratos, setContratos] = useState<ContratoLocacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchContratos = useCallback(async (filtros?: FiltrosContratos) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (filtros?.cliente) params.append('cliente__nome__icontains', filtros.cliente);
      if (filtros?.contrato) params.append('contrato__icontains', filtros.contrato);
      if (filtros?.dataInicio) params.append('inicio__gte', filtros.dataInicio);
      if (filtros?.dataFim) params.append('fim__lte', filtros.dataFim);
      if (filtros?.renovado && filtros.renovado !== 'todos') params.append('renovado', filtros.renovado);
      
      const queryString = params.toString();
      const url = queryString ? `${API_BASE_URL}/contratos_locacao/?${queryString}` : `${API_BASE_URL}/contratos_locacao/`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Erro ao buscar contratos');
      
      const data = await response.json();
      setContratos(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      setContratos([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchContrato = useCallback(async (id: number): Promise<ContratoLocacao | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/contratos_locacao/${id}/`);
      if (!response.ok) throw new Error('Erro ao buscar contrato');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      return null;
    }
  }, []);

  const fetchItensContrato = useCallback(async (contratoId?: number): Promise<ItemContratoLocacao[]> => {
    try {
      const url = contratoId 
        ? `${API_BASE_URL}/itens_contrato_locacao/?contrato=${contratoId}`
        : `${API_BASE_URL}/itens_contrato_locacao/`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Erro ao buscar itens do contrato');
      
      const data = await response.json();
      return Array.isArray(data) ? data : data.results || [];
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      return [];
    }
  }, []);

  return {
    contratos,
    loading,
    error,
    fetchContratos,
    fetchContrato,
    fetchItensContrato,
  };
};

export const useContratosDashboard = () => {
  const [dashboard, setDashboard] = useState<ContratosDashboard | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calcularDashboard = useCallback((contratos: ContratoLocacao[]): ContratosDashboard => {
    const hoje = new Date();
    const contratosAtivos = contratos.filter(contrato => new Date(contrato.fim) >= hoje);
    const contratosInativos = contratos.filter(contrato => new Date(contrato.fim) < hoje);
    
    const valorTotalContratos = contratos.reduce((sum, contrato) => sum + contrato.valorcontrato, 0);
    const valorMedioContrato = contratos.length > 0 ? valorTotalContratos / contratos.length : 0;
    
    // Agrupar por tipo de contrato
    const tiposMap = new Map<number, { quantidade: number; valorTotal: number }>();
    contratos.forEach(contrato => {
      const atual = tiposMap.get(contrato.tipocontrato) || { quantidade: 0, valorTotal: 0 };
      tiposMap.set(contrato.tipocontrato, {
        quantidade: atual.quantidade + 1,
        valorTotal: atual.valorTotal + contrato.valorcontrato
      });
    });
    
    const distribuicaoTipos = Array.from(tiposMap.entries()).map(([tipo, dados]) => ({
      tipo,
      ...dados
    }));

    // Calcular evolução mensal (últimos 12 meses)
    const evolutionMensal = [];
    for (let i = 11; i >= 0; i--) {
      const data = new Date();
      data.setMonth(data.getMonth() - i);
      const mesInicio = new Date(data.getFullYear(), data.getMonth(), 1);
      const mesFim = new Date(data.getFullYear(), data.getMonth() + 1, 0);
      
      const contratosMes = contratos.filter(contrato => {
        const dataContrato = new Date(contrato.data);
        return dataContrato >= mesInicio && dataContrato <= mesFim;
      });
      
      const renovacoesMes = contratosMes.filter(c => c.renovado === 'SIM').length;
      const valorMes = contratosMes.reduce((sum, c) => sum + c.valorcontrato, 0);
      
      evolutionMensal.push({
        mes: `${data.getFullYear()}-${(data.getMonth() + 1).toString().padStart(2, '0')}`,
        novosContratos: contratosMes.length,
        renovacoes: renovacoesMes,
        valor: valorMes
      });
    }

    return {
      totalContratos: contratos.length,
      contratosAtivos: contratosAtivos.length,
      contratosInativos: contratosInativos.length,
      totalMaquinas: contratos.reduce((sum, contrato) => sum + contrato.totalmaquinas, 0),
      valorTotalContratos,
      valorMedioContrato,
      distribuicaoTipos,
      evolutionMensal
    };
  }, []);

  const fetchDashboard = useCallback(async (filtros?: FiltrosContratos) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (filtros?.cliente) params.append('cliente__nome__icontains', filtros.cliente);
      if (filtros?.dataInicio) params.append('inicio__gte', filtros.dataInicio);
      if (filtros?.dataFim) params.append('fim__lte', filtros.dataFim);
      
      const queryString = params.toString();
      const url = queryString ? `${API_BASE_URL}/contratos_locacao/?${queryString}` : `${API_BASE_URL}/contratos_locacao/`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Erro ao buscar dados para dashboard');
      
      const data = await response.json();
      const contratos = Array.isArray(data) ? data : data.results || [];
      
      const dashboardData = calcularDashboard(contratos);
      setDashboard(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      setDashboard(null);
    } finally {
      setLoading(false);
    }
  }, [calcularDashboard]);

  return {
    dashboard,
    loading,
    error,
    fetchDashboard,
  };
};
