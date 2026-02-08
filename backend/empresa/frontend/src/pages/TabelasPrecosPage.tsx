import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'textarea', valueType: 'string' },
  { name: 'data_inicio', label: 'Data Início', inputType: 'date', valueType: 'date' },
  { name: 'data_fim', label: 'Data Fim', inputType: 'date', valueType: 'date' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Tabela' },
  { key: 'data_inicio', label: 'Início' },
  { key: 'data_fim', label: 'Fim' }
];

const TabelasPrecosPage: React.FC = () => (
  <CadastroManager
    title="Tabelas de Preço"
    description="Crie tabelas de preço para clientes e períodos específicos."
    endpoint="/contas/tabelas-precos/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default TabelasPrecosPage;
