import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'ativo', label: 'Ativo (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'tipo', label: 'Tipo', inputType: 'text', valueType: 'string', required: true },
  { name: 'data_abertura', label: 'Data Abertura', inputType: 'date', valueType: 'date' },
  { name: 'data_fechamento', label: 'Data Fechamento', inputType: 'date', valueType: 'date' },
  { name: 'responsavel_id', label: 'Responsável (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'custo_previsto', label: 'Custo Previsto', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'custo_real', label: 'Custo Real', inputType: 'number', valueType: 'decimal', step: '0.01' },
  {
    name: 'status',
    label: 'Status',
    inputType: 'select',
    valueType: 'string',
    options: [
      { label: 'Aberta', value: 'A' },
      { label: 'Em execução', value: 'E' },
      { label: 'Finalizada', value: 'F' },
      { label: 'Cancelada', value: 'C' }
    ]
  },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'ativo', label: 'Ativo' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'status', label: 'Status' },
  { key: 'custo_previsto', label: 'Custo Previsto' }
];

const ManutencoesAtivosPage: React.FC = () => (
  <CadastroManager
    title="Manutenções de Ativos"
    description="Registre manutenções preventivas e corretivas nos ativos patrimoniais."
    endpoint="/contas/manutencoes-ativos/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ManutencoesAtivosPage;
