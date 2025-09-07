import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import { ArrowDownCircle, ArrowUpCircle, DollarSign } from "lucide-react";

interface FluxoCaixaSummaryProps {
  totalPagar: number;
  totalReceber: number;
  saldo: number;
}

export const FluxoCaixaSummary = ({ totalPagar, totalReceber, saldo }: FluxoCaixaSummaryProps) => {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total a Receber</CardTitle>
          <ArrowUpCircle className="h-4 w-4 text-green-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">{formatCurrency(totalReceber)}</div>
          <p className="text-xs text-muted-foreground">Previsto no período</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total a Pagar</CardTitle>
          <ArrowDownCircle className="h-4 w-4 text-red-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-600">{formatCurrency(totalPagar)}</div>
          <p className="text-xs text-muted-foreground">Previsto no período</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Saldo Previsto</CardTitle>
          <DollarSign className={`h-4 w-4 ${saldo >= 0 ? 'text-blue-500' : 'text-orange-500'}`} />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${saldo >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>{formatCurrency(saldo)}</div>
          <p className="text-xs text-muted-foreground">Receitas - Despesas</p>
        </CardContent>
      </Card>
    </div>
  );
};
