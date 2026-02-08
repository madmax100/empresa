import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'razao_social', label: 'Razão Social', inputType: 'text', valueType: 'string', required: true },
  { name: 'nome_fantasia', label: 'Nome Fantasia', inputType: 'text', valueType: 'string' },
  { name: 'cnpj', label: 'CNPJ', inputType: 'text', valueType: 'string', required: true },
  { name: 'ie', label: 'IE', inputType: 'text', valueType: 'string' },
  { name: 'endereco', label: 'Endereço', inputType: 'text', valueType: 'string' },
  { name: 'numero', label: 'Número', inputType: 'text', valueType: 'string' },
  { name: 'complemento', label: 'Complemento', inputType: 'text', valueType: 'string' },
  { name: 'bairro', label: 'Bairro', inputType: 'text', valueType: 'string' },
  { name: 'cidade', label: 'Cidade', inputType: 'text', valueType: 'string' },
  { name: 'estado', label: 'Estado', inputType: 'text', valueType: 'string' },
  { name: 'cep', label: 'CEP', inputType: 'text', valueType: 'string' },
  { name: 'telefone', label: 'Telefone', inputType: 'tel', valueType: 'string' },
  { name: 'email', label: 'Email', inputType: 'email', valueType: 'string' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'razao_social', label: 'Razão Social' },
  { key: 'cnpj', label: 'CNPJ' },
  { key: 'cidade', label: 'Cidade' },
  { key: 'telefone', label: 'Telefone' }
];

const EmpresasPage: React.FC = () => (
  <CadastroManager
    title="Empresas"
    description="Cadastre as empresas e mantenha informações fiscais atualizadas."
    endpoint="/contas/empresas/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default EmpresasPage;
