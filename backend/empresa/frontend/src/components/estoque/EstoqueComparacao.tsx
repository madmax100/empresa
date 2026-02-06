import React, { useState, useEffect, useMemo } from 'react';
import { RefreshCw } from 'lucide-react';
import api from '../../services/api';

interface ComparativoItem {
    produto_id: number;
    codigo: string;
    nome: string;
    fiscal: {
        entrada: number;
        saida: number;
        saldo_fluxo: number;
        valor_entrada: number;
        valor_saida: number;
        valor_saldo_fluxo: number;
    };
    fisico: {
        saldo_inicial: number;
        entrada: number;
        saida: number;
        saldo_fluxo: number;
        saldo_final: number;
        valor_entrada: number;
        valor_saida: number;
        valor_saldo_inicial: number;
        valor_saldo_final: number;
    };
    diferenca: {
        entrada: number;
        saida: number;
        saldo_fluxo: number;
    };
}

interface ComparativoResponse {
    periodo: {
        inicio: string;
        fim: string;
    };
    comparativo: ComparativoItem[];
}

interface ComparativoProps {
    dataInicio: string;
    dataFim: string;
}


// ============================================================================
// Modal de Detalhes
// ============================================================================
interface itemDetalhe {
    data: string;
    documento: string;
    parceiro: string;
    quantidade: number;
    valor_unitario: number;
    valor_total: number;
}

const ModalDetalhe: React.FC<{
    isOpen: boolean;
    onClose: () => void;
    titulo: string;
    dados: itemDetalhe[];
    loading: boolean;
}> = ({ isOpen, onClose, titulo, dados, loading }) => {
    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000
        }}>
            <div style={{
                backgroundColor: 'white', borderRadius: '8px', width: '90%', maxWidth: '800px',
                maxHeight: '90vh', display: 'flex', flexDirection: 'column', boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
                <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#111827' }}>{titulo}</h3>
                    <button onClick={onClose} style={{ border: 'none', background: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#6b7280' }}>&times;</button>
                </div>

                <div style={{ padding: '0', overflowY: 'auto', flex: 1 }}>
                    {loading ? (
                        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>Carregando detalhes...</div>
                    ) : dados.length === 0 ? (
                        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>Nenhum registro encontrado.</div>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                            <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f9fafb' }}>
                                <tr style={{ borderBottom: '1px solid #e5e7eb', color: '#4b5563', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                                    <th style={{ padding: '12px', textAlign: 'left' }}>Data</th>
                                    <th style={{ padding: '12px', textAlign: 'left' }}>Documento</th>
                                    <th style={{ padding: '12px', textAlign: 'left' }}>Parceiro / Tipo</th>
                                    <th style={{ padding: '12px', textAlign: 'right' }}>Qtd</th>
                                    <th style={{ padding: '12px', textAlign: 'right' }}>Unit. (R$)</th>
                                    <th style={{ padding: '12px', textAlign: 'right' }}>Total (R$)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {dados.map((item, index) => (
                                    <tr key={index} style={{ borderBottom: '1px solid #f3f4f6', backgroundColor: index % 2 === 0 ? 'white' : '#f9fafb' }}>
                                        <td style={{ padding: '10px 12px' }}>{item.data}</td>
                                        <td style={{ padding: '10px 12px' }}>{item.documento}</td>
                                        <td style={{ padding: '10px 12px' }}>{item.parceiro}</td>
                                        <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: '500' }}>
                                            {item.quantidade.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 3 })}
                                        </td>
                                        <td style={{ padding: '10px 12px', textAlign: 'right', color: '#6b7280' }}>
                                            {item.valor_unitario.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                        </td>
                                        <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: '600', color: '#111827' }}>
                                            {item.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                <div style={{ padding: '16px', borderTop: '1px solid #e5e7eb', textAlign: 'right' }}>
                    <button
                        onClick={onClose}
                        style={{ padding: '8px 16px', backgroundColor: '#e5e7eb', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: '500', color: '#374151' }}
                    >
                        Fechar
                    </button>
                </div>
            </div>
        </div>
    );
};

const EstoqueComparacao: React.FC<ComparativoProps> = ({ dataInicio, dataFim }) => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<ComparativoResponse | null>(null);

    // Estado do Modal
    const [modalOpen, setModalOpen] = useState(false);
    const [modalLoading, setModalLoading] = useState(false);
    const [modalTitulo, setModalTitulo] = useState('');
    const [modalDados, setModalDados] = useState<itemDetalhe[]>([]);

    const carregarDados = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/api/estoque-comparativo/?data_inicio=${dataInicio}&data_fim=${dataFim}`);
            setData(response.data);
        } catch (error) {
            console.error('Erro ao carregar comparativo:', error);
            alert('Erro ao carregar dados do comparativo.');
        } finally {
            setLoading(false);
        }
    };

    const abrirDetalhe = async (produto: ComparativoItem, tipo: 'fiscal_entrada' | 'fiscal_saida' | 'fisico_entrada' | 'fisico_saida', titulo: string) => {
        setModalTitulo(`${titulo} - ${produto.nome}`);
        setModalOpen(true);
        setModalLoading(true);
        setModalDados([]);

        try {
            const response = await api.get(`/api/estoque-comparativo/`, {
                params: {
                    acao: 'detalhe',
                    tipo: tipo,
                    produto_id: produto.produto_id,
                    data_inicio: dataInicio,
                    data_fim: dataFim
                }
            });
            setModalDados(response.data);
        } catch (error) {
            console.error('Erro ao carregar detalhes:', error);
            alert('Erro ao carregar detalhes.');
            setModalOpen(false);
        } finally {
            setModalLoading(false);
        }
    };

    useEffect(() => {
        carregarDados();
    }, [dataInicio, dataFim]);

    const totais = useMemo(() => {
        if (!data?.comparativo) return null;
        return data.comparativo.reduce((acc, item) => ({
            fiscal: {
                entrada: acc.fiscal.entrada + item.fiscal.entrada,
                saida: acc.fiscal.saida + item.fiscal.saida,
                saldo_fluxo: acc.fiscal.saldo_fluxo + item.fiscal.saldo_fluxo,
                valor_entrada: acc.fiscal.valor_entrada + (item.fiscal.valor_entrada || 0),
                valor_saida: acc.fiscal.valor_saida + (item.fiscal.valor_saida || 0),
                valor_saldo_fluxo: acc.fiscal.valor_saldo_fluxo + (item.fiscal.valor_saldo_fluxo || 0),
            },
            fisico: {
                saldo_inicial: acc.fisico.saldo_inicial + item.fisico.saldo_inicial,
                entrada: acc.fisico.entrada + item.fisico.entrada,
                saida: acc.fisico.saida + item.fisico.saida,
                saldo_final: acc.fisico.saldo_final + item.fisico.saldo_final,
                valor_entrada: acc.fisico.valor_entrada + (item.fisico.valor_entrada || 0),
                valor_saida: acc.fisico.valor_saida + (item.fisico.valor_saida || 0),
                valor_saldo_final: acc.fisico.valor_saldo_final + (item.fisico.valor_saldo_final || 0),
            }
        }), {
            fiscal: { entrada: 0, saida: 0, saldo_fluxo: 0, valor_entrada: 0, valor_saida: 0, valor_saldo_fluxo: 0 },
            fisico: { saldo_inicial: 0, entrada: 0, saida: 0, saldo_final: 0, valor_entrada: 0, valor_saida: 0, valor_saldo_final: 0 }
        });
    }, [data]);

    return (
        <div style={{ padding: '20px' }}>
            {/* Modal de Detalhes */}
            <ModalDetalhe
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                titulo={modalTitulo}
                dados={modalDados}
                loading={modalLoading}
            />

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ margin: 0, color: '#1f2937' }}>Comparativo de Estoque: Fiscal x Físico</h2>

                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <button
                        onClick={carregarDados}
                        disabled={loading}
                        style={{
                            display: 'flex', alignItems: 'center', gap: '8px',
                            padding: '8px 16px', backgroundColor: '#3b82f6', color: 'white',
                            border: 'none', borderRadius: '4px', cursor: 'pointer',
                            opacity: loading ? 0.7 : 1
                        }}
                    >
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                        Atualizar
                    </button>
                </div>
            </div>

            {/* Cards de Resumo */}
            {totais && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '24px' }}>
                    {/* Card Físico (Real) */}
                    <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden', borderLeft: '4px solid #16a34a' }}>
                        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f0fdf4', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0, color: '#166534', fontSize: '1.1rem' }}>Estoque Físico (Real)</h3>
                            <span style={{ fontSize: '0.8rem', color: '#166534', backgroundColor: '#dcfce7', padding: '2px 8px', borderRadius: '12px' }}>Base: Movimentações</span>
                        </div>
                        <div style={{ padding: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '16px', textAlign: 'center' }}>
                            <div>
                                <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '4px' }}>Entradas</div>
                                <div style={{ fontSize: '1.25rem', fontWeight: '600', color: '#16a34a' }}>{totais.fisico.entrada.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}</div>
                                <div style={{ fontSize: '0.75rem', color: '#16a34a', marginTop: '4px' }}>
                                    {totais.fisico.valor_entrada.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '4px' }}>Saídas</div>
                                <div style={{ fontSize: '1.25rem', fontWeight: '600', color: '#dc2626' }}>{totais.fisico.saida.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}</div>
                                <div style={{ fontSize: '0.75rem', color: '#dc2626', marginTop: '4px' }}>
                                    {totais.fisico.valor_saida.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '4px' }}>Variação</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>
                                    {(totais.fisico.entrada - totais.fisico.saida).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: '#374151', marginTop: '4px' }}>
                                    {(totais.fisico.valor_entrada - totais.fisico.valor_saida).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '4px' }}>Saldo Atual</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{totais.fisico.saldo_final.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}</div>
                                <div style={{ fontSize: '0.75rem', color: '#374151', marginTop: '4px' }}>
                                    {totais.fisico.valor_saldo_final.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Card Fiscal (Notas) */}
                    <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden', borderLeft: '4px solid #2563eb' }}>
                        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#eff6ff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0, color: '#1e40af', fontSize: '1.1rem' }}>Estoque Fiscal (Notas)</h3>
                            <span style={{ fontSize: '0.8rem', color: '#1e40af', backgroundColor: '#dbeafe', padding: '2px 8px', borderRadius: '12px' }}>Base: NFe/NFS</span>
                        </div>
                        <div style={{ padding: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', textAlign: 'center' }}>
                            <div>
                                <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '4px' }}>Entradas</div>
                                <div style={{ fontSize: '1.25rem', fontWeight: '600', color: '#2563eb' }}>{totais.fiscal.entrada.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}</div>
                                <div style={{ fontSize: '0.75rem', color: '#2563eb', marginTop: '4px' }}>
                                    {totais.fiscal.valor_entrada.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '4px' }}>Saídas</div>
                                <div style={{ fontSize: '1.25rem', fontWeight: '600', color: '#dc2626' }}>{totais.fiscal.saida.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}</div>
                                <div style={{ fontSize: '0.75rem', color: '#dc2626', marginTop: '4px' }}>
                                    {totais.fiscal.valor_saida.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '4px' }}>Variação Período</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>{totais.fiscal.saldo_fluxo.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}</div>
                                <div style={{ fontSize: '0.75rem', color: '#374151', marginTop: '4px' }}>
                                    {totais.fiscal.valor_saldo_fluxo.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                    <thead>
                        <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
                            <th style={{ padding: '12px', textAlign: 'left', width: '25%' }}>Produto</th>

                            <th style={{ padding: '8px', textAlign: 'center', backgroundColor: '#f0fdf4', borderLeft: '1px solid #e5e7eb' }} colSpan={5}>
                                Físico (Real)
                            </th>

                            <th style={{ padding: '8px', textAlign: 'center', backgroundColor: '#eff6ff', borderLeft: '1px solid #e5e7eb' }} colSpan={3}>
                                Fiscal (Notas)
                            </th>

                            <th style={{ padding: '8px', textAlign: 'center', backgroundColor: '#fef2f2', borderLeft: '1px solid #e5e7eb' }} colSpan={1}>
                                Dif.
                            </th>
                        </tr>
                        <tr style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb', fontSize: '11px', color: '#6b7280' }}>
                            <th style={{ padding: '8px 12px', textAlign: 'left' }}></th>

                            {/* Físico */}
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#f0fdf4', borderLeft: '1px solid #e5e7eb' }}>S. Inic</th>
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#f0fdf4', color: '#16a34a' }}>Entrada</th>
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#f0fdf4', color: '#dc2626' }}>Saída</th>
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#f0fdf4' }}>Var.</th>
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#dcfce7', fontWeight: 'bold' }}>S. Final</th>

                            {/* Fiscal */}
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#eff6ff', borderLeft: '1px solid #e5e7eb' }}>Entrada</th>
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#eff6ff' }}>Saída</th>
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#eff6ff' }}>Var.</th>

                            {/* Diferença */}
                            <th style={{ padding: '8px', textAlign: 'right', backgroundColor: '#fef2f2', borderLeft: '1px solid #e5e7eb' }}>Fluxo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan={10} style={{ padding: '40px', textAlign: 'center' }}>Carregando dados...</td></tr>
                        ) : !data?.comparativo.length ? (
                            <tr><td colSpan={10} style={{ padding: '40px', textAlign: 'center' }}>Nenhum dado encontrado para o período.</td></tr>
                        ) : (
                            data.comparativo.map((item) => (
                                <tr key={item.produto_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                    <td style={{ padding: '12px' }}>
                                        <div style={{ fontWeight: '500', color: '#111827' }}>{item.nome}</div>
                                        <div style={{ fontSize: '12px', color: '#6b7280' }}>Cód: {item.codigo}</div>
                                    </td>

                                    {/* Físico */}
                                    <td style={{ padding: '12px', textAlign: 'right', backgroundColor: '#f0fdf4', borderLeft: '1px solid #e5e7eb', color: '#4b5563' }}>
                                        {item.fisico.saldo_inicial?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </td>

                                    {/* Físico Entrada (Clicável) */}
                                    <td
                                        onClick={() => item.fisico.entrada > 0 && abrirDetalhe(item, 'fisico_entrada', 'Entradas Físicas')}
                                        style={{
                                            padding: '12px', textAlign: 'right', backgroundColor: '#f0fdf4', color: '#16a34a',
                                            cursor: item.fisico.entrada > 0 ? 'pointer' : 'default',
                                            textDecoration: item.fisico.entrada > 0 ? 'underline' : 'none'
                                        }}
                                        title={item.fisico.entrada > 0 ? "Clique para ver detalhes" : ""}
                                    >
                                        {item.fisico.entrada > 0 ? item.fisico.entrada.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '-'}
                                    </td>

                                    {/* Físico Saída (Clicável) */}
                                    <td
                                        onClick={() => item.fisico.saida > 0 && abrirDetalhe(item, 'fisico_saida', 'Saídas Físicas')}
                                        style={{
                                            padding: '12px', textAlign: 'right', backgroundColor: '#f0fdf4', color: '#dc2626',
                                            cursor: item.fisico.saida > 0 ? 'pointer' : 'default',
                                            textDecoration: item.fisico.saida > 0 ? 'underline' : 'none'
                                        }}
                                        title={item.fisico.saida > 0 ? "Clique para ver detalhes" : ""}
                                    >
                                        {item.fisico.saida > 0 ? item.fisico.saida.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '-'}
                                    </td>

                                    <td style={{ padding: '12px', textAlign: 'right', backgroundColor: '#f0fdf4' }}>
                                        {item.fisico.saldo_fluxo?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </td>
                                    <td style={{ padding: '12px', textAlign: 'right', backgroundColor: '#dcfce7', fontWeight: 'bold', color: '#15803d' }}>
                                        {item.fisico.saldo_final?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </td>

                                    {/* Fiscal Entrada (Clicável) */}
                                    <td
                                        onClick={() => item.fiscal.entrada > 0 && abrirDetalhe(item, 'fiscal_entrada', 'Entradas Fiscais')}
                                        style={{
                                            padding: '12px', textAlign: 'right', backgroundColor: '#eff6ff', borderLeft: '1px solid #f3f4f6',
                                            cursor: item.fiscal.entrada > 0 ? 'pointer' : 'default',
                                            textDecoration: item.fiscal.entrada > 0 ? 'underline' : 'none'
                                        }}
                                        title={item.fiscal.entrada > 0 ? "Clique para ver detalhes" : ""}
                                    >
                                        {item.fiscal.entrada > 0 ? item.fiscal.entrada.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '-'}
                                    </td>

                                    {/* Fiscal Saída (Clicável) */}
                                    <td
                                        onClick={() => item.fiscal.saida > 0 && abrirDetalhe(item, 'fiscal_saida', 'Saídas Fiscais')}
                                        style={{
                                            padding: '12px', textAlign: 'right', backgroundColor: '#eff6ff',
                                            cursor: item.fiscal.saida > 0 ? 'pointer' : 'default',
                                            textDecoration: item.fiscal.saida > 0 ? 'underline' : 'none'
                                        }}
                                        title={item.fiscal.saida > 0 ? "Clique para ver detalhes" : ""}
                                    >
                                        {item.fiscal.saida > 0 ? item.fiscal.saida.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '-'}
                                    </td>

                                    <td style={{ padding: '12px', textAlign: 'right', backgroundColor: '#eff6ff', fontWeight: '600' }}>
                                        {item.fiscal.saldo_fluxo?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </td>

                                    {/* Diferença */}
                                    <td style={{ padding: '12px', textAlign: 'right', backgroundColor: '#fef2f2', borderLeft: '1px solid #e5e7eb', fontWeight: 'bold', color: item.diferenca.saldo_fluxo !== 0 ? '#dc2626' : '#9ca3af' }}>
                                        {item.diferenca.saldo_fluxo?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default EstoqueComparacao;
