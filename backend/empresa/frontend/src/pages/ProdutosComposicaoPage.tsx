import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'componente', label: 'Componente (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'quantidade', label: 'Quantidade', inputType: 'number', valueType: 'decimal', step: '0.0001' }
];

const listColumns: ListColumn[] = [
  { key: 'produto', label: 'Produto' },
  { key: 'componente', label: 'Componente' },
  { key: 'quantidade', label: 'Quantidade' }
];

const ProdutosComposicaoPage: React.FC = () => (
  <CadastroManager
    title="Composição de Produtos"
    description="Monte kits e componentes (BOM)."
    endpoint="/contas/produtos-composicao/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ProdutosComposicaoPage;
