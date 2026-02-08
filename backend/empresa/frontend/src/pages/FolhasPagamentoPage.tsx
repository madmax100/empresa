import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'competencia', label: 'Competência', inputType: 'date', valueType: 'date', required: true },
  { name: 'data_fechamento', label: 'Data Fechamento', inputType: 'date', valueType: 'date' },
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
  { name: 'total_bruto', label: 'Total Bruto', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'total_descontos', label: 'Total Descontos', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'total_liquido', label: 'Total Líquido', inputType: 'number', valueType: 'decimal', step: '0.01' }
];

const listColumns: ListColumn[] = [
  { key: 'competencia', label: 'Competência' },
  { key: 'status', label: 'Status' },
  { key: 'total_liquido', label: 'Total Líquido' }
];

const FolhasPagamentoPage: React.FC = () => (
  <CadastroManager
    title="Folhas de Pagamento"
    description="Gerencie folhas por competência e acompanhe totais financeiros."
    endpoint="/contas/folhas-pagamento/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default FolhasPagamentoPage;
