import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'textarea', valueType: 'string' },
  { name: 'valor_padrao', label: 'Valor Padrão', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Benefício' },
  { key: 'valor_padrao', label: 'Valor Padrão' },
  { key: 'ativo', label: 'Ativo' }
];

const BeneficiosRhPage: React.FC = () => (
  <CadastroManager
    title="Benefícios"
    description="Cadastre benefícios oferecidos aos colaboradores."
    endpoint="/contas/beneficios-rh/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default BeneficiosRhPage;
