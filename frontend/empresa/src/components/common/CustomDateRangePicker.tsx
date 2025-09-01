import React, { useState } from "react";
import { format, addMonths, subMonths, startOfMonth, endOfMonth, startOfWeek, endOfWeek, addDays, isSameMonth, isSameDay, isToday, isBefore, isAfter } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, X } from "lucide-react";
import { Button } from "@/components/ui/button";
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

interface CustomDateRangePickerProps {
  date?: DateRange | undefined;
  onDateChange?: (date: DateRange | undefined) => void;
}

export const CustomDateRangePicker: React.FC<CustomDateRangePickerProps> = ({
  date,
  onDateChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [hoveredDate, setHoveredDate] = useState<Date | null>(null);

  const handleDateClick = (day: Date) => {
    if (!date?.from || (date.from && date.to)) {
      // Iniciando nova seleção
      onDateChange?.({ from: day, to: undefined });
    } else if (date.from && !date.to) {
      // Completando seleção
      if (isBefore(day, date.from)) {
        onDateChange?.({ from: day, to: date.from });
      } else {
        onDateChange?.({ from: date.from, to: day });
      }
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
    const startOfThisMonth = startOfMonth(today);
    const startOfYear = new Date(today.getFullYear(), 0, 1);
    const lastMonth = subMonths(startOfThisMonth, 1);
    const endOfLastMonth = endOfMonth(lastMonth);

    return [
      {
        label: "Hoje",
        range: { from: today, to: today }
      },
      {
        label: "Este mês",
        range: { from: startOfThisMonth, to: today }
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

  const renderCalendar = (monthOffset: number = 0) => {
    const month = addMonths(currentMonth, monthOffset);
    const monthStart = startOfMonth(month);
    const monthEnd = endOfMonth(month);
    const startDate = startOfWeek(monthStart, { weekStartsOn: 0 });
    const endDate = endOfWeek(monthEnd, { weekStartsOn: 0 });

    const dateFormat = "d";
    const rows: JSX.Element[] = [];
    let days: JSX.Element[] = [];
    let day = startDate;

    // Header dos dias da semana
    const daysOfWeek: JSX.Element[] = [];
    const startWeek = startOfWeek(new Date(), { weekStartsOn: 0 });
    for (let i = 0; i < 7; i++) {
      daysOfWeek.push(
        <div key={i} className="text-center text-xs font-medium text-muted-foreground p-2 w-9">
          {format(addDays(startWeek, i), "EEEEEE", { locale: ptBR })}
        </div>
      );
    }

    while (day <= endDate) {
      for (let i = 0; i < 7; i++) {
        const cloneDay = day;
        const isSelected = date?.from && isSameDay(day, date.from) || (date?.to && isSameDay(day, date.to));
        const isInRange = date?.from && date?.to && isAfter(day, date.from) && isBefore(day, date.to);
        const isRangeStart = date?.from && isSameDay(day, date.from);
        const isRangeEnd = date?.to && isSameDay(day, date.to);
        const isHovered = hoveredDate && date?.from && !date?.to && isAfter(day, date.from) && isBefore(day, hoveredDate);
        const isCurrentMonth = isSameMonth(day, month);
        const isCurrentDay = isToday(day);
        const isFutureDate = isAfter(day, new Date());

        days.push(
          <div
            key={day.toString()}
            className={cn(
              "relative p-0 text-center text-sm cursor-pointer w-9 h-9 flex items-center justify-center",
              "hover:bg-accent hover:text-accent-foreground rounded-md",
              !isCurrentMonth && "text-muted-foreground opacity-50",
              isCurrentDay && "bg-accent text-accent-foreground font-semibold",
              (isSelected || isRangeStart || isRangeEnd) && "bg-primary text-primary-foreground hover:bg-primary",
              (isInRange || isHovered) && "bg-accent text-accent-foreground",
              isRangeStart && "rounded-r-none",
              isRangeEnd && "rounded-l-none",
              (isInRange || isHovered) && !isRangeStart && !isRangeEnd && "rounded-none",
              isFutureDate && "opacity-50 cursor-not-allowed"
            )}
            onClick={() => !isFutureDate && handleDateClick(cloneDay)}
            onMouseEnter={() => setHoveredDate(cloneDay)}
            onMouseLeave={() => setHoveredDate(null)}
          >
            {format(day, dateFormat)}
          </div>
        );
        day = addDays(day, 1);
      }
      rows.push(
        <div key={day.toString()} className="flex justify-between">
          {days}
        </div>
      );
      days = [];
    }

    return (
      <div className="p-3">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-sm font-medium">
            {format(month, "MMMM yyyy", { locale: ptBR })}
          </h2>
          {monthOffset === 0 && (
            <div className="flex space-x-1">
              <Button
                variant="outline"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
        <div className="flex justify-between mb-2">
          {daysOfWeek}
        </div>
        <div className="space-y-1">
          {rows}
        </div>
      </div>
    );
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
                    onClick={() => {
                      onDateChange?.(preset.range);
                      setIsOpen(false);
                    }}
                  >
                    {preset.label}
                  </Button>
                ))}
              </div>
            </div>
            <div className="flex">
              {renderCalendar(0)}
              {renderCalendar(1)}
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
};
