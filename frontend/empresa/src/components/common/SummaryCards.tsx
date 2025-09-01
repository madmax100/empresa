import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FluxoCaixaResponse } from '@/types/fluxo_caixa/models';
import { format } from 'date-fns';

interface SummaryCardsProps {
  data: FluxoCaixaResponse | null;
  loading: boolean;
}

const formatarMoeda = (valor: number = 0): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

export const SummaryCards: React.FC<SummaryCardsProps> = ({ data, loading }) => {
  // Card loading state
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((index) => (
          <Card key={index}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3"></div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Valores padrão caso data seja null
  const totalizadores = data?.totalizadores ?? {
    entradas_previstas: 0,
    entradas_realizadas: 0,
    saidas_previstas: 0,
    saidas_realizadas: 0,
    saldo_realizado: 0,
    saldo_projetado: 0
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Saldo Atual */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">
            Saldo Atual
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatarMoeda(data?.saldo_final_realizado ?? 0)}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Atualizado em {format(new Date(), "dd/MM/yyyy 'às' HH:mm")}
          </p>
        </CardContent>
      </Card>

      {/* Entradas Previstas */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">
            Entradas Previstas
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">
            {formatarMoeda(totalizadores.entradas_previstas)}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            No período selecionado
          </p>
        </CardContent>
      </Card>

      {/* Saídas Previstas */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">
            Saídas Previstas
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-600">
            {formatarMoeda(totalizadores.saidas_previstas)}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            No período selecionado
          </p>
        </CardContent>
      </Card>

      {/* Saldo Projetado */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">
            Saldo Projetado
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatarMoeda(data?.saldo_final_projetado ?? 0)}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Final do período
          </p>
        </CardContent>
      </Card>
    </div>
  );
};