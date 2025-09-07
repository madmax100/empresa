import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Conta } from "@/types/financeiro";

interface ContasTableProps {
  contas: Conta[];
  title: string;
}

export const ContasTable = ({ contas, title }: ContasTableProps) => {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Descrição</TableHead>
              <TableHead>Cliente/Fornecedor</TableHead>
              <TableHead>Data Vencimento</TableHead>
              <TableHead className="text-right">Valor</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contas.length > 0 ? (
              contas.map((conta) => (
                <TableRow key={conta.id}>
                  <TableCell>{conta.descricao}</TableCell>
                  <TableCell>{conta.pessoa?.nome}</TableCell>
                  <TableCell>{formatDate(conta.data_vencimento)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(conta.valor)}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} className="text-center">
                  Nenhuma conta encontrada para o período.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
