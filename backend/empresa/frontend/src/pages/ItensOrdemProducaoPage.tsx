import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'ordem', label: 'Ordem (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'produto_insumo', label: 'Produto Insumo (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'quantidade', label: 'Quantidade', inputType: 'number', valueType: 'decimal', step: '0.0001' }
];

const listColumns: ListColumn[] = [
  { key: 'ordem', label: 'Ordem' },
  { key: 'produto_insumo', label: 'Insumo' },
  { key: 'quantidade', label: 'Quantidade' }
];

const ItensOrdemProducaoPage: React.FC = () => (
  <CadastroManager
    title="Itens da Ordem"
    description="Cadastre os insumos necessários para cada ordem de produção."
    endpoint="/contas/itens-ordem-producao/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ItensOrdemProducaoPage;
