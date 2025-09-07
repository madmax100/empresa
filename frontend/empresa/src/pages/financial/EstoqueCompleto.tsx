import { useState, useEffect, useCallback } from 'react';
import { Calendar as CalendarIcon, Package, History, TrendingUp, RotateCcw, ChevronUp, ChevronDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { formatCurrency, formatDate, cn } from '@/lib/utils';
import { financialService } from '@/services/financialService';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface EstoqueHistorico {
  data_consulta: string;
  valor_total: number;
  total_itens: number;
  itens: Array<{
    produto_id?: number;
    produto: string;
    categoria: string;
    quantidade: number;
    valor_unitario: number;
    valor_total: number;
  }>;
}

type SortField = 'produto' | 'categoria' | 'quantidade' | 'valor_unitario' | 'valor_total';
type SortDirection = 'asc' | 'desc';

interface SaldoAtual {
  id: number;
  produto: any;
  local: any;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
  data_ultima_movimentacao: string;
  // Campos enriquecidos pelo serviço
  produto_nome?: string;
  categoria?: string;
  custo_medio?: number;
  ultima_movimentacao?: string;
}

interface MovimentacaoDia {
  id: number;
  produto: any;
  tipo_movimentacao: any;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
  data_movimentacao: string;
  documento_referencia: string;
  observacoes: string;
  // Campos enriquecidos pelo serviço
  produto_nome?: string;
  tipo_descricao?: string;
  valor_total_calculado?: number;
}

const EstoqueCompleto = () => {
  const [activeTab, setActiveTab] = useState('historico');
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estado para cada aba
  const [estoqueHistorico, setEstoqueHistorico] = useState<EstoqueHistorico | null>(null);
  const [saldosAtuais, setSaldosAtuais] = useState<SaldoAtual[]>([]);
  const [movimentacoesDia, setMovimentacoesDia] = useState<MovimentacaoDia[]>([]);

  // Estados para ordenação
  const [sortField, setSortField] = useState<SortField>('produto');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  // Função para ordenar os itens
  const sortItems = (items: any[], field: string, direction: SortDirection) => {
    return [...items].sort((a, b) => {
      let aVal = a[field];
      let bVal = b[field];
      
      // Para valores numéricos
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return direction === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      // Para strings
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
        if (direction === 'asc') {
          return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        } else {
          return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
        }
      }
      
      return 0;
    });
  };

  // Função para lidar com clique no cabeçalho da tabela
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Função para renderizar o ícone de ordenação
  const renderSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ChevronUp className="h-4 w-4 opacity-30" />;
    }
    return sortDirection === 'asc' ? 
      <ChevronUp className="h-4 w-4" /> : 
      <ChevronDown className="h-4 w-4" />;
  };

  const fetchEstoqueHistorico = useCallback(async () => {
    console.log('🔍 Iniciando fetchEstoqueHistorico...');
    setLoading(true);
    setError(null);
    try {
      const dateStr = selectedDate.toISOString().split('T')[0];
      console.log('📅 Data selecionada:', dateStr);
      const result = await financialService.getRelatorioEstoqueHistorico(dateStr);
      console.log('✅ Resultado recebido:', result);
      setEstoqueHistorico(result);
    } catch (err: any) {
      console.error('❌ Erro ao buscar estoque histórico:', err);
      setError('Falha ao buscar dados do estoque histórico.');
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  const fetchSaldosAtuais = useCallback(async () => {
    console.log('🔍 Iniciando fetchSaldosAtuais...');
    setLoading(true);
    setError(null);
    try {
      const result = await financialService.getSaldosEstoque();
      console.log('✅ Saldos recebidos:', result);
      setSaldosAtuais(result);
    } catch (err: any) {
      console.error('❌ Erro ao buscar saldos atuais:', err);
      setError('Falha ao buscar saldos atuais.');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchMovimentacoesDia = useCallback(async () => {
    console.log('🔍 Iniciando fetchMovimentacoesDia...');
    setLoading(true);
    setError(null);
    try {
      const dateStr = selectedDate.toISOString().split('T')[0];
      console.log('📅 Data para movimentações:', dateStr);
      const result = await financialService.getMovimentacoesDia();
      console.log('✅ Movimentações recebidas:', result);
      setMovimentacoesDia(result);
    } catch (err: any) {
      console.error('❌ Erro ao buscar movimentações do dia:', err);
      setError('Falha ao buscar movimentações do dia.');
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  // Buscar dados quando a aba muda
  useEffect(() => {
    console.log('🔄 Mudança de aba ou dependência. Aba ativa:', activeTab);
    switch (activeTab) {
      case 'historico':
        fetchEstoqueHistorico();
        break;
      case 'saldos':
        fetchSaldosAtuais();
        break;
      case 'movimentacoes':
        fetchMovimentacoesDia();
        break;
    }
  }, [activeTab, fetchEstoqueHistorico, fetchSaldosAtuais, fetchMovimentacoesDia]);

  const renderEstoqueHistorico = () => (
    <div className="space-y-6">
      {estoqueHistorico ? (
        <>
          {/* Cards de Resumo */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Data da Consulta</CardTitle>
                <CalendarIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatDate(estoqueHistorico.data_consulta)}</div>
                <p className="text-xs text-muted-foreground">Data de referência</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total de Itens</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{estoqueHistorico.total_itens}</div>
                <p className="text-xs text-muted-foreground">itens em estoque</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(estoqueHistorico.valor_total)}</div>
                <p className="text-xs text-muted-foreground">valor do estoque</p>
              </CardContent>
            </Card>
          </div>

          {/* Tabela de Itens */}
          <Card>
            <CardHeader>
              <CardTitle>Estoque Histórico - {formatDate(estoqueHistorico.data_consulta)}</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead 
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => handleSort('produto')}
                    >
                      <div className="flex items-center gap-2">
                        Produto
                        {renderSortIcon('produto')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => handleSort('categoria')}
                    >
                      <div className="flex items-center gap-2">
                        Categoria
                        {renderSortIcon('categoria')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="text-right cursor-pointer hover:bg-muted/50"
                      onClick={() => handleSort('quantidade')}
                    >
                      <div className="flex items-center justify-end gap-2">
                        Quantidade
                        {renderSortIcon('quantidade')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="text-right cursor-pointer hover:bg-muted/50"
                      onClick={() => handleSort('valor_unitario')}
                    >
                      <div className="flex items-center justify-end gap-2">
                        Valor Unitário
                        {renderSortIcon('valor_unitario')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="text-right cursor-pointer hover:bg-muted/50"
                      onClick={() => handleSort('valor_total')}
                    >
                      <div className="flex items-center justify-end gap-2">
                        Valor Total
                        {renderSortIcon('valor_total')}
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortItems(estoqueHistorico.itens, sortField, sortDirection).map((item, index) => (
                    <TableRow key={item.produto_id || index}>
                      <TableCell className="font-medium">{item.produto}</TableCell>
                      <TableCell>{item.categoria}</TableCell>
                      <TableCell className="text-right">{item.quantidade}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.valor_unitario)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.valor_total)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card>
          <CardContent className="p-8 text-center">
            <History className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Estoque Histórico</h3>
            <p className="text-gray-500 mb-4">
              Selecione uma data para visualizar o estoque naquele período.
            </p>
            <Button onClick={fetchEstoqueHistorico} disabled={loading}>
              <History className="h-4 w-4 mr-2" />
              {loading ? 'Carregando...' : 'Buscar Estoque Histórico'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );

  const renderSaldosAtuais = () => (
    <div className="space-y-6">
      {saldosAtuais.length > 0 ? (
        <>
          {/* Card de Resumo */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Itens com Saldo</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{saldosAtuais.length}</div>
                <p className="text-xs text-muted-foreground">produtos disponíveis</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Quantidade Total</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {saldosAtuais.reduce((sum, item) => sum + item.quantidade, 0)}
                </div>
                <p className="text-xs text-muted-foreground">unidades em estoque</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(saldosAtuais.reduce((sum, item) => sum + (item.valor_total || 0), 0))}
                </div>
                <p className="text-xs text-muted-foreground">valor atual</p>
              </CardContent>
            </Card>
          </div>

          {/* Tabela de Saldos */}
          <Card>
            <CardHeader>
              <CardTitle>Saldos Atuais de Estoque</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Produto</TableHead>
                    <TableHead>Categoria</TableHead>
                    <TableHead className="text-right">Quantidade</TableHead>
                    <TableHead className="text-right">Valor Unitário</TableHead>
                    <TableHead className="text-right">Valor Total</TableHead>
                    <TableHead className="text-right">Última Movimentação</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {saldosAtuais.map((saldo) => (
                    <TableRow key={saldo.id}>
                      <TableCell className="font-medium">
                        {saldo.produto_nome || saldo.produto?.nome || 'Produto não identificado'}
                      </TableCell>
                      <TableCell>{saldo.categoria || saldo.local?.nome || 'Local/Categoria não identificado'}</TableCell>
                      <TableCell className="text-right">{saldo.quantidade}</TableCell>
                      <TableCell className="text-right">{formatCurrency(saldo.valor_unitario || 0)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(saldo.valor_total || 0)}</TableCell>
                      <TableCell className="text-right">
                        {formatDate(saldo.data_ultima_movimentacao)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card>
          <CardContent className="p-8 text-center">
            <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Saldos Atuais</h3>
            <p className="text-gray-500 mb-4">
              Visualize todos os produtos com saldo atual em estoque.
            </p>
            <Button onClick={fetchSaldosAtuais} disabled={loading}>
              <Package className="h-4 w-4 mr-2" />
              {loading ? 'Carregando...' : 'Buscar Saldos Atuais'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );

  const renderMovimentacoesDia = () => (
    <div className="space-y-6">
      {movimentacoesDia.length > 0 ? (
        <>
          {/* Card de Resumo */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Data Selecionada</CardTitle>
                <CalendarIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatDate(selectedDate.toISOString())}</div>
                <p className="text-xs text-muted-foreground">data das movimentações</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total de Movimentações</CardTitle>
                <RotateCcw className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{movimentacoesDia.length}</div>
                <p className="text-xs text-muted-foreground">movimentações realizadas</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Valor Total Movimentado</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(movimentacoesDia.reduce((sum, mov) => sum + (mov.valor_total_calculado || mov.valor_total || 0), 0))}
                </div>
                <p className="text-xs text-muted-foreground">valor movimentado</p>
              </CardContent>
            </Card>
          </div>

          {/* Tabela de Movimentações */}
          <Card>
            <CardHeader>
              <CardTitle>Movimentações do Dia - {formatDate(selectedDate.toISOString())}</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Produto</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead className="text-right">Quantidade</TableHead>
                    <TableHead className="text-right">Valor Unitário</TableHead>
                    <TableHead className="text-right">Valor Total</TableHead>
                    <TableHead>Documento</TableHead>
                    <TableHead>Observações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {movimentacoesDia.map((movimentacao) => (
                    <TableRow key={movimentacao.id}>
                      <TableCell className="font-medium">
                        {movimentacao.produto_nome || movimentacao.produto?.nome || 'Produto não identificado'}
                      </TableCell>
                      <TableCell>
                        {movimentacao.tipo_descricao || movimentacao.tipo_movimentacao?.nome || 'Tipo não identificado'}
                      </TableCell>
                      <TableCell className="text-right">{movimentacao.quantidade}</TableCell>
                      <TableCell className="text-right">{formatCurrency(movimentacao.valor_unitario || 0)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(movimentacao.valor_total_calculado || movimentacao.valor_total || 0)}</TableCell>
                      <TableCell>{movimentacao.documento_referencia || '-'}</TableCell>
                      <TableCell>{movimentacao.observacoes || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card>
          <CardContent className="p-8 text-center">
            <RotateCcw className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Movimentações do Dia</h3>
            <p className="text-gray-500 mb-4">
              Visualize todas as movimentações de estoque realizadas na data selecionada.
            </p>
            <Button onClick={fetchMovimentacoesDia} disabled={loading}>
              <RotateCcw className="h-4 w-4 mr-2" />
              {loading ? 'Carregando...' : 'Buscar Movimentações'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Relatórios de Estoque</h1>
        
        <div className="flex space-x-2">
          {/* Seletor de Data (visível apenas para abas que precisam) */}
          {(activeTab === 'historico' || activeTab === 'movimentacoes') && (
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
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600 font-medium">⚠️ Erro</p>
          <p className="text-red-500 text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="historico" className="flex items-center space-x-2">
            <History className="h-4 w-4" />
            <span>Estoque Histórico</span>
          </TabsTrigger>
          <TabsTrigger value="saldos" className="flex items-center space-x-2">
            <Package className="h-4 w-4" />
            <span>Saldos Atuais</span>
          </TabsTrigger>
          <TabsTrigger value="movimentacoes" className="flex items-center space-x-2">
            <RotateCcw className="h-4 w-4" />
            <span>Movimentações do Dia</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="historico" className="mt-6">
          {renderEstoqueHistorico()}
        </TabsContent>

        <TabsContent value="saldos" className="mt-6">
          {renderSaldosAtuais()}
        </TabsContent>

        <TabsContent value="movimentacoes" className="mt-6">
          {renderMovimentacoesDia()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EstoqueCompleto;
