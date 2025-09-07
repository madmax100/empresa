import React from 'react';

interface DateRange {
  from: Date;
  to: Date;
}

interface SeparateDatePickerProps {
  date: DateRange;
  onDateChange: (dateRange: DateRange | undefined) => void;
  className?: string;
}

export const SeparateDatePicker: React.FC<SeparateDatePickerProps> = ({ 
  date, 
  onDateChange, 
  className 
}) => {
  const formatDateForInput = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  const handleFromDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFromDate = new Date(e.target.value + 'T00:00:00');
    if (!isNaN(newFromDate.getTime())) {
      onDateChange({
        from: newFromDate,
        to: date.to
      });
    }
  };

  const handleToDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newToDate = new Date(e.target.value + 'T23:59:59');
    if (!isNaN(newToDate.getTime())) {
      onDateChange({
        from: date.from,
        to: newToDate
      });
    }
  };

  return (
    <div className={`flex flex-col sm:flex-row gap-2 items-center ${className || ''}`}>
      <div className="flex flex-col">
        <label className="text-sm font-medium text-gray-700 mb-1">Data Inicial</label>
        <input
          type="date"
          value={formatDateForInput(date.from)}
          onChange={handleFromDateChange}
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div className="flex flex-col">
        <label className="text-sm font-medium text-gray-700 mb-1">Data Final</label>
        <input
          type="date"
          value={formatDateForInput(date.to)}
          onChange={handleToDateChange}
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
    </div>
  );
};
