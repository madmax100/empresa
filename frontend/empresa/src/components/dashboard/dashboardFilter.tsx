// components/dashboard/DashboardFilter.tsx
import React from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Download, RefreshCw } from "lucide-react";
import { Filtros } from '@/types/dashboardNovo';

interface DashboardFilterProps {
  filters: Filtros;
  onFilterChange: (filters: Partial<Filtros>) => void;
  onRefresh: () => void;
  onExport: () => void;
}

export const DashboardFilter: React.FC<DashboardFilterProps> = ({
  filters,
  onFilterChange,
  onRefresh,
  onExport
}) => {
  return (
    <Card className="mb-6">
      <CardContent className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Data Inicial</label>
            <input
              type="date"
              className="w-full px-3 py-2 border rounded-md"
              value={filters.dataInicial}
              min="2024-01-01"
              onChange={(e) => onFilterChange({ dataInicial: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Data Final</label>
            <input
              type="date"
              className="w-full px-3 py-2 border rounded-md"
              value={filters.dataFinal}
              min="2024-01-01"
              onChange={(e) => onFilterChange({ dataFinal: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Tipo</label>
            <select
              className="w-full px-3 py-2 border rounded-md"
              value={filters.tipo}
              onChange={(e) => onFilterChange({ tipo: e.target.value })}
            >
              <option value="todos">Todos os Tipos</option>
              <option value="entrada">Entradas</option>
              <option value="saida">Saídas</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Fonte</label>
            <select
              className="w-full px-3 py-2 border rounded-md"
              value={filters.fonte}
              onChange={(e) => onFilterChange({ fonte: e.target.value })}
            >
              <option value="todos">Todas as Fontes</option>
              <option value="nfs">Notas Fiscais Saída</option>
              <option value="nfe">Notas Fiscais Entrada</option>
              <option value="nfserv">Notas de Serviço</option>
              <option value="conta_receber">Contas a Receber</option>
              <option value="conta_pagar">Contas a Pagar</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={onRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button variant="outline" onClick={onExport}>
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};