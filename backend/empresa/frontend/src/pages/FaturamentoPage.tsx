// src/pages/FaturamentoPage.tsx

import { useState } from 'react';
import { FaturamentoDashboard } from '../components/dashboard/FaturamentoDashboard';

export function FaturamentoPage() {
  const [dateRange, setDateRange] = useState({
    from: new Date(new Date().getFullYear(), new Date().getMonth(), 1), // Primeiro dia do mês atual
    to: new Date() // Hoje
  });

  const handleDateChange = (field: 'from' | 'to', date: Date) => {
    setDateRange(prev => ({
      ...prev,
      [field]: date
    }));
  };

  const formatDateForInput = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#F1F5F9', 
      padding: '24px' 
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Cabeçalho com filtros */}
        <div style={{
          backgroundColor: '#FFFFFF',
          padding: '24px',
          borderRadius: '8px',
          border: '1px solid #E2E8F0',
          marginBottom: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <h1 style={{ 
            margin: '0 0 24px 0', 
            fontSize: '32px', 
            fontWeight: '700', 
            color: '#1E293B' 
          }}>
            Relatório de Faturamento
          </h1>
          
          <div style={{
            display: 'flex',
            gap: '16px',
            alignItems: 'end',
            flexWrap: 'wrap'
          }}>
            <div style={{ minWidth: '180px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '8px'
              }}>
                Data Início
              </label>
              <input
                type="date"
                value={formatDateForInput(dateRange.from)}
                onChange={(e) => handleDateChange('from', new Date(e.target.value))}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: '#FFFFFF',
                  color: '#374151'
                }}
              />
            </div>
            
            <div style={{ minWidth: '180px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '8px'
              }}>
                Data Fim
              </label>
              <input
                type="date"
                value={formatDateForInput(dateRange.to)}
                onChange={(e) => handleDateChange('to', new Date(e.target.value))}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: '#FFFFFF',
                  color: '#374151'
                }}
              />
            </div>

            <div style={{ 
              display: 'flex', 
              gap: '8px',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={() => setDateRange({
                  from: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
                  to: new Date()
                })}
                style={{
                  padding: '12px 16px',
                  backgroundColor: '#3B82F6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                Mês Atual
              </button>
              
              <button
                onClick={() => setDateRange({
                  from: new Date(new Date().getFullYear(), 0, 1),
                  to: new Date()
                })}
                style={{
                  padding: '12px 16px',
                  backgroundColor: '#10B981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                Ano Atual
              </button>

              <button
                onClick={() => setDateRange({
                  from: new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000),
                  to: new Date()
                })}
                style={{
                  padding: '12px 16px',
                  backgroundColor: '#F59E0B',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                Últimos 30 dias
              </button>
            </div>
          </div>

          <div style={{
            marginTop: '16px',
            padding: '12px',
            backgroundColor: '#EFF6FF',
            border: '1px solid #DBEAFE',
            borderRadius: '6px',
            fontSize: '14px',
            color: '#1E40AF'
          }}>
            <strong>Período selecionado:</strong> {dateRange.from.toLocaleDateString('pt-BR')} até {dateRange.to.toLocaleDateString('pt-BR')}
          </div>
        </div>

        {/* Dashboard */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '8px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          <FaturamentoDashboard dateRange={dateRange} />
        </div>
      </div>
    </div>
  );
}
