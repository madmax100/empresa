import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface IndicadorCardProps {
  /**
   * Título do indicador
   */
  titulo: string;
  
  /**
   * Valor principal do indicador
   */
  valor: number;
  
  /**
   * Valores comparativos (opcional)
   */
  comparativo?: {
    valor?: number;
    percentual: number;
    label?: string;
  };
  
  /**
   * Cor do tema (afeta o valor principal)
   */
  cor?: 'default' | 'blue' | 'green' | 'red' | 'purple' | 'orange';
  
  /**
   * Ícone do card (opcional)
   */
  icone?: React.ReactNode;
  
  /**
   * Texto de descrição (opcional)
   */
  descricao?: string;
  
  /**
   * Label do valor secundário (opcional)
   */
  labelSecundario?: string;
  
  /**
   * Valor secundário (opcional)
   */
  valorSecundario?: number;
  
  /**
   * Formato do valor principal
   */
  formato?: 'currency' | 'number' | 'percentage';

  /**
   * Classe CSS adicional (opcional)
   */
  className?: string;
}

export const IndicadorCard: React.FC<IndicadorCardProps> = ({
  titulo,
  valor,
  comparativo,
  cor = 'default',
  icone,
  descricao,
  labelSecundario,
  valorSecundario,
  formato = 'currency',
  className = ''
}) => {
  // Mapa de cores para texto
  const coresTexto: Record<string, string> = {
    default: 'text-gray-900',
    blue: 'text-blue-600',
    green: 'text-green-600',
    red: 'text-red-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600'
  };

  // Função de formatação de valores
  const formatarValor = (val: number, fmt: 'currency' | 'number' | 'percentage' = formato) => {
    if (fmt === 'currency') {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(val);
    }
    if (fmt === 'percentage') {
      return `${val.toFixed(1)}%`;
    }
    return new Intl.NumberFormat('pt-BR').format(val);
  };

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center space-x-2">
          {icone && <div>{icone}</div>}
          <span>{titulo}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          {/* Valor Principal */}
          <div className={`text-2xl font-bold ${coresTexto[cor]}`}>
            {formatarValor(valor)}
          </div>

          {/* Comparativo */}
          {comparativo && (
            <div className="flex items-center text-sm space-x-1">
              {comparativo.percentual >= 0 ? (
                <>
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-green-500">
                    +{comparativo.percentual.toFixed(1)}%
                  </span>
                </>
              ) : (
                <>
                  <TrendingDown className="h-4 w-4 text-red-500" />
                  <span className="text-red-500">
                    {comparativo.percentual.toFixed(1)}%
                  </span>
                </>
              )}
              {comparativo.label && (
                <span className="text-muted-foreground ml-1">
                  {comparativo.label}
                </span>
              )}
            </div>
          )}

          {/* Descrição */}
          {descricao && (
            <p className="text-sm text-muted-foreground">{descricao}</p>
          )}

          {/* Valor Secundário */}
          {labelSecundario && valorSecundario !== undefined && (
            <div className="mt-2 pt-2 border-t border-gray-100">
              <span className="text-sm text-muted-foreground block">
                {labelSecundario}
              </span>
              <div className="font-medium">
                {formatarValor(valorSecundario, 'number')}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default IndicadorCard;