import React, { useState } from "react";
import { format } from "date-fns";
import { DateRange } from "react-day-picker";
import { ptBR } from "date-fns/locale";
import { Calendar as CalendarIcon, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

interface DateRangePickerProps {
  date?: DateRange | undefined;
  onDateChange?: (date: DateRange | undefined) => void;
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  date,
  onDateChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleDateChange = (newDate: DateRange | undefined) => {
    onDateChange?.(newDate);
    // Fechar o popover quando ambas as datas forem selecionadas
    if (newDate?.from && newDate?.to) {
      setIsOpen(false);
    }
  };

  const clearDates = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDateChange?.(undefined);
    setIsOpen(false);
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

  return (
    <div className="grid gap-2">
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-[300px] justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date?.from ? (
              <>
                {date.to ? (
                  <>
                    {format(date.from, "dd/MM/yyyy", { locale: ptBR })} -{" "}
                    {format(date.to, "dd/MM/yyyy", { locale: ptBR })}
                  </>
                ) : (
                  format(date.from, "dd/MM/yyyy", { locale: ptBR })
                )}
                <X 
                  className="ml-auto h-4 w-4 opacity-50 hover:opacity-100" 
                  onClick={clearDates}
                />
              </>
            ) : (
              <span>Selecione um período</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <div className="flex">
            <div className="border-r">
              <div className="p-3 space-y-2">
                <h4 className="text-sm font-medium">Períodos pré-definidos</h4>
                {getPresetRanges().map((preset) => (
                  <Button
                    key={preset.label}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => handleDateChange(preset.range)}
                  >
                    {preset.label}
                  </Button>
                ))}
              </div>
            </div>
            <Calendar
              mode="range"
              defaultMonth={date?.from || new Date()}
              selected={date}
              onSelect={handleDateChange}
              numberOfMonths={2}
              locale={ptBR}
              weekStartsOn={0}
              disabled={(date) => date > new Date()}
            />
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
};
