import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { format } from "date-fns";
import { ptBR } from 'date-fns/locale';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown";
import { MoreHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";

interface Column {
  key: string;
  title: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: any) => React.ReactNode;
  sortable?: boolean;
}

interface Action {
  label: string;
  onClick: (row: any) => void;
  icon?: React.ReactNode;
  variant?: 'default' | 'destructive';
  disabled?: boolean | ((row: any) => boolean);
}

interface FinancialTableProps {
  data: any[];
  columns: Column[];
  actions?: Action[];
  selection?: {
    selected: number[];
    onSelect: (id: number) => void;
    onSelectAll: (checked: boolean) => void;
  };
  loading?: boolean;
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
  getStatusColor?: (realizado: boolean) => string;
  getStatusLabel?: (realizado: boolean) => string;
  emptyMessage?: string;
}

export const FinancialTable: React.FC<FinancialTableProps> = ({
  data,
  columns,
  actions,
  selection,
  loading = false,
  onSort,
  getStatusColor,
  getStatusLabel,
  emptyMessage = "Nenhum registro encontrado"
}) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc' | null;
  }>({ key: '', direction: null });

  const handleSort = (key: string) => {
    if (!onSort) return;

    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    
    setSortConfig({ key, direction });
    onSort(key, direction);
  };

  const formatValue = (value: any, type?: string): string => {
    if (value === null || value === undefined) return '-';

    if (type === 'date' && typeof value === 'string') {
      return format(new Date(value), 'dd/MM/yyyy', { locale: ptBR });
    }

    if (type === 'currency' && typeof value === 'number') {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(value);
    }

    return String(value);
  };

  const renderCell = (column: Column, row: any) => {
    if (column.render) {
      return column.render(row[column.key], row);
    }

    if (column.key === 'status' && getStatusColor && getStatusLabel) {
      return (
        <span className={cn(
          "px-2 py-1 rounded-full text-xs font-semibold",
          getStatusColor(row.status)
        )}>
          {getStatusLabel(row.status)}
        </span>
      );
    }

    return formatValue(row[column.key]);
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-full mb-4" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded w-full mb-2" />
        ))}
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            {selection && (
              <TableHead className="w-12">
                <Checkbox
                  checked={data.length > 0 && selection.selected.length === data.length}
                  onCheckedChange={(checked) => {
                    selection.onSelectAll(!!checked);
                  }}
                />
              </TableHead>
            )}
            {columns.map((column) => (
              <TableHead
                key={column.key}
                className={cn(
                  column.sortable && "cursor-pointer",
                  column.align === 'right' && "text-right",
                  column.align === 'center' && "text-center"
                )}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                <div className="flex items-center gap-2">
                  {column.title}
                  {sortConfig.key === column.key && (
                    <span className="text-xs">
                      {sortConfig.direction === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </TableHead>
            ))}
            {actions && <TableHead className="w-[80px]">Ações</TableHead>}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={columns.length + (selection ? 1 : 0) + (actions ? 1 : 0)}
                className="h-24 text-center"
              >
                {emptyMessage}
              </TableCell>
            </TableRow>
          ) : (
            data.map((row) => (
              <TableRow key={row.id}>
                {selection && (
                  <TableCell className="w-12">
                    <Checkbox
                      checked={selection.selected.includes(row.id)}
                      onCheckedChange={() => selection.onSelect(row.id)}
                    />
                  </TableCell>
                )}
                {columns.map((column) => (
                  <TableCell
                    key={column.key}
                    className={cn(
                      column.align === 'right' && "text-right",
                      column.align === 'center' && "text-center"
                    )}
                  >
                    {renderCell(column, row)}
                  </TableCell>
                ))}
                {actions && (
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Ações</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        {actions.map((action, index) => (
                          <DropdownMenuItem
                            key={index}
                            onClick={() => action.onClick(row)}
                            disabled={typeof action.disabled === 'function' 
                              ? action.disabled(row) 
                              : action.disabled}
                          >
                            {action.icon && (
                              <span className="mr-2">{action.icon}</span>
                            )}
                            {action.label}
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                )}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
};

export default FinancialTable;