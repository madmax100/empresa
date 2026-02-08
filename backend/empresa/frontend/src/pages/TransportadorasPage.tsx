import React from 'react';
import CadastroManager, { FieldConfig, ListColumn } from '../components/cadastros/CadastroManager';

const fields: FieldConfig[] = [
  { name: 'razao_social', label: 'Razão Social', inputType: 'text', valueType: 'string', required: true },
  { name: 'nome', label: 'Nome Fantasia', inputType: 'text', valueType: 'string' },
  { name: 'cnpj', label: 'CNPJ', inputType: 'text', valueType: 'string' },
  { name: 'ie', label: 'IE', inputType: 'text', valueType: 'string' },
  { name: 'endereco', label: 'Endereço', inputType: 'text', valueType: 'string' },
  { name: 'numero', label: 'Número', inputType: 'text', valueType: 'string' },
  { name: 'complemento', label: 'Complemento', inputType: 'text', valueType: 'string' },
  { name: 'bairro', label: 'Bairro', inputType: 'text', valueType: 'string' },
  { name: 'cidade', label: 'Cidade', inputType: 'text', valueType: 'string' },
  { name: 'estado', label: 'Estado', inputType: 'text', valueType: 'string' },
  { name: 'cep', label: 'CEP', inputType: 'text', valueType: 'string' },
  { name: 'fone', label: 'Telefone', inputType: 'tel', valueType: 'string' },
  { name: 'celular', label: 'Celular', inputType: 'tel', valueType: 'string' },
  { name: 'email', label: 'Email', inputType: 'email', valueType: 'string' },
  { name: 'contato_principal', label: 'Contato Principal', inputType: 'text', valueType: 'string' },
  { name: 'site_rastreamento', label: 'Site de Rastreamento', inputType: 'text', valueType: 'string' },
  { name: 'formato_codigo_rastreio', label: 'Formato do Código', inputType: 'text', valueType: 'string' },
  { name: 'prazo_medio_entrega', label: 'Prazo Médio (dias)', inputType: 'number', valueType: 'integer', step: '1' },
  { name: 'valor_minimo_frete', label: 'Valor Mínimo de Frete', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'percentual_seguro', label: 'Percentual de Seguro', inputType: 'number', valueType: 'decimal', step: '0.01' },
  { name: 'observacoes', label: 'Observações', inputType: 'textarea', valueType: 'string' },
  { name: 'contato', label: 'Contato', inputType: 'text', valueType: 'string' },
  { name: 'ativo', label: 'Ativo', inputType: 'checkbox', valueType: 'boolean' }
];

const listColumns: ListColumn[] = [
  { key: 'razao_social', label: 'Razão Social' },
  { key: 'cnpj', label: 'CNPJ' },
  { key: 'cidade', label: 'Cidade' },
  { key: 'fone', label: 'Telefone' }
];

const TransportadorasPage: React.FC = () => (
  <CadastroManager
    title="Transportadoras"
    description="Cadastre transportadoras e controle informações de frete."
    endpoint="/contas/transportadoras/"
    fields={fields}
    listColumns={listColumns}
  />
);

export default TransportadorasPage;
