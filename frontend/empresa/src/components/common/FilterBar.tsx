import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RefreshCcw, Download } from "lucide-react";
import { Filtros } from '@/types/dashboardNovo';

interface FilterBarProps {
  filtros: Filtros;
  onFiltrosChange: (filtros: Partial<Filtros>) => void;
  onRefresh: () => void;
  onExport: () => void;
  className?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filtros,
  onFiltrosChange,
  onRefresh,
  onExport,
  className = '',
}) => {
  const tipoOptions = [
    { value: 'todos', label: 'Todos os Tipos' },
    { value: 'entrada', label: 'Entradas' },
    { value: 'saida', label: 'Saídas' },
  ];

  const fonteOptions = [
    { value: 'todos', label: 'Todas as Fontes' },
    { value: 'nfs', label: 'Notas Fiscais Saída' },
    { value: 'nfe', label: 'Notas Fiscais Entrada' },
    { value: 'nfserv', label: 'Notas de Serviço' },
    { value: 'conta_receber', label: 'Contas a Receber' },
    { value: 'conta_pagar', label: 'Contas a Pagar' },
  ];

  // Garante que sempre teremos uma data válida
  const formatDateForInput = (dateString: string | undefined): string => {
    if (!dateString) {
      return new Date().toISOString().split('T')[0];
    }
    try {
      return dateString.split('T')[0];
    } catch {
      return new Date().toISOString().split('T')[0];
    }
  };

  const handleDateChange = (field: 'dataInicial' | 'dataFinal', value: string) => {
    onFiltrosChange({ [field]: value || new Date().toISOString().split('T')[0] });
  };

  return (
    <Card className={className}>
      <CardContent className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {/* Data Inicial */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Data Inicial</label>
            <Input
              type="date"
              value={formatDateForInput(filtros.dataInicial)}
              onChange={(e) => handleDateChange('dataInicial', e.target.value)}
              className="w-full"
            />
          </div>

          {/* Data Final */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Data Final</label>
            <Input
              type="date"
              value={formatDateForInput(filtros.dataFinal)}
              onChange={(e) => handleDateChange('dataFinal', e.target.value)}
              className="w-full"
            />
          </div>

          {/* Tipo de Movimento */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Tipo</label>
            <Select
              value={filtros.tipo || 'todos'}
              onValueChange={(value) => onFiltrosChange({ tipo: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent>
                {tipoOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Fonte */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Fonte</label>
            <Select
              value={filtros.fonte || 'todos'}
              onValueChange={(value) => onFiltrosChange({ fonte: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione a fonte" />
              </SelectTrigger>
              <SelectContent>
                {fonteOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Botões de Ação */}
        <div className="flex justify-end gap-2">
          <Button 
            variant="outline" 
            onClick={onRefresh}
          >
            <RefreshCcw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button 
            variant="default" 
            onClick={onExport}
          >
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};