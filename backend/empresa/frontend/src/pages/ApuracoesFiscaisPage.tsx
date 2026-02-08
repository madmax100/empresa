import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'data_inicio', label: 'Data Início', inputType: 'date', valueType: 'date', required: true },
  { name: 'data_fim', label: 'Data Fim', inputType: 'date', valueType: 'date', required: true },
  {
    name: 'status',
    label: 'Status',
    inputType: 'select',
    valueType: 'string',
    options: [
      { label: 'Aberta', value: 'A' },
      { label: 'Fechada', value: 'F' }
    ]
  },
  { name: 'total_debitos', label: 'Total Débitos', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'total_creditos', label: 'Total Créditos', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'saldo', label: 'Saldo', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'data_inicio', label: 'Início' },
  { key: 'data_fim', label: 'Fim' },
  { key: 'status', label: 'Status' },
  { key: 'saldo', label: 'Saldo' }
];

const ApuracoesFiscaisPage: React.FC = () => (
  <CadastroManager
    title="Apurações Fiscais"
    description="Gerencie períodos de apuração e saldos tributários."
    endpoint="/contas/apuracoes-fiscais/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ApuracoesFiscaisPage;
