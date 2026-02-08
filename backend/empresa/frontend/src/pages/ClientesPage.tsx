import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  {
    name: 'tipo_pessoa',
    label: 'Tipo de Pessoa',
    inputType: 'select',
    valueType: 'string',
    options: [
      { label: 'Física', value: 'F' },
      { label: 'Jurídica', value: 'J' }
    ]
  },
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'cpf_cnpj', label: 'CPF/CNPJ', inputType: 'text', valueType: 'string' },
  { name: 'rg_ie', label: 'RG/IE', inputType: 'text', valueType: 'string' },
  { name: 'data_nascimento', label: 'Data de Nascimento', inputType: 'date', valueType: 'date' },
  { name: 'endereco', label: 'Endereço', inputType: 'text', valueType: 'string' },
  { name: 'numero', label: 'Número', inputType: 'text', valueType: 'string' },
  { name: 'complemento', label: 'Complemento', inputType: 'text', valueType: 'string' },
  { name: 'bairro', label: 'Bairro', inputType: 'text', valueType: 'string' },
  { name: 'cidade', label: 'Cidade', inputType: 'text', valueType: 'string' },
  { name: 'estado', label: 'Estado', inputType: 'text', valueType: 'string' },
  { name: 'cep', label: 'CEP', inputType: 'text', valueType: 'string' },
  { name: 'telefone', label: 'Telefone', inputType: 'tel', valueType: 'string' },
  { name: 'email', label: 'Email', inputType: 'email', valueType: 'string' },
  { name: 'limite_credito', label: 'Limite de Crédito', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'contato', label: 'Contato', inputType: 'text', valueType: 'string' },
  { name: 'especificacao', label: 'Especificação', inputType: 'textarea', valueType: 'string' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Nome' },
  { key: 'cpf_cnpj', label: 'CPF/CNPJ' },
  { key: 'cidade', label: 'Cidade' },
  { key: 'telefone', label: 'Telefone' }
];

const ClientesPage: React.FC = () => (
  <CadastroManager
    title="Clientes"
    description="Gerencie o cadastro de clientes e informações de contato."
    endpoint="/contas/clientes/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ClientesPage;
