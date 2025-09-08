import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import {
  Calendar,
  Download,
  AlertTriangle
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { resultadosService, type ResultadosPeriodo, type FiltrosPeriodo } from '@/services/resultados-service';

const ResultadosDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resultados, setResultados] = useState<ResultadosPeriodo | null>(null);
  
  const defaultFrom = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // 30 dias atrás
  const defaultTo = new Date();
  
  const [filtros, setFiltros] = useState<FiltrosPeriodo>({
    data_inicio: defaultFrom.toISOString().split('T')[0],
    data_fim: defaultTo.toISOString().split('T')[0]
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatPercent = (value: number) => `${value.toFixed(1)}%`;

  const formatDateDisplay = (iso: string) => {
    const d = new Date(iso + 'T00:00:00');
    return isNaN(d.getTime()) ? iso : d.toLocaleDateString();
  };

  const carregarResultados = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔄 Carregando resultados do período...');
      console.log(`📅 Período: ${filtros.data_inicio} até ${filtros.data_fim}`);

      // Usar o serviço real para buscar os dados
      const dadosResultados = await resultadosService.buscarResultadosPeriodo(filtros);
      setResultados(dadosResultados);

      console.log('✅ Resultados carregados com sucesso:', dadosResultados);

    } catch (err) {
      console.error('❌ Erro ao carregar resultados:', err);
      setError('Falha ao carregar dados dos resultados do período');
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  useEffect(() => {
    carregarResultados();
  }, [carregarResultados]);

  const exportToCSV = () => {
    if (!resultados) return;
    
    try {
      const headers = ['Métrica', 'Valor', 'Observações'];
      const rows = [
        ['Variação de Estoque', formatCurrency(resultados.variacaoEstoque.diferenca), `${formatPercent(resultados.variacaoEstoque.percentual)} de variação`],
        ['Lucro Operacional', formatCurrency(resultados.lucroOperacional.lucro), `${formatPercent(resultados.lucroOperacional.margem)} de margem`],
        ['Contratos Recebidos', formatCurrency(resultados.contratosRecebidos.valorTotal), `${resultados.contratosRecebidos.quantidadeContratos} contratos`],
        ['Resultado Líquido', formatCurrency(resultados.resumoGeral.resultadoLiquido), `${formatPercent(resultados.resumoGeral.margem)} de margem total`]
      ];
      
      const csv = [headers.join(';'), ...rows.map(r => r.join(';'))].join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resultados_periodo_${filtros.data_inicio}_${filtros.data_fim}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Falha ao exportar CSV:', e);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* Cabeçalho */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Resultados do Período</h1>
          <p className="text-gray-600">Análise de variação de estoque, lucro operacional e recebimentos</p>
        </div>
        <div className="flex items-center space-x-2 text-gray-600">
          <Calendar className="h-5 w-5" />
          <span className="text-sm">
            {formatDateDisplay(filtros.data_inicio)} - {formatDateDisplay(filtros.data_fim)}
          </span>
        </div>
      </div>

      {/* Filtros de Período */}
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '24px'
      }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px' }}>Filtros de Período</h3>
        
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Botões de período pré-definido */}
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => {
                const now = new Date();
                const from = new Date(now.getFullYear(), now.getMonth(), 1);
                const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                setFiltros({
                  data_inicio: from.toISOString().split('T')[0],
                  data_fim: to.toISOString().split('T')[0],
                });
              }}
              style={{
                padding: '8px 16px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Mês Atual
            </button>
            <button
              onClick={() => {
                const now = new Date();
                const firstDayPrev = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                const lastDayPrev = new Date(now.getFullYear(), now.getMonth(), 0);
                setFiltros({
                  data_inicio: firstDayPrev.toISOString().split('T')[0],
                  data_fim: lastDayPrev.toISOString().split('T')[0],
                });
              }}
              style={{
                padding: '8px 16px',
                backgroundColor: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Último Mês
            </button>
            <button
              onClick={() => {
                const now = new Date();
                const from = new Date(now.getFullYear(), 0, 1);
                const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                setFiltros({
                  data_inicio: from.toISOString().split('T')[0],
                  data_fim: to.toISOString().split('T')[0],
                });
              }}
              style={{
                padding: '8px 16px',
                backgroundColor: '#059669',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Ano Atual
            </button>
          </div>

          {/* Campos de data customizados */}
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <label style={{ fontSize: '0.875rem', color: '#374151' }}>De:</label>
            <input
              type="date"
              value={filtros.data_inicio}
              onChange={(e) => setFiltros(prev => ({ ...prev, data_inicio: e.target.value }))}
              style={{
                padding: '8px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '0.875rem'
              }}
            />
            <label style={{ fontSize: '0.875rem', color: '#374151' }}>Até:</label>
            <input
              type="date"
              value={filtros.data_fim}
              onChange={(e) => setFiltros(prev => ({ ...prev, data_fim: e.target.value }))}
              style={{
                padding: '8px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '0.875rem'
              }}
            />
            <button
              onClick={carregarResultados}
              style={{
                padding: '8px 16px',
                backgroundColor: '#dc2626',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Aplicar
            </button>
          </div>
        </div>
      </div>

      {error && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Cards de Métricas Principais */}
      {resultados && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            {/* Variação de Estoque */}
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: '4px solid #3b82f6',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                Variação de Estoque
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(resultados.variacaoEstoque.diferenca)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px', display: 'flex', alignItems: 'center' }}>
                {resultados.variacaoEstoque.diferenca >= 0 ? '📈' : '📉'} {formatPercent(Math.abs(resultados.variacaoEstoque.percentual))} vs período anterior
              </div>
            </div>

            {/* Lucro Operacional */}
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: '4px solid #10b981',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                Lucro Operacional
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(resultados.lucroOperacional.lucro)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
                {formatPercent(resultados.lucroOperacional.margem)} de margem
              </div>
            </div>

            {/* Contratos Recebidos */}
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: '4px solid #f59e0b',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                Contratos Recebidos
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                {formatCurrency(resultados.contratosRecebidos.valorTotal)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
                {resultados.contratosRecebidos.quantidadeContratos} contratos • Média: {formatCurrency(resultados.contratosRecebidos.valorMedio)}
              </div>
            </div>

            {/* Resultado Líquido */}
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              borderLeft: `4px solid ${resultados.resumoGeral.resultadoLiquido >= 0 ? '#10b981' : '#ef4444'}`,
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
                Resultado Líquido
              </div>
              <div style={{ 
                fontSize: '1.5rem', 
                fontWeight: '700', 
                color: resultados.resumoGeral.resultadoLiquido >= 0 ? '#10b981' : '#ef4444'
              }}>
                {formatCurrency(resultados.resumoGeral.resultadoLiquido)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
                {formatPercent(resultados.resumoGeral.margem)} de margem total
              </div>
            </div>
          </div>

          {/* Resumo Consolidado */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            marginBottom: '24px'
          }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
              Resumo Consolidado do Período
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              <div style={{
                backgroundColor: '#f8fafc',
                padding: '16px',
                borderRadius: '6px',
                borderLeft: '3px solid #3b82f6',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#3b82f6', marginBottom: '4px' }}>
                  Patrimônio
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#111827' }}>
                  {formatCurrency(resultados.variacaoEstoque.diferenca)}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                  Variação de Estoque
                </div>
              </div>

              <div style={{
                backgroundColor: '#f0fdf4',
                padding: '16px',
                borderRadius: '6px',
                borderLeft: '3px solid #10b981',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#10b981', marginBottom: '4px' }}>
                  Operacional
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#111827' }}>
                  {formatCurrency(resultados.lucroOperacional.lucro)}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                  Lucro de Operações
                </div>
              </div>

              <div style={{
                backgroundColor: '#fffbeb',
                padding: '16px',
                borderRadius: '6px',
                borderLeft: '3px solid #f59e0b',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f59e0b', marginBottom: '4px' }}>
                  Recebimentos
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#111827' }}>
                  {formatCurrency(resultados.contratosRecebidos.valorTotal)}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                  Contratos de Locação
                </div>
              </div>
            </div>

            <div style={{ 
              marginTop: '24px', 
              paddingTop: '24px', 
              borderTop: '1px solid #e5e7eb', 
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '1.125rem', fontWeight: '600', color: '#10b981', marginBottom: '8px' }}>
                Total do Período
              </div>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: '700', 
                color: resultados.resumoGeral.resultadoLiquido >= 0 ? '#10b981' : '#ef4444',
                marginBottom: '4px'
              }}>
                {formatCurrency(resultados.resumoGeral.resultadoLiquido)}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                Resultado líquido consolidado ({formatPercent(resultados.resumoGeral.margem)} de margem)
              </div>
            </div>
          </div>
        </>
      )}

      {/* Botão de Exportação */}
      <div className="flex justify-end">
        <Button variant="outline" onClick={exportToCSV}>
          <Download className="h-4 w-4 mr-2" />
          Exportar Relatório
        </Button>
      </div>
    </div>
  );
};

export default ResultadosDashboard;
