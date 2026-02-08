import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'ncm', label: 'NCM', inputType: 'text', valueType: 'string' },
  { name: 'cfop', label: 'CFOP', inputType: 'text', valueType: 'string' },
  { name: 'cst', label: 'CST', inputType: 'text', valueType: 'string' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'produto', label: 'Produto' },
  { key: 'ncm', label: 'NCM' },
  { key: 'cfop', label: 'CFOP' }
];

const ProdutosFiscalPage: React.FC = () => (
  <CadastroManager
    title="Fiscal por Produto"
    description="Cadastre dados fiscais vinculados aos produtos."
    endpoint="/contas/produtos-fiscal/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ProdutosFiscalPage;
