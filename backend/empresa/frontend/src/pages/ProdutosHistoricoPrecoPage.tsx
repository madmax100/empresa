import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'data_inicio', label: 'Data Início', inputType: 'date', valueType: 'date' },
  { name: 'data_fim', label: 'Data Fim', inputType: 'date', valueType: 'date' },
  { name: 'preco', label: 'Preço', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'produto', label: 'Produto' },
  { key: 'preco', label: 'Preço' },
  { key: 'data_inicio', label: 'Início' }
];

const ProdutosHistoricoPrecoPage: React.FC = () => (
  <CadastroManager
    title="Histórico de Preços"
    description="Controle alterações de preço por produto."
    endpoint="/contas/produtos-historico-preco/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ProdutosHistoricoPrecoPage;
