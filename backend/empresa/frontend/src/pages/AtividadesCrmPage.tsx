import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'oportunidade', label: 'Oportunidade (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'tipo', label: 'Tipo', inputType: 'text', valueType: 'string', required: true },
  { name: 'data_agendada', label: 'Data Agendada', inputType: 'date', valueType: 'date' },
  { name: 'concluida', label: 'Concluída', inputType: 'checkbox', valueType: 'boolean' },
  { name: 'data_conclusao', label: 'Data de Conclusão', inputType: 'date', valueType: 'date' },
  { name: 'usuario_id', label: 'Usuário (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'descricao', label: 'Descrição', inputType: 'textarea', valueType: 'string' }
];

const listColumns: ListColumn[] = [
  { key: 'tipo', label: 'Tipo' },
  { key: 'data_agendada', label: 'Agendada' },
  { key: 'concluida', label: 'Concluída' },
  { key: 'usuario_id', label: 'Usuário' }
];

const AtividadesCrmPage: React.FC = () => (
  <CadastroManager
    title="Atividades do CRM"
    description="Registre interações, reuniões e tarefas vinculadas às oportunidades."
    endpoint="/contas/atividades-crm/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default AtividadesCrmPage;
