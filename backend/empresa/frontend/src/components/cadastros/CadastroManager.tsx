import React, { useCallback, useEffect, useMemo, useState } from 'react';
import api from '../../services/api';

export type FieldValueType = 'string' | 'integer' | 'decimal' | 'boolean' | 'date';

export interface FieldOption {
  label: string;
  value: string;
}

export interface FieldConfig {
  name: string;
  label: string;
  inputType: 'text' | 'email' | 'number' | 'date' | 'checkbox' | 'textarea' | 'select' | 'tel';
  valueType?: FieldValueType;
  placeholder?: string;
  required?: boolean;
  step?: string;
  options?: FieldOption[];
}

export interface ListColumn {
  key: string;
  label: string;
}

interface CadastroManagerProps {
  title: string;
  description?: string;
  endpoint: string;
  fields: FieldConfig[];
  listColumns: ListColumn[];
}

const buildInitialValues = (fields: FieldConfig[]) =>
  fields.reduce<Record<string, string | boolean>>((acc, field) => {
    acc[field.name] = field.inputType === 'checkbox' ? false : '';
    return acc;
  }, {});

const parseValue = (field: FieldConfig, value: string | boolean) => {
  if (field.valueType === 'boolean') {
    return Boolean(value);
  }

  if (value === '') {
    return null;
  }

  if (field.valueType === 'integer') {
    const parsed = Number.parseInt(String(value), 10);
    return Number.isNaN(parsed) ? null : parsed;
  }

  if (field.valueType === 'decimal') {
    const parsed = Number.parseFloat(String(value));
    return Number.isNaN(parsed) ? null : parsed;
  }

  return value;
};

const resolveListData = (data: unknown) => {
  if (Array.isArray(data)) {
    return data;
  }

  if (data && typeof data === 'object' && 'results' in data && Array.isArray((data as { results: unknown[] }).results)) {
    return (data as { results: unknown[] }).results;
  }

  return [];
};

const CadastroManager: React.FC<CadastroManagerProps> = ({
  title,
  description,
  endpoint,
  fields,
  listColumns
}) => {
  const [records, setRecords] = useState<Record<string, any>[]>([]);
  const [loading, setLoading] = useState(false);
  const [formValues, setFormValues] = useState(buildInitialValues(fields));
  const [error, setError] = useState<string | null>(null);
  const [editId, setEditId] = useState<number | null>(null);
  const [search, setSearch] = useState('');

  const filteredRecords = useMemo(() => {
    if (!search.trim()) {
      return records;
    }

    const query = search.toLowerCase();
    return records.filter((record) =>
      listColumns.some((column) => String(record[column.key] ?? '').toLowerCase().includes(query))
    );
  }, [records, search, listColumns]);

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get(endpoint);
      setRecords(resolveListData(response.data));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar dados.');
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  const resetForm = () => {
    setFormValues(buildInitialValues(fields));
    setEditId(null);
  };

  const handleChange = (field: FieldConfig, value: string | boolean) => {
    setFormValues((prev) => ({
      ...prev,
      [field.name]: value
    }));
  };

  const handleEdit = (record: Record<string, any>) => {
    const nextValues = buildInitialValues(fields);

    fields.forEach((field) => {
      const rawValue = record[field.name];
      if (field.inputType === 'checkbox') {
        nextValues[field.name] = Boolean(rawValue);
      } else {
        nextValues[field.name] = rawValue ?? '';
      }
    });

    setFormValues(nextValues);
    setEditId(record.id as number);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    const payload = fields.reduce<Record<string, unknown>>((acc, field) => {
      acc[field.name] = parseValue(field, formValues[field.name]);
      return acc;
    }, {});

    try {
      if (editId) {
        await api.put(`${endpoint}${editId}/`, payload);
      } else {
        await api.post(endpoint, payload);
      }

      resetForm();
      fetchRecords();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar dados.');
    }
  };

  const handleDelete = async (recordId: number) => {
    setError(null);

    try {
      await api.delete(`${endpoint}${recordId}/`);
      fetchRecords();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao remover registro.');
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{
        backgroundColor: 'white',
        padding: '24px',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        marginBottom: '24px'
      }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', marginBottom: '8px' }}>{title}</h2>
        {description && <p style={{ color: '#6b7280', marginBottom: 0 }}>{description}</p>}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1.1fr) minmax(0, 1fr)',
        gap: '24px'
      }}>
        <form
          onSubmit={handleSubmit}
          style={{
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)'
          }}
        >
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '16px', color: '#1f2937' }}>
            {editId ? 'Editar cadastro' : 'Novo cadastro'}
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '16px'
          }}>
            {fields.map((field) => (
              <label key={field.name} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#374151' }}>{field.label}</span>
                {field.inputType === 'textarea' ? (
                  <textarea
                    value={String(formValues[field.name] ?? '')}
                    onChange={(event) => handleChange(field, event.target.value)}
                    placeholder={field.placeholder}
                    rows={3}
                    style={{
                      padding: '10px',
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb',
                      fontSize: '0.9rem'
                    }}
                  />
                ) : field.inputType === 'select' ? (
                  <select
                    value={String(formValues[field.name] ?? '')}
                    onChange={(event) => handleChange(field, event.target.value)}
                    style={{
                      padding: '10px',
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb',
                      fontSize: '0.9rem'
                    }}
                  >
                    <option value="">Selecione</option>
                    {field.options?.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : field.inputType === 'checkbox' ? (
                  <input
                    type="checkbox"
                    checked={Boolean(formValues[field.name])}
                    onChange={(event) => handleChange(field, event.target.checked)}
                    style={{ width: '20px', height: '20px' }}
                  />
                ) : (
                  <input
                    type={field.inputType}
                    value={String(formValues[field.name] ?? '')}
                    onChange={(event) => handleChange(field, event.target.value)}
                    placeholder={field.placeholder}
                    step={field.step}
                    style={{
                      padding: '10px',
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb',
                      fontSize: '0.9rem'
                    }}
                  />
                )}
              </label>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
            <button
              type="submit"
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: '#2563eb',
                color: 'white',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              {editId ? 'Atualizar' : 'Cadastrar'}
            </button>
            <button
              type="button"
              onClick={resetForm}
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                backgroundColor: 'white',
                color: '#374151',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Limpar
            </button>
          </div>

          {error && (
            <div style={{ marginTop: '16px', color: '#b91c1c', backgroundColor: '#fee2e2', padding: '12px', borderRadius: '8px' }}>
              {error}
            </div>
          )}
        </form>

        <div style={{
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#1f2937', marginBottom: '6px' }}>Registros</h3>
              <p style={{ margin: 0, color: '#6b7280', fontSize: '0.85rem' }}>
                {records.length} registros encontrados
              </p>
            </div>
            <button
              type="button"
              onClick={fetchRecords}
              disabled={loading}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                backgroundColor: 'white',
                color: '#374151',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Atualizar
            </button>
          </div>

          <input
            type="text"
            placeholder="Buscar por nome, documento ou cidade"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            style={{
              padding: '10px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              width: '100%',
              marginBottom: '16px'
            }}
          />

          {loading ? (
            <p style={{ color: '#6b7280' }}>Carregando...</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {listColumns.map((column) => (
                      <th
                        key={column.key}
                        style={{
                          textAlign: 'left',
                          padding: '10px',
                          borderBottom: '1px solid #e5e7eb',
                          fontSize: '0.8rem',
                          color: '#6b7280'
                        }}
                      >
                        {column.label}
                      </th>
                    ))}
                    <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((record) => (
                    <tr key={record.id}>
                      {listColumns.map((column) => (
                        <td key={column.key} style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                          {String(record[column.key] ?? '')}
                        </td>
                      ))}
                      <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button
                            type="button"
                            onClick={() => handleEdit(record)}
                            style={{
                              padding: '6px 10px',
                              borderRadius: '6px',
                              border: '1px solid #e5e7eb',
                              backgroundColor: 'white',
                              cursor: 'pointer',
                              fontSize: '0.8rem'
                            }}
                          >
                            Editar
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDelete(record.id)}
                            style={{
                              padding: '6px 10px',
                              borderRadius: '6px',
                              border: '1px solid #fee2e2',
                              backgroundColor: '#fee2e2',
                              color: '#b91c1c',
                              cursor: 'pointer',
                              fontSize: '0.8rem'
                            }}
                          >
                            Remover
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredRecords.length === 0 && (
                <p style={{ color: '#6b7280', marginTop: '16px' }}>Nenhum registro encontrado.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CadastroManager;
