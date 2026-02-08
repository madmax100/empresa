import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'funcionario', label: 'Funcionário (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'beneficio', label: 'Benefício (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'data_inicio', label: 'Data Início', inputType: 'date', valueType: 'date' },
  { name: 'data_fim', label: 'Data Fim', inputType: 'date', valueType: 'date' },
  { name: 'valor', label: 'Valor', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'funcionario', label: 'Funcionário' },
  { key: 'beneficio', label: 'Benefício' },
  { key: 'valor', label: 'Valor' },
  { key: 'ativo', label: 'Ativo' }
];

const VinculosBeneficiosRhPage: React.FC = () => (
  <CadastroManager
    title="Vínculos de Benefícios"
    description="Vincule benefícios aos colaboradores e controle vigências."
    endpoint="/contas/vinculos-beneficios-rh/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default VinculosBeneficiosRhPage;
