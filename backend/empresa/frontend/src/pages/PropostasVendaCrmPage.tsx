import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'oportunidade', label: 'Oportunidade (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'numero', label: 'Número', inputType: 'text', valueType: 'string', required: true },
  { name: 'data_emissao', label: 'Data de Emissão', inputType: 'date', valueType: 'date' },
  { name: 'validade', label: 'Validade', inputType: 'date', valueType: 'date' },
  { name: 'valor_total', label: 'Valor Total', inputType: 'number', valueType: 'decimal', step: '0.01' },
  {
    name: 'status',
    label: 'Status',
    inputType: 'select',
    valueType: 'string',
    options: [
      { label: 'Rascunho', value: 'R' },
      { label: 'Enviada', value: 'E' },
      { label: 'Aceita', value: 'A' },
      { label: 'Negada', value: 'N' }
    ]
  },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'numero', label: 'Número' },
  { key: 'status', label: 'Status' },
  { key: 'valor_total', label: 'Valor Total' },
  { key: 'data_emissao', label: 'Emissão' }
];

const PropostasVendaCrmPage: React.FC = () => (
  <CadastroManager
    title="Propostas de Venda"
    description="Crie e acompanhe propostas comerciais vinculadas às oportunidades."
    endpoint="/contas/propostas-venda/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default PropostasVendaCrmPage;
