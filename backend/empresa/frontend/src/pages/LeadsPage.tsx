import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'email', label: 'Email', inputType: 'email', valueType: 'string' },
  { name: 'telefone', label: 'Telefone', inputType: 'tel', valueType: 'string' },
  { name: 'origem', label: 'Origem', inputType: 'text', valueType: 'string' },
  {
    name: 'status',
    label: 'Status',
    inputType: 'select',
    valueType: 'string',
    options: [
      { label: 'Novo', value: 'N' },
      { label: 'Contactado', value: 'C' },
      { label: 'Qualificado', value: 'Q' },
      { label: 'Descartado', value: 'D' }
    ]
  },
  { name: 'responsavel_id', label: 'Responsável (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Lead' },
  { key: 'email', label: 'Email' },
  { key: 'telefone', label: 'Telefone' },
  { key: 'status', label: 'Status' }
];

const LeadsPage: React.FC = () => (
  <CadastroManager
    title="Leads"
    description="Registre contatos iniciais e acompanhe o status de qualificação."
    endpoint="/contas/leads/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default LeadsPage;
