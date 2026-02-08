import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'local', label: 'Local (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'custo', label: 'Custo', inputType: 'number', valueType: 'decimal', step: '0.01' }
];

const listColumns: ListColumn[] = [
  { key: 'produto', label: 'Produto' },
  { key: 'local', label: 'Local' },
  { key: 'custo', label: 'Custo' }
];

const ProdutosCustoLocalPage: React.FC = () => (
  <CadastroManager
    title="Custo por Local"
    description="Cadastre custos por produto e local de estoque."
    endpoint="/contas/produtos-custo-local/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ProdutosCustoLocalPage;
