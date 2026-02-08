import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'folha', label: 'Folha (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'funcionario', label: 'Funcionário (ID)', inputType: 'number', valueType: 'integer', step: '1', required: true },
  { name: 'salario_base', label: 'Salário Base', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'horas_extras', label: 'Horas Extras', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'descontos', label: 'Descontos', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'beneficios', label: 'Benefícios', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'valor_liquido', label: 'Valor Líquido', inputType: 'number', valueType: 'decimal', step: '0.01' }
];

const listColumns: ListColumn[] = [
  { key: 'folha', label: 'Folha' },
  { key: 'funcionario', label: 'Funcionário' },
  { key: 'valor_liquido', label: 'Valor Líquido' }
];

const ItensFolhaPagamentoPage: React.FC = () => (
  <CadastroManager
    title="Itens da Folha"
    description="Detalhe salários, descontos e benefícios por colaborador."
    endpoint="/contas/itens-folha-pagamento/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default ItensFolhaPagamentoPage;
