import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'pedido', label: 'Pedido (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'produto', label: 'Produto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'quantidade', label: 'Quantidade', inputType: 'number', valueType: 'decimal', step: '0.0001' },
  { name: 'valor_unitario', label: 'Valor Unitário', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'desconto', label: 'Desconto', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'valor_total', label: 'Valor Total', inputType: 'number', valueType: 'decimal', step: '0.01' }
];

const listColumns: ListColumn[] = [
  { key: 'pedido', label: 'Pedido' },
  { key: 'produto', label: 'Produto' },
  { key: 'quantidade', label: 'Quantidade' },
  { key: 'valor_total', label: 'Total' }
];

const ItensPedidoVendaPage: React.FC = () => (
  <CadastroManager
    title="Itens do Pedido"
    description="Gerencie itens e valores associados aos pedidos de venda."
    endpoint="/contas/itens-pedido-venda/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ItensPedidoVendaPage;
