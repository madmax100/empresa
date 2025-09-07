// src/components/financial/contracts/ContractsDashboard.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  BarChart,
  Bar,
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
  Clock,
  CheckCircle2,
  FileWarning,
  ArrowUpCircle,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { financialService } from '@/services/financialService';
import { contratosService, notasFiscaisService } from '@/services/api';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { SeparateDatePicker } from '../../common/SeparateDatePicker';

interface DadosContrato {
  id: number;
  cliente: string;
  clienteId?: number;
  contratoNumero?: string;
  equipamento: string;
  valorMensal: number;
  franquia: number;
  dataInicio: string;
  dataFim: string;
  status: string;
  copias: {
    realizadas: number;
    excedentes: number;
    valor: number;
  };
  faturamento: {
    mensal: number;
    excedentes: number;
    total: number;
  };
  manutencoes: {
    quantidade: number;
    custo: number;
  };
  suprimentos: number;
}

interface AnaliseDesempenho {
  volumeCopias: number;
  valorFaturado: number;
  custoManutencao: number;
  custoSuprimentos: number;
  margemContribuicao: number;
  tendencia: {
    copias: 'alta' | 'estavel' | 'baixa';
    custos: 'alta' | 'estavel' | 'baixa';
  };
}

interface DateRange {
  from: Date;
  to: Date;
}

interface NotaResumoDiag {
  id?: number;
  numero_nota?: string;
  data?: string;
  cfop?: string;
  operacao?: string;
  finalidade?: string;
  valor_total_nota?: number;
}

interface DiagnosticoSuprimento {
  contratoNumero?: string;
  clienteId?: number;
  cliente?: string;
  quantidade: number;
  total: number;
  amostras: NotaResumoDiag[];
}

const ContractsDashboard: React.FC = () => {
  const [contratos, setContratos] = useState<DadosContrato[]>([]);
  const defaultFrom = new Date('2024-01-01T00:00:00');
  const defaultTo = new Date();
  const [dateRange, setDateRange] = useState<DateRange>({ from: defaultFrom, to: defaultTo });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('desempenho');
  const [analiseDesempenho, setAnaliseDesempenho] = useState<AnaliseDesempenho | null>(null);
  const [usedFallback, setUsedFallback] = useState(false);
  const [mostrarDiag, setMostrarDiag] = useState(false);
  const [diagnostico, setDiagnostico] = useState<DiagnosticoSuprimento[]>([]);
  
  // Estados para expansão de linhas e notas fiscais
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [notasFiscais, setNotasFiscais] = useState<Map<number, any[]>>(new Map());
  const [loadingNotas, setLoadingNotas] = useState<Set<number>>(new Set());

  const loadContratosData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const toYmd = (d: Date) => d.toISOString().split('T')[0];
      const min = new Date('2024-01-01T00:00:00');
      const from = dateRange.from < min ? min : dateRange.from;
      const to = dateRange.to < from ? from : dateRange.to;

      // Tenta buscar análise de performance; se falhar (400/500), seguimos com fallback
      let performance: any | null = null;
      try {
        performance = await financialService.getAnalisePerformance();
      } catch (e) {
        console.warn('analise_performance indisponível, usando fallback de contratos:', e);
      }

      interface ProcessedData {
        id: number;
        cliente: string;
        clienteId?: number;
        contratoNumero?: string;
        equipamento: string;
        valorMensal: number;
        franquia: number;
        dataInicio: string;
        dataFim: string;
        status: string;
        copias: {
          realizadas: number;
          excedentes: number;
          valor: number;
        };
        faturamento: {
          mensal: number;
          excedentes: number;
          total: number;
        };
        manutencoes: {
          quantidade: number;
          custo: number;
        };
        suprimentos: number;
      }

  const resultados = Array.isArray(performance?.resultados) ? performance.resultados : [];
      
      // Calcular número de meses no período selecionado
      const diffMonths = Math.max(1, Math.round((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24 * 30.44)));
      
      let processedData: ProcessedData[] = resultados.map((result: any) => {
        // Assumindo que metricas_financeiras.faturamento é valor anual, calcular proporcional ao período
        const faturamentoAnual = result.metricas_financeiras.faturamento || 0;
        const faturamentoMensal = faturamentoAnual / 12;
        const faturamentoPeriodo = faturamentoMensal * diffMonths;
        
        return {
          id: result.contrato_id,
          cliente: result.cliente,
          clienteId: result.cliente_id,
          contratoNumero: result.contrato_numero,
          equipamento: String(result.metricas_operacionais.quantidade_equipamentos),
          valorMensal: faturamentoMensal,
          franquia: result.metricas_operacionais.quantidade_equipamentos * 5000,
          dataInicio: result.periodo_analise.inicio,
          dataFim: result.periodo_analise.fim,
          status: result.alertas.length > 0 ? 'Atenção' : 'Normal',
          copias: {
            realizadas: result.metricas_operacionais.uptime_percentual * 100000,
            excedentes: (result.metricas_operacionais.uptime_percentual * 100000) - 5000,
            valor: faturamentoPeriodo,
          },
          faturamento: {
            mensal: faturamentoMensal,
            excedentes: faturamentoPeriodo * 0.1,
            total: faturamentoPeriodo,
          },
          manutencoes: {
            quantidade: result.metricas_operacionais.manutencoes_periodo,
            custo: result.metricas_financeiras.custos,
          },
          suprimentos: 0,
        };
      });

  if (processedData.length === 0) {
        try {
          const contratos = await contratosService.listar();
          processedData = (contratos || []).map((c) => {
            const valorMensal = Number((c as any).valorpacela || (c as any).valorcontrato || 0);
            const faturamentoPeriodo = valorMensal * diffMonths;
            
            return {
              id: c.id,
              cliente: c.cliente?.nome || 'Cliente não informado',
              clienteId: c.cliente?.id,
              contratoNumero: (c as any).contrato,
              equipamento: (c.totalMaquinas as any) ?? '1',
              valorMensal: valorMensal,
              franquia: 5000,
              dataInicio: (c.inicio || c.data || new Date().toISOString()),
              dataFim: (c.fim || new Date().toISOString()),
              status: c.status || 'Normal',
              copias: {
                realizadas: 0,
                excedentes: 0,
                valor: faturamentoPeriodo,
              },
              faturamento: {
                mensal: valorMensal,
                excedentes: 0,
                total: faturamentoPeriodo,
              },
              manutencoes: {
                quantidade: 0,
                custo: 0,
              },
              suprimentos: 0,
            };
          });
          setUsedFallback(true);
          if (processedData.length === 0) {
            setError('Nenhum contrato importado foi encontrado. Verifique a importação do MS Access.');
          } else {
            setError(null);
          }
        } catch (e) {
          console.warn('Fallback contratos falhou:', e);
          setError('Falha ao carregar contratos. Verifique o backend e a importação.');
        }
      }

  // Calcular custo de suprimentos usando o novo endpoint otimizado
  const filtrosSuprimentos = { 
    data_inicial: toYmd(from), 
    data_final: toYmd(to) 
  };

      try {
        const suprimentosResponse = await contratosService.buscarSuprimentos(filtrosSuprimentos);
        
        // Criar mapa de suprimentos por contrato
        const suprimentosMapByContrato = new Map<string, number>();
        const suprimentosMapByCliente = new Map<number, number>();
        const diagnostico: DiagnosticoSuprimento[] = [];

        // Processar resultados do endpoint
        suprimentosResponse.resultados?.forEach((resultado: any) => {
          const contratoNumero = resultado.contrato_numero;
          const clienteId = resultado.cliente?.id;
          const valor = Number(resultado.suprimentos?.total_valor || 0);
          const quantidade = Number(resultado.suprimentos?.quantidade_notas || 0);
          
          if (contratoNumero && valor > 0) {
            suprimentosMapByContrato.set(contratoNumero, valor);
            
            // Converter amostras para o formato esperado
            const amostras = (resultado.suprimentos?.notas_amostra || []).map((amostra: any) => ({
              id: amostra.id,
              numero_nota: amostra.numero_nota,
              data: amostra.data,
              cfop: amostra.cfop,
              operacao: amostra.operacao,
              finalidade: amostra.finalidade || '',
              valor_total_nota: amostra.valor_total_nota,
            }));

            diagnostico.push({
              contratoNumero,
              clienteId,
              cliente: resultado.cliente?.nome || '',
              quantidade,
              total: valor,
              amostras,
            });
          }
          
          if (clienteId && valor > 0) {
            suprimentosMapByCliente.set(clienteId, valor);
          }
        });

        console.log(`Suprimentos carregados: ${diagnostico.length} contratos com remessas`);
        setDiagnostico(diagnostico);

        // Apply suprimentos costs to processedData
        processedData = processedData.map(d => {
          let supr = 0;
          if (d.contratoNumero && suprimentosMapByContrato.has(d.contratoNumero)) {
            supr = suprimentosMapByContrato.get(d.contratoNumero)!;
          } else if (d.clienteId && suprimentosMapByCliente.has(d.clienteId)) {
            supr = suprimentosMapByCliente.get(d.clienteId)!;
          }
          return { ...d, suprimentos: supr };
        });

      } catch (suprimentosError) {
        console.error('Erro ao carregar suprimentos:', suprimentosError);
        // Continue sem suprimentos em caso de erro
        setDiagnostico([]);
      }

      setContratos(processedData);

    if (processedData.length > 0) {
        const analise: AnaliseDesempenho = {
          volumeCopias: processedData.reduce((acc: number, curr: DadosContrato) => acc + curr.copias.realizadas, 0),
          valorFaturado: processedData.reduce((acc: number, curr: DadosContrato) => acc + curr.faturamento.total, 0),
          custoManutencao: processedData.reduce((acc: number, curr: DadosContrato) => acc + (Number(curr.manutencoes.custo) || 0), 0),
          custoSuprimentos: processedData.reduce((acc: number, curr: DadosContrato) => acc + (Number(curr.suprimentos) || 0), 0),
          margemContribuicao: processedData.reduce((acc: number, curr: DadosContrato) => 
            acc + (curr.faturamento.total - (Number(curr.manutencoes.custo) || 0) - (Number(curr.suprimentos) || 0)), 0),
          tendencia: { copias: 'estavel', custos: 'estavel' },
        };
        setAnaliseDesempenho(analise);
        setError(null);
      } else {
        setAnaliseDesempenho(null);
        setError('Nenhum contrato encontrado para o período selecionado.');
      }
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      // Evita sobrescrever mensagens mais específicas
      setError((prev) => prev || 'Falha ao carregar dados dos contratos. Verifique se o backend está funcionando.');
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  useEffect(() => { loadContratosData(); }, [loadContratosData]);

  const formatCurrency = (value: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  const formatNumber = (value: number) => new Intl.NumberFormat('pt-BR').format(value);

  // Função para alternar expansão de linha
  const toggleRowExpansion = async (contratoId: number, contratoNumero?: string) => {
    const newExpandedRows = new Set(expandedRows);
    
    if (expandedRows.has(contratoId)) {
      // Contraindo a linha
      newExpandedRows.delete(contratoId);
      setExpandedRows(newExpandedRows);
    } else {
      // Expandindo a linha
      newExpandedRows.add(contratoId);
      setExpandedRows(newExpandedRows);
      
      // Carregar notas fiscais se ainda não foram carregadas
      if (!notasFiscais.has(contratoId) && contratoNumero) {
        setLoadingNotas(prev => new Set([...prev, contratoId]));
        
        try {
          const toYmd = (d: Date) => d.toISOString().split('T')[0];
          const response = await notasFiscaisService.buscarPorContrato(contratoNumero, {
            data_inicial: toYmd(dateRange.from),
            data_final: toYmd(dateRange.to)
          });
          
          setNotasFiscais(prev => new Map(prev.set(contratoId, response.results || [])));
        } catch (error) {
          console.error('Erro ao carregar notas fiscais:', error);
          setNotasFiscais(prev => new Map(prev.set(contratoId, [])));
        } finally {
          setLoadingNotas(prev => {
            const newSet = new Set(prev);
            newSet.delete(contratoId);
            return newSet;
          });
        }
      }
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

      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Gestão de Contratos</h1>
        <SeparateDatePicker
          date={dateRange}
          onDateChange={(date) => {
            if (date && date.from && date.to) setDateRange({ from: date.from, to: date.to });
          }}
        />
      </div>

      <div className="flex items-center justify-end gap-2">
        <button
          type="button"
          className="text-xs px-2 py-1 rounded border hover:bg-muted"
          onClick={() => setMostrarDiag(v => !v)}
        >
          {mostrarDiag ? 'Ocultar diagnóstico' : 'Mostrar diagnóstico'}
        </button>
      </div>

      {mostrarDiag && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Diagnóstico de Suprimentos (Remessas)</CardTitle></CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground mb-3">Mostrando quantidade e total por contrato/cliente e algumas amostras de NFs (até 5).</div>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Referência</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead className="text-right">Qtde</TableHead>
                  <TableHead className="text-right">Valor Total</TableHead>
                  <TableHead>Amostras (nº/CFOP)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {diagnostico.length === 0 && (
                  <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground py-6">Nenhuma remessa encontrada no período.</TableCell></TableRow>
                )}
                {diagnostico.map((d, i) => (
                  <TableRow key={i}>
                    <TableCell>{d.contratoNumero ? `Contrato ${d.contratoNumero}` : (d.cliente ? `Cliente ${d.cliente}` : `Cliente #${d.clienteId}`)}</TableCell>
                    <TableCell>{d.cliente || '-'}</TableCell>
                    <TableCell className="text-right">{d.quantidade}</TableCell>
                    <TableCell className="text-right">{formatCurrency(d.total)}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-2">
                        {d.amostras.map((n, idx) => (
                          <span key={idx} className="text-xs px-2 py-1 rounded bg-muted">
                            {n.numero_nota || n.id} / {n.cfop || '-'}
                          </span>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {analiseDesempenho && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Volume de Cópias</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(analiseDesempenho.volumeCopias)}</div>
              <div className="flex items-center text-sm"><Clock className="h-4 w-4 mr-1 text-blue-500" /><span>Total no período</span></div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Faturamento</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{formatCurrency(analiseDesempenho.valorFaturado)}</div>
              <div className="flex items-center text-sm"><ArrowUpCircle className="h-4 w-4 mr-1 text-green-500" /><span>Total faturado</span></div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Custo Manutenção</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{formatCurrency(analiseDesempenho.custoManutencao)}</div>
              <div className="flex items-center text-sm"><FileWarning className="h-4 w-4 mr-1 text-red-500" /><span>Total custos</span></div>
              {usedFallback && (
                <div className="mt-2 text-xs text-muted-foreground">Dados de manutenção indisponíveis no momento (exibindo 0 por falta de dados de performance).</div>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Custo de Suprimentos</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-amber-600">{formatCurrency(analiseDesempenho.custoSuprimentos)}</div>
              <div className="flex items-center text-sm"><FileWarning className="h-4 w-4 mr-1 text-amber-500" /><span>Remessas (simples remessa)</span></div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Margem</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{formatCurrency(analiseDesempenho.margemContribuicao)}</div>
              <div className="flex items-center text-sm"><CheckCircle2 className="h-4 w-4 mr-1 text-purple-500" /><span>Margem total</span></div>
            </CardContent>
          </Card>
        </div>
      )}

      {!analiseDesempenho && !loading && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              <AlertCircle className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Nenhum dado encontrado</h3>
              <p>Não foram encontrados contratos para o período selecionado.</p>
              <p className="text-sm mt-2">Tente ajustar o período ou verificar se existem contratos cadastrados.</p>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="desempenho">Desempenho</TabsTrigger>
          <TabsTrigger value="contratos">Contratos</TabsTrigger>
          <TabsTrigger value="detalhes">Detalhes</TabsTrigger>
          <TabsTrigger value="manutencao">Manutenção</TabsTrigger>
        </TabsList>

        <TabsContent value="desempenho">
          <Card>
            <CardContent className="pt-6">
              {contratos.length > 0 ? (
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={contratos}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="cliente" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="copias.realizadas" name="Cópias" stroke="#2563eb" />
                      <Line yAxisId="right" type="monotone" dataKey="faturamento.total" name="Faturamento" stroke="#16a34a" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">Sem dados para exibir no gráfico.</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contratos">
          <Card>
            <CardContent>
              <Table>
        <TableHeader>
                  <TableRow>
                    <TableHead className="w-10"></TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Equipamentos</TableHead>
                    <TableHead className="text-right">Faturamento</TableHead>
                    <TableHead className="text-right">Custo Suprimentos</TableHead>
                    <TableHead className="text-right">Margem</TableHead>
                    <TableHead className="text-right">Valor Mensal</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contratos.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center text-muted-foreground py-8">Sem contratos para o período selecionado.</TableCell>
                    </TableRow>
                  )}
          {contratos.map((contrato) => {
            const margem = contrato.faturamento.total - (contrato.manutencoes.custo || 0) - (contrato.suprimentos || 0);
            const margemPercentual = contrato.faturamento.total > 0 ? (margem / contrato.faturamento.total) * 100 : 0;
            const isExpanded = expandedRows.has(contrato.id);
            const contratoNotas = notasFiscais.get(contrato.id) || [];
            const isLoadingNotas = loadingNotas.has(contrato.id);
            
            return (
              <React.Fragment key={contrato.id}>
                <TableRow className="hover:bg-muted/50">
                  <TableCell>
                    <button
                      onClick={() => toggleRowExpansion(contrato.id, contrato.contratoNumero)}
                      className="p-1 hover:bg-muted rounded"
                      disabled={!contrato.contratoNumero}
                    >
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </button>
                  </TableCell>
                  <TableCell>{contrato.cliente}</TableCell>
                  <TableCell>{contrato.equipamento}</TableCell>
                  <TableCell className="text-right font-medium text-green-600">{formatCurrency(contrato.faturamento.total)}</TableCell>
                  <TableCell className="text-right font-medium text-amber-600">{formatCurrency(contrato.suprimentos || 0)}</TableCell>
                  <TableCell className="text-right font-medium">
                    <div className={`${margem >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(margem)}
                      <div className="text-xs text-muted-foreground">
                        {margemPercentual.toFixed(1)}%
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-right">{formatCurrency(contrato.valorMensal)}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${contrato.status === 'Normal' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>{contrato.status}</span>
                  </TableCell>
                </TableRow>
                
                {isExpanded && (
                  <TableRow>
                    <TableCell colSpan={8} className="bg-muted/30 p-0">
                      <div className="p-4">
                        <h4 className="font-medium mb-3">Notas Fiscais - {contrato.contratoNumero || 'Sem número'}</h4>
                        {isLoadingNotas ? (
                          <div className="text-center py-4 text-muted-foreground">
                            Carregando notas fiscais...
                          </div>
                        ) : contratoNotas.length > 0 ? (
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Número</TableHead>
                                <TableHead>Data</TableHead>
                                <TableHead>CFOP</TableHead>
                                <TableHead>Operação</TableHead>
                                <TableHead className="text-right">Valor</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {contratoNotas.map((nota: any, idx: number) => (
                                <TableRow key={idx}>
                                  <TableCell>{nota.numero_nota || '-'}</TableCell>
                                  <TableCell>{nota.data ? new Date(nota.data).toLocaleDateString('pt-BR') : '-'}</TableCell>
                                  <TableCell>{nota.cfop || '-'}</TableCell>
                                  <TableCell>{nota.operacao || '-'}</TableCell>
                                  <TableCell className="text-right">{formatCurrency(nota.valor_total_nota || 0)}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        ) : (
                          <div className="text-center py-4 text-muted-foreground">
                            Nenhuma nota fiscal encontrada para este contrato no período selecionado.
                          </div>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </React.Fragment>
            );
          })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="detalhes">
          <Card>
            <CardHeader>
              <CardTitle>Detalhes dos Contratos</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Nº Contrato</TableHead>
                    <TableHead>Equipamentos</TableHead>
                    <TableHead>Franquia</TableHead>
                    <TableHead>Data Início</TableHead>
                    <TableHead>Data Fim</TableHead>
                    <TableHead className="text-right">Cópias Realizadas</TableHead>
                    <TableHead className="text-right">Cópias Excedentes</TableHead>
                    <TableHead className="text-right">Valor Excedentes</TableHead>
                    <TableHead className="text-right">Qtd. Manutenções</TableHead>
                    <TableHead className="text-right">Custo Manutenções</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contratos.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={11} className="text-center text-muted-foreground py-8">Sem contratos para o período selecionado.</TableCell>
                    </TableRow>
                  )}
                  {contratos.map((contrato) => (
                    <TableRow key={contrato.id}>
                      <TableCell className="font-medium">{contrato.cliente}</TableCell>
                      <TableCell>{contrato.contratoNumero || '-'}</TableCell>
                      <TableCell>{contrato.equipamento}</TableCell>
                      <TableCell className="text-right">{formatNumber(contrato.franquia)}</TableCell>
                      <TableCell>{new Date(contrato.dataInicio).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell>{new Date(contrato.dataFim).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell className="text-right">{formatNumber(contrato.copias.realizadas)}</TableCell>
                      <TableCell className="text-right">
                        <span className={contrato.copias.excedentes > 0 ? 'text-amber-600 font-medium' : ''}>
                          {formatNumber(contrato.copias.excedentes)}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        <span className={contrato.faturamento.excedentes > 0 ? 'text-amber-600 font-medium' : ''}>
                          {formatCurrency(contrato.faturamento.excedentes)}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">{formatNumber(contrato.manutencoes.quantidade)}</TableCell>
                      <TableCell className="text-right">
                        <span className={contrato.manutencoes.custo > 0 ? 'text-red-600 font-medium' : ''}>
                          {formatCurrency(contrato.manutencoes.custo)}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="manutencao">
          <Card>
            <CardContent className="pt-6">
              {contratos.length > 0 ? (
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={contratos}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="cliente" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="manutencoes.quantidade" name="Qtde. Manutenções" fill="#3b82f6" />
                      <Bar dataKey="manutencoes.custo" name="Custo Manutenção" fill="#ef4444" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">Sem dados para exibir no gráfico.</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ContractsDashboard;
