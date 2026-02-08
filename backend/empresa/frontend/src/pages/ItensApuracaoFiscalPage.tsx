import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'apuracao', label: 'Apuração (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'imposto', label: 'Imposto (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'valor_debito', label: 'Valor Débito', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'valor_credito', label: 'Valor Crédito', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'saldo', label: 'Saldo', inputType: 'number', valueType: 'decimal', step: '0.01' }
];

const listColumns: ListColumn[] = [
  { key: 'apuracao', label: 'Apuração' },
  { key: 'imposto', label: 'Imposto' },
  { key: 'valor_debito', label: 'Débito' },
  { key: 'valor_credito', label: 'Crédito' },
  { key: 'saldo', label: 'Saldo' }
];

const ItensApuracaoFiscalPage: React.FC = () => (
  <CadastroManager
    title="Itens de Apuração"
    description="Detalhe débitos e créditos por imposto em cada apuração."
    endpoint="/contas/itens-apuracao-fiscal/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ItensApuracaoFiscalPage;
