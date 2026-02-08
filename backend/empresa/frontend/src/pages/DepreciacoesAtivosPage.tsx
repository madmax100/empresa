import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'ativo', label: 'Ativo (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'competencia', label: 'Competência', inputType: 'date', valueType: 'date', required: true },
  { name: 'valor_depreciado', label: 'Valor Depreciado', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'valor_acumulado', label: 'Valor Acumulado', inputType: 'number', valueType: 'decimal', step: '0.01' }
];

const listColumns: ListColumn[] = [
  { key: 'ativo', label: 'Ativo' },
  { key: 'competencia', label: 'Competência' },
  { key: 'valor_depreciado', label: 'Depreciado' },
  { key: 'valor_acumulado', label: 'Acumulado' }
];

const DepreciacoesAtivosPage: React.FC = () => (
  <CadastroManager
    title="Depreciações de Ativos"
    description="Controle a depreciação mensal dos ativos e valores acumulados."
    endpoint="/contas/depreciacoes-ativos/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default DepreciacoesAtivosPage;
