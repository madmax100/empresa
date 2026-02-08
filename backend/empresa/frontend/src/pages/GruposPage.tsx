import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Grupo' }
];

const GruposPage: React.FC = () => (
  <CadastroManager
    title="Grupos"
    description="Organize produtos em grupos comerciais."
    endpoint="/contas/grupos/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default GruposPage;
