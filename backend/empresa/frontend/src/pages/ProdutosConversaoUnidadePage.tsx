import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'unidade_origem', label: 'Unidade Origem', inputType: 'text', valueType: 'string' },
  { name: 'unidade_destino', label: 'Unidade Destino', inputType: 'text', valueType: 'string' },
  { name: 'fator', label: 'Fator', inputType: 'number', valueType: 'decimal', step: '0.0001' }
];

const listColumns: ListColumn[] = [
  { key: 'produto', label: 'Produto' },
  { key: 'unidade_origem', label: 'Origem' },
  { key: 'unidade_destino', label: 'Destino' },
  { key: 'fator', label: 'Fator' }
];

const ProdutosConversaoUnidadePage: React.FC = () => (
  <CadastroManager
    title="Conversões de Unidade"
    description="Cadastre fatores de conversão de unidades por produto."
    endpoint="/contas/produtos-conversao-unidade/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ProdutosConversaoUnidadePage;
