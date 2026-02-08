import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'text', valueType: 'string' },
  { name: 'sku', label: 'SKU', inputType: 'text', valueType: 'string' },
  { name: 'ean', label: 'EAN', inputType: 'text', valueType: 'string' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'produto', label: 'Produto' },
  { key: 'descricao', label: 'Variação' },
  { key: 'sku', label: 'SKU' }
];

const ProdutosVariacoesPage: React.FC = () => (
  <CadastroManager
    title="Variações de Produto"
    description="Cadastre variações de produto com SKU/EAN."
    endpoint="/contas/produtos-variacoes/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ProdutosVariacoesPage;
