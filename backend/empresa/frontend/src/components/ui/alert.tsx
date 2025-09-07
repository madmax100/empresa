import * as React from "react"

interface AlertProps {
  className?: string;
  children: React.ReactNode;
}

const Alert = ({ className, children }: AlertProps) => (
  <div className={`relative w-full rounded-lg border p-4 ${className || ''}`}>
    {children}
  </div>
)

interface AlertDescriptionProps {
  className?: string;
  children: React.ReactNode;
}

const AlertDescription = ({ className, children }: AlertDescriptionProps) => (
  <div className={`text-sm [&_p]:leading-relaxed ${className || ''}`}>
    {children}
  </div>
)

export { Alert, AlertDescription }
