import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface MetricCardProps {
  title: string;
  value?: number | null;
  change?: number | null;
  format?: 'currency' | 'percentage' | 'number' | 'days';
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value = 0, 
  change, 
  format = 'currency' 
}) => {
  const formatValue = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return '-';
    
    try {
      switch (format) {
        case 'currency':
          return new Intl.NumberFormat('pt-BR', { 
            style: 'currency', 
            currency: 'BRL' 
          }).format(val);
        case 'percentage':
          return `${Number(val).toFixed(2)}%`;
        case 'days':
          return `${Number(val).toLocaleString('pt-BR')} dias`;
        default:
          return Number(val).toLocaleString('pt-BR');
      }
    } catch (error) {
      console.error('Error formatting value:', error);
      return '-';
    }
  };

  const renderTrend = () => {
    if (change === null || change === undefined) return null;
    
    const trendValue = Number(change).toFixed(1);
    const isPositive = change >= 0;
    const TrendIcon = isPositive ? TrendingUp : TrendingDown;
    const trendColor = isPositive ? "text-green-500" : "text-red-500";
    
    return (
      <div className="flex items-center text-sm">
        <TrendIcon className={`h-4 w-4 mr-1 ${trendColor}`} />
        <span className={trendColor}>
          {isPositive ? '+' : ''}{trendValue}%
        </span>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{formatValue(value)}</div>
        {renderTrend()}
      </CardContent>
    </Card>
  );
};

export default MetricCard;