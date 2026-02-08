import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'textarea', valueType: 'string' },
  { name: 'percentual', label: 'Percentual', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Política' },
  { key: 'percentual', label: 'Percentual' },
  { key: 'ativo', label: 'Ativo' }
];

const PoliticasDescontoPage: React.FC = () => (
  <CadastroManager
    title="Políticas de Desconto"
    description="Defina regras e percentuais de desconto."
    endpoint="/contas/politicas-desconto/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default PoliticasDescontoPage;
