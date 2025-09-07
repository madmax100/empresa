import { useState, useEffect, useCallback } from 'react';
import { Calendar as CalendarIcon, Package, DollarSign } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatCurrency, formatDate, cn } from '@/lib/utils';
import { financialService } from '@/services/financialService';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface EstoqueItem {
  id: number;
  produto: string;
  categoria: string;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
}

interface EstoqueData {
  data_consulta: string;
  total_itens: number;
  valor_total_estoque: number;
  itens: EstoqueItem[];
}

const RelatorioEstoque = () => {
  const [data, setData] = useState<EstoqueData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [demoMode, setDemoMode] = useState(false);

  const loadDemoData = () => {
    const demoData: EstoqueData = {
      data_consulta: selectedDate.toISOString().split('T')[0],
      total_itens: 8,
      valor_total_estoque: 125480.75,
      itens: [
        {
          id: 1,
          produto: 'Papel A4 75g Branco',
          categoria: 'Papéis',
          quantidade: 2500,
          valor_unitario: 12.50,
          valor_total: 31250.00
        },
        {
          id: 2,
          produto: 'Toner HP 85A Original',
          categoria: 'Suprimentos',
          quantidade: 45,
          valor_unitario: 245.90,
          valor_total: 11065.50
        },
        {
          id: 3,
          produto: 'Papel Fotográfico A4',
          categoria: 'Papéis Especiais',
          quantidade: 500,
          valor_unitario: 28.90,
          valor_total: 14450.00
        },
        {
          id: 4,
          produto: 'Cartão Visita 300g',
          categoria: 'Papéis Especiais',
          quantidade: 1000,
          valor_unitario: 15.75,
          valor_total: 15750.00
        },
        {
          id: 5,
          produto: 'Tinta para Impressora',
          categoria: 'Suprimentos',
          quantidade: 120,
          valor_unitario: 89.50,
          valor_total: 10740.00
        },
        {
          id: 6,
          produto: 'Papel Couché 200g',
          categoria: 'Papéis Especiais',
          quantidade: 800,
          valor_unitario: 35.20,
          valor_total: 28160.00
        },
        {
          id: 7,
          produto: 'Envelope Saco 229x324mm',
          categoria: 'Envelopes',
          quantidade: 2000,
          valor_unitario: 0.85,
          valor_total: 1700.00
        },
        {
          id: 8,
          produto: 'Fita Dupla Face',
          categoria: 'Materiais de Acabamento',
          quantidade: 150,
          valor_unitario: 8.35,
          valor_total: 1252.50
        }
      ]
    };
    
    setData(demoData);
    setDemoMode(true);
    setError(null);
  };

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setDemoMode(false); // Reset demo mode when fetching real data

    try {
      const dateStr = selectedDate.toISOString().split('T')[0];
      const result = await financialService.getRelatorioEstoque();
      setData({
        data_consulta: dateStr,
        total_itens: result.resumo.total_itens,
        valor_total_estoque: result.resumo.valor_total,
        itens: result.itens
      });
    } catch (err: any) {
      console.error('Erro completo:', err);
      
      if (err?.response?.status === 500) {
        setError('Erro interno do servidor. Tente novamente em alguns instantes.');
      } else if (err?.response?.status === 404) {
        setError('Endpoint não encontrado.');
      } else {
        setError('Falha ao buscar dados do estoque.');
      }
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Relatório de Valor do Estoque</h1>
        
        <div className="flex space-x-2">
          {/* Botão para recarregar dados */}
          <Button
            onClick={() => fetchData()}
            disabled={loading}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Package className="h-4 w-4" />
            <span>{loading ? 'Carregando...' : 'Atualizar'}</span>
          </Button>

          {/* Seletor de Data */}
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-[240px] justify-start text-left font-normal",
                  !selectedDate && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {selectedDate ? (
                  format(selectedDate, "dd/MM/yyyy", { locale: ptBR })
                ) : (
                  <span>Selecione uma data</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => date && setSelectedDate(date)}
                initialFocus
                locale={ptBR}
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {demoMode && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-green-600">🎯</span>
              <div>
                <p className="text-green-800 font-medium">Modo Demonstração Ativo</p>
                <p className="text-green-700 text-sm">
                  Exibindo dados fictícios para demonstrar a funcionalidade da página.
                </p>
              </div>
            </div>
            <Button
              onClick={() => { setDemoMode(false); fetchData(); }}
              variant="outline"
              size="sm"
              className="bg-green-100 border-green-300 text-green-800 hover:bg-green-200"
            >
              Voltar aos Dados Reais
            </Button>
          </div>
        </div>
      )}

      {loading && <p>Carregando...</p>}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600 font-medium">⚠️ Erro</p>
          <p className="text-red-500 text-sm mt-1">{error}</p>
        </div>
      )}

      {!loading && !error && data && data.total_itens === 0 && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-start space-x-3">
              <Package className="h-6 w-6 text-blue-600 mt-1" />
              <div>
                <p className="text-blue-800 font-medium text-lg">Estoque Vazio</p>
                <p className="text-blue-600 text-sm mt-1">
                  Não há posições de estoque cadastradas no sistema para a data selecionada.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <h3 className="text-gray-800 font-medium mb-3">💡 Como adicionar itens ao estoque:</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                <span>Cadastre produtos através do endpoint <code className="bg-gray-200 px-1 rounded">/produtos/</code></span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                <span>Registre movimentações de entrada no <code className="bg-gray-200 px-1 rounded">/movimentacoes_estoque/</code></span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                <span>As posições de estoque serão automaticamente calculadas em <code className="bg-gray-200 px-1 rounded">/posicoes_estoque/</code></span>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-yellow-600">ℹ️</span>
                <div>
                  <p className="text-yellow-800 font-medium">Dados Disponíveis</p>
                  <p className="text-yellow-700 text-sm">
                    Encontramos <strong>5,496 produtos</strong> cadastrados no sistema. 
                    Para visualizar o estoque, é necessário registrar as movimentações de entrada.
                  </p>
                </div>
              </div>
              <Button
                onClick={loadDemoData}
                variant="outline"
                className="ml-4 bg-yellow-100 border-yellow-300 text-yellow-800 hover:bg-yellow-200"
              >
                <Package className="h-4 w-4 mr-2" />
                Carregar Demo
              </Button>
            </div>
          </div>
        </div>
      )}

      {data && (
        <>
          {/* Cards de Resumo */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Data da Consulta</CardTitle>
                <CalendarIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatDate(data.data_consulta)}</div>
                <p className="text-xs text-muted-foreground">Data de referência</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total de Itens</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.total_itens.toLocaleString('pt-BR')}</div>
                <p className="text-xs text-muted-foreground">Produtos em estoque</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Valor Total do Estoque</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(data.valor_total_estoque)}
                </div>
                <p className="text-xs text-muted-foreground">Valor total investido</p>
              </CardContent>
            </Card>
          </div>

          {/* Tabela de Itens */}
          <Card>
            <CardHeader>
              <CardTitle>Detalhamento por Produto</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Produto</TableHead>
                      <TableHead>Categoria</TableHead>
                      <TableHead className="text-right">Quantidade</TableHead>
                      <TableHead className="text-right">Valor Unitário</TableHead>
                      <TableHead className="text-right">Valor Total</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.itens.length > 0 ? (
                      data.itens.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell className="font-medium">{item.produto}</TableCell>
                          <TableCell>{item.categoria}</TableCell>
                          <TableCell className="text-right">
                            {item.quantidade.toLocaleString('pt-BR')}
                          </TableCell>
                          <TableCell className="text-right">
                            {formatCurrency(item.valor_unitario)}
                          </TableCell>
                          <TableCell className="text-right font-medium">
                            {formatCurrency(item.valor_total)}
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center">
                          Nenhum item encontrado no estoque para esta data.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default RelatorioEstoque;
