import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'nome', label: 'Nome', inputType: 'text', valueType: 'string', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'nome', label: 'Categoria' }
];

const CategoriasProdutosPage: React.FC = () => (
  <CadastroManager
    title="Categorias de Produtos"
    description="Organize os produtos por categorias."
    endpoint="/contas/categorias_produtos/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default CategoriasProdutosPage;
