import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'titulo', label: 'Título', inputType: 'text', valueType: 'string', required: true },
  { name: 'lead', label: 'Lead (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'cliente', label: 'Cliente (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'etapa', label: 'Etapa (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'valor_estimado', label: 'Valor Estimado', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'probabilidade', label: 'Probabilidade (%)', inputType: 'number', valueType: 'decimal', step: '0.01' },
  {
    name: 'status',
    label: 'Status',
    inputType: 'select',
    valueType: 'string',
    options: [
      { label: 'Aberta', value: 'A' },
      { label: 'Ganha', value: 'G' },
      { label: 'Perdida', value: 'P' }
    ]
  },
  { name: 'origem', label: 'Origem', inputType: 'text', valueType: 'string' },
  { name: 'responsavel_id', label: 'Responsável (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'data_fechamento', label: 'Data de Fechamento', inputType: 'date', valueType: 'date' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'titulo', label: 'Oportunidade' },
  { key: 'status', label: 'Status' },
  { key: 'valor_estimado', label: 'Valor' },
  { key: 'probabilidade', label: 'Prob.' }
];

const OportunidadesPage: React.FC = () => (
  <CadastroManager
    title="Oportunidades"
    description="Acompanhe oportunidades do funil e previsões de receita."
    endpoint="/contas/oportunidades/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default OportunidadesPage;
