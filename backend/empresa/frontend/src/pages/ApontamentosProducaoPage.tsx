import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'ordem', label: 'Ordem (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'local_id', label: 'Local (ID)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'quantidade', label: 'Quantidade', inputType: 'number', valueType: 'decimal', step: '0.0001' },
  { name: 'data_apontamento', label: 'Data Apontamento', inputType: 'date', valueType: 'date' }
];

const listColumns: ListColumn[] = [
  { key: 'ordem', label: 'Ordem' },
  { key: 'quantidade', label: 'Quantidade' },
  { key: 'data_apontamento', label: 'Data Apontamento' }
];

const ApontamentosProducaoPage: React.FC = () => (
  <CadastroManager
    title="Apontamentos de Produção"
    description="Registre as entradas de produção e apontamentos do processo." 
    endpoint="/contas/apontamentos-producao/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ApontamentosProducaoPage;
