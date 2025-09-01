// src/components/financial/contracts/ContractsDashboardGrouped.tsx
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
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  ChevronDown,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Users,
  FileText,
  DollarSign,
  AlertCircle
} from "lucide-react";
import { contratosService } from '@/services/api';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { SeparateDatePicker } from '../../common/SeparateDatePicker';

interface ClienteAgrupado {
  clienteId: number;
  cliente: string;
  contratos: ContratoCliente[];
  faturamentoTotal: number;
  despesasSuprimentos: number;
  quantidadeContratos: number;
  margemLiquida: number;
}

interface ContratoCliente {
  id: number;
  contratoNumero: string;
  equipamento: string;
  valorMensal: number;
  dataInicio: string;
  dataFim: string;
  status: string;
  faturamento: number;
  suprimentos: number;
}

interface SuprimentoDetalhado {
  id: number;
  numero_nota: string;
  data: string;
  valor_total_nota: number;
  operacao: string;
  cfop: string;
  obs?: string;
}

interface DateRange {
  from: Date;
  to: Date;
}

interface ResumoFinanceiro {
  totalClientes: number;
  totalContratos: number;
  faturamentoTotal: number;
  despesasTotal: number;
  margemTotal: number;
  percentualMargem: number;
}

const ContractsDashboardGrouped: React.FC = () => {
  const [clientesAgrupados, setClientesAgrupados] = useState<ClienteAgrupado[]>([]);
  const [resumoFinanceiro, setResumoFinanceiro] = useState<ResumoFinanceiro | null>(null);
  const defaultFrom = new Date('2024-01-01T00:00:00');
  const defaultTo = new Date();
  const [dateRange, setDateRange] = useState<DateRange>({ from: defaultFrom, to: defaultTo });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('clientes');
  
  // Estados para expansão de linhas e dados de suprimentos
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [suprimentosDetalhados, setSuprimentosDetalhados] = useState<Map<number, SuprimentoDetalhado[]>>(new Map());
  const [loadingSuprimentos, setLoadingSuprimentos] = useState<Set<number>>(new Set());

  const loadClientesAgrupados = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const toYmd = (d: Date) => d.toISOString().split('T')[0];
      
      // 1. Carregar contratos básicos
      const contratos = await contratosService.listar();
      
      // 2. Configurar período para faturamento proporcional
      console.log(`📊 ANÁLISE DE CONTRATOS POR PERÍODO:`);
      console.log(`🗓️ Período selecionado: ${dateRange.from.toLocaleDateString()} até ${dateRange.to.toLocaleDateString()}`);
      console.log(`� Apenas contratos ativos no período serão incluídos`);
      console.log(`🧮 Faturamento será proporcional ao tempo ativo no período`);
      console.log(`==================================================`);
      
      // 3. Buscar dados de suprimentos por cliente
      const filtrosSuprimentos = { 
        data_inicial: toYmd(dateRange.from), 
        data_final: toYmd(dateRange.to) 
      };
      
      const suprimentosResponse = await contratosService.buscarSuprimentos(filtrosSuprimentos);
      
      console.log(`📋 Resposta de suprimentos:`, suprimentosResponse);
      console.log(`📋 Total de resultados: ${suprimentosResponse.resultados?.length || 0}`);
      
      // 4. Criar mapa de suprimentos por cliente - evitando duplicação
      const suprimentosPorCliente = new Map<number, number>();
      const notasProcessadas = new Set<number>(); // Para evitar processar a mesma nota múltiplas vezes
      
      suprimentosResponse.resultados?.forEach((resultado: any) => {
        const clienteId = resultado.cliente?.id;
        const clienteNome = resultado.cliente?.nome;
        
        console.log(`🔍 Processando resultado:`, {
          contrato: resultado.contrato_numero,
          cliente: clienteNome,
          clienteId,
          quantidadeNotas: resultado.suprimentos?.quantidade_notas || 0
        });
        
        if (clienteId) {
          // Processar cada nota individual para evitar duplicação
          const notas = resultado.suprimentos?.notas || [];
          notas.forEach((nota: any) => {
            const notaId = nota.id;
            const valorNota = Number(nota.valor_total_nota || 0);
            
            // Verificar se a nota já foi processada (evita duplicação entre contratos)
            if (!notasProcessadas.has(notaId)) {
              notasProcessadas.add(notaId);
              
              const valorExistente = suprimentosPorCliente.get(clienteId) || 0;
              suprimentosPorCliente.set(clienteId, valorExistente + valorNota);
              
              console.log(`� Nota ${nota.numero_nota} (ID: ${notaId}): R$ ${valorNota} - Cliente: ${clienteNome}`);
            } else {
              console.log(`⚠️ Nota ${nota.numero_nota} (ID: ${notaId}) já processada - evitando duplicação`);
            }
          });
        }
      });
      
      console.log(`📊 Resumo final de suprimentos por cliente:`);
      suprimentosPorCliente.forEach((valor, clienteId) => {
        console.log(`👤 Cliente ID ${clienteId}: R$ ${valor.toFixed(2)}`);
      });
      
      // 5. Agrupar contratos por cliente
      const clientesMap = new Map<number, ClienteAgrupado>();
      
      contratos.forEach((contrato: any) => {
        const clienteId = contrato.cliente?.id;
        const clienteNome = contrato.cliente?.nome || 'Cliente não informado';
        
        if (!clienteId) return;
        
        // � VERIFICAÇÃO DE PERÍODO ATIVO DO CONTRATO:
        const dataInicioContrato = new Date(contrato.inicio || contrato.data || '1900-01-01');
        const dataFimContrato = new Date(contrato.fim || '2099-12-31');
        const periodoInicio = dateRange.from;
        const periodoFim = dateRange.to;
        
        // Verificar se o contrato está ativo durante o período selecionado
        const contratoAtivoNoPeriodo = dataInicioContrato <= periodoFim && dataFimContrato >= periodoInicio;
        
        if (!contratoAtivoNoPeriodo) {
          console.log(`❌ CONTRATO EXCLUÍDO - Não ativo no período:`);
          console.log(`📋 Contrato: ${contrato.contrato || `C${contrato.id}`}`);
          console.log(`👤 Cliente: ${clienteNome}`);
          console.log(`📅 Início do Contrato: ${dataInicioContrato.toLocaleDateString()}`);
          console.log(`📅 Fim do Contrato: ${dataFimContrato.toLocaleDateString()}`);
          console.log(`🗓️ Período Consultado: ${periodoInicio.toLocaleDateString()} até ${periodoFim.toLocaleDateString()}`);
          console.log(`--------------------------------------------------`);
          return; // Pular este contrato
        }
        
        // Calcular sobreposição de período para faturamento proporcional
        const inicioEfetivo = dataInicioContrato > periodoInicio ? dataInicioContrato : periodoInicio;
        const fimEfetivo = dataFimContrato < periodoFim ? dataFimContrato : periodoFim;
        const diasEfetivos = Math.max(1, Math.round((fimEfetivo.getTime() - inicioEfetivo.getTime()) / (1000 * 60 * 60 * 24)));
        const mesesEfetivos = Math.max(0.1, diasEfetivos / 30.44);
        
        // �📊 ORIGEM DO VALOR MENSAL:
        // 1º Prioridade: contrato.valorpacela (valor da parcela mensal)
        // 2º Prioridade: contrato.valorcontrato (valor total do contrato)
        // 3º Fallback: 0 (se nenhum valor estiver disponível)
        const valorMensal = Number(contrato.valorpacela || contrato.valorcontrato || 0);
        
        // 💰 CÁLCULO DO FATURAMENTO PROPORCIONAL AO PERÍODO ATIVO:
        const faturamentoPeriodo = valorMensal * mesesEfetivos;
        
        console.log(`✅ CONTRATO ATIVO NO PERÍODO:`);
        console.log(`👤 Cliente: ${clienteNome}`);
        console.log(`📋 Contrato: ${contrato.contrato || `C${contrato.id}`}`);
        console.log(`📅 Período Contrato: ${dataInicioContrato.toLocaleDateString()} até ${dataFimContrato.toLocaleDateString()}`);
        console.log(`📅 Período Efetivo: ${inicioEfetivo.toLocaleDateString()} até ${fimEfetivo.toLocaleDateString()}`);
        console.log(`⏱️ Dias Efetivos: ${diasEfetivos} dias (${mesesEfetivos.toFixed(2)} meses)`);
        console.log(`💵 Valor Mensal: R$ ${valorMensal.toFixed(2)} (${contrato.valorpacela ? 'valorpacela' : contrato.valorcontrato ? 'valorcontrato' : 'valor zerado'})`);
        console.log(`🧮 Faturamento Proporcional: R$ ${faturamentoPeriodo.toFixed(2)} (${valorMensal} x ${mesesEfetivos.toFixed(2)} meses)`);
        console.log(`--------------------------------------------------`);
        
        const contratoData: ContratoCliente = {
          id: contrato.id,
          contratoNumero: contrato.contrato || `C${contrato.id}`,
          equipamento: String(contrato.totalMaquinas || 1),
          valorMensal,
          dataInicio: dataInicioContrato.toISOString(),
          dataFim: dataFimContrato.toISOString(),
          status: contrato.status || 'Ativo',
          faturamento: faturamentoPeriodo,
          suprimentos: 0 // Será distribuído proporcionalmente
        };
        
        if (clientesMap.has(clienteId)) {
          const clienteExistente = clientesMap.get(clienteId)!;
          clienteExistente.contratos.push(contratoData);
          clienteExistente.faturamentoTotal += faturamentoPeriodo;
          clienteExistente.quantidadeContratos += 1;
        } else {
          const despesasSuprimentos = suprimentosPorCliente.get(clienteId) || 0;
          clientesMap.set(clienteId, {
            clienteId,
            cliente: clienteNome,
            contratos: [contratoData],
            faturamentoTotal: faturamentoPeriodo,
            despesasSuprimentos,
            quantidadeContratos: 1,
            margemLiquida: faturamentoPeriodo - despesasSuprimentos
          });
        }
      });
      
      // 6. Distribuir custos de suprimentos proporcionalmente entre contratos do cliente
      clientesMap.forEach((clienteAgrupado) => {
        const totalFaturamentoCliente = clienteAgrupado.faturamentoTotal;
        const totalSuprimentosCliente = clienteAgrupado.despesasSuprimentos;
        
        clienteAgrupado.contratos.forEach((contrato) => {
          if (totalFaturamentoCliente > 0) {
            const proporcao = contrato.faturamento / totalFaturamentoCliente;
            contrato.suprimentos = totalSuprimentosCliente * proporcao;
          }
        });
        
        // Atualizar margem líquida
        clienteAgrupado.margemLiquida = clienteAgrupado.faturamentoTotal - clienteAgrupado.despesasSuprimentos;
      });
      
      const clientesArray = Array.from(clientesMap.values())
        .sort((a, b) => b.faturamentoTotal - a.faturamentoTotal);
      
      setClientesAgrupados(clientesArray);
      
      // 7. Calcular resumo financeiro
      if (clientesArray.length > 0) {
        const totalFaturamento = clientesArray.reduce((acc, cliente) => acc + cliente.faturamentoTotal, 0);
        const totalDespesas = clientesArray.reduce((acc, cliente) => acc + cliente.despesasSuprimentos, 0);
        const totalMargem = totalFaturamento - totalDespesas;
        
        console.log(`📈 RESUMO FINANCEIRO FINAL:`);
        console.log(`👥 Total de Clientes: ${clientesArray.length}`);
        console.log(`💰 Faturamento Total: R$ ${totalFaturamento.toFixed(2)}`);
        console.log(`💸 Despesas Suprimentos: R$ ${totalDespesas.toFixed(2)}`);
        console.log(`🎯 Margem Líquida: R$ ${totalMargem.toFixed(2)}`);
        console.log(`📊 % Margem: ${totalFaturamento > 0 ? ((totalMargem / totalFaturamento) * 100).toFixed(1) : 0}%`);
        console.log(`==================================================`);
        
        setResumoFinanceiro({
          totalClientes: clientesArray.length,
          totalContratos: clientesArray.reduce((acc, cliente) => acc + cliente.quantidadeContratos, 0),
          faturamentoTotal: totalFaturamento,
          despesasTotal: totalDespesas,
          margemTotal: totalMargem,
          percentualMargem: totalFaturamento > 0 ? (totalMargem / totalFaturamento) * 100 : 0
        });
        setError(null);
      } else {
        setResumoFinanceiro(null);
        setError('Nenhum cliente com contratos encontrado para o período selecionado.');
      }
      
    } catch (err) {
      console.error('Erro ao carregar dados agrupados:', err);
      setError('Falha ao carregar dados dos contratos. Verifique se o backend está funcionando.');
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  useEffect(() => { loadClientesAgrupados(); }, [loadClientesAgrupados]);

  const formatCurrency = (value: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  const formatNumber = (value: number) => new Intl.NumberFormat('pt-BR').format(value);
  const formatPercent = (value: number) => `${value.toFixed(1)}%`;

  // Função para alternar expansão de linha e carregar suprimentos detalhados
  const toggleRowExpansion = async (clienteId: number) => {
    const newExpandedRows = new Set(expandedRows);
    
    if (expandedRows.has(clienteId)) {
      // Contraindo a linha
      newExpandedRows.delete(clienteId);
      setExpandedRows(newExpandedRows);
    } else {
      // Expandindo a linha
      newExpandedRows.add(clienteId);
      setExpandedRows(newExpandedRows);
      
      // Carregar detalhes de suprimentos se ainda não foram carregados
      if (!suprimentosDetalhados.has(clienteId)) {
        setLoadingSuprimentos(prev => new Set([...prev, clienteId]));
        
        try {
          const toYmd = (d: Date) => d.toISOString().split('T')[0];
          
          // 🎯 BUSCAR NOTAS APENAS DO PRIMEIRO CONTRATO DO CLIENTE
          const cliente = clientesAgrupados.find(c => c.clienteId === clienteId);
          if (!cliente || cliente.contratos.length === 0) {
            console.log(`❌ Cliente ${clienteId} não encontrado ou sem contratos`);
            setSuprimentosDetalhados(prev => new Map(prev.set(clienteId, [])));
            return;
          }
          
          // Usar apenas o primeiro contrato (por ID ou por ordem)
          const primeiroContrato = cliente.contratos[0];
          
          console.log(`🔍 BUSCANDO NOTAS APENAS DO PRIMEIRO CONTRATO:`);
          console.log(`👤 Cliente: ${cliente.cliente}`);
          console.log(`📋 Primeiro Contrato: ${primeiroContrato.contratoNumero}`);
          console.log(`📊 Total de Contratos do Cliente: ${cliente.contratos.length}`);
          console.log(`�️ Filtro de Período: ${toYmd(dateRange.from)} até ${toYmd(dateRange.to)}`);
          console.log(`�💡 Evitando duplicação de notas entre contratos`);
          
          // Buscar suprimentos específicos deste contrato
          const filtros = {
            data_inicial: toYmd(dateRange.from),
            data_final: toYmd(dateRange.to),
            contrato_id: primeiroContrato.id.toString() // Usar contrato_id ao invés de cliente_id
          };
          
          const response = await contratosService.buscarSuprimentos(filtros);
          
          console.log(`📡 Resposta do backend:`, response);
          console.log(`📋 Resultados encontrados: ${response.resultados?.length || 0}`);
          
          // Backend já filtra por data, apenas extrair notas do primeiro contrato
          const notasDetalhadas: SuprimentoDetalhado[] = [];
          
          response.resultados?.forEach((resultado: any) => {
            // Verificar se é realmente do contrato específico
            if (resultado.contrato_id === primeiroContrato.id) {
              const notas = resultado.suprimentos?.notas || [];
              console.log(`✅ Contrato encontrado: ${resultado.contrato_numero} com ${notas.length} notas`);
              
              notas.forEach((nota: any) => {
                notasDetalhadas.push({
                  id: nota.id,
                  numero_nota: nota.numero_nota,
                  data: nota.data,
                  valor_total_nota: Number(nota.valor_total_nota || 0),
                  operacao: nota.operacao || '',
                  cfop: nota.cfop || '',
                  obs: nota.obs || ''
                });
                
                console.log(`📝 Nota adicionada: ${nota.numero_nota} - Data: ${nota.data} - Valor: ${nota.valor_total_nota}`);
              });
            }
          });
          
          // Ordenar por data (mais recentes primeiro)
          notasDetalhadas.sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());
          
          setSuprimentosDetalhados(prev => new Map(prev.set(clienteId, notasDetalhadas)));
          
          console.log(`✅ Carregadas ${notasDetalhadas.length} notas de suprimentos do contrato ${primeiroContrato.contratoNumero}`);
          if (cliente.contratos.length > 1) {
            console.log(`ℹ️ Ignorados ${cliente.contratos.length - 1} contratos adicionais para evitar duplicação`);
          }
          console.log(`--------------------------------------------------`);
          
        } catch (error) {
          console.error('Erro ao carregar suprimentos detalhados:', error);
          setSuprimentosDetalhados(prev => new Map(prev.set(clienteId, [])));
        } finally {
          setLoadingSuprimentos(prev => {
            const newSet = new Set(prev);
            newSet.delete(clienteId);
            return newSet;
          });
        }
      }
    }
  };

  // Dados para gráficos
  const dadosGrafico = clientesAgrupados.map(cliente => ({
    cliente: cliente.cliente.length > 20 ? cliente.cliente.substring(0, 20) + '...' : cliente.cliente,
    faturamento: cliente.faturamentoTotal,
    despesas: cliente.despesasSuprimentos,
    margem: cliente.margemLiquida
  })).slice(0, 10); // Top 10 clientes

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0', '#ffb347'];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dashboard de Contratos por Cliente</h1>
          <p className="text-muted-foreground">Análise financeira agrupada por cliente</p>
        </div>
        <SeparateDatePicker
          date={dateRange}
          onDateChange={(newDateRange) => {
            if (newDateRange?.from && newDateRange?.to) {
              setDateRange({ from: newDateRange.from, to: newDateRange.to });
            }
          }}
        />
      </div>

      {error && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Cards de Resumo */}
      {resumoFinanceiro && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Clientes</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(resumoFinanceiro.totalClientes)}</div>
              <p className="text-xs text-muted-foreground">
                {formatNumber(resumoFinanceiro.totalContratos)} contratos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Faturamento Total</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(resumoFinanceiro.faturamentoTotal)}</div>
              <p className="text-xs text-muted-foreground">
                Período selecionado
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Despesas Suprimentos</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(resumoFinanceiro.despesasTotal)}</div>
              <p className="text-xs text-muted-foreground">
                {formatPercent((resumoFinanceiro.despesasTotal / resumoFinanceiro.faturamentoTotal) * 100)} do faturamento
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Margem Líquida</CardTitle>
              {resumoFinanceiro.percentualMargem >= 0 ? 
                <TrendingUp className="h-4 w-4 text-green-600" /> : 
                <TrendingDown className="h-4 w-4 text-red-600" />
              }
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(resumoFinanceiro.margemTotal)}</div>
              <p className="text-xs text-muted-foreground">
                {formatPercent(resumoFinanceiro.percentualMargem)} margem
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="clientes">Clientes</TabsTrigger>
          <TabsTrigger value="graficos">Gráficos</TabsTrigger>
        </TabsList>

        <TabsContent value="clientes">
          <Card>
            <CardHeader>
              <CardTitle>Contratos Agrupados por Cliente</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-8"></TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead className="text-center">Contratos</TableHead>
                    <TableHead className="text-right">Faturamento</TableHead>
                    <TableHead className="text-right">Suprimentos</TableHead>
                    <TableHead className="text-right">Margem Líquida</TableHead>
                    <TableHead className="text-center">% Margem</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {clientesAgrupados.map((cliente) => (
                    <React.Fragment key={cliente.clienteId}>
                      <TableRow 
                        className="cursor-pointer hover:bg-muted/50"
                        onClick={() => toggleRowExpansion(cliente.clienteId)}
                      >
                        <TableCell>
                          {expandedRows.has(cliente.clienteId) ? 
                            <ChevronDown className="h-4 w-4" /> : 
                            <ChevronRight className="h-4 w-4" />
                          }
                        </TableCell>
                        <TableCell className="font-medium">{cliente.cliente}</TableCell>
                        <TableCell className="text-center">{cliente.quantidadeContratos}</TableCell>
                        <TableCell className="text-right">{formatCurrency(cliente.faturamentoTotal)}</TableCell>
                        <TableCell className="text-right">{formatCurrency(cliente.despesasSuprimentos)}</TableCell>
                        <TableCell className="text-right">
                          <span className={cliente.margemLiquida >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {formatCurrency(cliente.margemLiquida)}
                          </span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className={cliente.margemLiquida >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {formatPercent((cliente.margemLiquida / cliente.faturamentoTotal) * 100)}
                          </span>
                        </TableCell>
                      </TableRow>

                      {/* Linha expandida - Contratos do cliente */}
                      {expandedRows.has(cliente.clienteId) && (
                        <TableRow>
                          <TableCell colSpan={7} className="bg-muted/25 p-0">
                            <div className="p-4">
                              <h4 className="font-semibold mb-3">Contratos de {cliente.cliente}</h4>
                              <Table>
                                <TableHeader>
                                  <TableRow>
                                    <TableHead>Contrato</TableHead>
                                    <TableHead>Equipamentos</TableHead>
                                    <TableHead>Valor Mensal</TableHead>
                                    <TableHead>Período</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead className="text-right">Faturamento</TableHead>
                                    <TableHead className="text-right">Suprimentos</TableHead>
                                  </TableRow>
                                </TableHeader>
                                <TableBody>
                                  {cliente.contratos.map((contrato) => (
                                    <TableRow key={contrato.id}>
                                      <TableCell className="font-mono">{contrato.contratoNumero}</TableCell>
                                      <TableCell>{contrato.equipamento}</TableCell>
                                      <TableCell>{formatCurrency(contrato.valorMensal)}</TableCell>
                                      <TableCell>
                                        {new Date(contrato.dataInicio).toLocaleDateString()} - {' '}
                                        {new Date(contrato.dataFim).toLocaleDateString()}
                                      </TableCell>
                                      <TableCell>
                                        <span className={`px-2 py-1 rounded-full text-xs ${
                                          contrato.status === 'Ativo' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                        }`}>
                                          {contrato.status}
                                        </span>
                                      </TableCell>
                                      <TableCell className="text-right">{formatCurrency(contrato.faturamento)}</TableCell>
                                      <TableCell className="text-right">{formatCurrency(contrato.suprimentos)}</TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>

                              {/* Detalhes de suprimentos */}
                              {loadingSuprimentos.has(cliente.clienteId) && (
                                <div className="mt-4 text-center">
                                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
                                  <p className="text-sm text-muted-foreground mt-2">Carregando detalhes de suprimentos...</p>
                                </div>
                              )}

                              {suprimentosDetalhados.has(cliente.clienteId) && (
                                <div className="mt-4">
                                  <h5 className="font-semibold mb-2">
                                    Notas Fiscais - Primeiro Contrato 
                                    <span className="text-sm font-normal text-muted-foreground ml-2">
                                      ({suprimentosDetalhados.get(cliente.clienteId)!.length} nota(s) de suprimentos)
                                    </span>
                                  </h5>
                                  <p className="text-xs text-muted-foreground mb-3">
                                    💡 Exibindo notas apenas do primeiro contrato para evitar duplicação quando o cliente possui múltiplos contratos.
                                  </p>
                                  {suprimentosDetalhados.get(cliente.clienteId)!.length > 0 ? (
                                    <Table>
                                      <TableHeader>
                                        <TableRow>
                                          <TableHead>Número NF</TableHead>
                                          <TableHead>Data</TableHead>
                                          <TableHead>CFOP</TableHead>
                                          <TableHead>Operação</TableHead>
                                          <TableHead>Observações</TableHead>
                                          <TableHead className="text-right">Valor</TableHead>
                                        </TableRow>
                                      </TableHeader>
                                      <TableBody>
                                        {suprimentosDetalhados.get(cliente.clienteId)!.map((nota) => {
                                          // Determinar o tipo baseado no CFOP e operação
                                          let tipoOperacao = nota.operacao || 'Outros';
                                          let corTipo = 'bg-gray-100 text-gray-800';
                                          
                                          if (nota.cfop === '5910' || nota.cfop === '6910') {
                                            tipoOperacao = 'SIMPLES REMESSA';
                                            corTipo = 'bg-blue-100 text-blue-800';
                                          } else if (nota.cfop === '5949' || nota.cfop === '6949') {
                                            tipoOperacao = nota.operacao || 'SIMPLES REMESSA';
                                            corTipo = 'bg-purple-100 text-purple-800';
                                          } else if (nota.operacao?.toLowerCase().includes('remessa')) {
                                            corTipo = 'bg-blue-100 text-blue-800';
                                          } else if (nota.operacao?.toLowerCase().includes('suprimento')) {
                                            corTipo = 'bg-green-100 text-green-800';
                                          }
                                          
                                          return (
                                            <TableRow key={nota.id}>
                                              <TableCell className="font-mono">{nota.numero_nota}</TableCell>
                                              <TableCell>{new Date(nota.data).toLocaleDateString()}</TableCell>
                                              <TableCell className="font-mono">{nota.cfop}</TableCell>
                                              <TableCell>
                                                <span className={`px-2 py-1 rounded-full text-xs ${corTipo}`}>
                                                  {tipoOperacao}
                                                </span>
                                              </TableCell>
                                              <TableCell className="max-w-xs truncate text-xs" title={nota.obs}>
                                                {nota.obs || '-'}
                                              </TableCell>
                                              <TableCell className="text-right font-semibold">
                                                {formatCurrency(nota.valor_total_nota)}
                                              </TableCell>
                                            </TableRow>
                                          );
                                        })}
                                      </TableBody>
                                      <tfoot>
                                        <TableRow className="bg-muted/50">
                                          <TableCell colSpan={5} className="text-right font-semibold">
                                            Total de Suprimentos:
                                          </TableCell>
                                          <TableCell className="text-right font-bold">
                                            {formatCurrency(
                                              suprimentosDetalhados.get(cliente.clienteId)!
                                                .reduce((sum, nota) => sum + nota.valor_total_nota, 0)
                                            )}
                                          </TableCell>
                                        </TableRow>
                                      </tfoot>
                                    </Table>
                                  ) : (
                                    <div className="text-center py-4">
                                      <p className="text-muted-foreground text-sm">
                                        Nenhuma nota fiscal de suprimentos encontrada para este cliente no período.
                                      </p>
                                      <p className="text-xs text-muted-foreground mt-1">
                                        Dados obtidos do endpoint: /contratos_locacao/suprimentos/
                                      </p>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="graficos">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Faturamento vs Despesas por Cliente (Top 10)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={dadosGrafico}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="cliente" 
                      angle={-45}
                      textAnchor="end"
                      height={100}
                    />
                    <YAxis tickFormatter={(value) => formatCurrency(value)} />
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Legend />
                    <Bar dataKey="faturamento" fill="#8884d8" name="Faturamento" />
                    <Bar dataKey="despesas" fill="#82ca9d" name="Despesas Suprimentos" />
                    <Bar dataKey="margem" fill="#ffc658" name="Margem Líquida" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Distribuição de Faturamento</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={dadosGrafico.slice(0, 7)}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({cliente, percent}) => `${cliente} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="faturamento"
                    >
                      {dadosGrafico.slice(0, 7).map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ContractsDashboardGrouped;
