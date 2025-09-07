import { useState, useEffect } from 'react';
import { DateRange } from 'react-day-picker';
import { subDays } from 'date-fns';
import { FluxoCaixaSummary } from '@/components/financial/fluxo-caixa/FluxoCaixaSummary';
import { FluxoCaixaChart } from '@/components/financial/fluxo-caixa/FluxoCaixaChart';
import { ContasTable } from '@/components/financial/fluxo-caixa/ContasTable';
import { DatePickerWithRange } from '@/components/ui/date-range-picker';
import { financialService } from '@/services/financialService';
import { FluxoCaixaData } from '@/types/financeiro';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

// Função para gerar dados do gráfico diário
const generateDailyChartData = (startDate: Date, endDate: Date, apiData: any) => {
  const days: any[] = [];
  const currentDate = new Date(startDate);
  let saldoAcumulado = 0;

  while (currentDate <= endDate) {
    const dateStr = currentDate.toISOString().split('T')[0];
    
    // Calcular receitas do dia (contas a receber que vencem neste dia)
    const receitasDia = apiData.contas_a_receber
      ?.filter((conta: any) => conta.vencimento?.startsWith(dateStr))
      ?.reduce((total: number, conta: any) => total + Number(conta.valor || 0), 0) || 0;
    
    // Calcular despesas do dia (contas a pagar que vencem neste dia)
    const despesasDia = apiData.contas_a_pagar
      ?.filter((conta: any) => conta.vencimento?.startsWith(dateStr))
      ?.reduce((total: number, conta: any) => total + Number(conta.valor || 0), 0) || 0;
    
    // Saldo do dia
    const saldoDia = receitasDia - despesasDia;
    saldoAcumulado += saldoDia;

    days.push({
      name: currentDate.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
      receitas: receitasDia,
      despesas: despesasDia,
      saldo: saldoAcumulado,
      data: dateStr
    });

    currentDate.setDate(currentDate.getDate() + 1);
  }

  return days;
};

const FluxoCaixa = () => {
  const [data, setData] = useState<FluxoCaixaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: subDays(new Date(), 29),
    to: new Date(),
  });

  useEffect(() => {
    const fetchData = async () => {
      if (!dateRange?.from || !dateRange?.to) return;

      setLoading(true);
      setError(null);

      try {
        const filtros = {
          data_inicial: dateRange.from.toISOString().split('T')[0],
          data_final: dateRange.to.toISOString().split('T')[0],
        };
        const result = await financialService.getFluxoCaixa(filtros);
        
        // Mapear dados da API para o formato esperado pelo frontend
        const mappedData = {
          total_a_pagar: result.resumo?.total_a_pagar || 0,
          total_a_receber: result.resumo?.total_a_receber || 0,
          saldo_periodo: result.resumo?.saldo_previsto || 0,
          contas_a_pagar: result.contas_a_pagar?.map((conta: any) => ({
            id: conta.id,
            descricao: conta.historico || conta.descricao || 'Sem descrição',
            valor: Number(conta.valor) || 0,
            data_vencimento: conta.vencimento || conta.data_vencimento,
            pessoa: {
              id: conta.pessoa?.id || conta.fornecedor_id || 0,
              nome: conta.fornecedor_nome || conta.pessoa?.nome || 'Não informado'
            }
          })) || [],
          contas_a_receber: result.contas_a_receber?.map((conta: any) => ({
            id: conta.id,
            descricao: conta.historico || conta.descricao || 'Sem descrição',
            valor: Number(conta.valor) || 0,
            data_vencimento: conta.vencimento || conta.data_vencimento,
            pessoa: {
              id: conta.pessoa?.id || conta.cliente_id || 0,
              nome: conta.cliente_nome || conta.pessoa?.nome || 'Não informado'
            }
          })) || [],
          grafico_diario: generateDailyChartData(dateRange.from!, dateRange.to!, result)
        };
        
        setData(mappedData);
      } catch (err) {
        setError('Falha ao buscar dados do fluxo de caixa.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [dateRange]);

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Fluxo de Caixa</h1>
        <DatePickerWithRange date={dateRange} onDateChange={setDateRange} />
      </div>

      {loading && <p>Carregando...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {data && (
        <>
          <FluxoCaixaSummary
            totalPagar={data.total_a_pagar}
            totalReceber={data.total_a_receber}
            saldo={data.saldo_periodo}
          />

          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Fluxo Diário (Receitas vs. Despesas)</CardTitle>
              </CardHeader>
              <CardContent>
                <FluxoCaixaChart data={data.grafico_diario} type="bar" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Evolução do Saldo Acumulado</CardTitle>
              </CardHeader>
              <CardContent>
                <FluxoCaixaChart data={data.grafico_diario} type="line" />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Visão Combinada - Fluxo e Saldo</CardTitle>
            </CardHeader>
            <CardContent>
              <FluxoCaixaChart data={data.grafico_diario} type="composed" />
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-2 gap-6">
            <ContasTable contas={data.contas_a_receber} title="Contas a Receber" />
            <ContasTable contas={data.contas_a_pagar} title="Contas a Pagar" />
          </div>
        </>
      )}
    </div>
  );
};

export default FluxoCaixa;
