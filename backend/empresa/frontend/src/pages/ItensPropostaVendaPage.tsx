import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'proposta', label: 'Proposta (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'quantidade', label: 'Quantidade', inputType: 'number', valueType: 'decimal', step: '0.0001' },
  { name: 'valor_unitario', label: 'Valor Unitário', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'desconto', label: 'Desconto', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'valor_total', label: 'Valor Total', inputType: 'number', valueType: 'decimal', step: '0.01' }
];

const listColumns: ListColumn[] = [
  { key: 'proposta', label: 'Proposta' },
  { key: 'produto', label: 'Produto' },
  { key: 'quantidade', label: 'Quantidade' },
  { key: 'valor_total', label: 'Valor Total' }
];

const ItensPropostaVendaPage: React.FC = () => (
  <CadastroManager
    title="Itens da Proposta"
    description="Inclua itens, valores e descontos vinculados às propostas de venda."
    endpoint="/contas/itens-proposta-venda/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ItensPropostaVendaPage;
