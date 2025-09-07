import React, { useState } from 'react';
import type { FiltrosContratos } from '../types/contratos';

interface FiltrosContratosProps {
  onFiltrosChange: (filtros: FiltrosContratos) => void;
  loading?: boolean;
}

export const FiltrosContratosComponent: React.FC<FiltrosContratosProps> = ({ 
  onFiltrosChange, 
  loading = false 
}) => {
  const [filtros, setFiltros] = useState<FiltrosContratos>({
    cliente: '',
    contrato: '',
    status: 'todos',
    dataInicio: '',
    dataFim: '',
    valorMin: undefined,
    valorMax: undefined,
    renovado: 'todos'
  });

  const handleInputChange = (field: keyof FiltrosContratos, value: string | number | undefined) => {
    const novosFiltros = { ...filtros, [field]: value };
    setFiltros(novosFiltros);
  };

  const aplicarFiltros = () => {
    // Remove campos vazios
    const filtrosLimpos = Object.entries(filtros).reduce((acc, [key, value]) => {
      if (value !== '' && value !== undefined && value !== 'todos') {
        acc[key as keyof FiltrosContratos] = value;
      }
      return acc;
    }, {} as FiltrosContratos);
    
    onFiltrosChange(filtrosLimpos);
  };

  const limparFiltros = () => {
    const filtrosVazios: FiltrosContratos = {
      cliente: '',
      contrato: '',
      status: 'todos',
      dataInicio: '',
      dataFim: '',
      valorMin: undefined,
      valorMax: undefined,
      renovado: 'todos'
    };
    setFiltros(filtrosVazios);
    onFiltrosChange({});
  };

  return (
    <div style={{
      backgroundColor: 'white',
      padding: '20px',
      borderRadius: '8px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      marginBottom: '24px'
    }}>
      {/* Header dos Filtros */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
        paddingBottom: '16px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            backgroundColor: '#dbeafe',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <span style={{ fontSize: '1.125rem' }}>🔍</span>
          </div>
          <div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111827', margin: 0 }}>
              Filtros de Pesquisa
            </h3>
            <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0 }}>
              Refine sua busca por contratos específicos
            </p>
          </div>
        </div>
        
        {/* Botões de Ação no Header */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={aplicarFiltros}
            disabled={loading}
            style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              padding: '8px 16px',
              borderRadius: '6px',
              border: 'none',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            {loading ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid white',
                  borderTop: '2px solid transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                Aplicando...
              </>
            ) : (
              <>
                <span>🔍</span>
                Aplicar
              </>
            )}
          </button>
          
          <button
            onClick={limparFiltros}
            disabled={loading}
            style={{
              backgroundColor: '#6b7280',
              color: 'white',
              padding: '8px 16px',
              borderRadius: '6px',
              border: 'none',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <span>🗑️</span>
            Limpar
          </button>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px'
      }}>
        {/* Cliente */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            👤 Cliente
          </label>
          <input
            type="text"
            value={filtros.cliente}
            onChange={(e) => handleInputChange('cliente', e.target.value)}
            placeholder="Nome do cliente..."
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '0.875rem',
              backgroundColor: loading ? '#f9fafb' : 'white',
              cursor: loading ? 'not-allowed' : 'text'
            }}
            disabled={loading}
          />
        </div>

        {/* Número do Contrato */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            📋 Número do Contrato
          </label>
          <input
            type="text"
            value={filtros.contrato}
            onChange={(e) => handleInputChange('contrato', e.target.value)}
            placeholder="Ex: C1614..."
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '0.875rem',
              backgroundColor: loading ? '#f9fafb' : 'white',
              cursor: loading ? 'not-allowed' : 'text'
            }}
            disabled={loading}
          />
        </div>

        {/* Status */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            📊 Status
          </label>
          <select
            value={filtros.status}
            onChange={(e) => handleInputChange('status', e.target.value as 'ativo' | 'inativo' | 'todos')}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '0.875rem',
              backgroundColor: loading ? '#f9fafb' : 'white',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
            disabled={loading}
          >
            <option value="todos">Todos os Status</option>
            <option value="ativo">Ativos</option>
            <option value="inativo">Inativos</option>
          </select>
        </div>

        {/* Renovado */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            🔄 Renovação
          </label>
          <select
            value={filtros.renovado}
            onChange={(e) => handleInputChange('renovado', e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '0.875rem',
              backgroundColor: loading ? '#f9fafb' : 'white',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
            disabled={loading}
          >
            <option value="todos">Todos</option>
            <option value="SIM">Renovados</option>
            <option value="NÃO">Não Renovados</option>
          </select>
        </div>

        {/* Data de Início */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            📅 Data Início (a partir de)
          </label>
          <input
            type="date"
            value={filtros.dataInicio}
            onChange={(e) => handleInputChange('dataInicio', e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '0.875rem',
              backgroundColor: loading ? '#f9fafb' : 'white',
              cursor: loading ? 'not-allowed' : 'text'
            }}
            disabled={loading}
          />
        </div>

        {/* Data de Fim */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            🏁 Data Fim (até)
          </label>
          <input
            type="date"
            value={filtros.dataFim}
            onChange={(e) => handleInputChange('dataFim', e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '0.875rem',
              backgroundColor: loading ? '#f9fafb' : 'white',
              cursor: loading ? 'not-allowed' : 'text'
            }}
            disabled={loading}
          />
        </div>

        {/* Valor Mínimo */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            💰 Valor Mínimo (R$)
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={filtros.valorMin || ''}
            onChange={(e) => handleInputChange('valorMin', e.target.value ? parseFloat(e.target.value) : undefined)}
            placeholder="R$ 0,00"
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '0.875rem',
              backgroundColor: loading ? '#f9fafb' : 'white',
              cursor: loading ? 'not-allowed' : 'text'
            }}
            disabled={loading}
          />
        </div>

        {/* Valor Máximo */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            💰 Valor Máximo (R$)
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={filtros.valorMax || ''}
            onChange={(e) => handleInputChange('valorMax', e.target.value ? parseFloat(e.target.value) : undefined)}
            placeholder="R$ 999.999,99"
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '0.875rem',
              backgroundColor: loading ? '#f9fafb' : 'white',
              cursor: loading ? 'not-allowed' : 'text'
            }}
            disabled={loading}
          />
        </div>
      </div>
    </div>
  );
};
