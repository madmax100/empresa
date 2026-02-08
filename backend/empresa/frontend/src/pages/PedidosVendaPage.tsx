import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'numero_pedido', label: 'Número do Pedido', inputType: 'text', valueType: 'string', required: true },
  { name: 'cliente', label: 'Cliente (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'vendedor', label: 'Vendedor (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'data_emissao', label: 'Data Emissão', inputType: 'date', valueType: 'date' },
  { name: 'status', label: 'Status', inputType: 'text', valueType: 'string' },
  { name: 'valor_total', label: 'Valor Total', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'frete', label: 'Frete', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'desconto', label: 'Desconto', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'numero_pedido', label: 'Pedido' },
  { key: 'cliente', label: 'Cliente' },
  { key: 'valor_total', label: 'Total' },
  { key: 'status', label: 'Status' }
];

const PedidosVendaPage: React.FC = () => (
  <CadastroManager
    title="Pedidos de Venda"
    description="Cadastre pedidos e acompanhe o status do faturamento."
    endpoint="/contas/pedidos-venda/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default PedidosVendaPage;
