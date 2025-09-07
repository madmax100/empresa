import * as React from "react"

interface TableProps {
  className?: string;
  children: React.ReactNode;
}

const Table = ({ className, children }: TableProps) => (
  <div className="relative w-full overflow-auto">
    <table className={`w-full caption-bottom text-sm ${className || ''}`}>
      {children}
    </table>
  </div>
)

interface TableHeaderProps {
  className?: string;
  children: React.ReactNode;
}

const TableHeader = ({ className, children }: TableHeaderProps) => (
  <thead className={`[&_tr]:border-b ${className || ''}`}>
    {children}
  </thead>
)

interface TableBodyProps {
  className?: string;
  children: React.ReactNode;
}

const TableBody = ({ className, children }: TableBodyProps) => (
  <tbody className={`[&_tr:last-child]:border-0 ${className || ''}`}>
    {children}
  </tbody>
)

interface TableRowProps {
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
}

const TableRow = ({ className, children, onClick }: TableRowProps) => (
  <tr 
    className={`border-b transition-colors hover:bg-gray-50/50 data-[state=selected]:bg-gray-50 ${className || ''}`}
    onClick={onClick}
  >
    {children}
  </tr>
)

interface TableHeadProps {
  className?: string;
  children?: React.ReactNode;
}

const TableHead = ({ className, children }: TableHeadProps) => (
  <th className={`h-12 px-4 text-left align-middle font-medium text-gray-500 [&:has([role=checkbox])]:pr-0 ${className || ''}`}>
    {children}
  </th>
)

interface TableCellProps {
  className?: string;
  children: React.ReactNode;
  colSpan?: number;
  title?: string;
}

const TableCell = ({ className, children, colSpan, title }: TableCellProps) => (
  <td className={`p-4 align-middle [&:has([role=checkbox])]:pr-0 ${className || ''}`} colSpan={colSpan} title={title}>
    {children}
  </td>
)

export {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
}
