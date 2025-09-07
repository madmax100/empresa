import * as React from "react"

interface TabsProps {
  value: string;
  onValueChange: (value: string) => void;
  className?: string;
  children: React.ReactNode;
}

const Tabs = ({ value, onValueChange, className, children }: TabsProps) => (
  <div className={className} data-tabs-value={value}>
    {React.Children.map(children, child => 
      React.isValidElement(child) 
        ? React.cloneElement(child, { currentValue: value, onValueChange } as any)
        : child
    )}
  </div>
)

interface TabsListProps {
  className?: string;
  children: React.ReactNode;
  currentValue?: string;
  onValueChange?: (value: string) => void;
}

const TabsList = ({ className, children, currentValue, onValueChange }: TabsListProps) => (
  <div className={`inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1 text-gray-500 ${className || ''}`}>
    {React.Children.map(children, child => 
      React.isValidElement(child) 
        ? React.cloneElement(child, { currentValue, onValueChange } as any)
        : child
    )}
  </div>
)

interface TabsTriggerProps {
  value: string;
  className?: string;
  children: React.ReactNode;
  currentValue?: string;
  onValueChange?: (value: string) => void;
}

const TabsTrigger = ({ value, className, children, currentValue, onValueChange }: TabsTriggerProps) => {
  const isActive = currentValue === value;
  
  return (
    <button
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
        isActive 
          ? 'bg-white text-gray-900 shadow-sm' 
          : 'hover:bg-gray-200'
      } ${className || ''}`}
      onClick={() => onValueChange?.(value)}
    >
      {children}
    </button>
  )
}

interface TabsContentProps {
  value: string;
  className?: string;
  children: React.ReactNode;
  currentValue?: string;
}

const TabsContent = ({ value, className, children, currentValue }: TabsContentProps) => {
  if (currentValue !== value) return null;
  
  return (
    <div className={`mt-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${className || ''}`}>
      {children}
    </div>
  )
}

export { Tabs, TabsList, TabsTrigger, TabsContent }
