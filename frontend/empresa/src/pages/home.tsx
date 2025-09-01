import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { financialService } from '@/services/financialService';
import {
  DashboardGerencial,
  DashboardOperacional,
  DashboardEstrategico,
  Filtros
} from '@/types/dashboardNovo';
import { DashboardFilter } from '@/components/dashboard/dashboardFilter';
import OperationalDashboard from './dashboard/OperationalDashboard';
import { ManagementDashboard } from './dashboard/ManagementDashboard';
import { StrategicDashboard } from './dashboard/StrategicDashboard';

interface DashboardState {
  operacional: DashboardOperacional | null;
  estrategico: DashboardEstrategico | null;
  gerencial: DashboardGerencial | null;
}

const Home: React.FC = () => {
  // Estados
  const [activeTab, setActiveTab] = useState('operacional');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DashboardState>({
    operacional: null,
    estrategico: null,
    gerencial: null
  });

  // Estado dos filtros - restringindo a partir de 01/01/2024
  const [filters, setFilters] = useState<Filtros>(() => {
    const today = new Date();
    const minDate = new Date('2024-01-01');
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    
    // Se o primeiro dia do mês atual for anterior a janeiro 2024, usar 2024-01-01
    const startDate = firstDay < minDate ? minDate : firstDay;
    
    const toISO = (d: Date) => d.toISOString().split('T')[0];
    console.log('🏠 Inicializando filtros:', {
      startDate: toISO(startDate),
      endDate: toISO(today),
      minDate: toISO(minDate)
    });
    
    return {
      dataInicial: toISO(startDate),
      dataFinal: toISO(today),
      tipo: 'todos',
      fonte: 'todos'
    };
  });

  // Função para carregar dados do dashboard
  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const apiFilters = {
        dataInicial: filters.dataInicial,
        dataFinal: filters.dataFinal,
        tipo: filters.tipo,
        fonte: filters.fonte
      };

      switch (activeTab) {
        case 'operacional': {
          const dashboardData = await financialService.getDashboardOperacional(apiFilters);
          setData(prev => ({ ...prev, operacional: dashboardData }));
          break;
        }
        case 'estrategico': {
          const dashboardData = await financialService.getDashboardEstrategico(apiFilters);
          setData(prev => ({ ...prev, estrategico: dashboardData }));
          break;
        }
        case 'gerencial': {
          const dashboardData = await financialService.getDashboardGerencial(apiFilters);
          setData(prev => ({ ...prev, gerencial: dashboardData }));
          break;
        }
      }
    } catch (error: any) {
      setError(error?.response?.data?.detail || 'Erro ao carregar dados do dashboard');
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setLoading(false);
    }
  }, [activeTab, filters]);

  // Carregar dados quando os filtros ou a aba mudar
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Handler para mudança de filtros com validação de data mínima
  const handleFilterChange = (newFilters: Partial<Filtros>) => {
    const minDate = '2024-01-01';
    
    console.log('🔄 Alterando filtros:', newFilters);
    
    // Validar se as datas não são anteriores a 01/01/2024
    const updatedFilters = { ...newFilters };
    
    if (updatedFilters.dataInicial && updatedFilters.dataInicial < minDate) {
      console.log('⚠️ Data inicial ajustada de', updatedFilters.dataInicial, 'para', minDate);
      updatedFilters.dataInicial = minDate;
    }
    
    if (updatedFilters.dataFinal && updatedFilters.dataFinal < minDate) {
      console.log('⚠️ Data final ajustada de', updatedFilters.dataFinal, 'para', minDate);
      updatedFilters.dataFinal = minDate;
    }
    
    setFilters(prev => ({ ...prev, ...updatedFilters }));
  };

  // Handler para mudança de status de movimentação
  const handleMovementStatusChange = async (id: number) => {
    try {
      setLoading(true);
      await financialService.realizarLancamento(id);
      await loadDashboardData();
    } catch (error: any) {
      setError(error?.response?.data?.detail || 'Erro ao atualizar status do movimento');
      console.error('Erro ao atualizar status:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handler para exportação
  const handleExport = async () => {
    try {
      setLoading(true);
      const blob = await financialService.getRelatorioFluxoCaixa(
        {
          inicio: filters.dataInicial,
          fim: filters.dataFinal
        },
        'excel'
      );
      financialService.exportarRelatorio(blob, 'fluxo-caixa.xlsx');
    } catch (error: any) {
      setError(error?.response?.data?.detail || 'Erro ao exportar relatório');
      console.error('Erro ao exportar:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handler para atualização dos dados
  const handleRefresh = () => {
    loadDashboardData();
  };

  if (loading && !data[activeTab as keyof DashboardState]) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard Financeiro</h1>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <DashboardFilter
        filters={filters}
        onFilterChange={handleFilterChange}
        onRefresh={handleRefresh}
        onExport={handleExport}
      />

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="operacional">Operacional</TabsTrigger>
          <TabsTrigger value="estrategico">Estratégico</TabsTrigger>
          <TabsTrigger value="gerencial">Gerencial</TabsTrigger>
        </TabsList>

        <TabsContent value="operacional">
          {data.operacional && (
            <OperationalDashboard
              data={data.operacional}
              loading={loading}
              onFiltrosChange={handleFilterChange}
              onRefresh={handleRefresh}
              onExport={handleExport}
              onMovimentoStatusChange={handleMovementStatusChange}
            />
          )}
        </TabsContent>

        <TabsContent value="estrategico">
          {data.estrategico && (
            <StrategicDashboard
              data={data.estrategico}
              loading={loading}
              onFiltrosChange={handleFilterChange}
              onRefresh={handleRefresh}
              onExport={handleExport}
            />
          )}
        </TabsContent>

        <TabsContent value="gerencial">
          {data.gerencial && (
            <ManagementDashboard
              data={data.gerencial}
              loading={loading}
              onExport={handleExport}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Home;