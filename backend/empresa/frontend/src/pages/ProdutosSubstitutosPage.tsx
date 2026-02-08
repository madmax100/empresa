import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'substituto', label: 'Substituto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'produto', label: 'Produto' },
  { key: 'substituto', label: 'Substituto' }
];

const ProdutosSubstitutosPage: React.FC = () => (
  <CadastroManager
    title="Substitutos de Produto"
    description="Cadastre substitutos e alternativas de produto."
    endpoint="/contas/produtos-substitutos/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ProdutosSubstitutosPage;
