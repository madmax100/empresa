import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Package, 
  Calculator, 
  Calendar,
  BarChart3 
} from 'lucide-react';
import { useGerencia, type DateRange } from '../../hooks/useGerencia';
import { GerenciaService, type ResultadoMensal } from '../../services/gerencia-service';

const GerenciaDashboard: React.FC = () => {
  const [dataInicio, setDataInicio] = useState<string>(
    new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]
  );
  const [dataFim, setDataFim] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  
  const { data, loading, error, fetchGerencia } = useGerencia();
  const [activeTab, setActiveTab] = useState<'visao-geral' | 'resultados-mensais'>('visao-geral');
  const [mensais, setMensais] = useState<ResultadoMensal[] | null>(null);
  const [loadingMensais, setLoadingMensais] = useState(false);
  const [errorMensais, setErrorMensais] = useState<string | null>(null);

  useEffect(() => {
    const dateRange: DateRange = {
      from: new Date(dataInicio),
      to: new Date(dataFim)
    };
    fetchGerencia(dateRange);
    // Também pré-carrega os resultados mensais
    (async () => {
      try {
        setLoadingMensais(true);
        setErrorMensais(null);
        const res = await GerenciaService.calcularResultadosMensais(dataInicio, dataFim);
        setMensais(res);
      } catch (e) {
        const msg = e instanceof Error ? e.message : 'Erro ao carregar resultados mensais';
        setErrorMensais(msg);
      } finally {
        setLoadingMensais(false);
      }
    })();
  }, [dataInicio, dataFim, fetchGerencia]);

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div style={{ fontSize: '18px', color: '#666' }}>Carregando dados...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '20px', 
        textAlign: 'center',
        color: '#d32f2f',
        backgroundColor: '#ffebee',
        borderRadius: '8px',
        margin: '20px'
      }}>
        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>Erro ao carregar dados</div>
        <div style={{ marginTop: '8px' }}>{error}</div>
      </div>
    );
  }

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const calcularLucroTotal = () => {
    if (!data) return 0;
    return data.faturamentoContratos - data.custosFixos - data.custosVariaveis;
  };

  const calcularMargemLucro = () => {
    if (!data || !data.faturamentoContratos) return 0;
    const lucro = calcularLucroTotal();
    return (lucro / data.faturamentoContratos) * 100;
  };

  const calcularVariacaoEstoque = () => {
    if (!data) return 0;
    return data.estoqueFim - data.estoqueInicio;
  };

  const calcularIndicadorEstoque = () => {
    const variacao = calcularVariacaoEstoque();
    if (variacao > 0) return { texto: 'Aumento', cor: '#2e7d32', icone: '📈' };
    if (variacao < 0) return { texto: 'Redução', cor: '#d32f2f', icone: '📉' };
    return { texto: 'Estável', cor: '#f57c00', icone: '➡️' };
  };

  // Saldo em aberto na data de corte: Receber - Pagar
  const saldoInicio = (data?.contasReceberInicio || 0) - (data?.contasPagarInicio || 0);
  const saldoFim = (data?.contasReceberFim || 0) - (data?.contasPagarFim || 0);
  const saldoColor = (v: number) => (v > 0 ? '#16a34a' : v < 0 ? '#dc2626' : '#475569');

  // Variação do saldo desconsiderando custos fixos (retira FIXO do A Pagar)
  const pagarInicioSemFixos = (data?.contasPagarInicio || 0) - (data?.contasPagarInicioFixos || 0);
  const pagarFimSemFixos = (data?.contasPagarFim || 0) - (data?.contasPagarFimFixos || 0);
  const saldoInicioSemFixos = (data?.contasReceberInicio || 0) - pagarInicioSemFixos;
  const saldoFimSemFixos = (data?.contasReceberFim || 0) - pagarFimSemFixos;
  const variacaoSaldoSemFixos = saldoFimSemFixos - saldoInicioSemFixos;

  return (
    <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ 
          fontSize: '32px', 
          fontWeight: 'bold', 
          color: '#333', 
          marginBottom: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <BarChart3 size={36} color="#1976d2" />
          Painel de Gerencia
        </h1>
        <p style={{ fontSize: '16px', color: '#666' }}>
          Visao geral dos indicadores financeiros da empresa
        </p>
        {/* Abas */}
        <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
          <button
            onClick={() => setActiveTab('visao-geral')}
            style={{
              padding: '8px 12px',
              borderRadius: 6,
              border: '1px solid #e5e7eb',
              backgroundColor: activeTab === 'visao-geral' ? '#3b82f6' : 'white',
              color: activeTab === 'visao-geral' ? 'white' : '#374151',
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            Visão geral
          </button>
          <button
            onClick={() => setActiveTab('resultados-mensais')}
            style={{
              padding: '8px 12px',
              borderRadius: 6,
              border: '1px solid #e5e7eb',
              backgroundColor: activeTab === 'resultados-mensais' ? '#3b82f6' : 'white',
              color: activeTab === 'resultados-mensais' ? 'white' : '#374151',
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            Resultados por mês
          </button>
        </div>
        {data && (
          <div style={{ 
            marginTop: '16px',
            padding: '12px 16px',
            backgroundColor: data.fonteDados.isToday ? '#eff6ff' : '#fef3c7',
            border: `1px solid ${data.fonteDados.isToday ? '#bfdbfe' : '#fcd34d'}`,
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px'
          }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: data.fonteDados.isToday ? '#3b82f6' : '#f59e0b' 
            }} />
            <span style={{ fontWeight: '500', color: '#374151' }}>
              📊 Fonte dos dados: {data.fonteDados.estoque === 'atual' ? 'Atual' : 'Histórico'}
            </span>
            <span style={{ color: '#6b7280' }}>
              • Período: {data.fonteDados.periodo}
            </span>
            {data.fonteDados.isToday && (
              <span style={{ 
                color: '#059669', 
                fontSize: '12px',
                padding: '2px 6px',
                backgroundColor: '#d1fae5',
                borderRadius: '4px',
                fontWeight: '500'
              }}>
                TEMPO REAL
              </span>
            )}
          </div>
        )}
      </div>
      {activeTab === 'visao-geral' && (
      <div style={{ 
        backgroundColor: '#eff6ff',
        border: '1px solid #bfdbfe',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '24px'
      }}>
        <h3 style={{ 
          fontSize: '1rem', 
          fontWeight: '600', 
          color: '#1e40af',
          marginBottom: '8px'
        }}>
          📋 Regras de Negócio - Lógica do Controle de Estoque
        </h3>
        <div style={{ fontSize: '0.875rem', color: '#1e40af', lineHeight: '1.5' }}>
          • <strong>Data atual:</strong> Usa dados em tempo real dos sistemas<br/>
          • <strong>Datas históricas:</strong> Calcula baseado em movimentações e períodos<br/>
          • <strong>Estoque inteligente:</strong> Aplica regras de documento_referencia para precisão<br/>
          • <strong>Fonte automática:</strong> Sistema escolhe automaticamente a melhor fonte de dados
        </div>
      </div>
      )}

      <div style={{ marginBottom: '24px', display: 'flex', gap: '16px' }}>
        <label style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px',
          fontSize: '16px',
          fontWeight: '500',
          color: '#333'
        }}>
          <Calendar size={20} />
          Data Inicio:
          <input
            type="date"
            value={dataInicio}
            onChange={(e) => setDataInicio(e.target.value)}
            style={{
              padding: '8px 12px',
              border: '1px solid #ddd',
              borderRadius: '6px',
              fontSize: '16px',
              marginLeft: '8px'
            }}
          />
        </label>
        <label style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px',
          fontSize: '16px',
          fontWeight: '500',
          color: '#333'
        }}>
          Data Fim:
          <input
            type="date"
            value={dataFim}
            onChange={(e) => setDataFim(e.target.value)}
            style={{
              padding: '8px 12px',
              border: '1px solid #ddd',
              borderRadius: '6px',
              fontSize: '16px',
              marginLeft: '8px'
            }}
          />
        </label>
      </div>

    {activeTab === 'visao-geral' && (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '20px' }}>
        {/* Contas por Data de Corte - Início do Período */}
        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Calendar size={24} color="#0ea5e9" />
            Contas na Data de Corte (Início)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '14px', color: '#475569' }}>A Receber</div>
              <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#16a34a' }}>
                {formatCurrency(data?.contasReceberInicio || 0)}
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>
                {data?.contasReceberInicioCount ?? 0} títulos
              </div>
              <div style={{ marginTop: '6px', fontSize: '12px', color: '#0f766e', background: '#ecfeff', border: '1px solid #99f6e4', borderRadius: 6, padding: '6px 8px' }}>
                • Com contrato: <strong>{formatCurrency(data?.contasReceberInicioContratos || 0)}</strong>
                {typeof data?.contasReceberInicioContratosCount === 'number' && (
                  <span> ({data?.contasReceberInicioContratosCount})</span>
                )}
              </div>
              <div style={{ marginTop: '6px', fontSize: '12px', color: '#1f2937', background: '#f9fafb', border: '1px dashed #d1d5db', borderRadius: 6, padding: '6px 8px' }}>
                • Vendas: <strong>{formatCurrency(Math.max(0, (data?.contasReceberInicio || 0) - (data?.contasReceberInicioContratos || 0)))}</strong>
                {typeof data?.contasReceberInicioCount === 'number' && typeof data?.contasReceberInicioContratosCount === 'number' && (
                  <span> ({Math.max(0, (data?.contasReceberInicioCount || 0) - (data?.contasReceberInicioContratosCount || 0))})</span>
                )}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '14px', color: '#475569' }}>A Pagar</div>
              <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#dc2626' }}>
                {formatCurrency(data?.contasPagarInicio || 0)}
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>
                {data?.contasPagarInicioCount ?? 0} títulos
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#475569' }}>
                <div>
                  • Fixos: <strong>{formatCurrency(data?.contasPagarInicioFixos || 0)}</strong> ({data?.contasPagarInicioFixosCount ?? 0})
                </div>
                <div>
                  • Variáveis: <strong>{formatCurrency(data?.contasPagarInicioVariaveis || 0)}</strong> ({data?.contasPagarInicioVariaveisCount ?? 0})
                </div>
                {(data?.contasPagarInicioOutros ?? 0) > 0 && (
                  <div>
                    • Outros: <strong>{formatCurrency(data?.contasPagarInicioOutros || 0)}</strong> ({data?.contasPagarInicioOutrosCount ?? 0})
                  </div>
                )}
              </div>
            </div>
            <div style={{ gridColumn: '1 / -1', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e5e7eb' }}>
              <div style={{ fontSize: '14px', color: '#475569' }}>Saldo (Receber - Pagar)</div>
              <div style={{ fontSize: '22px', fontWeight: 'bold', color: saldoColor(saldoInicio) }}>
                {formatCurrency(saldoInicio)}
              </div>
              <div style={{ marginTop: '8px' }}>
                <div style={{ fontSize: '14px', color: '#475569' }}>Saldo sem Custos Fixos</div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: saldoColor(saldoInicioSemFixos) }}>
                  {formatCurrency(saldoInicioSemFixos)}
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Contas por Data de Corte - Fim do Período */}
        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Calendar size={24} color="#0284c7" />
            Contas na Data de Corte (Fim)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '14px', color: '#475569' }}>A Receber</div>
              <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#16a34a' }}>
                {formatCurrency(data?.contasReceberFim || 0)}
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>
                {data?.contasReceberFimCount ?? 0} títulos
              </div>
              <div style={{ marginTop: '6px', fontSize: '12px', color: '#0f766e', background: '#ecfeff', border: '1px solid #99f6e4', borderRadius: 6, padding: '6px 8px' }}>
                • Com contrato: <strong>{formatCurrency(data?.contasReceberFimContratos || 0)}</strong>
                {typeof data?.contasReceberFimContratosCount === 'number' && (
                  <span> ({data?.contasReceberFimContratosCount})</span>
                )}
              </div>
              <div style={{ marginTop: '6px', fontSize: '12px', color: '#1f2937', background: '#f9fafb', border: '1px dashed #d1d5db', borderRadius: 6, padding: '6px 8px' }}>
                • Vendas: <strong>{formatCurrency(Math.max(0, (data?.contasReceberFim || 0) - (data?.contasReceberFimContratos || 0)))}</strong>
                {typeof data?.contasReceberFimCount === 'number' && typeof data?.contasReceberFimContratosCount === 'number' && (
                  <span> ({Math.max(0, (data?.contasReceberFimCount || 0) - (data?.contasReceberFimContratosCount || 0))})</span>
                )}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '14px', color: '#475569' }}>A Pagar</div>
              <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#dc2626' }}>
                {formatCurrency(data?.contasPagarFim || 0)}
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>
                {data?.contasPagarFimCount ?? 0} títulos
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#475569' }}>
                <div>
                  • Fixos: <strong>{formatCurrency(data?.contasPagarFimFixos || 0)}</strong> ({data?.contasPagarFimFixosCount ?? 0})
                </div>
                <div>
                  • Variáveis: <strong>{formatCurrency(data?.contasPagarFimVariaveis || 0)}</strong> ({data?.contasPagarFimVariaveisCount ?? 0})
                </div>
                {(data?.contasPagarFimOutros ?? 0) > 0 && (
                  <div>
                    • Outros: <strong>{formatCurrency(data?.contasPagarFimOutros || 0)}</strong> ({data?.contasPagarFimOutrosCount ?? 0})
                  </div>
                )}
              </div>
            </div>
            <div style={{ gridColumn: '1 / -1', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e5e7eb' }}>
              <div style={{ fontSize: '14px', color: '#475569' }}>Saldo (Receber - Pagar)</div>
              <div style={{ fontSize: '22px', fontWeight: 'bold', color: saldoColor(saldoFim) }}>
                {formatCurrency(saldoFim)}
              </div>
              <div style={{ marginTop: '8px' }}>
                <div style={{ fontSize: '14px', color: '#475569' }}>Saldo sem Custos Fixos</div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: saldoColor(saldoFimSemFixos) }}>
                  {formatCurrency(saldoFimSemFixos)}
                </div>
              </div>
            </div>
          </div>
  </div>
  {/* Variação do Saldo (Fim - Início) */}
  <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={24} color="#334155" />
            Variação do Saldo (Fim - Início)
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: saldoColor(saldoFim - saldoInicio) }}>
            {formatCurrency(saldoFim - saldoInicio)}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            {saldoFim - saldoInicio > 0 ? 'Aumento do saldo em aberto' : (saldoFim - saldoInicio < 0 ? 'Redução do saldo em aberto' : 'Saldo estável no período')}
          </div>
          <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #e5e7eb' }}>
            <div style={{ fontSize: '14px', color: '#475569', fontWeight: 600 }}>Sem Custos Fixos</div>
            <div style={{ fontSize: '22px', fontWeight: 'bold', color: saldoColor(variacaoSaldoSemFixos) }}>
              {formatCurrency(variacaoSaldoSemFixos)}
            </div>
          </div>
        </div>
      </div>
  )}

  {activeTab === 'visao-geral' && (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '20px' }}>
        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Package size={24} color="#1976d2" />
            Estoque Inicio
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#2e7d32' }}>
            {formatCurrency(data?.estoqueInicio || 0)}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            Valor no inicio do periodo
          </div>
        </div>

        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Package size={24} color="#1976d2" />
            Estoque Fim
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#2e7d32' }}>
            {formatCurrency(data?.estoqueFim || 0)}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            Valor no fim do periodo
          </div>
        </div>

        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Package size={24} color="#1976d2" />
            Variação Estoque <span style={{ fontSize: '16px' }}>{calcularIndicadorEstoque().icone}</span>
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: calcularIndicadorEstoque().cor }}>
            {formatCurrency(Math.abs(calcularVariacaoEstoque()))}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            {calcularIndicadorEstoque().texto} no período
          </div>
        </div>
  </div>
  )}

  {activeTab === 'visao-geral' && (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '20px' }}>
        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={24} color="#2e7d32" />
            Faturamento Contratos
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#2e7d32' }}>
            {formatCurrency(data?.faturamentoContratos || 0)}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            Receita do periodo
          </div>
        </div>
  </div>
  )}

  {activeTab === 'visao-geral' && (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Calculator size={24} color="#f57c00" />
            Custos Fixos
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#f57c00' }}>
            {formatCurrency(data?.custosFixos || 0)}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            Custos fixos do periodo
          </div>
        </div>

        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingDown size={24} color="#d32f2f" />
            Custos Variaveis
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#d32f2f' }}>
            {formatCurrency(data?.custosVariaveis || 0)}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            Custos variaveis do periodo
          </div>
        </div>

        <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', border: '1px solid #e0e0e0' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={24} color="#2e7d32" />
            Lucro Total
          </div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: calcularLucroTotal() >= 0 ? '#2e7d32' : '#d32f2f' }}>
            {formatCurrency(calcularLucroTotal())}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
            Margem: {calcularMargemLucro().toFixed(2)}%
          </div>
        </div>
      </div>
      )}

      {activeTab === 'resultados-mensais' && (
        <div style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e5e7eb' }}>
          <h3 style={{ fontSize: 18, fontWeight: 700, color: '#111827', marginBottom: 12 }}>Resultados por mês</h3>
          <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 12 }}>
            Para cada mês: Resultado = Variação do Saldo sem Custos Fixos + Variação do Estoque
          </div>
          {loadingMensais && (
            <div style={{ padding: 12, color: '#6b7280' }}>Carregando resultados mensais...</div>
          )}
          {errorMensais && (
            <div style={{ padding: 12, color: '#dc2626', backgroundColor: '#fee2e2', borderRadius: 8 }}>{errorMensais}</div>
          )}
          {!loadingMensais && mensais && mensais.length > 0 && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Mês</th>
                    <th style={{ textAlign: 'right', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Saldo s/ Fixos (Início)</th>
                    <th style={{ textAlign: 'right', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Saldo s/ Fixos (Fim)</th>
                    <th style={{ textAlign: 'right', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Variação Saldo s/ Fixos</th>
                    <th style={{ textAlign: 'right', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Estoque (Início)</th>
                    <th style={{ textAlign: 'right', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Estoque (Fim)</th>
                    <th style={{ textAlign: 'right', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Variação Estoque</th>
                    <th style={{ textAlign: 'right', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Resultado Mensal</th>
                  </tr>
                </thead>
                <tbody>
                  {mensais.map((m) => (
                    <tr key={m.mes}>
                      <td style={{ padding: 8, borderBottom: '1px solid #f1f5f9' }}>{m.mes}</td>
                      <td style={{ padding: 8, borderBottom: '1px solid #f1f5f9', textAlign: 'right' }}>{formatCurrency(m.saldo_sem_fixos_inicio)}</td>
                      <td style={{ padding: 8, borderBottom: '1px solid #f1f5f9', textAlign: 'right' }}>{formatCurrency(m.saldo_sem_fixos_fim)}</td>
                      <td style={{ padding: 8, borderBottom: '1px solid #f1f5f9', textAlign: 'right', color: m.variacao_saldo_sem_fixos >= 0 ? '#16a34a' : '#dc2626' }}>{formatCurrency(m.variacao_saldo_sem_fixos)}</td>
                      <td style={{ padding: 8, borderBottom: '1px solid #f1f5f9', textAlign: 'right' }}>{formatCurrency(m.estoque_inicio)}</td>
                      <td style={{ padding: 8, borderBottom: '1px solid #f1f5f9', textAlign: 'right' }}>{formatCurrency(m.estoque_fim)}</td>
                      <td style={{ padding: 8, borderBottom: '1px solid #f1f5f9', textAlign: 'right', color: m.variacao_estoque >= 0 ? '#16a34a' : '#dc2626' }}>{formatCurrency(m.variacao_estoque)}</td>
                      <td style={{ padding: 8, borderBottom: '1px solid #f1f5f9', textAlign: 'right', fontWeight: 700, color: m.resultado_mensal >= 0 ? '#16a34a' : '#dc2626' }}>{formatCurrency(m.resultado_mensal)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td style={{ padding: 8, borderTop: '2px solid #e5e7eb', fontWeight: 700 }}>Totais</td>
                    <td></td>
                    <td></td>
                    <td style={{ padding: 8, borderTop: '2px solid #e5e7eb', textAlign: 'right', fontWeight: 700 }}>
                      {formatCurrency(mensais.reduce((acc, m) => acc + m.variacao_saldo_sem_fixos, 0))}
                    </td>
                    <td></td>
                    <td></td>
                    <td style={{ padding: 8, borderTop: '2px solid #e5e7eb', textAlign: 'right', fontWeight: 700 }}>
                      {formatCurrency(mensais.reduce((acc, m) => acc + m.variacao_estoque, 0))}
                    </td>
                    <td style={{ padding: 8, borderTop: '2px solid #e5e7eb', textAlign: 'right', fontWeight: 700 }}>
                      {formatCurrency(mensais.reduce((acc, m) => acc + m.resultado_mensal, 0))}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
          {!loadingMensais && (!mensais || mensais.length === 0) && (
            <div style={{ padding: 12, color: '#6b7280' }}>Sem dados para o período selecionado.</div>
          )}
        </div>
      )}
    </div>
  );
};

export default GerenciaDashboard;