import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'numero_ordem', label: 'Número da Ordem', inputType: 'text', valueType: 'string', required: true },
  { name: 'produto_final', label: 'Produto Final (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'local_id', label: 'Local (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'quantidade_planejada', label: 'Quantidade Planejada', inputType: 'number', valueType: 'decimal', step: '0.0001' },
  { name: 'quantidade_produzida', label: 'Quantidade Produzida', inputType: 'number', valueType: 'decimal', step: '0.0001' },
  {
    name: 'status',
    label: 'Status',
    inputType: 'select',
    valueType: 'string',
    options: [
      { label: 'Rascunho', value: 'R' },
      { label: 'Aprovada', value: 'A' },
      { label: 'Em produção', value: 'E' },
      { label: 'Finalizada', value: 'F' },
      { label: 'Cancelada', value: 'X' }
    ]
  },
  { name: 'data_inicio', label: 'Data Início', inputType: 'date', valueType: 'date' },
  { name: 'data_fim', label: 'Data Fim', inputType: 'date', valueType: 'date' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'numero_ordem', label: 'Ordem' },
  { key: 'produto_final', label: 'Produto Final' },
  { key: 'status', label: 'Status' },
  { key: 'quantidade_planejada', label: 'Qtd. Planejada' }
];

const OrdensProducaoPage: React.FC = () => (
  <CadastroManager
    title="Ordens de Produção"
    description="Gerencie ordens de produção, quantidades e status do processo produtivo."
    endpoint="/contas/ordens-producao/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default OrdensProducaoPage;
