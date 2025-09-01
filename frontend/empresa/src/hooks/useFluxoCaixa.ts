// hooks/useFluxoCaixa.tsx
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
    FluxoCaixaFiltros, 
    DashboardOperacional, 
    DashboardEstrategico, 
    DashboardGerencial,
    MovimentoStatus,
    Movimento
} from '../types';

interface UseFluxoCaixaReturn {
    // Estados
    dashboardOperacional: DashboardOperacional | null;
    dashboardEstrategico: DashboardEstrategico | null;
    dashboardGerencial: DashboardGerencial | null;
    filtros: FluxoCaixaFiltros;
    loading: boolean;
    error: string | null;
    
    // Funções
    setFiltros: (filtros: Partial<FluxoCaixaFiltros>) => void;
    refreshData: () => Promise<void>;
    exportData: () => Promise<void>;
    updateMovimentoStatus: (movimentoId: number, novoStatus: MovimentoStatus) => Promise<void>;
    atualizarMovimento: (movimentoId: number, dados: Partial<Movimento>) => Promise<void>;
}

const api = axios.create({
    baseURL: 'http://localhost:8000/api'
});

export const useFluxoCaixa = (): UseFluxoCaixaReturn => {
    // Estados principais
    const [dashboardOperacional, setDashboardOperacional] = useState<DashboardOperacional | null>(null);
    const [dashboardEstrategico, setDashboardEstrategico] = useState<DashboardEstrategico | null>(null);
    const [dashboardGerencial, setDashboardGerencial] = useState<DashboardGerencial | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Estado dos filtros
    const [filtros, setFiltros] = useState<FluxoCaixaFiltros>({
        dataInicial: new Date().toISOString().split('T')[0],
        dataFinal: new Date().toISOString().split('T')[0],
        tipo: 'todos',
        fonte: 'todos',
        status: 'todos'
    });

    // Função para atualizar filtros
    const handleSetFiltros = useCallback((novosFiltros: Partial<FluxoCaixaFiltros>) => {
        setFiltros(prevFiltros => ({
            ...prevFiltros,
            ...novosFiltros
        }));
    }, []);

    // Função para buscar dados dos dashboards
    const fetchDashboardData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const [operacionalRes, estrategicoRes, gerencialRes] = await Promise.all([
                api.get<DashboardOperacional>('/fluxo-caixa/operacional', { params: filtros }),
                api.get<DashboardEstrategico>('/fluxo-caixa/estrategico', { params: filtros }),
                api.get<DashboardGerencial>('/fluxo-caixa/gerencial', { params: filtros })
            ]);

            setDashboardOperacional(operacionalRes.data);
            setDashboardEstrategico(estrategicoRes.data);
            setDashboardGerencial(gerencialRes.data);

        } catch (err) {
            setError('Erro ao carregar dados do fluxo de caixa');
            console.error('Erro ao buscar dados:', err);
        } finally {
            setLoading(false);
        }
    }, [filtros]);

    // Efeito para carregar dados iniciais e ao mudar filtros
    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);

    // Função para atualizar status de um movimento
    const updateMovimentoStatus = async (movimentoId: number, novoStatus: MovimentoStatus) => {
        try {
            setLoading(true);
            await api.patch(`/fluxo-caixa/movimentos/${movimentoId}/status`, {
                status: novoStatus
            });
            await fetchDashboardData(); // Recarrega os dados após atualização
        } catch (err) {
            setError('Erro ao atualizar status do movimento');
            console.error('Erro ao atualizar status:', err);
        } finally {
            setLoading(false);
        }
    };

    // Função para atualizar dados de um movimento
    const atualizarMovimento = async (movimentoId: number, dados: Partial<Movimento>) => {
        try {
            setLoading(true);
            await api.patch(`/fluxo-caixa/movimentos/${movimentoId}`, dados);
            await fetchDashboardData(); // Recarrega os dados após atualização
        } catch (err) {
            setError('Erro ao atualizar movimento');
            console.error('Erro ao atualizar movimento:', err);
        } finally {
            setLoading(false);
        }
    };

    // Função para exportar dados
    const exportData = async () => {
        try {
            setLoading(true);
            const response = await api.post('/fluxo-caixa/export', filtros, {
                responseType: 'blob'
            });

            // Cria um link para download do arquivo
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `fluxo-caixa-${new Date().toISOString()}.xlsx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            setError('Erro ao exportar dados');
            console.error('Erro ao exportar:', err);
        } finally {
            setLoading(false);
        }
    };

    return {
        // Estados
        dashboardOperacional,
        dashboardEstrategico,
        dashboardGerencial,
        filtros,
        loading,
        error,

        // Funções
        setFiltros: handleSetFiltros,
        refreshData: fetchDashboardData,
        exportData,
        updateMovimentoStatus,
        atualizarMovimento
    };
};