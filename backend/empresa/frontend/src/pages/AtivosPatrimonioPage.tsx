import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'codigo', label: 'Código', inputType: 'text', valueType: 'string', required: true },
  { name: 'descricao', label: 'Descrição', inputType: 'text', valueType: 'string', required: true },
  { name: 'categoria', label: 'Categoria', inputType: 'text', valueType: 'string' },
  { name: 'localizacao', label: 'Localização', inputType: 'text', valueType: 'string' },
  { name: 'data_aquisicao', label: 'Data Aquisição', inputType: 'date', valueType: 'date' },
  { name: 'valor_aquisicao', label: 'Valor Aquisição', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'vida_util_meses', label: 'Vida Útil (meses)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'valor_residual', label: 'Valor Residual', inputType: 'number', valueType: 'decimal', step: '0.01' },
  {
    name: 'status',
    label: 'Status',
    inputType: 'select',
    valueType: 'string',
    options: [
      { label: 'Ativo', value: 'A' },
      { label: 'Inativo', value: 'I' },
      { label: 'Baixado', value: 'B' }
    ]
  },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'codigo', label: 'Código' },
  { key: 'descricao', label: 'Descrição' },
  { key: 'categoria', label: 'Categoria' },
  { key: 'status', label: 'Status' }
];

const AtivosPatrimonioPage: React.FC = () => (
  <CadastroManager
    title="Ativos Patrimoniais"
    description="Cadastre bens patrimoniais e controle o ciclo de vida dos ativos."
    endpoint="/contas/ativos-patrimonio/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default AtivosPatrimonioPage;
