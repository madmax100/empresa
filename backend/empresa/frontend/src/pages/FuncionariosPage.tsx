import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'cpf', label: 'CPF', inputType: 'text', valueType: 'string' },
  { name: 'rg', label: 'RG', inputType: 'text', valueType: 'string' },
  { name: 'data_nascimento', label: 'Data de Nascimento', inputType: 'date', valueType: 'date' },
  { name: 'data_admissao', label: 'Data de Admissão', inputType: 'date', valueType: 'date' },
  { name: 'data_demissao', label: 'Data de Demissão', inputType: 'date', valueType: 'date' },
  { name: 'cargo', label: 'Cargo', inputType: 'text', valueType: 'string' },
  { name: 'salario_base', label: 'Salário Base', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'endereco', label: 'Endereço', inputType: 'text', valueType: 'string' },
  { name: 'numero', label: 'Número', inputType: 'text', valueType: 'string' },
  { name: 'complemento', label: 'Complemento', inputType: 'text', valueType: 'string' },
  { name: 'bairro', label: 'Bairro', inputType: 'text', valueType: 'string' },
  { name: 'cidade', label: 'Cidade', inputType: 'text', valueType: 'string' },
  { name: 'estado', label: 'Estado', inputType: 'text', valueType: 'string' },
  { name: 'cep', label: 'CEP', inputType: 'text', valueType: 'string' },
  { name: 'telefone', label: 'Telefone', inputType: 'tel', valueType: 'string' },
  { name: 'email', label: 'Email', inputType: 'email', valueType: 'string' },
  { name: 'banco', label: 'Banco', inputType: 'text', valueType: 'string' },
  { name: 'agencia', label: 'Agência', inputType: 'text', valueType: 'string' },
  { name: 'conta', label: 'Conta', inputType: 'text', valueType: 'string' },
  { name: 'pix', label: 'PIX', inputType: 'text', valueType: 'string' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Nome' },
  { key: 'cargo', label: 'Cargo' },
  { key: 'cidade', label: 'Cidade' },
  { key: 'telefone', label: 'Telefone' }
];

const FuncionariosPage: React.FC = () => (
  <CadastroManager
    title="Funcionários"
    description="Gerencie dados dos colaboradores e informações bancárias." 
    endpoint="/contas/funcionarios/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default FuncionariosPage;
