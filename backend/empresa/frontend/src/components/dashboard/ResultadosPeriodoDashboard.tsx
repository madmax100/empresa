import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  TrendingUp,
  TrendingDown,
  Package,
  DollarSign,
  FileText,
  Calendar,
  Download,
  AlertTriangle
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { resultadosService, type ResultadosPeriodo, type FiltrosPeriodo } from '@/services/resultados-service';

const ResultadosPeriodoDashboard: React.FC = () => {
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
    <div className="container mx-auto p-6 space-y-6 bg-background min-h-screen">
      {/* Cabeçalho */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Resultados do Período</h1>
          <p className="text-muted-foreground">Análise de variação de estoque, lucro operacional e recebimentos</p>
        </div>
        <div className="flex items-center space-x-2 text-muted-foreground">
          <Calendar className="h-5 w-5" />
          <span className="text-sm">
            {formatDateDisplay(filtros.data_inicio)} - {formatDateDisplay(filtros.data_fim)}
          </span>
        </div>
      </div>

      {/* Filtros de Período */}
      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">Filtros de Período</CardTitle>
        </CardHeader>
        <CardContent className="p-6 pt-0">
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <Button
              className="rounded-md bg-blue-600 text-white hover:bg-blue-700"
              onClick={() => {
                const now = new Date();
                const from = new Date(now.getFullYear(), now.getMonth(), 1);
                const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                setFiltros({
                  data_inicio: from.toISOString().split('T')[0],
                  data_fim: to.toISOString().split('T')[0],
                });
              }}
            >
              Mês Atual
            </Button>
            <Button
              className="rounded-md bg-gray-500 text-white hover:bg-gray-600"
              onClick={() => {
                const now = new Date();
                const firstDayPrev = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                const lastDayPrev = new Date(now.getFullYear(), now.getMonth(), 0);
                setFiltros({
                  data_inicio: firstDayPrev.toISOString().split('T')[0],
                  data_fim: lastDayPrev.toISOString().split('T')[0],
                });
              }}
            >
              Último Mês
            </Button>
            <Button
              className="rounded-md bg-green-600 text-white hover:bg-green-700"
              onClick={() => {
                const now = new Date();
                const from = new Date(now.getFullYear(), 0, 1);
                const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                setFiltros({
                  data_inicio: from.toISOString().split('T')[0],
                  data_fim: to.toISOString().split('T')[0],
                });
              }}
            >
              Ano Atual
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Data Início</label>
              <Input
                type="date"
                value={filtros.data_inicio}
                onChange={(e) => setFiltros(prev => ({ ...prev, data_inicio: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Data Fim</label>
              <Input
                type="date"
                value={filtros.data_fim}
                onChange={(e) => setFiltros(prev => ({ ...prev, data_fim: e.target.value }))}
              />
            </div>
            <div className="flex items-end">
              <Button
                variant="destructive"
                className="w-full"
                onClick={carregarResultados}
              >
                Aplicar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Cards de Métricas Principais */}
      {resultados && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Variação de Estoque */}
            <Card className="border-l-4 border-blue-500 hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Variação de Estoque</CardTitle>
                <Package className="h-5 w-5 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {formatCurrency(resultados.variacaoEstoque.diferenca)}
                </div>
                <p className="text-xs text-muted-foreground flex items-center mt-1">
                  {resultados.variacaoEstoque.diferenca >= 0 ? (
                    <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                  ) : (
                    <TrendingDown className="h-3 w-3 mr-1 text-red-500" />
                  )}
                  {formatPercent(Math.abs(resultados.variacaoEstoque.percentual))} vs período anterior
                </p>
              </CardContent>
            </Card>

            {/* Lucro Operacional */}
            <Card className="border-l-4 border-green-500 hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Lucro Operacional</CardTitle>
                <TrendingUp className="h-5 w-5 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(resultados.lucroOperacional.lucro)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {formatPercent(resultados.lucroOperacional.margem)} de margem
                </p>
              </CardContent>
            </Card>

            {/* Contratos Recebidos */}
            <Card className="border-l-4 border-amber-500 hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Contratos Recebidos</CardTitle>
                <FileText className="h-5 w-5 text-amber-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-amber-600">
                  {formatCurrency(resultados.contratosRecebidos.valorTotal)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {resultados.contratosRecebidos.quantidadeContratos} contratos • Média: {formatCurrency(resultados.contratosRecebidos.valorMedio)}
                </p>
              </CardContent>
            </Card>

            {/* Resultado Líquido */}
            <Card className="border-l-4 border-emerald-500 hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Resultado Líquido</CardTitle>
                <DollarSign className="h-5 w-5 text-emerald-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-600">
                  {formatCurrency(resultados.resumoGeral.resultadoLiquido)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {formatPercent(resultados.resumoGeral.margem)} de margem total
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Detalhamento dos Resultados */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Variação de Estoque Detalhada */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Package className="h-5 w-5 mr-2" />
                  Detalhamento - Variação de Estoque
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Valor Anterior</p>
                      <p className="font-semibold">{formatCurrency(resultados.variacaoEstoque.valorAnterior)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Valor Atual</p>
                      <p className="font-semibold">{formatCurrency(resultados.variacaoEstoque.valorAtual)}</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <p className="text-sm text-muted-foreground">Variação Absoluta</p>
                    <p className={`font-bold ${resultados.variacaoEstoque.diferenca >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(resultados.variacaoEstoque.diferenca)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Lucro Operacional Detalhado */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Detalhamento - Lucro Operacional
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Valor de Saída</p>
                      <p className="font-semibold">{formatCurrency(resultados.lucroOperacional.valorSaida)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Valor de Entrada</p>
                      <p className="font-semibold">{formatCurrency(resultados.lucroOperacional.valorEntrada)}</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <p className="text-sm text-muted-foreground">Lucro Bruto</p>
                    <p className="font-bold text-green-600">
                      {formatCurrency(resultados.lucroOperacional.lucro)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Resumo Consolidado */}
          <Card>
            <CardHeader>
              <CardTitle>Resumo Consolidado do Período</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-lg font-semibold text-blue-600">Patrimônio</div>
                  <div className="text-2xl font-bold">{formatCurrency(resultados.variacaoEstoque.diferenca)}</div>
                  <div className="text-sm text-muted-foreground">Variação de Estoque</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-green-600">Operacional</div>
                  <div className="text-2xl font-bold">{formatCurrency(resultados.lucroOperacional.lucro)}</div>
                  <div className="text-sm text-muted-foreground">Lucro de Operações</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-amber-600">Recebimentos</div>
                  <div className="text-2xl font-bold">{formatCurrency(resultados.contratosRecebidos.valorTotal)}</div>
                  <div className="text-sm text-muted-foreground">Contratos de Locação</div>
                </div>
              </div>
              <div className="mt-6 pt-6 border-t text-center">
                <div className="text-xl font-semibold text-emerald-600">Total do Período</div>
                <div className="text-3xl font-bold text-emerald-600">
                  {formatCurrency(resultados.resumoGeral.resultadoLiquido)}
                </div>
                <div className="text-sm text-muted-foreground">
                  Resultado líquido consolidado ({formatPercent(resultados.resumoGeral.margem)} de margem)
                </div>
              </div>
            </CardContent>
          </Card>
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

export default ResultadosPeriodoDashboard;
