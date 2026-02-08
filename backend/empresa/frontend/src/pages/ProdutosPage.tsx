import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'codigo', label: 'Código', inputType: 'text', valueType: 'string' },
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'textarea', valueType: 'string' },
  { name: 'categoria', label: 'Categoria (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'marca', label: 'Marca (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'grupo', label: 'Grupo (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'unidade', label: 'Unidade', inputType: 'text', valueType: 'string' },
  { name: 'preco', label: 'Preço', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'disponivel_locacao', label: 'Disponível para Locação', inputType: 'checkbox', valueType: 'boolean' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'codigo', label: 'Código' },
  { key: 'nome', label: 'Produto' },
  { key: 'categoria', label: 'Categoria' },
  { key: 'preco', label: 'Preço' }
];

const ProdutosPage: React.FC = () => (
  <CadastroManager
    title="Produtos"
    description="Cadastre produtos e controle disponibilidade para locação."
    endpoint="/contas/produtos/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ProdutosPage;
