import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { 
  BarChart, 
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { contractIndicatorsService } from '@/services/contractIndicatorsService';
import type { IndicadorGeral } from '@/services/contractIndicatorsService';
import { Download } from 'lucide-react';

const ContractIndicators = () => {
  const [indicadoresGerais, setIndicadoresGerais] = useState<IndicadorGeral | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodoAnalise, setPeriodoAnalise] = useState(12);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const indicadores = await contractIndicatorsService.getIndicadoresGerais();
        console.log('Dados carregados:', { indicadores });
        setIndicadoresGerais(indicadores);
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
        setError('Erro ao carregar indicadores. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [periodoAnalise]);

  const handleExportData = () => {
    console.log('Exportando dados...');
  };

  const renderIndicadores = () => {
    if (!indicadoresGerais?.indicadores_base) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {['Total de Contratos', 'Total de Itens', 'Valor Total', 'Valor Médio por Item'].map((title) => (
            <Card key={title}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">Carregando...</div>
              </CardContent>
            </Card>
          ))}
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total de Contratos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {indicadoresGerais.indicadores_base.total_contratos}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total de Itens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {indicadoresGerais.indicadores_base.total_itens}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Valor Total dos Contratos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {contractIndicatorsService.formatarMoeda(
                Number(indicadoresGerais.indicadores_base.valor_total_contratos)
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Valor Médio por Item</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {contractIndicatorsService.formatarMoeda(
                Number(indicadoresGerais.indicadores_base.valor_medio_item)
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderContratosPorTipo = () => {
    if (!indicadoresGerais?.contratos_por_tipo) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle>Contratos por Tipo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={indicadoresGerais.contratos_por_tipo}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="tipo" />
                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                <Tooltip 
                  formatter={(value: any, name: string) => {
                    if (name === 'Valor Total') {
                      return [contractIndicatorsService.formatarMoeda(Number(value)), name];
                    }
                    return [value, name];
                  }}
                />
                <Legend />
                <Bar yAxisId="left" dataKey="quantidade" name="Quantidade" fill="#8884d8" />
                <Bar yAxisId="right" dataKey="valor_total" name="Valor Total" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderVencimentosProximos = () => {
    if (!indicadoresGerais?.vencimentos_proximos?.length) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle>Vencimentos Próximos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contrato
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cliente
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vencimento
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {indicadoresGerais.vencimentos_proximos.map((vencimento) => (
                  <tr key={vencimento.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {vencimento.contrato}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {vencimento.cliente}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {contractIndicatorsService.formatarMoeda(Number(vencimento.valor))}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {format(new Date(vencimento.fim), 'dd/MM/yyyy')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    );
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Erro</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard de Contratos</h1>
        <div className="flex gap-4">
          <Select 
            value={periodoAnalise.toString()} 
            onValueChange={(value) => setPeriodoAnalise(Number(value))}
          >
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Período" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="3">Últimos 3 meses</SelectItem>
              <SelectItem value="6">Últimos 6 meses</SelectItem>
              <SelectItem value="12">Último ano</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={handleExportData}>
            <Download className="mr-2 h-4 w-4" />
            Exportar
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
          <>
            {renderIndicadores()}
            {renderContratosPorTipo()}
            {renderVencimentosProximos()}
          </>
        )}
      </div>
    </div>
  );
};

export default ContractIndicators;