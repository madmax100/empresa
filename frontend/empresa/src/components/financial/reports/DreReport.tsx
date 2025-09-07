// src/components/reports/DREReport.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import {
  AlertCircle,
  Download,
} from "lucide-react";
import { financialService } from '@/services/financialService';
import { 
  FluxoCaixaFiltros 
} from '@/types/financeiro';
import { DashboardEstrategico } from '@/types/dashboardNovo';
import { DateRangePicker } from '../../common/DataRangerPicker';

const DREReport: React.FC = () => {
  // Estados
  const [data, setData] = useState<DashboardEstrategico | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FluxoCaixaFiltros>({
    data_inicial: new Date().toISOString().split('T')[0],
    data_final: new Date().toISOString().split('T')[0],
    tipo: 'todos',
    fonte: 'todos',
    status: 'todos'
  });

  useEffect(() => {
    const loadDataAsync = async () => {
      try {
        setLoading(true);
        const dashboardData = await financialService.getDashboardEstrategico();
        setData(dashboardData);
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar DRE:', err);
        setError('Falha ao carregar dados do DRE');
      } finally {
        setLoading(false);
      }
    };
    
    loadDataAsync();
  }, [filters]);

  // Funções auxiliares
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  // Handler para exportação
  const handleExport = async () => {
    try {
      const blob = await financialService.getRelatorioDRE();
      financialService.exportarRelatorio(blob, 'dre.xlsx');
    } catch (err) {
      console.error('Erro ao exportar:', err);
      setError('Falha ao exportar relatório');
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
    <div className="container mx-auto p-6 space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Header com filtros */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Demonstração do Resultado</h1>
        <div className="flex gap-4">
          <DateRangePicker
            date={{
              from: new Date(filters.data_inicial),
              to: new Date(filters.data_final)
            }}
            onDateChange={range => setFilters(prev => ({
              ...prev,
              data_inicial: range?.from?.toISOString().split('T')[0] || '',
              data_final: range?.to?.toISOString().split('T')[0] || ''
            }))}
          />
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {data && (
        <>
          {/* Indicadores Principais */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">
                  Margem Operacional
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {data.indicadores.margem_operacional.toFixed(2)}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">
                  Crescimento de Receitas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {data.indicadores.crescimento_receitas.toFixed(2)}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">
                  Liquidez
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {data.indicadores.liquidez_imediata.toFixed(2)}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* DRE */}
          <Card>
            <CardHeader>
              <CardTitle>Demonstração do Resultado</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableBody>
                  <TableRow>
                    <TableCell className="font-medium">Receita Bruta</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(data.dre.receita_bruta)}
                    </TableCell>
                    <TableCell className="text-right w-24">100%</TableCell>
                  </TableRow>

                  <TableRow className="font-semibold">
                    <TableCell>Receita Líquida</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(data.dre.receita_liquida)}
                    </TableCell>
                    <TableCell className="text-right">
                      {((data.dre.receita_liquida / data.dre.receita_bruta) * 100).toFixed(1)}%
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell>Resultado Operacional</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(data.dre.resultado_operacional)}
                    </TableCell>
                    <TableCell className="text-right">
                      {((data.dre.resultado_operacional / data.dre.receita_bruta) * 100).toFixed(1)}%
                    </TableCell>
                  </TableRow>

                  <TableRow className="font-bold">
                    <TableCell>Resultado Líquido</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(data.dre.resultado_liquido)}
                    </TableCell>
                    <TableCell className="text-right">
                      {((data.dre.resultado_liquido / data.dre.receita_bruta) * 100).toFixed(1)}%
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Gráfico de Tendências */}
          <Card>
            <CardHeader>
              <CardTitle>Tendências de Receita</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.tendencias.receitas}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="periodo" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="valor_realizado"
                      name="Realizado"
                      stroke="#10b981"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="valor_previsto"
                      name="Previsto"
                      stroke="#3b82f6"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Projeções */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">
                  Projeção 30 dias
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(data.projecoes.proximos_30_dias.saldo_projetado)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">
                  Projeção 90 dias
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(data.projecoes.proximos_90_dias.saldo_projetado)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">
                  Projeção 180 dias
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(data.projecoes.proximos_180_dias.saldo_projetado)}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
};

export default DREReport;