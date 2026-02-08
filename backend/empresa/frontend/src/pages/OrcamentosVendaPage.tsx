import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'numero', label: 'Número', inputType: 'text', valueType: 'string', required: true },
  { name: 'cliente', label: 'Cliente (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'data_emissao', label: 'Data Emissão', inputType: 'date', valueType: 'date' },
  { name: 'validade', label: 'Validade', inputType: 'date', valueType: 'date' },
  { name: 'valor_total', label: 'Valor Total', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'status', label: 'Status', inputType: 'text', valueType: 'string' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'numero', label: 'Número' },
  { key: 'cliente', label: 'Cliente' },
  { key: 'valor_total', label: 'Valor Total' },
  { key: 'status', label: 'Status' }
];

const OrcamentosVendaPage: React.FC = () => (
  <CadastroManager
    title="Orçamentos de Venda"
    description="Cadastre orçamentos e propostas comerciais."
    endpoint="/contas/orcamentos-venda/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default OrcamentosVendaPage;
