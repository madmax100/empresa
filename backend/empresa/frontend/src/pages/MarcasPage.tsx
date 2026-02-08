import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Marca' }
];

const MarcasPage: React.FC = () => (
  <CadastroManager
    title="Marcas"
    description="Cadastre marcas associadas aos produtos."
    endpoint="/contas/marcas/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default MarcasPage;
