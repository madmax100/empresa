import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'codigo', label: 'Código', inputType: 'text', valueType: 'string', required: true },
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'tipo', label: 'Tipo', inputType: 'text', valueType: 'string' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'codigo', label: 'Código' },
  { key: 'nome', label: 'Nome' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'ativo', label: 'Ativo' }
];

const ImpostosFiscaisPage: React.FC = () => (
  <CadastroManager
    title="Impostos Fiscais"
    description="Cadastre impostos fiscais e seus tipos para controle tributário."
    endpoint="/contas/impostos-fiscais/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ImpostosFiscaisPage;
