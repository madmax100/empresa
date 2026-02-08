import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'funcionario', label: 'Funcionário (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'data', label: 'Data', inputType: 'date', valueType: 'date', required: true },
  { name: 'entrada', label: 'Entrada', inputType: 'date', valueType: 'date' },
  { name: 'saida', label: 'Saída', inputType: 'date', valueType: 'date' },
  { name: 'horas_trabalhadas', label: 'Horas Trabalhadas', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'funcionario', label: 'Funcionário' },
  { key: 'data', label: 'Data' },
  { key: 'horas_trabalhadas', label: 'Horas' }
];

const RegistrosPontoPage: React.FC = () => (
  <CadastroManager
    title="Registros de Ponto"
    description="Controle entradas, saídas e horas trabalhadas por colaborador."
    endpoint="/contas/registros-ponto/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default RegistrosPontoPage;
