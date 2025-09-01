import React, { useState } from "react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Calendar as CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

interface DateRange {
  from?: Date;
  to?: Date;
}

interface SeparateDatePickerProps {
  date?: DateRange | undefined;
  onDateChange?: (date: DateRange | undefined) => void;
}

export const SeparateDatePicker: React.FC<SeparateDatePickerProps> = ({
  date,
  onDateChange,
}) => {
  const [startOpen, setStartOpen] = useState(false);
  const [endOpen, setEndOpen] = useState(false);

  const handleStartDateChange = (selectedDate: Date | undefined) => {
    if (selectedDate) {
      onDateChange?.({ 
        from: selectedDate, 
        to: date?.to && selectedDate <= date.to ? date.to : undefined 
      });
      setStartOpen(false);
    }
  };

  const handleEndDateChange = (selectedDate: Date | undefined) => {
    if (selectedDate) {
      onDateChange?.({ 
        from: date?.from, 
        to: selectedDate 
      });
      setEndOpen(false);
    }
  };

  const getPresetRanges = () => {
    const today = new Date();
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    const startOfYear = new Date(today.getFullYear(), 0, 1);
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const endOfLastMonth = new Date(today.getFullYear(), today.getMonth(), 0);

    return [
      {
        label: "Hoje",
        range: { from: today, to: today }
      },
      {
        label: "Este mês",
        range: { from: startOfMonth, to: today }
      },
      {
        label: "Mês passado",
        range: { from: lastMonth, to: endOfLastMonth }
      },
      {
        label: "Este ano",
        range: { from: startOfYear, to: today }
      }
    ];
  };

  const clearDates = () => {
    onDateChange?.(undefined);
  };

  return (
    <div className="flex items-center gap-4">
      {/* Períodos pré-definidos */}
      <div className="flex gap-2">
        {getPresetRanges().map((preset) => (
          <Button
            key={preset.label}
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={() => onDateChange?.(preset.range)}
          >
            {preset.label}
          </Button>
        ))}
        <Button
          variant="outline"
          size="sm"
          className="text-xs"
          onClick={clearDates}
        >
          Limpar
        </Button>
      </div>

      {/* Data de início */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">De:</span>
        <Popover open={startOpen} onOpenChange={setStartOpen}>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "w-[140px] justify-start text-left font-normal",
                !date?.from && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {date?.from ? (
                format(date.from, "dd/MM/yyyy", { locale: ptBR })
              ) : (
                "Data início"
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="single"
              selected={date?.from}
              onSelect={handleStartDateChange}
              disabled={(date) => date > new Date()}
              locale={ptBR}
              weekStartsOn={0}
            />
          </PopoverContent>
        </Popover>
      </div>

      {/* Data final */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Até:</span>
        <Popover open={endOpen} onOpenChange={setEndOpen}>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "w-[140px] justify-start text-left font-normal",
                !date?.to && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {date?.to ? (
                format(date.to, "dd/MM/yyyy", { locale: ptBR })
              ) : (
                "Data final"
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="single"
              selected={date?.to}
              onSelect={handleEndDateChange}
              disabled={(dateParam) => 
                dateParam > new Date() || 
                Boolean(date?.from && dateParam < date.from)
              }
              locale={ptBR}
              weekStartsOn={0}
            />
          </PopoverContent>
        </Popover>
      </div>
    </div>
  );
};
