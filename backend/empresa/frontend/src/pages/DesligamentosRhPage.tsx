import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'funcionario', label: 'Funcionário (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'data_desligamento', label: 'Data Desligamento', inputType: 'date', valueType: 'date', required: true },
  { name: 'motivo', label: 'Motivo', inputType: 'text', valueType: 'string' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'funcionario', label: 'Funcionário' },
  { key: 'data_desligamento', label: 'Desligamento' },
  { key: 'motivo', label: 'Motivo' }
];

const DesligamentosRhPage: React.FC = () => (
  <CadastroManager
    title="Desligamentos"
    description="Registre desligamentos e motivos de saída."
    endpoint="/contas/desligamentos-rh/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default DesligamentosRhPage;
