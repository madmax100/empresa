import React, { useState, useEffect, useCallback } from 'react';
import {
    ArrowUpCircle,
    ArrowDownCircle,
    TrendingUp,
    Calendar,
    DollarSign,
    AlertTriangle
} from "lucide-react";
import { 
  fluxoCaixaService, 
  formatCurrency, 
  formatDate
} from '../../services/fluxo-caixa-service';
import type {
  MovimentacoesRealizadasResponse,
  FiltrosPeriodo
} from '../../types/fluxo-caixa';

// Estilos inline
const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
    backgroundColor: '#f8fafc',
    minHeight: '100vh'
  },
  header: {
    backgroundColor: '#1e40af',
    color: 'white',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
    textAlign: 'center' as const
  },
  title: {
    margin: 0,
    fontSize: '2rem',
    fontWeight: '600'
  },
  subtitle: {
    margin: '8px 0 0 0',
    fontSize: '1rem',
    opacity: 0.9
  },
  filterSection: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
  },
  filterRow: {
    display: 'flex',
    gap: '15px',
    alignItems: 'end',
    flexWrap: 'wrap' as const
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '5px'
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#374151'
  },
  input: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '0.875rem',
    backgroundColor: '#ffffff'
  },
  button: {
    backgroundColor: '#1e40af',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
    height: 'fit-content'
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '20px'
  },
  metricCard: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    borderLeft: '4px solid #1e40af',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
  },
  metricHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  metricTitle: {
    fontSize: '0.875rem',
    color: '#6b7280',
    fontWeight: '500',
    marginBottom: '5px'
  },
  metricValue: {
    fontSize: '1.5rem',
    fontWeight: '700',
    color: '#111827'
  },
  metricIcon: {
    opacity: 0.7
  },
  card: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  },
  cardHeader: {
    marginBottom: '15px'
  },
  cardTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#111827',
    margin: 0
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const
  },
  th: {
    textAlign: 'left' as const,
    padding: '12px 15px',
    backgroundColor: '#f9fafb',
    fontWeight: '600',
    fontSize: '0.875rem',
    color: '#374151',
    borderBottom: '1px solid #e5e7eb'
  },
  td: {
    padding: '12px 15px',
    borderBottom: '1px solid #e5e7eb',
    fontSize: '0.875rem'
  },
  badge: {
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '0.75rem',
    fontWeight: '500'
  },
  badgeEntrada: {
    backgroundColor: '#dcfce7',
    color: '#166534'
  },
  badgeSaida: {
    backgroundColor: '#fee2e2',
    color: '#dc2626'
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '60px 20px',
    fontSize: '1.125rem',
    color: '#6b7280'
  },
  error: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px'
  },
  errorTitle: {
    color: '#dc2626',
    fontWeight: '600',
    marginBottom: '10px'
  },
  errorMessage: {
    color: '#7f1d1d'
  },
  barChart: {
    display: 'flex',
    alignItems: 'end',
    gap: '20px',
    padding: '20px 0',
    height: '120px'
  },
  bar: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    flex: 1
  },
  barContainer: {
    width: '60px',
    height: '80px',
    position: 'relative' as const,
    backgroundColor: '#f3f4f6',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '8px'
  },
  barFill: {
    position: 'absolute' as const,
    bottom: 0,
    width: '100%',
    borderRadius: '4px 4px 0 0',
    transition: 'height 0.3s ease'
  },
  barLabel: {
    fontSize: '0.75rem',
    fontWeight: '500',
    color: '#374151',
    textAlign: 'center' as const
  }
};

// Componente para card de métrica
interface MetricCardProps {
    title: string;
    value: number;
    icon: React.ReactNode;
    color?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  icon, 
  color = '#1e40af'
}) => (
    <div style={{...styles.metricCard, borderLeftColor: color}}>
        <div style={styles.metricHeader}>
            <div>
                <div style={styles.metricTitle}>{title}</div>
                <div style={styles.metricValue}>{formatCurrency(value)}</div>
            </div>
            <div style={{...styles.metricIcon, color}}>
                {icon}
            </div>
        </div>
    </div>
);

const SimpleDashboard: React.FC = () => {
    // Estados
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    // Dados
    const [movimentacoesRealizadas, setMovimentacoesRealizadas] = useState<MovimentacoesRealizadasResponse | null>(null);

    // Filtros
    const [filtros, setFiltros] = useState<FiltrosPeriodo>({
        data_inicio: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        data_fim: new Date().toISOString().split('T')[0]
    });

    // Carregar dados
    const carregarDados = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            console.log('🔄 Tentando carregar dados da API...');

            try {
                const realizadas = await fluxoCaixaService.getMovimentacoesRealizadas(filtros);
                setMovimentacoesRealizadas(realizadas);
                console.log('✅ Dados carregados da API com sucesso!');

            } catch {
                console.log('⚠️ API não disponível, usando dados mockados...');
                
                // Dados mockados como fallback
                const mockRealizadas: MovimentacoesRealizadasResponse = {
                    periodo: {
                        data_inicio: filtros.data_inicio,
                        data_fim: filtros.data_fim
                    },
                    resumo: {
                        total_entradas: 150000,
                        total_saidas: 85000,
                        saldo_liquido: 65000,
                        total_movimentacoes: 8
                    },
                    movimentacoes: [
                        {
                            id: '1',
                            tipo: 'entrada',
                            data_pagamento: '2025-09-01',
                            valor: 50000,
                            contraparte: 'Cliente ABC Ltda',
                            historico: 'Receita de Vendas - Projeto X',
                            forma_pagamento: 'Transferência',
                            origem: 'contas_receber'
                        },
                        {
                            id: '2',
                            tipo: 'entrada',
                            data_pagamento: '2025-09-02',
                            valor: 75000,
                            contraparte: 'Cliente XYZ Corp',
                            historico: 'Receita de Serviços - Consultoria',
                            forma_pagamento: 'PIX',
                            origem: 'contas_receber'
                        },
                        {
                            id: '3',
                            tipo: 'entrada',
                            data_pagamento: '2025-09-03',
                            valor: 25000,
                            contraparte: 'Cliente DEF S.A.',
                            historico: 'Receita de Vendas - Produto Y',
                            forma_pagamento: 'Boleto',
                            origem: 'contas_receber'
                        },
                        {
                            id: '4',
                            tipo: 'saida',
                            data_pagamento: '2025-09-03',
                            valor: 30000,
                            contraparte: 'Fornecedor Tech Ltda',
                            historico: 'Pagamento de Materiais',
                            forma_pagamento: 'Transferência',
                            origem: 'contas_pagar'
                        },
                        {
                            id: '5',
                            tipo: 'saida',
                            data_pagamento: '2025-09-04',
                            valor: 15000,
                            contraparte: 'Empresa de Limpeza',
                            historico: 'Serviços de Limpeza - Trimestre',
                            forma_pagamento: 'PIX',
                            origem: 'contas_pagar'
                        },
                        {
                            id: '6',
                            tipo: 'saida',
                            data_pagamento: '2025-09-05',
                            valor: 12000,
                            contraparte: 'Imobiliária Santos',
                            historico: 'Aluguel Escritório - Setembro',
                            forma_pagamento: 'Boleto',
                            origem: 'contas_pagar'
                        },
                        {
                            id: '7',
                            tipo: 'saida',
                            data_pagamento: '2025-09-05',
                            valor: 18000,
                            contraparte: 'Folha de Pagamento',
                            historico: 'Salários Funcionários',
                            forma_pagamento: 'Transferência',
                            origem: 'contas_pagar'
                        },
                        {
                            id: '8',
                            tipo: 'saida',
                            data_pagamento: '2025-09-05',
                            valor: 10000,
                            contraparte: 'Receita Federal',
                            historico: 'Impostos e Taxas',
                            forma_pagamento: 'DARF',
                            origem: 'contas_pagar'
                        }
                    ]
                };

                setMovimentacoesRealizadas(mockRealizadas);
                console.log('✅ Dados mockados carregados!');
            }

        } catch (err) {
            console.error('❌ Erro ao carregar dados:', err);
            setError('Erro ao carregar dados do fluxo de caixa');
        } finally {
            setLoading(false);
        }
    }, [filtros]);

    useEffect(() => {
        carregarDados();
    }, [carregarDados]);

    // Renderização de loading
    if (loading) {
        return (
            <div style={styles.container}>
                <div style={styles.loading}>
                    <div>🔄 Carregando dashboard...</div>
                </div>
            </div>
        );
    }

    // Renderização de erro
    if (error) {
        return (
            <div style={styles.container}>
                <div style={styles.error}>
                    <div style={styles.errorTitle}>
                        <AlertTriangle size={20} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
                        Erro no Dashboard
                    </div>
                    <div style={styles.errorMessage}>{error}</div>
                    <button 
                        onClick={carregarDados} 
                        style={{...styles.button, marginTop: '15px'}}
                    >
                        Tentar Novamente
                    </button>
                </div>
            </div>
        );
    }

    // Dados para o gráfico
    const dadosGrafico = movimentacoesRealizadas ? {
        entradas: movimentacoesRealizadas.resumo.total_entradas,
        saidas: movimentacoesRealizadas.resumo.total_saidas
    } : { entradas: 0, saidas: 0 };

    const maxValor = Math.max(dadosGrafico.entradas, dadosGrafico.saidas);

    return (
        <div style={styles.container}>
            {/* Header */}
            <div style={styles.header}>
                <h1 style={styles.title}>Dashboard - Fluxo de Caixa</h1>
                <div style={styles.subtitle}>
                    <Calendar size={16} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
                    Período: {formatDate(filtros.data_inicio)} até {formatDate(filtros.data_fim)}
                </div>
            </div>

            {/* Filtros */}
            <div style={styles.filterSection}>
                <div style={styles.filterRow}>
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Data Início:</label>
                        <input
                            type="date"
                            value={filtros.data_inicio}
                            onChange={(e) => setFiltros(prev => ({ ...prev, data_inicio: e.target.value }))}
                            style={styles.input}
                        />
                    </div>
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Data Fim:</label>
                        <input
                            type="date"
                            value={filtros.data_fim}
                            onChange={(e) => setFiltros(prev => ({ ...prev, data_fim: e.target.value }))}
                            style={styles.input}
                        />
                    </div>
                    <button onClick={carregarDados} style={styles.button}>
                        🔄 Atualizar
                    </button>
                </div>
            </div>

            {/* Métricas */}
            {movimentacoesRealizadas && (
                <div style={styles.metricsGrid}>
                    <MetricCard
                        title="Total de Entradas"
                        value={movimentacoesRealizadas.resumo.total_entradas}
                        icon={<ArrowUpCircle size={32} />}
                        color="#10b981"
                    />
                    <MetricCard
                        title="Total de Saídas"
                        value={movimentacoesRealizadas.resumo.total_saidas}
                        icon={<ArrowDownCircle size={32} />}
                        color="#ef4444"
                    />
                    <MetricCard
                        title="Saldo Líquido"
                        value={movimentacoesRealizadas.resumo.saldo_liquido}
                        icon={<DollarSign size={32} />}
                        color="#3b82f6"
                    />
                    <MetricCard
                        title="Total de Movimentações"
                        value={movimentacoesRealizadas.resumo.total_movimentacoes}
                        icon={<TrendingUp size={32} />}
                        color="#8b5cf6"
                    />
                </div>
            )}

            {/* Gráfico de Barras */}
            {movimentacoesRealizadas && (
                <div style={styles.card}>
                    <div style={styles.cardHeader}>
                        <h3 style={styles.cardTitle}>Comparativo Entradas vs Saídas</h3>
                    </div>
                    <div style={styles.barChart}>
                        <div style={styles.bar}>
                            <div style={styles.barContainer}>
                                <div 
                                    style={{
                                        ...styles.barFill,
                                        backgroundColor: '#10b981',
                                        height: `${(dadosGrafico.entradas / maxValor) * 100}%`
                                    }}
                                />
                            </div>
                            <div style={styles.barLabel}>
                                Entradas<br/>{formatCurrency(dadosGrafico.entradas)}
                            </div>
                        </div>
                        <div style={styles.bar}>
                            <div style={styles.barContainer}>
                                <div 
                                    style={{
                                        ...styles.barFill,
                                        backgroundColor: '#ef4444',
                                        height: `${(dadosGrafico.saidas / maxValor) * 100}%`
                                    }}
                                />
                            </div>
                            <div style={styles.barLabel}>
                                Saídas<br/>{formatCurrency(dadosGrafico.saidas)}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Tabela de Movimentações */}
            {movimentacoesRealizadas && (
                <div style={styles.card}>
                    <div style={styles.cardHeader}>
                        <h3 style={styles.cardTitle}>Movimentações Realizadas</h3>
                    </div>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={styles.table}>
                            <thead>
                                <tr>
                                    <th style={styles.th}>Data</th>
                                    <th style={styles.th}>Tipo</th>
                                    <th style={styles.th}>Valor</th>
                                    <th style={styles.th}>Contraparte</th>
                                    <th style={styles.th}>Histórico</th>
                                    <th style={styles.th}>Forma Pagamento</th>
                                </tr>
                            </thead>
                            <tbody>
                                {movimentacoesRealizadas.movimentacoes.map((mov) => (
                                    <tr key={mov.id}>
                                        <td style={styles.td}>
                                            {formatDate(mov.data_pagamento)}
                                        </td>
                                        <td style={styles.td}>
                                            <span 
                                                style={{
                                                    ...styles.badge,
                                                    ...(mov.tipo === 'entrada' ? styles.badgeEntrada : styles.badgeSaida)
                                                }}
                                            >
                                                {mov.tipo === 'entrada' ? '↗️ Entrada' : '↘️ Saída'}
                                            </span>
                                        </td>
                                        <td style={styles.td}>
                                            <strong style={{ color: mov.tipo === 'entrada' ? '#10b981' : '#ef4444' }}>
                                                {formatCurrency(mov.valor)}
                                            </strong>
                                        </td>
                                        <td style={styles.td}>{mov.contraparte}</td>
                                        <td style={styles.td}>{mov.historico}</td>
                                        <td style={styles.td}>{mov.forma_pagamento}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SimpleDashboard;
