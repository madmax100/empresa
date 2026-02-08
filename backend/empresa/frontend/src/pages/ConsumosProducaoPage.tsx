import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'ordem', label: 'Ordem (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'local_id', label: 'Local (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'quantidade', label: 'Quantidade', inputType: 'number', valueType: 'decimal', step: '0.0001' },
  { name: 'data_consumo', label: 'Data Consumo', inputType: 'date', valueType: 'date' }
];

const listColumns: ListColumn[] = [
  { key: 'ordem', label: 'Ordem' },
  { key: 'produto', label: 'Produto' },
  { key: 'quantidade', label: 'Quantidade' },
  { key: 'data_consumo', label: 'Data Consumo' }
];

const ConsumosProducaoPage: React.FC = () => (
  <CadastroManager
    title="Consumos de Produção"
    description="Registre o consumo de insumos utilizado nas ordens de produção."
    endpoint="/contas/consumos-producao/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ConsumosProducaoPage;
