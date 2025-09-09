// src/components/financial/contracts/ContractsDashboardGrouped.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../ui/tabs";
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
  AlertCircle,
  Calendar,
  Download
} from "lucide-react";
import { contratosService, type SuprimentoDetalhado } from '../../../services/contratosService';
import { Alert, AlertDescription } from '../../ui/alert';

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

interface SuprimentoNota {
  id: number;
  numero_nota: string;
  data: string;
  valor_total_nota: number;
  operacao?: string;
  cfop?: string;
  obs?: string;
}

interface SuprimentoResultado {
  cliente?: { id: number; nome: string };
  contrato_numero: string;
  contrato_id: number;
  suprimentos?: {
    quantidade_notas: number;
    notas: SuprimentoNota[];
  };
}

interface ContratoData {
  id: number;
  cliente?: { id: number; nome: string };
  contrato?: string;
  inicio?: string;
  fim?: string;
  data?: string;
  status?: string;
  valorpacela?: number;
  valorcontrato?: number;
  totalMaquinas?: number;
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
  const [filtros, setFiltros] = useState<{ data_inicio: string; data_fim: string }>({
    data_inicio: defaultFrom.toISOString().split('T')[0],
    data_fim: defaultTo.toISOString().split('T')[0]
  });
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
      console.log(`📈 Apenas contratos ativos no período serão incluídos`);
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
      
      suprimentosResponse.resultados?.forEach((resultado: SuprimentoResultado) => {
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
          notas.forEach((nota: SuprimentoNota) => {
            const notaId = nota.id;
            const valorNota = Number(nota.valor_total_nota || 0);
            
            // Verificar se a nota já foi processada (evita duplicação entre contratos)
            if (!notasProcessadas.has(notaId)) {
              notasProcessadas.add(notaId);
              
              const valorExistente = suprimentosPorCliente.get(clienteId) || 0;
              suprimentosPorCliente.set(clienteId, valorExistente + valorNota);
              
              console.log(`💰 Nota ${nota.numero_nota} (ID: ${notaId}): R$ ${valorNota} - Cliente: ${clienteNome}`);
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
      
      contratos.forEach((contrato: ContratoData) => {
        const clienteId = contrato.cliente?.id;
        const clienteNome = contrato.cliente?.nome || 'Cliente não informado';
        
        if (!clienteId) return;
        
        // 📅 VERIFICAÇÃO DE PERÍODO ATIVO DO CONTRATO:
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
        
        // 📊 ORIGEM DO VALOR MENSAL:
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
  const formatPercent = (value: number) => {
    if (isNaN(value) || !isFinite(value)) {
      return '0.0%';
    }
    return `${value.toFixed(1)}%`;
  };
  const formatDateDisplay = (iso: string) => {
    const d = new Date(iso + 'T00:00:00');
    return isNaN(d.getTime()) ? iso : d.toLocaleDateString();
  };

  const exportToCSV = () => {
    try {
      const headers = ['Cliente', 'Contratos', 'Faturamento', 'Suprimentos', 'Margem', 'Margem%'];
      const rows = clientesAgrupados.map((c) => {
        const margemPerc = c.faturamentoTotal > 0 ? (c.margemLiquida / c.faturamentoTotal) * 100 : 0;
        return [
          c.cliente,
          String(c.quantidadeContratos),
          String(c.faturamentoTotal.toFixed(2)).replace('.', ','),
          String(c.despesasSuprimentos.toFixed(2)).replace('.', ','),
          String(c.margemLiquida.toFixed(2)).replace('.', ','),
          String(margemPerc.toFixed(1)).replace('.', ',')
        ];
      });
      const csv = [headers.join(';'), ...rows.map((r) => r.join(';'))].join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contratos_por_cliente_${filtros.data_inicio}_${filtros.data_fim}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Falha ao exportar CSV:', e);
    }
  };

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
          console.log(`🗓️ Filtro de Período: ${toYmd(dateRange.from)} até ${toYmd(dateRange.to)}`);
          console.log(`💡 Evitando duplicação de notas entre contratos`);
          
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
          
          response.resultados?.forEach((resultado: SuprimentoResultado) => {
            // Verificar se é realmente do contrato específico
            if (resultado.contrato_id === primeiroContrato.id) {
              const notas = resultado.suprimentos?.notas || [];
              console.log(`✅ Contrato encontrado: ${resultado.contrato_numero} com ${notas.length} notas`);
              
              notas.forEach((nota: SuprimentoNota) => {
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
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh' 
      }}>
        <div style={{ 
          animation: 'spin 1s linear infinite',
          borderRadius: '50%',
          height: '48px',
          width: '48px',
          borderWidth: '2px',
          borderStyle: 'solid',
          borderColor: 'transparent transparent #3b82f6 transparent'
        }} />
      </div>
    );
  }

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '24px', 
      backgroundColor: '#f8fafc', 
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', fontWeight: '700', color: '#111827' }}>
            Dashboard de Contratos por Cliente
          </h1>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Análise financeira agrupada por cliente
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6b7280' }}>
          <Calendar style={{ width: '20px', height: '20px' }} />
          <span className="text-sm">
            {formatDateDisplay(filtros.data_inicio)} - {formatDateDisplay(filtros.data_fim)}
          </span>
        </div>
      </div>

      {/* Filtros de Período - mesmo padrão do Fluxo de Caixa Realizado */}
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
              onClick={() => {
                const from = new Date(filtros.data_inicio + 'T00:00:00');
                const to = new Date(filtros.data_fim + 'T23:59:59');
                if (!isNaN(from.getTime()) && !isNaN(to.getTime())) {
                  setDateRange({ from, to });
                }
              }}
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
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Cards de Resumo */}
      {resumoFinanceiro && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #3b82f6',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              Total de Clientes
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatNumber(resumoFinanceiro.totalClientes)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {formatNumber(resumoFinanceiro.totalContratos)} contratos
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #10b981',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              Faturamento Total
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(resumoFinanceiro.faturamentoTotal)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              Período selecionado
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: '4px solid #ef4444',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              Despesas Suprimentos
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
              {formatCurrency(resumoFinanceiro.despesasTotal)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {formatPercent((resumoFinanceiro.despesasTotal / resumoFinanceiro.faturamentoTotal) * 100)} do faturamento
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            borderLeft: `4px solid ${resumoFinanceiro.percentualMargem >= 0 ? '#10b981' : '#ef4444'}`,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '500', marginBottom: '5px' }}>
              Margem Líquida
            </div>
            <div style={{ 
              fontSize: '1.5rem', 
              fontWeight: '700', 
              color: resumoFinanceiro.percentualMargem >= 0 ? '#10b981' : '#ef4444'
            }}>
              {formatCurrency(resumoFinanceiro.margemTotal)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
              {formatPercent(resumoFinanceiro.percentualMargem)} margem
            </div>
          </div>
        </div>
      )}

      {/* Abas de Navegação */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="clientes" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">
            👥 Clientes
          </TabsTrigger>
          <TabsTrigger value="graficos" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">
            📊 Gráficos
          </TabsTrigger>
        </TabsList>

        <TabsContent value="clientes">
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            overflow: 'hidden'
          }}>
            <div style={{
              padding: '20px',
              borderBottom: '1px solid #e5e7eb'
            }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827' }}>
                Contratos Agrupados por Cliente
              </h3>
            </div>
            
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: '#f9fafb' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase', width: '32px' }}></th>
                    <th style={{ padding: '12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Cliente</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Contratos</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Faturamento</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Suprimentos</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Margem Líquida</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>% Margem</th>
                  </tr>
                </thead>
                <tbody>
                  {clientesAgrupados.map((cliente) => (
                    <React.Fragment key={cliente.clienteId}>
                      <tr 
                        style={{ 
                          borderBottom: '1px solid #f3f4f6',
                          cursor: 'pointer'
                        }}
                        onClick={() => toggleRowExpansion(cliente.clienteId)}
                        onMouseEnter={(e) => (e.currentTarget as HTMLTableRowElement).style.backgroundColor = '#f9fafb'}
                        onMouseLeave={(e) => (e.currentTarget as HTMLTableRowElement).style.backgroundColor = 'transparent'}
                      >
                        <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827' }}>
                          {expandedRows.has(cliente.clienteId) ? 
                            <ChevronDown className="h-4 w-4" /> : 
                            <ChevronRight className="h-4 w-4" />
                          }
                        </td>
                        <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', fontWeight: '500' }}>
                          {cliente.cliente}
                        </td>
                        <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', textAlign: 'center' }}>
                          {cliente.quantidadeContratos}
                        </td>
                        <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', textAlign: 'right' }}>
                          {formatCurrency(cliente.faturamentoTotal)}
                        </td>
                        <td style={{ padding: '12px', fontSize: '0.875rem', color: '#111827', textAlign: 'right' }}>
                          {formatCurrency(cliente.despesasSuprimentos)}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          fontSize: '0.875rem', 
                          textAlign: 'right',
                          fontWeight: '600',
                          color: cliente.margemLiquida >= 0 ? '#059669' : '#dc2626'
                        }}>
                          {formatCurrency(cliente.margemLiquida)}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          fontSize: '0.875rem', 
                          textAlign: 'center',
                          fontWeight: '600',
                          color: cliente.margemLiquida >= 0 ? '#059669' : '#dc2626'
                        }}>
                          {cliente.faturamentoTotal > 0 ? formatPercent((cliente.margemLiquida / cliente.faturamentoTotal) * 100) : '0.0%'}
                        </td>
                      </tr>

                      {/* Linha expandida - Contratos do cliente */}
                      {expandedRows.has(cliente.clienteId) && (
                        <tr>
                          <td 
                            colSpan={7} 
                            style={{ 
                              backgroundColor: '#f8fafc',
                              padding: '0',
                              borderBottom: '1px solid #f3f4f6'
                            }}
                          >
                            <div style={{ padding: '16px' }}>
                              <h4 style={{ 
                                fontWeight: '600', 
                                marginBottom: '12px',
                                fontSize: '0.875rem',
                                color: '#111827'
                              }}>
                                Contratos de {cliente.cliente}
                              </h4>
                              <table style={{ 
                                width: '100%', 
                                borderCollapse: 'collapse' as const,
                                fontSize: '0.875rem'
                              }}>
                                <thead>
                                  <tr style={{ backgroundColor: '#f9fafb' }}>
                                    <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Contrato</th>
                                    <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Equipamentos</th>
                                    <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Valor Mensal</th>
                                    <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Período</th>
                                    <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Status</th>
                                    <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Faturamento</th>
                                    <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Suprimentos</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {cliente.contratos.map((contrato) => (
                                    <tr key={contrato.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                                      <td style={{ padding: '8px 12px', fontFamily: 'monospace', fontSize: '0.75rem', color: '#111827' }}>
                                        {contrato.contratoNumero}
                                      </td>
                                      <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                        {contrato.equipamento}
                                      </td>
                                      <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                        {formatCurrency(contrato.valorMensal)}
                                      </td>
                                      <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                        {new Date(contrato.dataInicio).toLocaleDateString()} - {' '}
                                        {new Date(contrato.dataFim).toLocaleDateString()}
                                      </td>
                                      <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                        <span style={{
                                          padding: '2px 8px',
                                          borderRadius: '9999px',
                                          fontSize: '0.75rem',
                                          backgroundColor: contrato.status === 'Ativo' ? '#dcfce7' : '#f3f4f6',
                                          color: contrato.status === 'Ativo' ? '#166534' : '#374151'
                                        }}>
                                          {contrato.status}
                                        </span>
                                      </td>
                                      <td style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', color: '#111827' }}>
                                        {formatCurrency(contrato.faturamento)}
                                      </td>
                                      <td style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', color: '#111827' }}>
                                        {formatCurrency(contrato.suprimentos)}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>

                              {/* Detalhes de suprimentos */}
                              {loadingSuprimentos.has(cliente.clienteId) && (
                                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                                  <div style={{ 
                                    animation: 'spin 1s linear infinite',
                                    borderRadius: '50%',
                                    height: '32px',
                                    width: '32px',
                                    borderWidth: '2px',
                                    borderStyle: 'solid',
                                    borderColor: 'transparent transparent #3b82f6 transparent',
                                    margin: '0 auto'
                                  }} />
                                  <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '8px' }}>
                                    Carregando detalhes de suprimentos...
                                  </p>
                                </div>
                              )}

                              {suprimentosDetalhados.has(cliente.clienteId) && (
                                <div style={{ marginTop: '16px' }}>
                                  <h5 style={{ 
                                    fontWeight: '600', 
                                    marginBottom: '8px',
                                    fontSize: '0.875rem',
                                    color: '#111827'
                                  }}>
                                    Notas Fiscais - Primeiro Contrato
                                    <span style={{ 
                                      fontSize: '0.75rem', 
                                      fontWeight: '400', 
                                      color: '#6b7280', 
                                      marginLeft: '8px'
                                    }}>
                                      ({suprimentosDetalhados.get(cliente.clienteId)!.length} nota(s) de suprimentos)
                                    </span>
                                  </h5>
                                  <p style={{ 
                                    fontSize: '0.75rem', 
                                    color: '#6b7280', 
                                    marginBottom: '12px'
                                  }}>
                                    💡 Exibindo notas apenas do primeiro contrato para evitar duplicação quando o cliente possui múltiplos contratos.
                                  </p>
                                  {suprimentosDetalhados.get(cliente.clienteId)!.length > 0 ? (
                                    <table style={{ 
                                      width: '100%', 
                                      borderCollapse: 'collapse' as const,
                                      fontSize: '0.875rem'
                                    }}>
                                      <thead>
                                        <tr style={{ backgroundColor: '#f9fafb' }}>
                                          <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Número NF</th>
                                          <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Data</th>
                                          <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>CFOP</th>
                                          <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Operação</th>
                                          <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Observações</th>
                                          <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.75rem', fontWeight: '600', color: '#374151', borderBottom: '1px solid #e5e7eb' }}>Valor</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {suprimentosDetalhados.get(cliente.clienteId)!.map((nota) => {
                                          // Determinar o tipo baseado no CFOP e operação
                                          let tipoOperacao = nota.operacao || 'Outros';
                                          let corTipo = { backgroundColor: '#f3f4f6', color: '#374151' };
                                          if (nota.cfop === '5910' || nota.cfop === '6910') {
                                            tipoOperacao = 'SIMPLES REMESSA';
                                            corTipo = { backgroundColor: '#dbeafe', color: '#1e40af' };
                                          } else if (nota.cfop === '5949' || nota.cfop === '6949') {
                                            tipoOperacao = nota.operacao || 'SIMPLES REMESSA';
                                            corTipo = { backgroundColor: '#e9d5ff', color: '#7c3aed' };
                                          } else if (nota.operacao?.toLowerCase().includes('remessa')) {
                                            corTipo = { backgroundColor: '#dbeafe', color: '#1e40af' };
                                          } else if (nota.operacao?.toLowerCase().includes('suprimento')) {
                                            corTipo = { backgroundColor: '#dcfce7', color: '#166534' };
                                          }
                                          return (
                                            <tr key={nota.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                                              <td style={{ padding: '8px 12px', fontFamily: 'monospace', fontSize: '0.75rem', color: '#111827' }}>
                                                {nota.numero_nota}
                                              </td>
                                              <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                                {new Date(nota.data).toLocaleDateString()}
                                              </td>
                                              <td style={{ padding: '8px 12px', fontFamily: 'monospace', fontSize: '0.75rem', color: '#111827' }}>
                                                {nota.cfop}
                                              </td>
                                              <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: '#111827' }}>
                                                <span style={{
                                                  padding: '2px 8px',
                                                  borderRadius: '9999px',
                                                  fontSize: '0.75rem',
                                                  ...corTipo
                                                }}>
                                                  {tipoOperacao}
                                                </span>
                                              </td>
                                              <td style={{ 
                                                padding: '8px 12px', 
                                                maxWidth: '240px', 
                                                whiteSpace: 'nowrap',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                fontSize: '0.75rem',
                                                color: '#111827'
                                              }} title={nota.obs}>
                                                {nota.obs || '-'}
                                              </td>
                                              <td style={{ 
                                                padding: '8px 12px', 
                                                textAlign: 'right', 
                                                fontWeight: '600',
                                                fontSize: '0.75rem',
                                                color: '#111827'
                                              }}>
                                                {formatCurrency(nota.valor_total_nota)}
                                              </td>
                                            </tr>
                                          );
                                        })}
                                      </tbody>
                                      <tfoot>
                                        <tr style={{ backgroundColor: '#f9fafb' }}>
                                          <td colSpan={5} style={{ 
                                            padding: '8px 12px', 
                                            textAlign: 'right', 
                                            fontWeight: '600',
                                            fontSize: '0.75rem',
                                            color: '#111827'
                                          }}>
                                            Total de Suprimentos:
                                          </td>
                                          <td style={{ 
                                            padding: '8px 12px', 
                                            textAlign: 'right', 
                                            fontWeight: '700',
                                            fontSize: '0.75rem',
                                            color: '#111827'
                                          }}>
                                            {formatCurrency(
                                              suprimentosDetalhados.get(cliente.clienteId)!
                                                .reduce((sum, nota) => sum + nota.valor_total_nota, 0)
                                            )}
                                          </td>
                                        </tr>
                                      </tfoot>
                                    </table>
                                  ) : (
                                    <div style={{ textAlign: 'center', padding: '16px 0' }}>
                                      <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                                        Nenhuma nota fiscal de suprimentos encontrada para este cliente no período.
                                      </p>
                                      <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
                                        Dados obtidos do endpoint: /contratos_locacao/suprimentos/
                                      </p>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="graficos">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
              Faturamento vs Despesas por Cliente (Top 10)
            </h3>
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
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
              Distribuição de Faturamento
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                  <Pie
                    data={dadosGrafico.slice(0, 7)}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({cliente, percent}) => `${cliente} ${((percent || 0) * 100).toFixed(0)}%`}
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
          </div>
        </div>
        </TabsContent>
      </Tabs>

      {/* Botão de Exportação */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
        <button
          onClick={exportToCSV}
          style={{
            padding: '8px 16px',
            backgroundColor: 'white',
            color: '#374151',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Download style={{ width: '16px', height: '16px' }} />
          Exportar Relatório
        </button>
      </div>
    </div>
  );
};

export default ContractsDashboardGrouped;
