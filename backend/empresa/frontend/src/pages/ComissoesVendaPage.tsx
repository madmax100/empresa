import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'pedido', label: 'Pedido (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'vendedor', label: 'Vendedor (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'percentual', label: 'Percentual', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'valor', label: 'Valor', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'status', label: 'Status', inputType: 'text', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'pedido', label: 'Pedido' },
  { key: 'vendedor', label: 'Vendedor' },
  { key: 'percentual', label: 'Percentual' },
  { key: 'valor', label: 'Valor' }
];

const ComissoesVendaPage: React.FC = () => (
  <CadastroManager
    title="Comissões de Venda"
    description="Controle comissões por pedido e vendedor."
    endpoint="/contas/comissoes-venda/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ComissoesVendaPage;
