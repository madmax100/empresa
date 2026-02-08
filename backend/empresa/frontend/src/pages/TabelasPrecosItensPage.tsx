import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'tabela', label: 'Tabela (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'preco', label: 'Preço', inputType: 'number', valueType: 'decimal', step: '0.01' }
];

const listColumns: ListColumn[] = [
  { key: 'tabela', label: 'Tabela' },
  { key: 'produto', label: 'Produto' },
  { key: 'preco', label: 'Preço' }
];

const TabelasPrecosItensPage: React.FC = () => (
  <CadastroManager
    title="Itens de Tabela de Preço"
    description="Associe produtos e preços às tabelas comerciais."
    endpoint="/contas/tabelas-precos-itens/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default TabelasPrecosItensPage;
