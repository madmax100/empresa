import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'funcionario', label: 'Funcionário (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'data_admissao', label: 'Data Admissão', inputType: 'date', valueType: 'date', required: true },
  { name: 'cargo', label: 'Cargo', inputType: 'text', valueType: 'string' },
  { name: 'salario', label: 'Salário', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'funcionario', label: 'Funcionário' },
  { key: 'data_admissao', label: 'Admissão' },
  { key: 'cargo', label: 'Cargo' }
];

const AdmissoesRhPage: React.FC = () => (
  <CadastroManager
    title="Admissões"
    description="Registre admissões e informações iniciais do colaborador."
    endpoint="/contas/admissoes-rh/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default AdmissoesRhPage;
