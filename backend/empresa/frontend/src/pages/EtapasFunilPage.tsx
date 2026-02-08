import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'ordem', label: 'Ordem', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'ativo', label: 'Ativa', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Etapa' },
  { key: 'ordem', label: 'Ordem' },
  { key: 'ativo', label: 'Ativa' }
];

const EtapasFunilPage: React.FC = () => (
  <CadastroManager
    title="Etapas do Funil"
    description="Defina as etapas do funil comercial e sua ordem de prioridade."
    endpoint="/contas/etapas-funil/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default EtapasFunilPage;
