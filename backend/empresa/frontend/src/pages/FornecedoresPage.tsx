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
  { name: 'endereco', label: 'Endereço', inputType: 'text', valueType: 'string' },
  { name: 'numero', label: 'Número', inputType: 'text', valueType: 'string' },
  { name: 'complemento', label: 'Complemento', inputType: 'text', valueType: 'string' },
  { name: 'bairro', label: 'Bairro', inputType: 'text', valueType: 'string' },
  { name: 'cidade', label: 'Cidade', inputType: 'text', valueType: 'string' },
  { name: 'estado', label: 'Estado', inputType: 'text', valueType: 'string' },
  { name: 'cep', label: 'CEP', inputType: 'text', valueType: 'string' },
  { name: 'telefone', label: 'Telefone', inputType: 'tel', valueType: 'string' },
  { name: 'email', label: 'Email', inputType: 'email', valueType: 'string' },
  { name: 'contato_nome', label: 'Contato', inputType: 'text', valueType: 'string' },
  { name: 'contato_telefone', label: 'Telefone do Contato', inputType: 'tel', valueType: 'string' },
  { name: 'tipo', label: 'Tipo', inputType: 'text', valueType: 'string' },
  { name: 'especificacao', label: 'Especificação', inputType: 'textarea', valueType: 'string' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Nome' },
  { key: 'cpf_cnpj', label: 'CPF/CNPJ' },
  { key: 'cidade', label: 'Cidade' },
  { key: 'telefone', label: 'Telefone' }
];

const FornecedoresPage: React.FC = () => (
  <CadastroManager
    title="Fornecedores"
    description="Cadastre fornecedores e mantenha dados de contato e documentos atualizados."
    endpoint="/contas/fornecedores/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default FornecedoresPage;
