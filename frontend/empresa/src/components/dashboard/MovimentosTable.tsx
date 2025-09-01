import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Check, X } from "lucide-react";
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { FinancialTable } from './FinancialTable';
import { Movimento } from '@/types/dashboardNovo';

interface MovimentosTableProps {
  movimentos: Movimento[];
  loading?: boolean;
  onStatusChange?: (id: number, novoStatus: MovimentoStatus) => Promise<void>;
  onEdit?: (movimento: Movimento) => void;
  onDelete?: (id: number) => Promise<void>;
  className?: string;
}

export const MovimentosTable: React.FC<MovimentosTableProps> = ({
  movimentos,
  loading = false,
  onStatusChange,
  onEdit,
  onDelete,
  className = ''
}) => {
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const getStatusColor = (realizado: boolean): string => {
    switch (realizado) {
      case true:
        return 'bg-green-50 text-green-600';
      case false:
        return 'bg-red-50 text-red-600';
      default:
        return 'bg-gray-50 text-gray-600';
    }
  };

  const getStatusLabel = (realizado: boolean): string => {
    switch (realizado) {
      case true:
        return 'Realizado';
      case false:
        return 'Previsto';
      default:
        return realizado ? 'Realizado' : 'Previsto';
    }
  };

  const handleStatusChange = async (movimento: Movimento, novoStatus: MovimentoStatus) => {
    if (!onStatusChange || updatingId === movimento.id) return;

    try {
      setUpdatingId(movimento.id);
      await onStatusChange(movimento.id, novoStatus);
    } finally {
      setUpdatingId(null);
    }
  };

  const columns = [
    {
      key: 'data',
      title: 'Data',
      sortable: true,
      render: (value: string) => format(new Date(value), 'dd/MM/yyyy', { locale: ptBR })
    },
    {
      key: 'tipo',
      title: 'Tipo',
      render: (value: 'entrada' | 'saida') => (
        <span className={value === 'entrada' ? 'text-green-600' : 'text-red-600'}>
          {value === 'entrada' ? 'Entrada' : 'Saída'}
        </span>
      )
    },
    {
      key: 'descricao',
      title: 'Descrição'
    },
    {
      key: 'valor',
      title: 'Valor',
      align: 'right' as const,
      sortable: true,
      render: (value: number, row: Movimento) => (
        <span className={row.tipo === 'entrada' ? 'text-green-600' : 'text-red-600'}>
          {row.tipo === 'saida' ? '- ' : ''}{formatCurrency(value)}
        </span>
      )
    },
    {
      key: 'categoria',
      title: 'Categoria'
    },
    {
      key: 'status',
      title: 'Status',
      align: 'center' as const
    }
  ];

  interface Action {
    label: string;
    icon?: JSX.Element;
    onClick: (movimento: Movimento) => void | Promise<void>;
    disabled?: (movimento: Movimento) => boolean;
    variant?: 'destructive';
  }

  const actions: Action[] = [
    {
      label: 'Realizar',
      icon: <Check className="h-4 w-4" />,
      onClick: (movimento: Movimento) => handleStatusChange(movimento, 'realizado'),
      disabled: (movimento: Movimento) => 
        movimento.realizado === true || updatingId === movimento.id
    },
    {
      label: 'Cancelar',
      icon: <X className="h-4 w-4" />,
      onClick: (movimento: Movimento) => handleStatusChange(movimento, 'cancelado'),
      disabled: (movimento: Movimento) => 
        movimento.realizado === false || updatingId === movimento.id
    }
  ];

  if (onEdit) {
    actions.push({
      label: 'Editar',
      onClick: (movimento: Movimento) => onEdit(movimento)
    });
  }

  if (onDelete) {
    actions.push({
      label: 'Excluir',
      onClick: async (movimento: Movimento) => {
        if (window.confirm('Tem certeza que deseja excluir este movimento?')) {
          await onDelete(movimento.id);
        }
      },
      variant: 'destructive'
    });
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Movimentações</CardTitle>
      </CardHeader>
      <CardContent>
        <FinancialTable
          data={movimentos}
          columns={columns}
          actions={actions}
          loading={loading}
          getStatusColor={getStatusColor}
          getStatusLabel={getStatusLabel}
          emptyMessage="Nenhuma movimentação encontrada"
        />
      </CardContent>
    </Card>
  );
};

export default MovimentosTable;